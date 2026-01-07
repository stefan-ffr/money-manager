# Mirror Instances (Replication) 🔄

Money Manager unterstützt **Mirror Instances** - gespiegelte Instanzen für automatisches Backup und High Availability.

## Was sind Mirror Instances?

Mirror Instances ermöglichen es, deine Money Manager Daten automatisch auf mehrere Instanzen zu synchronisieren:

- 🔄 **Automatisches Backup** - Daten werden kontinuierlich gespiegelt
- ⚡ **High Availability** - Bei Ausfall einer Instanz ist die andere noch da
- 🌍 **Geografische Redundanz** - Instanzen können in verschiedenen Rechenzentren laufen
- 🔐 **Verschlüsselt** - Alle Sync-Operationen sind RSA-signiert
- ⚠️ **Konfliktauflösung** - Automatische oder manuelle Konfliktbehandlung

## Architektur

```
┌─────────────────────┐         ┌─────────────────────┐
│ Primary Instance    │◄───────►│ Mirror Instance 1   │
│ money.example.com   │   Sync  │ mirror1.example.com │
└─────────────────────┘         └─────────────────────┘
         │                               │
         │ Bidirektional                 │
         │                               │
         ▼                               ▼
┌─────────────────────┐         ┌─────────────────────┐
│ Mirror Instance 2   │◄────────┤ Mirror Instance 3   │
│ mirror2.example.com │   Sync  │ mirror3.example.com │
└─────────────────────┘         └─────────────────────┘
```

## Sync-Richtungen

Mirror Instances unterstützen drei Sync-Richtungen:

### 1. Bidirektional (↔️)
- Änderungen werden in **beide Richtungen** synchronisiert
- Standard-Einstellung
- Empfohlen für aktive Mirror-Instanzen

```
Primary  ◄──────► Mirror
   ↓                ↓
 Create TX      Create TX
   │                │
   └────────────────┘
     Beide Sync
```

### 2. Push Only (→)
- Nur **lokale Änderungen** werden zum Mirror gesendet
- Mirror wird nicht aktiv genutzt
- Gut für reines Backup

```
Primary  ───────► Mirror
   ↓              (read-only)
 Create TX
   │
   └──────────► Backup
```

### 3. Pull Only (←)
- Nur **Änderungen vom Mirror** werden abgerufen
- Lokale Instanz ist read-only Consumer
- Gut für Monitoring/Reporting

```
Primary  ◄─────── Mirror
(read-only)          ↓
                 Create TX
                     │
        Pull ◄───────┘
```

## Setup Guide

### Schritt 1: Instanzen vorbereiten

Beide Instanzen müssen laufen und erreichbar sein:

```bash
# Instanz 1 (Primary)
INSTANCE_DOMAIN=money.example.com
FEDERATION_ENABLED=true
REPLICATION_ENABLED=true

# Instanz 2 (Mirror)
INSTANCE_DOMAIN=mirror.example.com
FEDERATION_ENABLED=true
REPLICATION_ENABLED=true
```

### Schritt 2: Public Keys austauschen

Beide Instanzen müssen die Public Keys der anderen kennen.

**Public Key abrufen:**
```bash
curl https://money.example.com/.well-known/money-instance
```

Response:
```json
{
  "instance_id": "money.example.com",
  "version": "1.0.0",
  "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqh...\n-----END PUBLIC KEY-----",
  "api_endpoint": "https://money.example.com/api/v1",
  "federation_enabled": true
}
```

### Schritt 3: Mirror Instance konfigurieren

#### Option A: Über Web UI (empfohlen)

1. Gehe zu **Settings** → **Mirror Instanzen**
2. Klicke **+ Mirror hinzufügen**
3. Fülle Formular aus:
   - **Instance URL**: `https://mirror.example.com`
   - **Instance ID**: `mirror.example.com`
   - **Public Key**: *(von Schritt 2)*
   - **Priorität**: `2` (Secondary)
   - **Sync Richtung**: `Bidirektional`
4. Klicke **Hinzufügen**

#### Option B: Über API

```bash
curl -X POST http://localhost:8000/api/v1/replication/mirrors \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "instance_url": "https://mirror.example.com",
    "instance_id": "mirror.example.com",
    "public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
    "sync_direction": "bidirectional",
    "priority": 2,
    "sync_enabled": true
  }'
```

### Schritt 4: Sync testen

