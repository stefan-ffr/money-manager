# Money Manager - Feature Updates

## 🔴 Automatische Einträge - Rote Markierung

### Problem
Einträge die automatisch erstellt werden (Telegram, Federation, CSV Import) sollten vor der Buchung überprüft werden können.

### Lösung
Alle automatischen Einträge werden **rot markiert** und erfordern manuelle Bestätigung.

### Visual

```
┌─────────────────────────────────────────────────────────────────┐
│ Transaktionen                                                    │
├─────────────────────────────────────────────────────────────────┤
│ Status │ Datum      │ Beschreibung           │ Quelle    │ CHF  │
├─────────────────────────────────────────────────────────────────┤
│ ✓      │ 01.12.2024 │ Miete Dezember         │ Manuell   │ -1200│
├─────────────────────────────────────────────────────────────────┤
│ ⚠️      │ 05.12.2024 │ Migros Einkauf         │ Telegram  │ -45  │
│        │            │ ⚠️ Bestätigung erforderlich            │     │
│        │            │ [✓ Bestätigen] [Löschen]              │     │
├─────────────────────────────────────────────────────────────────┤ ← ROT
│ ⚠️      │ 06.12.2024 │ From anna@money.ch     │ Federation│ -150 │
│        │            │ ⚠️ Bestätigung erforderlich            │     │
│        │            │ [✓ Bestätigen] [Löschen]              │     │
├─────────────────────────────────────────────────────────────────┤ ← ROT
│ ✓      │ 07.12.2024 │ Lohn                   │ Manuell   │ +5000│
└─────────────────────────────────────────────────────────────────┘
```

### Technische Details

**Backend:**
```python
class Transaction(Base):
    # ... existing fields
    source = Column(String(20), default="manual")  
    # Optionen: manual, telegram, federation, csv_import
    
    requires_confirmation = Column(Boolean, default=False)
    # True = Rot markiert, muss bestätigt werden
```

**Frontend:**
```tsx
<tr className={tx.requires_confirmation ? 
    'bg-red-50 border-l-4 border-red-500' : ''}>
  {tx.requires_confirmation && (
    <button onClick={confirm}>✓ Bestätigen</button>
  )}
</tr>
```

**Workflow:**
1. Telegram Bot erstellt Eintrag → `source="telegram"`, `requires_confirmation=True`
2. User sieht rote Markierung
3. User klickt "Bestätigen" → `status="confirmed"`, `requires_confirmation=False`
4. Eintrag wird normal angezeigt

### Quellen

| Source       | Beschreibung                  | Automatisch? |
|--------------|-------------------------------|--------------|
| `manual`     | Manuell erstellt (Web UI)     | ❌           |
| `telegram`   | Via Telegram Bot              | ✅ Rot       |
| `federation` | Von anderer Instanz           | ✅ Rot       |
| `csv_import` | CSV Bank-Import               | ✅ Rot       |

---

## 🔐 Sicherheitsfeatures

### 1. Federation Security (✅ Implementiert)

**RSA Public/Private Key wie SSH**

```
Instance A                          Instance B
    │                                   │
    │  1. Generate Invoice               │
    │  2. Sign with Private Key         │
    │────────────────────────────────►  │
    │     Signed Invoice + Signature    │
    │                                   │
    │                                   │  3. Fetch Public Key
    │                                   │  4. Verify Signature
    │                                   │  5. Accept if valid
    │  ◄────────────────────────────────│
    │         Confirmation              │
```

**Key Features:**
- 🔒 2048-bit RSA Keys
- ✅ Signature Verification
- 🚫 Man-in-the-Middle Protection
- 🔑 Public Key Discovery via /.well-known/

**Security Check:**
```bash
# Dein Public Key ist öffentlich
curl https://money.babsyit.ch/.well-known/money-instance

# Andere Instanzen können ihn verifizieren
{
  "instance_id": "money.babsyit.ch",
  "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIj...",
  "api_endpoint": "https://money.babsyit.ch/api/v1"
}
```

### 2. Passkey Authentication (🔧 Bereit zur Implementierung)

**Warum Passkeys?**
- ❌ Keine Passwörter (nichts zu merken, nichts zu hacken)
- 📱 Biometrisch (Face ID, Touch ID, Fingerprint)
- 🔐 Hardware Keys (YubiKey)
- 🚫 Phishing-Resistent

**User Flow:**

```
Registration:
User → [Email + Username] → Server generates challenge
    → Browser triggers Passkey creation (Face ID)
    → Credential stored on device
    → Public key sent to server

Login:
User → [Username] → Server sends challenge
    → Browser requests Passkey (Face ID)
    → Signature created
    → Server verifies with stored public key
    → ✅ Logged in
```

**Supported Devices:**
- 📱 iPhone/iPad (Face ID, Touch ID)
- 🖥️ Mac (Touch ID)
- 🤖 Android (Fingerprint, Face)
- 💻 Windows Hello
- 🔑 YubiKey, FIDO2 Keys

### 3. Mirror Instances (🔄 Konzept fertig)

