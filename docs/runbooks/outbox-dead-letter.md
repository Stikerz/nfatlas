# Runbook: Outbox dead-letter — inspect + replay

**Severity:** SEV-3 by default; escalate to SEV-2 if a real-money `draw.winner_selected.v1` event is dead-lettered (a winner hasn't been notified).
**Owner:** DevSecOps on-call → notify EL if any winner event lands here in prod.
**Last verified:** 2026-08-26 by 💻 Amelia (W8 Day 3 first draft — awaiting Tobi review per week-8-build-plan §5).
**Applies to:** V1 outbox rows that exhausted their retry budget (`attempts >= ATLAS_OUTBOX_MAX_ATTEMPTS`, default 10). V0.5 workloads are low volume — a dead-letter row is almost always a real problem, not a transient blip.
**Related:** ADR-002 §Processing model, `atlas.outbox.worker` module docstring, `paystack-webhook-outage.md`.

## Symptoms

- Rows appearing in `outbox_dead_letter` (a manual `SELECT count(*)` is the primitive check; a Sentry alert lives here in V1).
- A downstream side-effect that should have happened after a producer commit didn't (e.g. a revealed winner didn't receive their email).

## Detection

- **Direct:** `SELECT event_name, count(*) FROM outbox_dead_letter GROUP BY event_name;` — anything > 0 warrants attention.
- **Worker logs:** grep for `outbox: dispatch failed permanently` — every dead-letter migration logs this at ERROR before the row moves.
- **User signal (winner_selected only):** the primary winner reports they never received an email. The audit event `notification.winner_selected` still fires (audit-before-delivery) so cross-reference `audit_log` first — if the audit event is present but no email landed and there is a dead-letter row, the SMTP path is the failure.

## Impact

- **Users:** varies by event. Winner-notification events have the highest impact (silent failure of the promised prize touch). All other event types are internal-only in V0.5.
- **Data:** none. `outbox_dead_letter` is terminal storage — no data is lost; the row + full payload sit there indefinitely until an operator acts.
- **Regulatory:** for prize-competition compliance, the primary-winner notification is expected within a reasonable window. A dead-letter row on `draw.winner_selected.v1` is a compliance incident if unresolved > 24h.

## Investigate

### 1. Snapshot the queue

```sql
SELECT
  id, event_name, aggregate_type, aggregate_id,
  attempts, LEFT(last_error, 200) AS error_head,
  created_at, moved_at
FROM outbox_dead_letter
ORDER BY moved_at DESC
LIMIT 50;
```

### 2. Identify the root cause

`last_error` is the exception message from the final dispatch attempt. Common shapes:

- `mailhog is down` / SMTP connection errors → mailhog/SES outage. Check the delivery service before replaying.
- `no handler registered for '<event_name>'` → the producer emitted an event that no consumer knows about. Fix: either register a handler in `atlas.outbox.dispatcher.HANDLERS` and redeploy, or delete the dead-letter rows if the event was emitted in error.
- `ValidationError: ...` → payload schema drift between producer and consumer. Fix on the producer side (schema is source of truth in `atlas.events`).
- Anything else → treat as a real bug. Reproduce locally with the full payload before replaying.

### 3. Check for a systemic outage

`SELECT event_name, count(*) FROM outbox_dead_letter WHERE moved_at > now() - interval '1 hour' GROUP BY event_name;` — a cluster of dead-letters in a short window points at a downstream provider (mailhog, later WhatsApp), not per-event bugs.

## Recover

### Replay a single row

The consumer must be idempotent (ADR-002 §Idempotency), so replay is safe. Steps:

1. Pick a dead-letter row: `SELECT * FROM outbox_dead_letter WHERE id = :dl_id;`
2. Re-insert into `outbox` with reset bookkeeping:
   ```sql
   INSERT INTO outbox
     (event_name, aggregate_type, aggregate_id, payload, correlation_id,
      created_at, processed_at, attempts, last_error, next_attempt_at)
   SELECT event_name, aggregate_type, aggregate_id, payload, correlation_id,
          now(), NULL, 0, NULL, now()
   FROM outbox_dead_letter WHERE id = :dl_id;
   ```
3. Delete the dead-letter row (or keep for forensic history — recommend keep; the space cost is negligible in V0.5):
   ```sql
   DELETE FROM outbox_dead_letter WHERE id = :dl_id;
   ```
4. Watch the worker log — the row should pick up on the next poll (default 1s).

### Replay a batch

Same idea, filtered by event_name and moved_at window. Batch replays SHOULD only run after the root cause is fixed — otherwise the rows re-fail and re-dead-letter within one retry cycle.

### Give up on a row

If replay is inappropriate (event was emitted in error, or the downstream side-effect is permanently impossible), archive with a note:

```sql
UPDATE outbox_dead_letter
SET last_error = COALESCE(last_error, '') || ' | archived-by=<operator> reason=<...>'
WHERE id = :dl_id;
```

Never `TRUNCATE outbox_dead_letter` — it's the last record of a failure. Grow a rotation policy when volume warrants (post-V1).

## Prevent

- Ensure every new outbox event registers a handler at the same PR as the producer landing (import-time registration in `atlas.outbox.dispatcher.HANDLERS` — a missing handler is a producer-side error caught by the writer's `EVENT_SCHEMAS` check only if the event isn't in the schema map either; register both).
- Payload schemas live in `atlas.events` — breaking changes require a new `.vN` per ADR-002 §Forward-compat, not an in-place rewrite.
- W9+ will land grep-CI enforcement that every domain-write path emits an outbox event (per week-8-build-plan §7 cross-week dependencies).

## Escalate

- SEV-3 → resolve within the shift, note in the daily standup.
- SEV-2 (a `draw.winner_selected.v1` row that's blocked > 4h) → page the on-call engineer, notify EL.
- SEV-1 (a real-money primary winner's notification blocked > 24h) → page EL + Compliance & Risk (Adaeze).
