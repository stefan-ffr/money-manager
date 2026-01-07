# Money Manager - Projekt Struktur

## Übersicht

```
money-manager/
├── .github/
│   └── workflows/
│       └── docker-build.yml      # GitHub Actions für Container-Build
├── backend/
│   ├── app/
│   │   ├── api/                  # API Endpoints (FastAPI Routers)
│   │   │   ├── accounts.py       # Account CRUD
│   │   │   ├── transactions.py   # Transaction CRUD + Receipt Upload
│   │   │   ├── categories.py     # Categories + EasyTax Export
│   │   │   ├── shared_accounts.py # Gemeinschaftskonten
│   │   │   └── federation.py     # Inter-Instanz Communication
│   │   ├── core/                 # Zentrale Konfiguration
│   │   │   ├── config.py         # Settings (Pydantic)
│   │   │   └── database.py       # SQLAlchemy Setup
│   │   ├── models/               # Database Models
│   │   │   ├── account.py
│   │   │   ├── transaction.py
│   │   │   ├── category.py
│   │   │   └── shared_account.py
│   │   ├── services/             # Business Logic
│   │   │   ├── split_service.py      # Gemeinschaftskonto Logik
│   │   │   └── federation_service.py # Federation Logik
│   │   ├── federation/           # Kryptographie
│   │   │   └── crypto.py         # RSA Signing/Verification
│   │   └── main.py               # FastAPI App Entry Point
│   ├── alembic/                  # Database Migrations
│   │   └── versions/
│   ├── telegram_bot.py           # Telegram Bot
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── components/           # React Components
│   │   │   └── Layout.tsx        # Navigation Layout
│   │   ├── pages/                # Seiten
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Accounts.tsx
│   │   │   ├── Transactions.tsx
│   │   │   ├── SharedAccounts.tsx
│   │   │   └── Settings.tsx
│   │   ├── services/             # API Calls (wird erweitert)
│   │   ├── App.tsx               # Main App Component
│   │   ├── main.tsx              # Entry Point
│   │   └── index.css             # Tailwind CSS
│   ├── public/
│   ├── package.json
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
├── docker-compose.yml            # Multi-Container Setup
├── .env.example                  # Environment Template
├── .gitignore
├── README.md                     # Hauptdokumentation
├── QUICKSTART.md                 # Setup-Anleitung
├── CONTRIBUTING.md               # Contribution Guidelines
└── LICENSE                       # MIT License
```

## Services im docker-compose.yml

1. **db** - PostgreSQL 16 Database
2. **backend** - FastAPI REST API
3. **telegram-bot** - Telegram Bot Service
4. **frontend** - React App (über Nginx)
5. **traefik** (optional) - Reverse Proxy mit HTTPS

## Datenfluss

### Normaler Workflow
```
User → Frontend → Backend API → Database
                      ↓
                  Receipts Storage
```

### Telegram Workflow
```
User → Telegram Bot → Backend API → Database
                         ↓
                    OCR Processing
                         ↓
                   Receipts Storage
```

### Federation Workflow
```
Instance A → Sign Request → Instance B
    ↓                           ↓
Verify Response ← Sign Response ←
    ↓
Store Transaction
```

## API Endpoints

### Accounts
- `GET /api/v1/accounts` - Liste aller Konten
- `GET /api/v1/accounts/{id}` - Ein Konto
- `POST /api/v1/accounts` - Konto erstellen
- `PUT /api/v1/accounts/{id}` - Konto aktualisieren
- `DELETE /api/v1/accounts/{id}` - Konto löschen

### Transactions
- `GET /api/v1/transactions` - Liste mit Filtern
- `POST /api/v1/transactions` - Transaktion erstellen
- `PUT /api/v1/transactions/{id}` - Aktualisieren
- `POST /api/v1/transactions/{id}/receipt` - Receipt hochladen
- `GET /api/v1/transactions/{id}/receipt` - Receipt abrufen

### Categories
- `GET /api/v1/categories` - Alle Kategorien
- `POST /api/v1/categories` - Kategorie erstellen
- `GET /api/v1/categories/easytax-export` - EasyTax CSV Export

