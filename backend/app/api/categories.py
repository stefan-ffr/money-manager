from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.authorization import get_user_filter
from app.models.category import Category
from app.models.user import User

router = APIRouter()


class CategoryCreate(BaseModel):
    name: str
    easytax_code: str | None = None
    parent_id: int | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    easytax_code: str | None
    parent_id: int | None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[CategoryResponse])
def list_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List categories (system categories + user's own categories, or all if admin)"""
    if current_user.is_superuser:
        # Admins see all categories
        return db.query(Category).all()
    else:
        # Regular users see system categories (user_id is NULL) + their own categories
        return db.query(Category).filter(
            (Category.user_id == None) | (Category.user_id == current_user.id)
        ).all()


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new category (system category if admin, user category otherwise)"""
    # Only admins can create system categories (user_id=NULL)
    # Regular users create user-specific categories
    user_id = None if current_user.is_superuser else current_user.id

    db_category = Category(**category.model_dump(), user_id=user_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/easytax-export")
def export_easytax(
    year: int,
    user_filter = Depends(get_user_filter),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export transactions in EasyTax format (filtered by user unless admin)"""
    from fastapi.responses import StreamingResponse
    from io import StringIO
    import csv
    from datetime import date
    from app.models.transaction import Transaction

    # Query transactions for the year
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    transactions = db.query(Transaction).filter_by(**user_filter).filter(
        Transaction.date >= start_date,
        Transaction.date <= end_date,
        Transaction.status == "confirmed"
    ).order_by(Transaction.date).all()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['Datum', 'Betrag', 'Kategorie', 'Beschreibung', 'Belegnummer'])
    
    for tx in transactions:
        writer.writerow([
            tx.date.strftime('%d.%m.%Y'),
            f"{tx.amount:.2f}",
            tx.category or '',
            tx.description or '',
            f"TX-{tx.id}"
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=easytax_{year}.csv"}
    )
