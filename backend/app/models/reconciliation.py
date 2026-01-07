"""
Bank Reconciliation Models

Models for comparing bank statements with application transactions.
"""

from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class BankReconciliation(Base):
    """Bank Reconciliation Session"""
    __tablename__ = "bank_reconciliations"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)

    # Period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Balances
    bank_balance = Column(Numeric(precision=10, scale=2), nullable=True)
    app_balance = Column(Numeric(precision=10, scale=2), nullable=True)
    difference = Column(Numeric(precision=10, scale=2), nullable=True)

    # Status
    status = Column(String(20), default="pending")  # pending, in_review, completed

    # Statistics
    total_bank_transactions = Column(Integer, default=0)
    matched_count = Column(Integer, default=0)
    unmatched_bank_count = Column(Integer, default=0)
    unmatched_app_count = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    account = relationship("Account", back_populates="reconciliations")
    matches = relationship("ReconciliationMatch", back_populates="reconciliation", cascade="all, delete-orphan")


class ReconciliationMatch(Base):
    """Individual match between bank transaction and app transaction"""
    __tablename__ = "reconciliation_matches"

    id = Column(Integer, primary_key=True, index=True)
    reconciliation_id = Column(Integer, ForeignKey("bank_reconciliations.id"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)  # Null if unmatched bank transaction

    # Bank Transaction Data
    bank_date = Column(DateTime, nullable=False)
    bank_amount = Column(Numeric(precision=10, scale=2), nullable=False)
    bank_description = Column(String(500), nullable=True)
    bank_reference = Column(String(200), nullable=True)

    # Match Information
    match_status = Column(String(20), nullable=False)  # matched, unmatched_bank, unmatched_app, pending
    match_confidence = Column(Integer, default=0)  # 0-100
    match_type = Column(String(20), nullable=True)  # exact, fuzzy, manual

    # User Action
    action = Column(String(20), nullable=True)  # accept, ignore, create_transaction, link_existing
    action_taken_at = Column(DateTime, nullable=True)
    user_notes = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reconciliation = relationship("BankReconciliation", back_populates="matches")
    transaction = relationship("Transaction")
