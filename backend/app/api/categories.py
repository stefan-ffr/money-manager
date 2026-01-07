from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.core.database import get_db
from app.models.category import Category

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
def list_categories(db: Session = Depends(get_db)):
    """List all categories"""
    return db.query(Category).all()


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create new category"""
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/easytax-export")
def export_easytax(
    year: int,
    db: Session = Depends(get_db)
):
    """Export transactions in EasyTax format"""
    from fastapi.responses import StreamingResponse
    from io import StringIO
    import csv
    from datetime import date
    from app.models.transaction import Transaction
    
    # Query transactions for the year
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    transactions = db.query(Transaction).filter(
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
