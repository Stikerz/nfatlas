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
WEBHOOK_SECRET="${ATLAS_PAYSTACK_WEBHOOK_SECRET:-local_dev_paystack_webhook_secret_do_not_use_in_prod}"

# Python that has atlas + pydantic installed. Falls back to system
# python3 when the venv isn't available (e.g. inside the backend
# Docker container which pip-installed everything globally).
if [ -x backend/.venv/bin/python ]; then
  PYTHON=backend/.venv/bin/python
else
  PYTHON=python3
fi

sign_paystack() {
  # HMAC-SHA-512 hex of the body with the webhook secret. Portable
  # (openssl is everywhere), no dep on the atlas Python env.
  printf '%s' "$1" | openssl dgst -sha512 -hmac "$WEBHOOK_SECRET" | awk '{print $2}'
}

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

# Register + verify + password + login for a single consumer. Sets
# globals CONSUMER_EMAIL, CONSUMER_TOKEN.
register_consumer() {
  CONSUMER_EMAIL=$(random_email)
  local phone
  phone=$(random_phone)
  local password='correct horse battery staple'
  local reg_response
  reg_response=$(curl -sS -X POST "$API/api/v1/users" \
    -H 'Content-Type: application/json' \
    -H "Idempotency-Key: $(random_uuid)" \
    -d "{\"email\":\"$CONSUMER_EMAIL\",\"phone_e164\":\"$phone\",\"date_of_birth\":\"1993-03-12\",\"terms_accepted\":true}")
  local user_id
  user_id=$(echo "$reg_response" | jq -r '.user_id // empty')
  [ -n "$user_id" ] || fail "register failed: $reg_response"

  curl -sS -X POST "$API/api/v1/otps" \
    -H 'Content-Type: application/json' \
    -H "Idempotency-Key: $(random_uuid)" \
    -d "{\"user_id\":\"$user_id\",\"purpose\":\"registration\"}" >/dev/null
  sleep 1
  # Filter mailhog by recipient — items[0] alone races across the
  # multi-consumer loop and can pick the previous user's OTP.
  # mailhog's Mailbox field keeps the leading `+` so match on the
  # full phone_e164.
  local code
  code=$(curl -sS 'http://localhost:8025/api/v2/messages' \
    | jq -r --arg addr "$phone" \
        '[.items[] | select(.To[0].Mailbox==$addr)] | .[0].Content.Body' \
    | grep -oE '[0-9]{6}' | head -1)
  [ -n "$code" ] || fail "no OTP found in mailhog for phone $phone"
  curl -sS -X POST "$API/api/v1/otps/verify" \
    -H 'Content-Type: application/json' \
    -H "Idempotency-Key: $(random_uuid)" \
    -d "{\"user_id\":\"$user_id\",\"purpose\":\"registration\",\"code\":\"$code\"}" >/dev/null

  curl -sS -X POST "$API/api/v1/users/$user_id/password" \
    -H 'Content-Type: application/json' \
    -H "Idempotency-Key: $(random_uuid)" \
    -d "{\"password\":\"$password\"}" >/dev/null

  local login_response
  login_response=$(curl -sS -X POST "$API/api/v1/sessions" \
    -H 'Content-Type: application/json' \
    -H "Idempotency-Key: $(random_uuid)" \
    -d "{\"email\":\"$CONSUMER_EMAIL\",\"password\":\"$password\"}")
  CONSUMER_TOKEN=$(echo "$login_response" | jq -r '.access_token // empty')
  [ -n "$CONSUMER_TOKEN" ] || fail "login failed: $login_response"
}

# Answer the skill question correctly for the current CONSUMER_TOKEN,
# purchase a ticket, feed a signed webhook. May be called multiple
# times per draw to build the pool.
# Correct answer for each question seeded by seed_v0_5.py, keyed on a
# distinctive substring of the prompt.
#
# This was a flat "first option whose text is in this list" match, which
# answered "What is the square root of 81?" with 7 — the continents
# answer, which sorts earlier in display_order and is also in the list.
# Questions rotate per (user, draw, minute bucket), so across six
# consumers the script failed 1 - 0.9^6 = ~47% of runs on
# entitlement_not_correct. Keying on the prompt removes the collision.
correct_answer_for() {
  case "$1" in
    *'capital of Nigeria'*)                     printf 'Abuja' ;;
    *'top stripe of the Nigerian flag'*)        printf 'Green' ;;
    *'minutes are there in an hour'*)           printf '60' ;;
    *'12 multiplied by 12'*)                    printf '144' ;;
    *'Red Planet'*)                             printf 'Mars' ;;
    *'Water freezes'*)                          printf '0' ;;
    *'continents are there'*)                   printf '7' ;;
    *'most native speakers'*)                   printf 'Mandarin Chinese' ;;
    *'currency is used in the United Kingdom'*) printf 'Pound Sterling' ;;
    *'square root of 81'*)                      printf '9' ;;
    *) return 1 ;;
  esac
}

