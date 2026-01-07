# Money Manager - TL;DR

## Was ist das?
**Self-hosted Personal Finance für die Schweiz mit Federation**

## 3 Kern-Features
1. **Bank Integration** - CSV Import für 5 CH Banken mit Auto-Matching
2. **Cross-Instance Shared Accounts** - WG-Konten über mehrere Server
3. **API-First** - Alles über REST API (wie Cloudflare)

## Quick Facts
```
✅ 69 Files, 13 Dokumentationen
✅ 15+ Währungen (CHF, EUR, USD, THB, BTC...)
✅ 5 Schweizer Banken (PostFinance, UBS, Raiffeisen, ZKB, CS)
✅ RSA-verschlüsselte Federation
✅ Telegram Bot mit OCR
✅ Docker-ready
✅ MIT License
✅ PRODUKTIONSREIF
```

## In 5 Minuten starten
```bash
tar -xzf money-manager.tar.gz
cd money-manager
cp .env.example .env
docker compose up -d
open http://localhost:3000
```

## Hauptfunktionen

### Persönliche Finanzen
- Multi-Account Management
- Bank CSV Import (auto-matching!)
- EasyTax Export
- Receipt Management
- 15+ Währungen

### Team Features
- WG-Konten über Instanzen
- Vereinskassen
- Smart Split (equal, %, custom)
- Auto Balance Tracking
- Settlement Algorithmus

### Automation
- Telegram Bot
- REST API (komplett)
- Webhook-ready
- n8n/Zapier möglich

### Security
- RSA Encryption (wie SSH)
- Auto-Entries rot markiert
- Passkey ready (v1.1)
- Mirror Instances (v1.1)

## Use Cases

**Privat:** 4 Konten, monatlicher CSV Import, EasyTax für Steuern

**WG:** 3 Personen auf 3 Servern, Miete splitten, monatliches Settlement

**Verein:** 15+ Members, Vereinsausgaben transparent, jährliche Abrechnung

## Support
- **Docs:** EXECUTIVE_SUMMARY.md (ausführlich)
- **Quick Start:** QUICKSTART.md (5 min)
- **API:** http://localhost:8000/docs
- **Examples:** API_EXAMPLES.md

## Roadmap
- **v1.0** ✅ FERTIG (jetzt!)
- **v1.1** Passkey + Mirrors + Recurring (Q1 2025)
- **v1.2** ISO 20022 + eBill + ML (Q2 2025)
- **v2.0** Mobile App + Multi-Currency (Q4 2025)

## Warum Money Manager?

✅ **Privacy First** - Deine Daten auf deinem Server
✅ **Swiss Made** - EasyTax, CH Banken, CHF
✅ **API-First** - Web UI optional, alles über API
✅ **Federation** - WG-Konten über Server-Grenzen
✅ **Open Source** - MIT License, komplett frei

---

**80 KB | 69 Files | MIT License | Ready to Deploy**

Start: `docker compose up -d`
Docs: `EXECUTIVE_SUMMARY.md`
API: `http://localhost:8000/docs`
