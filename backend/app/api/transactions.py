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
from app.models.transaction import Transaction

router = APIRouter()


# Pydantic Schemas
class TransactionCreate(BaseModel):
    account_id: int
    date: date
    amount: Decimal
    category: Optional[str] = None
    description: Optional[str] = None
    status: str = "pending"


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
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List transactions with optional filters"""
    query = db.query(Transaction)
    
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if status:
        query = query.filter(Transaction.status == status)
    
    transactions = query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Get specific transaction"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.post("/", response_model=TransactionResponse, status_code=201)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """Create new transaction"""
    db_transaction = Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db)
):
    """Update transaction"""
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    update_data = transaction.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_transaction, key, value)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Delete transaction"""
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Delete receipt file if exists
    if db_transaction.receipt_path and os.path.exists(db_transaction.receipt_path):
        os.remove(db_transaction.receipt_path)
    
    db.delete(db_transaction)
    db.commit()
    return None


@router.post("/{transaction_id}/receipt")
async def upload_receipt(
    transaction_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload receipt for transaction"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Create receipts directory structure
    year = transaction.date.year
    month = transaction.date.month
    receipts_dir = Path(settings.RECEIPTS_PATH) / str(year) / f"{month:02d}"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_extension = Path(file.filename).suffix
    file_path = receipts_dir / f"transaction_{transaction_id}{file_extension}"
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Update transaction
    transaction.receipt_path = str(file_path)
    db.commit()
    
    return {"message": "Receipt uploaded successfully", "path": str(file_path)}


@router.get("/{transaction_id}/receipt")
async def get_receipt(transaction_id: int, db: Session = Depends(get_db)):
    """Get receipt for transaction"""
    from fastapi.responses import FileResponse
    
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction or not transaction.receipt_path:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    if not os.path.exists(transaction.receipt_path):
        raise HTTPException(status_code=404, detail="Receipt file not found")
    
    return FileResponse(transaction.receipt_path)
