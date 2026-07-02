# ADR-003: Double-entry ledger schema and chart of accounts

**Status:** Proposed — pending EL approval + Finance Lead approval
**Date:** 2026-06-29
**Approval:** _to be signed off by Engineering Lead and Finance Lead (two-approval per `AINE-AGENTS.md §6`)_
**Reversibility:** One-way door. Once real money has flowed through the ledger, the schema can be extended but not restructured without a migration that re-balances historical entries.

## Context

The Wallet & Ledger module is the financial source of truth. The V1 PRD (`PRD.md §3.3`) commits to: single Naira balance, double-entry ledger, **no mutable balance field anywhere** — balance is always derived from journal entries.

This ADR commits the schema, the chart of accounts for V1, and the invariants that must hold.

## Decision

### Chart of accounts (V1)

V1 holds only money paid by the user — no bonus, cashback, or promo balances. Account types:

| Account type | Owner | Cardinality | Purpose |
|---|---|---|---|
| `user_wallet` | One per user | N | User's spendable Naira balance |
| `operator_revenue` | Operator | 1 | Net revenue from ticket sales |
| `prize_pool` | Per draw | N | Funds reserved for a draw's prize |
| `refund_payable` | Operator | 1 | Refunds owed but not yet remitted |
| `payment_gateway_clearing` | Per gateway | 1 (Paystack in V1) | Funds in flight between user and operator |
| `tax_payable` | Operator | 1 | WHT and other tax obligations accrued |

### Schema

```sql
CREATE TABLE ledger_accounts (
  id            UUID PRIMARY KEY,
  account_type  TEXT NOT NULL,              -- one of the types above
  owner_type    TEXT NOT NULL,              -- "user", "operator", "draw", "gateway"
  owner_id      TEXT,                        -- nullable for operator-level accounts
  currency      TEXT NOT NULL DEFAULT 'NGN',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (account_type, owner_type, owner_id, currency)
);

CREATE TABLE ledger_entries (
  id               BIGSERIAL PRIMARY KEY,
  transaction_id   UUID NOT NULL,           -- groups debits + credits of one logical operation
  account_id       UUID NOT NULL REFERENCES ledger_accounts(id),
  direction        CHAR(1) NOT NULL CHECK (direction IN ('D','C')),  -- Debit or Credit
  amount_minor     BIGINT NOT NULL CHECK (amount_minor > 0),         -- kobo (NGN minor unit)
  currency         TEXT NOT NULL DEFAULT 'NGN',
  posted_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  description      TEXT NOT NULL,
  external_ref     TEXT,                    -- e.g. Paystack reference
  idempotency_key  TEXT,                    -- client-supplied where applicable
  metadata         JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX ledger_entries_account_posted_idx
  ON ledger_entries (account_id, posted_at);

CREATE INDEX ledger_entries_transaction_idx
  ON ledger_entries (transaction_id);

CREATE UNIQUE INDEX ledger_entries_idempotency_idx
  ON ledger_entries (idempotency_key)
  WHERE idempotency_key IS NOT NULL;
```

### Invariants (enforced)

1. **No mutable balance field.** There is no `balance` column on `ledger_accounts` or `users`. Balance is `SUM(amount_minor * sign(direction))` over `ledger_entries` for that account. Enforced by a CI grep: any migration adding a `balance` column to a user-or-account-shaped table fails the build.
2. **Every transaction balances.** For each `transaction_id`, total debits = total credits in the same currency. Enforced by a database trigger on `INSERT` that defers and checks at COMMIT.
3. **Append-only.** `ledger_entries` rows are never updated or deleted. Corrections are *contra entries* (a new transaction that posts the inverse). Enforced by revoking `UPDATE` and `DELETE` privileges on the table for the application role.
4. **Idempotency.** Any client-supplied operation (ticket purchase, payment intent) provides an `idempotency_key`. The unique index on `idempotency_key` makes replays a no-op rather than a duplicate post.

### Balance query

```sql
SELECT
  SUM(CASE direction WHEN 'C' THEN amount_minor ELSE -amount_minor END) AS balance_minor
FROM ledger_entries
WHERE account_id = $1;
```

For account types where convention dictates a normal sign (e.g. `user_wallet` is normally a credit balance — money owed to the user), the sign flip is applied in the service layer, not the database.

### Reconciliation

A nightly job per `PRD.md §3.3` reconciles `payment_gateway_clearing` against Paystack's settlement report. Discrepancy beyond a tolerance threshold (defined in `docs/qa/strategy.md`) fires a SEV-1 alert and creates a Compliance & Risk review.

## Alternatives considered

- **Mutable `balance` column with optimistic locking.** Lost: every prize-platform horror story involves a balance that doesn't match journal history. Double-entry is the accountancy-grade answer; the storage cost is trivial.
- **Single-entry ledger** (just a log of changes). Lost: makes it impossible to answer "where did this money come from / go to" without parsing free-text descriptions. Double-entry makes counterparty explicit.
- **Bonus / cashback / promo accounts as separate account types in V1.** Lost: introduces convertibility rules (can bonus be withdrawn?), expiry rules, and tax classification questions that are not on the V1 critical path. Deferred to V2; V2 amendment to this ADR will define the additional account types.
- **Use a third-party ledger library (e.g. `ledger`, `Tigerbeetle`).** Lost: adds a runtime dependency for a problem that fits in ~200 lines of SQLAlchemy + a trigger. Re-evaluate at V2 scale.

## Consequences

**Positive:**
- The ledger is provably correct at any point in time by re-summing entries.
- Audits can ask any question and get a deterministic answer from journal data.
- Adding new transaction types (bonus, cashback, partner revenue share) in V2 is additive — new account types + new transactions, no schema rewrite.
- Reconciliation is exact (penny-accurate) rather than approximate.

**Negative:**
- Balance queries always run an aggregation. Mitigated by the composite index; at V1 scale (< 10M entries) sub-millisecond. At larger scale, a materialised view or per-account snapshot row is the V2 amendment, computed offline from authoritative entries (the snapshot is a *cache*, the journal is the truth).
- Every business operation must explicitly think in debits and credits. Mitigated by service-layer helpers (`record_ticket_purchase(user, amount, ...)`) that produce balanced transactions; ledger primitives are not called directly from route handlers.
- Two-approval gate on every ledger PR slows iteration. Accepted — the alternative cost (a wrong ledger post in production) is higher.
