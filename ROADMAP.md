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

### OAuth2/OIDC Integration (Authentik, Keycloak) ✅ IMPLEMENTIERT
- [x] Backend OAuth2 Configuration
  - [x] Authlib Integration
  - [x] OAuth Configuration in Settings
  - [x] Authorization & Token Endpoints
  - [x] Userinfo Endpoint Integration
- [x] Frontend OAuth Support
  - [x] OAuth Login Flow
  - [x] Callback Handler
  - [x] State Management für CSRF Protection
- [x] Multi-Provider Support
  - [x] Authentik Configuration
  - [x] Keycloak Configuration
  - [x] Generic OIDC Support

**Priority:** MEDIUM
**Reason:** Enterprise SSO Integration
**Status:** ✅ Vollständig implementiert (2025-01-07)
**Details:**
- Backend: Authlib 1.3.0 mit OAuth2/OIDC Support
- Frontend: OAuth Login Option neben Passkeys
- Support für Authentik, Keycloak und generische OIDC Provider
- Automatische User-Erstellung bei OAuth Login
- CSRF-geschützt mit State Parameter

### Progressive Web App (PWA) ✅ IMPLEMENTIERT
- [x] Web App Manifest
  - [x] App Icons (192px, 512px)
  - [x] App Metadata
  - [x] Display Mode Standalone
- [x] Service Worker
  - [x] Offline Cache Strategy
  - [x] Network-First für API
  - [x] Cache-First für Static Assets
  - [x] Background Sync Vorbereitung
- [x] Installation
  - [x] Install Prompt Component
  - [x] iOS Installation Instructions
  - [x] Android/Desktop Auto-Prompt
- [x] PWA Optimierung
  - [x] Meta Tags für alle Plattformen
  - [x] Apple Touch Icons
  - [x] Theme Color
  - [x] Viewport Optimierung

**Priority:** HIGH
**Reason:** Mobile-First User Experience
**Status:** ✅ Vollständig implementiert (2025-01-07)
**Details:**
- Installierbar auf Chrome, Edge, Safari (iOS/macOS)
- Offline-Support für bereits geladene Seiten
- App-like Experience auf Smartphones
- Smart Install Prompt (nach Delay, dismissable)
- Funktioniert ohne App Store

### Mirror Instances (Replication) ✅ IMPLEMENTIERT
- [x] MirrorInstance Model & API
  - [x] Instance Configuration
  - [x] Sync Direction Settings (push, pull, bidirectional)
  - [x] Priority Management
- [x] Replication Service
  - [x] Bidirectional Sync Algorithm
  - [x] Conflict Detection & Resolution
  - [x] Delta Sync (nur Changes seit last_sync)
- [x] Background Sync Scheduler
  - [x] Automatic Sync Jobs (APScheduler)
  - [x] Manual Trigger Endpoint
  - [x] Sync Status Monitoring
- [x] Conflict Resolution UI
  - [x] Manual Conflict Review (Sync Logs)
  - [x] Strategy Selection (last_write_wins, primary_wins, manual)
  - [x] History View & Management

**Priority:** HIGH
**Reason:** Backup & High Availability
**Status:** ✅ Vollständig implementiert (2025-01-07)
**Details:**
- Backend: MirrorInstance, SyncLog, ConflictResolution Models
- Replication Service mit bidirektionaler Sync-Logik
- APScheduler für Background Jobs (konfigurierbar per REPLICATION_SYNC_INTERVAL_MINUTES)
- Frontend: Komplette Mirror Management UI in Settings
- Konfliktauflösungsstrategien: last_write_wins, primary_wins, manual
- RSA-Signatur-Verifizierung für alle Sync-Operationen
- Automatische und manuelle Sync-Trigger

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

### Bank Reconciliation ✅ IMPLEMENTIERT
- [x] Reconciliation Models
  - [x] BankReconciliation Model (Sessions tracking)
  - [x] ReconciliationMatch Model (Individual matches)
  - [x] Relationship with Account and Transaction
- [x] Matching Algorithm
  - [x] Exact Match (100% confidence)
  - [x] Fuzzy Match (date ±2 days, amount exact, description similarity)
  - [x] Unmatched Detection (bank only, app only)
