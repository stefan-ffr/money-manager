# Money Manager

**Self-hosted Personal Finance Management mit Federation Support**

[![Build Status](https://github.com/stefan-ffr/money-manager/actions/workflows/docker-build.yml/badge.svg)](https://github.com/stefan-ffr/money-manager/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Was ist Money Manager?

Money Manager ist eine selbst-gehostete Lösung zur Verwaltung persönlicher Finanzen mit einzigartigen Features:

- 💰 **Multi-Account Management** - Giro, Sparkonto, Kreditkarte, Bargeld
- 🤖 **Telegram Bot** - Ausgaben per Chat erfassen mit OCR
- 🏦 **Bank Import** - Auto-Import von Schweizer Banken (CSV)
- 🌐 **Federation** - Teile Konten mit anderen Instanzen
- 📊 **EasyTax Export** - Steuer-Export für Schweiz
- 🔐 **Security First** - Lokale Datenhaltung, RSA-verschlüsselt

## Quick Start

```bash
# Repository klonen
git clone https://github.com/stefan-ffr/money-manager.git
cd money-manager

# Environment konfigurieren
cp .env.example .env

# Starten
docker compose up -d
```

🌐 **Frontend:** http://localhost:3000
📡 **Backend API:** http://localhost:8000
📖 **API Docs:** http://localhost:8000/docs

## 📚 Dokumentation

Die vollständige Dokumentation findest du im **[Wiki](https://github.com/stefan-ffr/money-manager/wiki)**:

- 🚀 [Quick Start Guide](https://github.com/stefan-ffr/money-manager/wiki/Quickstart)
- 📚 [Features Overview](https://github.com/stefan-ffr/money-manager/wiki/Features)
- 🏗️ [Architecture](https://github.com/stefan-ffr/money-manager/wiki/Architecture)
- 🔒 [Security](https://github.com/stefan-ffr/money-manager/wiki/Security)
- 🗺️ [Roadmap](https://github.com/stefan-ffr/money-manager/wiki/Roadmap)

## Tech Stack

- **Backend:** FastAPI (Python 3.12+) + PostgreSQL 16
- **Frontend:** React 18 + TypeScript + Tailwind CSS
- **Deployment:** Docker Compose
- **CI/CD:** GitHub Actions

## Features Highlights

### 🤖 Telegram Bot
```
Sende Foto/PDF → Bot erstellt Buchung → Bestätige per Button
```

### 🏦 Bank Import
Unterstützt: PostFinance, UBS, Raiffeisen, ZKB, Credit Suisse
- Auto-Matching per IBAN
- Duplicate Detection
- CSV Upload

### 🌐 Federation (wie Mastodon)
```
Deine Instanz ←→ RSA Verschlüsselt ←→ Freunde's Instanz
```
- Cross-Instance Shared Accounts
- Signierte Requests
- Public Key Discovery

## Status

✅ **v1.0 - Production Ready**

Alle Core Features sind implementiert und getestet.
Nächste Version: **v1.1** mit Passkey Auth & Mirror Instances

## Contributing

Contributions sind willkommen! Siehe [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - siehe [LICENSE](LICENSE)

## Support

- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/stefan-ffr/money-manager/issues)
- 💬 **Diskussionen:** [GitHub Discussions](https://github.com/stefan-ffr/money-manager/discussions)
- 📖 **Dokumentation:** [Wiki](https://github.com/stefan-ffr/money-manager/wiki)

---

Made with ❤️ for self-hosted finance management
