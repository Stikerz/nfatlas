# Event catalogue

The producer–consumer contract for outbox events (ADR-002). `docs/AINE-AGENTS.md §4`
lists this file as a registry artefact owned by 🏗️ Winston, with 💻 Amelia, 🧪 Murat
and ⚖️ Adaeze as reviewers.

**Status:** created 2026-08-25 (W8 Day 5). ADR-001 §Consequences, ADR-002
§Outbox table and §Consequences, and `delivery-framework.md` all cite this path,
but the file had never been written — the schemas lived only in
`backend/src/atlas/events.py`. This documents what ships today; it is not a
design document, and adding an event means editing both this file and that module.

## How an event is declared

Every outbox-eligible event has three things, all in `atlas.events`:

1. A name constant carrying a `.vN` suffix.
2. A pydantic payload model with `extra="forbid"`.
3. An entry in `EVENT_SCHEMAS` mapping name → model.

`atlas.outbox.writer.emit` validates the payload against `EVENT_SCHEMAS[event_name]`
**before insert**, so a contract violation fails at the producer rather than in the
worker. `atlas.outbox.dispatcher.HANDLERS` maps the same name to its consumer.

Versioning is by name, not by payload rewrite (ADR-002 §Forward-compat invariants).
A breaking change needs a new constant, a new schema class, and a new handler
registration — the old version keeps working until its producers are migrated.

## Shipped events

### `notification.winner_selected.v1`

| | |
|---|---|
| **Producer** | `atlas.draw.service.reveal_draw` — one row per winner, written in the reveal transaction |
| **Consumer** | `atlas.notification.winner.deliver_from_payload` |
| **Schema** | `atlas.events.WinnerSelectedPayload` |
| **Since** | W8 Day 3 (2026-08-24) |

```python
draw_id:    UUID
winner_id:  UUID
ticket_id:  UUID
user_id:    UUID
position:   int      # 0 = primary, 1..n = reserves
is_primary: bool
prize_copy: str
```

Carries no PII beyond `user_id`. The consumer re-hydrates the winner's email from
the identity module at delivery time, so an outbox row is not a copy of personal
data at rest.

Ordering: rows for a single reveal share a transaction and are dispatched
independently. A reserve notification may be delivered before the primary — the
`position` field is authoritative, not arrival order.

## Planned

`delivery-framework.md §Event surface` names twelve V1 events: `UserRegistered`,
`KYCApproved`, `PaymentSucceeded`, `WalletCredited`, `TicketIssued`,
`FreeEntryTranscribed`, `DrawCommitted`, `DrawClosed`, `DrawRevealed`,
`WinnerSelected`, `PrizeClaimed`, `RefundIssued`.

Only the winner notification is implemented. **The others are not deferred by
design — they are simply not built yet**, and the ADR-002 forward-compat invariant
that "every state change emits an outbox event" is therefore not true today. See
ADR-002 §W8 execution amendment. The remaining producers and the CI grep gate that
would enforce the invariant are W9+ work.

Note that audit-log event names (`user.registered`, `otp.*`, `session.*`,
`draw.committed`, `draw.revealed`, …) are a **separate** namespace governed by
ADR-005 and written through `atlas.audit_log.writer`. They are not outbox events
and do not appear in `EVENT_SCHEMAS`.

## Cross-references

- [`docs/adr/ADR-002-outbox-pattern-for-async-work.md`](adr/ADR-002-outbox-pattern-for-async-work.md) — outbox decision + W8 execution amendment
- [`docs/adr/ADR-005-hash-chained-audit-log.md`](adr/ADR-005-hash-chained-audit-log.md) — the audit-log namespace, distinct from this one
- [`docs/runbooks/outbox-dead-letter.md`](runbooks/outbox-dead-letter.md) — what to do when a row exhausts its attempts
- `backend/src/atlas/events.py` — the authoritative schemas
