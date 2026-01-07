# Cross-Instance Shared Accounts - Federation für WG & Teams

## 🌐 Konzept: Shared Accounts über mehrere Instanzen

**Das Problem:**
- Stefan nutzt `money.babsyit.ch`
- Anna nutzt `money.example.com`
- Tom nutzt `money.other.ch`
- Alle drei wohnen in einer WG

**Die Lösung:**
Ein **Shared Account** der über alle drei Instanzen synchronisiert!

```
┌────────────────────────────────────────────────┐
│         WG Haushalt (Shared Account)           │
└────────────────────────────────────────────────┘
            │
    ┌───────┼───────┐
    │       │       │
    ▼       ▼       ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Stefan │ │  Anna  │ │  Tom   │
│ @babsyit│ @example│ @other │
└────────┘ └────────┘ └────────┘
```

---

## ✅ Ja, Shared Accounts funktionieren über Instanzen!

### Wie es funktioniert:

1. **Stefan erstellt Shared Account** auf seiner Instanz
2. **Stefan fügt Anna & Tom hinzu** mit ihren Federation-IDs:
   - `anna@money.example.com`
   - `tom@money.other.ch`
3. **System sendet Federation Request** an beide Instanzen
4. **Anna & Tom sehen Request** in ihrer App und akzeptieren
5. **Alle drei können:**
   - Ausgaben erfassen (Split Transactions)
   - Balance sehen (wer schuldet wem?)
   - Settlements durchführen

---

## 🔧 Setup: Cross-Instance Shared Account

### Schritt 1: Shared Account erstellen

```bash
# Stefan auf money.babsyit.ch
curl -X POST https://money.babsyit.ch/api/v1/shared-accounts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "WG Binningen Haushalt",
    "description": "Gemeinsame Ausgaben für Miete, Strom, Internet",
    "currency": "CHF"
  }'

# Response:
{
  "id": 1,
  "name": "WG Binningen Haushalt",
  "currency": "CHF",
  "owner": "stefan@money.babsyit.ch"
}
```

### Schritt 2: Members hinzufügen (Cross-Instance!)

```bash
# Anna hinzufügen (andere Instanz!)
curl -X POST https://money.babsyit.ch/api/v1/shared-accounts/1/members \
  -H "Content-Type: application/json" \
  -d '{
    "user_identifier": "anna@money.example.com",
    "instance_url": "https://money.example.com",
    "role": "member"
  }'

# Tom hinzufügen (wieder andere Instanz!)
curl -X POST https://money.babsyit.ch/api/v1/shared-accounts/1/members \
  -H "Content-Type: application/json" \
  -d '{
    "user_identifier": "tom@money.other.ch",
    "instance_url": "https://money.other.ch",
    "role": "member"
  }'
```

**Was passiert intern:**
1. Stefan's Instanz sendet **Federation Request** an Anna's Instanz
2. Anna's Instanz verifiziert **Signature** von Stefan's Instanz
3. Anna bekommt **Notification** über Shared Account Einladung
4. Anna **akzeptiert** → wird als Member hinzugefügt

### Schritt 3: Split Transaction erstellen

```bash
# Stefan bezahlt Miete CHF 1800
curl -X POST https://money.babsyit.ch/api/v1/shared-accounts/1/split-transaction \
  -H "Content-Type: application/json" \
  -d '{
    "paid_by": "stefan@money.babsyit.ch",
    "total_amount": 1800.00,
    "date": "2024-12-01",
    "description": "Miete Dezember",
    "category": "Rent",
    "split_type": "equal"
  }'
```

**Was passiert:**
1. System teilt CHF 1800 durch 3 Personen = CHF 600 pro Person
2. **Federation Messages** werden an Anna & Tom geschickt:
   - "Stefan hat Miete bezahlt, du schuldest CHF 600"
3. Anna & Tom sehen **rote Markierung** (pending confirmation)
4. Anna & Tom **bestätigen** ihre Anteile
5. Balance wird aktualisiert auf allen drei Instanzen

### Schritt 4: Balance abfragen

