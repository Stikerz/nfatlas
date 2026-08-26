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

### `draw.winner_selected.v1`

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

## Naming and emission rules

🏗️ Winston, W9 Day 1 review. These are the rules the inventory below is
classified against.

### 1. Events are named for the producing domain

Three conventions were in play: ADR-002 §Forward-compat gives `PaymentSucceeded.v1`,
`delivery-framework.md §Event surface` lists `UserRegistered`, and the one shipped
event is `draw.winner_selected.v1`.

The shipped one wins on being real, but it is named for its **consumer**. That
couples the name to whoever happens to listen, and breaks the moment a second
consumer appears — a public-surface update on reveal, say, alongside the email.

**Rule:** `<producing-domain>.<what-happened>.v<n>`, lowercase and dotted. This
matches the 28 audit event names already in the codebase (`draw.committed`,
`wallet.deposit_credited`), so one convention spans both namespaces.

**Consequence:** the shipped event, formerly prefixed `notification.`, is
renamed `draw.winner_selected.v1`. Cheap now with one event and no production
data; 14× the work after W9 mints the rest. ADR-002's PascalCase example needs
an amendment to match — flagged, not silently diverged from.

**Renaming an event is a deploy-ordering hazard, and this rename demonstrated
it.** Performing it locally, `backend` was rebuilt and `worker` was not — they
are separate images. The new producer emitted into a worker whose `HANDLERS`
still held the old key, and all six rows dead-lettered on the first attempt
with `no handler registered`. No retry, because rule 2.

Producer and consumer share a process today, so one rebuild fixed it. They will
not always: ADR-002 §V2 anticipates extracting consumers to separate services.
Then an event rename becomes a two-phase deploy — consumer accepts both names,
producer switches, old name retired — and the `.vN` suffix exists precisely so
a rename is never needed for a payload change. Worth stating before someone
renames an event with real winners in the table.

### 2. An event with no handler is worse than no event

`outbox/worker.py:81-91` dead-letters an unregistered event on the **first
attempt** — no retry. So emitting an event whose consumer does not exist yet
does not "prepare for later": it manufactures dead-letter rows that are not
failures, which poisons the exact signal `runbooks/outbox-dead-letter.md`
tells operators to act on.

The alternative — a no-op handler per event — is machinery that carries a
payload schema and a handler for zero behaviour, and quietly redefines the
invariant as "we emit everything" rather than "everything that must survive a
crash does".

**Rule:** emit when a consumer exists. Where a state change will need one later,
the CI allowlist carries it with the trigger named.

### 3. ADR-002's invariant needs amending to something true

As written: *"every state change emits an outbox event."* Held literally, that
requires 12 no-op handlers today, for the reason in rule 2.

**Proposed wording:** *every state change that triggers work outside its own
transaction emits an outbox event.* That is enforceable, is what the pattern is
for, and is what the Day 3 CI gate will check. Amendment owed on ADR-002 — the
gate should not enforce a rule the ADR does not state.

### 4. `otp.issued` cannot go through the outbox as it stands

This one is worth reading in full, because it was the week's intended headline
migration and it does not survive contact with the identity module.

`identity/otp_service.py:5` states the invariant: *"Code storage:
HMAC-SHA-256(otp_pepper, code) — plaintext never persisted."* The database
holds `code_hash` only. `issue()` returns the plaintext code exactly once, to
its caller, which hands it straight to `send_otp`.

An outbox payload is a row in `outbox`. It persists until processed, and a
dead-lettered row persists **indefinitely** — that is the point of the
dead-letter table. So moving the send to the outbox means writing live OTP
codes into a readable table, and an attacker with DB read access gets account
takeover on every pending login. That trades an invisible-failure bug for a
credential-disclosure bug, which is not a trade worth making.

Three ways out, none of them Day 2 work:

- **Encrypt the code in the payload** (Fernet, as ADR-006 does for the server
  seed). The worker needs decrypt, so the key spreads to another process —
  which is the same concern ⚖️ Adaeze is already reviewing on ADR-006.
- **Move code generation into the consumer.** The producer emits "an OTP was
  requested"; the worker generates, hashes, stores and sends. Preserves the
  invariant and gains durability, but the API response currently returns
  `otp_id` and `expires_at`, which would no longer exist at response time.
  A real design, and a larger one than a migration.
- **Leave the send synchronous** and accept that an OTP delivery failure is
  invisible and unretried, as it is today.

**Decision: leave it synchronous for W9**, recorded here with the reason so it
is a considered position rather than an oversight. The second option is the
one I would build, and it belongs in the Identity work in W10 where the
module is already open.

### What this means for W9

Of the 13 classified "must emit":

- **11** have no consumer, and emitting to a no-op handler dead-letters on the
  first attempt (rule 2).
- **1** — `otp.issued` — has a consumer but cannot carry its payload safely
  (rule 4).
- **1** — `draw.winner_selected` — already emits.

So **W9 migrates nothing**, and that is the correct outcome rather than a
shortfall. The inventory was commissioned to find out what was really there;
it found that the gap ADR-002 describes is not 12 missing producers but 12
missing *consumers*, plus one security constraint nobody had written down.

What W9 still lands, and what actually moves the needle:

- the naming rule, applied before 13 more events are minted under three
  competing conventions;
- the amended ADR-002 invariant, so the rule the gate enforces is a rule the
  ADR states;
- the **Day 3 CI gate**, which is the thing that stops the debt growing — new
  state changes now have to be classified rather than quietly added;
- an allowlist that names the trigger for each deferred producer, so the
  remainder is visible instead of invisible.

That is closing the invariant correctly rather than performing it.

---

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
| `draw.winner_selected` | `draw/service.py:322` | `draw.winner_selected.v1` (`draw/service.py:346`) |

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
