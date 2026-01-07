# Money Manager API - Beispiele

Praktische Beispiele wie du die Money Manager API nutzen kannst - genau wie Cloudflare's API.

## 🚀 Quick Start

```bash
# API Base URL
API_URL="http://localhost:8000"

# Mit Bearer Token (v1.1)
TOKEN="your_api_token_here"
```

---

## 💰 Accounts

### Liste alle Konten

```bash
curl ${API_URL}/api/v1/accounts
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Girokonto",
    "type": "checking",
    "iban": "CH1234567890",
    "balance": 5432.10,
    "currency": "CHF"
  },
  {
    "id": 2,
    "name": "Thailand Savings",
    "type": "savings",
    "balance": 50000.00,
    "currency": "THB"
  }
]
```

### Erstelle neues Konto

```bash
curl -X POST ${API_URL}/api/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Thailand Savings",
    "type": "savings",
    "currency": "THB",
    "balance": 50000.00
  }'
```

### Hole spezifisches Konto

```bash
curl ${API_URL}/api/v1/accounts/1
```

### Update Konto

```bash
curl -X PUT ${API_URL}/api/v1/accounts/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Girokonto UBS",
    "balance": 6000.00
  }'
```

### Lösche Konto

```bash
curl -X DELETE ${API_URL}/api/v1/accounts/1
```

---

## 💸 Transactions

### Liste Transaktionen (mit Filter)

```bash
# Alle Transaktionen
curl ${API_URL}/api/v1/transactions

# Filter nach Account
curl "${API_URL}/api/v1/transactions?account_id=1"

# Filter nach Status
curl "${API_URL}/api/v1/transactions?status=pending"

# Kombiniert mit Pagination
curl "${API_URL}/api/v1/transactions?account_id=1&limit=10&skip=0"
```

### Erstelle Transaktion

```bash
curl -X POST ${API_URL}/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "date": "2024-12-07",
    "amount": -150.50,
    "category": "Food",
    "description": "Grocery shopping at Migros",
    "source": "manual",
    "requires_confirmation": false
  }'
```

### Thai Baht Transaktion

```bash
curl -X POST ${API_URL}/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 2,
    "date": "2024-12-07",
    "amount": -1500.00,
    "category": "Food",
    "description": "Dinner in Bangkok",
    "source": "manual"
  }'
```

### Upload Receipt

```bash
curl -X POST ${API_URL}/api/v1/transactions/1/receipt \
  -F "file=@receipt.pdf"
```

### Get Receipt

```bash
curl ${API_URL}/api/v1/transactions/1/receipt \
  --output receipt.pdf
```

### Update Transaktion

```bash
curl -X PUT ${API_URL}/api/v1/transactions/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "confirmed",
    "requires_confirmation": false
  }'
```

### Bestätige Telegram/Federation Entry

```bash
# Ändere von pending/red zu confirmed/normal
curl -X PUT ${API_URL}/api/v1/transactions/5 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "confirmed",
    "requires_confirmation": false
  }'
```

---

## 🏷️ Categories & EasyTax

### Liste Kategorien

```bash
curl ${API_URL}/api/v1/categories
```

### Erstelle Kategorie

```bash
curl -X POST ${API_URL}/api/v1/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Verpflegung",
    "easytax_code": "3300"
  }'
```

### EasyTax Export

```bash
# Export für 2024
curl "${API_URL}/api/v1/categories/easytax-export?year=2024" \
  --output easytax_2024.csv

# Inhalt:
# Datum;Betrag;Kategorie;Beschreibung;Belegnummer
# 01.12.2024;-150.50;Food;Grocery shopping;TX-1
# 05.12.2024;-45.00;Transport;Train ticket;TX-2
```

---

## 👥 Shared Accounts (Gemeinschaftskonten)

### Liste Shared Accounts

```bash
curl ${API_URL}/api/v1/shared-accounts
```

### Erstelle WG Konto

```bash
curl -X POST ${API_URL}/api/v1/shared-accounts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "WG Haushalt",
    "description": "Gemeinsame Ausgaben",
    "currency": "CHF"
  }'
```

### Füge Member hinzu

```bash
curl -X POST ${API_URL}/api/v1/shared-accounts/1/members \
  -H "Content-Type: application/json" \
  -d '{
    "user_identifier": "anna@money.example.com",
    "instance_url": "https://money.example.com",
    "role": "member"
  }'
```

### Split Transaktion erstellen

