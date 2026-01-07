# Money Manager - Roadmap

## Aktueller Status: v1.0 🚀

Alle Features in v1.0 sind **implementiert und produktionsreif**!

---

## ✅ v1.0 - Core Features (FERTIG)

### Basis Funktionalität
- [x] Multi-Account Management (Giro, Sparkonto, Kreditkarte, Bargeld)
- [x] Transaction CRUD mit REST API
- [x] Receipt Upload & Storage System
- [x] PostgreSQL Database mit SQLAlchemy
- [x] Docker Compose Setup für alle Services
- [x] GitHub Actions für automatisches Container-Building

### Bank Integration 🆕
- [x] **CSV Import mit Auto-Matching** - System findet automatisch richtiges Konto
- [x] **5 Schweizer Banken** - PostFinance, UBS, Raiffeisen, ZKB, Credit Suisse
- [x] **IBAN-based Matching** - Konto einmal markieren, immer automatisch
- [x] **Duplicate Detection** - Keine doppelten Einträge
- [x] **Bank Import API** - Vollständig über API steuerbar

### Telegram Integration
- [x] Telegram Bot für Receipt Upload
- [x] OCR Support (Tesseract/Poppler bereit)
- [x] Provisorische Buchungen mit Bestätigung
- [x] **🔴 Automatische Einträge rot markiert**
- [x] Inline Buttons für Quick Actions

### Federation & Shared Accounts
- [x] **RSA Public/Private Key Encryption (wie SSH)**
- [x] Inter-Instanz Communication
- [x] Signierte Requests mit Verification
- [x] Public Key Discovery (/.well-known/money-instance)
- [x] Gemeinschaftskonten (Shared Accounts)
- [x] **🌍 Cross-Instance Shared Accounts** - Member auf verschiedenen Instanzen!
- [x] Split Transactions mit verschiedenen Modi
- [x] Balance Calculation & Settlement Algorithm

### Multi-Currency 🆕
- [x] **15+ Währungen** - CHF, EUR, USD, THB, GBP, JPY, CNY, AUD, CAD, SGD, INR, BRL, ZAR, BTC, ETH
- [x] **Korrekte Formatierung** - Länderspezifische Symbole und Trennzeichen
- [x] **Currency API** - Dynamisch geladen von Backend

### EasyTax Integration
- [x] Category System mit EasyTax Mapping
- [x] CSV Export im EasyTax Format
- [x] Configurable Category Mappings

### Frontend
- [x] React + TypeScript + Tailwind CSS
- [x] Dashboard mit Übersicht
- [x] Transaction List mit roter Markierung
- [x] Responsive Navigation
- [x] **Umfassende Settings Page mit 6 Tabs**
- [x] **API-First Architecture** - Alles API-basiert

### Dokumentation
- [x] Ausführliches README.md
- [x] QUICKSTART.md (5-Minuten Setup)
- [x] SECURITY.md (Alle Sicherheitsaspekte)
- [x] FEATURES.md (Feature-Erklärungen)
- [x] PROJECT_STRUCTURE.md
- [x] CONTRIBUTING.md
- [x] **API_ARCHITECTURE.md** - Vollständige API Dokumentation
- [x] **API_EXAMPLES.md** - Praktische Beispiele
- [x] **CROSS_INSTANCE_SHARED_ACCOUNTS.md** - Cross-Instance Guide
- [x] **BANK_IMPORT.md** - Bank Import Guide
- [x] **SETTINGS_GUIDE.md** - Settings Documentation

---

## 🔧 v1.1 - Security & Sync (Q1 2025)

### Passkey Authentication (WebAuthn) ✅ IMPLEMENTIERT
- [x] Backend WebAuthn Integration
  - [x] User Model erweitern
  - [x] Registration/Login Endpoints
  - [x] Credential Storage
- [x] Frontend Passkey Flow
  - [x] Registration UI
  - [x] Login UI mit Biometrie
  - [x] Multi-Device Support
- [x] Session Management
  - [x] JWT Tokens
  - [x] Refresh Token Logic
  - [x] Timeout Handling

