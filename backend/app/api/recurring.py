from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.authorization import verify_account_access
from app.models.user import User
from app.models.recurring_transaction import RecurringTransaction
from app.services.recurring_service import process_due_recurring

router = APIRouter()

VALID_INTERVALS = {"daily", "weekly", "monthly", "yearly"}


class RecurringCreate(BaseModel):
    account_id: int
    amount: Decimal
    category: Optional[str] = None
    description: Optional[str] = None
    interval: str = "monthly"
    next_run: date
    active: bool = True


class RecurringUpdate(BaseModel):
    amount: Optional[Decimal] = None
    category: Optional[str] = None
    description: Optional[str] = None
    interval: Optional[str] = None
    next_run: Optional[date] = None
    active: Optional[bool] = None


class RecurringResponse(BaseModel):
    id: int
    account_id: int
    amount: Decimal
    category: Optional[str]
    description: Optional[str]
    interval: str
    next_run: date
    last_run: Optional[date]
    active: bool

    class Config:
        from_attributes = True


def _get_owned_rule(rule_id: int, db: Session, current_user: User) -> RecurringTransaction:
    rule = db.query(RecurringTransaction).filter(RecurringTransaction.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    if not current_user.is_superuser and rule.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Kein Zugriff auf diese Dauerbuchung")
    return rule


@router.get("/", response_model=List[RecurringResponse])
def list_recurring(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the current user's recurring transactions."""
    query = db.query(RecurringTransaction)
    if not current_user.is_superuser:
        query = query.filter(RecurringTransaction.user_id == current_user.id)
    return query.order_by(RecurringTransaction.next_run).all()


@router.post("/", response_model=RecurringResponse, status_code=201)
def create_recurring(
    rule: RecurringCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a recurring transaction rule for one of the user's accounts."""
    if rule.interval not in VALID_INTERVALS:
        raise HTTPException(status_code=400, detail=f"interval must be one of {sorted(VALID_INTERVALS)}")
    verify_account_access(rule.account_id, db, current_user)

    db_rule = RecurringTransaction(**rule.model_dump(), user_id=current_user.id)
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.put("/{rule_id}", response_model=RecurringResponse)
def update_recurring(
    rule_id: int,
    update: RecurringUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a recurring transaction rule."""
    rule = _get_owned_rule(rule_id, db, current_user)

    data = update.model_dump(exclude_unset=True)
    if "interval" in data and data["interval"] not in VALID_INTERVALS:
        raise HTTPException(status_code=400, detail=f"interval must be one of {sorted(VALID_INTERVALS)}")
    for key, value in data.items():
        setattr(rule, key, value)

    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=204)
def delete_recurring(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a recurring transaction rule (created transactions are kept)."""
    rule = _get_owned_rule(rule_id, db, current_user)
    db.delete(rule)
    db.commit()
    return None


@router.post("/process")
def process_recurring(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate all of the current user's due recurring transactions now."""
    created = process_due_recurring(db, user_id=current_user.id)
    return {"message": "Recurring transactions processed", "created": created}
