# Runbook: Ledger reconciliation mismatch

**Severity:** SEV-1
**Owner:** on-call engineer (human) → EL + Finance Lead on any confirmed mismatch
**Last verified:** 2026-07-01 by 🛡️ Tobi (drafted)
**Applies to:** the nightly reconciliation job comparing Atlas's `payment_gateway_clearing` ledger balance against Paystack's settlement report.
**Related:** R-FIN-01 (⚫ catastrophic), R-FIN-02 (🔴 high), ADR-003, ADR-008.

## Symptoms

- The nightly reconciliation job (`backend/api/payment/jobs/reconcile.py`) reports a difference beyond tolerance threshold between Atlas's ledger `payment_gateway_clearing` account and Paystack's settlement statement for the same period.
- An alert fires: `LEDGER_RECON_MISMATCH` → SEV-1.
- The dashboard tile "Yesterday's reconciliation status" is red.

## Detection

- **Automated:** nightly job runs at 02:00 Africa/Lagos; posts result to a Postgres audit table and to Slack `#atlas-ops`.
- **Alert firing threshold:** any difference exceeding the tolerance defined in `docs/qa/strategy.md` (default: ₦100 or 0.01% of daily volume, whichever is greater).
- **Dashboard:** `platform-metrics/ledger` shows the last 30 nights' recon status.

## Impact

- **What money is at risk:** depends on the direction and size of the mismatch. Under-recon (Atlas thinks it holds more than Paystack settled) may indicate a webhook mis-processing or duplicate credit. Over-recon (Paystack settled more than Atlas recorded) may indicate a missed webhook or bug in payment intent recording.
- **What users see:** possibly nothing immediately. But: continued operation with an unreconciled ledger risks propagating the error into prize payouts.
- **Regulatory / compliance:** a persistent unreconciled state must be recorded in the audit log and reviewed by Adaeze. If unresolved for > 3 business days, must be reported to Finance Lead + Founder.

## Diagnosis steps

Run these in order. Do not proceed to Mitigation until Diagnosis identifies the cause.

1. **Confirm the alert is real, not a Paystack settlement lag.** Check Paystack dashboard for the same date range — Paystack occasionally posts a settlement 24–48 hours late. If Atlas's amount matches a *later* Paystack settlement, this is timing, not corruption. Document and dismiss.

2. **Pull the exact numbers.** Log in to the reconciliation dashboard:
   ```
   platform run --env production --service backend -- \
     python -m atlas.scripts.recon_detail --date $YESTERDAY
   ```
   Output shows: Atlas's `payment_gateway_clearing` credits for the date; Paystack's settlement for the date; the delta; the top-10 transactions on each side.

3. **Categorise the delta:**
   - **Atlas has entries Paystack does not:** possible duplicate webhook processing, or a payment intent recorded before Paystack confirmed.
   - **Paystack has settlements Atlas does not:** missed webhook, or webhook signature verification failure suppressed the record.
   - **Same transaction, different amount:** rare; usually a fee-record bug (fees should be a separate ledger entry per ADR-008).

4. **Cross-check with the outbox:** `SELECT id, event_name, aggregate_id, created_at, processed_at, attempts, last_error FROM outbox WHERE event_name IN ('PaymentSucceeded','WalletCredited') AND created_at::date = '$YESTERDAY' ORDER BY created_at;`. Look for unprocessed rows, dead-letter cases, or events with attempts > 1 (indicating retry).

5. **Cross-check with the audit log:** `SELECT * FROM audit_log WHERE event_name = 'payment.confirmed' AND occurred_at::date = '$YESTERDAY' ORDER BY seq;`. Count should match Paystack settlement count exactly. If it doesn't, you've localised the bug to the webhook handler.

6. **Cross-check with idempotency records:** `SELECT * FROM idempotency_records WHERE endpoint LIKE '%payment%' AND created_at::date = '$YESTERDAY' AND response_code IS NULL;` — non-null in-flight records over 30 minutes old suggest the request handler crashed between record insert and completion.

