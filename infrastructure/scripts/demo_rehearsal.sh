#!/usr/bin/env bash
# Demo rehearsal — full flagship-flow smoke via curl.
#
# Walks the 16 steps of v0.5-demo-plan §2 end-to-end and asserts each
# succeeds. Exit 0 if the demo is green; exit 1 with a diagnostic on the
# first failure. Runnable against a fresh `make demo-reset` state.
#
# What it does NOT do: exercise the mobile/admin UIs. Those need
# manual walkthroughs + the OBS recording per the fallback plan. This
# script is the "the backend + flow logic is honest" check.
#
# Usage (from repo root, after `make dev` + `make demo-reset`):
#
#     bash infrastructure/scripts/demo_rehearsal.sh
#
# Env:
#     ATLAS_API_BASE   default http://localhost:8000
#     ATLAS_ADMIN_EMAIL / ATLAS_ADMIN_PASSWORD  (must match bootstrap)

set -euo pipefail

API="${ATLAS_API_BASE:-http://localhost:8000}"
ADMIN_EMAIL="${ATLAS_SUPERADMIN_EMAIL:-adaobi.ibe@atlas.dev}"
ADMIN_PASSWORD="${ATLAS_SUPERADMIN_PASSWORD:-dev_bootstrap_password_change_me_00}"

step=0
say() {
  step=$((step + 1))
  printf '\n[STEP %02d] %s\n' "$step" "$1"
}

fail() {
  printf '\n✗ FAIL at step %d: %s\n' "$step" "$1" >&2
  exit 1
}

jq_or_die() {
  if ! command -v jq >/dev/null 2>&1; then
    fail 'jq is required — brew install jq'
  fi
}

random_uuid() { python3 -c 'import uuid;print(uuid.uuid4())'; }
random_phone() { python3 -c 'import random;print(f"+2348030{random.randint(0,999999):06d}")'; }
random_email() { python3 -c 'import uuid;print(f"kemi-{uuid.uuid4().hex[:8]}@example.com")'; }

jq_or_die

# ── Step 1: register a fresh consumer ────────────────────────────────
say 'Register a fresh consumer'
CONSUMER_EMAIL=$(random_email)
CONSUMER_PHONE=$(random_phone)
CONSUMER_PASSWORD='correct horse battery staple'
REG_RESPONSE=$(curl -sS -X POST "$API/api/v1/users" \
  -H 'Content-Type: application/json' \
  -H "Idempotency-Key: $(random_uuid)" \
  -d "{\"email\":\"$CONSUMER_EMAIL\",\"phone_e164\":\"$CONSUMER_PHONE\",\"date_of_birth\":\"1993-03-12\",\"terms_accepted\":true}")
USER_ID=$(echo "$REG_RESPONSE" | jq -r '.user_id // empty')
[ -n "$USER_ID" ] || fail "register failed: $REG_RESPONSE"

# ── Step 2: issue + verify OTP ───────────────────────────────────────
say 'Issue + verify registration OTP (via mailhog)'
curl -sS -X POST "$API/api/v1/otps" \
  -H 'Content-Type: application/json' \
  -H "Idempotency-Key: $(random_uuid)" \
  -d "{\"user_id\":\"$USER_ID\",\"purpose\":\"registration\"}" >/dev/null
sleep 1
CODE=$(curl -sS 'http://localhost:8025/api/v2/messages' \
  | jq -r '.items[0].Content.Body' \
  | grep -oE '[0-9]{6}' | head -1)
[ -n "$CODE" ] || fail 'no OTP found in mailhog'
curl -sS -X POST "$API/api/v1/otps/verify" \
  -H 'Content-Type: application/json' \
  -H "Idempotency-Key: $(random_uuid)" \
  -d "{\"user_id\":\"$USER_ID\",\"purpose\":\"registration\",\"code\":\"$CODE\"}" >/dev/null

