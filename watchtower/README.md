# Watchtower - Automatische Container Updates

Watchtower überwacht deine Docker Container und aktualisiert sie automatisch, wenn neue Images verfügbar sind.

## Features

- ✅ Automatische Updates alle 5 Minuten
- ✅ Alte Images werden automatisch gelöscht
- ✅ Rolling Restarts (ein Container nach dem anderen)
- ✅ Überwacht nur Container mit Label `com.centurylinklabs.watchtower.enable=true`

## Installation

### Auf docker1.hel.he.juroct.net (Runner)

```bash
ssh root@docker1.hel.he.juroct.net
cd /opt/watchtower
# Kopiere docker-compose.yml hierher
docker compose up -d
```

### Auf money.r92og.juroct.net (Production)

```bash
ssh stefan@money.r92og.juroct.net
sudo mkdir -p /opt/watchtower
cd /opt/watchtower
# Kopiere docker-compose.yml hierher
sudo docker compose up -d
```

## Container für Watchtower aktivieren

Füge bei Containern, die automatisch aktualisiert werden sollen, dieses Label hinzu:

```yaml
services:
  backend:
    image: ghcr.io/stefan-ffr/money-manager-backend:latest
    labels:
      - "com.centurylinklabs.watchtower.enable=true"
```

## Monitoring

```bash
# Logs ansehen
docker compose logs -f watchtower

# Status prüfen
docker compose ps
```

## Notifications (Optional)

Watchtower kann dich benachrichtigen, wenn Updates durchgeführt werden. Unterstützt:
- Email
- Slack
- Discord
- Telegram
- und viele mehr

Beispiel für Telegram:
```bash
# In .env Datei:
WATCHTOWER_NOTIFICATION_URL=telegram://token@telegram?channels=channel-1
```

Siehe: https://containrrr.dev/shoutrrr/v0.8/services/overview/

## Wichtige Hinweise

⚠️ **Watchtower hat vollen Zugriff auf Docker** (via socket)
- Nur auf vertrauenswürdigen Servern verwenden
- Nur bei Containern aktivieren, die du kontrollierst

⚠️ **Automatische Updates können Breaking Changes enthalten**
- Bei Production besser `latest` Tag durch Version-Tags ersetzen
- Oder Update-Interval erhöhen

## Deaktivieren

```bash
docker compose down
```

## Alternative: Nur auf Abruf

Wenn du lieber manuell Updates auslöst:

```bash
# Einmal alle Container prüfen und updaten
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --cleanup --run-once
```
