from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.shared_account import SharedAccount, SharedAccountMember, SplitTransaction, SplitShare

router = APIRouter()


def verify_shared_account_membership(
    account_id: int, db: Session, current_user: User
) -> SharedAccount:
    """Return the shared account only if the current user is a member of it."""
    account = db.query(SharedAccount).filter(SharedAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Shared account not found")

    if current_user.is_superuser:
        return account

    is_member = db.query(SharedAccountMember).filter(
        SharedAccountMember.shared_account_id == account_id,
        SharedAccountMember.user_identifier == current_user.email,
    ).first()
    if not is_member:
        raise HTTPException(status_code=403, detail="Kein Zugriff auf dieses Gemeinschaftskonto")
    return account


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


class MemberResponse(BaseModel):
    id: int
    user_identifier: str
    instance_url: str | None
    role: str

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
def list_shared_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List shared accounts the current user is a member of."""
    if current_user.is_superuser:
        return db.query(SharedAccount).all()

    return (
        db.query(SharedAccount)
        .join(SharedAccountMember, SharedAccountMember.shared_account_id == SharedAccount.id)
        .filter(SharedAccountMember.user_identifier == current_user.email)
        .all()
    )


@router.post("/", response_model=SharedAccountResponse, status_code=201)
def create_shared_account(
    account: SharedAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a shared account and link the creator as its owner member."""
    db_account = SharedAccount(**account.model_dump())
    db.add(db_account)
    db.flush()  # assign an id before adding the owner member

    # Link the creator so the account shows up for them and access is scoped
    owner = SharedAccountMember(
        shared_account_id=db_account.id,
        user_identifier=current_user.email,
        role="owner",
    )
    db.add(owner)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.post("/{account_id}/members")
def add_member(
    account_id: int,
    member: MemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add (link) a member to a shared account the current user belongs to."""
    verify_shared_account_membership(account_id, db, current_user)

    # Avoid duplicate links for the same identifier
    existing = db.query(SharedAccountMember).filter(
        SharedAccountMember.shared_account_id == account_id,
        SharedAccountMember.user_identifier == member.user_identifier,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Mitglied ist bereits verknüpft")

    db_member = SharedAccountMember(
        shared_account_id=account_id,
        **member.model_dump()
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)

    return {"message": "Member added successfully", "member_id": db_member.id}


@router.get("/{account_id}/members", response_model=List[MemberResponse])
def list_members(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List members (links) of a shared account the current user belongs to."""
    verify_shared_account_membership(account_id, db, current_user)
    return (
        db.query(SharedAccountMember)
        .filter(SharedAccountMember.shared_account_id == account_id)
        .all()
    )


@router.post("/{account_id}/split-transaction")
async def create_split_transaction(
    account_id: int,
    transaction: SplitTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create split transaction and distribute to members"""
    from app.services.split_service import create_and_distribute_split

    account = verify_shared_account_membership(account_id, db, current_user)

    result = await create_and_distribute_split(db, account, transaction)
    return result


@router.get("/{account_id}/balance")
def get_balance(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calculate who owes whom in shared account"""
    from app.services.split_service import calculate_balance

    verify_shared_account_membership(account_id, db, current_user)

    balance = calculate_balance(db, account_id)
    return balance


@router.post("/{account_id}/settle")
def settle_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calculate optimal settlement (who pays whom)"""
    from app.services.split_service import calculate_settlements

    verify_shared_account_membership(account_id, db, current_user)

    settlements = calculate_settlements(db, account_id)
    return settlements
