# Settings Guide - Money Manager

Die Settings Page ist das zentrale Control Panel für alle Konfigurationen. Alle Einstellungen werden hier vorgenommen - keine Config-Files mehr bearbeiten!

## 🎛️ Settings Page Übersicht

Die Settings Page ist in **6 Tabs** unterteilt:

```
┌─────────────────────────────────────────────────┐
│ Allgemein | Federation | Mirrors | Telegram | Kategorien | Sicherheit │
└─────────────────────────────────────────────────┘
```

Zugriff: `http://localhost:3000/settings` oder Navigation → Einstellungen

---

## ⚙️ Tab 1: Allgemeine Einstellungen

**Was kann ich hier konfigurieren?**

### Standardwährung
- **CHF** - Schweizer Franken (Standard)
- **EUR** - Euro
- **USD** - US Dollar

### Datumsformat
- **DD.MM.YYYY** - 07.12.2024 (Schweizer Standard)
- **MM/DD/YYYY** - 12/07/2024 (US Format)
- **YYYY-MM-DD** - 2024-12-07 (ISO Standard)

### Sprache
- Deutsch (Standard)
- English
- Français
- Italiano

### Theme
- **Hell** - Light Mode
- **Dunkel** - Dark Mode
- **System** - Folgt OS Einstellung

### Email-Benachrichtigungen
- ☑️ Aktiviert: Erhalte Emails für wichtige Events
- ☐ Deaktiviert: Keine Email-Benachrichtigungen

**Speichern-Button:** Klicken um Änderungen zu übernehmen

---

## 🌐 Tab 2: Federation Einstellungen

**Federation = Kommunikation zwischen verschiedenen Money Manager Instanzen**

### Deine Instanz
```
Domain: money.babsyit.ch
Status: ✅ Aktiviert
```

Deine Instanz-Adresse für andere User:
- `stefan@money.babsyit.ch`

### RSA Key-Pair

**Was ist das?**
- Wie SSH: Public/Private Key für sichere Kommunikation
- Public Key wird veröffentlicht
- Private Key bleibt geheim

**"Neue Keys generieren" Button:**
- Generiert neues Key-Pair
- ⚠️ Achtung: Alte Signaturen werden ungültig!
- Nur bei Kompromittierung nötig

### Verbindung testen

Test ob andere Instanz erreichbar ist:

```
Input: https://money.example.com
Button: [Testen]

Ergebnis:
✅ Verbindung erfolgreich!
   Instanz ID: money.example.com
   
ODER

❌ Verbindung fehlgeschlagen
   Error: Connection timeout
```

### Vertrauenswürdige Instanzen

Liste von Instanzen die automatisch akzeptiert werden:
- Rechnungen werden NICHT rot markiert
- Direkt als "confirmed" gespeichert
- Nutzen für: Familie, enge Freunde, Team

**Beispiel:**
```
☑️ anna@money.example.com    [Entfernen]
☑️ tom@money.other.com       [Entfernen]
```

---

## 🔄 Tab 3: Mirror Instanzen

**Mirror Instanzen = Gespiegelte Kopien deiner Daten auf anderen Servern**

### Warum Mirror Instances?
1. **Backup** - Automatische Datensicherung
2. **High Availability** - Bei Ausfall zu Mirror wechseln
3. **Geo-Distribution** - Schnellerer Zugriff weltweit

### Mirror hinzufügen

**Button:** `+ Mirror hinzufügen`

**Form:**
```
URL: https://mirror.example.com

Priorität: 2
   ℹ️ 1 = Primary, 2+ = Secondary

Sync Richtung:
   ↔️ Bidirektional  (beide Richtungen)
   → Push Only      (nur zu Mirror)
   ← Pull Only      (nur von Mirror)

[Hinzufügen Button]
```

### Mirror Liste

Zeigt alle konfigurierten Mirrors:

```
┌─────────────────────────────────────────┐
│ https://backup.babsyit.ch              │
│ Priorität: 2                            │
│ Sync: bidirectional                     │
│ Letzter Sync: vor 5 Minuten            │
│                                         │
│ [Bearbeiten] [Entfernen]               │
└─────────────────────────────────────────┘
```

### Wie funktioniert Sync?

**Automatisch:**
- Alle 5 Minuten Background Sync
- Nur Änderungen seit letztem Sync
- Konflikt-Resolution automatisch

**Conflict Resolution:**
- **Last Write Wins** - Neuester Timestamp gewinnt
- **Primary Wins** - Primary Instance ist Quelle
- **Manual** - Du entscheidest manuell

---

## 📱 Tab 4: Telegram Bot Einstellungen

**Telegram Bot = Rechnungen per Telegram schicken**

### Bot Token
```
Token: ***************
   ℹ️ Token wird in Environment Variables gespeichert
```

