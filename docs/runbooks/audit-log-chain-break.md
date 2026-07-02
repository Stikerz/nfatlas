# Runbook: Audit-log chain integrity break

**Severity:** SEV-1
**Owner:** on-call engineer (human) → EL + Compliance Lead on any confirmed break
**Last verified:** 2026-07-01 by 🛡️ Tobi (drafted)
**Applies to:** the hash-chained append-only `audit_log` table defined in ADR-005 and verified by the nightly chain-verification job.
**Related:** R-TEC-02 (🔴 high), ADR-005, trust-first positioning invariant.

## Symptoms

- The nightly chain-verification job reports one or more rows whose `row_hash` does not correctly hash the canonical row content OR whose `prev_hash` does not match the `row_hash` of the row with the previous `seq`.
- Alert fires: `AUDIT_LOG_CHAIN_BREAK` → SEV-1.
- Dashboard tile "Audit chain status" is red.

## Detection

- **Automated:** nightly chain-verification job runs at 03:00 Africa/Lagos.
- **Manual:** an operator or Compliance & Risk agent runs the verifier ad-hoc (e.g. immediately after a completed real-money draw per ADR-005).
- **Alert firing:** any break. There is no tolerance threshold — zero broken links is the target, always.

## Impact

- **Trust-critical.** The hash chain is Atlas's tamper-evidence guarantee. A confirmed break undermines the trust claim in the marketing and, more materially, exposes Atlas to inability to prove draw fairness or ledger integrity if challenged.
- **Regulatory:** a persistent break must be disclosed to Compliance Lead and, on counsel advice, may need to be disclosed to the NLRC and/or affected users depending on the affected event types.
- **Operational:** if the break affects `audit_log` rows related to an active or recent draw, that draw's provably-fair claim is degraded until the break is diagnosed as non-material.

## Diagnosis steps

Run in order. Every step generates evidence for the post-incident record.

1. **Confirm the break is real, not a verifier-job bug.** Re-run the verifier from a clean environment:
   ```
   platform run --env production --service backend -- \
     python -m atlas.tools.verify_audit_chain --from-seq 1 --to-seq LATEST --verbose
   ```
   If this second run reports no break, the original alert was a transient job failure. Log as a false positive, investigate the verifier's environment, close.

2. **Identify the exact broken link.** Verifier output names the `seq` of the first row where the chain fails to reconstruct. Record the `seq`.

3. **Snapshot the affected rows.** Take a read-only export of `audit_log` for `seq` in `[first_broken - 5, first_broken + 5]`:
   ```
   platform run --env production --service backend -- \
     python -m atlas.tools.audit_log_export --from-seq $((SEQ - 5)) --to-seq $((SEQ + 5)) \
     --output /tmp/audit-forensic-$(date +%Y%m%d-%H%M%S).jsonl
   ```
   This preserves forensic evidence before any mitigation touches the table.

4. **Determine the break type:**
   - **Type A — `row_hash` incorrect:** the row's `row_hash` does not equal `SHA-256(JCS-canonicalize(row_content))`. Suggests either a hashing bug or post-write mutation of a row column.
   - **Type B — `prev_hash` mismatch:** the row's `prev_hash` does not equal the `row_hash` of `seq - 1`. Suggests either a row was deleted (revoked permissions should prevent this) or a row was inserted with a wrong `prev_hash` value.
   - **Type C — missing `seq`:** a gap in the monotonic sequence. Suggests a row was deleted (again, permissions should prevent).

5. **Cross-check DB permissions:**
   ```
   SELECT grantee, privilege_type FROM information_schema.table_privileges
     WHERE table_name = 'audit_log';
   ```
   Expected: application role has `INSERT` only. If it has `UPDATE` or `DELETE`, permissions have been altered — this is itself a SEV-1 security incident (see `secret-loss.md` for pattern, apply similarly).

6. **Check for recent DBA / admin activity.** Query the platform DB audit log for any manual queries against `audit_log` in the past 7 days:
   ```
   platform db audit --env production --filter "table:audit_log" --since "7 days ago"
   ```
   If there is any manual `UPDATE` or `DELETE`, you have found the cause — escalate immediately.

7. **Check backup / restore recency.** If a restore from backup ran recently, the chain may have re-anchored at a different point. Consult `restore-from-backup.md` §Notes.

8. Escalate to EL + Compliance Lead once type is identified. **Do NOT mitigate before both are on the call.**

