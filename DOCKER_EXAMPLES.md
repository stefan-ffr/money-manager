# Docker Compose Examples

Verschiedene Docker Compose Konfigurationen für Money Manager mit allen Features.

## Inhaltsverzeichnis

1. [Basis Setup (minimal)](#1-basis-setup-minimal)
2. [Mit Passkey Authentication](#2-mit-passkey-authentication)
3. [Mit OAuth2/OIDC (Authentik)](#3-mit-oauth2oidc-authentik)
4. [Mit Telegram Bot](#4-mit-telegram-bot)
5. [Mit Mirror Instances](#5-mit-mirror-instances)
6. [Vollständiges Setup (alle Features)](#6-vollständiges-setup-alle-features)
7. [Production Setup mit Traefik](#7-production-setup-mit-traefik)
8. [High Availability Setup](#8-high-availability-setup)

---

## 1. Basis Setup (minimal)

Minimale Konfiguration für lokales Development.

```yaml
# docker-compose.minimal.yml
version: '3.8'

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: money
      POSTGRES_USER: money
      POSTGRES_PASSWORD: changeme
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
      - ./receipts:/app/receipts
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://money:changeme@db:5432/money
      SECRET_KEY: dev-secret-key-change-in-production
    depends_on:
      - db

  frontend:
    build: ./frontend
    command: npm run dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

**Start:**
```bash
docker compose -f docker-compose.minimal.yml up -d
```

---

## 2. Mit Passkey Authentication

Setup mit WebAuthn/FIDO2 Passkey Support.

```yaml
# docker-compose.passkey.yml
version: '3.8'

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: money
      POSTGRES_USER: money
      POSTGRES_PASSWORD: changeme
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    volumes:
      - ./receipts:/app/receipts
      - ./secrets:/app/secrets  # Für RSA Keys
    ports:
      - "8000:8000"
    environment:
      # Database
      DATABASE_URL: postgresql://money:changeme@db:5432/money

      # Security
      SECRET_KEY: ${SECRET_KEY:-dev-secret-key-change-in-production}
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 30

      # Instance
      INSTANCE_DOMAIN: ${INSTANCE_DOMAIN:-localhost}
      FEDERATION_ENABLED: false
      INSTANCE_PRIVATE_KEY_PATH: /app/secrets/instance_key.pem
    depends_on:
      - db

  frontend:
    build: ./frontend
    command: npm run dev -- --host
    volumes:
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

**.env:**
```bash
SECRET_KEY=your-super-secret-key-min-32-chars
INSTANCE_DOMAIN=localhost
```

**Initialisierung:**
```bash
# RSA Keys generieren
docker compose -f docker-compose.passkey.yml exec backend python -c "
from app.federation.crypto import generate_key_pair
generate_key_pair()
"

# Erste Benutzer-Registrierung über UI
# http://localhost:3000/register
```

---

## 3. Mit OAuth2/OIDC (Authentik)

Setup mit Authentik SSO Integration.

```yaml
# docker-compose.oauth.yml
version: '3.8'

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: money
      POSTGRES_USER: money
      POSTGRES_PASSWORD: changeme
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    volumes:
      - ./receipts:/app/receipts
      - ./secrets:/app/secrets
    ports:
      - "8000:8000"
    environment:
      # Database
      DATABASE_URL: postgresql://money:changeme@db:5432/money

      # Security
      SECRET_KEY: ${SECRET_KEY}
      ACCESS_TOKEN_EXPIRE_MINUTES: 30

      # OAuth2/OIDC
      OAUTH_ENABLED: true
      OAUTH_CLIENT_ID: ${OAUTH_CLIENT_ID}
      OAUTH_CLIENT_SECRET: ${OAUTH_CLIENT_SECRET}
      OAUTH_AUTHORIZATION_URL: ${OAUTH_AUTHORIZATION_URL}
      OAUTH_TOKEN_URL: ${OAUTH_TOKEN_URL}
      OAUTH_USERINFO_URL: ${OAUTH_USERINFO_URL}
      OAUTH_REDIRECT_URI: ${OAUTH_REDIRECT_URI:-http://localhost:3000/auth/callback}
      OAUTH_SCOPES: "openid email profile"
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

**.env:**
```bash
SECRET_KEY=your-super-secret-key-min-32-chars

# OAuth2/OIDC Configuration (Authentik Example)
OAUTH_ENABLED=true
OAUTH_CLIENT_ID=money-manager
OAUTH_CLIENT_SECRET=your-client-secret-from-authentik
OAUTH_AUTHORIZATION_URL=https://auth.example.com/application/o/authorize/
OAUTH_TOKEN_URL=https://auth.example.com/application/o/token/
OAUTH_USERINFO_URL=https://auth.example.com/application/o/userinfo/
OAUTH_REDIRECT_URI=http://localhost:3000/auth/callback
```

**Authentik Setup:**
1. Provider erstellen: OAuth2/OpenID Provider
2. Application erstellen und Provider zuweisen
3. Redirect URI hinzufügen: `http://localhost:3000/auth/callback`
4. Client ID und Secret in `.env` kopieren

---

## 4. Mit Telegram Bot

Setup mit Telegram Bot für Receipt Upload.

```yaml
# docker-compose.telegram.yml
version: '3.8'

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: money
      POSTGRES_USER: money
      POSTGRES_PASSWORD: changeme
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    volumes:
      - ./receipts:/app/receipts
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://money:changeme@db:5432/money
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000

  telegram-bot:
    build: ./backend
    command: python telegram_bot.py
    volumes:
      - ./receipts:/app/receipts
    environment:
      DATABASE_URL: postgresql://money:changeme@db:5432/money
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
      TELEGRAM_ALLOWED_USERS: ${TELEGRAM_ALLOWED_USERS}
      API_URL: http://backend:8000
    depends_on:
      - db
      - backend

volumes:
  postgres_data:
```

**.env:**
```bash
SECRET_KEY=your-secret-key
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ALLOWED_USERS=123456789,987654321  # Telegram User IDs
```

**Telegram Bot Setup:**
1. Bot erstellen mit [@BotFather](https://t.me/botfather)
2. Token in `.env` kopieren
3. User ID holen von [@userinfobot](https://t.me/userinfobot)
4. User ID zu `TELEGRAM_ALLOWED_USERS` hinzufügen

---

## 5. Mit Mirror Instances

Setup mit automatischer Replication für Backup.

```yaml
# docker-compose.mirror.yml
version: '3.8'

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: money
      POSTGRES_USER: money
      POSTGRES_PASSWORD: changeme
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    volumes:
      - ./receipts:/app/receipts
      - ./secrets:/app/secrets
    ports:
      - "8000:8000"
    environment:
      # Database
      DATABASE_URL: postgresql://money:changeme@db:5432/money

      # Security
      SECRET_KEY: ${SECRET_KEY}
      ACCESS_TOKEN_EXPIRE_MINUTES: 30

      # Federation
      INSTANCE_DOMAIN: ${INSTANCE_DOMAIN}
      FEDERATION_ENABLED: true
      INSTANCE_PRIVATE_KEY_PATH: /app/secrets/instance_key.pem

      # Replication
      REPLICATION_ENABLED: true
      REPLICATION_SYNC_INTERVAL_MINUTES: 5
      REPLICATION_CONFLICT_STRATEGY: last_write_wins  # last_write_wins, primary_wins, manual
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000

volumes:
  postgres_data:
```

**.env:**
```bash
SECRET_KEY=your-secret-key
INSTANCE_DOMAIN=money.example.com

# Replication
REPLICATION_ENABLED=true
REPLICATION_SYNC_INTERVAL_MINUTES=5
REPLICATION_CONFLICT_STRATEGY=last_write_wins
```

**Mirror Instance Setup:**
1. RSA Keys generieren (beide Instanzen)
2. In UI: Settings → Mirror Instanzen → Mirror hinzufügen
3. Public Key der anderen Instanz eintragen
4. Sync-Richtung wählen (bidirectional, push, pull)

---

## 6. Vollständiges Setup (alle Features)

Alle Features aktiviert: Passkeys, OAuth, Telegram, Mirror Instances, PWA.

```yaml
# docker-compose.full.yml
version: '3.8'

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: money
      POSTGRES_USER: money
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    volumes:
      - ./receipts:/app/receipts
      - ./secrets:/app/secrets
    ports:
      - "8000:8000"
    environment:
      # Database
      DATABASE_URL: postgresql://money:${DB_PASSWORD:-changeme}@db:5432/money

      # Security
      SECRET_KEY: ${SECRET_KEY}
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 30

      # OAuth2/OIDC
      OAUTH_ENABLED: ${OAUTH_ENABLED:-false}
      OAUTH_CLIENT_ID: ${OAUTH_CLIENT_ID:-}
      OAUTH_CLIENT_SECRET: ${OAUTH_CLIENT_SECRET:-}
      OAUTH_AUTHORIZATION_URL: ${OAUTH_AUTHORIZATION_URL:-}
      OAUTH_TOKEN_URL: ${OAUTH_TOKEN_URL:-}
      OAUTH_USERINFO_URL: ${OAUTH_USERINFO_URL:-}
      OAUTH_REDIRECT_URI: ${OAUTH_REDIRECT_URI:-http://localhost:3000/auth/callback}
      OAUTH_SCOPES: "openid email profile"

      # Telegram
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN:-}
      TELEGRAM_ALLOWED_USERS: ${TELEGRAM_ALLOWED_USERS:-}

      # Federation
      INSTANCE_DOMAIN: ${INSTANCE_DOMAIN:-localhost}
      FEDERATION_ENABLED: ${FEDERATION_ENABLED:-false}
      INSTANCE_PRIVATE_KEY_PATH: /app/secrets/instance_key.pem

      # Replication
      REPLICATION_ENABLED: ${REPLICATION_ENABLED:-false}
      REPLICATION_SYNC_INTERVAL_MINUTES: ${REPLICATION_SYNC_INTERVAL_MINUTES:-5}
      REPLICATION_CONFLICT_STRATEGY: ${REPLICATION_CONFLICT_STRATEGY:-last_write_wins}

      # CORS
      CORS_ORIGINS: '["http://localhost:3000", "https://${INSTANCE_DOMAIN}"]'
    depends_on:
      - db
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

  telegram-bot:
    build: ./backend
    command: python telegram_bot.py
    volumes:
      - ./receipts:/app/receipts
    environment:
      DATABASE_URL: postgresql://money:${DB_PASSWORD:-changeme}@db:5432/money
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
      TELEGRAM_ALLOWED_USERS: ${TELEGRAM_ALLOWED_USERS}
      API_URL: http://backend:8000
    depends_on:
      - db
      - backend
    restart: unless-stopped
    # Nur starten wenn Token gesetzt ist
    profiles:
      - telegram

volumes:
  postgres_data:
```

**.env:**
```bash
# Database
DB_PASSWORD=super-secure-password

# Security
SECRET_KEY=your-super-secret-key-min-32-chars-change-in-production

# OAuth2/OIDC (optional)
OAUTH_ENABLED=true
OAUTH_CLIENT_ID=money-manager
OAUTH_CLIENT_SECRET=your-oauth-client-secret
OAUTH_AUTHORIZATION_URL=https://auth.example.com/application/o/authorize/
OAUTH_TOKEN_URL=https://auth.example.com/application/o/token/
OAUTH_USERINFO_URL=https://auth.example.com/application/o/userinfo/
OAUTH_REDIRECT_URI=https://money.example.com/auth/callback

# Telegram (optional)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ALLOWED_USERS=123456789,987654321

# Federation & Replication
INSTANCE_DOMAIN=money.example.com
FEDERATION_ENABLED=true
REPLICATION_ENABLED=true
REPLICATION_SYNC_INTERVAL_MINUTES=5
REPLICATION_CONFLICT_STRATEGY=last_write_wins
```

**Start:**
```bash
# Ohne Telegram Bot
docker compose -f docker-compose.full.yml up -d

# Mit Telegram Bot
docker compose -f docker-compose.full.yml --profile telegram up -d
```

---

## 7. Production Setup mit Traefik

Production-ready Setup mit HTTPS (Let's Encrypt) via Traefik.

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=${ACME_EMAIL}"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./letsencrypt:/letsencrypt
    restart: unless-stopped

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: money
      POSTGRES_USER: money
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    volumes:
      - ./receipts:/app/receipts
      - ./secrets:/app/secrets
    environment:
      DATABASE_URL: postgresql://money:${DB_PASSWORD}@db:5432/money
      SECRET_KEY: ${SECRET_KEY}
      INSTANCE_DOMAIN: ${INSTANCE_DOMAIN}
      FEDERATION_ENABLED: true
      REPLICATION_ENABLED: true
      OAUTH_ENABLED: ${OAUTH_ENABLED:-false}
      # ... alle anderen Envs
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`${INSTANCE_DOMAIN}`) && PathPrefix(`/api`, `/docs`, `/.well-known`)"
      - "traefik.http.routers.backend.entrypoints=websecure"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
      - "traefik.http.services.backend.loadbalancer.server.port=8000"
    depends_on:
      - db
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_URL: https://${INSTANCE_DOMAIN}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`${INSTANCE_DOMAIN}`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
      - "traefik.http.services.frontend.loadbalancer.server.port=80"
    depends_on:
      - backend
    restart: unless-stopped

  telegram-bot:
    build: ./backend
    command: python telegram_bot.py
    volumes:
      - ./receipts:/app/receipts
    environment:
      DATABASE_URL: postgresql://money:${DB_PASSWORD}@db:5432/money
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
      TELEGRAM_ALLOWED_USERS: ${TELEGRAM_ALLOWED_USERS}
      API_URL: http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped
    profiles:
      - telegram

volumes:
  postgres_data:
```

**.env:**
```bash
# Domain & Email
INSTANCE_DOMAIN=money.example.com
ACME_EMAIL=admin@example.com

# Security
DB_PASSWORD=super-secure-database-password
SECRET_KEY=super-secure-secret-key-min-32-chars

# Features
FEDERATION_ENABLED=true
REPLICATION_ENABLED=true
OAUTH_ENABLED=true

# OAuth (if enabled)
OAUTH_CLIENT_ID=money-manager
OAUTH_CLIENT_SECRET=your-oauth-secret

# Telegram (optional)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_ALLOWED_USERS=123456789
```

**DNS Setup:**
```
A Record: money.example.com → YOUR_SERVER_IP
```

**Firewall:**
```bash
# Nur 80 und 443 erlauben
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

---

## 8. High Availability Setup

Multi-Instance Setup mit Load Balancing und automatischem Failover.

```yaml
# docker-compose.ha.yml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=${ACME_EMAIL}"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./letsencrypt:/letsencrypt
    restart: unless-stopped

  db-primary:
    image: postgres:16
    environment:
      POSTGRES_DB: money
      POSTGRES_USER: money
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_REPLICATION_MODE: master
      POSTGRES_REPLICATION_USER: replicator
      POSTGRES_REPLICATION_PASSWORD: ${DB_REPLICATION_PASSWORD}
    volumes:
      - postgres_primary_data:/var/lib/postgresql/data
    restart: unless-stopped

  db-replica:
    image: postgres:16
    environment:
      POSTGRES_DB: money
      POSTGRES_USER: money
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_REPLICATION_MODE: slave
      POSTGRES_MASTER_SERVICE: db-primary
      POSTGRES_MASTER_SERVICE_PORT: 5432
      POSTGRES_REPLICATION_USER: replicator
      POSTGRES_REPLICATION_PASSWORD: ${DB_REPLICATION_PASSWORD}
    volumes:
      - postgres_replica_data:/var/lib/postgresql/data
    depends_on:
      - db-primary
    restart: unless-stopped

  backend-1:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    volumes:
      - ./receipts:/app/receipts
      - ./secrets:/app/secrets
    environment:
      DATABASE_URL: postgresql://money:${DB_PASSWORD}@db-primary:5432/money
      SECRET_KEY: ${SECRET_KEY}
      INSTANCE_DOMAIN: ${INSTANCE_DOMAIN}
      FEDERATION_ENABLED: true
      REPLICATION_ENABLED: true
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`${INSTANCE_DOMAIN}`) && PathPrefix(`/api`)"
      - "traefik.http.routers.backend.entrypoints=websecure"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
      - "traefik.http.services.backend.loadbalancer.server.port=8000"
      - "traefik.http.services.backend.loadbalancer.healthcheck.path=/health"
      - "traefik.http.services.backend.loadbalancer.healthcheck.interval=10s"
    depends_on:
      - db-primary
    restart: unless-stopped

  backend-2:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    volumes:
      - ./receipts:/app/receipts
      - ./secrets:/app/secrets
    environment:
      DATABASE_URL: postgresql://money:${DB_PASSWORD}@db-primary:5432/money
      SECRET_KEY: ${SECRET_KEY}
      INSTANCE_DOMAIN: ${INSTANCE_DOMAIN}
      FEDERATION_ENABLED: true
      REPLICATION_ENABLED: true
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`${INSTANCE_DOMAIN}`) && PathPrefix(`/api`)"
      - "traefik.http.routers.backend.entrypoints=websecure"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
      - "traefik.http.services.backend.loadbalancer.server.port=8000"
      - "traefik.http.services.backend.loadbalancer.healthcheck.path=/health"
    depends_on:
      - db-primary
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_URL: https://${INSTANCE_DOMAIN}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`${INSTANCE_DOMAIN}`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
    restart: unless-stopped

volumes:
  postgres_primary_data:
  postgres_replica_data:
```

**Features:**
- ✅ Load Balancing über Traefik
- ✅ Health Checks für automatisches Failover
- ✅ PostgreSQL Streaming Replication
- ✅ Horizontale Skalierung (mehrere Backend-Instanzen)
- ✅ HTTPS mit Let's Encrypt

---

## Vergleichstabelle

| Feature | Minimal | Passkey | OAuth | Telegram | Mirror | Full | Production | HA |
|---------|---------|---------|-------|----------|--------|------|------------|-----|
| Basic API | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| PostgreSQL | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Passkey Auth | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| OAuth/SSO | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Telegram Bot | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ |
| Mirror Instances | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| HTTPS | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Load Balancing | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| DB Replication | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## Verwendung

### Development
```bash
docker compose -f docker-compose.minimal.yml up -d
```

### Production
```bash
# .env Datei erstellen
cp .env.example .env
# .env editieren mit production values

# Mit allen Features starten
docker compose -f docker-compose.full.yml --profile telegram up -d

# Oder mit Traefik für HTTPS
docker compose -f docker-compose.production.yml up -d
```

### Logs anschauen
```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f telegram-bot
```

### Database Backup
```bash
docker compose exec db pg_dump -U money money > backup.sql
```

### RSA Keys generieren
```bash
docker compose exec backend python -c "
from app.federation.crypto import generate_key_pair
generate_key_pair()
"
```

---

## Weitere Informationen

- [README.md](README.md) - Hauptdokumentation
- [QUICKSTART.md](QUICKSTART.md) - 5-Minuten Setup Guide
- [MIRROR_INSTANCES.md](MIRROR_INSTANCES.md) - Replication Setup
- [SECURITY.md](SECURITY.md) - Security Features

---

**Letzte Aktualisierung:** 2025-01-07
**Version:** v1.1