**Priority:** HIGH
**Reason:** Essenziell für Production Security
**Status:** ✅ Vollständig implementiert (2025-01-07)
**Details:**
- Backend: WebAuthn 2.2.0 mit vollständiger Registration/Login Flow
- Frontend: @simplewebauthn/browser 9.0.1 mit React Context
- JWT-basierte Session Management
- Protected Routes mit automatischer Redirect
- User-freundliche Login/Register UI mit Biometrie-Support

### Mirror Instances (Replication)
- [ ] MirrorInstance Model & API
  - [ ] Instance Configuration
  - [ ] Sync Direction Settings
  - [ ] Priority Management
- [ ] Replication Service
  - [ ] Bidirectional Sync Algorithm
  - [ ] Conflict Detection & Resolution
  - [ ] Delta Sync (nur Changes)
- [ ] Background Sync Scheduler
  - [ ] Automatic Sync Jobs
  - [ ] Manual Trigger Endpoint
  - [ ] Sync Status Monitoring
- [ ] Conflict Resolution UI
  - [ ] Manual Conflict Review
  - [ ] Strategy Selection
  - [ ] History View

**Priority:** HIGH  
**Reason:** Backup & High Availability  
**Implementierung:** Design in SECURITY.md komplett

### Advanced Security
- [ ] Replay Protection
  - [ ] Timestamp Validation
  - [ ] Nonce Storage & Checking
  - [ ] Request Expiry (5min window)
- [ ] Rate Limiting
  - [ ] API Request Limits
  - [ ] Per-User Quotas
  - [ ] Brute-Force Protection
- [ ] Audit Logs
  - [ ] All API Calls logged
  - [ ] User Actions tracked
  - [ ] Export für Compliance
- [ ] 2FA Support
  - [ ] TOTP (Google Authenticator)
  - [ ] Backup Codes
  - [ ] SMS Fallback (optional)

**Priority:** MEDIUM  
**Reason:** Production Hardening

---

## 📊 v1.2 - Bank Integration (Q2 2025)

### ISO 20022 Parser
- [ ] camt.053 (Account Statement) Parser
  - [ ] XML Parsing
  - [ ] Transaction Extraction
  - [ ] Automatic Account Mapping
- [ ] camt.054 (Debit/Credit Notification)
- [ ] pain.001 (Payment Initiation) Support
- [ ] Validation & Error Handling

**Priority:** HIGH  
**Reason:** Standard für CH Banken

### Enhanced CSV Import
- [ ] Bank-Specific Parsers
  - [ ] PostFinance Format
  - [ ] UBS Format
  - [ ] Raiffeisen Format
  - [ ] ZKB Format
  - [ ] Credit Suisse Format
- [ ] Custom CSV Mapping UI
  - [ ] Column Mapping Dialog
  - [ ] Date Format Detection
  - [ ] Amount Recognition
  - [ ] Preview before Import
- [ ] Duplicate Detection
  - [ ] Hash-based Checking
  - [ ] Manual Review
  - [ ] Auto-Skip Option

**Priority:** HIGH  
**Reason:** User Convenience

### eBill Integration
- [ ] eBill API Connection
  - [ ] Authentication
  - [ ] Bill Retrieval
  - [ ] Status Updates
- [ ] Automatic Bill Import
  - [ ] Scheduled Fetch
  - [ ] Notification System
  - [ ] Payment Tracking

**Priority:** MEDIUM  
**Reason:** Nice-to-Have für CH

### Automatic Categorization (ML)
- [ ] Training Data Collection
  - [ ] User-confirmed Categories
  - [ ] Description Patterns
  - [ ] Merchant Recognition
- [ ] Simple ML Model
  - [ ] Naive Bayes or Decision Tree
  - [ ] Scikit-learn Integration
  - [ ] Regular Re-training
- [ ] Suggestion System
  - [ ] Confidence Scores
  - [ ] User Feedback Loop
  - [ ] Learning from Corrections

**Priority:** LOW  
**Reason:** Feature Creep Risk

---

## 💰 v1.3 - Advanced Features (Q3 2025)

### Budget Tracking
- [ ] Budget Configuration
  - [ ] Monthly/Yearly Budgets
  - [ ] Per-Category Limits
  - [ ] Rollover Settings
- [ ] Real-time Tracking
  - [ ] Spending vs Budget
  - [ ] Visual Progress Bars
  - [ ] Warning Thresholds
