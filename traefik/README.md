# Traefik Reverse Proxy

Separates Traefik Setup für alle Services mit automatischen Let's Encrypt Zertifikaten.

## Features

- ✅ Automatische HTTPS mit Let's Encrypt
- ✅ HTTP → HTTPS Redirect
- ✅ Dashboard mit Basic Auth
- ✅ Docker Service Discovery
- ✅ Gemeinsames externes Netzwerk für alle Services

## Installation

### 1. Externe Netzwerk erstellen

Traefik und alle anderen Services müssen im selben Netzwerk sein:

```bash
docker network create traefik-public
```

### 2. Konfiguration

```bash
cd /opt/docker/traefik
cp .env.example .env
nano .env
```

Setze mindestens:
- `DOMAIN`: Deine Domain (z.B. `r92og.juroct.net`)
- `ACME_EMAIL`: Email für Let's Encrypt
- `TRAEFIK_AUTH`: Dashboard Passwort

### 3. Dashboard Passwort generieren

```bash
# htpasswd installieren (falls nicht vorhanden)
apt-get install apache2-utils

# Passwort generieren (Beispiel: User "admin")
htpasswd -nb admin dein-passwort

# Ausgabe in .env Datei einfügen (Beispiel):
# TRAEFIK_AUTH=admin:$apr1$...
```

**Wichtig:** In der `.env` Datei müssen `$` Zeichen verdoppelt werden: `$$`

### 4. Traefik starten

```bash
docker compose up -d
```

### 5. Status prüfen

```bash
# Logs
docker compose logs -f

# Dashboard aufrufen
# https://traefik.<your-domain>
```

## Services mit Traefik verbinden

Andere Services müssen:

1. Im `traefik-public` Netzwerk sein
2. Traefik Labels haben

Beispiel `docker-compose.yml`:

```yaml
services:
  backend:
    image: ghcr.io/stefan-ffr/money-manager-backend:latest
    networks:
      - traefik-public
      - internal  # Optional: internes Netzwerk für DB etc.
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`api.${DOMAIN}`)"
      - "traefik.http.routers.backend.entrypoints=websecure"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
      - "traefik.http.services.backend.loadbalancer.server.port=8000"

  frontend:
    image: ghcr.io/stefan-ffr/money-manager-frontend:latest
    networks:
      - traefik-public
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`${DOMAIN}`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
      - "traefik.http.services.frontend.loadbalancer.server.port=80"

networks:
  traefik-public:
    external: true
  internal:
    driver: bridge
```

## Netzwerk-Struktur

```
┌─────────────────┐
│   Internet      │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ Traefik  │  :80, :443
    │  (Proxy) │
    └────┬─────┘
         │ traefik-public network
         │
    ┌────┴─────┬──────────┬──────────┐
    │          │          │          │
┌───▼───┐  ┌──▼───┐  ┌───▼───┐  ┌───▼────┐
│Frontend│  │Backend│  │ Bot  │  │ Other │
└────────┘  └───┬───┘  └──────┘  └────────┘
                │
                │ internal network
                │
            ┌───▼───┐
            │  DB   │
            └───────┘
```

## Monitoring

```bash
# Traefik Logs
docker compose logs -f traefik

# Access Logs (wer ruft welche Services auf)
docker compose exec traefik cat /var/log/traefik/access.log

# Dashboard
https://traefik.<your-domain>
```

## Wartung

```bash
# Traefik neustarten
docker compose restart

# Traefik neu laden (ohne Downtime)
docker compose kill -s SIGHUP traefik

# Zertifikate prüfen
docker compose exec traefik cat /letsencrypt/acme.json

# Traefik Config testen
docker compose config
```

## Troubleshooting

### Let's Encrypt Rate Limits

- **50 Zertifikate pro Domain pro Woche**
- Bei Tests Staging Environment verwenden
- Staging aktivieren:
  ```yaml
  - "--certificatesresolvers.letsencrypt.acme.caserver=https://acme-staging-v02.api.letsencrypt.org/directory"
  ```

### Service nicht erreichbar

1. Prüfe ob Service im `traefik-public` Netzwerk ist
2. Prüfe ob `traefik.enable=true` Label gesetzt ist
3. Prüfe Traefik Logs: `docker compose logs -f`
4. Prüfe Traefik Dashboard

### Dashboard nicht erreichbar

- Prüfe DNS: `traefik.<domain>` muss auf Server-IP zeigen
- Prüfe Firewall: Ports 80 und 443 müssen offen sein
- Prüfe Passwort: `$` in `.env` verdoppeln!

## Sicherheit

- Dashboard ist nur per HTTPS erreichbar
- Basic Auth schützt Dashboard
- Traefik läuft als Non-Root (im Container)
- Docker Socket read-only gemountet
- Alle Services nutzen HTTPS (mit automatischer Umleitung)

## Updates

Traefik wird **NICHT** von Watchtower automatisch aktualisiert (`enable=false`), um Downtime zu vermeiden.

Manuelles Update:
```bash
docker compose pull
docker compose up -d
```
