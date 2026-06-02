from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime
from app.core.database import Base


class FederationPeer(Base):
    """An approved remote instance we federate with.

    The public key is pinned at pairing time (fetched over the peer's
    Let's Encrypt HTTPS endpoint), and federation is only allowed with peers
    that an admin has approved.
    """
    __tablename__ = "federation_peers"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False, unique=True, index=True)  # e.g. money.babsyit.ch
    name = Column(String(100), nullable=True)
    public_key = Column(Text, nullable=False)         # pinned PEM public key
    api_endpoint = Column(String(255), nullable=True)  # cached from /.well-known/money-instance
    approved = Column(Boolean, default=True, nullable=False)
    # how this peer entry came to exist: "manual" (admin added) or "request" (peer asked)
    origin = Column(String(20), default="manual")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
