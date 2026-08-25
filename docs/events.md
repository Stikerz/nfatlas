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

## Producer inventory

W9 Day 1 (`week-9-build-plan.md §2`). ADR-002 §Consequences states as a
forward-compat invariant that *"every state change emits an outbox event
(enforced by grep in CI)."* This table is the basis for making that true, and
for the CI allowlist that enforces it.

**Method.** Not a count of `async def`. Every recorded state change in this
codebase goes through `atlas.audit_log.writer.append` by ADR-005 design, so the
28 `audit.append` call sites *are* the state-change surface — a more defensible
basis than function signatures, which mix reads, pure helpers and writes.

Counted 2026-08-25. One of the 28 has an outbox producer today.

### Must emit

Each has, or will have, work that happens *after* the transaction commits and
must survive a crash: a notification, a public surface update, or a downstream
module reacting. Framework names are from `delivery-framework.md §Event surface`.

| Audit event | Site | Framework name | Why async |
|---|---|---|---|
| `user.registered` | `identity/service.py:75` | `UserRegistered` | Welcome message; later the KYC kickoff |
| `otp.issued` | `identity/otp_service.py:140` | — | **The send is currently a direct call** at `identity/routes.py:89`. A failure is invisible and unretried — the same debt W8 closed for winner notification |
| `payment.confirmed` | `payment/service.py:224` | `PaymentSucceeded` | Receipt, and the fan-out other modules react to |
| `payment.failed` | `payment/service.py:293` | — | Failure notice to the payer |
| `wallet.deposit_credited` | `wallet/service.py:163` | `WalletCredited` | Balance-change notification |
| `wallet.prize_awarded` | `wallet/service.py:270` | — | Winner payout notification |
| `wallet.refund_issued` | `wallet/service.py:454` | `RefundIssued` | Refund confirmation |
| `ticket.issued` | `ticket/service.py:116` | `TicketIssued` | Ticket confirmation |
| `ticket.free_transcribed` | `ticket/service.py:301` | `FreeEntryTranscribed` | Confirmation on the free route — the entry path the legal model depends on |
| `draw.committed` | `draw/service.py:104` | `DrawCommitted` | Publishes the commitment; the trust story starts here |
| `draw.entries_snapshot` | `draw/service.py:188` | `DrawClosed` | Sales closed, tickets hash published |
| `draw.revealed` | `draw/service.py:302` | `DrawRevealed` | Public proof surface |
| `draw.winner_claimed` | `draw/service.py:410` | `PrizeClaimed` | Fulfilment kickoff |

**13 to migrate.** Ordering note: `wallet.*` and `payment.*` sit in
two-approval-gate modules (`AINE-AGENTS.md §6`), so they sequence last and may
slip to W10 by gate availability rather than effort — anticipated in
`week-9-build-plan.md §6` risk 3.

### Already emits

| Audit event | Site | Outbox event |
|---|---|---|
| `draw.winner_selected` | `draw/service.py:322` | `notification.winner_selected.v1` (`draw/service.py:346`) |

### Must not emit

Recording the reason matters as much as the classification — this list becomes
the CI allowlist, and an allowlist without reasons rots into a list of things
nobody dares touch.

| Audit event | Site | Reason |
|---|---|---|
| `otp.verified` | `identity/otp_service.py:209` | No work follows. The audit row is the record |
| `otp.verification_failed` | `identity/otp_service.py:228` | Security signal for the audit trail; no consumer |
| `user.password_set` | `identity/password_service.py:77` | No consumer today. Revisit if a security-notification channel lands |
| `session.created` | `identity/session_service.py:105` | Login is an audit fact, not a domain event |
| `session.revoked` | `identity/session_service.py:133` | As above |
| `payment.intent_created` | `payment/service.py:125` | Intent is not yet money. `payment.confirmed` carries the consequence |
| `payment.ticket_metadata_missing` | `payment/service.py:258` | Error signal for operators; belongs in the audit trail |
| `wallet.ticket_purchase_posted` | `wallet/service.py:222` | Internal double-entry movement, no external consumer |
| `wallet.ticket_sale_recorded` | `wallet/service.py:335` | As above |
| `wallet.payment_fee_posted` | `wallet/service.py:400` | As above |
| `ticket.paid_purchase_completed` | `ticket/service.py:163` | Same domain moment as `ticket.issued`, which carries it |
| `skill_question.issued` | `skill/service.py:164` | Question delivery is synchronous and user-facing |
| `skill_question.answered_correct` / `_wrong` | `skill/service.py:226` | Answer outcome is returned in the response; nothing follows it |
| `notification.winner_selected` | `notification/winner.py:31` | **This is the consumer**, not a producer. It records that delivery was attempted |

**14 sites, 15 event names** (the skill answer site emits one of two names).

### Whole modules excluded

- `atlas.audit_log` — the hash chain is synchronous by design (ADR-005). An
  async audit write would break the ordering the chain depends on.
- `atlas.outbox` — infrastructure. A producer that emitted about emitting would
  recurse.
- `atlas.idempotency` — infrastructure, no domain state.

### Status

- 28 state-change sites, 1 with a producer, **13 to migrate**, 14 correctly without one.
- **Pending 🏗️ Winston's review** before any migration, per `week-9-build-plan.md
  §5`. He owns this file (`AINE-AGENTS.md §4`) and the event names.
- The CI gate (Day 3) will encode the "must not emit" table as its allowlist.

---

## Cross-references

- [`docs/adr/ADR-002-outbox-pattern-for-async-work.md`](adr/ADR-002-outbox-pattern-for-async-work.md) — outbox decision + W8 execution amendment
- [`docs/adr/ADR-005-hash-chained-audit-log.md`](adr/ADR-005-hash-chained-audit-log.md) — the audit-log namespace, distinct from this one
- [`docs/runbooks/outbox-dead-letter.md`](runbooks/outbox-dead-letter.md) — what to do when a row exhausts its attempts
- `backend/src/atlas/events.py` — the authoritative schemas