```bash
# Jeder auf seiner Instanz
curl https://money.babsyit.ch/api/v1/shared-accounts/1/balance  # Stefan
curl https://money.example.com/api/v1/shared-accounts/1/balance # Anna
curl https://money.other.ch/api/v1/shared-accounts/1/balance    # Tom
```

**Response (für alle gleich!):**
```json
[
  {
    "user": "stefan@money.babsyit.ch",
    "amount": 1200.00,
    "status": "owed"
  },
  {
    "user": "anna@money.example.com",
    "amount": -600.00,
    "status": "owes"
  },
  {
    "user": "tom@money.other.ch",
    "amount": -600.00,
    "status": "owes"
  }
]
```

**Interpretation:**
- Stefan hat CHF 1200 zu viel bezahlt (owed = ihm wird geschuldet)
- Anna schuldet CHF 600
- Tom schuldet CHF 600

### Schritt 5: Settlement

```bash
# Berechne minimale Transaktionen zum Ausgleich
curl -X POST https://money.babsyit.ch/api/v1/shared-accounts/1/settle
```

**Response:**
```json
[
  {
    "from": "anna@money.example.com",
    "to": "stefan@money.babsyit.ch",
    "amount": 600.00
  },
  {
    "from": "tom@money.other.ch",
    "to": "stefan@money.babsyit.ch",
    "amount": 600.00
  }
]
```

**Was passiert:**
1. Anna überweist Stefan CHF 600
2. Tom überweist Stefan CHF 600
3. Alle sind quitt!

---

## 🔐 Sicherheit bei Cross-Instance

### RSA Signierung

Alle Federation Messages sind **signiert**:

```python
# Stefan's Instanz signiert Message
message = {
    "type": "split_transaction",
    "shared_account_id": 1,
    "amount": 600.00,
    "for_user": "anna@money.example.com"
}

signature = sign_with_private_key(message, stefan_private_key)

# Sende zu Anna's Instanz
requests.post(
    "https://money.example.com/api/v1/federation/split/receive",
    json=message,
    headers={
        "X-Signature": signature,
        "X-Instance": "money.babsyit.ch"
    }
)

# Anna's Instanz verifiziert
stefan_public_key = get_public_key("money.babsyit.ch")
if verify_signature(message, signature, stefan_public_key):
    # Akzeptiere Message
    create_pending_transaction(message)
else:
    # Reject - ungültige Signatur!
    raise SecurityError("Invalid signature")
```

### Trust Model

**Option 1: Manual Approval (Default)**
- Jede Split Transaction muss manuell bestätigt werden
- Rot markiert bis Bestätigung
- Sicher aber mehr Klicks

**Option 2: Trusted Instances**
```bash
# Anna markiert Stefan's Instanz als trusted
curl -X POST https://money.example.com/api/v1/settings/federation \
  -d '{
    "trusted_instances": ["money.babsyit.ch"]
  }'

# Jetzt: Keine rote Markierung mehr für Stefan's Splits
# Auto-Accept von money.babsyit.ch
```

---

## 💡 Use Cases

### 1. WG (Wohngemeinschaft)

```
Members: 3-5 Personen, verschiedene Instanzen
Expenses: Miete, Strom, Internet, Putzmittel, WC-Papier
Split: Meist equal, manchmal custom (Zimmer-Größe)
Settlement: Monatlich
```

**Beispiel:**
```bash
# Miete
POST /split-transaction
{
  "amount": 1800.00,
  "split_type": "equal"
}

# Strom (Tom hat größeres Zimmer)
POST /split-transaction
{
  "amount": 150.00,
  "split_type": "custom",
  "shares": {
    "stefan": 30,
    "anna": 30,
    "tom": 40
  }
}
```

### 2. Vereinskasse

```
Members: 10-20 Personen, verschiedene Instanzen
Expenses: Vereinsanlässe, Material, Miete Vereinslokal
Split: Equal oder nach Teilnahme
Settlement: Jährlich an Generalversammlung
```

**Beispiel:**
```bash
# Vereinsanlass (nur Teilnehmer zahlen)
POST /split-transaction
{
  "amount": 500.00,
  "split_type": "custom",
  "participants": [
    "stefan@money.babsyit.ch",
    "anna@money.example.com",
    "peter@money.verein.ch",
    "maria@money.club.ch"
  ]
}
```

