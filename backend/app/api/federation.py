from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import List
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()


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
async def send_invoice(invoice: FederatedInvoice, db: Session = Depends(get_db)):
    """Send invoice to another instance"""
    from app.services.federation_service import send_federated_invoice
    
    if not settings.FEDERATION_ENABLED:
        raise HTTPException(status_code=403, detail="Federation not enabled")
    
    result = await send_federated_invoice(invoice)
    return result


@router.post("/invoice/receive")
async def receive_invoice(invoice: FederatedInvoice, signature: str, db: Session = Depends(get_db)):
    """Receive invoice from another instance"""
    from app.services.federation_service import verify_and_store_invoice
    from app.models.transaction import Transaction
    import base64
    from pathlib import Path
    
    if not settings.FEDERATION_ENABLED:
        raise HTTPException(status_code=403, detail="Federation not enabled")
    
    # Verify signature
    is_valid = await verify_and_store_invoice(invoice, signature)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Create provisional transaction
    db_transaction = Transaction(
        account_id=1,  # TODO: Map to correct account
        date=invoice.date,
        amount=invoice.amount,
        category=invoice.category,
        description=f"From {invoice.from_user}: {invoice.description}",
        status="pending",
        source="federation",
        requires_confirmation=True  # Von anderer Instanz = Bestätigung erforderlich
    )
    
    # Save attachments if any
    if invoice.attachments:
        receipts_dir = Path(settings.RECEIPTS_PATH) / "federated"
        receipts_dir.mkdir(parents=True, exist_ok=True)
        
        for attachment in invoice.attachments:
            file_data = base64.b64decode(attachment.data)
            file_path = receipts_dir / attachment.filename
            with open(file_path, "wb") as f:
                f.write(file_data)
            db_transaction.receipt_path = str(file_path)
            break  # Only use first attachment for now
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return InvoiceResponse(
        invoice_id=db_transaction.id,
        status="pending",
        message="Invoice received and stored as pending transaction"
    )


@router.post("/invoice/{invoice_id}/accept")
async def accept_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Accept received invoice"""
    from app.models.transaction import Transaction
    
    transaction = db.query(Transaction).filter(Transaction.id == invoice_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    transaction.status = "confirmed"
    db.commit()
    
    # TODO: Send confirmation back to sender instance
    
    return {"message": "Invoice accepted", "transaction_id": invoice_id}


@router.post("/invoice/{invoice_id}/reject")
async def reject_invoice(invoice_id: int, reason: str, db: Session = Depends(get_db)):
    """Reject received invoice"""
    from app.models.transaction import Transaction
    
    transaction = db.query(Transaction).filter(Transaction.id == invoice_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Delete transaction
    db.delete(transaction)
    db.commit()
    
    # TODO: Send rejection back to sender instance
    
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
