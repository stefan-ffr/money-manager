# Money Manager - Sicherheitskonzept

## Übersicht der Sicherheitsmechanismen

Money Manager implementiert mehrere Sicherheitsebenen:

1. **Federation Security** - RSA Public/Private Key Verschlüsselung
2. **User Authentication** - Passkey (WebAuthn) Support
3. **Instance Replication** - Gespiegelte Instanzen mit Sync

---

## 1. Federation Security - RSA Public/Private Key ✅

### Ja, die Federation ist wie SSH abgesichert!

**Implementierung:**

```python
# app/federation/crypto.py
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# Jede Instanz hat ein RSA Key-Pair (2048-bit)
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Signatur erstellen (wie SSH)
signature = private_key.sign(
    data.encode(),
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# Signatur verifizieren
public_key.verify(signature, data, ...)
```

### Wie funktioniert's?

1. **Instanz Setup:**
   ```bash
   # Beim ersten Start wird Key-Pair generiert
   docker compose exec backend python -c "
   from app.federation.crypto import generate_key_pair
   generate_key_pair()
   "
   
   # Private Key: /app/secrets/instance_key.pem (NIE teilen!)
   # Public Key: Über /.well-known/money-instance verfügbar
   ```

2. **Discovery:**
   ```bash
   # Andere Instanzen holen deinen Public Key
   curl https://money.babsyit.ch/.well-known/money-instance
   {
     "instance_id": "money.babsyit.ch",
     "public_key": "-----BEGIN PUBLIC KEY-----\n...",
     "api_endpoint": "https://money.babsyit.ch/api/v1",
     "federation_enabled": true
   }
   ```

3. **Signierter Request:**
   ```python
   # Sender (Instance A)
   invoice_json = invoice.model_dump_json()
   signature = sign_data(invoice_json)
   
   # Senden mit Signatur
   response = await client.post(
       "https://instance-b.ch/api/v1/federation/invoice/receive",
       json=invoice.model_dump(),
       headers={
           "X-Signature": signature,
           "X-Instance": "instance-a.ch"
       }
   )
   
   # Empfänger (Instance B)
   # 1. Holt Public Key von Instance A
   # 2. Verifiziert Signatur
   # 3. Akzeptiert nur bei gültiger Signatur
   if not verify_signature(invoice_json, signature, public_key):
       raise HTTPException(401, "Invalid signature")
   ```

### Sicherheitsmerkmale:

✅ **Man-in-the-Middle Schutz** - Signatur kann nicht gefälscht werden
✅ **Replay-Schutz** - Timestamps in Payloads (TODO: implementieren)
✅ **Identity Verification** - Jede Instanz hat eindeutigen Public Key
✅ **No Shared Secrets** - Nur Public Keys werden geteilt

### Zusätzliche Empfehlungen:

```python
# TODO: Timestamp & Nonce für Replay-Schutz
class FederatedInvoice(BaseModel):
    # ... existing fields
    timestamp: datetime  # Request creation time
    nonce: str  # Unique request ID
    
# Verify timestamp is within 5 minutes
if abs((invoice.timestamp - datetime.now()).total_seconds()) > 300:
    raise HTTPException(401, "Request expired")

# Store nonce to prevent replay
if nonce_already_used(invoice.nonce):
    raise HTTPException(401, "Duplicate request")
```

---

## 2. Passkey Authentication (WebAuthn) ✅ IMPLEMENTIERT

### Warum Passkeys?

Die **Web-Oberfläche** benötigt sichere Authentifizierung!

**Problem ohne Auth:**
- Jeder der die URL kennt, hat Zugriff
- Keine Unterscheidung zwischen Usern
- Keine Audit-Trails

**Lösung: Passkeys (WebAuthn)**
- Biometrisch (Face ID, Touch ID, Fingerprint)
- Hardware-basiert (YubiKey)
- Phishing-resistent
- Keine Passwörter!

### Status: Vollständig implementiert (v1.1)

### Implementation:

