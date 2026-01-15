"""Two-Factor Authentication (2FA) API endpoints"""

import base64
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.backup_code import BackupCode
from app.services.totp_service import totp_service

router = APIRouter()

# In-memory storage for 2FA setup sessions (in production, use Redis)
setup_sessions: dict[int, str] = {}


class TwoFactorSetupResponse(BaseModel):
    """Response for beginning 2FA setup"""
    qr_code: str  # Base64 encoded PNG
    secret: str  # For manual entry
    issuer: str


class TwoFactorCompleteRequest(BaseModel):
    """Request to complete 2FA setup"""
    code: str


class TwoFactorCompleteResponse(BaseModel):
    """Response after completing 2FA setup"""
    backup_codes: List[str]
    message: str


class TwoFactorStatusResponse(BaseModel):
    """Response for 2FA status"""
    totp_enabled: bool
    require_2fa: bool
    backup_codes_count: int


class TwoFactorDisableRequest(BaseModel):
    """Request to disable 2FA"""
    code: str


@router.post("/setup/begin", response_model=TwoFactorSetupResponse)
async def begin_2fa_setup(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Begin 2FA setup - generate QR code and secret

    Returns QR code image and secret for user to add to authenticator app
    """
    if current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled"
        )

    # Generate new TOTP secret
    secret = totp_service.generate_secret()

    # Store in session (temporary storage)
    setup_sessions[current_user.id] = secret

    # Generate provisioning URI
    uri = totp_service.get_provisioning_uri(current_user.username, secret)

    # Generate QR code
    qr_code_bytes = totp_service.generate_qr_code(uri)
    qr_code_base64 = base64.b64encode(qr_code_bytes).decode()

    return TwoFactorSetupResponse(
        qr_code=qr_code_base64,
        secret=secret,
        issuer="Money Manager"
    )


@router.post("/setup/complete", response_model=TwoFactorCompleteResponse)
async def complete_2fa_setup(
    request: TwoFactorCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete 2FA setup - verify code and save

    Verifies the TOTP code, enables 2FA, and generates backup codes
    """
    # Get secret from session
    secret = setup_sessions.get(current_user.id)
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Setup session expired. Please start setup again."
        )

    # Verify TOTP code
    if not totp_service.verify_totp(secret, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid TOTP code"
        )

    # Encrypt and save secret
    encrypted_secret = totp_service.encrypt_secret(secret)
    current_user.totp_secret = encrypted_secret
    current_user.totp_enabled = True

    # Generate backup codes
    backup_codes = totp_service.generate_backup_codes(count=10)

    # Save backup codes (hashed)
    for code in backup_codes:
        code_hash = totp_service.hash_backup_code(code)
        db_backup_code = BackupCode(
            user_id=current_user.id,
            code_hash=code_hash
        )
        db.add(db_backup_code)

    db.commit()

    # Clean up session
    del setup_sessions[current_user.id]

    return TwoFactorCompleteResponse(
        backup_codes=backup_codes,
        message="2FA enabled successfully. Save your backup codes in a secure place!"
    )


@router.get("/status", response_model=TwoFactorStatusResponse)
async def get_2fa_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get 2FA status for current user"""
    # Count unused backup codes
    unused_backup_codes = db.query(BackupCode).filter(
        BackupCode.user_id == current_user.id,
        BackupCode.used == False
    ).count()

    return TwoFactorStatusResponse(
        totp_enabled=current_user.totp_enabled,
        require_2fa=current_user.require_2fa,
        backup_codes_count=unused_backup_codes
    )


@router.post("/disable")
async def disable_2fa(
    request: TwoFactorDisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disable 2FA for current user

    Requires current TOTP code or backup code for verification
    """
    if not current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )

    # Verify TOTP code
    secret = totp_service.decrypt_secret(current_user.totp_secret)
    if not totp_service.verify_totp(secret, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid TOTP code"
        )

    # Disable 2FA
    current_user.totp_secret = None
    current_user.totp_enabled = False
    current_user.totp_last_used_at = None

    # Delete all backup codes
    db.query(BackupCode).filter(BackupCode.user_id == current_user.id).delete()

    db.commit()

    return {"message": "2FA disabled successfully"}


@router.post("/regenerate-backup-codes", response_model=TwoFactorCompleteResponse)
async def regenerate_backup_codes(
    request: TwoFactorDisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate backup codes

    Requires current TOTP code for verification
    Deletes all old backup codes and generates new ones
    """
    if not current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )

    # Verify TOTP code
    secret = totp_service.decrypt_secret(current_user.totp_secret)
    if not totp_service.verify_totp(secret, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid TOTP code"
        )

    # Delete all old backup codes
    db.query(BackupCode).filter(BackupCode.user_id == current_user.id).delete()

    # Generate new backup codes
    backup_codes = totp_service.generate_backup_codes(count=10)

    # Save new backup codes (hashed)
    for code in backup_codes:
        code_hash = totp_service.hash_backup_code(code)
        db_backup_code = BackupCode(
            user_id=current_user.id,
            code_hash=code_hash
        )
        db.add(db_backup_code)

    db.commit()

    return TwoFactorCompleteResponse(
        backup_codes=backup_codes,
        message="Backup codes regenerated successfully. Old codes are now invalid!"
    )
