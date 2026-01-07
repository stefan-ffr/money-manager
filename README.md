# Money Manager 💰

Eine moderne, selbst-gehostete Privatbuchhaltungs-Lösung für die Schweiz mit dezentraler Federation und Gemeinschaftskonten.

## Features

### Core Features
- 📊 **Multi-Account Management** - Giro, Sparkonto, Kreditkarte, Bargeld
- 💳 **Schweizer Bank-Import** - CSV Import für PostFinance, UBS, Raiffeisen, ZKB, BLKB, BKB, Migros Bank
- 📄 **Rechnungsverwaltung** - PDFs direkt an Transaktionen anhängen
- 🔍 **OCR für Belege** - Automatische Extraktion von Betrag, Datum, Beschreibung
- 📈 **Reports & Budgets** - Visualisierung deiner Finanzen
- 💱 **EasyTax Export** - Direkter Export für Schweizer Steuererklärung
- 🔴 **Auto-Entry Confirmation** - Automatische Einträge rot markiert, müssen bestätigt werden

### Telegram Integration
- 📲 **Telegram Bot** - Rechnungen per Telegram schicken
- ✅ **Provisorische Buchungen** - Review & Bestätigung über Telegram
- 🔔 **Notifications** - Benachrichtigungen für neue Transaktionen
- 🔴 **Red Flagging** - Telegram-Einträge erfordern manuelle Bestätigung

### Federation & Gemeinschaftskonten
- 🌐 **Inter-Instanz Kommunikation** - Rechnungen zwischen verschiedenen Instanzen teilen
- 🔐 **RSA Encryption** - Wie SSH: Signierte Requests mit Public/Private Keys
- 👥 **Shared Accounts** - WG-Konten, Vereinskassen, Familien-Budgets
- 🌍 **Cross-Instance Shared Accounts** - Member können auf verschiedenen Instanzen sein! (stefan@money.babsyit.ch, anna@money.example.com)
- ➗ **Smart Splitting** - Gleich, prozentual oder manuell aufteilen
- 💸 **Automatischer Ausgleich** - Berechnung wer wem wie viel schuldet
- 🔴 **Federation Confirmation** - Einträge von anderen Instanzen rot markiert

### Bank Integration 🏦
- 📥 **CSV Import mit Auto-Matching** - System findet automatisch das richtige Konto!
- 🏦 **8 Schweizer Banken** - PostFinance, UBS, Raiffeisen, ZKB, BLKB, BKB, Migros Bank, Credit Suisse
- 🔍 **IBAN-basiertes Matching** - Einmal konfigurieren, immer automatisch
- 🚫 **Duplicate Detection** - Keine doppelten Transaktionen
- 🔴 **Import Confirmation** - Alle Imports rot markiert für Review
- 📊 **Import Statistics** - Übersicht über alle Imports

### Security & Authentication (🆕 v1.1)
- 🔐 **Passkey Authentication** - WebAuthn/FIDO2 für biometrische Anmeldung (Face ID, Touch ID, Hardware Keys)
- 🔑 **OAuth2/OIDC Integration** - SSO mit Authentik, Keycloak oder anderen OIDC Providern
- 🔒 **RSA Public/Private Keys** - Sichere Federation wie SSH
- 🔄 **Mirror Instances** - Gespiegelte Instanzen für automatisches Backup & High Availability
- 📝 **Audit Logs** - Alle Sync-Operationen werden geloggt
- ⚠️ **Conflict Resolution** - Automatische oder manuelle Konfliktauflösung (last_write_wins, primary_wins, manual)
- 📱 **Progressive Web App (PWA)** - Installierbar auf Smartphone, Tablet und Desktop ohne App Store

## Schnellstart

### Mit Docker Compose (empfohlen)

```bash
# Repository klonen
git clone https://github.com/yourusername/money-manager.git
cd money-manager

# Environment Variables setzen
cp .env.example .env
# Editiere .env mit deinen Werten

# Container starten
docker compose up -d

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manuelles Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database Migration
alembic upgrade head

# Server starten
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Konfiguration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://money:password@db:5432/money

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OAuth2/OIDC (optional - für SSO)
OAUTH_ENABLED=true
OAUTH_CLIENT_ID=money-manager
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_AUTHORIZATION_URL=https://auth.example.com/application/o/authorize/
OAUTH_TOKEN_URL=https://auth.example.com/application/o/token/
OAUTH_USERINFO_URL=https://auth.example.com/application/o/userinfo/
OAUTH_REDIRECT_URI=http://localhost:3000/auth/callback

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ALLOWED_USERS=123456789,987654321

# Federation
INSTANCE_DOMAIN=money.example.com
FEDERATION_ENABLED=true
INSTANCE_PRIVATE_KEY_PATH=/app/secrets/instance_key.pem

# Mirror Instances / Replication
REPLICATION_ENABLED=true
REPLICATION_SYNC_INTERVAL_MINUTES=5
REPLICATION_CONFLICT_STRATEGY=last_write_wins  # last_write_wins, primary_wins, manual
```

