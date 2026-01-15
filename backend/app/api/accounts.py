from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from decimal import Decimal
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.authorization import get_user_filter, verify_account_access
from app.models.account import Account
from app.models.user import User

router = APIRouter()


# Pydantic Schemas
class AccountCreate(BaseModel):
    name: str
    type: str  # checking, savings, credit_card, cash
    iban: str | None = None
    balance: Decimal = Decimal("0.00")
    currency: str = "CHF"


class AccountUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    iban: str | None = None
    balance: Decimal | None = None
    currency: str | None = None


class AccountResponse(BaseModel):
    id: int
    name: str
    type: str
    iban: str | None
    balance: Decimal
    currency: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[AccountResponse])
def list_accounts(
    user_filter = Depends(get_user_filter),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List accounts (filtered by user unless admin)"""
    accounts = db.query(Account).filter_by(**user_filter).all()
    return accounts


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account: Account = Depends(verify_account_access)
):
    """Get specific account (with access verification)"""
    return account


@router.post("/", response_model=AccountResponse, status_code=201)
def create_account(
    account: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new account"""
    db_account = Account(**account.model_dump(), user_id=current_user.id)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account: AccountUpdate,
    db_account: Account = Depends(verify_account_access),
    db: Session = Depends(get_db)
):
    """Update account (with access verification)"""
    update_data = account.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_account, key, value)

    db.commit()
    db.refresh(db_account)
    return db_account


@router.delete("/{account_id}", status_code=204)
def delete_account(
    db_account: Account = Depends(verify_account_access),
    db: Session = Depends(get_db)
):
    """Delete account (with access verification)"""
    db.delete(db_account)
    db.commit()
    return None
