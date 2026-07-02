# Runbook: Restore Postgres from backup

**Severity:** SEV-1 when triggered by a real data-loss incident; Ops when run as a scheduled drill.
**Owner:** on-call engineer (human), DevSecOps agent for automation
**Last verified:** 2026-07-01 by 🛡️ Tobi (drafted; first drill scheduled Phase 0 exit)
**Applies to:** staging and production Postgres restores. Local dev restore is not covered (rebuild via `environment-bootstrap.md` instead).
**RTO target:** < 1 hour end-to-end (per ADR-011 and delivery-framework Phase 5 exit).
**RPO target:** < 24 hours (nightly dump cadence per ADR-012).

## Symptoms

- Production Postgres unresponsive after infra failure, corrupted, or accidentally destroyed.
- Ledger reconciliation cannot complete because a table is missing or unreadable.
- DBA / operator mistake (rare with RBAC controls, but not zero) has produced a state Atlas cannot recover from at the application layer.
- **Or:** this is a scheduled drill (quarterly for staging, quarterly for production restore-to-staging).

## Detection

- Alerts: platform database health alerts fire; `/readyz` returns 503; ledger reconciliation job errors with connection or schema faults.
- Sentry: connection-refused errors spike across all backend and worker instances.
- Manual: reported by an operator or engineer who has observed data loss / corruption.

## Impact

- **Real incident:** Atlas cannot serve requests. Every payment intent in flight will fail (Paystack will retry webhooks per its policy — most will land after restore). Users see error pages. Any real-money draw in a live sales window is blocked; the operator may need to postpone the draw per `draw-entropy-unavailable.md` §Rollback (same postponement mechanism).
- **Drill:** zero user impact — drill runs against staging, or against a restored-to-staging copy of production. Purpose is to verify RTO/RPO and refresh operator familiarity.

## Diagnosis steps

Only for a real incident. Skip for a drill.

1. Confirm Postgres is actually down, not the app: `platform db status --env production`.
2. Confirm the failure mode: partial data loss vs full DB unavailability vs corruption vs accidental table drop.
3. Confirm the last successful nightly backup timestamp: `platform storage list s3://<atlas-backup-bucket>/postgres/production/ | tail -5`.
4. **Establish RPO reality vs target.** RPO target is < 24h. If the last backup is > 24h old, escalate to EL immediately — a longer window means larger data loss.
5. Snapshot the current (broken) DB state before restoring — for forensics: `platform db snapshot --env production --label pre-restore-$(date +%Y%m%d-%H%M%S)`.
6. Announce the incident:
   - Internal Slack: `#atlas-incident` channel with the SEV-1 template.
   - External comms if user-visible: activate the incident-comms template from `delivery-framework.md §10`.

## Mitigation steps (the restore itself)

### For a DRILL (restore staging from staging's own backup)

1. Take a fresh backup right before the drill (so no data is lost even if the drill overwrites): `platform db backup --env staging --label pre-drill-$(date +%Y%m%d-%H%M%S)`.
2. Pick the backup to restore FROM — usually the last nightly automatic backup: `platform storage get s3://<atlas-backup-bucket>/postgres/staging/nightly-latest.dump -o /tmp/restore.dump`.
3. Verify the dump downloaded intact: `pg_restore --list /tmp/restore.dump | head` should list tables including `ledger_entries`, `outbox`, `audit_log`.
4. Provision a **new** Postgres instance for the restore target — do NOT restore into the running staging DB during a drill: `platform db create --env staging --name staging-restore-drill --size <same-as-current>`.
5. Restore into the new instance:
   ```
   pg_restore \
     --clean \
     --if-exists \
     --dbname=$STAGING_RESTORE_URL \
     --jobs=4 \
     /tmp/restore.dump
   ```
6. Validate the restore (§Validation below).
7. Record RTO: total elapsed time from step 2 to step 6 completion.
8. Tear down the drill instance: `platform db destroy --env staging --name staging-restore-drill --confirm`.
9. `shred -u /tmp/restore.dump`.
10. Log the drill result in `docs/runbooks/drill-log.md` (create if not present).

### For a REAL INCIDENT (restore production from production's own backup)

