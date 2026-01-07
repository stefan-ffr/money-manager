from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from app.core.database import get_db
from app.models.shared_account import SharedAccount, SharedAccountMember, SplitTransaction, SplitShare

router = APIRouter()


class SharedAccountCreate(BaseModel):
    name: str
    description: str | None = None
    currency: str = "CHF"


class MemberCreate(BaseModel):
    user_identifier: str
    instance_url: str | None = None
    role: str = "member"


class SharedAccountResponse(BaseModel):
    id: int
    name: str
    description: str | None
    currency: str

    class Config:
        from_attributes = True


class SplitTransactionCreate(BaseModel):
    shared_account_id: int
    paid_by: str
    total_amount: Decimal
    date: date
    description: str | None = None
    category: str | None = None
    split_type: str = "equal"  # equal, percentage, custom


@router.get("/", response_model=List[SharedAccountResponse])
def list_shared_accounts(db: Session = Depends(get_db)):
    """List all shared accounts"""
    return db.query(SharedAccount).all()


@router.post("/", response_model=SharedAccountResponse, status_code=201)
def create_shared_account(account: SharedAccountCreate, db: Session = Depends(get_db)):
    """Create new shared account"""
    db_account = SharedAccount(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.post("/{account_id}/members")
def add_member(account_id: int, member: MemberCreate, db: Session = Depends(get_db)):
    """Add member to shared account"""
    account = db.query(SharedAccount).filter(SharedAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Shared account not found")
    
    db_member = SharedAccountMember(
        shared_account_id=account_id,
        **member.model_dump()
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    
    return {"message": "Member added successfully", "member_id": db_member.id}


@router.post("/{account_id}/split-transaction")
async def create_split_transaction(
    account_id: int,
    transaction: SplitTransactionCreate,
    db: Session = Depends(get_db)
):
    """Create split transaction and distribute to members"""
    from app.services.split_service import create_and_distribute_split
    
    account = db.query(SharedAccount).filter(SharedAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Shared account not found")
    
    result = await create_and_distribute_split(db, account, transaction)
    return result


@router.get("/{account_id}/balance")
def get_balance(account_id: int, db: Session = Depends(get_db)):
    """Calculate who owes whom in shared account"""
    from app.services.split_service import calculate_balance
    
    account = db.query(SharedAccount).filter(SharedAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Shared account not found")
    
    balance = calculate_balance(db, account_id)
    return balance


@router.post("/{account_id}/settle")
def settle_account(account_id: int, db: Session = Depends(get_db)):
    """Calculate optimal settlement (who pays whom)"""
    from app.services.split_service import calculate_settlements
    
    account = db.query(SharedAccount).filter(SharedAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Shared account not found")
    
    settlements = calculate_settlements(db, account_id)
    return settlements
