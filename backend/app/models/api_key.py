from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class ApiKey(Base):
    """A hashed API key that lets an external service (e.g. the receipt bot)
    authenticate as a user without a passkey.

    The plaintext token is shown to the user only once at creation; only its
    SHA-256 hash is stored.
    """
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=True)             # human label, e.g. "Quittungsbot"
    key_prefix = Column(String(16), nullable=False)        # first chars, shown for identification
    key_hash = Column(String(64), nullable=False, unique=True, index=True)  # sha256 hex
    active = Column(Boolean, default=True, nullable=False)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
