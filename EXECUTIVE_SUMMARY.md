# Money Manager - Executive Summary

## 🎯 Was ist Money Manager?

**Self-hosted Personal Finance System für die Schweiz** - Open Source, Privacy-First, Federation-Enabled

### In 3 Sätzen:
1. **Verwalte deine Finanzen selbst** - Multi-Account Management, Bank CSV Import, EasyTax Export
2. **Teile Kosten mit anderen** - WG-Konten, Vereinskassen über mehrere Instanzen hinweg
3. **Komplett API-basiert** - Nutze Web, Mobile (future), CLI oder Automation

---

## ⚡ Kern-Features (v1.0 - PRODUKTIONSREIF)

### 💰 Basis Finanzen
```
✅ Multi-Account Management (Giro, Sparkonto, Kreditkarte, Bargeld)
✅ Transaktionen mit Belegen (PDF/Foto)
✅ Kategorien mit EasyTax-Mapping
✅ 15+ Währungen (CHF, EUR, USD, THB, BTC, etc.)
✅ Dashboard & Reports
```

### 🏦 Bank Integration
```
✅ CSV Import für 5 Schweizer Banken (PostFinance, UBS, Raiffeisen, ZKB, CS)
✅ Automatisches Konto-Matching via IBAN
✅ Duplicate Detection
✅ Alle Imports rot markiert für Review
```

### 🌐 Federation & Shared Accounts
```
✅ Cross-Instance Shared Accounts (WG über mehrere Server)
✅ RSA-verschlüsselte Inter-Instanz Kommunikation
✅ Smart Splitting (equal, percentage, custom)
✅ Automatische Balance-Berechnung
✅ Settlement-Algorithmus
```

### 📱 Automation
```
✅ Telegram Bot für Belege (mit OCR)
✅ Vollständige REST API
✅ Webhook-ready
✅ n8n/Zapier Integration möglich
```

### 🔐 Security
```
✅ RSA Public/Private Key Encryption (wie SSH)
✅ Alle Auto-Entries rot markiert (Telegram, Federation, CSV)
✅ Passkey Authentication (Code ready, v1.1)
✅ Mirror Instances für Backup (Design ready, v1.1)
```

---

## 🎨 Architektur

### API-First Design (wie Cloudflare)
```
         FastAPI REST API
              │
    ┌─────────┼─────────┐
    │         │         │
  React    Mobile    CLI/Scripts
   Web     (v2.0)    
```

**Vorteil:** Frontend ist nur ein Consumer. API kann von überall genutzt werden.

### Tech Stack
```
Backend:  FastAPI + SQLAlchemy + PostgreSQL
Frontend: React + TypeScript + Tailwind CSS
Bot:      Python Telegram Bot
Deploy:   Docker Compose + Traefik
Docs:     OpenAPI/Swagger (auto-generated)
```

---

## 💡 Use Cases

### 1️⃣ Persönliche Finanzen
```
Stefan verwaltet 4 Konten:
- PostFinance Giro
- UBS Sparkonto
- ZKB Kreditkarte
- Bargeld

Jeden Monat:
1. CSVs von Banken downloaden
2. Upload → System matcht automatisch
3. Kategorien prüfen
4. EasyTax Export für Steuern
```

### 2️⃣ WG Haushaltskasse
```
3 Personen, 3 verschiedene Money Manager Instanzen:
- Stefan@money.babsyit.ch
- Anna@money.example.com
- Tom@money.other.ch

Shared Account "WG Binningen":
- Miete CHF 1800 (Stefan zahlt)
- Split equal → jeder schuldet CHF 600
- Balance tracking über alle Instanzen
- Settlement monatlich
```

### 3️⃣ Vereinskasse
```
Feuerwehrverein Raura:
- 15 Members auf verschiedenen Instanzen
- Vereinsausgaben werden gesplittet
- Transparente Balance für alle
- Abrechnung an Generalversammlung
```

### 4️⃣ Familie Budget
```
Eltern + 2 Kinder:
- Familien-Shared-Account
- Ferien, Versicherungen, Haushalt
- Custom Splits (Eltern 80%, Kinder 20%)
- Kontinuierliches Settlement
```

---

## 📊 Zahlen & Fakten

```
68 Files total
29 Python Files
10 TypeScript Files
12 Dokumentationen

77 KB Tarball
100% Open Source (MIT License)
15+ Währungen
5 Schweizer Banken
∞ Accounts möglich
∞ Shared Accounts möglich
```

---

## 🚀 Getting Started

### Option 1: Quick Start (5 Minuten)
```bash
# Download
wget https://github.com/.../money-manager.tar.gz
tar -xzf money-manager.tar.gz
cd money-manager

# Setup
cp .env.example .env
# Edit .env mit deinen Daten

# Start
docker compose up -d

# Open
open http://localhost:3000
```

### Option 2: Production Deployment
```bash
# Mit Traefik + Let's Encrypt HTTPS
# Siehe DEPLOYMENT.md für Details

# Domain: money.babsyit.ch
# SSL: Automatic
# Backup: Mirror Instances
```

