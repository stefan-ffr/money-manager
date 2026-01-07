from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
from app.core.database import get_db
from app.core.config import settings
from app.models.category import Category

router = APIRouter()


# Pydantic Schemas
class UserPreferences(BaseModel):
    default_account_id: int | None = None
    default_currency: str = "CHF"
    date_format: str = "DD.MM.YYYY"
    language: str = "de"
    theme: str = "light"
    email_notifications: bool = True


class FederationSettings(BaseModel):
    enabled: bool
    instance_domain: str
    auto_accept_invoices: bool = False
    trusted_instances: List[str] = []


class MirrorInstanceConfig(BaseModel):
    url: str
    priority: int
    sync_direction: str  # push, pull, bidirectional
    sync_enabled: bool = True
    sync_interval_minutes: int = 5


class TelegramSettings(BaseModel):
    bot_token: str | None = None
    allowed_users: List[int] = []
    auto_confirm_enabled: bool = False
    ocr_enabled: bool = True


class CategoryMapping(BaseModel):
    category_name: str
    easytax_code: str
    parent_category: str | None = None


class SecuritySettings(BaseModel):
    passkey_enabled: bool = False
    two_factor_enabled: bool = False
    session_timeout_minutes: int = 60
    require_confirmation_for: List[str] = ["telegram", "federation", "csv_import"]


# GET Endpoints
@router.get("/preferences")
async def get_preferences(db: Session = Depends(get_db)):
    """Get user preferences"""
    # TODO: Store in database per user
    return {
        "default_account_id": None,
        "default_currency": "CHF",
        "date_format": "DD.MM.YYYY",
        "language": "de",
        "theme": "light",
        "email_notifications": True
    }


@router.get("/federation")
async def get_federation_settings(db: Session = Depends(get_db)):
    """Get federation settings"""
    return {
        "enabled": settings.FEDERATION_ENABLED,
        "instance_domain": settings.INSTANCE_DOMAIN,
        "auto_accept_invoices": False,
        "trusted_instances": []
    }


@router.get("/mirrors")
async def get_mirror_instances(db: Session = Depends(get_db)):
    """Get configured mirror instances"""
    # TODO: Load from database
    return []


@router.get("/telegram")
async def get_telegram_settings(db: Session = Depends(get_db)):
    """Get Telegram bot settings"""
    return {
        "bot_token": settings.TELEGRAM_BOT_TOKEN if settings.TELEGRAM_BOT_TOKEN else None,
        "allowed_users": settings.get_allowed_telegram_users(),
        "auto_confirm_enabled": False,
        "ocr_enabled": True
    }


@router.get("/categories/mappings")
async def get_category_mappings(db: Session = Depends(get_db)):
    """Get EasyTax category mappings"""
    categories = db.query(Category).all()
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "easytax_code": cat.easytax_code,
            "parent_id": cat.parent_id
        }
        for cat in categories
    ]


@router.get("/security")
async def get_security_settings(db: Session = Depends(get_db)):
    """Get security settings"""
    return {
        "passkey_enabled": False,
        "two_factor_enabled": False,
        "session_timeout_minutes": 60,
        "require_confirmation_for": ["telegram", "federation", "csv_import"]
    }


# POST/PUT Endpoints
@router.put("/preferences")
async def update_preferences(prefs: UserPreferences, db: Session = Depends(get_db)):
    """Update user preferences"""
    # TODO: Store in database per user
    return {"message": "Preferences updated", "preferences": prefs.model_dump()}


@router.put("/federation")
async def update_federation_settings(settings: FederationSettings, db: Session = Depends(get_db)):
    """Update federation settings"""
    # TODO: Update in config/database
    return {"message": "Federation settings updated"}


@router.post("/mirrors")
async def add_mirror_instance(mirror: MirrorInstanceConfig, db: Session = Depends(get_db)):
    """Add new mirror instance"""
    from app.models.shared_account import MirrorInstance
    
    # Verify instance is reachable
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{mirror.url}/.well-known/money-instance", timeout=5.0)
            response.raise_for_status()
            instance_data = response.json()
    except Exception as e:
        raise HTTPException(400, f"Could not reach instance: {str(e)}")
    
    # TODO: Create MirrorInstance in database
    return {"message": "Mirror instance added", "instance": instance_data}


@router.delete("/mirrors/{mirror_id}")
async def remove_mirror_instance(mirror_id: int, db: Session = Depends(get_db)):
    """Remove mirror instance"""
    # TODO: Delete from database
    return {"message": "Mirror instance removed"}


@router.put("/telegram")
async def update_telegram_settings(settings: TelegramSettings, db: Session = Depends(get_db)):
    """Update Telegram settings"""
    # TODO: Update environment or config
    return {"message": "Telegram settings updated"}


@router.post("/categories/mappings")
async def create_category_mapping(mapping: CategoryMapping, db: Session = Depends(get_db)):
    """Create or update category mapping"""
    category = db.query(Category).filter(Category.name == mapping.category_name).first()
    
    if category:
        category.easytax_code = mapping.easytax_code
    else:
        category = Category(
            name=mapping.category_name,
            easytax_code=mapping.easytax_code
        )
        db.add(category)
    
    db.commit()
    db.refresh(category)
    
    return {"message": "Category mapping created", "category": category}


@router.put("/security")
async def update_security_settings(settings: SecuritySettings, db: Session = Depends(get_db)):
    """Update security settings"""
    # TODO: Store in database
    return {"message": "Security settings updated"}


# Utility Endpoints
@router.post("/test-federation")
async def test_federation_connection(instance_url: str):
    """Test connection to another instance"""
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{instance_url}/.well-known/money-instance",
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "status": "success",
                "instance_id": data.get("instance_id"),
                "federation_enabled": data.get("federation_enabled"),
                "message": "Connection successful"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.post("/generate-federation-keys")
async def generate_federation_keys():
    """Generate new RSA key pair for federation"""
    from app.federation.crypto import generate_key_pair, get_public_key_pem
    
    generate_key_pair()
    public_key = get_public_key_pem()
    
    return {
        "message": "New key pair generated",
        "public_key": public_key
    }


@router.get("/export-data")
async def export_all_data(db: Session = Depends(get_db)):
    """Export all user data as JSON"""
    from app.models.account import Account
    from app.models.transaction import Transaction
    
    accounts = db.query(Account).all()
    transactions = db.query(Transaction).all()
    
    return {
        "accounts": [acc.__dict__ for acc in accounts],
        "transactions": [tx.__dict__ for tx in transactions],
        "exported_at": "2024-12-07T12:00:00Z"
    }


@router.get("/currencies")
async def get_currencies():
    """Get list of all supported currencies"""
    from app.core.currencies import get_all_currencies
    
    return {
        "currencies": get_all_currencies(),
        "default": "CHF"
    }
