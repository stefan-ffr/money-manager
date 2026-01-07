"""
Bank Reconciliation API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
import io
import pandas as pd
import chardet

from app.core.database import get_db
from app.services.reconciliation_service import ReconciliationService
from app.models.reconciliation import BankReconciliation
from app.services.bank_import_service import BankImportService


router = APIRouter()


# Schemas
class ReconciliationCreate(BaseModel):
    account_id: int
    period_start: str
    period_end: str
    bank_balance: Optional[float] = None


class MatchResolve(BaseModel):
    action: str  # accept, ignore, create_transaction, link_existing
    transaction_data: Optional[dict] = None
    notes: Optional[str] = None


class ReconciliationSummary(BaseModel):
    id: int
    account_id: int
    period_start: str
    period_end: str
    status: str
    matched_count: int
    unmatched_bank_count: int
    unmatched_app_count: int
    created_at: str

    class Config:
        from_attributes = True


@router.post("/reconciliation", status_code=201)
async def create_reconciliation(
    file: UploadFile = File(...),
    account_id: int = Form(...),
    period_start: str = Form(...),
    period_end: str = Form(...),
    bank_balance: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Create a new bank reconciliation by uploading a CSV bank statement

    - Upload CSV file with bank transactions
    - Specify account and time period
    - Optionally provide bank balance for verification
    - System will automatically match transactions
    """
    # Read CSV file
    content = await file.read()

    # Detect encoding
    detected = chardet.detect(content)
    encoding = detected['encoding'] if detected['encoding'] else 'utf-8'

    # Parse CSV
    try:
        df = pd.read_csv(io.BytesIO(content), encoding=encoding, sep=None, engine='python')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")

    # Use BankImportService to parse bank transactions
    import_service = BankImportService(db)

    # Detect bank format and parse
    bank_transactions = []
    try:
        # Try to parse using existing bank parsers
        parsed_data = import_service._parse_csv_by_bank(df, None)  # Will auto-detect

        for row in parsed_data:
            bank_transactions.append({
                'date': row['date'],
                'amount': row['amount'],
                'description': row['description'],
                'reference': row.get('reference', '')
            })

    except Exception as e:
        # Fallback: Try generic parsing
        # Assume columns: Date, Description, Amount
        if len(df.columns) < 3:
            raise HTTPException(
                status_code=400,
                detail="CSV must have at least 3 columns (Date, Description, Amount)"
            )

        # Try to identify columns
        date_col = None
        amount_col = None
        desc_col = None

        for col in df.columns:
            col_lower = col.lower()
            if any(x in col_lower for x in ['date', 'datum', 'valuta']):
                date_col = col
            elif any(x in col_lower for x in ['amount', 'betrag', 'credit', 'debit', 'saldo']):
                amount_col = col
            elif any(x in col_lower for x in ['description', 'beschreibung', 'text', 'avisierung']):
                desc_col = col

        if not (date_col and amount_col):
            raise HTTPException(
                status_code=400,
                detail="Could not identify Date and Amount columns in CSV"
            )

        for _, row in df.iterrows():
            try:
                # Parse date
                date_val = pd.to_datetime(row[date_col], dayfirst=True)

                # Parse amount (handle both credit/debit or single amount column)
                amount_val = float(row[amount_col]) if pd.notna(row[amount_col]) else 0.0

                # Get description
                desc_val = str(row[desc_col]) if desc_col and pd.notna(row[desc_col]) else ""

                bank_transactions.append({
                    'date': date_val,
                    'amount': amount_val,
                    'description': desc_val,
                    'reference': ''
                })
            except Exception:
                continue  # Skip rows that can't be parsed

    if not bank_transactions:
        raise HTTPException(
            status_code=400,
            detail="No valid transactions found in CSV"
        )

    # Create reconciliation
    service = ReconciliationService(db)

    try:
        reconciliation = service.create_reconciliation(
            account_id=account_id,
            period_start=datetime.fromisoformat(period_start),
            period_end=datetime.fromisoformat(period_end),
            bank_transactions=bank_transactions,
            bank_balance=Decimal(str(bank_balance)) if bank_balance else None
        )

        return {
            "id": reconciliation.id,
            "message": "Reconciliation created successfully",
            "matched_count": reconciliation.matched_count,
            "unmatched_bank_count": reconciliation.unmatched_bank_count,
            "unmatched_app_count": reconciliation.unmatched_app_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating reconciliation: {str(e)}")


@router.get("/reconciliation", response_model=List[ReconciliationSummary])
async def list_reconciliations(
    account_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get list of all reconciliations, optionally filtered by account"""
    query = db.query(BankReconciliation)

    if account_id:
        query = query.filter(BankReconciliation.account_id == account_id)

    reconciliations = query.order_by(BankReconciliation.created_at.desc()).all()

    return [
        ReconciliationSummary(
            id=r.id,
            account_id=r.account_id,
            period_start=r.period_start.isoformat(),
            period_end=r.period_end.isoformat(),
            status=r.status,
            matched_count=r.matched_count,
            unmatched_bank_count=r.unmatched_bank_count,
            unmatched_app_count=r.unmatched_app_count,
            created_at=r.created_at.isoformat()
        )
        for r in reconciliations
    ]


@router.get("/reconciliation/{reconciliation_id}")
async def get_reconciliation(
    reconciliation_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed reconciliation with all matches"""
    service = ReconciliationService(db)

    try:
        data = service.get_reconciliation_with_matches(reconciliation_id)
        return data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/reconciliation/{reconciliation_id}/resolve/{match_id}")
async def resolve_match(
    reconciliation_id: int,
    match_id: int,
    resolve_data: MatchResolve,
    db: Session = Depends(get_db)
):
    """
    Resolve a reconciliation match with user action

    Actions:
    - accept: Accept the suggested match
    - ignore: Ignore this bank transaction (won't create in app)
    - create_transaction: Create new transaction from bank data
    - link_existing: Link to a different existing transaction
    """
    service = ReconciliationService(db)

    try:
        match = service.resolve_match(
            match_id=match_id,
            action=resolve_data.action,
            transaction_data=resolve_data.transaction_data,
            notes=resolve_data.notes
        )

        return {
            "message": "Match resolved successfully",
            "match_id": match.id,
            "action": match.action,
            "match_status": match.match_status
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resolving match: {str(e)}")


@router.post("/reconciliation/{reconciliation_id}/complete")
async def complete_reconciliation(
    reconciliation_id: int,
    db: Session = Depends(get_db)
):
    """Mark reconciliation as completed"""
    service = ReconciliationService(db)

    try:
        reconciliation = service.complete_reconciliation(reconciliation_id)

        return {
            "message": "Reconciliation completed",
            "id": reconciliation.id,
            "status": reconciliation.status,
            "completed_at": reconciliation.completed_at.isoformat()
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/reconciliation/{reconciliation_id}")
async def delete_reconciliation(
    reconciliation_id: int,
    db: Session = Depends(get_db)
):
    """Delete a reconciliation session"""
    reconciliation = db.query(BankReconciliation).filter(
        BankReconciliation.id == reconciliation_id
    ).first()

    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation not found")

    db.delete(reconciliation)
    db.commit()

    return {"message": "Reconciliation deleted successfully"}
