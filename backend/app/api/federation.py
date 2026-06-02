from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import List, Optional
from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user
from app.core.authorization import verify_transaction_access, get_current_admin_user
from app.models.user import User
from app.models.account import Account
from app.models.federation_peer import FederationPeer

router = APIRouter()


def _get_approved_peer(domain: str, db: Session) -> Optional[FederationPeer]:
    """Return the approved peer for a domain, or None if not allow-listed."""
    return db.query(FederationPeer).filter(
        FederationPeer.domain == domain,
        FederationPeer.approved.is_(True),
    ).first()


def _apply_balance_delta(account: Account, delta: Decimal) -> None:
    """Adjust an account's balance by delta (kept in sync with transactions)."""
    account.balance = (account.balance or Decimal("0.00")) + delta


def _resolve_local_recipient(to_user: str, db: Session) -> User:
    """Map a federated 'user@instance.domain' recipient to a local user.

    The invoice must be addressed to THIS instance and reference a user that
    exists locally (matched by username or e-mail).
    """
    parts = to_user.split("@")
    if len(parts) != 2:
        raise HTTPException(status_code=422, detail="Invalid recipient format. Expected user@instance.domain")

    local_part, target_domain = parts
    if target_domain != settings.INSTANCE_DOMAIN:
        raise HTTPException(status_code=404, detail="Invoice is not addressed to this instance")

    user = (
        db.query(User)
        .filter((User.username == local_part) | (User.email == to_user))
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail=f"Unknown recipient '{to_user}' on this instance")
    return user


class InvoiceAttachment(BaseModel):
    filename: str
    data: str  # base64 encoded
    mime_type: str


class FederatedInvoice(BaseModel):
    from_user: str  # e.g., stefan@money.babsyit.ch
    to_user: str
    amount: Decimal
    currency: str = "CHF"
    description: str
    date: date
    category: str | None = None
    split_type: str | None = None
    shared_account_id: str | None = None
    attachments: List[InvoiceAttachment] = []


class InvoiceResponse(BaseModel):
    invoice_id: int
    status: str
    message: str