- [ ] Budget Reports
  - [ ] Monthly Summary
  - [ ] Trend Analysis
  - [ ] Forecasting

**Priority:** MEDIUM  
**Reason:** User Request

### Multi-Currency Support
- [ ] Currency Management
  - [ ] Exchange Rate API Integration
  - [ ] Historical Rates Storage
  - [ ] Manual Rate Override
- [ ] Multi-Currency Accounts
  - [ ] Currency per Account
  - [ ] Conversion Tracking
  - [ ] Total Balance in Base Currency
- [ ] Foreign Transaction Handling
  - [ ] Automatic Conversion
  - [ ] Fee Tracking
  - [ ] Exchange Gain/Loss

**Priority:** MEDIUM  
**Reason:** International Users

### Advanced Reports & Analytics
- [ ] Custom Report Builder
  - [ ] Date Range Selection
  - [ ] Filter by Categories/Accounts
  - [ ] Export Options (PDF, Excel, CSV)
- [ ] Visualization Dashboard
  - [ ] Spending by Category (Pie Chart)
  - [ ] Income vs Expenses (Bar Chart)
  - [ ] Balance Trend (Line Chart)
  - [ ] Monthly Comparison
- [ ] Savings Goals
  - [ ] Goal Definition
  - [ ] Progress Tracking
  - [ ] Projection Calculation

**Priority:** MEDIUM  
**Reason:** Power User Feature

### Recurring Transactions
- [ ] Recurring Transaction Setup
  - [ ] Frequency (Daily, Weekly, Monthly, Yearly)
  - [ ] End Date or Never
  - [ ] Amount Variation Rules
- [ ] Automatic Creation
  - [ ] Background Job
  - [ ] Notification before Creation
  - [ ] Manual Review Option
- [ ] Template Management
  - [ ] Save as Template
  - [ ] Edit Templates
  - [ ] Apply Template

**Priority:** HIGH  
**Reason:** Miete, Versicherungen, etc.

---

## 📱 v2.0 - Mobile & Platform (Q4 2025)

### Mobile App (React Native)
- [ ] Cross-Platform App
  - [ ] iOS Support
  - [ ] Android Support
  - [ ] Shared Codebase with Web
- [ ] Mobile-Specific Features
  - [ ] Camera for Receipts
  - [ ] Push Notifications
  - [ ] Biometric Auth
  - [ ] Offline Mode
- [ ] App Store Deployment
  - [ ] Apple App Store
  - [ ] Google Play Store
  - [ ] Auto-Update Mechanism

**Priority:** HIGH  
**Reason:** Mobile-First Users

### PWA (Progressive Web App)
- [ ] Service Worker
  - [ ] Offline Caching
  - [ ] Background Sync
  - [ ] Push Notifications
- [ ] Install Prompt
  - [ ] Add to Home Screen
  - [ ] App Icon
  - [ ] Splash Screen

**Priority:** MEDIUM  
**Reason:** Schnellere Alternative zu Native App

### Desktop Apps
- [ ] Electron Wrapper
  - [ ] Windows .exe
  - [ ] macOS .dmg
  - [ ] Linux .AppImage
- [ ] Native Features
  - [ ] System Tray Integration
  - [ ] Keyboard Shortcuts
  - [ ] File System Access

**Priority:** LOW  
**Reason:** Niche Use Case

---

## 🔮 v3.0 - Advanced Ecosystem (2026)

### Investment Tracking
- [ ] Portfolio Management
  - [ ] Stock/ETF Tracking
  - [ ] Crypto Support
  - [ ] Real-time Prices
- [ ] Performance Analytics
  - [ ] ROI Calculation
  - [ ] Diversification Analysis
  - [ ] Tax Loss Harvesting

**Priority:** LOW  
**Reason:** Different Product Focus

### Business Features
- [ ] Invoice Generation
  - [ ] PDF Creation
  - [ ] QR-Bill Integration
  - [ ] Email Sending
- [ ] VAT Handling
  - [ ] MWST Calculation
  - [ ] Quarterly Reports
  - [ ] Export für Steuerberater