**Gespiegelte Instanzen für:**
- 💾 Automatic Backup
- 🌍 High Availability
- ⚡ Geo-Distribution
- 👥 Team-Sync

**Architecture:**

```
    Primary (Binningen)           Secondary (Hetzner)
    ┌─────────────┐              ┌─────────────┐
    │  Database   │◄────sync────►│  Database   │
    │  Receipts   │              │  Receipts   │
    └─────────────┘              └─────────────┘
          │                            │
          │                            │
          └────────┬───────────────────┘
                   │
                   ▼
           Tertiary (Home Server)
           ┌─────────────┐
           │  Database   │
           │  Receipts   │
           └─────────────┘
```

**Sync Modes:**
- `push` - Nur zu Mirror pushen
- `pull` - Nur von Mirror holen
- `bidirectional` - Beide Richtungen

**Conflict Resolution:**
- `last_write_wins` - Neuester Timestamp gewinnt
- `primary_wins` - Primary Instance ist Quelle
- `manual` - Manuelle Auflösung nötig

**Automatic Sync:**
```python
# Alle 5 Minuten automatisch
scheduler.add_job(sync_job, 'interval', minutes=5)

# Oder on-demand
POST /api/v1/sync/trigger
```

---

## 📊 Feature Comparison

| Feature                    | Status    | Security Level |
|----------------------------|-----------|----------------|
| Manual Entry               | ✅ Live   | ⭐⭐⭐⭐⭐     |
| Telegram Bot               | ✅ Live   | ⭐⭐⭐⭐       |
| Federation                 | ✅ Live   | ⭐⭐⭐⭐⭐     |
| CSV Import                 | 🔧 Planned| ⭐⭐⭐⭐       |
| Passkey Auth               | 🔧 Ready  | ⭐⭐⭐⭐⭐     |
| Mirror Instances           | 🔧 Ready  | ⭐⭐⭐⭐⭐     |
| Red Confirmation Required  | ✅ Live   | ⭐⭐⭐⭐⭐     |

---

## 🎯 Roadmap

### v1.0 - Current
- [x] Basic CRUD
- [x] Telegram Bot
- [x] Federation
- [x] Red Confirmation for Auto-Entries
- [x] EasyTax Export

### v1.1 - Security & Sync
- [ ] Passkey Authentication
- [ ] Mirror Instances
- [ ] Replay Protection (Timestamp + Nonce)
- [ ] Rate Limiting
- [ ] Audit Logs

### v1.2 - Bank Integration
- [ ] ISO 20022 camt.053 Parser
- [ ] eBill Integration
- [ ] Multi-Bank CSV Import
- [ ] Automatic Categorization (ML)

### v2.0 - Advanced
- [ ] Mobile App (React Native)
- [ ] Multi-Currency
- [ ] Budget Tracking
- [ ] Custom Reports
- [ ] Encrypted Backups

---

## 💡 Tips & Tricks

### Telegram Bot Best Practices
```
✅ DO: Send clear, well-lit photos of receipts
✅ DO: Confirm entries immediately
✅ DO: Use /pending to review open items

❌ DON'T: Send multiple receipts at once (one at a time!)
❌ DON'T: Delete without checking
```

### Federation Security
```bash
# Always verify instance before adding
curl https://unknown-instance.com/.well-known/money-instance

# Check public key fingerprint
openssl rsa -pubin -in public_key.pem -text -noout

# Rotate keys yearly
docker compose exec backend python -m app.scripts.rotate_keys
```

### Mirror Setup
```yaml
# docker-compose.yml
environment:
  MIRROR_INSTANCES: >
    [{
      "url": "https://backup.example.com",
      "priority": 2,  # Lower = Higher Priority
      "sync_direction": "bidirectional"
    }]
```

---

## 🔧 Development Guide

### Adding New Auto-Source

```python
# 1. Add source type in model
# backend/app/models/transaction.py
source = Column(String(20), default="manual")
# Add: my_new_source

# 2. Create entries with requires_confirmation=True
transaction = Transaction(
    # ... fields
    source="my_new_source",
    requires_confirmation=True
)

# 3. Add badge in frontend
// frontend/src/components/TransactionList.tsx
const badges = {
  my_new_source: { 
    color: 'bg-orange-100 text-orange-800', 
    label: 'My Source' 
  }
}
```

### Testing Confirmation Flow

```bash
# Create test entry
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "date": "2024-12-07",
    "amount": -99.99,
    "description": "Test Entry",
    "source": "telegram",
    "requires_confirmation": true
  }'

# Verify it shows red in UI
open http://localhost:3000/transactions

# Confirm via API
curl -X PUT http://localhost:8000/api/v1/transactions/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "confirmed",
    "requires_confirmation": false
  }'
```

---

## 📚 Further Reading

- [WebAuthn Guide](https://webauthn.guide/)
- [RSA Cryptography Explained](https://en.wikipedia.org/wiki/RSA_(cryptosystem))
- [Database Replication Patterns](https://martinfowler.com/articles/patterns-of-distributed-systems/)
- [Fediverse Federation](https://en.wikipedia.org/wiki/Fediverse)
