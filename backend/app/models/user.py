from sqlalchemy import Column, Integer, String, Boolean, LargeBinary, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    credentials = relationship("WebAuthnCredential", back_populates="user", cascade="all, delete-orphan")


class WebAuthnCredential(Base):
    """WebAuthn credential storage for Passkey authentication"""
    __tablename__ = "webauthn_credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # WebAuthn specific fields
    credential_id = Column(LargeBinary, unique=True, nullable=False)  # Unique credential identifier
    public_key = Column(LargeBinary, nullable=False)  # Public key for verification
    sign_count = Column(Integer, default=0)  # Counter to prevent replay attacks

    # Optional metadata
    device_name = Column(String(100), nullable=True)  # e.g., "iPhone 15 Pro", "YubiKey"
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="credentials")