### Telegram Bot Setup

1. Erstelle einen Bot mit [@BotFather](https://t.me/botfather)
2. Kopiere den Token in `.env`
3. Starte den Bot: `docker compose up telegram-bot`
4. Sende `/start` an deinen Bot

## Bank CSV Import

Unterstützte Formate:

### PostFinance
```csv
Buchungsdatum;Valutadatum;Avisierungstext;Lastschrift;Gutschrift;Saldo
01.12.2024;01.12.2024;TWINT Zahlung;;-45.50;2450.00
```

### UBS
```csv
Date;Description;Debit;Credit;Balance
01.12.2024;Payment from John Doe;;1000.00;5450.00
```

### Raiffeisen
```csv
Datum;Beschreibung;Belastung;Gutschrift;Saldo
01.12.2024;Lohn;;;5000.00;12450.00
```

## EasyTax Export

1. Gehe zu **Reports** → **EasyTax Export**
2. Wähle Jahr & Kategorien
3. Download CSV
4. In EasyTax importieren unter **Import** → **Banktransaktionen**

Format:
```csv
Datum;Betrag;Kategorie;Beschreibung;Belegnummer
01.01.2024;-1200.00;Miete;Mietzahlung Januar;RG-2024-001
```

## Federation Setup

### Instanz einrichten

1. Setze `INSTANCE_DOMAIN` in `.env`
2. Generiere Instanz-Keypair:
```bash
docker compose exec backend python -m app.scripts.generate_keys
```

3. Stelle sicher dass deine Instanz öffentlich erreichbar ist
4. Instanz ist erreichbar unter: `https://your-domain.com/.well-known/money-instance`

### Andere Instanz hinzufügen

1. Gehe zu **Settings** → **Federation**
2. Klicke **Instanz hinzufügen**
3. Gib Domain ein: `money.example.com`
4. System verifiziert automatisch Public Key

### Rechnung an andere Instanz senden

```
Empfänger: anna@money.example.com
Betrag: CHF 150.00
Beschreibung: Miete Anteil Dezember
```

## Gemeinschaftskonten

### Erstellen

1. Gehe zu **Accounts** → **Gemeinschaftskonto erstellen**
2. Name: "WG Haushalt"
3. Mitglieder hinzufügen:
   - `anna@money.example.com`
   - `tom@money.other.com`

### Rechnung teilen

1. Upload Rechnung (Telegram oder Web)
2. Wähle Gemeinschaftskonto
3. Split-Methode:
   - ➗ Gleich aufteilen
   - % Prozentual (z.B. 40/30/30)
   - ✏️ Manuell
4. System sendet automatisch an alle Mitglieder

### Ausgleich berechnen

Das System berechnet automatisch den optimalen Ausgleich (minimale Anzahl Transaktionen):

```
Stefan hat CHF 500 zu viel bezahlt
Anna schuldet Stefan CHF 250
Tom schuldet Stefan CHF 250
```

## API Dokumentation

Vollständige API Docs verfügbar unter: `http://localhost:8000/docs`

### Beispiel: Transaktion erstellen

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "date": "2024-12-01",
    "amount": -45.50,
    "category": "Groceries",
    "description": "Migros Einkauf"
  }'
```

## Entwicklung

### Architecture

### API-First Design 🚀
Money Manager folgt einer **vollständig API-basierten Architektur** - genau wie Cloudflare, Stripe oder Twilio.

```
┌─────────────────────────────────────────┐
│         FastAPI REST API                │
│     (Everything is an API)              │
└─────────────────────────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
  Web UI   Mobile   CLI/Scripts