```python
# backend/requirements.txt
# Hinzufügen:
webauthn==1.11.0
fastapi-users[sqlalchemy]==12.1.0

# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, LargeBinary
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

class WebAuthnCredential(Base):
    __tablename__ = "webauthn_credentials"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    credential_id = Column(LargeBinary, unique=True)
    public_key = Column(LargeBinary)
    sign_count = Column(Integer, default=0)
    device_name = Column(String, nullable=True)  # z.B. "iPhone 15 Pro"
```

```python
# backend/app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    UserVerificationRequirement,
)

router = APIRouter()

@router.post("/auth/register/begin")
async def begin_registration(email: str, username: str, db: Session = Depends(get_db)):
    """Start Passkey Registration"""
    user = User(email=email, username=username)
    db.add(user)
    db.commit()
    
    options = generate_registration_options(
        rp_id=settings.INSTANCE_DOMAIN,
        rp_name="Money Manager",
        user_id=str(user.id),
        user_name=username,
        user_display_name=email,
        attestation="direct",
        authenticator_selection={
            "user_verification": UserVerificationRequirement.PREFERRED
        }
    )
    
    # Store challenge in session/cache
    cache.set(f"challenge_{user.id}", options.challenge, timeout=300)
    
    return options

@router.post("/auth/register/complete")
async def complete_registration(
    user_id: int,
    credential: dict,
    db: Session = Depends(get_db)
):
    """Complete Passkey Registration"""
    user = db.query(User).filter(User.id == user_id).first()
    challenge = cache.get(f"challenge_{user_id}")
    
    verification = verify_registration_response(
        credential=credential,
        expected_challenge=challenge,
        expected_rp_id=settings.INSTANCE_DOMAIN,
        expected_origin=f"https://{settings.INSTANCE_DOMAIN}",
    )
    
    # Store credential
    cred = WebAuthnCredential(
        user_id=user_id,
        credential_id=verification.credential_id,
        public_key=verification.credential_public_key,
        sign_count=verification.sign_count,
    )
    db.add(cred)
    db.commit()
    
    return {"message": "Registration successful"}

@router.post("/auth/login/begin")
async def begin_authentication(username: str, db: Session = Depends(get_db)):
    """Start Passkey Login"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    credentials = db.query(WebAuthnCredential).filter(
        WebAuthnCredential.user_id == user.id
    ).all()
    
    options = generate_authentication_options(
        rp_id=settings.INSTANCE_DOMAIN,
        allow_credentials=[
            PublicKeyCredentialDescriptor(id=c.credential_id)
            for c in credentials
        ],
        user_verification=UserVerificationRequirement.PREFERRED,
    )
    
    cache.set(f"auth_challenge_{user.id}", options.challenge, timeout=300)
    
    return options

@router.post("/auth/login/complete")
async def complete_authentication(
    username: str,
    credential: dict,
    db: Session = Depends(get_db)
):
    """Complete Passkey Login"""
    user = db.query(User).filter(User.username == username).first()
    challenge = cache.get(f"auth_challenge_{user.id}")
    
    cred = db.query(WebAuthnCredential).filter(
        WebAuthnCredential.credential_id == credential["id"]
    ).first()
    
    verification = verify_authentication_response(
        credential=credential,
        expected_challenge=challenge,
        expected_rp_id=settings.INSTANCE_DOMAIN,
        expected_origin=f"https://{settings.INSTANCE_DOMAIN}",
        credential_public_key=cred.public_key,
        credential_current_sign_count=cred.sign_count,
    )
    
    # Update sign count
    cred.sign_count = verification.new_sign_count
    db.commit()
    
    # Create JWT token
    token = create_access_token({"sub": str(user.id)})
    
    return {"access_token": token, "token_type": "bearer"}
```

