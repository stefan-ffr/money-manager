"""Helper for writing audit-log entries for security-relevant actions."""

from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request

from app.models.audit_log import AuditLog


def record_audit(
    db: Session,
    action: str,
    *,
    user_id: Optional[int] = None,
    target_user_id: Optional[int] = None,
    details: Optional[dict] = None,
    request: Optional[Request] = None,
    commit: bool = True,
) -> None:
    """Persist an audit-log entry.

    Best-effort: a logging failure must never break the underlying action, so
    any error is swallowed (after a rollback of just this insert).
    """
    try:
        ip_address = None
        user_agent = None
        if request is not None:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

        entry = AuditLog(
            user_id=user_id,
            action=action,
            target_user_id=target_user_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(entry)
        if commit:
            db.commit()
    except Exception:
        db.rollback()