```bash
# Stefan bezahlt Miete CHF 1800, aufteilen auf 3 Personen
curl -X POST ${API_URL}/api/v1/shared-accounts/1/split-transaction \
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

### Balance abfragen

```bash
curl ${API_URL}/api/v1/shared-accounts/1/balance
```

**Response:**
```json
[
  {
    "user": "stefan@money.babsyit.ch",
    "amount": 500.00,
    "status": "owed"
  },
  {
    "user": "anna@money.example.com",
    "amount": -250.00,
    "status": "owes"
  },
  {
    "user": "tom@money.other.com",
    "amount": -250.00,
    "status": "owes"
  }
]
```

### Settlement berechnen

```bash
curl -X POST ${API_URL}/api/v1/shared-accounts/1/settle
```

**Response:**
```json
[
  {
    "from": "anna@money.example.com",
    "to": "stefan@money.babsyit.ch",
    "amount": 250.00
  },
  {
    "from": "tom@money.other.com",
    "to": "stefan@money.babsyit.ch",
    "amount": 250.00
  }
]
```

---

## 🌐 Federation

### Test Verbindung zu anderer Instanz

```bash
curl -X POST "${API_URL}/api/v1/settings/test-federation?instance_url=https://money.example.com"
```

**Response:**
```json
{
  "status": "success",
  "instance_id": "money.example.com",
  "federation_enabled": true,
  "message": "Connection successful"
}
```

### Sende Rechnung an andere Instanz

```bash
curl -X POST ${API_URL}/api/v1/federation/invoice/send \
  -H "Content-Type: application/json" \
  -d '{
    "from_user": "stefan@money.babsyit.ch",
    "to_user": "anna@money.example.com",
    "amount": 150.00,
    "currency": "CHF",
    "description": "Miete Anteil",
    "date": "2024-12-01",
    "category": "Rent"
  }'
```

### Public Key abrufen

```bash
curl ${API_URL}/.well-known/money-instance
```

**Response:**
```json
{
  "instance_id": "money.babsyit.ch",
  "version": "1.0.0",
  "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIj...",
  "api_endpoint": "https://money.babsyit.ch/api/v1",
  "federation_enabled": true
}
```

---

## ⚙️ Settings

### Hole alle Einstellungen

```bash
# Preferences
curl ${API_URL}/api/v1/settings/preferences

# Federation
curl ${API_URL}/api/v1/settings/federation

# Telegram
curl ${API_URL}/api/v1/settings/telegram

# Security
curl ${API_URL}/api/v1/settings/security
```

### Liste Währungen

```bash
curl ${API_URL}/api/v1/settings/currencies
```

**Response:**
```json
{
  "currencies": {
    "CHF": {
      "code": "CHF",
      "name": "Schweizer Franken",
      "symbol": "CHF",
      "decimal_places": 2
    },
    "THB": {
      "code": "THB",
      "name": "Thai Baht",
      "symbol": "฿",
      "decimal_places": 2
    },
    "BTC": {
      "code": "BTC",
      "name": "Bitcoin",
      "symbol": "₿",
      "decimal_places": 8
    }
  },
  "default": "CHF"
}
```

### Update Preferences

```bash
curl -X PUT ${API_URL}/api/v1/settings/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "default_currency": "THB",
    "date_format": "DD.MM.YYYY",
    "language": "de",
    "theme": "dark"
  }'
```

### Generiere neue Federation Keys

```bash
curl -X POST ${API_URL}/api/v1/settings/generate-federation-keys
```

### Export alle Daten

```bash
curl ${API_URL}/api/v1/settings/export-data \
  --output money-manager-export.json
```

---

## 🔐 Authentication (v1.1)

### Login mit Credentials

```bash
curl -X POST ${API_URL}/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "stefan",
    "password": "your_password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Nutze API mit Token

```bash
# Speichere Token
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Nutze in Requests
curl -H "Authorization: Bearer ${TOKEN}" \
  ${API_URL}/api/v1/accounts
```

---

## 📊 Batch Operations

### Multiple Transaktionen erstellen

```bash
# transactions.json
[
  {
    "account_id": 1,
    "date": "2024-12-01",
    "amount": -50.00,
    "description": "Groceries"
  },
  {
    "account_id": 1,
    "date": "2024-12-02",
    "amount": -25.00,
    "description": "Coffee"
  },
  {
    "account_id": 1,
    "date": "2024-12-03",
    "amount": -100.00,
    "description": "Restaurant"
  }
]

# Loop durch alle Transaktionen
cat transactions.json | jq -c '.[]' | while read tx; do
  curl -X POST ${API_URL}/api/v1/transactions \
    -H "Content-Type: application/json" \
    -d "$tx"
done
```