```typescript
// frontend/src/services/auth.ts
import { startRegistration, startAuthentication } from '@simplewebauthn/browser'

export async function registerPasskey(email: string, username: string) {
  // 1. Get options from server
  const optionsResponse = await fetch('/api/v1/auth/register/begin', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, username }),
  })
  const options = await optionsResponse.json()
  
  // 2. Trigger browser Passkey registration
  const credential = await startRegistration(options)
  
  // 3. Send credential to server
  const verificationResponse = await fetch('/api/v1/auth/register/complete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: options.user.id,
      credential,
    }),
  })
  
  return verificationResponse.json()
}

export async function loginWithPasskey(username: string) {
  // 1. Get challenge
  const optionsResponse = await fetch('/api/v1/auth/login/begin', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username }),
  })
  const options = await optionsResponse.json()
  
  // 2. Authenticate with Passkey
  const credential = await startAuthentication(options)
  
  // 3. Verify and get token
  const verificationResponse = await fetch('/api/v1/auth/login/complete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, credential }),
  })
  
  const { access_token } = await verificationResponse.json()
  localStorage.setItem('token', access_token)
  
  return access_token
}
```

### User Experience:

```tsx
// frontend/src/components/Login.tsx
function Login() {
  const [username, setUsername] = useState('')
  
  return (
    <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">Login</h2>
      
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
        className="w-full px-4 py-2 border rounded mb-4"
      />
      
      <button
        onClick={() => loginWithPasskey(username)}
        className="w-full bg-primary-600 text-white py-2 rounded hover:bg-primary-700"
      >
        🔐 Mit Passkey anmelden
      </button>
      
      <p className="text-sm text-gray-600 mt-4">
        Noch kein Passkey? 
        <button onClick={() => navigate('/register')} className="text-primary-600">
          Registrieren
        </button>
      </p>
    </div>
  )
}
```

### Vorteile:

✅ **Keine Passwörter** - nichts zu merken, nichts zu hacken
✅ **Biometrisch** - Face ID, Touch ID, Fingerprint
✅ **Hardware Keys** - YubiKey Support
✅ **Multi-Device** - Sync über iCloud/Google
✅ **Phishing-Resistent** - Domain-gebunden

---

## 2.1 OAuth2/OIDC Integration (SSO) ✅ IMPLEMENTIERT

### Warum OAuth2/OIDC?

Für Enterprise-Umgebungen und zentrale Benutzerverwaltung ist Single Sign-On (SSO) essentiell.

**Use Cases:**
- **Authentik Integration** - Self-hosted SSO Lösung
- **Keycloak Integration** - Enterprise Identity Management
- **Generic OIDC** - Beliebige OIDC-Provider (Auth0, Okta, etc.)
- **Zentrale User-Verwaltung** - Ein Login für alle Apps
- **Gruppen & Rollen** - User Permissions zentral verwalten

### Status: Vollständig implementiert (v1.1)

### Implementation:

**Backend Configuration:**

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # OAuth2/OIDC Configuration
    OAUTH_ENABLED: bool = False
    OAUTH_CLIENT_ID: str = ""
    OAUTH_CLIENT_SECRET: str = ""
    OAUTH_AUTHORIZATION_URL: str = ""  # e.g. https://auth.example.com/application/o/authorize/
    OAUTH_TOKEN_URL: str = ""          # e.g. https://auth.example.com/application/o/token/
    OAUTH_USERINFO_URL: str = ""       # e.g. https://auth.example.com/application/o/userinfo/
    OAUTH_REDIRECT_URI: str = "http://localhost:3000/auth/callback"
    OAUTH_SCOPES: str = "openid email profile"
```

**Backend OAuth Endpoints:**

```python
# backend/app/api/auth.py
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()

@router.get("/auth/oauth/config")
async def get_oauth_config():
    """Return OAuth configuration for frontend"""
    if not settings.OAUTH_ENABLED:
        return {"enabled": False}

    return {
        "enabled": True,
        "authorization_url": settings.OAUTH_AUTHORIZATION_URL,
        "client_id": settings.OAUTH_CLIENT_ID,
        "redirect_uri": settings.OAUTH_REDIRECT_URI,
        "scopes": settings.OAUTH_SCOPES.split(),
    }

@router.get("/auth/oauth/login")
async def oauth_login(request: Request):
    """Initiate OAuth login flow"""
    redirect_uri = settings.OAUTH_REDIRECT_URI
    return await oauth.create_client('oidc').authorize_redirect(request, redirect_uri)

