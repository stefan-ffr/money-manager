# Money Manager - Quick Start Guide

## 1. GitHub Repository erstellen

```bash
# Entpacke das Archiv
tar -xzf money-manager.tar.gz
cd money-manager

# Git initialisieren
git init
git add .
git commit -m "Initial commit: Money Manager"

# GitHub Repository erstellen und pushen
# Erstelle zuerst ein neues Repo auf github.com
git remote add origin https://github.com/DEIN-USERNAME/money-manager.git
git branch -M main
git push -u origin main
```

## 2. GitHub Actions aktivieren

GitHub Actions werden automatisch aktiviert. Die Container werden gebaut bei:
- **Push auf `main`** → `latest` Tag
- **Push eines Tags** (z.B. `v1.0.0`) → Release Version

Die Container sind dann verfügbar unter:
```
ghcr.io/DEIN-USERNAME/money-manager-backend:latest
ghcr.io/DEIN-USERNAME/money-manager-frontend:latest
```

## 3. Lokale Entwicklung starten

```bash
# 1. Environment Variables setzen
cp .env.example .env
nano .env  # Bearbeite mit deinen Werten

# 2. Docker Compose starten
docker compose up -d

# 3. URLs:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 4. Telegram Bot einrichten

```bash
# 1. Bot erstellen bei @BotFather auf Telegram
# 2. Token kopieren in .env
TELEGRAM_BOT_TOKEN=dein_token_hier

# 3. Deine User ID herausfinden
# Sende eine Nachricht an @userinfobot
TELEGRAM_ALLOWED_USERS=deine_user_id_hier

# 4. Bot neu starten
docker compose restart telegram-bot
```

## 5. Erste Schritte

1. **Konto erstellen**
   ```bash
   curl -X POST http://localhost:8000/api/v1/accounts \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Girokonto",
       "type": "checking",
       "balance": 1000.00
     }'
   ```

2. **Transaktion erstellen**
   ```bash
   curl -X POST http://localhost:8000/api/v1/transactions \
     -H "Content-Type: application/json" \
     -d '{
       "account_id": 1,
       "date": "2024-12-01",
       "amount": -45.50,
       "description": "Einkauf"
     }'
   ```

3. **Rechnung per Telegram senden**
   - Sende PDF/Foto an deinen Bot
   - Bot erstellt provisorische Buchung
   - Bestätige mit Button

## 6. Production Deployment

### Option 1: Docker Compose auf Server

```bash
# Auf deinem Server
git clone https://github.com/DEIN-USERNAME/money-manager.git
cd money-manager

# Environment setzen
cp .env.example .env
nano .env

# Mit Traefik für HTTPS (optional)
# Kommentiere Traefik Service in docker-compose.yml ein
docker compose up -d
```

### Option 2: GitHub Container Registry nutzen

```yaml
# docker-compose.prod.yml
services:
  backend:
    image: ghcr.io/DEIN-USERNAME/money-manager-backend:latest
    # ... rest der config

  frontend:
    image: ghcr.io/DEIN-USERNAME/money-manager-frontend:latest
    # ... rest der config
```

## 7. Federation Setup (Optional)

Für Inter-Instanz Communication:

```bash
# 1. Keypair generieren
docker compose exec backend python -c "
from app.federation.crypto import generate_key_pair
generate_key_pair()
print('Keypair generated!')
"

# 2. Domain in .env setzen
INSTANCE_DOMAIN=money.example.com
FEDERATION_ENABLED=true

# 3. Instanz muss öffentlich erreichbar sein
# z.B. über Traefik mit Let's Encrypt
```

## 8. Bank CSV Import (mit Auto-Matching)

```bash
# 1. Konto für Auto-Import konfigurieren (einmal!)
curl -X POST http://localhost:8000/api/v1/import/bank/setup \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "bank_name": "PostFinance",
    "bank_identifier": "CH9300762011623852957",
    "enable_auto_import": true
  }'

# 2. CSV importieren (System findet automatisch das richtige Konto!)
curl -X POST http://localhost:8000/api/v1/import/bank/import \
  -F "file=@postfinance_export.csv" \
  -F "auto_match=true"

# Response:
# {
#   "success": true,
#   "bank": "postfinance",
#   "account_name": "Girokonto",
#   "transactions_created": 45,
#   "duplicates_skipped": 3
# }
```

**Python Script:**
```python
import requests

# Setup Account (einmal)
requests.post('http://localhost:8000/api/v1/import/bank/setup', json={
    "account_id": 1,
    "bank_name": "PostFinance",
    "bank_identifier": "CH9300762011623852957"
})

# Import CSV (immer)
with open('bank_export.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/import/bank/import',
        files={'file': f},
        data={'auto_match': 'true'}
    )
    print(response.json())
```

**Unterstützte Banken:** PostFinance, UBS, Raiffeisen, ZKB, Credit Suisse
```

## 9. Backup

```bash
# Database Backup
docker compose exec db pg_dump -U money money > backup.sql

# Receipts Backup
tar -czf receipts-backup.tar.gz receipts/
```

## Troubleshooting

**Port bereits belegt?**
```bash
# Ändere Ports in docker-compose.yml
ports:
  - "3001:3000"  # Frontend
  - "8001:8000"  # Backend
```

**Database Migration Fehler?**
```bash
docker compose exec backend alembic upgrade head
```

**Telegram Bot antwortet nicht?**
```bash
# Logs prüfen
docker compose logs telegram-bot

# User ID korrekt?
docker compose exec backend python -c "
from app.core.config import settings
print(settings.get_allowed_telegram_users())
"
```

## Nächste Schritte

- [ ] Kategorien anlegen für EasyTax
- [ ] Bank CSV Import testen
- [ ] Gemeinschaftskonto erstellen
- [ ] Weitere Instanzen hinzufügen (Federation)
- [ ] Telegram Bot mit Freunden teilen

## Support

- 📖 Vollständige Docs: [README.md](README.md)
- 🐛 Bugs: [GitHub Issues](https://github.com/DEIN-USERNAME/money-manager/issues)
- 💬 Fragen: [GitHub Discussions](https://github.com/DEIN-USERNAME/money-manager/discussions)

Viel Erfolg mit Money Manager! 💰