- [x] API Endpoints
  - [x] CSV Upload & Parse
  - [x] Automatic Matching
  - [x] Manual Resolution Actions
  - [x] Reconciliation History
- [x] Frontend UI
  - [x] CSV Upload Form
  - [x] Visual Comparison (Bank vs App side-by-side)
  - [x] Ampel-System (🟢 90%+, 🟡 70-90%, 🔴 <70%)
  - [x] Manual Actions (Accept, Create Transaction, Ignore)
  - [x] Balance Comparison
  - [x] Statistics Dashboard

**Priority:** HIGH
**Reason:** Essential for accuracy verification
**Status:** ✅ Vollständig implementiert (2025-01-07)
**Details:**
- Intelligenter Matching-Algorithmus (Date, Amount, Description)
- Visuelle Gegenüberstellung mit Confidence-Indikatoren
- Manuelle Editierbarkeit für alle Matches
- Unterstützt alle CH Bank CSV Formate via existing parsers
- Balance-Abgleich zwischen Bank und App
- Audit Trail für alle Reconciliations

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

## 💡 v1.4 - Performance & UX (Q3 2025)

### Performance Optimization
- [ ] Database Optimization
  - [ ] Query Performance Tuning
  - [ ] Index Optimization
  - [ ] Connection Pooling
  - [ ] Caching Layer (Redis)
- [ ] Frontend Performance
  - [ ] Code Splitting
  - [ ] Lazy Loading
  - [ ] Image Optimization
  - [ ] Bundle Size Reduction
- [ ] API Optimization
  - [ ] Response Compression
  - [ ] Pagination Improvements
  - [ ] Batch Endpoints
  - [ ] GraphQL Alternative (optional)

**Priority:** MEDIUM
**Reason:** Skalierbarkeit für mehr Benutzer

### Enhanced UX
- [ ] Dark Mode
  - [ ] Dark Theme Implementation
  - [ ] User Preference Storage
  - [ ] System Preference Detection
- [ ] Accessibility (a11y)
  - [ ] ARIA Labels
  - [ ] Keyboard Navigation
  - [ ] Screen Reader Support
  - [ ] WCAG 2.1 AA Compliance
- [ ] Internationalization
  - [ ] German (Existing)
  - [ ] French (FR-CH)
  - [ ] Italian (IT-CH)
  - [ ] English (EN)

**Priority:** MEDIUM
**Reason:** Benutzerfreundlichkeit & Inklusivität

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

## 🏛️ Money Manager Vereine - Separate Edition

> **Separate Variante für Schweizer Vereine** - Eigenständiges Repository mit Datenaustausch zur Standard-Edition

### 📋 Konzept: Zwei Editionen

**Money Manager (Standard Edition)**
- Persönliche Finanzverwaltung
- Gemeinschaftskonten (Shared Accounts)
- Bank Import & Reconciliation
- Multi-Currency & Federation
- PWA & Self-Hosted

**Money Manager Vereine (Vereins-Edition)**
- Alle Features der Standard-Edition
- **PLUS:** Mitgliederverwaltung
- **PLUS:** Vereinsspezifische Buchhaltung
- **PLUS:** OR-Compliance & GV-Support
- **PLUS:** QR-Rechnungen für Mitgliederbeiträge
- **PLUS:** Spendenverwaltung

### 🔄 Datenaustausch zwischen Editionen

#### Architektur-Prinzipien
1. **Shared Database Schema (Core Models)**
   - Beide Editionen nutzen die gleichen Core Models (Account, Transaction, Category, etc.)
   - Vereins-Edition erweitert diese mit zusätzlichen Models (Member, Membership, Donation, etc.)
   - Standard-Edition kann Transaktionen von Vereins-Edition importieren (ohne Vereins-Metadaten)

2. **Federation/Replication**
   - Bereits implementiertes Federation-System (RSA-Signatur, Public Key Discovery)
   - Vereine können mit privaten Instanzen Shared Accounts haben
   - Beispiel: Vorstandsmitglied hat private Instanz + Vereins-Instanz, beide synchronisiert

