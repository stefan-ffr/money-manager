from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.api_key import get_user_from_api_key, generate_api_key
from app.models.user import User
from app.models.api_key import ApiKey
from app.models.account import Account
from app.models.transaction import Transaction

router = APIRouter()

RECEIPT_ACCOUNT_TYPE = "receipt_bot"
RECEIPT_ACCOUNT_NAME = "Quittungsabrechnung"


# ---------------------------------------------------------------------------
# API key management (authenticated as a normal user)
# ---------------------------------------------------------------------------

class ApiKeyCreate(BaseModel):
    name: Optional[str] = None


class ApiKeyResponse(BaseModel):
    id: int
    name: Optional[str]
    key_prefix: str
    active: bool

    class Config:
        from_attributes = True


@router.post("/api-keys")
def create_api_key(
    body: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new API key. The plaintext token is returned ONCE."""
    token, prefix, key_hash = generate_api_key()
    db_key = ApiKey(user_id=current_user.id, name=body.name, key_prefix=prefix, key_hash=key_hash)
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return {
        "id": db_key.id,
        "name": db_key.name,
        "token": token,  # shown only here
        "key_prefix": db_key.key_prefix,
        "message": "Bewahre diesen Token sicher auf – er wird nicht erneut angezeigt.",
    }


@router.get("/api-keys", response_model=List[ApiKeyResponse])
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(ApiKey).filter(ApiKey.user_id == current_user.id).order_by(ApiKey.id.desc()).all()


@router.delete("/api-keys/{key_id}", status_code=204)
def revoke_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    key = db.query(ApiKey).filter(ApiKey.id == key_id, ApiKey.user_id == current_user.id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    db.delete(key)
    db.commit()
    return None


# ---------------------------------------------------------------------------
# Receipt-bot ingestion (authenticated via X-API-Key)
# ---------------------------------------------------------------------------

class ReceiptBotTransaction(BaseModel):
    date: date
    amount: Decimal                       # negative = expense, positive = income
    description: Optional[str] = None
    category: Optional[str] = None
    currency: Optional[str] = None        # used to set the account currency on first use
    external_ref: Optional[str] = None    # bot's own id; used for idempotency


class ReceiptBotPush(BaseModel):
    transactions: List[ReceiptBotTransaction]


def _get_or_create_receipt_account(db: Session, user: User, currency: Optional[str]) -> Account:
    account = db.query(Account).filter(
        Account.user_id == user.id,
        Account.type == RECEIPT_ACCOUNT_TYPE,
    ).first()
    if not account:
        account = Account(
            user_id=user.id,
            name=RECEIPT_ACCOUNT_NAME,
            type=RECEIPT_ACCOUNT_TYPE,
            currency=(currency or "CHF").upper(),
            balance=Decimal("0.00"),
        )
        db.add(account)
        db.flush()
    return account


@router.post("/receipt-bot/transactions")
def ingest_receipt_bot_transactions(
    push: ReceiptBotPush,
    db: Session = Depends(get_db),
    user: User = Depends(get_user_from_api_key),
):
    """Push transactions from the receipt bot into the user's special
    "Quittungsabrechnung" account. Idempotent per external_ref."""
    if not push.transactions:
        return {"created": 0, "skipped": 0, "account_id": None}

    account = _get_or_create_receipt_account(db, user, push.transactions[0].currency)

    created = 0
    skipped = 0
    try:
        for tx in push.transactions:
            if tx.external_ref:
                exists = db.query(Transaction).filter(
                    Transaction.user_id == user.id,
                    Transaction.external_ref == tx.external_ref,
                ).first()
                if exists:
                    skipped += 1
                    continue

            db_tx = Transaction(
                user_id=user.id,
                account_id=account.id,
                date=tx.date,
                amount=tx.amount,
                category=tx.category or "Quittungsabrechnung",
                description=tx.description,
                status="confirmed",
                source="receipt_bot",
                external_ref=tx.external_ref,
            )
            db.add(db_tx)
            account.balance = (account.balance or Decimal("0.00")) + tx.amount
            created += 1
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Transaktionen konnten nicht gespeichert werden")

    return {"created": created, "skipped": skipped, "account_id": account.id}
