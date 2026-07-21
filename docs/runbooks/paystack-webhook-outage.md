# Runbook: Paystack webhook outage

**Severity:** SEV-2 (SEV-1 if webhook stalls span a draw close)
**Owner:** on-call engineer → EL if backlog exceeds 30 minutes
**Last verified:** 2026-07-25 by 💻 Amelia (W4 Day 5 draft — awaiting Tobi review)
**Applies to:** V1 (Paystack-only). Sibling adapters in V2 produce sibling runbooks.
**Related:** ADR-008 §Webhook handling, ADR-002 §Outbox, `payment-outage.md`, `ledger-reconciliation-mismatch.md`.

## Symptoms

Distinct from a full Paystack outage — the API side may be healthy while webhooks stall or fail verification.

- Users complete Paystack checkout ("payment successful" on Paystack's page) but their wallet balance in-app does not update within ~2 minutes.
- Support tickets: *"I paid but the app still shows nothing"*.
- `WEBHOOK_STALE` alert fires (no webhook deliveries observed in 15 minutes during business hours).
- Signature-verification errors spike (401s on `/api/v1/payments/webhooks/paystack`) — indicates either secret rotation drift or a spoof attempt.
- `payment_intents` rows accumulate in `status = 'initiated'` well beyond the ~5-minute expected lag.

## Detection

- **Alert:** `WEBHOOK_STALE` — no rows appended to `audit_log` with `event_name = 'payment.confirmed'` in 15 minutes during a period with active intent creation.
- **Alert:** `WEBHOOK_401_SPIKE` — verify-signature-fail rate > 5% over 10 minutes.
- **Dashboard signal:** the ratio of `payment_intents` in `initiated` vs `succeeded` states diverges from the trailing-7-day baseline.
- **User signal:** ticket-queue tag "payment-not-credited".
- **External signal:** Paystack dashboard → Settings → API Keys & Webhooks → **Recent deliveries**. Failed deliveries and retry state are visible there.

## Impact

- **Users:** paid successfully at Paystack but see no wallet balance. Trust hit if unresolved > 15 minutes.
- **Ledger:** money moved at the vendor but no ledger entry landed. Reconciliation (once implemented Week 6) will surface this as a shortfall on the next-day pass.
- **Money at risk:** low if backlog processes cleanly after recovery; higher if manual reprocessing is needed (each hand-fire is a chance to introduce a duplicate credit — the idempotency layer defends but only within the intended window).

## Diagnosis steps

1. **Distinguish which side of the outage this is.** Query the last-received webhook:
   ```sql
   SELECT MAX(occurred_at) FROM audit_log WHERE event_name IN ('payment.confirmed', 'payment.failed');
   ```
   Age of the last event = webhook-side outage window.
2. **Check Paystack's recent-deliveries panel.** Log in to the Paystack dashboard, navigate to **Recent webhook deliveries**. Three cases:
   - **Deliveries succeeding at Paystack (200 responses), no matching audit rows.** → Our side dropped the webhook after receipt. Check backend logs for 5xx or crash. Confirm the deployed webhook route is `/api/v1/payments/webhooks/paystack` and reachable at the current DNS.
   - **Deliveries failing at Paystack (401 from us).** → Signature mismatch. Almost certainly a webhook-secret drift — see §Mitigation "Secret drift".
   - **No deliveries attempted.** → Paystack-side issue. Follow `payment-outage.md` instead.
3. **Confirm the webhook endpoint is publicly reachable.**
   ```
   curl -X POST https://api.atlas.example.com/api/v1/payments/webhooks/paystack \
        -H 'x-paystack-signature: bogus' \
        -H 'Content-Type: application/json' \
        -d '{}'
   ```
   Expected: `401 invalid_signature` (proves the route is up and signature check is running). If you get anything else — timeout, 404, 502 — the endpoint is genuinely down; escalate to Tobi.
4. **Check for stuck `initiated` intents that Paystack considers settled.** For each, run `PaystackAdapter.fetch(vendor_reference)` — if Paystack says `success` but our row is still `initiated`, we missed the webhook.

## Mitigation steps

### Endpoint is up but delivery is failing at Paystack

1. Verify the webhook secret registered in Paystack matches `ATLAS_PAYSTACK_WEBHOOK_SECRET` in the running backend. Rotate to match; the source of truth is the value in secrets management, not the value that happens to be in the running process.
2. Ask Paystack support (or use the dashboard) to **re-deliver** the queued failed events. Do not attempt to re-fire manually via curl — the idempotency layer defends, but the audit trail should show real Paystack redeliveries rather than synthesized ones.

### Endpoint is up, deliveries succeeded at Paystack, no audit rows on our side

3. Read the last 15 minutes of backend logs for 5xx responses to `/api/v1/payments/webhooks/paystack`. Signature mismatches log as 401 (not our problem); anything else = handler crashed.
4. If the handler crashed on a specific event body, reproduce locally:
   ```
   BODY='...paystack event body from logs...'
   SIG=$(printf '%s' "$BODY" | python infrastructure/scripts/sign_paystack_webhook.py)
   curl -X POST http://localhost:8000/api/v1/payments/webhooks/paystack \
        -H "x-paystack-signature: $SIG" \
        -H "Content-Type: application/json" \
        -d "$BODY"
   ```
5. Fix + redeploy. Then have Paystack re-deliver the queued events.

### Endpoint is down (route not reachable, DNS, TLS, load balancer)

6. This is not a webhook-specific runbook; escalate per `environment-bootstrap.md` §Recovery.

### Manual credit as last resort

7. **Do NOT credit user wallets manually** except with EL + Adaeze approval. If required, use `PaystackAdapter.fetch(vendor_reference)` to confirm Paystack agrees the payment succeeded, then call `wallet.service.record_deposit(...)` with `idempotency_key=f"deposit:{vendor_reference}"` — this matches the key the webhook path would have used, so a delayed real webhook will no-op instead of double-crediting.

## Rollback steps

- If a bad deployment introduced the crash, roll back via the standard `platform rollback` path (see `environment-bootstrap.md`).
- Nothing else to roll back; the runbook's actions (re-delivery via Paystack, secret rotation) are naturally forward-only.

## Post-incident actions

- Post-mortem if backlog exceeded 30 minutes OR a manual credit was issued OR a signature-drift went undetected > 1 hour.
- If manual credits were issued, run reconciliation for the affected window (Week 6+ once cron lands; until then, run the diff helper ad hoc).
- Update the risk register: cumulative webhook outages > 2 hours in trailing 30 days should trigger a conversation about a webhook-replay job (poll `PaystackAdapter.fetch` for `initiated` intents older than 15 minutes).
- AI Integration Log entry.
- Notify Adaeze if any user-visible balances were adjusted manually.

## Notes

- The webhook endpoint is signature-gated (ADR-008 §Invariants 2) — a 401 is Paystack's problem to fix (retry with correct secret), not ours to loosen. Never disable signature verification to "clear a backlog".
- Idempotency keys used by the deposit flow are deterministic (`deposit:{vendor_reference}`, `fee:{vendor_reference}`); manual credits that follow this pattern will collide safely with a delayed webhook.
- Week 6's reconciliation job will surface any missed webhook the next morning as a shortfall on the settlement diff. Until Week 6, the on-call is the reconciliation.
