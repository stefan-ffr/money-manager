# Bank Import mit Auto-Matching

## 🏦 Problem gelöst: Automatische Konto-Zuordnung

**Das Problem:**
- Du hast 5 Konten bei verschiedenen Banken
- Jeden Monat 5 CSV Files zum Importieren
- Jedes Mal: "Welches Konto war das nochmal?" 🤔

**Die Lösung:**
**Markiere deine Konten** mit IBAN/Account Number → System findet automatisch das richtige Konto!

---

## ✅ Unterstützte Banken

### Schweizer Banken (v1.0)

| Bank | Format | Erkennungs-Feature | Status |
|------|--------|-------------------|---------|
| **PostFinance** | CSV (;) | "Buchungsdatum", "Valuta" | ✅ |
| **UBS** | CSV (,) | "Trade Date" | ✅ |
| **Raiffeisen** | CSV (;) | "Avisierungstext" | ✅ |
| **ZKB** | CSV (;) | "Wertstellung", "Belastung" | ✅ |
| **Credit Suisse** | CSV (,) | "Booking Date" | ✅ |

### Geplant (v1.2)

- Migros Bank
- Cantonal Banks (weitere)
- Neobanks (Neon, Yuh, etc.)
- ISO 20022 camt.053 (Universal!)

---

## 🔧 Setup: Konto für Auto-Import konfigurieren

### Schritt 1: Bank Identifier setzen

```bash
# API Call
curl -X POST http://localhost:8000/api/v1/import/bank/setup \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "bank_name": "PostFinance",
    "bank_identifier": "CH9300762011623852957",
    "enable_auto_import": true
  }'
```

**Response:**
```json
{
  "message": "Bank account configured",
  "account": {
    "id": 1,
    "name": "Girokonto PostFinance",
    "bank_name": "PostFinance",
    "bank_identifier": "CH9300762011623852957",
    "auto_import_enabled": true
  }
}
```

### Schritt 2: Jetzt einfach CSV hochladen!

```bash
# Upload CSV - System findet automatisch das richtige Konto!
curl -X POST http://localhost:8000/api/v1/import/bank/import \
  -F "file=@postfinance_export.csv" \
  -F "auto_match=true"
```

**Response:**
```json
{
  "success": true,
  "bank": "postfinance",
  "account_id": 1,
  "account_name": "Girokonto PostFinance",
  "transactions_created": 45,
  "duplicates_skipped": 3,
  "total_parsed": 48
}
```

**Das war's!** 🎉

---

## 🎯 Wie funktioniert Auto-Matching?

### 1. Bank Format erkennen

```python
# System liest CSV Header
header = "Buchungsdatum;Valuta;Avisierungstext;Gutschrift;Lastschrift;Saldo"

# Erkennt: PostFinance!
bank = detect_bank_format(header)
# -> "postfinance"
```

### 2. IBAN/Account Number extrahieren

```python
# System sucht nach IBAN im CSV (erste 10 Zeilen)
iban_found = "CH9300762011623852957"

# Oder: Account Number
account_number = "623852957"
```

### 3. Account finden

```python
# Query Database
account = db.query(Account).filter(
    Account.bank_identifier == "CH9300762011623852957"
).first()

# Gefunden! → account_id = 1
```

### 4. Transaktionen importieren

```python
# Parse CSV mit bank-spezifischem Parser
transactions = parse_postfinance(csv_content)

# Create Transactions
for tx in transactions:
    create_transaction(
        account_id=1,
        date=tx.date,
        amount=tx.amount,
        description=tx.description,
        source="csv_import",
        requires_confirmation=True  # Rot markiert!
    )
```

### 5. Duplicate Detection

```python
# Check: Existiert schon?
existing = db.query(Transaction).filter(
    Transaction.account_id == account_id,
    Transaction.date == tx.date,
    Transaction.amount == tx.amount,
    Transaction.description == tx.description
).first()

if existing:
    skip()  # Duplicate!
else:
    create()  # Neu!
```

---

## 📋 Bank-Spezifische Formate

### PostFinance CSV

