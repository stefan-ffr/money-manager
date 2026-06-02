"""API-key generation and authentication for external integrations."""

import hashlib
import secrets
from datetime import datetime
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.api_key import ApiKey
from app.models.user import User

TOKEN_PREFIX = "mmk_"  # money-manager key


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def generate_api_key() -> tuple[str, str, str]:
    """Return (plaintext_token, key_prefix, key_hash). Plaintext is shown once."""
    token = TOKEN_PREFIX + secrets.token_urlsafe(32)
    return token, token[:12], hash_token(token)


def get_user_from_api_key(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> User:
    """Authenticate a request via the X-API-Key header and return the user."""
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-Key header")

    key = db.query(ApiKey).filter(
        ApiKey.key_hash == hash_token(x_api_key),
        ApiKey.active.is_(True),
    ).first()
    if not key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    user = db.query(User).filter(User.id == key.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive")

    key.last_used = datetime.utcnow()
    db.commit()
    return user
