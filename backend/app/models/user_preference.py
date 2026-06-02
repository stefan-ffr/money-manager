from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class UserPreference(Base):
    """Per-user display/UX preferences (one row per user)."""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    default_account_id = Column(Integer, nullable=True)
    default_currency = Column(String(3), default="CHF")
    date_format = Column(String(20), default="DD.MM.YYYY")
    language = Column(String(5), default="de")
    theme = Column(String(10), default="light")
    email_notifications = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