@router.post("/invoice/send")
async def send_invoice(
    invoice: FederatedInvoice,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send an invoice to another instance on behalf of the current user."""
    from app.services.federation_service import send_federated_invoice

    if not settings.FEDERATION_ENABLED:
        raise HTTPException(status_code=403, detail="Federation not enabled")

    # Only send to an approved, paired peer
    to_parts = invoice.to_user.split("@")
    if len(to_parts) != 2:
        raise HTTPException(status_code=422, detail="Invalid recipient format. Expected user@instance.domain")
    if not _get_approved_peer(to_parts[1], db):
        raise HTTPException(status_code=403, detail=f"Instance '{to_parts[1]}' is not an approved federation peer")

    # Set the sender server-side so a user cannot impersonate someone else
    invoice.from_user = f"{current_user.username}@{settings.INSTANCE_DOMAIN}"

    try:
        result = await send_federated_invoice(invoice)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Invoice konnte nicht zugestellt werden: {e}")
    return result


@router.post("/invoice/receive")
async def receive_invoice(
    request: Request,
    db: Session = Depends(get_db),
    x_signature: Optional[str] = Header(default=None),
):
    """Receive a signed invoice from another instance (server-to-server).

    Authentication is by cryptographic signature (X-Signature header) over the
    exact request body, not by user session – the call originates from a peer.
    """
    from app.federation.crypto import verify_signature
    from app.models.transaction import Transaction
    import base64
    from pathlib import Path

    if not settings.FEDERATION_ENABLED:
        raise HTTPException(status_code=403, detail="Federation not enabled")

    if not x_signature:
        raise HTTPException(status_code=401, detail="Missing X-Signature header")

    # Read the raw body and parse it (we verify the signature over these bytes)
    raw_body = (await request.body()).decode("utf-8")
    try:
        invoice = FederatedInvoice.model_validate_json(raw_body)
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid invoice payload")

    # Allow-list: only accept invoices from an approved, paired peer
    sender_parts = invoice.from_user.split("@")
    if len(sender_parts) != 2:
        raise HTTPException(status_code=422, detail="Invalid sender format")
    sender_domain = sender_parts[1]
    peer = _get_approved_peer(sender_domain, db)
    if not peer:
        raise HTTPException(status_code=403, detail=f"Instance '{sender_domain}' is not an approved federation peer")

    # Verify the signature over the exact received bytes using the PINNED key
    if not verify_signature(raw_body, x_signature, peer.public_key):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Map the recipient to a real local user and one of their accounts
    recipient = _resolve_local_recipient(invoice.to_user, db)
    account = (
        db.query(Account)
        .filter(Account.user_id == recipient.id)
        .order_by(Account.id)
        .first()
    )
    if not account:
        raise HTTPException(
            status_code=409,
            detail=f"Recipient '{invoice.to_user}' has no account to book the invoice into",
        )

    description = f"From {invoice.from_user}: {invoice.description}"
    if invoice.currency and invoice.currency != account.currency:
        description += f" ({invoice.amount} {invoice.currency})"

    # Idempotency: ignore a duplicate delivery of the same invoice
    existing = db.query(Transaction).filter(
        Transaction.user_id == recipient.id,
        Transaction.account_id == account.id,
        Transaction.source == "federation",
        Transaction.date == invoice.date,
        Transaction.amount == invoice.amount,
        Transaction.description == description,
    ).first()
    if existing:
        return InvoiceResponse(
            invoice_id=existing.id,
            status=existing.status,
            message="Invoice already received (duplicate ignored)",
        )

    try:
        db_transaction = Transaction(
            user_id=recipient.id,
            account_id=account.id,
            date=invoice.date,
            amount=invoice.amount,
            category=invoice.category,
            description=description,
            status="pending",
            source="federation",
            requires_confirmation=True,  # von anderer Instanz = Bestätigung erforderlich
        )

        # Save first attachment if any
        if invoice.attachments:
            receipts_dir = Path(settings.RECEIPTS_PATH) / "federated"
            receipts_dir.mkdir(parents=True, exist_ok=True)
            attachment = invoice.attachments[0]
            file_data = base64.b64decode(attachment.data)
            # Use the transaction-less, collision-safe name once we have an id
            safe_name = Path(attachment.filename).name
            file_path = receipts_dir / f"{recipient.id}_{invoice.date}_{safe_name}"
            with open(file_path, "wb") as f:
                f.write(file_data)
            db_transaction.receipt_path = str(file_path)

        db.add(db_transaction)
        _apply_balance_delta(account, db_transaction.amount)
        db.commit()
        db.refresh(db_transaction)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Invoice konnte nicht gespeichert werden")

    return InvoiceResponse(
        invoice_id=db_transaction.id,
        status="pending",
        message="Invoice received and stored as pending transaction",
    )


@router.post("/invoice/{invoice_id}/accept")
async def accept_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accept a received invoice (only the recipient may do this)."""
    # verify_transaction_access ensures the invoice belongs to the current user
    transaction = verify_transaction_access(invoice_id, db, current_user)

    transaction.status = "confirmed"
    transaction.requires_confirmation = False
    db.commit()

    # NOTE: sending a confirmation back to the sender instance is tracked in #11
    return {"message": "Invoice accepted", "transaction_id": invoice_id}


@router.post("/invoice/{invoice_id}/reject")
async def reject_invoice(
    invoice_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject a received invoice and revert its balance effect."""
    from app.models.transaction import Transaction

    transaction = verify_transaction_access(invoice_id, db, current_user)

    try:
        account = db.query(Account).filter(Account.id == transaction.account_id).first()
        if account:
            _apply_balance_delta(account, -transaction.amount)
        db.delete(transaction)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Invoice konnte nicht abgelehnt werden")

    # NOTE: sending a rejection back to the sender instance is tracked in #11
    return {"message": "Invoice rejected", "reason": reason}


@router.get("/instances/{domain}")
async def get_instance_info(domain: str, current_user: User = Depends(get_current_user)):
    """Fetch public key and info from another instance"""
    import httpx

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"https://{domain}/.well-known/money-instance")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not reach instance: {str(e)}")


# ---------------------------------------------------------------------------
# Federation peers (allow-list). Trust is bootstrapped over the peer's HTTPS
# (Let's Encrypt) endpoint at pairing time; the RSA public key is then pinned.
# ---------------------------------------------------------------------------

class PeerCreate(BaseModel):
    domain: str
    name: Optional[str] = None


class PeerUpdate(BaseModel):
    name: Optional[str] = None
    approved: Optional[bool] = None


class PeerResponse(BaseModel):
    id: int
    domain: str
    name: Optional[str]
    api_endpoint: Optional[str]
    approved: bool
    origin: str

    class Config:
        from_attributes = True


def _normalize_domain(domain: str) -> str:
    return domain.strip().lower().removeprefix("https://").removeprefix("http://").strip("/")


@router.get("/peers", response_model=List[PeerResponse])
def list_peers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """List configured federation peers (admin)."""
    return db.query(FederationPeer).order_by(FederationPeer.domain).all()


@router.post("/peers", response_model=PeerResponse, status_code=201)
async def add_peer(
    peer: PeerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Pair with a peer instance (admin): fetch its public key over HTTPS and
    pin it as an approved peer. The HTTPS/Let's Encrypt cert authenticates the
    domain at this step."""
    from app.services.federation_service import fetch_instance_info

    domain = _normalize_domain(peer.domain)
    if not domain:
        raise HTTPException(status_code=422, detail="Domain darf nicht leer sein")
    if db.query(FederationPeer).filter(FederationPeer.domain == domain).first():
        raise HTTPException(status_code=409, detail="Peer ist bereits konfiguriert")

    try:
        info = await fetch_instance_info(domain)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Instanz nicht erreichbar oder ungültig: {e}")

    db_peer = FederationPeer(
        domain=domain,
        name=peer.name or info.get("instance_id"),
        public_key=info["public_key"],
        api_endpoint=info.get("api_endpoint"),
        approved=True,
        origin="manual",
    )
    db.add(db_peer)
    db.commit()
    db.refresh(db_peer)
    return db_peer


@router.post("/peers/{peer_id}/refresh", response_model=PeerResponse)
async def refresh_peer_key(
    peer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Re-fetch and re-pin a peer's public key (e.g. after key rotation)."""
    from app.services.federation_service import fetch_instance_info

    db_peer = db.query(FederationPeer).filter(FederationPeer.id == peer_id).first()
    if not db_peer:
        raise HTTPException(status_code=404, detail="Peer not found")
    try:
        info = await fetch_instance_info(db_peer.domain)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Instanz nicht erreichbar: {e}")
    db_peer.public_key = info["public_key"]
    db_peer.api_endpoint = info.get("api_endpoint")
    db.commit()
    db.refresh(db_peer)
    return db_peer


@router.put("/peers/{peer_id}", response_model=PeerResponse)
def update_peer(
    peer_id: int,
    update: PeerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Approve/disable or rename a peer (admin)."""
    db_peer = db.query(FederationPeer).filter(FederationPeer.id == peer_id).first()
    if not db_peer:
        raise HTTPException(status_code=404, detail="Peer not found")
    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(db_peer, key, value)
    db.commit()
    db.refresh(db_peer)
    return db_peer


@router.delete("/peers/{peer_id}", status_code=204)
def delete_peer(
    peer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Remove a federation peer (admin)."""
    db_peer = db.query(FederationPeer).filter(FederationPeer.id == peer_id).first()
    if not db_peer:
        raise HTTPException(status_code=404, detail="Peer not found")
    db.delete(db_peer)
    db.commit()
    return None


@router.post("/pair-request", status_code=202)
async def pair_request(
    request: Request,
    db: Session = Depends(get_db),
    x_instance: str = Header(..., alias="X-Instance"),
):
    """Server-to-server: another instance asks to federate with us.

    We fetch and pin the requester's public key over HTTPS (TLS authenticates
    the domain), but store it as NOT approved – an admin must approve it before
    any invoices are accepted. This keeps federation explicit, not automatic.
    """
    from app.services.federation_service import fetch_instance_info

    if not settings.FEDERATION_ENABLED:
        raise HTTPException(status_code=403, detail="Federation not enabled")

    domain = _normalize_domain(x_instance)
    existing = db.query(FederationPeer).filter(FederationPeer.domain == domain).first()
    if existing:
        return {"status": existing.approved and "approved" or "pending", "domain": domain}

    try:
        info = await fetch_instance_info(domain)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Requesting instance unreachable: {e}")

    db.add(FederationPeer(
        domain=domain,
        name=info.get("instance_id"),
        public_key=info["public_key"],
        api_endpoint=info.get("api_endpoint"),
        approved=False,
        origin="request",
    ))
    db.commit()
    return {"status": "pending", "domain": domain, "message": "Pairing request stored; awaiting approval"}