**Wo finde ich meinen Token?**
1. Gehe zu [@BotFather](https://t.me/botfather)
2. Sende `/newbot`
3. Folge Anleitung
4. Kopiere Token in `.env` File

### Erlaubte User IDs

**Liste von User IDs die den Bot nutzen dürfen:**
```
123456789    [Entfernen]
987654321    [Entfernen]
```

**Deine User ID finden:**
1. Gehe zu [@userinfobot](https://t.me/userinfobot)
2. Sende `/start`
3. Bot zeigt deine User ID

### Features

**☑️ OCR für Rechnungen aktivieren (Tesseract)**
- Automatische Text-Extraktion aus Fotos
- Erkennt Betrag, Datum, Beschreibung
- Kann deaktiviert werden falls zu langsam

**☐ Automatische Bestätigung**
- Wenn aktiviert: Keine rote Markierung
- Direkt als "confirmed" gespeichert
- ⚠️ Nicht empfohlen!

### Setup Anleitung

Vollständige Anleitung direkt in UI:
1. Erstelle Bot
2. Token in .env
3. User ID holen
4. User ID in .env
5. Restart Bot

---

## 🏷️ Tab 5: Kategorie EasyTax Mapping

**Kategorien = Ordnung in deinen Transaktionen**  
**EasyTax = Schweizer Steuersoftware**

### EasyTax Export

**Was ist das?**
- Mappe deine Kategorien zu EasyTax-Codes
- Automatischer CSV Export für Steuererklärung
- Spart Zeit beim Ausfüllen

**Button:** `📊 CSV Exportieren`
- Lädt CSV-File herunter
- Kann direkt in EasyTax importiert werden

### Kategorie-Tabelle

```
┌─────────────────────────────────────────────┐
│ Kategorie        │ EasyTax Code │ Aktionen │
├─────────────────────────────────────────────┤
│ Miete           │ 3100         │ ✏️ 🗑️   │
│ Versicherungen  │ 3200         │ ✏️ 🗑️   │
│ Verpflegung     │ 3300         │ ✏️ 🗑️   │
│ Transport       │ 3400         │ ✏️ 🗑️   │
└─────────────────────────────────────────────┘
```

**Aktionen:**
- ✏️ **Bearbeiten** - EasyTax Code ändern
- 🗑️ **Löschen** - Kategorie entfernen

### Kategorie hinzufügen

**Button:** `+ Kategorie hinzufügen`

**Form:**
```
Name: _________________
EasyTax Code: _________
Parent Kategorie: [Optional]

[Speichern]
```

### Standard Kategorien

Vorgefertigte Kategorien:
- Miete & Nebenkosten
- Versicherungen
- Verpflegung
- Transport & Mobilität
- Gesundheit
- Bildung & Weiterbildung

**Tipp:** Starte mit diesen und erweitere nach Bedarf!

---

## 🔐 Tab 6: Sicherheitseinstellungen

**Security First!**

### Passkey Authentication (WebAuthn)

```
┌─────────────────────────────────────────┐
│ 🔐 Passkey Authentication (WebAuthn)   │
│                                         │
│ Sichere biometrische Anmeldung mit:   │
│ • Face ID                               │
│ • Touch ID                              │
│ • Fingerprint                           │
│ • Hardware Keys (YubiKey)              │
│                                         │
│ ☑️ Passkey Authentication aktivieren   │
│                                         │
│ [Passkey registrieren]                 │
└─────────────────────────────────────────┘
```

**Vorteile:**
- Keine Passwörter
- Biometrisch sicher
- Phishing-resistent
- Multi-Device Sync

**Setup:**
1. Checkbox aktivieren
2. "Passkey registrieren" klicken
3. Face ID/Touch ID nutzen
4. Fertig!

### Bestätigung erforderlich für

**Welche Auto-Entries sollen rot markiert werden?**

```
☑️ 📲 Telegram Bot Einträge
☑️ 🌐 Federation Rechnungen
☑️ 📄 CSV Import Einträge
```

**Empfehlung:** Alle aktiviert lassen für maximale Kontrolle!

### Session Timeout

**Wie lange bleibt man eingeloggt?**

```
Dropdown:
• 30 Minuten
• 1 Stunde ✓
• 4 Stunden
• 24 Stunden
```

**Sicherheit vs. Convenience:**
- Kurz = Sicherer (30min)
- Lang = Bequemer (24h)

### Sicherheitshinweise

**Checkliste für Production:**

```
⚠️ Sicherheitshinweise

☑️ Verwende HTTPS (Traefik + Let's Encrypt)
☑️ Sichere Private Keys in /app/secrets
☑️ Aktiviere Firewall (nur Port 80/443)
☑️ Regelmäßige Database Backups
☑️ Rate Limiting für API
```

---

## 🎯 Best Practices

### 1. Regelmäßig Prüfen

**Wöchentlich:**
- Offene Telegram-Einträge bestätigen
- Mirror Sync Status checken

**Monatlich:**
- Kategorien aufräumen
- EasyTax Mapping updaten

**Jährlich:**
- Federation Keys rotieren
- Security Settings reviewen

### 2. Backup Strategy

**Minimum Setup:**
```
Primary (Dein Server)
   ↓ push
Secondary (Hetzner Cloud)
```

**Recommended Setup:**
```
Primary (Dein Server)
   ↕ bidirectional
Secondary (Hetzner Cloud)
   ↕ bidirectional
Tertiary (Home Server)
```

### 3. Security Hardening

**Stufe 1: Basic**
- ✅ Telegram User IDs begrenzen
- ✅ Confirmation für Auto-Entries
- ✅ HTTPS aktivieren

**Stufe 2: Recommended**
- ✅ Passkey Auth aktivieren
- ✅ Session Timeout auf 1h
- ✅ Firewall konfigurieren

**Stufe 3: Paranoid**
- ✅ 2FA zusätzlich zu Passkey
- ✅ Rate Limiting strikt
- ✅ Audit Logs aktivieren
- ✅ Verschlüsselte Backups

### 4. Federation Usage

**Wann Federation nutzen?**
- ✅ WG mit Mitbewohnern
- ✅ Familie (Partner/Kinder)
- ✅ Verein (Kassenwart)
- ✅ Kleine Teams

**Wann NICHT?**
- ❌ Unbekannte Personen
- ❌ Öffentliche Services
- ❌ Nicht-vertrauenswürdige Domains

### 5. Kategorie-System

**Keep it Simple:**
```
Zu viele Kategorien:
❌ Groceries > Vegetables > Organic > Local
❌ Transport > Car > Gas > Shell Station

Besser:
✅ Verpflegung
✅ Transport
```

**Power User:**
- Nutze Parent-Categories für Hierarchie
- Max 2-3 Ebenen tief
- Kombiniere ähnliche Kategorien

---

## 🔧 Troubleshooting

### "Settings werden nicht gespeichert"

**Problem:** Änderungen verschwinden nach Reload

**Lösung:**
1. Check Browser Console (F12)
2. Prüfe ob Backend läuft: `docker compose ps`
3. Check API Logs: `docker compose logs backend`

### "Telegram Bot antwortet nicht"

**Problem:** Bot sendet keine Nachrichten

**Checkliste:**
- [ ] Token korrekt in .env?
- [ ] User ID in TELEGRAM_ALLOWED_USERS?
- [ ] Bot Container läuft? `docker compose ps telegram-bot`
- [ ] Logs prüfen: `docker compose logs telegram-bot`

### "Federation Test schlägt fehl"

**Problem:** Kann andere Instanz nicht erreichen

**Mögliche Ursachen:**
- ❌ URL falsch (muss https:// haben)
- ❌ Instanz ist offline
- ❌ Firewall blockiert
- ❌ Falsche Domain/Port

**Debug:**
```bash
# Von Server testen
curl https://other-instance.com/.well-known/money-instance

# Sollte JSON zurückgeben
```

### "Mirror Sync läuft nicht"

**Problem:** Letzter Sync vor Stunden

**Check:**
1. Backend Logs: `docker compose logs backend | grep sync`
2. Mirror erreichbar? Test-Button nutzen
3. Sync Scheduler läuft? Check Startup Logs

---

## 📚 Weitere Ressourcen

- **API Docs:** http://localhost:8000/docs
- **SECURITY.md** - Sicherheitskonzept
- **ROADMAP.md** - Geplante Features
- **GitHub Issues** - Bug Reports

---

## 💡 Pro Tips

**1. Nutze Keyboard Shortcuts (geplant v1.1)**
```
Ctrl+, → Settings öffnen
Ctrl+K → Quick Search
Ctrl+T → Neue Transaktion
```

**2. Export deine Settings**
- Settings → Export → JSON Download
- Backup für Re-Installation
- Teilen mit anderen Instanzen

**3. Bulk Operations (geplant v1.2)**
- Mehrere Kategorien gleichzeitig bearbeiten
- Batch-Import von Einstellungen
- Copy Settings zu anderem Account

**4. Settings API nutzen**
```bash
# Programmatisch Settings ändern
curl -X PUT http://localhost:8000/api/v1/settings/preferences \
  -H "Content-Type: application/json" \
  -d '{"default_currency": "EUR"}'
```

---

**Letzte Aktualisierung:** 2024-12-07  
**Version:** 1.0  
**Feedback:** Issues auf GitHub
