from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.authorization import verify_account_access
from app.models.user import User
from app.services.bank_import_service import BankImportService, setup_bank_account

router = APIRouter()


class BankAccountSetup(BaseModel):
    account_id: int
    bank_name: str
    bank_identifier: str  # IBAN oder Account Number
    enable_auto_import: bool = True


class ImportResult(BaseModel):
    success: bool
    bank: Optional[str] = None
    account_id: Optional[int] = None
    account_name: Optional[str] = None
    transactions_created: Optional[int] = None
    duplicates_skipped: Optional[int] = None
    total_parsed: Optional[int] = None
    error: Optional[str] = None


@router.post("/bank/setup")
async def setup_account_for_bank_import(
    setup: BankAccountSetup,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Konfiguriere Account für automatischen Bank Import
    
    Setze bank_identifier (IBAN oder Account Number), damit beim CSV Import
    das System automatisch das richtige Konto findet.
    
    Example:
        {
            "account_id": 1,
            "bank_name": "PostFinance",
            "bank_identifier": "CH1234567890",
            "enable_auto_import": true
        }
    """
    # Verify the current user owns this account
    verify_account_access(setup.account_id, db, current_user)

    try:
        account = setup_bank_account(
            db=db,
            account_id=setup.account_id,
            bank_name=setup.bank_name,
            bank_identifier=setup.bank_identifier,
            enable_auto_import=setup.enable_auto_import
        )
        
        return {
            "message": "Bank account configured",
            "account": {
                "id": account.id,
                "name": account.name,
                "bank_name": account.bank_name,
                "bank_identifier": account.bank_identifier,
                "auto_import_enabled": account.bank_import_enabled
            }
        }
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("/bank/import", response_model=ImportResult)
async def import_bank_csv(
    file: UploadFile = File(...),
    account_id: Optional[int] = None,
    auto_match: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Importiere Bank CSV mit automatischem Account Matching
    
    Unterstützte Banken:
    - PostFinance
    - UBS
    - Raiffeisen
    - ZKB (Zürcher Kantonalbank)
    - Credit Suisse
    
    Auto-Matching:
    Wenn auto_match=True und account_id nicht gegeben, versucht das System
    automatisch den richtigen Account zu finden basierend auf IBAN/Account Number
    im CSV.
    
    Voraussetzung für Auto-Match:
    Account muss bank_identifier gesetzt haben (siehe /bank/setup)
    
    Args:
        file: CSV File Upload
        account_id: Optional - spezifischer Account
        auto_match: Wenn True, automatisches Account-Matching
    
    Returns:
        ImportResult mit Details zum Import
    """
    # If a specific account is given, verify the current user owns it
    if account_id is not None:
        verify_account_access(account_id, db, current_user)

    # Read CSV content (tolerate non-UTF-8 bank exports)
    content = await file.read()
    try:
        csv_content = content.decode('utf-8-sig')
    except UnicodeDecodeError:
        csv_content = content.decode('latin-1')

    # Import service – scoped to the current user's accounts
    service = BankImportService(db)
    try:
        result = service.import_csv(
            csv_content=csv_content,
            account_id=account_id,
            auto_match=auto_match,
            user_id=current_user.id
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(500, detail={"success": False, "error": f"Import fehlgeschlagen: {e}"})

    if not result['success']:
        raise HTTPException(400, detail=result)

    return ImportResult(**result)


@router.get("/bank/supported")
async def get_supported_banks():
    """
    Liste aller unterstützten Banken für CSV Import
    """
    return {
        "banks": [
            {
                "id": "postfinance",
                "name": "PostFinance",
                "format": "Semicolon-separated (;)",
                "encoding": "UTF-8",
                "date_format": "DD.MM.YYYY",
                "decimal_separator": "."
            },
            {
                "id": "ubs",
                "name": "UBS",
                "format": "Comma-separated (,)",
                "encoding": "UTF-8",
                "date_format": "YYYY-MM-DD",
                "decimal_separator": "."
            },
            {
                "id": "raiffeisen",
                "name": "Raiffeisen",
                "format": "Semicolon-separated (;)",
                "encoding": "UTF-8",
                "date_format": "DD.MM.YYYY",
                "decimal_separator": "."
            },
            {
                "id": "zkb",
                "name": "Zürcher Kantonalbank",
                "format": "Semicolon-separated (;)",
                "encoding": "UTF-8",
                "date_format": "DD.MM.YYYY",
                "decimal_separator": "."
            },
            {
                "id": "credit_suisse",
                "name": "Credit Suisse",
                "format": "Comma-separated (,)",
                "encoding": "UTF-8",
                "date_format": "YYYY-MM-DD",
                "decimal_separator": "."
            }
        ]
    }


@router.get("/bank/account/{account_id}/info")
async def get_bank_account_info(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Hole Bank Import Info für Account
    """
    # Verify ownership and load the account
    account = verify_account_access(account_id, db, current_user)

    return {
        "account_id": account.id,
        "account_name": account.name,
        "bank_configured": bool(account.bank_name and account.bank_identifier),
        "bank_name": account.bank_name,
        "bank_identifier": account.bank_identifier,
        "auto_import_enabled": account.bank_import_enabled,
        "last_import": account.last_import_date.isoformat() if account.last_import_date else None
    }