- [ ] Multi-User Access
  - [ ] Role-Based Permissions
  - [ ] Team Collaboration
  - [ ] Activity Log

**Priority:** LOW  
**Reason:** B2B Pivot

### AI Features
- [ ] Smart Predictions
  - [ ] Spending Forecast
  - [ ] Savings Opportunities
  - [ ] Bill Reminders
- [ ] Natural Language Interface
  - [ ] "Show me spending last month"
  - [ ] "How much did I spend on food?"
  - [ ] ChatGPT-style Interaction
- [ ] Anomaly Detection
  - [ ] Unusual Transactions
  - [ ] Fraud Detection
  - [ ] Budget Overrun Warnings

**Priority:** VERY LOW  
**Reason:** Hype vs Reality

---

## 📈 Metrics & KPIs

### v1.1 Target Metrics
- [ ] 100% Test Coverage für Security Features
- [ ] <200ms API Response Time (P95)
- [ ] 99.9% Uptime with Mirror Failover
- [ ] Zero Data Loss in Sync

### v1.2 Target Metrics
- [ ] Support for 5+ Swiss Banks
- [ ] <5 min Average Import Time
- [ ] 90% Auto-Categorization Accuracy

### v2.0 Target Metrics
- [ ] 10,000+ Mobile Downloads
- [ ] <100MB App Size
- [ ] Offline Mode with 7-day Sync

---

## 🎯 Development Priorities

### HIGH Priority (Next 3 Months)
1. **Passkey Authentication** - Production Security
2. **Mirror Instances** - Data Safety
3. **Recurring Transactions** - User Convenience
4. **ISO 20022 Parser** - Swiss Bank Standard

### MEDIUM Priority (3-6 Months)
1. Budget Tracking
2. Multi-Currency
3. Enhanced CSV Import
4. eBill Integration

### LOW Priority (6-12 Months)
1. Mobile App
2. Advanced Analytics
3. Investment Tracking

---

## 🤝 Community Contributions

Wir freuen uns über Beiträge! Hier sind Bereiche wo Help willkommen ist:

### Easy Contributions
- [ ] Translations (FR, IT, EN)
- [ ] Bank CSV Parser für neue Banken
- [ ] Category Templates
- [ ] Documentation Improvements
- [ ] Bug Reports & Testing

### Medium Contributions
- [ ] Frontend Components
- [ ] API Endpoints
- [ ] Database Migrations
- [ ] Unit Tests

### Advanced Contributions
- [ ] ML Model Training
- [ ] Mobile App Development
- [ ] Performance Optimization
- [ ] Security Audits

Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Details.

---

## 📝 Decision Log

### Warum Passkeys statt Passwörter?
- **Entscheidung:** Passkeys (WebAuthn) als primäre Auth
- **Grund:** Phishing-Resistent, Biometrisch, Keine Passwörter
- **Datum:** 2024-12-07

### Warum Mirror Instances statt Cloud Backup?
- **Entscheidung:** Self-Hosted Mirror Instances
- **Grund:** Volle Kontrolle, Privacy, kein Vendor Lock-in
- **Datum:** 2024-12-07

### Warum React Native für Mobile?
- **Entscheidung:** React Native für v2.0
- **Grund:** Code Sharing mit Web, große Community
- **Alternativen:** Flutter (rejected: neue Language), Native (rejected: 2x Development)
- **Datum:** TBD

---

## 🚀 Getting Started with Development

Möchtest du an der Roadmap mitarbeiten?

```bash
# 1. Fork & Clone
git clone https://github.com/DEIN-USERNAME/money-manager.git

# 2. Pick ein Feature von Roadmap
# z.B. "Passkey Authentication"

# 3. Erstelle Branch
git checkout -b feature/passkey-auth

# 4. Entwickle & Teste
docker compose up -d
# ... code ...
pytest backend/tests/

# 5. Pull Request erstellen
git push origin feature/passkey-auth
```

---

## 📚 Related Documents

- [README.md](README.md) - Hauptdokumentation
- [SECURITY.md](SECURITY.md) - Sicherheitskonzept
- [FEATURES.md](FEATURES.md) - Feature-Übersicht
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution Guide

---

**Letzte Aktualisierung:** 2024-12-07  
**Nächstes Review:** 2025-03-01
