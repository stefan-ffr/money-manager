# API-First Architecture - Money Manager

Money Manager folgt einer **vollständig API-basierten Architektur** - genau wie Cloudflare, Stripe, oder Twilio.

## 🎯 Prinzip: Everything is an API

```
┌─────────────────────────────────────────────────────┐
│                   API Layer                          │
│              FastAPI REST API                        │
│         /api/v1/* - All Endpoints                   │
└─────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Web UI    │  │  Mobile App │  │  CLI Tool   │
│  (React)    │  │   (Future)  │  │   (curl)    │
└─────────────┘  └─────────────┘  └─────────────┘
```

**Kernprinzip:** Das Frontend ist nur **ein Consumer** von vielen!

---

## 🔑 API-First Benefits

### 1. **Flexibilität**
Jeder kann die API nutzen:
- Web Interface (React)
- Mobile Apps (iOS/Android)
- CLI Tools (curl, Python scripts)
- Third-Party Integrations
- Automation (n8n, Zapier)

### 2. **Unabhängigkeit**
Frontend und Backend sind **komplett entkoppelt**:
- Backend kann ohne Frontend deployt werden
- Frontend kann gegen verschiedene APIs laufen
- Einfaches Testing mit Postman/Insomnia
- Mock-Daten für Frontend-Development

### 3. **Skalierbarkeit**
- Backend kann horizontal skalieren
- Frontend ist statisch (CDN)
- API kann LoadBalancer vorgeschaltet werden
- Microservices-ready

### 4. **Documentation First**
- Auto-Generated OpenAPI Docs
- Interactive API Explorer
- Code Examples automatisch
- Immer aktuell

---

## 📡 API Endpoints Overview

### Core Resources

```
Accounts
  GET    /api/v1/accounts              - List all accounts
  GET    /api/v1/accounts/{id}         - Get specific account
  POST   /api/v1/accounts              - Create account
  PUT    /api/v1/accounts/{id}         - Update account
  DELETE /api/v1/accounts/{id}         - Delete account

Transactions
  GET    /api/v1/transactions          - List transactions
  GET    /api/v1/transactions/{id}     - Get transaction
  POST   /api/v1/transactions          - Create transaction
  PUT    /api/v1/transactions/{id}     - Update transaction
  DELETE /api/v1/transactions/{id}     - Delete transaction
  POST   /api/v1/transactions/{id}/receipt    - Upload receipt
  GET    /api/v1/transactions/{id}/receipt    - Get receipt

Categories
  GET    /api/v1/categories            - List categories
  POST   /api/v1/categories            - Create category
  GET    /api/v1/categories/easytax-export?year=2024  - Export CSV

Shared Accounts
  GET    /api/v1/shared-accounts       - List shared accounts
  POST   /api/v1/shared-accounts       - Create shared account
  POST   /api/v1/shared-accounts/{id}/members          - Add member
  POST   /api/v1/shared-accounts/{id}/split-transaction - Split payment
  GET    /api/v1/shared-accounts/{id}/balance          - Get balance
  POST   /api/v1/shared-accounts/{id}/settle           - Calculate settlement

Federation
  POST   /api/v1/federation/invoice/send                - Send invoice
  POST   /api/v1/federation/invoice/receive             - Receive invoice
  POST   /api/v1/federation/invoice/{id}/accept         - Accept invoice
  POST   /api/v1/federation/invoice/{id}/reject         - Reject invoice
  GET    /api/v1/federation/instances/{domain}          - Get instance info

Settings
  GET    /api/v1/settings/preferences  - Get preferences
  PUT    /api/v1/settings/preferences  - Update preferences
  GET    /api/v1/settings/federation   - Get federation config
  PUT    /api/v1/settings/federation   - Update federation
  GET    /api/v1/settings/mirrors      - List mirror instances
  POST   /api/v1/settings/mirrors      - Add mirror
  DELETE /api/v1/settings/mirrors/{id} - Remove mirror
  GET    /api/v1/settings/telegram     - Get telegram config
  PUT    /api/v1/settings/telegram     - Update telegram
  GET    /api/v1/settings/categories/mappings - Get mappings
  POST   /api/v1/settings/categories/mappings - Create mapping
  GET    /api/v1/settings/security     - Get security settings
  PUT    /api/v1/settings/security     - Update security
  POST   /api/v1/settings/test-federation     - Test connection
  POST   /api/v1/settings/generate-federation-keys - Generate keys
  GET    /api/v1/settings/export-data         - Export all data
```