**Format:**
```csv
Buchungsdatum;Valuta;Avisierungstext;Gutschrift;Lastschrift;Saldo
01.12.2024;01.12.2024;MIGROS BASEL;45.50;;5'432.10
05.12.2024;05.12.2024;LOHN DEZEMBER;;5'000.00;10'432.10
```

**Eigenschaften:**
- Delimiter: `;` (Semicolon)
- Date Format: `DD.MM.YYYY`
- Decimal: `.` (Point)
- Thousands: `'` (Apostrophe)
- Encoding: UTF-8

**Parser Logic:**
```python
amount = Decimal(row.get('Gutschrift', '0').replace("'", ""))
if not amount:
    amount = -Decimal(row.get('Lastschrift', '0').replace("'", ""))
```

### UBS CSV

**Format:**
```csv
Date,Description,Amount,Balance
2024-12-01,Grocery Store,-45.50,5432.10
2024-12-05,Salary,5000.00,10432.10
```

**Eigenschaften:**
- Delimiter: `,` (Comma)
- Date Format: `YYYY-MM-DD`
- Decimal: `.` (Point)
- Thousands: `,` (Comma)
- Encoding: UTF-8

**Parser Logic:**
```python
amount = Decimal(row['Amount'])  # Negative für Ausgaben
```

### Raiffeisen CSV

**Format:**
```csv
Buchung;Avisierungstext;Soll;Haben
01.12.2024;MIGROS BASEL;45.50;
05.12.2024;LOHN;;5'000.00
```

**Eigenschaften:**
- Delimiter: `;` (Semicolon)
- Date Format: `DD.MM.YYYY`
- Decimal: `.` (Point)
- Thousands: `'` (Apostrophe)
- Separate "Soll" (debit) / "Haben" (credit) columns

**Parser Logic:**
```python
amount = Decimal(row.get('Haben', '0').replace("'", ""))
if not amount:
    amount = -Decimal(row.get('Soll', '0').replace("'", ""))
```

### ZKB CSV

**Format:**
```csv
Wertstellung;Beschreibung;Belastung;Gutschrift
01.12.2024;MIGROS BASEL;45.50;
05.12.2024;LOHN;;5'000.00
```

**Eigenschaften:**
- Delimiter: `;` (Semicolon)
- Date Format: `DD.MM.YYYY`
- Decimal: `.` (Point)
- Thousands: `'` (Apostrophe)

---

## 💡 Use Cases

### Use Case 1: Monatlicher Import

```bash
# 1. Download CSVs von all deinen Banken
postfinance.csv
ubs.csv
raiffeisen.csv

# 2. Upload alle (System matcht automatisch)
for csv in *.csv; do
  curl -X POST http://localhost:8000/api/v1/import/bank/import \
    -F "file=@$csv" \
    -F "auto_match=true"
done

# 3. Fertig! Alle Transaktionen importiert ✅
```

### Use Case 2: Setup für neues Konto

```bash
# 1. Erstelle Account
curl -X POST http://localhost:8000/api/v1/accounts \
  -d '{
    "name": "UBS Sparkonto",
    "type": "savings",
    "iban": "CH1234567890",
    "currency": "CHF"
  }'
# -> account_id = 5

# 2. Setze Bank Identifier
curl -X POST http://localhost:8000/api/v1/import/bank/setup \
  -d '{
    "account_id": 5,
    "bank_name": "UBS",
    "bank_identifier": "CH1234567890",
    "enable_auto_import": true
  }'

# 3. Import CSV (findet jetzt automatisch Account 5)
curl -X POST http://localhost:8000/api/v1/import/bank/import \
  -F "file=@ubs_export.csv"
```

### Use Case 3: Multi-Bank Setup

```bash
# Setup für alle deine Konten
accounts=(
  "1:PostFinance:CH9300762011623852957"
  "2:UBS:CH1234567890"
  "3:Raiffeisen:CH9876543210"
  "4:ZKB:CH5555555555"
)

for account in "${accounts[@]}"; do
  IFS=: read -r id bank iban <<< "$account"
  
  curl -X POST http://localhost:8000/api/v1/import/bank/setup \
    -d "{
      \"account_id\": $id,
      \"bank_name\": \"$bank\",
      \"bank_identifier\": \"$iban\",
      \"enable_auto_import\": true
    }"
done

echo "All accounts configured for auto-import!"
```