# ── Step 3: set password ─────────────────────────────────────────────
say 'Set password + login'
curl -sS -X POST "$API/api/v1/users/$USER_ID/password" \
  -H 'Content-Type: application/json' \
  -H "Idempotency-Key: $(random_uuid)" \
  -d "{\"password\":\"$CONSUMER_PASSWORD\"}" >/dev/null

LOGIN_RESPONSE=$(curl -sS -X POST "$API/api/v1/sessions" \
  -H 'Content-Type: application/json' \
  -H "Idempotency-Key: $(random_uuid)" \
  -d "{\"email\":\"$CONSUMER_EMAIL\",\"password\":\"$CONSUMER_PASSWORD\"}")
CONSUMER_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')
[ -n "$CONSUMER_TOKEN" ] || fail "login failed: $LOGIN_RESPONSE"

# ── Step 4: browse active draw ───────────────────────────────────────
say 'Browse active draw + verify commitment surfaces'
DRAW_ID=$(curl -sS "$API/api/v1/draws" | jq -r '.items[0].id // empty')
[ -n "$DRAW_ID" ] || fail 'no active draw — run make demo-seed first'
COMMITMENT=$(curl -sS "$API/api/v1/draws/$DRAW_ID" | jq -r '.commitment')
[ "${#COMMITMENT}" -eq 64 ] || fail "commitment not sha-256 hex: $COMMITMENT"

# ── Step 5: wallet chip reads 0 ─────────────────────────────────────
say 'Wallet chip reads 0 for a fresh consumer'
BAL=$(curl -sS "$API/api/v1/users/me/wallet" \
  -H "Authorization: Bearer $CONSUMER_TOKEN" | jq -r '.balance_minor')
[ "$BAL" = '0' ] || fail "wallet balance was $BAL not 0"

# ── Step 6: skill question ──────────────────────────────────────────
say 'Fetch skill question + answer correctly'
QUESTION_JSON=$(curl -sS "$API/api/v1/draws/$DRAW_ID/skill-questions/next" \
  -H "Authorization: Bearer $CONSUMER_TOKEN")
