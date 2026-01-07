from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class SharedAccount(Base):
    """Gemeinschaftskonto für WGs, Vereine, etc."""
    __tablename__ = "shared_accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    currency = Column(String(3), default="CHF")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    members = relationship("SharedAccountMember", back_populates="shared_account", cascade="all, delete-orphan")
    split_transactions = relationship("SplitTransaction", back_populates="shared_account", cascade="all, delete-orphan")
    settlements = relationship("Settlement", back_populates="shared_account", cascade="all, delete-orphan")


class SharedAccountMember(Base):
    """Mitglieder eines Gemeinschaftskontos"""
    __tablename__ = "shared_account_members"

    id = Column(Integer, primary_key=True, index=True)
    shared_account_id = Column(Integer, ForeignKey("shared_accounts.id"), nullable=False)
    user_identifier = Column(String(255), nullable=False)  # e.g., stefan@money.babsyit.ch
    instance_url = Column(String(255), nullable=True)  # Full instance URL
    role = Column(String(20), default="member")  # owner, member, viewer
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    shared_account = relationship("SharedAccount", back_populates="members")


class SplitTransaction(Base):
    """Aufgeteilte Transaktionen im Gemeinschaftskonto"""
    __tablename__ = "split_transactions"

    id = Column(Integer, primary_key=True, index=True)
    shared_account_id = Column(Integer, ForeignKey("shared_accounts.id"), nullable=False)
    paid_by = Column(String(255), nullable=False)  # User identifier who paid
    total_amount = Column(Numeric(10, 2), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String(500), nullable=True)
    category = Column(String(50), nullable=True)
    receipt_path = Column(String(255), nullable=True)
    status = Column(String(20), default="pending")  # pending, confirmed, settled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    shared_account = relationship("SharedAccount", back_populates="split_transactions")
    shares = relationship("SplitShare", back_populates="split_transaction", cascade="all, delete-orphan")


class SplitShare(Base):
    """Anteil einer Person an einer aufgeteilten Transaktion"""
    __tablename__ = "split_shares"

    id = Column(Integer, primary_key=True, index=True)
    split_transaction_id = Column(Integer, ForeignKey("split_transactions.id"), nullable=False)
    user_identifier = Column(String(255), nullable=False)
    share_amount = Column(Numeric(10, 2), nullable=False)
    share_percentage = Column(Numeric(5, 2), nullable=True)  # Optional percentage
    status = Column(String(20), default="pending")  # pending, accepted, rejected, paid
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    split_transaction = relationship("SplitTransaction", back_populates="shares")


class Settlement(Base):
    """Ausgleichszahlungen zwischen Nutzern"""
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    shared_account_id = Column(Integer, ForeignKey("shared_accounts.id"), nullable=False)
    from_user = Column(String(255), nullable=False)
    to_user = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    settled_at = Column(DateTime, default=datetime.utcnow)
    description = Column(String(500), nullable=True)

    # Relationships
    shared_account = relationship("SharedAccount", back_populates="settlements")