### 3. Familien-Budget

```
Members: 2-4 Personen (Eltern, Kinder)
Expenses: Haushalt, Ferien, Versicherungen
Split: Custom (Eltern 50/50, Kinder anteilsmäßig)
Settlement: Kontinuierlich
```

**Beispiel:**
```bash
# Ferien CHF 3000 (Eltern 50%, Kinder je 25%)
POST /split-transaction
{
  "amount": 3000.00,
  "split_type": "percentage",
  "shares": {
    "papa@money.babsyit.ch": 50,
    "mama@money.family.ch": 50,
    "kind1@money.family.ch": 25,
    "kind2@money.family.ch": 25
  }
}
```

### 4. Projekt-Team

```
Members: 5-10 Personen, Remote Team
Expenses: Coworking Space, Software, Hardware
Split: Equal oder nach Nutzung
Settlement: Pro Projekt
```

---

## 📊 Synchronisation

### Wie bleibt alles sync?

**Real-time Updates (Future v1.2):**
```
Stefan erstellt Split
    ↓
Federation Messages zu Anna & Tom
    ↓
Anna & Tom's Instanzen empfangen
    ↓
WebSocket Update zu Anna & Tom's Clients
    ↓
UI updated automatisch
```

**Current v1.0:**
```
Stefan erstellt Split
    ↓
Anna & Tom müssen manuell refreshen
    ↓
Oder: Nächster API Call zeigt neue Balance
```

### Conflict Resolution

**Szenario:** Zwei Personen erstellen gleichzeitig Split

```
Stefan: Split CHF 100 at 10:00:01
Anna:   Split CHF 50  at 10:00:02
```

**Resolution:**
- Beide Splits sind valid (verschiedene Transaktionen)
- Balance berechnet beide ein
- Kein Konflikt!

**Echter Konflikt:** Same Split, different amounts

```
Stefan's Instance: Split CHF 100 (Stefan paid)
Anna's Instance:   Split CHF 50  (Anna paid)
```

**Resolution:**
- Last-Write-Wins basierend auf Timestamp
- Oder: Manual Review wenn Delta > Threshold

---

## 🔧 Administration

### Shared Account Owner Rechte

**Owner kann:**
- Members hinzufügen/entfernen
- Shared Account Settings ändern
- Alle Splits sehen und editieren
- Account löschen

**Members können:**
- Eigene Splits erstellen
- Eigene Splits bestätigen/ablehnen
- Balance sehen
- Nicht: Andere Members entfernen

### Member entfernen

```bash
# Owner entfernt Member
DELETE /api/v1/shared-accounts/1/members/anna@money.example.com
```

**Was passiert:**
1. Balance wird final berechnet
2. Wenn Member Schulden hat: Settlement Message
3. Member wird aus Shared Account entfernt
4. Federation Message an Member's Instanz

---

## 🚨 Edge Cases

### 1. Member's Instanz ist offline

**Problem:** Tom's Instanz `money.other.ch` ist down

**Lösung:**
- Split wird trotzdem erstellt
- Tom's Anteil wird als "pending_federation" markiert
- Retry Logic sendet Message später nochmal
- Nach 7 Tagen: Manual Notification an Owner

### 2. Member wechselt Instanz

**Problem:** Anna wechselt von `money.example.com` zu `money.newhost.com`

**Lösung:**
```bash
# Owner updated Member
PUT /api/v1/shared-accounts/1/members/anna@money.example.com
{
  "new_identifier": "anna@money.newhost.com",
  "new_instance_url": "https://money.newhost.com"
}
```

### 3. Unterschiedliche Währungen

**Problem:** Stefan (CHF), Anna (EUR), Tom (THB) in einem Shared Account

**Current v1.0:**
- Shared Account hat **eine** Währung (z.B. CHF)
- Alle Splits in dieser Währung
- Conversion muss manuell erfolgen

**Future v1.2:**
- Multi-Currency Shared Accounts
- Automatic Conversion mit Exchange Rates
- Settlement in preferred Currency

---

## 📱 UI/UX

### In der App anzeigen

