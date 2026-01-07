import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.replication import MirrorInstance, SyncLog, ConflictResolution
from app.models.transaction import Transaction
from app.models.account import Account
from app.federation.crypto import sign_data, verify_signature, get_public_key_pem


class ReplicationService:
    """Service for bidirectional replication between mirror instances"""

    def __init__(self, db: Session):
        self.db = db

    async def sync_all_mirrors(self) -> Dict[str, Any]:
        """
        Sync with all enabled mirror instances

        Returns:
            Dict with sync statistics
        """
        mirrors = self.db.query(MirrorInstance).filter(
            MirrorInstance.sync_enabled == True
        ).all()

        if not mirrors:
            return {"message": "No mirror instances configured", "synced_count": 0}

        results = []
        for mirror in mirrors:
            try:
                result = await self.sync_with_mirror(mirror)
                results.append(result)
            except Exception as e:
                self.log_sync_error(mirror, str(e))
                results.append({"mirror": mirror.instance_id, "status": "error", "error": str(e)})

        return {
            "synced_count": len([r for r in results if r.get("status") == "success"]),
            "failed_count": len([r for r in results if r.get("status") == "error"]),
            "results": results
        }

    async def sync_with_mirror(self, mirror: MirrorInstance) -> Dict[str, Any]:
        """
        Bidirectional sync with one mirror instance

        Args:
            mirror: Mirror instance configuration

        Returns:
            Dict with sync result
        """
        try:
            stats = {"pushed": 0, "pulled": 0, "conflicts": 0}

            # Push changes to mirror (if direction allows)
            if mirror.sync_direction in ["push", "bidirectional"]:
                push_stats = await self.push_changes(mirror)
                stats["pushed"] = push_stats.get("synced", 0)

            # Pull changes from mirror (if direction allows)
            if mirror.sync_direction in ["pull", "bidirectional"]:
                pull_stats = await self.pull_changes(mirror)
                stats["pulled"] = pull_stats.get("synced", 0)
                stats["conflicts"] = pull_stats.get("conflicts", 0)

            # Update last sync time
            mirror.last_sync = datetime.utcnow()
            self.db.commit()

            return {"mirror": mirror.instance_id, "status": "success", **stats}

        except Exception as e:
            return {"mirror": mirror.instance_id, "status": "error", "error": str(e)}

    async def push_changes(self, mirror: MirrorInstance) -> Dict[str, Any]:
        """
        Push local changes to mirror instance

        Args:
            mirror: Mirror instance configuration

        Returns:
            Dict with push statistics
        """
        # Get changes since last sync
        since = mirror.last_sync or datetime.utcnow() - timedelta(days=7)

        # Get changed transactions
        transactions = self.db.query(Transaction).filter(
            Transaction.updated_at > since
        ).all()

        # Get changed accounts
        accounts = self.db.query(Account).filter(
            Account.updated_at > since
        ).all()

        # Prepare payload
        payload = {
            "transactions": [self._serialize_transaction(tx) for tx in transactions],
            "accounts": [self._serialize_account(acc) for acc in accounts],
            "timestamp": datetime.utcnow().isoformat(),
            "source_instance": settings.INSTANCE_DOMAIN,
        }

        # Sign payload
        signature = sign_data(json.dumps(payload, default=str))

        # Send to mirror
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{mirror.instance_url}/api/v1/replication/receive",
                json=payload,
                headers={
                    "X-Signature": signature,
                    "X-Instance": settings.INSTANCE_DOMAIN,
                }
            )
            response.raise_for_status()

        # Log successful sync
        for tx in transactions:
            self._log_sync(mirror, "push", "transaction", tx.id, "create", "success")
        for acc in accounts:
            self._log_sync(mirror, "push", "account", acc.id, "create", "success")

        return {"synced": len(transactions) + len(accounts)}

    async def pull_changes(self, mirror: MirrorInstance) -> Dict[str, Any]:
        """
        Pull changes from mirror instance

        Args:
            mirror: Mirror instance configuration

        Returns:
            Dict with pull statistics
        """
        since = mirror.last_sync or datetime.utcnow() - timedelta(days=7)

        # Request changes from mirror
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{mirror.instance_url}/api/v1/replication/changes",
                params={"since": since.isoformat()},
            )
            response.raise_for_status()

            data = response.json()

            # Verify signature
            signature = response.headers.get("X-Signature")
            if not verify_signature(json.dumps(data, default=str), signature, mirror.public_key):
                raise ValueError("Invalid signature from mirror")

        # Apply changes
        result = await self.apply_changes(data, mirror)

        return result

    async def apply_changes(self, data: Dict[str, Any], mirror: MirrorInstance) -> Dict[str, Any]:
        """
        Apply changes from mirror instance

        Args:
            data: Changes from mirror
            mirror: Mirror instance configuration

        Returns:
            Dict with apply statistics
        """
        synced = 0
        conflicts = 0

        # Apply transaction changes
        for tx_data in data.get("transactions", []):
            try:
                existing = self.db.query(Transaction).filter(
                    Transaction.id == tx_data["id"]
                ).first()

                if existing:
                    # Check for conflict
                    remote_updated = datetime.fromisoformat(tx_data["updated_at"])
                    if existing.updated_at > remote_updated:
                        # Our version is newer - handle conflict
                        if await self.handle_conflict(existing, tx_data, mirror, "transaction"):
                            conflicts += 1
                            continue

                    # Update existing
                    for key, value in tx_data.items():
                        if key not in ["id", "created_at"] and hasattr(existing, key):
                            setattr(existing, key, value)
                else:
                    # Create new
                    new_tx = Transaction(**tx_data)
                    self.db.add(new_tx)

                self._log_sync(mirror, "pull", "transaction", tx_data["id"], "update", "success")
                synced += 1

            except Exception as e:
                self._log_sync(mirror, "pull", "transaction", tx_data.get("id", 0), "update", "failed", str(e))

        # Apply account changes
        for acc_data in data.get("accounts", []):
            try:
                existing = self.db.query(Account).filter(
                    Account.id == acc_data["id"]
                ).first()

                if existing:
                    # Check for conflict
                    remote_updated = datetime.fromisoformat(acc_data["updated_at"])
                    if existing.updated_at > remote_updated:
                        # Our version is newer - handle conflict
                        if await self.handle_conflict(existing, acc_data, mirror, "account"):
                            conflicts += 1
                            continue

                    # Update existing
                    for key, value in acc_data.items():
                        if key not in ["id", "created_at"] and hasattr(existing, key):
                            setattr(existing, key, value)
                else:
                    # Create new
                    new_acc = Account(**acc_data)
                    self.db.add(new_acc)

                self._log_sync(mirror, "pull", "account", acc_data["id"], "update", "success")
                synced += 1

            except Exception as e:
                self._log_sync(mirror, "pull", "account", acc_data.get("id", 0), "update", "failed", str(e))

        self.db.commit()

        return {"synced": synced, "conflicts": conflicts}

    async def handle_conflict(
        self,
        local: Any,
        remote: Dict[str, Any],
        mirror: MirrorInstance,
        entity_type: str
    ) -> bool:
        """
        Handle sync conflict

        Args:
            local: Local entity
            remote: Remote entity data
            mirror: Mirror instance
            entity_type: Type of entity (transaction, account)

        Returns:
            True if conflict was stored (manual resolution needed), False if auto-resolved
        """
        # Get conflict resolution strategy
        resolution = self.db.query(ConflictResolution).filter(
            ConflictResolution.entity_type == entity_type
        ).first()

        if not resolution:
            # Use default strategy from settings
            strategy = settings.REPLICATION_CONFLICT_STRATEGY
        else:
            strategy = resolution.strategy

        if strategy == "last_write_wins":
            # Remote is newer (we already checked this), keep local
            return False

        elif strategy == "primary_wins":
            # Primary instance wins
            if mirror.priority > 1:  # Mirror is secondary
                return False  # Keep local version (we are primary)
            else:
                # Mirror is primary, use remote version
                for key, value in remote.items():
                    if key not in ["id", "created_at"] and hasattr(local, key):
                        setattr(local, key, value)
                return False

        elif strategy == "manual":
            # Store conflict for manual resolution
            self._log_sync(
                mirror,
                "pull",
                entity_type,
                local.id,
                "update",
                "conflict",
                None,
                {
                    "local": self._serialize_entity(local, entity_type),
                    "remote": remote,
                }
            )
            return True  # Keep local for now

        return False

    def _serialize_transaction(self, tx: Transaction) -> Dict[str, Any]:
        """Serialize transaction to dict"""
        return {
            "id": tx.id,
            "account_id": tx.account_id,
            "date": tx.date.isoformat(),
            "amount": str(tx.amount),
            "category": tx.category,
            "description": tx.description,
            "status": tx.status,
            "source": tx.source,
            "requires_confirmation": tx.requires_confirmation,
            "receipt_path": tx.receipt_path,
            "created_at": tx.created_at.isoformat(),
            "updated_at": tx.updated_at.isoformat(),
        }

    def _serialize_account(self, acc: Account) -> Dict[str, Any]:
        """Serialize account to dict"""
        return {
            "id": acc.id,
            "name": acc.name,
            "type": acc.type,
            "iban": acc.iban,
            "balance": str(acc.balance),
            "currency": acc.currency,
            "bank_name": acc.bank_name,
            "created_at": acc.created_at.isoformat(),
            "updated_at": acc.updated_at.isoformat(),
        }

    def _serialize_entity(self, entity: Any, entity_type: str) -> Dict[str, Any]:
        """Serialize any entity based on type"""
        if entity_type == "transaction":
            return self._serialize_transaction(entity)
        elif entity_type == "account":
            return self._serialize_account(entity)
        return {}

    def _log_sync(
        self,
        mirror: MirrorInstance,
        sync_type: str,
        entity_type: str,
        entity_id: int,
        operation: str,
        status: str,
        error_message: Optional[str] = None,
        conflict_data: Optional[Dict] = None
    ):
        """Log sync operation"""
        log = SyncLog(
            mirror_instance_id=mirror.id,
            sync_type=sync_type,
            entity_type=entity_type,
            entity_id=entity_id,
            operation=operation,
            status=status,
            error_message=error_message,
            conflict_data=conflict_data
        )
        self.db.add(log)
        self.db.commit()

    def log_sync_error(self, mirror: MirrorInstance, error: str):
        """Log general sync error"""
        self._log_sync(mirror, "sync", "general", 0, "sync", "failed", error)
