# Integration: Quittungsabrechnungsbot → Money Manager

Der [Quittungsabrechnungsbot](https://github.com/stefan-ffr/Quittungsabrechnungsbot) kann seine
Transaktionen **zusätzlich** an den Money Manager schicken. Sie landen in einem speziellen Konto
**„Quittungsabrechnung"** (Typ `receipt_bot`), das pro Benutzer automatisch angelegt wird.
Der Bot bleibt eigenständig – das ist ein Push/Spiegel, kein Ersatz.

## 1. API-Key erstellen

Im Money Manager: **Einstellungen → Integrationen → API-Keys → „Key erstellen"**.
Der Token wird **nur einmal** angezeigt – sicher speichern (z. B. in der `.env` des Bots).

## 2. Transaktionen pushen

```
POST /api/v1/integrations/receipt-bot/transactions
Header: X-API-Key: <dein-token>
Content-Type: application/json
```

```json
{
  "transactions": [
    {
      "date": "2026-06-02",
      "amount": -42.50,
      "description": "Migros – Anteil Rolf",
      "category": "Lebensmittel",
      "currency": "CHF",
      "external_ref": "receipt-1234"
    }
  ]
}
```

- `amount`: negativ = Ausgabe, positiv = Einnahme/erhaltene Zahlung.
- `external_ref`: die eigene ID des Bots (Quittungs-/Transfer-ID). Wird zur **Idempotenz**
  genutzt – ein erneuter Push mit derselben `external_ref` wird übersprungen (kein Doppeleintrag).
- `currency`: setzt beim ersten Push die Währung des Spezialkontos (Default `CHF`).

**Antwort:**
```json
{ "created": 1, "skipped": 0, "account_id": 7 }
```

## Mapping-Empfehlung (Bot-Seite)

| Bot | Push an Money Manager |
|---|---|
| Quittung (Anteil „ich") | eine Transaktion `amount = -my_share`, `external_ref="receipt-<id>"` |
| `cash_transfer` `paid` | `amount = -betrag`, `external_ref="transfer-<id>"` |
| `cash_transfer` `received` | `amount = +betrag`, `external_ref="transfer-<id>"` |

So spiegelt das Spezialkonto den eigenen Saldo aus der Quittungsabrechnung wider, während die
detaillierte Personen-/Item-Aufteilung weiterhin im Bot lebt.

## Sicherheit

- Authentifizierung über `X-API-Key` (SHA-256-gehasht gespeichert, Klartext nur einmal sichtbar).
- Keys sind pro Benutzer; Widerruf jederzeit über die UI.
- Der Endpoint schreibt ausschließlich in das eigene Spezialkonto des Key-Besitzers.
