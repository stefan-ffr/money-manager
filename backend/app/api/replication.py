from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User
from app.models.replication import MirrorInstance, SyncLog, ConflictResolution
from app.services.replication_service import ReplicationService
from app.federation.crypto import verify_signature, sign_data, get_public_key_pem

router = APIRouter()


# Pydantic Models
class MirrorInstanceCreate(BaseModel):
    instance_url: str
    instance_id: str
    public_key: str
    sync_enabled: bool = True
    sync_direction: str = "bidirectional"  # push, pull, bidirectional
    priority: int = 2


class MirrorInstanceUpdate(BaseModel):
    sync_enabled: Optional[bool] = None
    sync_direction: Optional[str] = None
    priority: Optional[int] = None


class MirrorInstanceResponse(BaseModel):
    id: int
    instance_url: str
    instance_id: str
    sync_enabled: bool
    sync_direction: str
    last_sync: Optional[datetime]
    priority: int
    created_at: datetime

    class Config:
        from_attributes = True


class SyncLogResponse(BaseModel):
    id: int
    mirror_instance_id: int
    sync_type: str
    entity_type: str
    entity_id: int
    operation: str
    status: str
    synced_at: datetime

    class Config:
        from_attributes = True


class ConflictResolutionUpdate(BaseModel):
    strategy: str  # last_write_wins, primary_wins, manual
    primary_instance_id: Optional[str] = None