1. Confirm EL is on the call. This is a two-person operation — never restore production alone.
2. Freeze writes at the platform edge if the DB is partially responsive (put backend into read-only mode via the `MAINTENANCE_MODE=true` env var flip → hot-reload).
3. Take the pre-restore forensic snapshot (step 5 in Diagnosis above) if not already done.
4. Download the most recent good backup: `platform storage get s3://<atlas-backup-bucket>/postgres/production/nightly-latest.dump -o /tmp/restore.dump`. If the most recent backup is itself corrupted or too old, work backwards through prior nightlies (retention is 7 days per ADR-012).
5. Verify the dump: `pg_restore --list /tmp/restore.dump | wc -l` (expect ~40+ objects for V1; falling below means dump is incomplete).
6. **Decision point:** restore into the **existing** production DB (fast, destructive) or **provision new** production DB (slower, requires DNS re-point). EL calls this. Default recommendation: provision new — leaves the broken DB available for forensics and reduces cascade risk if the restore itself has issues.
7. Provision new production Postgres (if that path): `platform db create --env production --name production-restored-$(date +%Y%m%d) --size <same-as-current>`.
8. Restore:
   ```
   pg_restore \
     --clean \
     --if-exists \
     --dbname=$NEW_PROD_URL \
     --jobs=4 \
     /tmp/restore.dump
   ```
9. Validate (§Validation below).
10. Update `DATABASE_URL` secret to point at the new instance: `platform secrets set --env production DATABASE_URL --from-file /tmp/new_prod_url` (never in shell history).
11. Restart backend and worker services: `platform restart --env production --service backend && platform restart --env production --service worker`.
12. Verify `/readyz` → `{"status":"ready"}`.
13. Un-freeze writes: `MAINTENANCE_MODE=false` → hot-reload.
14. `shred -u /tmp/restore.dump`.
15. Announce restoration in `#atlas-incident` and to users if external comms were sent.

## Validation (both drill and real incident)

Run all of these against the restored DB before considering the restore complete:

1. `SELECT COUNT(*) FROM ledger_entries;` — expect the count from the last backup, ± any writes that were lost.
2. `SELECT COUNT(*) FROM tickets;` — same.
3. `SELECT COUNT(*) FROM audit_log;` — same.
4. Ledger balance: `SELECT SUM(CASE direction WHEN 'C' THEN amount_minor ELSE -amount_minor END) FROM ledger_entries;` — expect zero (double-entry invariant). Non-zero = restore is bad.
5. Audit-log chain: run the chain-verification job manually against the restored DB. If it fails, the backup itself was corrupt; escalate.
6. Outbox: `SELECT COUNT(*) FROM outbox WHERE processed_at IS NULL;` — note the count; worker will process these on startup (they may re-fire events, which is fine given the outbox pattern's at-least-once contract per ADR-002 — consumers are idempotent).

Any validation failure → do NOT flip production traffic to the restored DB. Escalate to EL, roll back per §Rollback, and investigate.

## Rollback steps

If the restore fails validation, or produces an unusable DB:

1. If the restore was into a NEW instance (recommended path), simply do not flip `DATABASE_URL`. The original (broken) production DB remains the current pointer. Destroy the failed restore: `platform db destroy --env production --name production-restored-<date> --confirm`.
2. If the restore was into the EXISTING production DB (fast path), you are in trouble — the DB now contains partial-restore state. Try the next-oldest backup (step 4 above with a prior filename) or escalate to a forensic recovery specialist.
3. Announce failure and next steps in `#atlas-incident`.

## Post-incident actions

For real incidents:

- Full post-mortem within 5 working days. Document in `docs/incidents/YYYY-MM-DD-<slug>.md`.
- Root-cause analysis — was the original failure a bug, ops mistake, infra outage, or attack?
- Improve backup cadence if RPO reality > RPO target.
- If chain-verification failed on the restore, add an alert on backup-integrity to prevent silent-bad-backup accumulation.
- AI Integration Log entry.

For drills:

- Update `docs/runbooks/drill-log.md` with RTO achieved and any friction observed.
- If RTO > 1 hour, file a task to reduce it (parallelise, pre-provision spare instance, etc.).
- Update this runbook with any step that was unclear during the drill.
- Next drill scheduled within 90 days.

## Notes

- The BVN pepper (ADR-010) is unaffected by DB restore — it lives in the secret manager, not the DB. Any restore leaves self-exclusion enforcement intact.
- The server-seed encryption key (ADR-006) is similarly unaffected. However, in-flight draws with a `revealed_at` timestamp between the backup and the restore point may need manual reconciliation with published proof data.
- If the restore's target RTO cannot be met, the launch date does NOT hold per `docs/risk-register.md §9`. This runbook is a hard prerequisite.
