#!/usr/bin/env bash
# End-to-end integration test: two federated instances + full feature smoke test.
# Expects the stack from docker-compose.yml to be running (backend-a on :8001,
# backend-b on :8002). Exits non-zero on the first failed assertion.
set -euo pipefail

A="http://localhost:8001"
B="http://localhost:8002"
COMPOSE="docker compose -f deploy/integration-test/docker-compose.yml"

pass() { echo "  ✓ $1"; }
fail() { echo "  ✗ $1"; exit 1; }
assert_eq() { [ "$1" = "$2" ] || fail "$3 (expected '$2', got '$1')"; }

wait_health() {
  local url="$1" name="$2"
  for _ in $(seq 1 60); do
    curl -fsS "$url/health" >/dev/null 2>&1 && { pass "$name healthy"; return; }
    sleep 2
  done
  fail "$name did not become healthy"
}

mk_user() { # service username email  -> prints JWT
  $COMPOSE exec -T "$1" python - "$2" "$3" <<'PY' | tail -1
import sys
from decimal import Decimal
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.user import User
from app.models.account import Account
un, em = sys.argv[1], sys.argv[2]
db = SessionLocal()
u = db.query(User).filter(User.username == un).first()
if not u:
    u = User(username=un, email=em, is_active=True, is_superuser=True)
    db.add(u); db.commit(); db.refresh(u)
if not db.query(Account).filter(Account.user_id == u.id).first():
    db.add(Account(user_id=u.id, name="Hauptkonto", type="checking", currency="CHF", balance=Decimal("0.00")))
    db.commit()
print(create_access_token({"sub": str(u.id)}))
PY
}

echo "== Warten auf Backends =="
wait_health "$A" backend-a
wait_health "$B" backend-b

echo "== Test-User =="
TA=$(mk_user backend-a stefan stefan@backend-a:8000); [ -n "$TA" ] && pass "stefan@A angelegt"
TB=$(mk_user backend-b rolf  rolf@backend-b:8000);  [ -n "$TB" ] && pass "rolf@B angelegt"
AUTH_A=(-H "Authorization: Bearer $TA")
AUTH_B=(-H "Authorization: Bearer $TB")

echo "== Federation: well-known =="
pk=$(curl -fsS "$A/.well-known/money-instance" | jq -r .public_key | head -c 27)
assert_eq "$pk" "-----BEGIN PUBLIC KEY-----" "A well-known liefert public_key"

echo "== Federation: Pairing (beidseitig) =="
r=$(curl -fsS -X POST "$A/api/v1/federation/peers" "${AUTH_A[@]}" -H 'Content-Type: application/json' -d '{"domain":"backend-b:8000","name":"B"}')
assert_eq "$(echo "$r" | jq -r .approved)" "true" "A pairt B"
r=$(curl -fsS -X POST "$B/api/v1/federation/peers" "${AUTH_B[@]}" -H 'Content-Type: application/json' -d '{"domain":"backend-a:8000","name":"A"}')
assert_eq "$(echo "$r" | jq -r .approved)" "true" "B pairt A"

echo "== Federation: Rechnung senden (ohne from_user) =="
r=$(curl -fsS -X POST "$A/api/v1/federation/invoice/send" "${AUTH_A[@]}" -H 'Content-Type: application/json' \
  -d '{"to_user":"rolf@backend-b:8000","amount":"12.50","currency":"CHF","description":"e2e","date":"2026-06-02"}')
assert_eq "$(echo "$r" | jq -r .status)" "pending" "Invoice gesendet & empfangen"

echo "== Federation: Empfang + Annahme + Saldo =="
inv=$(curl -fsS "$B/api/v1/transactions/" "${AUTH_B[@]}")
assert_eq "$(echo "$inv" | jq -r '.[0].source')" "federation" "B hat Federation-Transaktion"
tid=$(echo "$inv" | jq -r '.[0].id')
curl -fsS -X POST "$B/api/v1/federation/invoice/$tid/accept" "${AUTH_B[@]}" >/dev/null
bal=$(curl -fsS "$B/api/v1/accounts/" "${AUTH_B[@]}" | jq -r '.[0].balance')
assert_eq "$bal" "12.50" "rolfs Saldo nach Annahme"

