#!/usr/bin/env bash
# Mirror/replication e2e: instance A pushes its account+transaction to instance B.
set -euo pipefail

A="http://localhost:8001"
B="http://localhost:8002"
COMPOSE="docker compose -f deploy/replication-test/docker-compose.yml"

pass() { echo "  ✓ $1"; }
fail() { echo "  ✗ $1"; exit 1; }
assert_eq() { [ "$1" = "$2" ] || fail "$3 (expected '$2', got '$1')"; }

wait_health() {
  for _ in $(seq 1 60); do curl -fsS "$1/health" >/dev/null 2>&1 && { pass "$2 healthy"; return; }; sleep 2; done
  fail "$2 not healthy"
}

mk_user() { # service username email withAccount(0|1) -> prints JWT
  $COMPOSE exec -T "$1" python - "$2" "$3" "$4" <<'PY' | tail -1
import sys
from decimal import Decimal
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.user import User
from app.models.account import Account
un, em, wa = sys.argv[1], sys.argv[2], sys.argv[3]
db = SessionLocal()
u = db.query(User).filter(User.username == un).first()
if not u:
    u = User(username=un, email=em, is_active=True, is_superuser=True)
    db.add(u); db.commit(); db.refresh(u)
if wa == "1" and not db.query(Account).filter(Account.user_id == u.id).first():
    db.add(Account(user_id=u.id, name="Hauptkonto", type="checking", currency="CHF", balance=Decimal("0.00")))
    db.commit()
print(create_access_token({"sub": str(u.id)}))
PY
}

echo "== Warten =="
wait_health "$A" backend-a
wait_health "$B" backend-b

echo "== Identische User (geteilte Mirror-Identität, id=1) =="
TA=$(mk_user backend-a stefan stefan@a 1)   # user + Konto
TB=$(mk_user backend-b stefan stefan@b 0)   # nur user (Konto kommt per Replikation)
[ -n "$TA" ] && [ -n "$TB" ] && pass "User auf A und B"

echo "== Mirrors konfigurieren (Public Keys gepinnt) =="
APK=$(curl -fsS "$A/.well-known/money-instance" | jq -r .public_key)
BPK=$(curl -fsS "$B/.well-known/money-instance" | jq -r .public_key)
# B kennt A (damit /receive die signierte Payload akzeptiert)
curl -fsS -X POST "$B/api/v1/replication/mirrors" -H "Authorization: Bearer $TB" -H 'Content-Type: application/json' \
  -d "{\"instance_url\":\"http://backend-a:8000\",\"instance_id\":\"backend-a:8000\",\"public_key\":$(jq -Rs . <<<"$APK"),\"sync_direction\":\"pull\"}" >/dev/null
pass "B kennt A"
# A pusht zu B
mid=$(curl -fsS -X POST "$A/api/v1/replication/mirrors" -H "Authorization: Bearer $TA" -H 'Content-Type: application/json' \
  -d "{\"instance_url\":\"http://backend-b:8000\",\"instance_id\":\"backend-b:8000\",\"public_key\":$(jq -Rs . <<<"$BPK"),\"sync_direction\":\"push\"}" | jq -r .id)
[ -n "$mid" ] && pass "A pusht zu B (mirror $mid)"

echo "== Buchung auf A erstellen =="
giro=$(curl -fsS "$A/api/v1/accounts/" -H "Authorization: Bearer $TA" | jq -r '.[0].id')
curl -fsS -X POST "$A/api/v1/transactions/" -H "Authorization: Bearer $TA" -H 'Content-Type: application/json' \
  -d "{\"account_id\":$giro,\"date\":\"2026-06-02\",\"amount\":-50.00,\"description\":\"Mirror-Test\"}" >/dev/null
pass "Transaktion auf A"

echo "== Sync auslösen (A -> B push) =="
res=$(curl -fsS -X POST "$A/api/v1/replication/mirrors/$mid/sync" -H "Authorization: Bearer $TA")
echo "  → $res"
assert_eq "$(echo "$res" | jq -r .status)" "success" "Sync erfolgreich"
[ "$(echo "$res" | jq -r .pushed)" -ge 2 ] && pass "mind. 2 Entitäten gepusht" || fail "zu wenig gepusht"

echo "== Verifizieren: Daten auf B angekommen =="
bacc=$(curl -fsS "$B/api/v1/accounts/" -H "Authorization: Bearer $TB")
assert_eq "$(echo "$bacc" | jq -r '.[0].name')" "Hauptkonto" "Konto auf B repliziert"
assert_eq "$(echo "$bacc" | jq -r '.[0].balance')" "-50.00" "Saldo auf B repliziert"
btx=$(curl -fsS "$B/api/v1/transactions/" -H "Authorization: Bearer $TB")
assert_eq "$(echo "$btx" | jq -r '.[0].description')" "Mirror-Test" "Transaktion auf B repliziert"
assert_eq "$(echo "$btx" | jq -r '.[0].amount')" "-50.00" "Betrag auf B repliziert"

echo ""
echo "✅ Mirror/Replication e2e bestanden."