### Shared Accounts
- `GET /api/v1/shared-accounts` - Liste
- `POST /api/v1/shared-accounts` - Erstellen
- `POST /api/v1/shared-accounts/{id}/members` - Member hinzufügen
- `POST /api/v1/shared-accounts/{id}/split-transaction` - Split erstellen
- `GET /api/v1/shared-accounts/{id}/balance` - Balance berechnen
- `POST /api/v1/shared-accounts/{id}/settle` - Ausgleich berechnen

### Federation
- `POST /api/v1/federation/invoice/send` - Invoice senden
- `POST /api/v1/federation/invoice/receive` - Invoice empfangen
- `POST /api/v1/federation/invoice/{id}/accept` - Akzeptieren
- `POST /api/v1/federation/invoice/{id}/reject` - Ablehnen
- `GET /api/v1/federation/instances/{domain}` - Instanz Info abrufen

### Well-known
- `GET /.well-known/money-instance` - Federation Discovery

## Database Schema

### Accounts
- id, name, type, iban, balance, currency

### Transactions
- id, account_id, date, amount, category, description
- status, receipt_path, telegram_message_id

### Categories
- id, name, easytax_code, parent_id

### Shared Accounts
- SharedAccount: id, name, description, currency
- SharedAccountMember: id, shared_account_id, user_identifier, role
- SplitTransaction: id, shared_account_id, paid_by, total_amount
- SplitShare: id, split_transaction_id, user_identifier, share_amount
- Settlement: id, shared_account_id, from_user, to_user, amount

## Environment Variables

Wichtigste Variablen in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:pass@db:5432/money

# Security
SECRET_KEY=your-secret-key

# Telegram
TELEGRAM_BOT_TOKEN=bot_token
TELEGRAM_ALLOWED_USERS=123456789

# Federation
INSTANCE_DOMAIN=money.example.com
FEDERATION_ENABLED=true

# Frontend
VITE_API_URL=http://localhost:8000
```

## Erweiterungsmöglichkeiten

### Geplante Features (v1.1+)

1. **Bank Integration**
   - ISO 20022 camt.053 Parser
   - eBill Integration
   - Automatischer Import

2. **Erweiterte Analytics**
   - Budget-Tracking
   - Ausgaben-Prognosen
   - Custom Reports

3. **Mobile App**
   - React Native App
   - Offline-Modus
   - Push Notifications

4. **Multi-Currency**
   - Währungsumrechnung
   - Exchange Rate API
   - Multi-Currency Accounts

5. **Advanced Federation**
   - Automatische Instanz-Discovery
   - Verschlüsselte Nachrichten
   - Group-Settlements

### Code hinzufügen

Neue API Endpoints:
```python
# backend/app/api/new_feature.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def new_endpoint():
    return {"message": "Hello"}

# In main.py einbinden:
app.include_router(new_feature.router, prefix="/api/v1/new", tags=["new"])
```

Neue Frontend Page:
```tsx
// frontend/src/pages/NewPage.tsx
function NewPage() {
  return <div>New Page</div>
}

// In App.tsx einbinden:
<Route path="/new" element={<NewPage />} />
```

## Testing

```bash
# Backend Tests
cd backend
pytest

# Frontend Tests  
cd frontend
npm test

# E2E Tests (zukünftig)
npm run test:e2e
```

## Deployment Checklist

- [ ] Environment Variables gesetzt
- [ ] Database Backups eingerichtet
- [ ] HTTPS konfiguriert (Traefik/Let's Encrypt)
- [ ] Firewall Regeln gesetzt
- [ ] Monitoring eingerichtet
- [ ] Logs rotieren
- [ ] Federation Keys gesichert
- [ ] Telegram Bot Token sicher gespeichert

## Performance Tips

1. **Database**: Indizes auf oft genutzte Filter setzen
2. **API**: Caching für häufige Queries
3. **Frontend**: Code Splitting, Lazy Loading
4. **Federation**: Rate Limiting, Request Queuing
5. **Files**: CDN für Receipts (optional)