---

## 🎯 Warum Money Manager?

### ✅ Privacy First
```
- Self-Hosted (deine Daten auf deinem Server)
- Keine Cloud (außer du willst)
- Open Source (Code überprüfbar)
- DSGVO-konform
```

### ✅ Swiss Made (for Switzerland)
```
- EasyTax Export für Steuern
- Schweizer Banken (PostFinance, UBS, etc.)
- CHF als Standard-Währung
- Schweizer Datumsformat (DD.MM.YYYY)
```

### ✅ API-First
```
- Alles über REST API steuerbar
- Web UI ist optional
- Automation-ready
- CLI Tools möglich
- Mobile App (v2.0)
```

### ✅ Federation
```
- WG-Konten über mehrere Server
- Keine zentrale Instanz nötig
- RSA-verschlüsselt
- Decentralized
```

---

## 📈 Roadmap Highlights

### v1.1 (Q1 2025) - Security & Sync
```
⏳ Passkey Authentication (Code ready!)
⏳ Mirror Instances (Design ready!)
⏳ Replay Protection
⏳ Recurring Transactions
```

### v1.2 (Q2 2025) - Advanced Bank Integration
```
⏳ ISO 20022 camt.053 Parser (Universal!)
⏳ eBill Integration
⏳ 10+ Schweizer Banken
⏳ ML Auto-Categorization
```

### v2.0 (Q4 2025) - Mobile & Multi-Currency
```
⏳ React Native Mobile App
⏳ Multi-Currency Support
⏳ Budget Tracking
⏳ Advanced Analytics
```

Vollständige Roadmap: [ROADMAP.md](ROADMAP.md)

---

## 🆚 Vergleich mit anderen Tools

| Feature | Money Manager | YNAB | Splitwise | Firefly III |
|---------|--------------|------|-----------|-------------|
| Self-Hosted | ✅ | ❌ | ❌ | ✅ |
| Federation | ✅ | ❌ | ❌ | ❌ |
| Cross-Instance Shared | ✅ | ❌ | ❌ | ❌ |
| Swiss Banks | ✅ | ❌ | ❌ | ⚠️ |
| API-First | ✅ | ⚠️ | ⚠️ | ✅ |
| Open Source | ✅ | ❌ | ❌ | ✅ |
| Telegram Bot | ✅ | ❌ | ❌ | ❌ |
| Multi-Currency | ✅ | ✅ | ✅ | ✅ |
| EasyTax Export | ✅ | ❌ | ❌ | ❌ |
| Price | FREE | $99/year | Free | FREE |

---

## 🎓 Dokumentation

### Für Anfänger
```
README.md           - Übersicht & Installation
QUICKSTART.md       - 5-Minuten Setup
FEATURES.md         - Was kann das System?
```

### Für Fortgeschrittene
```
API_ARCHITECTURE.md - API Design
API_EXAMPLES.md     - curl/Python Beispiele
BANK_IMPORT.md      - Bank Integration
CROSS_INSTANCE_SHARED_ACCOUNTS.md - Federation Guide
```

### Für Admins
```
SECURITY.md         - Sicherheitskonzept
DEPLOYMENT.md       - Production Setup
PROJECT_STRUCTURE.md - Code Organisation
```

### Für Entwickler
```
CONTRIBUTING.md     - Contribution Guide
ROADMAP.md          - Feature Planung
OpenAPI Docs        - http://localhost:8000/docs
```

---

## 🤝 Support & Community

### Fragen?
```
📖 Dokumentation lesen
🐛 GitHub Issues erstellen
💬 Discussions auf GitHub
📧 Email an maintainer
```

### Beitragen?
```
🐛 Bug Reports
📝 Dokumentation verbessern
🔧 Features implementieren
🌍 Translations (FR, IT, EN)
🏦 Neue Banken hinzufügen
```

Siehe [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📝 License

**MIT License** - Komplett frei nutzbar, auch kommerziell.

```
- ✅ Private Nutzung
- ✅ Kommerzielle Nutzung
- ✅ Modifikation
- ✅ Distribution
- ✅ Sub-Licensing
```

---

## 🎉 Status

```
✅ v1.0 PRODUKTIONSREIF
✅ Alle Core Features implementiert
✅ Vollständig dokumentiert
✅ Docker-ready
✅ API-First
✅ Security-hardened
✅ Bank Integration
✅ Federation enabled
```

**Ready to deploy!** 🚀

---

## 📞 Quick Links

- **Demo:** http://demo.money-manager.example.com (coming soon)
- **Docs:** http://localhost:8000/docs
- **GitHub:** https://github.com/yourusername/money-manager
- **Issues:** https://github.com/yourusername/money-manager/issues

---

**Money Manager - Self-Hosted Personal Finance. Privacy First. Swiss Made. Federation Enabled.**

Version 1.0 | December 2024 | MIT License
