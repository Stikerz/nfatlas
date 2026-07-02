# ADR-002: Outbox pattern for async work and inter-module events

**Status:** Approved
**Date:** 2026-06-29
**Approved by:** S1408661 (Engineering Lead) on 2026-07-02
**Reversibility:** Two-way door. Outbox can be swapped for a broker (Kafka, NATS) later without changing producer code.

## Context

V1's modules need to communicate asynchronously (e.g. `PaymentSucceeded` → credit the wallet, issue the ticket, kick off receipt email). The long-form PRD listed Redis Streams as an initial choice with Kafka as a future option. The V1 PRD (`PRD.md §4`) cuts both for V1 in favour of "an outbox table polled by a worker process."

This ADR commits to the outbox pattern, defines the schema and processing model, and explains why no broker ships in V1.

## Decision

Every state-changing operation that needs to trigger downstream work writes a row into an **outbox table** in the same database transaction as the state change. A separate **worker process** (running the same Docker image as the API, different command — see ADR-001) polls the outbox and dispatches each row to its consumer(s).

### Outbox table

```sql
CREATE TABLE outbox (
  id              BIGSERIAL PRIMARY KEY,
  event_name      TEXT NOT NULL,                  -- e.g. "PaymentSucceeded"
  aggregate_type  TEXT NOT NULL,                  -- e.g. "Payment"
  aggregate_id    TEXT NOT NULL,                  -- e.g. payment UUID
  payload         JSONB NOT NULL,                 -- the event body (schema in docs/events.md)
  correlation_id  TEXT,                           -- propagated request ID
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  processed_at    TIMESTAMPTZ,                    -- null until dispatched successfully
  attempts        INT NOT NULL DEFAULT 0,
  last_error      TEXT,
  next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX outbox_unprocessed_idx
  ON outbox (next_attempt_at)
  WHERE processed_at IS NULL;
```

### Processing model

- Worker polls every 1 second for unprocessed rows with `next_attempt_at <= now()`, locks them via `SELECT ... FOR UPDATE SKIP LOCKED`, and dispatches them in batches of 100.
- Dispatch = invoking the registered handler(s) for that `event_name`. Handlers are in-process function calls in V1 (the modular monolith).
- On success, `processed_at` is set.
- On failure, `attempts` increments, `last_error` is set, `next_attempt_at` is set to an exponential backoff (`min(60s * 2^attempts, 1h)`).
- After 10 failed attempts, the row is moved to `outbox_dead_letter` and a Sentry alert fires.

### Idempotency

- **Producers** are idempotent because the outbox write is in the same DB transaction as the state change — either both commit or neither does.
- **Consumers must be idempotent** because at-least-once delivery is the contract (a worker crash between dispatch and `processed_at = now()` re-delivers). Convention: every consumer either deduplicates on `(event_name, aggregate_id, idempotency_key)` or performs an idempotent upsert.

## Alternatives considered

- **Redis Streams.** Lost for V1: adds a second piece of stateful infra to operate. Outbox lives in the DB you already operate. Redis Streams becomes attractive when consumers are external services (V2 module extraction), at which point ADR amendment is the path.
- **Kafka / NATS / SQS.** Lost: same reason, more so. Brokered queues are correct when you've extracted services; premature when you haven't.
- **Synchronous in-process function calls only, no events.** Lost: makes module boundaries leaky (the call site of `credit_wallet` would need to know about every consumer). Outbox keeps producers ignorant of consumers.
- **Postgres LISTEN/NOTIFY for the dispatch trigger** instead of polling. Considered: gives lower latency than 1-second polling. Deferred to amendment if the 1-second floor becomes a UX problem; polling is simpler and reliably re-delivers if the worker restarts.

## Consequences

**Positive:**
- No new infrastructure beyond Postgres.
- Producer-consumer contract is the event schema in `docs/events.md`; switching to a real broker is a worker-side change.
- Replayability is free: re-set `processed_at = NULL` and the worker re-dispatches.
- Crash-safe: the outbox row commits with the state change; a worker crash never loses an event.

**Negative:**
- Adds load to Postgres (writes for every state change + polling reads). Mitigated by the partial index and `FOR UPDATE SKIP LOCKED`. Acceptable at V1 traffic; revisit if outbox table grows beyond ~10M rows.
- 1-second polling floor on event latency. Acceptable for V1's events (none are user-blocking in the latency-sensitive sense).
- Dead-letter handling is a manual operational task in V1 — runbook required (`docs/runbooks/outbox-dead-letter.md`, owned by DevSecOps).

**Forward-compat invariants:**
- Every state change emits an outbox event (enforced by grep in CI: any service method that writes to a domain table must also write to `outbox`).
- Event payload schema is in `docs/events.md` and versioned via the `event_name` (e.g. `PaymentSucceeded.v1`); breaking changes require a new version, not a payload rewrite.

V2 broker swap: a separate worker reads outbox rows and produces to the broker; existing consumers keep their in-process handlers until extracted.
