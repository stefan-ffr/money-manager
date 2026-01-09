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
- [x] Shared Accounts UI (Erstellen, Mitglieder, Split Transactions, Balance, Settlement)
- [x] Receipt Upload (Beleg hochladen, anzeigen, herunterladen für Transaktionen)
- [x] Konten-Seite MS Money 99 Style (Split-Layout: Tabelle oben, Formular unten)

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
**Status:** ✅ FERTIG (2026-01-08 19:25)
**Backend:** ✅ Komplett implementiert
**Beschreibung:**
- ✅ Shared Accounts Liste mit Cards
- ✅ Neues Shared Account erstellen (Name, Beschreibung, Währung)
- ✅ Details Modal mit 3 Tabs (Mitglieder, Transaktionen, Abrechnung)
- ✅ Mitglieder hinzufügen (User Identifier, Instance URL, Rolle)
- ✅ Split Transaction erstellen (Wer hat bezahlt, Betrag, Split-Type: equal/percentage/custom)
- ✅ Balance anzeigen (Wer schuldet wem mit farblicher Kennzeichnung)
- ✅ Settlement anzeigen (Optimale Abrechnung mit Greedy-Algorithmus)
- ✅ Federation-ready (Instanz URL für externe Mitglieder)

**Priorität:** ✅ IMPLEMENTIERT

### 3. Receipt Upload bei Transaktionen
**Status:** ✅ FERTIG (2026-01-09 10:30)
**Backend:** ✅ `/api/v1/transactions/{id}/receipt`
**Beschreibung:**
- ✅ Upload-Button in Transaktionen-Liste (Auge-Icon wenn vorhanden, Upload-Icon wenn nicht)
- ✅ Beleg-Vorschau Modal (PDF mit iframe, Bilder mit img tag)
- ✅ Beleg-Download Button
- ✅ File Upload mit automatischer Invalidierung
- ✅ Backend-Fix: TransactionUpdate Schema um requires_confirmation erweitert

**Priorität:** ✅ IMPLEMENTIERT

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
**Status:** ✅ FERTIG (2026-01-09 11:15)
**Backend:** ✅ `PUT /api/v1/transactions/{id}`
**Beschreibung:**
- ✅ Klick auf Transaktion lädt sie ins Formular
- ✅ Formular wird vorausgefüllt
- ✅ Update-Funktion in MS Money 99 Style Page

**Priorität:** ✅ IMPLEMENTIERT

### 9. Account Balance Tracking
**Status:** ✅ FERTIG (2026-01-09 11:15)
**Backend:** ✅ Daten vorhanden
**Beschreibung:**
- ✅ Running Balance wird in Transaktions-Tabelle berechnet
- ✅ Balance wird bei jeder Transaktion aktualisiert
- ✅ Saldo-Spalte in MS Money 99 Style Page

**Priorität:** ✅ IMPLEMENTIERT

### 10. Filter & Suche
**Status:** ❌ Fehlt
**Backend:** ✅ Query-Parameter vorhanden
**Beschreibung:**
- Transaktionen filtern (Datum, Konto, Kategorie, Status)
- Suche in Beschreibung
- Export filtered results

**Priorität:** 🟢 NIEDRIG

## 📋 Implementierungs-Reihenfolge

**Phase 1: Kritische Features** ✅ ABGESCHLOSSEN
1. ✅ Bank CSV Import UI
2. ✅ Shared Accounts - Basic CRUD
3. ✅ Shared Accounts - Split Transactions
4. ✅ Shared Accounts - Balance & Settlement
5. ✅ Receipt Upload bei Transaktionen

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

## 🆕 Neue Feature-Requests

### Konten-Seite: MS Money 99 Style
**Status:** ✅ FERTIG (2026-01-09 11:15)
**Beschreibung:**
- ✅ Header: Konto-Auswahl Dropdown + Edit/Neu Buttons
- ✅ Oben (2/3): Transaktions-Tabelle mit Spalten (Datum, Beschreibung, Kategorie, Einnahme, Ausgabe, Saldo, Beleg)
- ✅ Unten (1/3): Transaktions-Formular (Typ, Datum, Betrag, Beschreibung, Kategorie, Beleg)
- ✅ Klick auf Transaktion lädt sie ins Formular
- ✅ Buttons: Neu, Speichern, Verschieben, Löschen
- ✅ Running Balance Berechnung
- ✅ Receipt Upload/Preview integriert
- ✅ Blue-Highlight für ausgewählte Transaktion

**Priorität:** ✅ IMPLEMENTIERT

---

**Letztes Update:** 2026-01-09 11:20 (nach MS Money 99 Style Konten-Seite Implementierung)
**Nächster Schritt:** Categories Management oder Dashboard Improvements