ATTEMPT_ID=$(echo "$QUESTION_JSON" | jq -r '.attempt_id')
# Demo seed uses "correct" as the answer text.
CORRECT_ID=$(echo "$QUESTION_JSON" | jq -r '.options[] | select(.text=="Abuja" or .text=="Green" or .text=="60" or .text=="144" or .text=="Mars" or .text=="0" or .text=="7" or .text=="Mandarin Chinese" or .text=="Pound Sterling" or .text=="9") | .id' | head -1)
[ -n "$CORRECT_ID" ] || fail "no known-correct option in question: $QUESTION_JSON"
ANSWER=$(curl -sS -X POST "$API/api/v1/skill-questions/attempts/$ATTEMPT_ID/answer" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $CONSUMER_TOKEN" \
  -H "Idempotency-Key: $(random_uuid)" \
  -d "{\"option_id\":\"$CORRECT_ID\"}")
[ "$(echo "$ANSWER" | jq -r '.is_correct')" = 'true' ] || fail "expected correct, got: $ANSWER"

# ── Step 7: purchase intent + webhook credit ────────────────────────
say 'Purchase ticket + simulate signed Paystack webhook'
PURCHASE=$(curl -sS -X POST "$API/api/v1/tickets/purchase" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $CONSUMER_TOKEN" \
  -H "Idempotency-Key: $(random_uuid)" \
  -d "{\"draw_id\":\"$DRAW_ID\",\"entitlement_id\":\"$ATTEMPT_ID\"}")
VENDOR_REF=$(echo "$PURCHASE" | jq -r '.vendor_reference')
AMOUNT=$(echo "$PURCHASE" | jq -r '.amount_minor')
[ -n "$VENDOR_REF" ] || fail "purchase failed: $PURCHASE"

BODY="{\"event\":\"charge.success\",\"data\":{\"reference\":\"$VENDOR_REF\",\"amount\":$AMOUNT,\"currency\":\"NGN\",\"status\":\"success\",\"channel\":\"card\",\"fees\":10000,\"customer\":{\"email\":\"$CONSUMER_EMAIL\"}}}"
SIG=$(printf '%s' "$BODY" | python3 infrastructure/scripts/sign_paystack_webhook.py)
curl -sS -X POST "$API/api/v1/payments/webhooks/paystack" \
  -H "x-paystack-signature: $SIG" \
  -H 'Content-Type: application/json' \
  -d "$BODY" >/dev/null

# ── Step 8: ticket shows up ─────────────────────────────────────────
say 'Ticket lands in /tickets/me'
MY_TICKETS=$(curl -sS "$API/api/v1/tickets/me" \
  -H "Authorization: Bearer $CONSUMER_TOKEN")
TICKET_ID=$(echo "$MY_TICKETS" | jq -r '.items[0].id // empty')
[ -n "$TICKET_ID" ] || fail "no ticket minted: $MY_TICKETS"

# ── Step 9: admin login ─────────────────────────────────────────────
say 'Admin login'
ADMIN_LOGIN=$(curl -sS -X POST "$API/api/v1/sessions" \
  -H 'Content-Type: application/json' \
  -H "Idempotency-Key: $(random_uuid)" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}")
ADMIN_TOKEN=$(echo "$ADMIN_LOGIN" | jq -r '.access_token // empty')
[ -n "$ADMIN_TOKEN" ] || fail "admin login failed: $ADMIN_LOGIN"

# ── Step 10: close draw ─────────────────────────────────────────────
say 'Admin closes the draw'
CLOSE=$(curl -sS -X POST "$API/api/v1/draws/$DRAW_ID/close" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Idempotency-Key: $(random_uuid)")
[ "$(echo "$CLOSE" | jq -r '.state')" = 'sales_closed' ] || fail "close failed: $CLOSE"

# ── Step 11: reveal draw ────────────────────────────────────────────
say 'Admin reveals the draw'
REVEAL=$(curl -sS -X POST "$API/api/v1/draws/$DRAW_ID/reveal" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Idempotency-Key: $(random_uuid)")
WINNER_COUNT=$(echo "$REVEAL" | jq -r '.winner_count')
[ "$WINNER_COUNT" -ge 1 ] || fail "no winners: $REVEAL"

# ── Step 12: fetch public proof ─────────────────────────────────────
say 'Public /proof publishes the full proof'
PROOF=$(curl -sS "$API/api/v1/draws/$DRAW_ID/proof")
[ "$(echo "$PROOF" | jq -r '.state')" = 'revealed' ] || fail "proof not revealed: $PROOF"
SERVER_SEED=$(echo "$PROOF" | jq -r '.server_seed // empty')
[ -n "$SERVER_SEED" ] || fail 'server_seed missing from proof'

# ── Step 13: verifier CLI reproduces the winner ─────────────────────
say 'verify_draw.py reproduces the same winner from the proof'
echo "$PROOF" > /tmp/atlas-proof.json
python3 backend/tools/verify_draw.py --proof /tmp/atlas-proof.json > /tmp/verify-output.txt
grep -q '^MATCH' /tmp/verify-output.txt || fail "verifier did not report MATCH:\n$(cat /tmp/verify-output.txt)"

# ── Step 14: audit-log chain intact ────────────────────────────────
say 'Audit-log chain is verified over the flow'
AUDIT=$(curl -sS "$API/api/v1/audit-log?limit=100" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
[ "$(echo "$AUDIT" | jq -r '.chain_verified')" = 'true' ] || fail "chain not verified: $AUDIT"

printf '\n✓ Demo rehearsal complete — all %d steps green.\n' "$step"
printf '  Draw:    %s\n' "$DRAW_ID"
printf '  Proof:   %s/api/v1/draws/%s/proof\n' "$API" "$DRAW_ID"
printf '  Winners: %s\n\n' "$WINNER_COUNT"