7. Escalate to EL + Finance Lead once cause is identified with evidence. **Do NOT mitigate before EL is on the call.**

## Mitigation steps

Depending on cause identified in Diagnosis. All mitigations require EL approval and produce **contra-entries** (never edit or delete existing ledger rows — ADR-003 forbids and DB enforces).

### Cause A — Missed webhook (Paystack has settlement, Atlas doesn't)

1. Confirm the specific missed webhook by finding the payment reference in Paystack's dashboard and checking Atlas's `payments` table: `SELECT * FROM payments WHERE vendor_reference = '$REF';`.
2. If Atlas has no record at all: re-fetch from Paystack: `platform run --env production --service backend -- python -m atlas.scripts.payment_refetch --reference $REF`. This idempotent script pulls the current state from Paystack and processes it as if the webhook had arrived.
3. Verify the recon delta shrinks by the expected amount.
4. Re-run the nightly reconciliation for the affected date: `platform run --env production --service backend -- python -m atlas.scripts.recon --date $YESTERDAY --replay`.

### Cause B — Duplicate credit (Atlas has entries Paystack doesn't have twice)

1. Identify the duplicate transaction IDs from Diagnosis step 4 (outbox retry column will show attempts > 1 with idempotency-key collision).
2. **Contra-entry the duplicate.** Run: `platform run --env production --service backend -- python -m atlas.scripts.contra_entry --original-tx $TX_ID --reason "duplicate webhook processing 2026-MM-DD"`. This script creates a balanced reverse transaction, audit-logged, with EL + Finance Lead as the required approvers via the two-approval gate.
3. Verify user-facing wallet balance is now correct: `platform run --env production --service backend -- python -m atlas.scripts.balance_check --user-id $USER_ID`.
4. Notify the affected user if the correction is visible in their history (rare — the user usually only sees the correct final balance).

### Cause C — Fee-record bug (same tx, different amount)

1. Compute the fee delta from Paystack settlement.
2. Ensure a `operator_revenue → payment_gateway_clearing` contra entry for the fee is present. If not, create it as in Cause B.
3. File a bug ticket for the fee-recording code path — this is a code fix, not just a data fix.

### Cause D — Paystack settlement timing (dismissed in Diagnosis step 1)

1. Document the timing in the reconciliation audit log with the expected next-day match.
2. Confirm the next day's reconciliation shows the match. If it doesn't, escalate — this is now a real mismatch.

## Rollback steps

Contra-entries are themselves append-only ledger entries; there is no "rollback." If a contra-entry is created in error, the mitigation is another contra-entry that reverses the erroneous one. Each layer requires EL + Finance Lead re-approval.

## Post-incident actions

- Post-mortem within 5 working days.
- **Compliance review by Adaeze is mandatory** for every ledger reconciliation mismatch, whether cause was a bug, timing, or ops mistake. Verdict recorded in `docs/compliance/reviews/`.
- If cause was a code bug: fix + regression test that would have caught it. File as a story owned by Amelia.
- If cause was Paystack-side (missed webhook): file a ticket with Paystack support; consider changing to explicit-poll for a period.
- Update this runbook with any diagnostic step that was missing.
- AI Integration Log entry.
- If two mismatches occur within a 30-day window regardless of root cause: **halt real-money draws** until root-cause pattern is understood. Discuss with Founder.

## Notes

- The tolerance threshold in `docs/qa/strategy.md` exists to avoid noise; do NOT raise the threshold to make an alert go quiet. If threshold seems too tight, that's a design conversation with Adaeze, not an operational one.
- Reconciliation runs during a window when payment webhooks are still arriving for the *previous* day's late-close transactions. The job accounts for this with a 3-hour grace window; alerts that fire before 05:00 local are almost always the grace-window edge case and should be verified before escalation.
- The `contra_entry` script is the only sanctioned mechanism for ledger correction. If you find yourself wanting to run raw SQL against `ledger_entries`, stop.
