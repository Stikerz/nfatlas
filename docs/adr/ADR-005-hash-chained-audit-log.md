# ADR-005: Hash-chained append-only audit log

**Status:** Approved
**Date:** 2026-06-29
**Approved by:** S1408661 (Engineering Lead + Compliance Lead, sole founder) on 2026-07-02
**Reversibility:** One-way door once production data is present.

## Context

A prize-competition platform whose trust positioning is "Africa's most trusted" must be able to prove, after the fact, that a draw ran as specified, that no entries were inserted or removed after sale close, and that audit records have not been tampered with. The Compliance & Risk Agent (per `AINE-AGENTS.md`) is required to verify audit-log integrity after every real-money draw.

This ADR commits the audit-log mechanism.

## Decision

A single append-only `audit_log` table records every consequential event in the system, hash-chained so any retroactive modification is detectable.

### Schema

```sql
CREATE TABLE audit_log (
  seq            BIGSERIAL PRIMARY KEY,        -- monotonic sequence
  occurred_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  actor_type     TEXT NOT NULL,                -- "user", "operator", "system", "agent"
  actor_id       TEXT,                          -- user UUID, operator UUID, agent name, "system"
  event_name     TEXT NOT NULL,                -- e.g. "draw.committed", "ticket.issued"
  subject_type   TEXT NOT NULL,                -- e.g. "draw", "ticket", "user"
  subject_id     TEXT NOT NULL,
  payload        JSONB NOT NULL,                -- the event-specific data
  prev_hash      TEXT NOT NULL,                 -- hash of the previous row (or genesis)
  row_hash       TEXT NOT NULL                  -- hash of (prev_hash || canonical(this_row))
);

CREATE UNIQUE INDEX audit_log_row_hash_idx ON audit_log (row_hash);
```

### Hash chain

Each row's `row_hash` is computed as:

```
canonical = JCS-canonicalize({
  seq, occurred_at, actor_type, actor_id, event_name,
  subject_type, subject_id, payload, prev_hash
})
row_hash = SHA-256(canonical)
```

(JCS = JSON Canonicalization Scheme, RFC 8785.)

The first row's `prev_hash` is the literal string `"GENESIS"`.

### Append-only enforcement

- The application role has `INSERT` only on `audit_log`. `UPDATE` and `DELETE` are revoked.
- A trigger on `INSERT` verifies that `prev_hash` matches the `row_hash` of the row with the previous `seq`. Insertions that don't chain correctly are rejected.
- The trigger also verifies that `row_hash` correctly hashes the canonical row content.

### What goes in the audit log

V1 events (non-exhaustive; the full catalogue lives in `docs/compliance/audit-log-spec.md`):

- `draw.committed` — server-seed commitment hash published.
- `draw.entries_snapshot` — full ticket list hashed at sale close.
- `draw.revealed` — server seed and entropy inputs revealed.
- `draw.winner_selected` — deterministic algorithm output with reserve list.
- `ticket.issued` — every paid or free-entry ticket.
- `payment.confirmed` — Paystack webhook accepted.
- `kyc.approved`, `kyc.rejected`, `kyc.flagged`.
- `self_exclusion.activated`.
- `prize.claimed`, `prize.fulfilled`.
- `operator.role_granted`, `operator.role_revoked`.
- `refund.issued`.
- `migration.applied` (every Alembic migration in production).
- `rbac.permission_used` for sensitive operator actions (e.g. KYC manual override).

### Verification

A scheduled job runs nightly: re-hashes every row in sequence and verifies the chain. A break fires a SEV-1 Compliance & Risk alert.

After every real-money draw, Compliance & Risk Agent runs a verification report against the audit log for that draw's `subject_id` and attaches it to the draw's `docs/compliance/reviews/` entry.

### Export

The audit log is exportable to JSONL (per draw, per user, or full) via an operator endpoint behind a two-approval gate. Each export includes the genesis hash and the final row's `row_hash` so an external verifier can independently re-hash the chain.

## Alternatives considered

- **External append-only service (AWS QLDB, Hyperledger).** Lost for V1: adds vendor and operational surface area for a problem solvable in-DB. Re-evaluate at multi-region V2.
- **Sign each row with an operator private key.** Considered: would give non-repudiation against an external party. Lost for V1: key management is itself a risk; hashing chain plus the periodic export to off-platform storage (S3 with object-lock) is the V1 stance.
- **Hash chain only on the draw module's events, not platform-wide.** Lost: draws aren't the only place trust can leak. KYC overrides, RBAC grants, refunds all benefit from the same integrity guarantee.
- **Synchronous external timestamping (RFC 3161).** Considered: adds external-party timestamp evidence per row. Deferred to V2 amendment — the periodic export to object-lock storage gives a sufficient anchor for V1.

## Consequences

**Positive:**
- Tamper-evidence: any retroactive `UPDATE` or `DELETE` breaks the chain and is caught by the nightly job.
- Single mechanism across modules; operators, agents, and the system all log to the same chain.
- Exportable proof for legal counsel or regulators.

**Negative:**
- The trigger adds a small cost per insert. Acceptable; the audit log is write-volume modest (estimated < 10k rows per active day at V1 scale).
- Schema evolution of `payload` shapes is fine (JSONB), but a payload schema change must be additive — old rows must still verify against the canonical form they were hashed with.
- An accidentally deleted row (e.g. via a manual DBA action) breaks the chain and requires Compliance & Risk involvement to triage. Mitigated by the `INSERT`-only application role and a DB-admin runbook.

**Invariants:**
- Every event in the catalogue (`docs/compliance/audit-log-spec.md`) must appear in `audit_log` for the relevant subject. Missing events are CI-flagged via integration tests that exercise the trigger paths.
- Nightly chain-verification job is operational from Phase 2.
- Compliance & Risk Agent verifies the chain over a draw's events before a winner is announced publicly.