## Mitigation steps

Mitigation is triage. The chain cannot be "repaired" in the sense of re-hashing broken rows (that would forge the chain). Mitigation is about isolating the impact, protecting the going-forward chain, and documenting the break.

### Immediate (all break types)

1. Stop any real-money draw currently in a `revealed` or pending-reveal state; postpone per `draw-entropy-unavailable.md` §Rollback (same postponement mechanism) until Compliance clears.
2. Freeze audit-log-affecting write paths that are known to be affected? — In practice, all real-money draw and ledger operations write to `audit_log`. If chain break is confirmed, put backend into `MAINTENANCE_MODE=true` (read-only + no ledger/draw writes) until diagnosis complete.
3. Create a **chain-continuation record**: a new row with a designated `event_name = "chain.break_recorded"` whose payload references the broken `seq` range. This preserves the going-forward chain while explicitly recording the break rather than pretending it didn't happen.
   ```
   platform run --env production --service backend -- \
     python -m atlas.tools.chain_break_record --broken-from-seq $FIRST_BAD --broken-to-seq $LAST_BAD --reason "$SHORT_DESC"
   ```
4. Preserve the forensic export from Diagnosis step 3 in cold storage (S3 with object-lock): `platform storage put s3://<atlas-forensic-bucket>/audit-break/<date>/ /tmp/audit-forensic-*.jsonl --immutable`.

### Type-specific follow-up

**Type A (`row_hash` incorrect):**
- Determine whether the row content was mutated post-write (compare against any prior nightly backup): `pg_restore` a prior backup into a temp DB, `SELECT * FROM audit_log WHERE seq = $SEQ;`, compare column values with production row.
- If mutation is confirmed, file a security incident — application role should not be able to mutate audit rows.

**Type B (`prev_hash` mismatch):**
- Determine whether a row was deleted or an insertion happened out of order. `SELECT MAX(seq), COUNT(*) FROM audit_log;` — if MAX(seq) > COUNT, rows were deleted.
- Same permissions check as Diagnosis step 5.

**Type C (missing `seq`):**
- Confirmed deletion. Same security incident escalation.

### Root-cause mitigation

- If a code bug: patch, test, deploy. Ensure the trigger enforcement is correct.
- If a permissions drift: rotate DB credentials, restore correct `INSERT`-only grant, review who has DBA access to production.
- If an intentional but unrecorded operator action: engage HR / Founder — this is a discipline breach.

## Rollback steps

There is no "rollback" for an audit-log break — the break happened, and pretending it didn't is exactly the anti-pattern the chain is designed to prevent. The `chain.break_recorded` row in Mitigation step 3 is the append-only acknowledgement that a break occurred; it is the closest thing to a "rollback." Do not attempt to reconstruct the missing links.

## Post-incident actions

**All confirmed chain breaks (whether root cause is bug, permissions, or intentional action):**

- Post-mortem within 5 working days.
- **Compliance & Risk review is mandatory.** Adaeze produces a verdict in `docs/compliance/reviews/` including whether the break is material to any specific completed draw or ledger event.
- **If any affected `seq` range covers a real-money draw's audit events**, that draw's proof is degraded. Adaeze recommends whether to (a) re-run the verifier script publicly with the acknowledged break flagged, (b) proactively disclose the break to affected users, (c) engage counsel on disclosure obligations.
- If root cause is a bug: fix + regression test + amended ADR-005 if the design needs strengthening.
- If root cause is a permissions or ops mistake: DB access review; consider additional controls (e.g. break-glass audit on production DB access).
- Update this runbook.
- AI Integration Log entry with full detail.
- **Consider whether the launch date holds** — a chain break during the pre-launch soak (Phase 5–6) is a red flag. Two breaks pre-launch = do not launch until the mechanism is proven stable for 30 consecutive days.

## Notes

- The chain break scenario is *rare by design* — the INSERT-only application role, the trigger, and the CI grep invariants layer defence. If a break occurs and none of those layers caught it, something significant has been bypassed. Treat with corresponding seriousness.
- The forensic export in Mitigation step 4 goes to S3 with object-lock (immutable) precisely so a subsequent attacker or ops mistake cannot destroy the evidence.
- The `chain.break_recorded` event pattern is a design choice: honest acknowledgement is more defensible than silent repair. Discussed and adopted per ADR-005 §Consequences.
