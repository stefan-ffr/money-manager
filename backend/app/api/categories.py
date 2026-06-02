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


class CategoryUpdate(BaseModel):
    name: str | None = None
    easytax_code: str | None = None
    parent_id: int | None = None


def _get_writable_category(category_id: int, db: Session, current_user: User) -> Category:
    """Load a category the current user may modify.

    System categories (user_id is NULL) are writable by admins only; user
    categories only by their owner (admins may edit any).
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if current_user.is_superuser:
        return category
    if category.user_id is None:
        raise HTTPException(status_code=403, detail="Systemkategorien können nur von Admins geändert werden")
    if category.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Kein Zugriff auf diese Kategorie")
    return category


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


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    update: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a category the current user owns (admins may edit any)."""
    category = _get_writable_category(category_id, db, current_user)

    data = update.model_dump(exclude_unset=True)
    # Prevent a category from becoming its own parent
    if data.get("parent_id") == category_id:
        raise HTTPException(status_code=400, detail="Eine Kategorie kann nicht ihr eigenes Elternteil sein")
    for key, value in data.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a category. Child categories are detached (parent set to NULL).

    Transactions keep their category name (stored as plain text), so existing
    bookings are not affected.
    """
    category = _get_writable_category(category_id, db, current_user)

    # Detach any children so the FK constraint is not violated
    db.query(Category).filter(Category.parent_id == category_id).update(
        {Category.parent_id: None}
    )
    db.delete(category)
    db.commit()
    return None


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
