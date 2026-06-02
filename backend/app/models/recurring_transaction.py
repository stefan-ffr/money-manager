from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class RecurringTransaction(Base):
    """A rule that creates a transaction on a recurring schedule."""
    __tablename__ = "recurring_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)

    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String(50), nullable=True)
    description = Column(String(500), nullable=True)

    # daily, weekly, monthly, yearly
    interval = Column(String(20), nullable=False, default="monthly")
    next_run = Column(Date, nullable=False, index=True)  # next date a transaction is due
    last_run = Column(Date, nullable=True)               # last date one was created
    active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User")
    account = relationship("Account")
