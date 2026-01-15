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
from app.models.user import User

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
    """Create new transaction"""
    # Verify that the account belongs to the user
    account = verify_account_access(transaction.account_id, db, current_user)

    db_transaction = Transaction(**transaction.model_dump(), user_id=current_user.id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction: TransactionUpdate,
    db_transaction: Transaction = Depends(verify_transaction_access),
    db: Session = Depends(get_db)
):
    """Update transaction (with access verification)"""
    update_data = transaction.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_transaction, key, value)

    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    db_transaction: Transaction = Depends(verify_transaction_access),
    db: Session = Depends(get_db)
):
    """Delete transaction (with access verification)"""
    # Delete receipt file if exists
    if db_transaction.receipt_path and os.path.exists(db_transaction.receipt_path):
        os.remove(db_transaction.receipt_path)

    db.delete(db_transaction)
    db.commit()
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
