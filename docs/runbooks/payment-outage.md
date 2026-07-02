# Runbook: Paystack outage

**Severity:** SEV-2 (SEV-1 if a real-money draw is in a live sales window at the time of the outage)
**Owner:** on-call engineer (human) → EL if outage exceeds 15 minutes
**Last verified:** 2026-07-01 by 🛡️ Tobi (drafted)
**Applies to:** V1 (Paystack-only). V2 additions of Flutterwave / Moniepoint / USSD-direct produce sibling runbooks.
**Related:** R-VEN-01 (🔴 high), ADR-008.

## Symptoms

- Payment success rate drops below 95% for a sustained window (> 10 minutes).
- Paystack API returns 5xx errors on `POST /transaction/initialize` or webhook deliveries stop landing.
- Users report failed payments; support ticket volume for "payment failed" spikes.
- Paystack status page reports degradation or outage.

## Detection

- **Alert:** `PAYMENT_SUCCESS_RATE_LOW` fires when success rate < 95% over 10 minutes → SEV-2 to Slack + PagerDuty.
- **Alert (harder):** `WEBHOOK_STALE` fires when no webhook has landed in 15 minutes during business hours → SEV-2.
- **External signal:** Paystack status page https://status.paystack.com/ (bookmark; on-call checks proactively during any user-report spike).
- **User signal:** support tickets flowing through the "payment" queue tag.

## Impact

- **Users:** cannot buy paid tickets during the outage. Free-entry postal route remains available (per prize-competition mechanics) but is not a real-time UX substitute.
- **Draws:** if a draw is in a live sales window, entries stop coming in until Paystack recovers. Purchase intents already submitted may end up in inconsistent states — some paid, some pending, some failed.
- **Money at risk:** small in normal circumstances. But: (a) if a webhook backlog processes after recovery, at-least-once delivery per ADR-002 means some events fire twice — idempotency layer must catch this or R-FIN-02 (ledger mismatch) triggers; (b) if the outage crosses a draw's scheduled close, ambiguity about whether late-arriving payment intents count.
- **Trust:** worst impact is user perception if handled with poor UX ("payment failed" with no explanation).

## Diagnosis steps

1. **Confirm scale and side of the outage:**
   ```
   platform run --env production --service backend -- \
     python -m atlas.scripts.payment_health --window 15m
   ```
   Output: request count, success rate, error breakdown (Paystack 5xx, timeouts, network errors, our 4xx).
2. **Check Paystack status page:** https://status.paystack.com/. Record the incident ID if published.
3. **Distinguish Paystack outage from our-side bug:**
   - If Atlas backend can reach `https://api.paystack.co/health` (or equivalent) → the outage is not connectivity; likely Paystack API issue.
   - If Atlas backend cannot reach Paystack at all → check platform network egress, DNS, TLS chain.
4. **Check webhook queue depth:** `SELECT COUNT(*) FROM outbox WHERE event_name LIKE 'Payment%' AND processed_at IS NULL;`. A growing count suggests webhooks are arriving but our worker is not consuming — different problem, see `outbox-dead-letter.md` (V2 runbook).
5. **Check if a real-money draw is affected.** Draw list with `state IN ('open_for_sale', 'closing_soon')`:
   ```
   platform run --env production --service backend -- \
     python -m atlas.scripts.draw_state --state open,closing_soon
   ```
   If any draw is affected → escalate to SEV-1, EL on call.

## Mitigation steps

### For a Paystack-side outage (Atlas has no direct fix)

1. **Update user-facing messaging.** Flip the `PAYMENT_BANNER_ACTIVE=true` env var (hot-reload) — this surfaces a polite banner in Flutter and admin: *"Payments temporarily unavailable — we're monitoring the issue and will update shortly. Free-entry route remains available for all draws."*
2. **Communicate on Atlas's status page / X account / WhatsApp broadcast** if the outage exceeds 30 minutes.
3. **Draws affected — decision tree:**
   - Draw in early-to-mid sale window: no action; users can retry post-recovery.
   - Draw within 2 hours of scheduled close: **postpone the close time**. Announce the new close time (add ≥ 2 hours to the outage-clear time). Publish the postponement on the draw page; log to audit as `draw.close_postponed`.
   - Draw in reveal window: this shouldn't be affected by a payment outage (reveal is not payment-dependent) — but confirm no in-flight payments are erroneously counted as tickets.
4. **Do NOT force a manual close** while payment intent state is uncertain. Wait for Paystack recovery + a 15-minute post-recovery buffer to let webhook backlog process.

### After Paystack recovers

5. **Let the outbox worker catch up.** Do not manually re-fire webhooks. Monitor `SELECT COUNT(*) FROM outbox WHERE processed_at IS NULL;` — should drain to steady-state within 10 minutes.
6. **Reconcile the outage window.** Run reconciliation for the affected window (not just yesterday):
   ```
   platform run --env production --service backend -- \
     python -m atlas.scripts.recon --from "$OUTAGE_START" --to "$OUTAGE_END + 30m"
   ```
7. **If reconciliation surfaces a mismatch** → follow `ledger-reconciliation-mismatch.md`.
8. **Un-flip the banner.** `PAYMENT_BANNER_ACTIVE=false`.

### For an Atlas-side bug masquerading as Paystack outage

9. If Diagnosis step 3 indicates our-side issue: this is not a Paystack-outage runbook. Escalate to EL as an Atlas incident; investigate connectivity, DNS, TLS, backend deployment history.

## Rollback steps

Nothing to roll back on a Paystack outage — Atlas took no state-changing action. The banner env var is reverted in Mitigation step 8.

If a draw was postponed (Mitigation step 3), un-postponing is not appropriate; the postponed time is now the announced time.

## Post-incident actions

- Post-mortem if outage exceeded 30 minutes OR affected a draw's close/reveal window OR produced a reconciliation mismatch.
- Update `docs/risk-register.md` R-VEN-01 with the incident date; if cumulative Paystack downtime exceeds 4 hours in the trailing 30 days, trigger the V2 second-payment-rail conversation (Flutterwave) per PRD-v1 §4 deferrals.
- Verify the incident-comms template held up under real use; update if not.
- AI Integration Log entry.
- Notify Adaeze — she reviews for any regulatory-disclosure implications (particularly if a draw was postponed).

## Notes

- Paystack has historically been highly reliable in the Nigerian market, but not immune to sub-hour incidents. This runbook exists so the first Paystack incident is not the first time the on-call thinks about handling it.
- The `PAYMENT_BANNER_ACTIVE` toggle is a hot-reloadable env var, not a DB write — recovery from the banner state is instant.
- Draw postponement uses the same mechanism as `draw-entropy-unavailable.md` §Rollback. The commit hash of the draw remains valid; only the close and reveal times shift.
- **Do NOT** attempt to route around Paystack by manually crediting user wallets during an outage. That path leads directly to R-FIN-01 (ledger integrity break).
