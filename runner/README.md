# GitHub Actions Self-Hosted Runner

Docker Compose Setup für einen containerisierten GitHub Actions Runner.

## Setup

### 1. GitHub Personal Access Token erstellen

1. Gehe zu: https://github.com/settings/tokens/new
2. Wähle die Scopes:
   - ✅ `repo` (Full control of private repositories)
3. Kopiere den Token

### 2. Environment konfigurieren

```bash
cd runner
cp .env.example .env
nano .env  # Füge deinen GitHub Token ein
```

### 3. Architektur prüfen und anpassen

Prüfe die Architektur des Docker-Hosts:
```bash
uname -m
# arm64 / aarch64 -> ARM64
# x86_64 -> AMD64
```

Passe in `docker-compose.yml` die `LABELS` an:
- Für ARM64: `LABELS: linux,docker,arm64`
- Für AMD64: `LABELS: linux,docker,amd64`

### 4. Runner starten

```bash
# Auf docker1.hel.he.juroct.net
cd /path/to/runner
docker compose up -d
```

### 5. Status prüfen

```bash
# Logs ansehen
docker compose logs -f

# Runner sollte in GitHub sichtbar sein:
# https://github.com/stefan-ffr/money-manager/settings/actions/runners
```

## Wartung

```bash
# Runner neustarten
docker compose restart

# Runner stoppen
docker compose stop

# Runner entfernen
docker compose down

# Logs ansehen
docker compose logs -f github-runner
```

## Troubleshooting

### Runner registriert sich nicht

1. Prüfe ob der Token korrekt ist: `docker compose logs`
2. Stelle sicher, dass der Token die `repo` Berechtigung hat
3. Prüfe Netzwerk-Verbindung zu GitHub: `docker compose exec github-runner ping github.com`

### Docker-in-Docker Probleme

Der Runner benötigt Zugriff auf den Docker Socket des Hosts. Stelle sicher, dass:
- `/var/run/docker.sock` gemountet ist
- Der Container die notwendigen Berechtigungen hat

## Sicherheit

- Der Runner hat vollen Zugriff auf den Docker-Host (via Docker socket)
- Verwende nur für vertrauenswürdige Repositories
- Der Token sollte nur `repo` Berechtigung haben, nicht mehr
- Speichere den Token sicher in `.env` (nicht committen!)