```typescript
// Shared Account List
const SharedAccountsList = () => {
  return (
    <div>
      <h2>Meine Gemeinschaftskonten</h2>
      <div className="shared-account">
        <h3>WG Binningen</h3>
        <div className="members">
          <span>👤 Stefan (du)</span>
          <span>🌐 Anna@money.example.com</span>
          <span>🌐 Tom@money.other.ch</span>
        </div>
        <div className="balance">
          <span className="owed">Dir wird geschuldet: CHF 600</span>
        </div>
      </div>
    </div>
  )
}
```

### Split erstellen

```typescript
const CreateSplitForm = () => {
  return (
    <form>
      <input type="number" placeholder="Betrag" />
      <select>
        <option>Equal Split</option>
        <option>Custom Amounts</option>
        <option>Percentage</option>
      </select>
      
      {/* Cross-Instance Members anzeigen */}
      <div className="members">
        <label>
          <input type="checkbox" checked disabled />
          Stefan (du) - money.babsyit.ch
        </label>
        <label>
          <input type="checkbox" defaultChecked />
          🌐 Anna - money.example.com
        </label>
        <label>
          <input type="checkbox" defaultChecked />
          🌐 Tom - money.other.ch
        </label>
      </div>
      
      <button>Split erstellen</button>
    </form>
  )
}
```

---

## 🎯 Best Practices

### 1. Start Small
- Beginne mit 2-3 Members
- Teste mit kleinen Beträgen
- Aktiviere Trust erst nach erfolgreichem Test

### 2. Clear Naming
```
✅ "WG Binningen - Haushalt"
✅ "Familie Müller - Ferien"
✅ "Feuerwehrverein - Kasse"

❌ "Shared1"
❌ "Test"
❌ "WG"
```

### 3. Regular Settlement
- WG: Monatlich
- Verein: Quartalsweise
- Familie: Kontinuierlich
- Projekte: Nach Abschluss

### 4. Documentation
- Description Field nutzen
- Categories setzen (Rent, Utilities, Food)
- Receipts hochladen wo möglich

### 5. Communication
- Vor großen Splits kommunizieren
- Settlement Date ankündigen
- Changes transparent machen

---

## 🚀 Roadmap

### v1.1 - Enhanced Federation
- [ ] Real-time Updates (WebSocket)
- [ ] Push Notifications für neue Splits
- [ ] Offline Support mit Sync Queue
- [ ] Better Conflict Resolution UI

### v1.2 - Advanced Features
- [ ] Multi-Currency Shared Accounts
- [ ] Recurring Splits (Miete automatisch)
- [ ] Split Templates
- [ ] Export für Accounting

### v2.0 - Mobile
- [ ] Mobile App mit Shared Account Support
- [ ] QR Code für schnelles Member hinzufügen
- [ ] Camera für Receipt Upload
- [ ] Biometric Auth für Settlement

---

## 💬 FAQ

**Q: Kann ich in mehreren Shared Accounts sein?**  
A: Ja, unbegrenzt! Verschiedene WGs, Vereine, Familien.

**Q: Muss ich der anderen Instanz vertrauen?**  
A: Nein, alle Messages sind RSA-signiert. Du musst nur deiner eigenen Instanz vertrauen.

**Q: Was wenn jemand nicht zahlt?**  
A: Settlement zeigt who owes what. Enforcement ist social, nicht technical.

**Q: Kann ich Member ohne ihre Zustimmung hinzufügen?**  
A: Nein, Member müssen Federation Request akzeptieren.

**Q: Kosten Shared Accounts extra?**  
A: Nein, komplett gratis in der Open Source Version.

**Q: Kann ich mit Nicht-Money-Manager Usern teilen?**  
A: Nein, beide müssen Money Manager nutzen (irgendeine Instanz).

**Q: Was wenn eine Instanz nicht mehr existiert?**  
A: Member kann auf neue Instanz wechseln (siehe Edge Cases).

---

**Cross-Instance Shared Accounts sind PRODUCTION READY!** 🚀

Siehe auch:
- [FEDERATION.md](FEDERATION.md) - Federation Details
- [SECURITY.md](SECURITY.md) - Security Konzept
- [API_EXAMPLES.md](API_EXAMPLES.md) - API Usage