---

## 🔍 Import Status prüfen

### Account Info abrufen

```bash
curl http://localhost:8000/api/v1/import/bank/account/1/info
```

**Response:**
```json
{
  "account_id": 1,
  "account_name": "Girokonto PostFinance",
  "bank_configured": true,
  "bank_name": "PostFinance",
  "bank_identifier": "CH9300762011623852957",
  "auto_import_enabled": true,
  "last_import": "2024-12-07T10:30:00Z"
}
```

### Unterstützte Banken listen

```bash
curl http://localhost:8000/api/v1/import/bank/supported
```

**Response:**
```json
{
  "banks": [
    {
      "id": "postfinance",
      "name": "PostFinance",
      "format": "Semicolon-separated (;)",
      "encoding": "UTF-8",
      "date_format": "DD.MM.YYYY"
    },
    {
      "id": "ubs",
      "name": "UBS",
      "format": "Comma-separated (,)",
      "encoding": "UTF-8",
      "date_format": "YYYY-MM-DD"
    }
  ]
}
```

---

## ⚠️ Wichtige Hinweise

### Duplicate Detection

**System prüft:**
- Gleiche Account ID
- Gleiches Datum
- Gleicher Betrag
- Gleiche Beschreibung

**→ Wenn alle 4 gleich = Duplicate (skip)**

**Tipp:** Bei mehrfachem Import keine Angst vor Duplikaten!

### Bestätigungspflicht

**Alle CSV Imports sind rot markiert!**
```python
source = "csv_import"
requires_confirmation = True
```

**Warum?**
- Sicherheit: Review vor Finalisierung
- Kategorisierung: Chance zum Anpassen
- Fehlerkorrektur: Falsche Einträge löschen

**Workflow:**
1. Import → Einträge sind rot
2. Review in UI
3. Bestätigen → Einträge werden grün
4. Oder: Löschen wenn falsch

### IBAN Format

**Valid IBAN:**
```
CH93 0076 2011 6238 5295 7  (mit Spaces)
CH9300762011623852957       (ohne Spaces)
```

**System akzeptiert beide!**

---

## 🎨 UI Integration (geplant v1.1)

### Import Page

```typescript
const BankImportPage = () => {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  
  const handleImport = async () => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('auto_match', 'true')
    
    const res = await fetch('/api/v1/import/bank/import', {
      method: 'POST',
      body: formData
    })
    
    const data = await res.json()
    setResult(data)
  }
  
  return (
    <div>
      <h2>Bank CSV Import</h2>
      
      {/* Upload */}
      <input 
        type="file" 
        accept=".csv"
        onChange={(e) => setFile(e.target.files[0])}
      />
      
      <button onClick={handleImport}>
        Import
      </button>
      
      {/* Result */}
      {result && (
        <div className="success">
          ✅ {result.transactions_created} Transaktionen importiert
          ℹ️ {result.duplicates_skipped} Duplikate übersprungen
          🏦 Bank: {result.bank}
          💼 Konto: {result.account_name}
        </div>
      )}
    </div>
  )
}
```

### Account Settings

```typescript
const AccountSettings = ({ account }) => {
  return (
    <div className="bank-config">
      <h3>Bank Import Konfiguration</h3>
      
      <label>
        Bank Name
        <input value={account.bank_name} />
      </label>
      
      <label>
        IBAN / Account Number
        <input value={account.bank_identifier} />
      </label>
      
      <label>
        <input 
          type="checkbox" 
          checked={account.bank_import_enabled}
        />
        Auto-Import aktivieren
      </label>
      
      {account.last_import && (
        <p>Letzter Import: {account.last_import}</p>
      )}
      
      <button>Speichern</button>
    </div>
  )
}
```

---

## 🚀 Roadmap

