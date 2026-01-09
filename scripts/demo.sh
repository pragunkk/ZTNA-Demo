#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://localhost:5001}"

echo "[1/7] Starting stack..."
docker compose up -d --build >/dev/null
echo "OK"

echo "[2/7] Health check..."
curl -sS "$BASE/healthz" | python3 -m json.tool >/dev/null
echo "OK"

echo "[3/7] Login as alice..."
ALICE_TOKEN=$(curl -sS "$BASE/login" -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"alice123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "OK"

echo "[4/7] Alice -> eng (ALLOW with posture)"
curl -sS "$BASE/apps/eng" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "X-Device-Trusted: true" \
  -H "X-MFA: false" \
  -H "X-Geo: IN" | python3 -m json.tool >/dev/null
echo "OK"

echo "[5/7] Alice -> finance (DENY)"
STATUS=$(curl -sS -o /dev/null -w "%{http_code}" "$BASE/apps/finance" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "X-Device-Trusted: true" \
  -H "X-MFA: true" \
  -H "X-Geo: IN")
test "$STATUS" = "403"
echo "OK (403)"

echo "[6/7] Login as bob..."
BOB_TOKEN=$(curl -sS "$BASE/login" -H 'Content-Type: application/json' \
  -d '{"username":"bob","password":"bob123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "OK"

echo "[7/7] Bob -> finance (ALLOW with posture + MFA)"
curl -sS "$BASE/apps/finance" \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -H "X-Device-Trusted: true" \
  -H "X-MFA: true" \
  -H "X-Geo: IN" | python3 -m json.tool >/dev/null
echo "OK"

echo "✅ ZTNA demo completed successfully"