3. **Import/Export Schnittstellen**
   - CSV/JSON Export aus Vereins-Edition → Import in Standard-Edition
   - Bank Import Kompatibilität (beide nutzen gleiche Parser)
   - API-kompatibel: Gleiche REST Endpoints für Core Funktionen

#### Technische Implementierung

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│  Money Manager (Standard)       │       │  Money Manager Vereine          │
│                                 │       │                                 │
│  - Account                      │◄─────►│  - Account (inherited)          │
│  - Transaction                  │ RSA   │  - Transaction (inherited)      │
│  - Category                     │ Sign  │  - Category (inherited)         │
│  - User                         │       │  - User (inherited)             │
│  - Federation                   │       │  - Federation (inherited)       │
│                                 │       │                                 │
│                                 │       │  + Member                       │
│                                 │       │  + MembershipFee                │
│                                 │       │  + Donation                     │
│                                 │       │  + CostCenter                   │
│                                 │       │  + Project                      │
│                                 │       │  + Board                        │
│                                 │       │  + AssociationSettings          │
└─────────────────────────────────┘       └─────────────────────────────────┘
         │                                           │
         │                                           │
         └───────────────┬───────────────────────────┘
                         ▼
                 Shared Database Schema
                 (Core: alembic migrations)
```

#### API-Kompatibilität

**Gleiche Endpoints (100% kompatibel):**
- `/api/v1/accounts` - Account Management
- `/api/v1/transactions` - Transaction CRUD
- `/api/v1/categories` - Category Management
- `/api/v1/bank-import` - CSV Import
- `/api/v1/reconciliation` - Bank Reconciliation
- `/api/v1/federation` - Instance Discovery
- `/api/v1/replication` - Mirror Sync
- `/api/v1/auth` - Authentication (Passkeys, OAuth)

**Zusätzliche Endpoints (nur Vereine):**
- `/api/v1/members` - Member Management
- `/api/v1/memberships` - Membership Fees
- `/api/v1/donations` - Donation Management
- `/api/v1/cost-centers` - Cost Center Accounting
- `/api/v1/projects` - Project/Event Management
- `/api/v1/compliance` - OR Annual Reports
- `/api/v1/qr-invoices` - Swiss QR-Code Generation

### Repository-Struktur

**Empfohlene Struktur:**
```
money-manager/                    # Standard Edition (dieses Repo)
├── backend/
├── frontend/
├── docs/
└── README.md