echo "== Smoke: Konten & Buchungen (A) =="
spar=$(curl -fsS -X POST "$A/api/v1/accounts/" "${AUTH_A[@]}" -H 'Content-Type: application/json' -d '{"name":"Sparkonto","type":"savings","currency":"CHF"}' | jq -r .id)
giro=$(curl -fsS "$A/api/v1/accounts/" "${AUTH_A[@]}" | jq -r '.[] | select(.name=="Hauptkonto") | .id')
curl -fsS -X POST "$A/api/v1/transactions/" "${AUTH_A[@]}" -H 'Content-Type: application/json' -d "{\"account_id\":$giro,\"date\":\"2026-06-02\",\"amount\":-20.00,\"description\":\"Test\"}" >/dev/null
bal=$(curl -fsS "$A/api/v1/accounts/$giro" "${AUTH_A[@]}" | jq -r .balance)
assert_eq "$bal" "-20.00" "Buchung aktualisiert Saldo"

echo "== Smoke: Umbuchung =="
curl -fsS -X POST "$A/api/v1/transactions/transfer" "${AUTH_A[@]}" -H 'Content-Type: application/json' \
  -d "{\"from_account_id\":$giro,\"to_account_id\":$spar,\"amount\":10.00,\"date\":\"2026-06-02\"}" >/dev/null
sbal=$(curl -fsS "$A/api/v1/accounts/$spar" "${AUTH_A[@]}" | jq -r .balance)
assert_eq "$sbal" "10.00" "Umbuchung gutgeschrieben"

echo "== Smoke: Dauerbuchung =="
curl -fsS -X POST "$A/api/v1/recurring/" "${AUTH_A[@]}" -H 'Content-Type: application/json' \
  -d "{\"account_id\":$giro,\"amount\":-5.00,\"interval\":\"monthly\",\"next_run\":\"2026-06-02\"}" >/dev/null
created=$(curl -fsS -X POST "$A/api/v1/recurring/process" "${AUTH_A[@]}" | jq -r .created)
[ "$created" -ge 1 ] && pass "Dauerbuchung erzeugt ($created)" || fail "Dauerbuchung nicht erzeugt"

echo "== Smoke: Integrationen (API-Key + Receipt-Bot-Push, idempotent) =="
key=$(curl -fsS -X POST "$A/api/v1/integrations/api-keys" "${AUTH_A[@]}" -H 'Content-Type: application/json' -d '{"name":"bot"}' | jq -r .token)
[ -n "$key" ] && pass "API-Key erstellt"
push() { curl -fsS -X POST "$A/api/v1/integrations/receipt-bot/transactions" -H "X-API-Key: $key" -H 'Content-Type: application/json' \
  -d '{"transactions":[{"date":"2026-06-02","amount":-3.00,"description":"Bon","external_ref":"r1"}]}'; }
assert_eq "$(push | jq -r .created)" "1" "Receipt-Bot Push erstellt"
assert_eq "$(push | jq -r .skipped)" "1" "Receipt-Bot Push idempotent"

echo "== Smoke: EasyTax-Export =="
code=$(curl -s -o /dev/null -w '%{http_code}' "$A/api/v1/settings/categories/easytax-export" "${AUTH_A[@]}")
assert_eq "$code" "200" "EasyTax-Export liefert CSV"

echo "== Smoke: Kategorien CRUD =="
cid=$(curl -fsS -X POST "$A/api/v1/categories/" "${AUTH_A[@]}" -H 'Content-Type: application/json' -d '{"name":"Miete","easytax_code":"3100"}' | jq -r .id)
curl -fsS -X PUT "$A/api/v1/categories/$cid" "${AUTH_A[@]}" -H 'Content-Type: application/json' -d '{"easytax_code":"3200"}' >/dev/null
ucode=$(curl -s -o /dev/null -w '%{http_code}' -X DELETE "$A/api/v1/categories/$cid" "${AUTH_A[@]}")
assert_eq "$ucode" "204" "Kategorie CRUD"

echo ""
echo "✅ Alle Integrationstests bestanden."
