from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # checking, savings, credit_card, cash
    iban = Column(String(34), nullable=True)
    balance = Column(Numeric(10, 2), default=0.00)
    currency = Column(String(3), default="CHF")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Bank Integration
    bank_name = Column(String(100), nullable=True)  # "PostFinance", "UBS", "Raiffeisen"
    bank_identifier = Column(String(100), nullable=True)  # IBAN oder Account Number für Matching
    bank_import_enabled = Column(Boolean, default=False)  # Auto-Import aktiviert?
    last_import_date = Column(DateTime, nullable=True)  # Letzter erfolgreicher Import

    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    reconciliations = relationship("BankReconciliation", back_populates="account", cascade="all, delete-orphan")
