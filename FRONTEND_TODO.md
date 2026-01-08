# Frontend Implementation TODO

Tracking für fehlende Frontend-Features. Backend ist vollständig implementiert.

## ✅ Bereits implementiert (2026-01-08)

- [x] Login/Register mit WebAuthn/Passkey
- [x] Dashboard (Basic: Gesamtsaldo, Anzahl Konten)
- [x] Konten Management (CRUD mit Privatkonto, Sparkonto, Säule 3a, Kreditkarte, Bargeld)
- [x] Transaktionen Liste (Anzeige mit Status, Quelle, Bestätigung)
- [x] Transaktion erstellen (Manuell mit Konto, Datum, Betrag, Kategorie, Beschreibung)
- [x] Transaktion löschen
- [x] Transaktion bestätigen (Rot markierte Auto-Entries)
- [x] Abstimmung/Reconciliation (CSV Upload, Bank-Matching)
- [x] Einstellungen - Federation Tab (Instanz-Info anzeigen)
- [x] Einstellungen - Mirror Instanzen (CRUD)
- [x] Einstellungen - Allgemein (Platzhalter)
- [x] Einstellungen - Telegram Bot (Anleitung)
- [x] Einstellungen - Kategorien (Platzhalter)
- [x] Einstellungen - Sicherheit (Info)
- [x] Bank CSV Import UI (Upload, Bank-Auswahl, Auto-Match, Setup Modal, Ergebnis-Anzeige)

## 🔴 Kritisch - Kern-Features fehlen

### 1. Bank CSV Import UI
**Status:** ✅ FERTIG (2026-01-08 19:15)
**Backend:** ✅ `/api/v1/import/bank/import` + `/api/v1/import/bank/setup`
**Beschreibung:**
- ✅ Upload-Seite für CSV Dateien mit Drag & Drop
- ✅ Bank-Auswahl (PostFinance, UBS, Raiffeisen, ZKB, CS)
- ✅ Auto-Matching Konfiguration (Konto automatisch erkennen)
- ✅ Import-Ergebnis anzeigen (erfolgreiche Imports, Duplikate, Fehler)
- ✅ Integration in Navigation als "Bank Import"
- ✅ Bank Setup Modal für IBAN-Konfiguration
- ✅ Unterstützte Banken Sidebar mit Details
- ✅ Anleitung für Benutzer

**Priorität:** ✅ IMPLEMENTIERT

### 2. Shared Accounts (Gemeinschaftskonten)
**Status:** ❌ Nur Platzhalter
**Backend:** ✅ Komplett implementiert
**Beschreibung:**
- Shared Accounts Liste
- Neues Shared Account erstellen (Name, Beschreibung, Währung)
- Mitglieder hinzufügen (User Identifier, Instance URL, Rolle)
- Split Transaction erstellen (Wer hat bezahlt, Betrag, Split-Type)
- Balance anzeigen (Wer schuldet wem)
- Settlement anzeigen (Optimale Abrechnung)

**Priorität:** 🔥 SEHR HOCH (Kern-Feature laut Doku - "Cross-Instance Shared Accounts")

### 3. Receipt Upload bei Transaktionen
**Status:** ❌ Fehlt
**Backend:** ✅ `/api/v1/transactions/{id}/receipt`
**Beschreibung:**
- Upload-Button in Transaktion-Formular
- Upload-Button in Transaktionen-Liste
- Beleg-Vorschau (PDF/Bild)
- Beleg-Download

**Priorität:** 🔥 HOCH

## 🟡 Wichtig - Vervollständigung

### 4. Categories Management
**Status:** ❌ Nur Platzhalter in Settings
**Backend:** ✅ `/api/v1/categories/`
**Beschreibung:**
- Kategorien anlegen/bearbeiten/löschen
- EasyTax Mapping konfigurieren
- Standard-Kategorien anzeigen

**Priorität:** 🟡 MITTEL

### 5. EasyTax Export
**Status:** ❌ Fehlt
**Backend:** ❓ Unklar ob implementiert
**Beschreibung:**
- Export-Button für CSV
- Zeitraum auswählen
- Nach Kategorien filtern

**Priorität:** 🟡 MITTEL (Swiss-specific Feature)

### 6. Dashboard Verbesserung
**Status:** ⚠️ Nur Basic Platzhalter
**Backend:** ✅ Daten via APIs verfügbar
**Beschreibung:**
- Letzte Transaktionen anzeigen
- Ausgaben/Einnahmen Chart (Monat/Jahr)
- Top Kategorien
- Pending Confirmations Zähler

**Priorität:** 🟡 MITTEL

## 🟢 Nice-to-Have - Ergänzungen

### 7. Federation Management UI
**Status:** ⚠️ Nur Info-Anzeige
**Backend:** ✅ `/api/v1/federation/`
**Beschreibung:**
- Andere Instanzen hinzufügen
- Public Key testen
- Verbindung testen

**Priorität:** 🟢 NIEDRIG (für v1.0 optional)

### 8. Transaktion bearbeiten
**Status:** ❌ Fehlt
**Backend:** ✅ `PUT /api/v1/transactions/{id}`
**Beschreibung:**
- Edit-Button in Transaktionen-Liste
- Formular vorausfüllen
- Update-Funktion

**Priorität:** 🟢 NIEDRIG (erstmal nur Create + Delete)

### 9. Account Balance Tracking
**Status:** ❌ Statisch
**Backend:** ✅ Daten vorhanden
**Beschreibung:**
- Balance wird bei Transaktion automatisch aktualisiert
- Balance History anzeigen

**Priorität:** 🟢 NIEDRIG

### 10. Filter & Suche
**Status:** ❌ Fehlt
**Backend:** ✅ Query-Parameter vorhanden
**Beschreibung:**
- Transaktionen filtern (Datum, Konto, Kategorie, Status)
- Suche in Beschreibung
- Export filtered results

**Priorität:** 🟢 NIEDRIG

## 📋 Implementierungs-Reihenfolge

**Phase 1: Kritische Features** (Nächste 3-5 Steps)
1. ✅ Bank CSV Import UI
2. ✅ Shared Accounts - Basic CRUD
3. ✅ Shared Accounts - Split Transactions
4. ✅ Shared Accounts - Balance & Settlement
5. ✅ Receipt Upload

**Phase 2: Vervollständigung** (Danach)
6. Categories Management
7. EasyTax Export
8. Dashboard Improvements

**Phase 3: Polish** (Optional)
9. Federation Management UI
10. Edit Transactions
11. Filter & Suche

---

## Notizen

- **Backend ist vollständig implementiert** - alle APIs funktionieren
- **Frontend ist Mockup-artig** - viele Platzhalter statt echten Features
- **Dokumentation verspricht mehr** als aktuell im Frontend sichtbar ist
- **Fokus:** Erst die kritischen Features implementieren, dann polieren

---

**Letztes Update:** 2026-01-08 19:10 (nach Transaktions-Form Implementierung)
**Nächster Schritt:** Bank CSV Import UI implementieren
