from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import List, Optional
from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user
from app.core.authorization import verify_transaction_access
from app.models.user import User
from app.models.account import Account

router = APIRouter()


def _apply_balance_delta(account: Account, delta: Decimal) -> None:
    """Adjust an account's balance by delta (kept in sync with transactions)."""
    account.balance = (account.balance or Decimal("0.00")) + delta


def _resolve_local_recipient(to_user: str, db: Session) -> User:
    """Map a federated 'user@instance.domain' recipient to a local user.

    The invoice must be addressed to THIS instance and reference a user that
    exists locally (matched by username or e-mail).
    """
    parts = to_user.split("@")
    if len(parts) != 2:
        raise HTTPException(status_code=422, detail="Invalid recipient format. Expected user@instance.domain")

    local_part, target_domain = parts
    if target_domain != settings.INSTANCE_DOMAIN:
        raise HTTPException(status_code=404, detail="Invoice is not addressed to this instance")

    user = (
        db.query(User)
        .filter((User.username == local_part) | (User.email == to_user))
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail=f"Unknown recipient '{to_user}' on this instance")
    return user


class InvoiceAttachment(BaseModel):
    filename: str
    data: str  # base64 encoded
    mime_type: str


class FederatedInvoice(BaseModel):
    from_user: str  # e.g., stefan@money.babsyit.ch
    to_user: str
    amount: Decimal
    currency: str = "CHF"
    description: str
    date: date
    category: str | None = None
    split_type: str | None = None
    shared_account_id: str | None = None
    attachments: List[InvoiceAttachment] = []


class InvoiceResponse(BaseModel):
    invoice_id: int
    status: str
    message: str


@router.post("/invoice/send")
async def send_invoice(
    invoice: FederatedInvoice,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send an invoice to another instance on behalf of the current user."""
    from app.services.federation_service import send_federated_invoice

    if not settings.FEDERATION_ENABLED:
        raise HTTPException(status_code=403, detail="Federation not enabled")

    # Set the sender server-side so a user cannot impersonate someone else
    invoice.from_user = f"{current_user.username}@{settings.INSTANCE_DOMAIN}"

    try:
        result = await send_federated_invoice(invoice)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Invoice konnte nicht zugestellt werden: {e}")
    return result


@router.post("/invoice/receive")
async def receive_invoice(
    invoice: FederatedInvoice,
    db: Session = Depends(get_db),
    x_signature: Optional[str] = Header(default=None),
):
    """Receive a signed invoice from another instance (server-to-server).

    Authentication is by cryptographic signature (X-Signature header), not by
    user session – the call originates from a peer instance.
    """
    from app.services.federation_service import verify_and_store_invoice
    from app.models.transaction import Transaction
    import base64
    from pathlib import Path

    if not settings.FEDERATION_ENABLED:
        raise HTTPException(status_code=403, detail="Federation not enabled")

    if not x_signature:
        raise HTTPException(status_code=401, detail="Missing X-Signature header")

    # Verify the signature against the sender instance's published public key
    is_valid = await verify_and_store_invoice(invoice, x_signature)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Map the recipient to a real local user and one of their accounts
    recipient = _resolve_local_recipient(invoice.to_user, db)
    account = (
        db.query(Account)
        .filter(Account.user_id == recipient.id)
        .order_by(Account.id)
        .first()
    )
    if not account:
        raise HTTPException(
            status_code=409,
            detail=f"Recipient '{invoice.to_user}' has no account to book the invoice into",
        )

    description = f"From {invoice.from_user}: {invoice.description}"
    if invoice.currency and invoice.currency != account.currency:
        description += f" ({invoice.amount} {invoice.currency})"

    # Idempotency: ignore a duplicate delivery of the same invoice
    existing = db.query(Transaction).filter(
        Transaction.user_id == recipient.id,
        Transaction.account_id == account.id,
        Transaction.source == "federation",
        Transaction.date == invoice.date,
        Transaction.amount == invoice.amount,
        Transaction.description == description,
    ).first()
    if existing:
        return InvoiceResponse(
            invoice_id=existing.id,
            status=existing.status,
            message="Invoice already received (duplicate ignored)",
        )

    try:
        db_transaction = Transaction(
            user_id=recipient.id,
            account_id=account.id,
            date=invoice.date,
            amount=invoice.amount,
            category=invoice.category,
            description=description,
            status="pending",
            source="federation",
            requires_confirmation=True,  # von anderer Instanz = Bestätigung erforderlich
        )

        # Save first attachment if any
        if invoice.attachments:
            receipts_dir = Path(settings.RECEIPTS_PATH) / "federated"
            receipts_dir.mkdir(parents=True, exist_ok=True)
            attachment = invoice.attachments[0]
            file_data = base64.b64decode(attachment.data)
            # Use the transaction-less, collision-safe name once we have an id
            safe_name = Path(attachment.filename).name
            file_path = receipts_dir / f"{recipient.id}_{invoice.date}_{safe_name}"
            with open(file_path, "wb") as f:
                f.write(file_data)
            db_transaction.receipt_path = str(file_path)

        db.add(db_transaction)
        _apply_balance_delta(account, db_transaction.amount)
        db.commit()
        db.refresh(db_transaction)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Invoice konnte nicht gespeichert werden")

    return InvoiceResponse(
        invoice_id=db_transaction.id,
        status="pending",
        message="Invoice received and stored as pending transaction",
    )


@router.post("/invoice/{invoice_id}/accept")
async def accept_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accept a received invoice (only the recipient may do this)."""
    # verify_transaction_access ensures the invoice belongs to the current user
    transaction = verify_transaction_access(invoice_id, db, current_user)

    transaction.status = "confirmed"
    transaction.requires_confirmation = False
    db.commit()

    # NOTE: sending a confirmation back to the sender instance is tracked in #11
    return {"message": "Invoice accepted", "transaction_id": invoice_id}


@router.post("/invoice/{invoice_id}/reject")
async def reject_invoice(
    invoice_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject a received invoice and revert its balance effect."""
    from app.models.transaction import Transaction

    transaction = verify_transaction_access(invoice_id, db, current_user)

    try:
        account = db.query(Account).filter(Account.id == transaction.account_id).first()
        if account:
            _apply_balance_delta(account, -transaction.amount)
        db.delete(transaction)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Invoice konnte nicht abgelehnt werden")

    # NOTE: sending a rejection back to the sender instance is tracked in #11
    return {"message": "Invoice rejected", "reason": reason}


@router.get("/instances/{domain}")
async def get_instance_info(domain: str):
    """Fetch public key and info from another instance"""
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://{domain}/.well-known/money-instance")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not reach instance: {str(e)}")
