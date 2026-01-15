from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey, BigInteger, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String(50), nullable=True)
    description = Column(String(500), nullable=True)
    status = Column(String(20), default="pending")  # pending, confirmed, reconciled
    source = Column(String(20), default="manual")  # manual, telegram, federation, csv_import
    requires_confirmation = Column(Boolean, default=False)  # Rot markiert wenn True
    receipt_path = Column(String(255), nullable=True)
    telegram_message_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