### Well-Known Endpoints

```
GET /.well-known/money-instance       - Federation discovery
```

### Health & Meta

```
GET /                                 - API info
GET /health                           - Health check
GET /docs                             - Interactive API docs (Swagger UI)
GET /redoc                            - Alternative docs (ReDoc)
GET /openapi.json                     - OpenAPI spec
```

---

## 🔐 Authentication (v1.1)

### API Key Authentication

```bash
# Header-based
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://money.babsyit.ch/api/v1/accounts

# Query parameter (fallback)
curl https://money.babsyit.ch/api/v1/accounts?api_key=YOUR_API_KEY
```

### OAuth2 / JWT Tokens

```bash
# 1. Login
curl -X POST https://money.babsyit.ch/api/v1/auth/login \
  -d '{"username": "stefan", "password": "***"}'

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}

# 2. Use token
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  https://money.babsyit.ch/api/v1/accounts
```

### Passkey / WebAuthn

```javascript
// Frontend initiates WebAuthn
const credential = await navigator.credentials.get({
  publicKey: challengeFromServer
})

// Send to backend
fetch('/api/v1/auth/webauthn/verify', {
  method: 'POST',
  body: JSON.stringify(credential)
})
```

---

## 📊 API Response Format

### Success Response

```json
{
  "data": {
    "id": 123,
    "name": "Girokonto",
    "balance": 5432.10
  },
  "meta": {
    "timestamp": "2024-12-07T12:34:56Z",
    "version": "v1"
  }
}
```

### List Response with Pagination

```json
{
  "data": [
    {"id": 1, "...": "..."},
    {"id": 2, "...": "..."}
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 156,
    "total_pages": 8
  },
  "links": {
    "first": "/api/v1/transactions?page=1",
    "prev": null,
    "next": "/api/v1/transactions?page=2",
    "last": "/api/v1/transactions?page=8"
  }
}
```

### Error Response

```json
{
  "error": {
    "code": "INVALID_ACCOUNT",
    "message": "Account with ID 999 not found",
    "details": {
      "account_id": 999
    }
  },
  "meta": {
    "timestamp": "2024-12-07T12:34:56Z",
    "request_id": "req_abc123"
  }
}
```

---

## 🎨 Frontend als API Consumer

### React Query Pattern

```typescript
// frontend/src/services/api.ts
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor for auth
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Services
export const accountsApi = {
  list: () => api.get('/api/v1/accounts'),
  get: (id: number) => api.get(`/api/v1/accounts/${id}`),
  create: (data: AccountCreate) => api.post('/api/v1/accounts', data),
  update: (id: number, data: AccountUpdate) => 
    api.put(`/api/v1/accounts/${id}`, data),
  delete: (id: number) => api.delete(`/api/v1/accounts/${id}`)
}
```

### Component Usage

```typescript
// frontend/src/components/AccountList.tsx
import { useQuery, useMutation } from '@tanstack/react-query'
import { accountsApi } from '../services/api'

function AccountList() {
  // Query
  const { data, isLoading } = useQuery({
    queryKey: ['accounts'],
    queryFn: accountsApi.list
  })

  // Mutation
  const createAccount = useMutation({
    mutationFn: accountsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['accounts'])
    }
  })

  // Everything is API-driven!
  return (
    <div>
      {data?.data.map(account => (
        <div key={account.id}>{account.name}</div>
      ))}
    </div>
  )
}
```

