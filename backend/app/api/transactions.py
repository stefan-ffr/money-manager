from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import date
import os
from pathlib import Path
from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user
from app.core.authorization import get_user_filter, verify_transaction_access, verify_account_access
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.user import User

router = APIRouter()


def _apply_balance_delta(account: Account, delta: Decimal) -> None:
    """Adjust an account's balance by delta (positive = income, negative = expense)."""
    account.balance = (account.balance or Decimal("0.00")) + delta


# Pydantic Schemas
class TransactionCreate(BaseModel):
    account_id: int
    date: date
    amount: Decimal
    category: Optional[str] = None
    description: Optional[str] = None
    status: str = "pending"


class TransferCreate(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: Decimal  # positive amount to move
    date: date
    description: Optional[str] = None


class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    amount: Optional[Decimal] = None
    category: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    requires_confirmation: Optional[bool] = None


class TransactionResponse(BaseModel):
    id: int
    account_id: int
    date: date
    amount: Decimal
    category: Optional[str]
    description: Optional[str]
    status: str
    source: str
    requires_confirmation: bool
    receipt_path: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    account_id: Optional[int] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    user_filter = Depends(get_user_filter),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List transactions with optional filters (user-filtered unless admin)"""
    query = db.query(Transaction).filter_by(**user_filter)

    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if status:
        query = query.filter(Transaction.status == status)
    if category:
        query = query.filter(Transaction.category == category)
    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)
    if q:
        query = query.filter(Transaction.description.ilike(f"%{q}%"))

    transactions = query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction: Transaction = Depends(verify_transaction_access)
):
    """Get specific transaction (with access verification)"""
    return transaction


@router.post("/", response_model=TransactionResponse, status_code=201)
def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new transaction and update the account balance."""
    # Verify that the account belongs to the user
    account = verify_account_access(transaction.account_id, db, current_user)

    try:
        db_transaction = Transaction(**transaction.model_dump(), user_id=current_user.id)
        db.add(db_transaction)
        # Keep the account balance in sync with its transactions
        _apply_balance_delta(account, db_transaction.amount)
        db.commit()
        db.refresh(db_transaction)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Buchung konnte nicht gespeichert werden")
    return db_transaction


@router.post("/transfer", response_model=List[TransactionResponse], status_code=201)
def create_transfer(
    transfer: TransferCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Move money between two of the user's own accounts in a single booking.

    Creates a paired expense (source) and income (target) transaction and
    updates both account balances atomically.
    """
    if transfer.from_account_id == transfer.to_account_id:
        raise HTTPException(status_code=400, detail="Quell- und Zielkonto müssen unterschiedlich sein")
    if transfer.amount <= 0:
        raise HTTPException(status_code=400, detail="Betrag muss größer als 0 sein")

    # Verify ownership of both accounts
    from_account = verify_account_access(transfer.from_account_id, db, current_user)
    to_account = verify_account_access(transfer.to_account_id, db, current_user)

    if from_account.currency != to_account.currency:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Umbuchung nur zwischen Konten gleicher Währung möglich "
                f"({from_account.currency} ≠ {to_account.currency})"
            ),
        )

    label = transfer.description or f"Umbuchung {from_account.name} → {to_account.name}"

    try:
        out_tx = Transaction(
            user_id=current_user.id,
            account_id=from_account.id,
            date=transfer.date,
            amount=-transfer.amount,
            category="Umbuchung",
            description=label,
            status="confirmed",
            source="transfer",
        )
        in_tx = Transaction(
            user_id=current_user.id,
            account_id=to_account.id,
            date=transfer.date,
            amount=transfer.amount,
            category="Umbuchung",
            description=label,
            status="confirmed",
            source="transfer",
        )
        db.add(out_tx)
        db.add(in_tx)
        _apply_balance_delta(from_account, -transfer.amount)
        _apply_balance_delta(to_account, transfer.amount)
        db.commit()
        db.refresh(out_tx)
        db.refresh(in_tx)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Umbuchung konnte nicht gespeichert werden")

    return [out_tx, in_tx]


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction: TransactionUpdate,
    db_transaction: Transaction = Depends(verify_transaction_access),
    db: Session = Depends(get_db)
):
    """Update transaction and keep the account balance in sync."""
    update_data = transaction.model_dump(exclude_unset=True)

    # If the amount changes, adjust the account balance by the difference
    new_amount = update_data.get("amount")
    try:
        if new_amount is not None and new_amount != db_transaction.amount:
            account = db.query(Account).filter(Account.id == db_transaction.account_id).first()
            if account:
                _apply_balance_delta(account, new_amount - db_transaction.amount)

        for key, value in update_data.items():
            setattr(db_transaction, key, value)

        db.commit()
        db.refresh(db_transaction)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Buchung konnte nicht aktualisiert werden")
    return db_transaction


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    db_transaction: Transaction = Depends(verify_transaction_access),
    db: Session = Depends(get_db)
):
    """Delete transaction and revert its effect on the account balance."""
    # Delete receipt file if exists
    if db_transaction.receipt_path and os.path.exists(db_transaction.receipt_path):
        os.remove(db_transaction.receipt_path)

    try:
        # Reverse this transaction's contribution to the account balance
        account = db.query(Account).filter(Account.id == db_transaction.account_id).first()
        if account:
            _apply_balance_delta(account, -db_transaction.amount)

        db.delete(db_transaction)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Buchung konnte nicht gelöscht werden")
    return None


@router.post("/{transaction_id}/receipt")
async def upload_receipt(
    file: UploadFile = File(...),
    transaction: Transaction = Depends(verify_transaction_access),
    db: Session = Depends(get_db)
):
    """Upload receipt for transaction (with access verification)"""
    # Create receipts directory structure
    year = transaction.date.year
    month = transaction.date.month
    receipts_dir = Path(settings.RECEIPTS_PATH) / str(year) / f"{month:02d}"
    receipts_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_extension = Path(file.filename).suffix
    file_path = receipts_dir / f"transaction_{transaction.id}{file_extension}"

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Update transaction
    transaction.receipt_path = str(file_path)
    db.commit()

    return {"message": "Receipt uploaded successfully", "path": str(file_path)}


@router.get("/{transaction_id}/receipt")
async def get_receipt(
    transaction: Transaction = Depends(verify_transaction_access)
):
    """Get receipt for transaction (with access verification)"""
    from fastapi.responses import FileResponse

    if not transaction.receipt_path:
        raise HTTPException(status_code=404, detail="Receipt not found")

    if not os.path.exists(transaction.receipt_path):
        raise HTTPException(status_code=404, detail="Receipt file not found")

    return FileResponse(transaction.receipt_path)