```

**Benefits:**
- ✅ Frontend komplett entkoppelt vom Backend
- ✅ Jeder kann die API nutzen (Web, Mobile, CLI, Automation)
- ✅ Auto-Generated OpenAPI Docs (`/docs`)
- ✅ Einfaches Testing mit curl/Postman
- ✅ Horizontal skalierbar
- ✅ Multiple Clients möglich

**API Docs:** http://localhost:8000/docs  
**Vollständige Dokumentation:** [API_ARCHITECTURE.md](API_ARCHITECTURE.md)

### Multi-Currency Support 💱
Unterstützt **15+ Währungen** out-of-the-box:
- **CHF** - Schweizer Franken (mit Schweizer Formatierung: 1'234.56 CHF)
- **EUR** - Euro (1.234,56 €)
- **USD** - US Dollar ($1,234.56)
- **THB** - Thai Baht (฿50,000.00)
- **GBP, JPY, CNY, AUD, CAD, SGD, INR, BRL, ZAR**
- **BTC, ETH** - Crypto (experimental)

Jede Währung mit korrektem:
- Symbol (฿, €, $, £, ¥, ₹, ₿)
- Tausendertrennzeichen (', . oder ,)
- Dezimalstellen (0-18)
- Formatierung nach Landesstandard

**Weitere Währungen hinzufügen:** Einfach in `backend/app/core/currencies.py`

## Tech Stack

- **Backend**: FastAPI (Python 3.12+)
- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Database**: PostgreSQL 16
- **OCR**: Tesseract / Poppler
- **Telegram**: python-telegram-bot

### Projekt-Struktur

```
money-manager/
├── backend/
│   ├── app/
│   │   ├── api/          # API Endpoints
│   │   ├── core/         # Config, Security
│   │   ├── models/       # SQLAlchemy Models
│   │   ├── services/     # Business Logic
│   │   └── federation/   # Inter-Instanz Communication
│   ├── alembic/          # DB Migrations
│   └── telegram_bot.py   # Telegram Bot
├── frontend/
│   └── src/
│       ├── components/   # React Components
│       ├── pages/        # Pages
│       └── services/     # API Calls
└── docker-compose.yml
```

### Tests ausführen

```bash
# Backend Tests
cd backend
pytest

# Frontend Tests
cd frontend
npm test
```

## GitHub Actions

Das Projekt nutzt GitHub Actions für automatisches Container-Building:

- **Push auf `main`**: Baut und pusht `latest` Tag
- **Push eines Tags (`v*`)**: Baut Release-Version
- **Pull Requests**: Führt Tests aus

Container verfügbar auf GitHub Container Registry:
```bash
docker pull ghcr.io/yourusername/money-manager-backend:latest
docker pull ghcr.io/yourusername/money-manager-frontend:latest
```

## Roadmap

### v1.0 (Current) ✅
- ✅ Basic CRUD für Accounts & Transactions
- ✅ Bank CSV Import
- ✅ Telegram Bot
- ✅ OCR für Rechnungen
- ✅ EasyTax Export
- ✅ Federation & Inter-Instanz Communication
- ✅ Gemeinschaftskonten
- ✅ Red Confirmation für Auto-Entries
- ✅ **Umfassende Settings Page**

### v1.1 (Q1 2025) ✅ FERTIG!
- ✅ **Passkey Authentication** (WebAuthn) - Biometrische Anmeldung mit Face ID, Touch ID, Hardware Keys
- ✅ **OAuth2/OIDC Integration** - SSO mit Authentik, Keycloak oder anderen OIDC Providern
- ✅ **Progressive Web App (PWA)** - Installierbar auf allen Plattformen ohne App Store
- ✅ **Mirror Instances** - Bidirektionale Synchronisation für Backup & High Availability
- ⏳ Replay Protection (Timestamp + Nonce)
- ⏳ Rate Limiting & Audit Logs
- ⏳ Recurring Transactions

### v1.2 (Q2 2025)
- ⏳ ISO 20022 camt.053 Parser
- ⏳ eBill Integration
- ⏳ Enhanced CSV Import (5+ Schweizer Banken)
- ⏳ Automatic Categorization (ML)

### v2.0 (Q4 2025)
- ⏳ Mobile App (React Native)
- ⏳ Multi-Currency Support
- ⏳ Budget Tracking & Analytics
- ⏳ Advanced Reports

Vollständige Roadmap: [ROADMAP.md](ROADMAP.md)

## Support

- 📖 [Dokumentation](https://github.com/yourusername/money-manager/wiki)
- 🐛 [Issues](https://github.com/yourusername/money-manager/issues)
- 💬 [Discussions](https://github.com/yourusername/money-manager/discussions)

## Lizenz

MIT License - siehe [LICENSE](LICENSE)

## Credits

Inspiriert von MS Money 99 und modernen Self-Hosted Finance Tools wie Firefly III und Actual Budget.