---

## 🐍 Python Script Beispiel

```python
#!/usr/bin/env python3
import requests
import json
from datetime import date

API_URL = "http://localhost:8000"

# Erstelle Account
def create_account(name, type, currency="CHF"):
    response = requests.post(
        f"{API_URL}/api/v1/accounts",
        json={
            "name": name,
            "type": type,
            "currency": currency,
            "balance": 0.00
        }
    )
    return response.json()

# Liste Accounts
def list_accounts():
    response = requests.get(f"{API_URL}/api/v1/accounts")
    return response.json()

# Erstelle Transaktion
def create_transaction(account_id, amount, description):
    response = requests.post(
        f"{API_URL}/api/v1/transactions",
        json={
            "account_id": account_id,
            "date": str(date.today()),
            "amount": amount,
            "description": description,
            "source": "api"
        }
    )
    return response.json()

# Export EasyTax
def export_easytax(year):
    response = requests.get(
        f"{API_URL}/api/v1/categories/easytax-export",
        params={"year": year}
    )
    with open(f"easytax_{year}.csv", "wb") as f:
        f.write(response.content)
    print(f"Exported to easytax_{year}.csv")

# Main
if __name__ == "__main__":
    # Erstelle Thailand Account
    account = create_account("Thailand Savings", "savings", "THB")
    print(f"Created account: {account['id']}")
    
    # Erstelle Transaktionen
    tx1 = create_transaction(account['id'], -1500.00, "Dinner in Bangkok")
    tx2 = create_transaction(account['id'], -500.00, "Shopping at MBK")
    
    print(f"Created {len([tx1, tx2])} transactions")
    
    # Export für Steuern
    export_easytax(2024)
```

---

## 🔄 Automation mit n8n

```json
{
  "nodes": [
    {
      "name": "HTTP Request",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:8000/api/v1/transactions",
        "method": "POST",
        "bodyParameters": {
          "parameters": [
            {
              "name": "account_id",
              "value": "1"
            },
            {
              "name": "date",
              "value": "={{$now.format('YYYY-MM-DD')}}"
            },
            {
              "name": "amount",
              "value": "-50.00"
            },
            {
              "name": "description",
              "value": "{{$json.description}}"
            }
          ]
        }
      }
    }
  ]
}
```

---

## 📱 Mobile App Integration (v2.0)

```swift
// Swift iOS Example
import Foundation

struct Account: Codable {
    let id: Int
    let name: String
    let balance: Double
    let currency: String
}

class MoneyManagerAPI {
    let baseURL = "https://money.babsyit.ch"
    
    func getAccounts() async throws -> [Account] {
        let url = URL(string: "\(baseURL)/api/v1/accounts")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode([Account].self, from: data)
    }
}
```

---

## 🎯 Best Practices

### 1. Error Handling

```bash
# Nutze -f für fail on error
# Nutze -s für silent
# Nutze -S für show errors

curl -fsSL ${API_URL}/api/v1/accounts || echo "Request failed"
```

### 2. Response Formatting

```bash
# Mit jq für pretty JSON
curl ${API_URL}/api/v1/accounts | jq '.'

# Nur bestimmte Felder
curl ${API_URL}/api/v1/accounts | jq '.[].name'

# Filter
curl ${API_URL}/api/v1/accounts | jq '.[] | select(.currency == "THB")'
```

### 3. Rate Limiting

```bash
# Check headers
curl -I ${API_URL}/api/v1/accounts

# Response:
# X-RateLimit-Limit: 1000
# X-RateLimit-Remaining: 995
# X-RateLimit-Reset: 1702123456
```

### 4. Debugging

```bash
# Verbose mode
curl -v ${API_URL}/api/v1/accounts

# Trace mode
curl --trace-ascii - ${API_URL}/api/v1/accounts
```

---

## 📚 Weitere Ressourcen

- **Interactive API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Spec:** http://localhost:8000/openapi.json
- **Architecture:** [API_ARCHITECTURE.md](API_ARCHITECTURE.md)
- **Postman:** Import OpenAPI spec in Postman

---

**Die API ist das Herz! Nutze sie wie du willst!** 🚀