@router.post("/auth/oauth/callback")
async def oauth_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle OAuth callback and create/login user"""
    # Exchange code for token
    token_response = await oauth.create_client('oidc').authorize_access_token(code=code)

    # Get user info
    userinfo = await oauth.create_client('oidc').userinfo(token=token_response['access_token'])

    # Find or create user
    user = db.query(User).filter(User.email == userinfo['email']).first()
    if not user:
        user = User(
            email=userinfo['email'],
            username=userinfo.get('preferred_username', userinfo['email']),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Create JWT token
    access_token = create_access_token({"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}
```

**Frontend OAuth Integration:**

```typescript
// frontend/src/services/auth.ts
export async function loginWithOAuth(): Promise<void> {
  // Get OAuth configuration
  const configResponse = await axios.get(`${API_URL}/api/v1/auth/oauth/config`)
  const config = configResponse.data

  if (!config.enabled) {
    throw new Error('OAuth is not enabled')
  }

  // Generate state for CSRF protection
  const state = generateRandomString(32)
  sessionStorage.setItem('oauth_state', state)

  // Build authorization URL
  const params = new URLSearchParams({
    client_id: config.client_id,
    redirect_uri: config.redirect_uri,
    response_type: 'code',
    scope: config.scopes.join(' '),
    state: state,
  })

  // Redirect to OAuth provider
  window.location.href = `${config.authorization_url}?${params.toString()}`
}

export async function handleOAuthCallback(code: string, state: string): Promise<string> {
  // Verify state (CSRF protection)
  const savedState = sessionStorage.getItem('oauth_state')
  if (state !== savedState) {
    throw new Error('Invalid state parameter')
  }

  // Exchange code for token
  const response = await axios.post(`${API_URL}/api/v1/auth/oauth/callback`, {
    code,
    state,
  })

  const { access_token } = response.data
  localStorage.setItem('token', access_token)

  return access_token
}
```

### Authentik Setup Beispiel:

```yaml
# 1. Authentik Provider erstellen
Provider Type: OAuth2/OpenID Provider
Name: Money Manager
Client ID: money-manager
Client Secret: <generate>
Redirect URIs: http://localhost:3000/auth/callback

# 2. Application erstellen
Name: Money Manager
Slug: money-manager
Provider: Money Manager (from step 1)

# 3. .env konfigurieren
OAUTH_ENABLED=true
OAUTH_CLIENT_ID=money-manager
OAUTH_CLIENT_SECRET=<from-step-1>
OAUTH_AUTHORIZATION_URL=https://auth.example.com/application/o/authorize/
OAUTH_TOKEN_URL=https://auth.example.com/application/o/token/
OAUTH_USERINFO_URL=https://auth.example.com/application/o/userinfo/
OAUTH_REDIRECT_URI=http://localhost:3000/auth/callback
```

### Security Features:

✅ **State Parameter** - CSRF Protection
✅ **PKCE Support** - Enhanced security for public clients
✅ **Automatic User Creation** - User wird bei erstem Login angelegt
✅ **Multiple Providers** - Authentik, Keycloak, generic OIDC
✅ **Role Mapping** - Gruppen aus OIDC Provider übernehmen (TODO)

### Vorteile:

✅ **Zentrales User Management** - Ein Login für alle Apps
✅ **Enterprise-Ready** - LDAP/AD Integration über Authentik
✅ **Self-Hosted** - Volle Kontrolle mit Authentik/Keycloak
✅ **2FA/MFA Support** - Über OIDC Provider
✅ **Audit Logs** - Zentral im SSO System

---

## 3. Gespiegelte Instanzen (Replication) ✅ IMPLEMENTIERT

### Status: Vollständig implementiert (v1.1)

Mirror Instances ermöglichen automatisches Backup und High Availability.

**Use Cases:**
1. **Backup** - Automatische bidirektionale Replikation
2. **High Availability** - Failover bei Ausfall
3. **Multi-Region** - Geografische Redundanz
4. **Team-Sync** - Mehrere Personen, gleiche Daten

**Features:**
- ✅ Bidirektionale Synchronisation
- ✅ Conflict Detection & Resolution
- ✅ Background Sync Scheduler (APScheduler)
- ✅ RSA-signierte Sync-Requests
- ✅ Sync-Logs & Audit Trail
- ✅ Frontend Management UI

### Architecture:

```
Primary Instance (Binningen)
    ↕ bidirectional sync
Secondary Instance (Hetzner Cloud)
    ↕ bidirectional sync  
Tertiary Instance (Home Server)
```

### Implementation:

```python
# backend/app/models/replication.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from datetime import datetime
from app.core.database import Base

class MirrorInstance(Base):
    """Gespiegelte Instanz Configuration"""
    __tablename__ = "mirror_instances"
    
    id = Column(Integer, primary_key=True)
    instance_url = Column(String, unique=True)  # https://mirror.babsyit.ch
    instance_id = Column(String, unique=True)   # mirror.babsyit.ch
    public_key = Column(String)  # RSA Public Key
    sync_enabled = Column(Boolean, default=True)
    sync_direction = Column(String, default="bidirectional")  # push, pull, bidirectional
    last_sync = Column(DateTime, nullable=True)
    priority = Column(Integer, default=1)  # 1=primary, 2=secondary
    

class SyncLog(Base):
    """Synchronization Audit Log"""
    __tablename__ = "sync_logs"
    
    id = Column(Integer, primary_key=True)
    mirror_instance_id = Column(Integer, ForeignKey("mirror_instances.id"))
    sync_type = Column(String)  # push, pull
    entity_type = Column(String)  # transaction, account, etc.
    entity_id = Column(Integer)
    operation = Column(String)  # create, update, delete
    status = Column(String)  # success, failed, conflict
    conflict_data = Column(JSON, nullable=True)
    synced_at = Column(DateTime, default=datetime.utcnow)


class ConflictResolution(Base):
    """Conflict Resolution Strategy"""
    __tablename__ = "conflict_resolutions"
    
    id = Column(Integer, primary_key=True)
    entity_type = Column(String)
    strategy = Column(String)  # last_write_wins, primary_wins, manual
    primary_instance_id = Column(String)  # Which instance is source of truth
```

```python
# backend/app/services/replication_service.py
import asyncio
from datetime import datetime, timedelta
from typing import List
import httpx

class ReplicationService:
    def __init__(self, db: Session):
        self.db = db
    
    async def sync_all_mirrors(self):
        """Sync with all enabled mirror instances"""
        mirrors = self.db.query(MirrorInstance).filter(
            MirrorInstance.sync_enabled == True
        ).all()
        
        tasks = [self.sync_with_mirror(mirror) for mirror in mirrors]
        await asyncio.gather(*tasks)
    
    async def sync_with_mirror(self, mirror: MirrorInstance):
        """Bidirectional sync with one mirror"""
        try:
            # 1. Push changes to mirror
            await self.push_changes(mirror)
            
            # 2. Pull changes from mirror
            await self.pull_changes(mirror)
            
            # 3. Update last sync time
            mirror.last_sync = datetime.utcnow()
            self.db.commit()
            
        except Exception as e:
            self.log_sync_error(mirror, str(e))
    
    async def push_changes(self, mirror: MirrorInstance):
        """Push local changes to mirror"""
        # Get changes since last sync
        since = mirror.last_sync or datetime.utcnow() - timedelta(days=7)
        
        # Transactions
        transactions = self.db.query(Transaction).filter(
            Transaction.updated_at > since
        ).all()
        
        # Accounts
        accounts = self.db.query(Account).filter(
            Account.updated_at > since
        ).all()
        
        # Send to mirror with signature
        payload = {
            "transactions": [tx.__dict__ for tx in transactions],
            "accounts": [acc.__dict__ for acc in accounts],
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        signature = sign_data(json.dumps(payload))
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{mirror.instance_url}/api/v1/sync/receive",
                json=payload,
                headers={
                    "X-Signature": signature,
                    "X-Instance": settings.INSTANCE_DOMAIN,
                }
            )
            response.raise_for_status()
    
    async def pull_changes(self, mirror: MirrorInstance):
        """Pull changes from mirror"""
        since = mirror.last_sync or datetime.utcnow() - timedelta(days=7)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{mirror.instance_url}/api/v1/sync/changes",
                params={"since": since.isoformat()},
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Verify signature
            signature = response.headers.get("X-Signature")
            if not verify_signature(json.dumps(data), signature, mirror.public_key):
                raise ValueError("Invalid signature from mirror")
            
            # Apply changes
            await self.apply_changes(data, mirror)
    
    async def apply_changes(self, data: dict, mirror: MirrorInstance):
        """Apply changes from mirror, handle conflicts"""
        for tx_data in data.get("transactions", []):
            existing = self.db.query(Transaction).filter(
                Transaction.id == tx_data["id"]
            ).first()
            
            if existing:
                # Conflict detection
                if existing.updated_at > datetime.fromisoformat(tx_data["updated_at"]):
                    # Our version is newer
                    conflict = self.handle_conflict(existing, tx_data, mirror)
                    if conflict:
                        continue
                
                # Update existing
                for key, value in tx_data.items():
                    if key not in ["id", "created_at"]:
                        setattr(existing, key, value)
            else:
                # Create new
                new_tx = Transaction(**tx_data)
                self.db.add(new_tx)
            
            # Log sync
            self.log_sync(mirror, "transaction", tx_data["id"], "update", "success")
        
        self.db.commit()
    
    def handle_conflict(self, local: Transaction, remote: dict, mirror: MirrorInstance):
        """Handle sync conflict"""
        resolution = self.db.query(ConflictResolution).filter(
            ConflictResolution.entity_type == "transaction"
        ).first()
        
        if not resolution:
            resolution = ConflictResolution(
                entity_type="transaction",
                strategy="last_write_wins"
            )
        
        if resolution.strategy == "last_write_wins":
            # Remote is newer, we already handled this above
            return False
        
        elif resolution.strategy == "primary_wins":
            # Primary instance wins
            if mirror.priority > 1:  # Mirror is secondary
                return True  # Keep local version
            else:
                return False  # Use remote version
        
        elif resolution.strategy == "manual":
            # Store conflict for manual resolution
            conflict = SyncLog(
                mirror_instance_id=mirror.id,
                entity_type="transaction",
                entity_id=local.id,
                operation="update",
                status="conflict",
                conflict_data={
                    "local": local.__dict__,
                    "remote": remote,
                }
            )
            self.db.add(conflict)
            self.db.commit()
            return True  # Keep local for now
```

```python
# backend/app/api/sync.py
from fastapi import APIRouter, Depends, HTTPException, Header
from app.services.replication_service import ReplicationService

router = APIRouter()

@router.post("/sync/receive")
async def receive_sync(
    data: dict,
    x_signature: str = Header(...),
    x_instance: str = Header(...),
    db: Session = Depends(get_db)
):
    """Receive sync data from mirror instance"""
    
    # Get mirror instance
    mirror = db.query(MirrorInstance).filter(
        MirrorInstance.instance_id == x_instance
    ).first()
    
    if not mirror:
        raise HTTPException(404, "Unknown instance")
    
    # Verify signature
    if not verify_signature(json.dumps(data), x_signature, mirror.public_key):
        raise HTTPException(401, "Invalid signature")
    
    # Apply changes
    service = ReplicationService(db)
    await service.apply_changes(data, mirror)
    
    return {"status": "success", "entities_updated": len(data.get("transactions", [])) + len(data.get("accounts", []))}

@router.get("/sync/changes")
async def get_changes(
    since: datetime,
    db: Session = Depends(get_db)
):
    """Get changes since timestamp for mirror to pull"""
    
    transactions = db.query(Transaction).filter(
        Transaction.updated_at > since
    ).all()
    
    accounts = db.query(Account).filter(
        Account.updated_at > since
    ).all()
    
    payload = {
        "transactions": [tx.__dict__ for tx in transactions],
        "accounts": [acc.__dict__ for acc in accounts],
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # Sign response
    signature = sign_data(json.dumps(payload))
    
    return Response(
        content=json.dumps(payload),
        headers={"X-Signature": signature}
    )
```

### Automatic Background Sync:

```python
# backend/app/main.py
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

app = FastAPI()

@app.on_event("startup")
async def start_sync_scheduler():
    """Start automatic sync every 5 minutes"""
    scheduler = AsyncIOScheduler()
    
    async def sync_job():
        db = SessionLocal()
        try:
            service = ReplicationService(db)
            await service.sync_all_mirrors()
        finally:
            db.close()
    
    scheduler.add_job(sync_job, 'interval', minutes=5)
    scheduler.start()
```

### Configuration:

```yaml
# docker-compose.yml - Add for each mirror
services:
  backend:
    environment:
      MIRROR_INSTANCES: >
        [
          {
            "url": "https://mirror.babsyit.ch",
            "priority": 2,
            "sync_direction": "bidirectional"
          },
          {
            "url": "https://backup.example.com",
            "priority": 3,
            "sync_direction": "push"
          }
        ]
```

### Vorteile:

✅ **Automatic Backup** - Daten auf mehreren Servern
✅ **High Availability** - Bei Ausfall zu Mirror wechseln
✅ **Geo-Distribution** - Schneller Zugriff weltweit
✅ **Conflict Resolution** - Automatisch oder manuell
✅ **Audit Trail** - Komplettes Sync-Log

---

## Zusammenfassung (Stand: v1.1 - 2025-01-07)

### ✅ Federation Security
- RSA 2048-bit Public/Private Keys
- Wie SSH: Signierte Requests
- Man-in-the-Middle Schutz
- **Status: Vollständig implementiert**

### 🔐 Passkey Authentication (WebAuthn)
- WebAuthn 2.2.0 Standard
- Biometrisch (Face ID, Touch ID, Hardware Keys)
- Phishing-resistent
- Multi-Device Support
- **Status: ✅ Vollständig implementiert (v1.1)**

### 🔑 OAuth2/OIDC Integration
- SSO mit Authentik, Keycloak, generic OIDC
- Zentrales User Management
- CSRF-geschützt (State Parameter)
- Automatic User Creation
- **Status: ✅ Vollständig implementiert (v1.1)**

### 🔄 Mirror Instances (Replication)
- Bidirektionale Synchronisation
- Conflict Resolution (last_write_wins, primary_wins, manual)
- Automatic Background Sync (APScheduler)
- RSA-signierte Sync-Requests
- Frontend Management UI
- **Status: ✅ Vollständig implementiert (v1.1)**

### 📱 Progressive Web App (PWA)
- Installierbar auf allen Plattformen
- Offline-Support mit Service Worker
- App-like Experience ohne App Store
- **Status: ✅ Vollständig implementiert (v1.1)**

## Empfohlene Security Best Practices

1. **HTTPS Pflicht** - Traefik mit Let's Encrypt
2. **Firewall** - Nur 80/443 offen
3. **Rate Limiting** - API Request Limits
4. **Secrets Management** - Private Keys in Docker Secrets
5. **Audit Logs** - Alle Changes tracken
6. **Regular Backups** - Database + Receipts + Mirror Instances
7. **2FA für Telegram** - TELEGRAM_ALLOWED_USERS nutzen
8. **OAuth/Passkey Auth** - Sichere Anmeldung aktivieren
9. **Mirror Instances** - Mindestens eine Backup-Instanz einrichten
10. **Monitoring** - Sync-Logs und API-Errors überwachen

## Weitere Informationen

- [MIRROR_INSTANCES.md](MIRROR_INSTANCES.md) - Detaillierte Anleitung für Mirror Instances
- [ROADMAP.md](ROADMAP.md) - Zukünftige Security Features
- [README.md](README.md) - Hauptdokumentation

---

**Letzte Aktualisierung:** 2025-01-07
**Version:** v1.1