# Mirror Instance Management Endpoints
@router.post("/mirrors", response_model=MirrorInstanceResponse, status_code=status.HTTP_201_CREATED)
def create_mirror_instance(
    mirror: MirrorInstanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new mirror instance configuration

    Requires authentication
    """
    # Check if instance already exists
    existing = db.query(MirrorInstance).filter(
        MirrorInstance.instance_id == mirror.instance_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mirror instance with this ID already exists"
        )

    # Create mirror instance
    db_mirror = MirrorInstance(**mirror.dict())
    db.add(db_mirror)
    db.commit()
    db.refresh(db_mirror)

    return db_mirror


@router.get("/mirrors", response_model=List[MirrorInstanceResponse])
def list_mirror_instances(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all mirror instances"""
    mirrors = db.query(MirrorInstance).all()
    return mirrors


@router.get("/mirrors/{mirror_id}", response_model=MirrorInstanceResponse)
def get_mirror_instance(
    mirror_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get mirror instance by ID"""
    mirror = db.query(MirrorInstance).filter(MirrorInstance.id == mirror_id).first()
    if not mirror:
        raise HTTPException(status_code=404, detail="Mirror instance not found")
    return mirror


@router.patch("/mirrors/{mirror_id}", response_model=MirrorInstanceResponse)
def update_mirror_instance(
    mirror_id: int,
    update: MirrorInstanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update mirror instance configuration"""
    mirror = db.query(MirrorInstance).filter(MirrorInstance.id == mirror_id).first()
    if not mirror:
        raise HTTPException(status_code=404, detail="Mirror instance not found")

    # Update fields
    for key, value in update.dict(exclude_unset=True).items():
        setattr(mirror, key, value)

    db.commit()
    db.refresh(mirror)
    return mirror


@router.delete("/mirrors/{mirror_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mirror_instance(
    mirror_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete mirror instance"""
    mirror = db.query(MirrorInstance).filter(MirrorInstance.id == mirror_id).first()
    if not mirror:
        raise HTTPException(status_code=404, detail="Mirror instance not found")

    db.delete(mirror)
    db.commit()


# Sync Endpoints
@router.post("/mirrors/{mirror_id}/sync")
async def trigger_sync(
    mirror_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger sync with specific mirror instance"""
    mirror = db.query(MirrorInstance).filter(MirrorInstance.id == mirror_id).first()
    if not mirror:
        raise HTTPException(status_code=404, detail="Mirror instance not found")

    service = ReplicationService(db)
    result = await service.sync_with_mirror(mirror)

    return result


@router.post("/sync-all")
async def trigger_sync_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger sync with all mirror instances"""
    service = ReplicationService(db)
    result = await service.sync_all_mirrors()

    return result


# Sync Logs
@router.get("/mirrors/{mirror_id}/logs", response_model=List[SyncLogResponse])
def get_mirror_logs(
    mirror_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sync logs for specific mirror instance"""
    logs = db.query(SyncLog).filter(
        SyncLog.mirror_instance_id == mirror_id
    ).order_by(SyncLog.synced_at.desc()).limit(limit).all()

    return logs


@router.get("/logs/conflicts", response_model=List[SyncLogResponse])
def get_conflict_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all conflict logs requiring manual resolution"""
    logs = db.query(SyncLog).filter(
        SyncLog.status == "conflict"
    ).order_by(SyncLog.synced_at.desc()).limit(limit).all()

    return logs


# Conflict Resolution
@router.get("/conflict-resolution/{entity_type}")
def get_conflict_resolution(
    entity_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conflict resolution strategy for entity type"""
    resolution = db.query(ConflictResolution).filter(
        ConflictResolution.entity_type == entity_type
    ).first()

    if not resolution:
        return {
            "entity_type": entity_type,
            "strategy": settings.REPLICATION_CONFLICT_STRATEGY,
            "primary_instance_id": None
        }

    return resolution


@router.put("/conflict-resolution/{entity_type}")
def update_conflict_resolution(
    entity_type: str,
    update: ConflictResolutionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update conflict resolution strategy"""
    resolution = db.query(ConflictResolution).filter(
        ConflictResolution.entity_type == entity_type
    ).first()

    if not resolution:
        resolution = ConflictResolution(entity_type=entity_type)
        db.add(resolution)

    resolution.strategy = update.strategy
    if update.primary_instance_id:
        resolution.primary_instance_id = update.primary_instance_id

    db.commit()
    db.refresh(resolution)

    return resolution


# Federation Endpoints (Receive sync data from other instances)
@router.post("/receive")
async def receive_sync_data(
    data: Dict[str, Any],
    x_signature: str = Header(..., alias="X-Signature"),
    x_instance: str = Header(..., alias="X-Instance"),
    db: Session = Depends(get_db)
):
    """
    Receive sync data from another mirror instance

    This endpoint is called by other instances to push data to us
    """
    # Get mirror instance
    mirror = db.query(MirrorInstance).filter(
        MirrorInstance.instance_id == x_instance
    ).first()

    if not mirror:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown mirror instance"
        )

    # Verify signature
    if not verify_signature(json.dumps(data, default=str), x_signature, mirror.public_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )

    # Apply changes
    service = ReplicationService(db)
    result = await service.apply_changes(data, mirror)

    return {
        "status": "success",
        "entities_synced": result.get("synced", 0),
        "conflicts": result.get("conflicts", 0)
    }


@router.get("/changes")
async def get_changes(
    since: datetime,
    db: Session = Depends(get_db)
):
    """
    Get changes since timestamp for mirror to pull

    This endpoint is called by other instances to pull data from us
    """
    # Note: In production, you should verify the requester is a known mirror instance

    # Get transactions
    transactions = db.query(Transaction).filter(
        Transaction.updated_at > since
    ).all()

    # Get accounts
    accounts = db.query(Account).filter(
        Account.updated_at > since
    ).all()

    # Serialize
    service = ReplicationService(db)
    payload = {
        "transactions": [service._serialize_transaction(tx) for tx in transactions],
        "accounts": [service._serialize_account(acc) for acc in accounts],
        "timestamp": datetime.utcnow().isoformat(),
        "source_instance": settings.INSTANCE_DOMAIN,
    }

    # Sign response
    from fastapi.responses import JSONResponse
    response = JSONResponse(content=payload)
    response.headers["X-Signature"] = sign_data(json.dumps(payload, default=str))

    return response


from app.models.transaction import Transaction
from app.models.account import Account