### v1.1 - Enhanced Import
- [ ] UI für CSV Upload (Drag & Drop)
- [ ] Import History (alle Imports anzeigen)
- [ ] Batch Import (mehrere Files gleichzeitig)
- [ ] Preview vor Import

### v1.2 - ISO 20022
- [ ] camt.053 Parser (Universal XML Format)
- [ ] camt.054 Support
- [ ] Auto-Download direkt von Bank (Open Banking API)

### v2.0 - Smart Features
- [ ] ML-based Category Prediction
- [ ] Automatic Merchant Recognition
- [ ] Recurring Transaction Detection
- [ ] Anomaly Detection

---

## 🔧 Troubleshooting

### Problem: "Unknown bank format"

**Ursache:** CSV Header nicht erkannt

**Lösung:**
```bash
# Check CSV Header
head -1 your_file.csv

# Manuell Bank angeben (future)
curl -F "file=@file.csv" -F "bank=postfinance"
```

### Problem: "No matching account found"

**Ursache:** Account hat keinen bank_identifier gesetzt

**Lösung:**
```bash
# Setup Bank Identifier
POST /api/v1/import/bank/setup
{
  "account_id": 1,
  "bank_identifier": "YOUR_IBAN"
}
```

### Problem: "Encoding Error"

**Ursache:** CSV nicht in UTF-8

**Lösung:**
```bash
# Convert to UTF-8
iconv -f ISO-8859-1 -t UTF-8 input.csv > output.csv

# Then import
curl -F "file=@output.csv"
```

### Problem: Zu viele Duplicates

**Ursache:** CSV enthält alte Transaktionen

**Lösung:**
- Normal! System überspringt Duplikate automatisch
- Check: `duplicates_skipped` in Response
- Tipp: Bank CSVs immer ab letztem Import-Datum exportieren

---

## 📊 Statistics

```bash
# Import Statistics (future API)
GET /api/v1/import/bank/stats

{
  "total_imports": 48,
  "total_transactions": 1205,
  "by_bank": {
    "postfinance": 856,
    "ubs": 234,
    "raiffeisen": 115
  },
  "last_import": "2024-12-07T10:30:00Z",
  "average_per_import": 25
}
```

---

## 💡 Pro Tips

### 1. IBAN als Identifier nutzen

```
✅ bank_identifier = "CH9300762011623852957"
❌ bank_identifier = "Girokonto"
```

**Warum?**
- IBAN ist eindeutig
- Steht in jedem CSV
- Kein Verwechslungsrisiko

### 2. Monatlicher Import Workflow

```bash
#!/bin/bash
# monthly_import.sh

# Download CSVs von Banken (manuell oder via API future)
# ...

# Import alle
for csv in downloads/*.csv; do
  echo "Importing $csv..."
  curl -X POST http://localhost:8000/api/v1/import/bank/import \
    -F "file=@$csv" \
    -F "auto_match=true"
done

echo "✅ All imports done!"
```

### 3. Test mit kleinem CSV

```csv
Buchungsdatum;Valuta;Avisierungstext;Gutschrift;Lastschrift;Saldo
01.12.2024;01.12.2024;TEST TRANSACTION;100.00;;1000.00
```

**Import → Check → Löschen → Real Import**

### 4. Backup vor Import

```bash
# Export current state
curl http://localhost:8000/api/v1/settings/export-data \
  > backup_before_import.json

# Import
curl -F "file=@bank.csv" ...

# Bei Fehler: Restore
# ...
```

---

## 🎯 Zusammenfassung

**Setup einmal:**
```bash
POST /bank/setup
{
  "account_id": 1,
  "bank_identifier": "CH..."
}
```

**Import immer:**
```bash
POST /bank/import
{
  "file": csv_file,
  "auto_match": true
}
```

**Fertig!** 🚀

System findet automatisch das richtige Konto und importiert alle Transaktionen. Duplicates werden erkannt, alles ist rot markiert für Review, und du sparst massiv Zeit!

---

Siehe auch:
- [API_EXAMPLES.md](API_EXAMPLES.md) - API Usage
- [FEATURES.md](FEATURES.md) - Feature Overview
- [ROADMAP.md](ROADMAP.md) - Future Plans