buy_ticket_for_current_consumer() {
  local draw_id="$1"
  local question_json
  question_json=$(curl -sS "$API/api/v1/draws/$draw_id/skill-questions/next" \
    -H "Authorization: Bearer $CONSUMER_TOKEN")
  local attempt_id
  attempt_id=$(echo "$question_json" | jq -r '.attempt_id')
  local prompt answer correct_id
  prompt=$(echo "$question_json" | jq -r '.prompt')
  answer=$(correct_answer_for "$prompt") \
    || fail "no known answer for seeded question: $prompt"
  correct_id=$(echo "$question_json" \
    | jq -r --arg a "$answer" '.options[] | select(.text==$a) | .id' | head -1)
  [ -n "$correct_id" ] || fail "answer '$answer' not among options for: $prompt"
  curl -sS -X POST "$API/api/v1/skill-questions/attempts/$attempt_id/answer" \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $CONSUMER_TOKEN" \
    -H "Idempotency-Key: $(random_uuid)" \
    -d "{\"option_id\":\"$correct_id\"}" >/dev/null

  local purchase
  purchase=$(curl -sS -X POST "$API/api/v1/tickets/purchase" \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $CONSUMER_TOKEN" \
    -H "Idempotency-Key: $(random_uuid)" \
    -d "{\"draw_id\":\"$draw_id\",\"entitlement_id\":\"$attempt_id\"}")
  local vendor_ref amount
  vendor_ref=$(echo "$purchase" | jq -r '.vendor_reference // empty')
  amount=$(echo "$purchase" | jq -r '.amount_minor // empty')
  [ -n "$vendor_ref" ] && [ -n "$amount" ] || fail "purchase failed: $purchase"

  local body sig
  body="{\"event\":\"charge.success\",\"data\":{\"reference\":\"$vendor_ref\",\"amount\":$amount,\"currency\":\"NGN\",\"status\":\"success\",\"channel\":\"card\",\"fees\":10000,\"customer\":{\"email\":\"$CONSUMER_EMAIL\"}}}"
  sig=$(sign_paystack "$body")
  curl -sS -X POST "$API/api/v1/payments/webhooks/paystack" \
    -H "x-paystack-signature: $sig" \
    -H 'Content-Type: application/json' \
    -d "$body" >/dev/null
}

# ── Step 1: browse active draw ───────────────────────────────────────
say 'Browse active draw + verify commitment surfaces'
DRAW_ID=$(curl -sS "$API/api/v1/draws" | jq -r '.items[0].id // empty')
[ -n "$DRAW_ID" ] || fail 'no active draw — run make demo-seed first'
COMMITMENT=$(curl -sS "$API/api/v1/draws/$DRAW_ID" | jq -r '.commitment')
[ "${#COMMITMENT}" -eq 64 ] || fail "commitment not sha-256 hex: $COMMITMENT"

# ── Steps 2-8: six consumers register + buy tickets ─────────────────
# reveal_draw defaults to reserves=5, so we need 1 primary + 5 reserves
# = 6 tickets in the pool. The rehearsal registers six consumers so the
# demo can go straight from "sales open" to "close + reveal".
say 'Register 6 consumers + each buys a paid ticket via signed webhook'
for i in 1 2 3 4 5 6; do
  register_consumer
  # First consumer sanity-checks wallet chip reads 0.
  if [ "$i" -eq 1 ]; then
    BAL=$(curl -sS "$API/api/v1/users/me/wallet" \
      -H "Authorization: Bearer $CONSUMER_TOKEN" | jq -r '.balance_minor')
    [ "$BAL" = '0' ] || fail "wallet balance was $BAL not 0"
    LAST_CONSUMER_TOKEN="$CONSUMER_TOKEN"
    LAST_CONSUMER_EMAIL="$CONSUMER_EMAIL"
  fi
  buy_ticket_for_current_consumer "$DRAW_ID"
  printf '  consumer %d: %s\n' "$i" "$CONSUMER_EMAIL"
done

# ── Step 9: sanity — first consumer's ticket landed ────────────────
say 'First consumer sees their ticket in /tickets/me'
MY_TICKETS=$(curl -sS "$API/api/v1/tickets/me" \
  -H "Authorization: Bearer $LAST_CONSUMER_TOKEN")
TICKET_ID=$(echo "$MY_TICKETS" | jq -r '.items[0].id // empty')
[ -n "$TICKET_ID" ] || fail "no ticket minted for first consumer: $MY_TICKETS"

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
"$PYTHON" backend/tools/verify_draw.py --proof /tmp/atlas-proof.json > /tmp/verify-output.txt
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