money-manager-vereine/            # Vereine Edition (separates Repo)
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── __init__.py       # Importiert von Standard + Vereine
│   │   │   ├── member.py         # NEU: Vereine-spezifisch
│   │   │   ├── membership.py     # NEU: Vereine-spezifisch
│   │   │   └── donation.py       # NEU: Vereine-spezifisch
│   │   ├── api/
│   │   │   ├── members.py        # NEU: Vereine-spezifisch
│   │   │   └── ...
│   │   └── services/
│   │       ├── qr_invoice_service.py  # NEU: Vereine-spezifisch
│   │       └── ...
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Members.tsx       # NEU: Vereine-spezifisch
│   │   │   ├── Compliance.tsx    # NEU: Vereine-spezifisch
│   │   │   └── ...
│   │   └── components/
│   │       └── ...
├── docs/
│   ├── VEREINE_SETUP.md          # Setup-Guide für Vereine
│   ├── OR_COMPLIANCE.md          # OR-Jahresrechnung Guide
│   └── QR_INVOICE.md             # Swiss QR-Code Integration
└── README.md                      # Vereine-spezifische Doku
```

**Shared Code (via Git Submodule oder Package):**
- Option A: Git Submodule (Core Models als Submodule)
- Option B: Python Package (money-manager-core als PyPI Package)
- Option C: Code-Duplikation mit Manual Sync (einfacher, aber Wartungsaufwand)

### 🎯 Warum Separate Edition?

#### Vorteile
1. **Klare Trennung** - Standard bleibt schlank für Privatpersonen
2. **Spezialisierung** - Vereine-Features ohne Feature-Creep
3. **Unabhängige Entwicklung** - Verschiedene Release-Zyklen
4. **Unterschiedliche Zielgruppen** - Privat vs. Verein
5. **Separate Dokumentation** - Vereins-spezifische Guides
6. **Einfacheres Testing** - Keine Vereine-Tests in Standard-Edition

#### Nachteile (und Lösungen)
1. **Code-Duplikation** → Lösung: Shared Core Package
2. **Doppelte Wartung** → Lösung: API-Kompatibilität gewährleistet
3. **Migration Complex** → Lösung: Gleiche DB-Schema für Core Models

### 📅 Entwicklungsplan

**Phase 1: Foundation (Monat 1-2)**
- [ ] Separates Repository erstellen
- [ ] Core Models von Standard-Edition übernehmen
- [ ] Build-Pipeline aufsetzen (Docker, CI/CD)
- [ ] Basis-Frontend mit Standard-Features

**Phase 2: Vereine-Models (Monat 2-3)**
- [ ] Member, MembershipFee, Donation Models
- [ ] CostCenter, Project, Board Models
- [ ] Database Migrations
- [ ] API Endpoints für Vereins-Features

**Phase 3: Frontend (Monat 3-4)**
- [ ] Mitgliederverwaltung UI
- [ ] Beitragsverwaltung UI
- [ ] Kostenstellen & Projekte UI
- [ ] Dashboard für Vereine

**Phase 4: Compliance & QR (Monat 4-5)**
- [ ] OR-Jahresabschluss Generator
- [ ] Swiss QR-Code Integration
- [ ] GV-Unterlagen Export
- [ ] Revisor-Reports

**Phase 5: Testing & Docs (Monat 5-6)**
- [ ] End-to-End Testing
- [ ] Vereine-spezifische Dokumentation
- [ ] Setup-Guides für verschiedene Vereinstypen
- [ ] Beta-Testing mit echten Vereinen

### 🏛️ Feature-Roadmap: Vereine Edition

#### Mitgliederverwaltung
- [ ] Mitglieder-Modul
  - [ ] Mitglieder CRUD (Name, Adresse, Email, Telefon)
  - [ ] Mitgliedsnummern (automatisch generiert)
  - [ ] Mitgliedsstatus (Aktiv, Passiv, Ehrenmitglied, Ausgetreten)
  - [ ] Beitrittsdatum & Austrittsdatum
  - [ ] Kategorien (Aktivmitglied, Passivmitglied, Junioren, Senioren)
  - [ ] Notizen & Custom Fields
- [ ] Mitgliederbeiträge
  - [ ] Beitragstypen (Jahresbeitrag, Eintrittsbeitrag, Zusatzbeiträge)
  - [ ] Beitragsperioden (Jährlich, Halbjährlich, Quartalsweise)
  - [ ] Beitragskategorien nach Alter/Typ
  - [ ] Rabatte & Ermässigungen
  - [ ] Automatische Beitragsberechnung
- [ ] Zahlungsverwaltung
  - [ ] Offene Posten pro Mitglied
  - [ ] Mahnwesen (1. Mahnung, 2. Mahnung, Letzte Mahnung)
  - [ ] Zahlungserinnerungen per Email
  - [ ] QR-Rechnung Generierung (Swiss QR-Code)
  - [ ] Automatische Zuordnung von Zahlungseingängen

**Priority:** HIGH
**Reason:** Core Feature für Vereine

#### Vereinskassen-Buchhaltung
- [ ] Vereinsspezifische Kontenstruktur
  - [ ] Vereinskasse (Hauptkonto)
  - [ ] Sparkonto / Anlagekonto
  - [ ] Projektkassen (Events, Anlässe)
  - [ ] Fonds & Rückstellungen
- [ ] Kostenstellen
  - [ ] Kostenstellen definieren (z.B. "Jugendförderung", "Vereinsanlass", "Unterhalt")
  - [ ] Transaktionen Kostenstellen zuweisen
  - [ ] Kostenstellen-Reporting
  - [ ] Budget pro Kostenstelle
- [ ] Projekt-Buchhaltung
  - [ ] Projekte/Events erstellen (z.B. "Sommerfest 2025", "Jubiläum 50 Jahre")
  - [ ] Einnahmen & Ausgaben pro Projekt tracken
  - [ ] Projekt-Budget vs. Ist-Kosten
  - [ ] Erfolgsrechnung pro Projekt
- [ ] Vorstandsverwaltung
  - [ ] Vorstandsmitglieder mit Funktionen (Präsident, Kassier, Aktuar, etc.)
  - [ ] Amtsperioden
  - [ ] Unterschriftsberechtigungen
  - [ ] Sitzungsprotokolle (optional)

**Priority:** HIGH
**Reason:** Essentiell für professionelle Vereinsführung

#### Schweizer Vereins-Compliance
- [ ] Jahresabschluss nach OR (Obligationenrecht)
  - [ ] Bilanz (Aktiven / Passiven)
  - [ ] Erfolgsrechnung (Einnahmen / Ausgaben)
  - [ ] Anhang zur Jahresrechnung
  - [ ] Revisionsbericht-Vorlage
- [ ] Revisorenwesen
  - [ ] Revisoren erfassen
  - [ ] Kontrollstelle zuweisen
  - [ ] Revisionsbericht generieren
  - [ ] Revisions-Checkliste
- [ ] Budgetierung
  - [ ] Jahresbudget erstellen
  - [ ] Budget vs. Ist-Vergleich
  - [ ] Budget-Kategorien nach Vereinsbedürfnissen
  - [ ] Budgetvorschlag für Generalversammlung
- [ ] Generalversammlung (GV) Support
  - [ ] GV-Unterlagen Export
  - [ ] Jahresbericht-Generator
  - [ ] Mitgliederliste für Stimmrecht
  - [ ] Protokoll-Vorlagen

**Priority:** HIGH
**Reason:** Rechtliche Anforderungen in CH

#### Spendenverwaltung
- [ ] Spender-Management
  - [ ] Spender erfassen (Privatpersonen, Firmen)
  - [ ] Spendenhistorie pro Spender
  - [ ] Dauerspenden (monatlich, jährlich)
  - [ ] Spendenkategorien (Allgemein, Zweckgebunden)
- [ ] Spendenbescheinigungen
  - [ ] Automatische Spendenbescheinigung-Generierung
  - [ ] PDF Export mit Vereinsstempel
  - [ ] Sammelbestätigung Jahresende
  - [ ] ESTV-konforme Formulare (für Steuerabzug)
- [ ] Spenden-Tracking
  - [ ] Zweckgebundene Spenden verwalten
  - [ ] Spendenverwendung dokumentieren
  - [ ] Spenden-Reporting für Transparenz
  - [ ] Dankesschreiben-Vorlagen

**Priority:** MEDIUM
**Reason:** Wichtig für gemeinnützige Vereine

#### Vereins-Reporting
- [ ] Schweizer Vereins-Reports
  - [ ] Kassabericht (detailliert)
  - [ ] Jahresrechnung nach Schweizer Standard
  - [ ] Budget-Ist-Vergleich
  - [ ] Mitgliederstatistik (Zu-/Abgänge)
  - [ ] Beitragseinnahmen-Übersicht
  - [ ] Offene Posten Liste
- [ ] Export-Funktionen
  - [ ] PDF Export für GV-Unterlagen
  - [ ] Excel Export für Revisoren
  - [ ] CSV für Buchhaltungssoftware
  - [ ] Banana Accounting Export (beliebte CH Software)
- [ ] Dashboard für Vorstand
  - [ ] Vereinsvermögen Übersicht
  - [ ] Mitgliederzahl & Entwicklung
  - [ ] Offene Beiträge
  - [ ] Nächste Zahlungen
  - [ ] Budget-Status

**Priority:** HIGH
**Reason:** Vereinsvorstand braucht Transparenz

#### QR-Rechnung Integration (Swiss QR-Code)
- [ ] QR-Rechnung Generierung
  - [ ] Swiss QR-Code gemäss Standard
  - [ ] Strukturierte Referenznummer
  - [ ] IBAN & Zahlungsempfänger aus Vereinsdaten
  - [ ] Betrag & Währung (CHF/EUR)
  - [ ] Verwendungszweck (Mitgliederbeitrag, Spende, etc.)
- [ ] Massen-QR-Rechnung
  - [ ] Alle offenen Beiträge als QR-Rechnungen
  - [ ] PDF-Sammeldatei für Postversand
  - [ ] Email-Versand mit QR-Rechnung Anhang
- [ ] Zahlungsabgleich
  - [ ] Camt.054 Import (Zahlungsavise)
  - [ ] Automatische Zuordnung via QR-Referenz
  - [ ] Offene Posten automatisch schliessen

**Priority:** HIGH
**Reason:** Standard in CH seit 2020, sehr wichtig für Vereine

#### Vereins-Templates
- [ ] Vorlagen für Schweizer Vereine
  - [ ] Kontenplan-Vorlagen (Sportverein, Kulturverein, etc.)
  - [ ] Kategorie-Templates
  - [ ] Brief-Vorlagen (Zahlungserinnerung, Dankesschreiben)
  - [ ] Protokoll-Vorlagen (GV, Vorstandssitzung)
- [ ] Branchen-spezifisch
  - [ ] Sportverein (Trainerbeiträge, Turniere, Material)
  - [ ] Kulturverein (Konzerte, Ausstellungen, Mitgliederbeiträge)
  - [ ] Gemeinnütziger Verein (Spenden, Projekte)
  - [ ] Interessenverein (z.B. Quartierverein, Hobbyverein)

**Priority:** MEDIUM
**Reason:** Nice-to-have für schnellen Start

#### Multi-Tenant für Vereine
- [ ] Mandantenfähigkeit
  - [ ] Mehrere Vereine pro Instanz
  - [ ] Getrennte Buchhaltung pro Verein
  - [ ] Getrennte Mitgliederdaten
  - [ ] Zentrale Administration
- [ ] Rollen & Berechtigungen
  - [ ] Vorstand (voller Zugriff)
  - [ ] Kassier (Finanz-Zugriff)
  - [ ] Aktuar (Protokolle, Mitglieder)
  - [ ] Revisor (Read-Only Finanz)
  - [ ] Mitglied (eigene Daten ansehen)
- [ ] Datenschutz
  - [ ] DSGVO/FADP Compliance
  - [ ] Mitglieder-Einwilligungen
  - [ ] Datenexport für Mitglieder
  - [ ] Löschkonzept

**Priority:** LOW
**Reason:** Für Hosting-Provider oder Dachverbände

---

### 💡 Vereins-Use Cases

#### Use Case 1: Sportverein mit 150 Mitgliedern
**Anforderungen:**
- Mitgliederverwaltung mit Kategorien (Aktiv, Passiv, Junioren)
- Jahresbeitrag CHF 120.- (Erwachsene), CHF 60.- (Junioren)
- QR-Rechnungen per Email versenden
- Trainerbeiträge verwalten
- Event-Buchhaltung (Sommerfest, Jubiläum)
- Jahresrechnung für GV

**Lösung mit Vereine-Edition:**
- Mitglieder erfassen mit Kategorien
- Beitragstypen definieren
- Automatische QR-Rechnung-Generierung Ende Jahr
- Projekt "Sommerfest 2025" mit eigenem Budget
- Jahresabschluss-Export als PDF für GV

#### Use Case 2: Kulturverein mit Spenden
**Anforderungen:**
- 50 Mitglieder + 200 Spender
- Mitgliederbeiträge CHF 50.-
- Spendenverwaltung mit Bescheinigungen
- Konzert-Organisation (Ticket-Einnahmen)
- Gemeinnützig anerkannt (Steuerabzug)

**Lösung mit Vereine-Edition:**
- Mitglieder + Spender getrennt verwalten
- Spendenbescheinigungen automatisch generieren
- Projekt "Konzert Frühling 2025" mit Ticketeinnahmen
- Zweckgebundene Spenden tracken
- ESTV-konforme Formulare

#### Use Case 3: Quartierverein
**Anforderungen:**
- 30 Mitglieder
- Kleines Budget (~CHF 5'000.- / Jahr)
- Quartalsfest organisieren
- Einfache Buchhaltung für Vorstand
- Revisor braucht Export

**Lösung mit Vereine-Edition:**
- Simple Mitgliederverwaltung
- Projekt "Quartalsfest" mit Budget
- Dashboard für Vorstand (aktueller Stand)
- Excel-Export für Revisor
- Jahresrechnung in 5 Minuten

#### Use Case 4: Vorstandsmitglied mit beiden Editionen
**Szenario:**
- Person ist Kassier in Sportverein
- Gleichzeitig private Money Manager Instanz
- Will Vereins-Transaktionen NICHT in privater Instanz, aber Zugriff auf beide

**Lösung:**
- Vereins-Edition auf Vereins-Server (verein-buchhaltung.example.com)
- Standard-Edition auf privatem Server (mein-geld.example.com)
- Federation: Beide Instanzen können Shared Accounts haben (z.B. gemeinsames Haushaltskonto mit Partner)
- Vorstand nutzt Vereine-Edition für Vereinsbuchhaltung
- Privat nutzt Standard-Edition für persönliche Finanzen
- Optional: Export aus Vereine → Import in Standard für Transparenz (z.B. Spesenabrechnung)

---

### 🎯 Vorteile: Separate Vereine-Edition

#### Für Entwickler
- ✅ **Clean Separation** - Keine If-Else "isVerein" Logik im Code
- ✅ **Spezialisierte Features** - Vereins-Features ohne Kompromisse
- ✅ **Unabhängige Releases** - Standard v1.5 ≠ Vereine v1.3
- ✅ **Einfacheres Testing** - Nur relevante Tests pro Edition
- ✅ **Klarere Dokumentation** - Separate Docs für separate Zielgruppen

#### Für Benutzer
- ✅ **Richtige Edition wählen** - Privat vs. Verein
- ✅ **Keine Feature-Überfrachtung** - Standard bleibt schlank
- ✅ **Spezialisierte UX** - UI optimiert für Vereins-Workflows
- ✅ **Daten-Interoperabilität** - Bei Bedarf Austausch möglich

#### Für Schweizer Vereine
- ✅ **OR-Compliance out-of-the-box** - Rechtliche Anforderungen erfüllt
- ✅ **QR-Rechnungen** - Swiss Payment Standard integriert
- ✅ **Kostenlos & Self-Hosted** - CHF 0.- vs. CHF 240-600.- pro Jahr
- ✅ **Datenschutz** - DSGVO/FADP konform, eigene Daten
- ✅ **Federation** - Dachverbände + Sektionen können zusammenarbeiten

### 📊 Vergleich: Standard vs. Vereine Edition

| Feature | Standard | Vereine | Datenaustausch |
|---------|----------|---------|----------------|
| **Core Features** |
| Account Management | ✅ | ✅ | 100% kompatibel |
| Transactions | ✅ | ✅ | 100% kompatibel |
| Bank Import | ✅ | ✅ | 100% kompatibel |
| Reconciliation | ✅ | ✅ | 100% kompatibel |
| Multi-Currency | ✅ | ✅ | 100% kompatibel |
| Federation | ✅ | ✅ | 100% kompatibel |
| Shared Accounts | ✅ | ✅ | 100% kompatibel |
| Replication | ✅ | ✅ | 100% kompatibel |
| PWA | ✅ | ✅ | N/A |
| Passkeys/OAuth | ✅ | ✅ | N/A |
| **Vereine Features** |
| Mitgliederverwaltung | ❌ | ✅ | Export möglich |
| Beitragsverwaltung | ❌ | ✅ | Export möglich |
| Kostenstellen | ❌ | ✅ | Transaction-Level |
| Projekt-Buchhaltung | ❌ | ✅ | Transaction-Level |
| OR-Jahresabschluss | ❌ | ✅ | PDF Export |
| QR-Rechnungen | ❌ | ✅ | N/A |
| Spendenverwaltung | ❌ | ✅ | Export möglich |
| GV-Unterlagen | ❌ | ✅ | PDF Export |
| Revisoren-Reports | ❌ | ✅ | Excel Export |
| **Target User** |
| Privatpersonen | ✅ | ❌ | - |
| Gemeinschaftskonten | ✅ | ✅ | Federation |
| Kleine Vereine | ❌ | ✅ | - |
| Große Vereine | ❌ | ✅ | - |
| Dachverbände | ❌ | ✅ | Federation |

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

**Letzte Aktualisierung:** 2025-01-07
**Nächstes Review:** 2025-03-01