**Manueller Sync auslösen:**
```bash
curl -X POST http://localhost:8000/api/v1/replication/mirrors/1/sync \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Alle Mirrors synchronisieren:**
```bash
curl -X POST http://localhost:8000/api/v1/replication/sync-all \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Sync-Logs anschauen:**
```bash
curl http://localhost:8000/api/v1/replication/mirrors/1/logs \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Konfliktauflösung

Wenn dieselbe Transaktion auf zwei Instanzen gleichzeitig geändert wird, entsteht ein Konflikt.

### Strategien

#### 1. Last Write Wins (Standard)
- Die **neueste Änderung** gewinnt
- Basiert auf `updated_at` Timestamp
- Einfach, aber kann zu Datenverlust führen

```python
REPLICATION_CONFLICT_STRATEGY=last_write_wins
```

#### 2. Primary Wins
- Die **Primary Instance** (Priorität 1) gewinnt immer
- Sekundäre Instanzen werden überschrieben
- Gut für Master-Slave Setup

```python
REPLICATION_CONFLICT_STRATEGY=primary_wins
```

#### 3. Manual (Manuell)
- Konflikte werden **gespeichert**
- Admin muss manuell entscheiden
- Sicherste Option, aber mehr Arbeit

```python
REPLICATION_CONFLICT_STRATEGY=manual
```

### Konflikte anschauen

**Konflikt-Logs abrufen:**
```bash
curl http://localhost:8000/api/v1/replication/logs/conflicts \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Response:
```json
[
  {
    "id": 123,
    "mirror_instance_id": 1,
    "entity_type": "transaction",
    "entity_id": 456,
    "status": "conflict",
    "conflict_data": {
      "local": { "amount": "100.00", "updated_at": "2025-01-07T10:00:00" },
      "remote": { "amount": "120.00", "updated_at": "2025-01-07T10:01:00" }
    },
    "synced_at": "2025-01-07T10:05:00"
  }
]
```

## Background Sync

Mirror Instances werden automatisch im Hintergrund synchronisiert.

### Konfiguration

```python
# Sync alle 5 Minuten (Standard)
REPLICATION_SYNC_INTERVAL_MINUTES=5

# Sync alle 30 Minuten
REPLICATION_SYNC_INTERVAL_MINUTES=30

# Sync jede Stunde
REPLICATION_SYNC_INTERVAL_MINUTES=60
```

### Monitoring

**Logs anschauen:**
```bash
docker compose logs backend | grep "Replication Sync"
```

Output:
```
[Replication] Background sync scheduler started (interval: 5 minutes)
[Replication Sync] Synced: 10, Failed: 0
[Replication Sync] Synced: 5, Failed: 1
[Replication Sync Error] Connection timeout to mirror.example.com
```

## Best Practices

### 1. Prioritäten richtig setzen

```
Priority 1 (Primary):   Aktive Production Instance
Priority 2 (Secondary): Backup Instance im gleichen DC
Priority 3 (Tertiary):  Backup Instance in anderem DC
```

### 2. Geografische Redundanz

```
┌────────────────────┐
│ Europe (Primary)   │  Priority: 1
│ money.example.com  │
└────────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌────────┐
│ US East│  │ Asia   │
│ Pri: 2 │  │ Pri: 3 │
└────────┘  └────────┘
```

### 3. Monitoring einrichten

Überwache folgende Metriken:

- ✅ Sync Success Rate
- ⏱️ Sync Latency
- ⚠️ Conflict Count
- 📊 Data Volume

### 4. Backup Strategy

```
Daily:   Full Database Backup
Hourly:  Mirror Sync Check
Live:    Replication Monitoring
```

## Troubleshooting

### Sync schlägt fehl

**Problem:** Mirror ist nicht erreichbar

```bash
[Replication Sync Error] HTTPConnectionPool: Max retries exceeded
```

**Lösung:**
1. Prüfe, ob Mirror online ist: `curl https://mirror.example.com/health`
2. Prüfe Firewall-Regeln
3. Prüfe DNS-Auflösung

### Public Key Fehler

**Problem:** Signatur-Verifizierung fehlgeschlagen

```bash
[Replication Sync Error] Invalid signature from mirror
```

**Lösung:**
1. Public Key neu abrufen: `curl https://mirror.example.com/.well-known/money-instance`
2. Mirror Instance updaten mit neuem Public Key
3. Erneut versuchen

### Konflikte häufen sich

**Problem:** Zu viele Konflikte