---

## 🔨 CLI Tool Usage

### curl Examples

```bash
# List accounts
curl https://money.babsyit.ch/api/v1/accounts

# Create account
curl -X POST https://money.babsyit.ch/api/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sparkonto",
    "type": "savings",
    "balance": 10000.00,
    "currency": "CHF"
  }'

# Create transaction
curl -X POST https://money.babsyit.ch/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "date": "2024-12-07",
    "amount": -50.00,
    "description": "Groceries",
    "category": "Food"
  }'

# Export EasyTax
curl https://money.babsyit.ch/api/v1/categories/easytax-export?year=2024 \
  -o easytax_2024.csv
```

### Python SDK (Future)

```python
# money_manager/__init__.py
from money_manager import MoneyManager

client = MoneyManager(
    api_url="https://money.babsyit.ch",
    api_key="your_api_key"
)

# List accounts
accounts = client.accounts.list()

# Create transaction
tx = client.transactions.create(
    account_id=1,
    date="2024-12-07",
    amount=-50.00,
    description="Groceries"
)

# Export EasyTax
client.categories.export_easytax(year=2024, output="tax.csv")
```

---

## 📱 Multi-Currency Support

### Currencies Supported

```python
# backend/app/core/currencies.py
SUPPORTED_CURRENCIES = {
    "CHF": {"name": "Schweizer Franken", "symbol": "CHF", "decimal_places": 2},
    "EUR": {"name": "Euro", "symbol": "€", "decimal_places": 2},
    "USD": {"name": "US Dollar", "symbol": "$", "decimal_places": 2},
    "THB": {"name": "Thai Baht", "symbol": "฿", "decimal_places": 2},
    # Easy to add more:
    "GBP": {"name": "British Pound", "symbol": "£", "decimal_places": 2},
    "JPY": {"name": "Japanese Yen", "symbol": "¥", "decimal_places": 0},
    "BTC": {"name": "Bitcoin", "symbol": "₿", "decimal_places": 8},
}

def get_currency_symbol(currency_code: str) -> str:
    return SUPPORTED_CURRENCIES.get(currency_code, {}).get("symbol", currency_code)
```

### API Currency Handling

```json
// Request
POST /api/v1/accounts
{
  "name": "Thailand Savings",
  "type": "savings",
  "currency": "THB",
  "balance": 50000.00
}

// Response
{
  "data": {
    "id": 5,
    "name": "Thailand Savings",
    "type": "savings",
    "currency": "THB",
    "balance": 50000.00,
    "formatted_balance": "฿50,000.00"
  }
}
```

---

## 🔄 API Versioning

### Current: v1

```
/api/v1/accounts
/api/v1/transactions
```

### Future: v2 (Breaking Changes)

```
/api/v2/accounts
/api/v2/transactions
```

### Version Header Support

```bash
# Request specific version
curl -H "X-API-Version: 1" \
  https://money.babsyit.ch/api/accounts

# Default to latest
curl https://money.babsyit.ch/api/v1/accounts
```

---

## 📈 Rate Limiting

### Default Limits (v1.1)

```
Endpoint Type          Limit
──────────────────────────────
Public                 100 req/min
Authenticated          1000 req/min
Admin                  Unlimited
```

### Rate Limit Headers

```bash
curl -I https://money.babsyit.ch/api/v1/accounts

HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1702123456
```

### Implementation

```python
# backend/app/middleware/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/accounts")
@limiter.limit("1000/minute")
async def list_accounts():
    # ...
```

---

## 🧪 API Testing

### Interactive Docs

```
Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
OpenAPI:     http://localhost:8000/openapi.json
```

**Features:**
- Try it out in browser
- Auto-generated code samples
- Request/Response examples
- Schema validation

### Postman Collection

```bash
# Export OpenAPI spec
curl http://localhost:8000/openapi.json > money-manager.openapi.json

# Import in Postman
File → Import → money-manager.openapi.json
```

