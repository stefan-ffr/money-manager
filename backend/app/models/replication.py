from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class MirrorInstance(Base):
    """Mirror Instance Configuration for Replication"""
    __tablename__ = "mirror_instances"

    id = Column(Integer, primary_key=True, index=True)
    instance_url = Column(String(255), unique=True, nullable=False)  # https://mirror.example.com
    instance_id = Column(String(255), unique=True, nullable=False)   # mirror.example.com
    public_key = Column(String, nullable=False)  # RSA Public Key for verification
    sync_enabled = Column(Boolean, default=True)
    sync_direction = Column(String(20), default="bidirectional")  # push, pull, bidirectional
    last_sync = Column(DateTime, nullable=True)
    priority = Column(Integer, default=1)  # 1=primary, 2=secondary, 3=tertiary
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sync_logs = relationship("SyncLog", back_populates="mirror_instance", cascade="all, delete-orphan")


class SyncLog(Base):
    """Synchronization Audit Log"""
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    mirror_instance_id = Column(Integer, ForeignKey("mirror_instances.id"), nullable=False)
    sync_type = Column(String(10), nullable=False)  # push, pull
    entity_type = Column(String(50), nullable=False)  # transaction, account, etc.
    entity_id = Column(Integer, nullable=False)
    operation = Column(String(20), nullable=False)  # create, update, delete
    status = Column(String(20), nullable=False)  # success, failed, conflict
    conflict_data = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    synced_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    mirror_instance = relationship("MirrorInstance", back_populates="sync_logs")


class ConflictResolution(Base):
    """Conflict Resolution Strategy Configuration"""
    __tablename__ = "conflict_resolutions"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), unique=True, nullable=False)  # transaction, account, etc.
    strategy = Column(String(20), default="last_write_wins")  # last_write_wins, primary_wins, manual
    primary_instance_id = Column(String(255), nullable=True)  # Which instance is source of truth
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