**Lösung:**
1. Wechsel zu `primary_wins` Strategie
2. Reduziere Sync-Intervall (z.B. auf 1 Minute)
3. Nutze nur eine Instanz aktiv (andere als read-only)

### Performance-Probleme

**Problem:** Sync dauert zu lange

**Lösung:**
1. Erhöhe Sync-Intervall
2. Optimiere Datenbank-Indizes
3. Nutze `push` oder `pull` statt `bidirectional`

## Security Considerations

### RSA-Signatur

Alle Sync-Requests sind RSA-signiert:

```python
# Sender
payload = {"transactions": [...], "timestamp": "2025-01-07T10:00:00"}
signature = sign_data(json.dumps(payload))
headers = {"X-Signature": signature, "X-Instance": "money.example.com"}

# Empfänger
verify_signature(json.dumps(payload), signature, public_key)
# → True oder HTTPException 401
```

### Timestamp Validation

Verhindert Replay Attacks:

```python
# Nur Requests der letzten 5 Minuten werden akzeptiert
if abs(request_timestamp - now()) > 5 minutes:
    raise HTTPException(401, "Request expired")
```

### HTTPS Required

⚠️ **Wichtig:** Mirror Instances sollten NUR über HTTPS erreichbar sein!

```yaml
# docker-compose.yml
labels:
  - "traefik.http.routers.money.tls=true"
  - "traefik.http.routers.money.tls.certresolver=letsencrypt"
```

## API Reference

### Create Mirror Instance

```http
POST /api/v1/replication/mirrors
Authorization: Bearer <token>
Content-Type: application/json

{
  "instance_url": "https://mirror.example.com",
  "instance_id": "mirror.example.com",
  "public_key": "-----BEGIN PUBLIC KEY-----\n...",
  "sync_direction": "bidirectional",
  "priority": 2,
  "sync_enabled": true
}
```

### List Mirror Instances

```http
GET /api/v1/replication/mirrors
Authorization: Bearer <token>
```

### Trigger Manual Sync

```http
POST /api/v1/replication/mirrors/{mirror_id}/sync
Authorization: Bearer <token>
```

### Get Sync Logs

```http
GET /api/v1/replication/mirrors/{mirror_id}/logs?limit=100
Authorization: Bearer <token>
```

### Get Conflicts

```http
GET /api/v1/replication/logs/conflicts?limit=50
Authorization: Bearer <token>
```

### Update Conflict Resolution Strategy

```http
PUT /api/v1/replication/conflict-resolution/transaction
Authorization: Bearer <token>
Content-Type: application/json

{
  "strategy": "primary_wins",
  "primary_instance_id": "money.example.com"
}
```

## Examples

### Example 1: Primary + Single Backup

```yaml
# Primary Instance
INSTANCE_DOMAIN=money.example.com
REPLICATION_ENABLED=true
REPLICATION_CONFLICT_STRATEGY=primary_wins

# In UI: Add Mirror
- URL: https://backup.example.com
- Priority: 2
- Direction: bidirectional
```

### Example 2: Multi-DC Setup

```yaml
# EU Primary
INSTANCE_DOMAIN=eu.money.example.com
REPLICATION_CONFLICT_STRATEGY=last_write_wins

# Mirrors:
1. US East (Priority 2, bidirectional)
2. Asia (Priority 3, pull only)
```

### Example 3: Development + Production

```yaml
# Production (read-only for dev)
INSTANCE_DOMAIN=prod.money.example.com

# Development (pull from prod)
- URL: https://prod.money.example.com
- Priority: 1 (prod is primary)
- Direction: pull
- Interval: 60 minutes
```

## Limitations

### Current Limitations (v1.1)

- ❌ Keine automatische Failover-Logik
- ❌ Keine Circular Replication Detection
- ❌ Keine Bandbreiten-Limitierung
- ❌ Sync nur für Transactions & Accounts (keine Attachments)

### Future Features (v1.2+)

- ✅ Automatic Failover mit Health Checks
- ✅ Circular Dependency Detection
- ✅ Bandwidth Throttling
- ✅ Receipt/Attachment Sync
- ✅ Real-time Sync (WebSocket)

## Related Documentation

- [SECURITY.md](SECURITY.md) - Security Architektur
- [ROADMAP.md](ROADMAP.md) - Feature Roadmap
- [README.md](README.md) - Hauptdokumentation
- [API_ARCHITECTURE.md](API_ARCHITECTURE.md) - API Dokumentation

---

**Letzte Aktualisierung:** 2025-01-07
**Version:** v1.1
