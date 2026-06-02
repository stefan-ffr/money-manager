# Feature → Test Coverage

Traceability matrix: each **✅ Live** feature from [FEATURES.md](FEATURES.md) (and the
core app features) mapped to the automated test that exercises it. Keep this in
sync when adding features — a new "Live" feature should add a row + a test.

Test sources:
- **e2e** = `deploy/integration-test/run.sh` (two-instance workflow `integration.yml`)
- **unit** = `backend/tests/` (workflow `test.yml`)

| Feature (FEATURES.md / app) | Status | Automated test |
|---|---|---|
| Federation: pairing (TLS bootstrap + pinned key) | ✅ Live | e2e: *Pairing (beidseitig)* |
| Federation: signed invoice send/receive | ✅ Live | e2e: *Rechnung senden / Empfang*; unit: `test_federation_crypto.py` |
| Federation: signature verify/tamper/wrong-key | ✅ Live | unit: `test_federation_crypto.py` |
| Federation: allow-list (approved peers only) | ✅ Live | e2e: *Pairing* (send only to approved) |
| Federation: public-key discovery (`/.well-known`) | ✅ Live | e2e: *well-known* |
| 🔴 Red confirmation for auto-entries | ✅ Live | e2e: *Rote Markierung* (`requires_confirmation`, accept→confirmed) |
| Manual entry + running balance | ✅ Live | e2e: *Konten & Buchungen* |
| Transfer between own accounts | ✅ Live | e2e: *Umbuchung* |
| Recurring transactions | ✅ Live | e2e: *Dauerbuchung*; unit: `test_recurring.py` (date logic) |
| EasyTax CSV export | ✅ Live | e2e: *EasyTax-Export* |
| Categories CRUD + EasyTax mapping | ✅ Live | e2e: *Kategorien CRUD* |
| Receipt-bot integration (API key + push) | ✅ Live | e2e: *Integrationen* (key + idempotent push) |
| Multi-currency formatting | ✅ Live | unit: `test_currencies.py` |
| API-key auth (hashing) | ✅ Live | unit: `test_api_key.py` |
| CORS parsing (regression) | ✅ Live | unit: `test_config.py` |
| Auth / data isolation (per-user scoping) | ✅ Live | covered implicitly by e2e (per-token access); see security review |
| Passkey (WebAuthn) auth | 🔧 Ready | **not automatable headlessly** (needs an authenticator) — verified manually |
| Telegram bot | ✅ Live | **not in CI** (needs Telegram) — bot has its own repo/build |
| Mirror instances / replication | 🔧 Ready | endpoints guarded; full sync needs a dedicated harness (tracked) |
| ISO 20022 / eBill / ML categorization | 🔧 Planned | not implemented |

## How we use FEATURES.md as the test spec

1. A feature marked **✅ Live** in FEATURES.md must have a row here and a test.
2. FEATURES.md sometimes embeds a concrete recipe (e.g. *Testing Confirmation
   Flow*); encode it as an assertion in `run.sh` rather than leaving it as prose.
3. The two CI workflows enforce it on every push/PR:
   - `test.yml` — backend unit tests + frontend type-check/build
   - `integration.yml` — two-instance federation e2e + feature smoke test
4. Features that can't run headlessly (Passkey/WebAuthn, Telegram) are called out
   here explicitly so the gap is visible, not silently uncovered.