### Automated Testing

```python
# backend/tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_accounts():
    response = client.get("/api/v1/accounts")
    assert response.status_code == 200
    assert "data" in response.json()

def test_create_account():
    response = client.post("/api/v1/accounts", json={
        "name": "Test Account",
        "type": "checking",
        "currency": "CHF"
    })
    assert response.status_code == 201
    assert response.json()["data"]["name"] == "Test Account"
```

---

## 🌍 CORS Configuration

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Local dev
        "https://money.babsyit.ch",   # Production
        "https://app.babsyit.ch",     # Alternative domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🚀 API Deployment

### Production Checklist

- [ ] HTTPS enabled (Let's Encrypt)
- [ ] Rate limiting configured
- [ ] CORS properly set
- [ ] Authentication required
- [ ] API keys rotated regularly
- [ ] Monitoring & logging
- [ ] Backup strategy
- [ ] API versioning clear
- [ ] Documentation published
- [ ] Changelog maintained

### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/money-api
server {
    listen 443 ssl http2;
    server_name api.babsyit.ch;

    ssl_certificate /etc/letsencrypt/live/api.babsyit.ch/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.babsyit.ch/privkey.pem;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /.well-known/ {
        proxy_pass http://localhost:8000;
    }
}
```

---

## 📊 API Analytics (Future)

### Metrics to Track

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram

api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)
```

### Grafana Dashboard

- Request Rate per Endpoint
- Error Rate
- Response Time P50/P95/P99
- Active Users
- Most Used Endpoints

---

## 🎯 API-First Best Practices

### 1. Design First
- Define OpenAPI spec first
- Review with team
- Generate code from spec

### 2. Consistency
- Use REST conventions
- Consistent naming
- Standard error codes

### 3. Documentation
- Keep docs updated
- Provide examples
- Version breaking changes

### 4. Security
- Always HTTPS
- Rate limiting
- Input validation
- Output encoding

### 5. Performance
- Caching headers
- Compression
- Pagination
- Field selection

### 6. Monitoring
- Log all requests
- Track errors
- Alert on anomalies
- Performance metrics

---

## 🔮 Future API Features

### GraphQL Support (v2.0)

```graphql
query {
  accounts {
    id
    name
    balance
    transactions(limit: 10) {
      id
      amount
      description
    }
  }
}
```

### WebSocket API (v2.0)

```javascript
const ws = new WebSocket('wss://money.babsyit.ch/ws')

ws.onmessage = (event) => {
  const update = JSON.parse(event.data)
  if (update.type === 'NEW_TRANSACTION') {
    console.log('New transaction:', update.data)
  }
}
```

### Webhooks (v1.2)

```json
POST https://your-server.com/webhook
{
  "event": "transaction.created",
  "data": {
    "id": 123,
    "amount": -50.00,
    "account_id": 1
  },
  "timestamp": "2024-12-07T12:34:56Z"
}
```

---

## 📚 Additional Resources

- **OpenAPI Spec:** http://localhost:8000/openapi.json
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Postman Collection:** [Export from OpenAPI]
- **Code Examples:** See `/docs` for all endpoints

---

## 💡 Pro Tips

### 1. Use API Client Libraries
```bash
npm install axios
pip install httpx
```

### 2. Cache Responses
```javascript
const cache = new Map()
const getCached = async (url) => {
  if (cache.has(url)) return cache.get(url)
  const data = await fetch(url).then(r => r.json())
  cache.set(url, data)
  return data
}
```

### 3. Batch Requests (Future)
```json
POST /api/v1/batch
{
  "requests": [
    {"method": "GET", "path": "/accounts"},
    {"method": "GET", "path": "/transactions"}
  ]
}
```

### 4. Field Selection (Future)
```
GET /api/v1/accounts?fields=id,name,balance
```

---

**Die API ist das Herz von Money Manager!**  
Alles andere ist nur ein Interface dazu. 🚀
