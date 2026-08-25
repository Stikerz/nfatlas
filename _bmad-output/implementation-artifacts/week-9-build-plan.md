# Week 9 Build Plan — Foundation week (outbox invariant + quality debt)

**Status:** approved 2026-08-25. All 5 asks resolved on recommendations — see §0.
**Start:** immediately, not the nominal Monday cadence (ask 5).
**Phase:** opens Phase 3 per `delivery-framework.md §7`.

---

## 0. Founder decisions

All 5 asks resolved on recommendations 2026-08-25.

| # | Ask | Decision | Impact |
|---|---|---|---|
| 1 | Foundation week, or Phase 3 Identity now? | **Foundation week** | Outbox invariant, events catalogue, flaky sweep, worker probes. Identity's remainder moves to W10, gated on ADR-007. |
| 2 | How complete must the producer sweep be? | **Option (b) — gate live with an honest allowlist** | Migration continues into W10. The gate stops the debt growing; the allowlist makes the remainder visible rather than invisible. |
| 3 | ADR-006 decrypt split | **Adaeze reads it first** | Not W9 scope. Compliance review is a §5 handoff; scheduling follows her verdict, not precedes it. |
| 4 | Does the flaky sweep gate the week? | **Best-effort, findings reported** | A 1.6% flake does not block a week. A second 47% one would be escalated. |
| 5 | Start date | **Immediately** | W8's five planned days ran across two calendar days; W9 follows on rather than waiting for 2026-08-31. |

§9 is retained as the record of what was asked and what was recommended.

---

## 1. Scope

W9 sits on a fault line. `delivery-framework.md §7` puts **Identity (weeks 9–10)**
at the start of Phase 3 — registration, OTP, login, MFA, KYC adapter,
self-exclusion. But that list was written before the V0.5 pivot, and §2 of the
same document notes Phase 3 was *"reshaped from greenfield module build to
real-launch completion of V0.5 … Phase 3 extends and hardens rather than starts
from scratch."*

Measured against the repo today:

| Phase 3 Identity item | State |
|---|---|
| registration, OTP, login | Built (W3), running in the demo |
| MFA | Not built |
| KYC adapter | Not built — no `kyc` symbol anywhere in `backend/src/atlas` |
| self-exclusion | Not built — no `self_exclusion` symbol anywhere |

So Identity is genuinely ~60% done, and the remainder is gated on ADR-007 (KYC
vendor), which is a Phase 0 procurement decision that has not landed.

**Decided (§0 ask 1): W9 is a foundation week; Identity's remainder starts W10.**

### In

**1. Close the ADR-002 outbox invariant.** This is the headline.

ADR-002 §Consequences states as a forward-compat invariant that *"every state
change emits an outbox event (enforced by grep in CI)."* The W8 execution
amendment records plainly that this is **not true today**. Measured:

- `outbox.emit` call sites in `backend/src/atlas`: **1** (`draw/service.py:346`)
- state-changing service functions across the 7 modules: **37**
- CI checks enforcing the invariant: **0**

W8 deferred this explicitly (`week-8-build-plan.md §0 ask 3`) on the grounds that
it *"needs a producer inventory pass first."* That pass is done — see §3.1.

Doing this **before** Phase 3 module work rather than after is the whole argument
for the recommendation: the per-module lifecycle in `delivery-framework.md §7`
makes "Architect updates `docs/events.md`" step 5 of every module. Building five
more modules against an unenforced invariant compounds the debt five times over
and makes the eventual sweep a cross-module refactor instead of a one-week job.

**2. `docs/events.md` becomes real.** Created W8 Day 5 because ADR-001, ADR-002
and `delivery-framework.md` all cite the path and it had never been written. It
currently documents 1 event and states plainly that the other eleven named in the
framework are not built. Every producer migrated in item 1 lands its schema here.
Owner is 🏗️ Winston per `AINE-AGENTS.md §4`; this week hands him a populated
catalogue rather than a stub.

**3. The flaky-test sweep.** Three flakes were found in W8, all one bug class — a
"make it different" step that can silently produce something identical:

| Test | Rate | Mechanism |
|---|---|---|
| skill-question answer collision | ~47% | first match in a flat set, `square root of 81` → `7` |
| `test_different_minute_may_rotate` | ~4% | 2 buckets on a 5-question pool |
| `test_tampered_signature_rejected` | ~1.6% | fixed `'X'` on a base64 signature |

The first was gating `v0.5-close.md` success gate #1, which means that gate was
passing on a coin flip. Three instances is a pattern, not a coincidence, so W9
sweeps the suite for the shape rather than waiting for the fourth to fail CI.

**4. Worker liveness/readiness probes** (`week-8-build-plan.md §7`). The outbox
worker's compose healthcheck is
`["CMD", "python", "-c", "import sys; sys.exit(0)"]` — it asserts that the
interpreter starts, nothing more. It reports healthy while the poll loop is
wedged, and W8 gate 6 leaned on it. Needed before any platform deploy, cheap now.

### Out (deferred, with the reason)

- **KYC adapter, MFA, self-exclusion** — Identity's remainder. Gated on ADR-007
  vendor selection, which is a Founder + Legal gate (`AINE-AGENTS.md §6`) and has
  not happened. Proposed for W10 if the vendor lands; otherwise MFA and
  self-exclusion can proceed without it and the adapter waits.
- **Splitting server-seed decrypt into its own process** — ADR-006 §W8 execution
  amendment records that decrypt is *not* worker-only as Stage 1 describes: the
  API process holds the key, so encryption at rest protects against a stolen dump
  but not against compromise of the API. That is a real gap in the trust story and
  it needs ⚖️ Adaeze before it is scheduled, not after. Surfaced as a §5 handoff.
- **Multi-key Fernet rotation with `key_version`** (`week-8-build-plan.md §7`) —
  no key has been rotated and none needs to be. Revisit when the first rotation
  is actually due, or at Phase 5 KMS envelope.
- **Per-event idempotency table** — gated on a founder ask W8 left open.
- **WhatsApp producer** — blocked on ADR-007, same as the KYC adapter.
- **Seven dead admin sidebar links** (`/admin/tickets`, `/free-entries`,
  `/claims`, `/users`, `/compliance`, `/skill-questions`, `/seed-tools`) — visible
  in `docs/VISUAL-WALKTHROUGH.md` §3. A product call for 📋 John and 🎨 Sally:
  build, hide, or mark coming-soon. Not engineering scope.
- **Pinning dev-tool floors** — `ruff>=0.7` resolved to 0.16.4 and `mypy>=1.13` to
  2.3.1, and that drift produced two of the W8 findings. Worth a constraints file,
  but it is a 30-minute job that can ride along with any week.

---

## 2. Day-by-day breakdown

### Day 1 — Producer inventory → decision table

- Enumerate every state-changing service function (§3.1 has the starting list) and
  classify: **must emit**, **must not emit**, or **already emits**.
- "Must not" needs a written reason per entry. Two are already known:
  `atlas.audit_log.writer` stays synchronous by design (ADR-005 — the hash chain
  cannot tolerate async), and `atlas.idempotency` is infrastructure, not domain.
- Output: `docs/events.md` §Producer inventory, reviewed by 🏗️ Winston before any
  code moves.

**Verified EOD:** every one of the 37 functions has a classification and a reason.

### Day 2 — Migrate the identified producers

- Each becomes `outbox.emit(<event>.v1, payload, session)` inside the caller's
  transaction, with a pydantic payload schema in `atlas.events` and a handler in
  `atlas.outbox.dispatcher`.
- Known first target: `identity/routes.py:89` still direct-calls
  `mailhog_sender.send_otp`. Same shape as the winner-notification debt W8 closed
  — a failure there is currently invisible and unretried.
- Payload discipline per the W8 precedent: carry ids, not PII. The consumer
  re-hydrates contact details at delivery time.

**Verified EOD:** every "must emit" function emits; `pytest` green; the rehearsal
still passes with the worker in the loop.

### Day 3 — The CI gate

- Add the `module-boundaries` job step ADR-002 promises. Shape follows the
  existing whitelist checks in `ci.yaml`: a grep with an explicit, commented
  allowlist, so adding a non-emitting state change is a visible diff.
- **Prove it fails.** Add a deliberately non-emitting state change on a scratch
  branch, confirm the job goes red, remove it. A gate never seen to fail is not
  known to work — the `get_secret_value` step sat red for four commits in W8 while
  enforcing nothing.

**Verified EOD:** gate green on `main`, and its failure mode demonstrated.

### Day 4 — Flaky-test sweep + worker probes

- Sweep `backend/tests` and `mobile/test` for the W8 bug class: a mutation step
  whose output can equal its input. Candidate greps: fixed substitutions on random
  data, `[:-n] + "literal"`, single-sample comparisons against a small modulus.
- Each finding gets the same treatment as the three already fixed — measure the
  rate, fix, prove the fix in both directions.
- Replace the worker's `exit 0` healthcheck with a real liveness signal: last
  successful poll timestamp, stale beyond N seconds fails.

**Verified EOD:** sweep findings listed with measured rates; worker healthcheck
fails when the loop is wedged, demonstrated by pausing it.

### Day 5 — Gates, log, docs

- §8 gates verified with evidence, not assertion.
- `docs/AI-INTEGRATION-LOG.md` session rows + W9 gate-close YAML.
- ADR-002 amendment updated: the forward-compat invariant moves from *"not true
  today"* to enforced, with the allowlist recorded.
- `docs/events.md` reflects the full catalogue.

**Verified EOW:** CI green on `main`; rehearsal green; ADR-002's invariant true.

---

## 3. Module contracts

### 3.1 Producer inventory — starting point

Counted 2026-08-25 from `backend/src/atlas/*/service.py`:

| Module | State-changing fns | Emits today |
|---|---|---|
| wallet | 10 | 0 |
| draw | 9 | 1 (`reveal_draw`) |
| ticket | 7 | 0 |
| payment | 5 | 0 |
| admin | 3 | 0 |
| skill | 2 | 0 |
| identity | 1 (+ `routes.py` direct-calls) | 0 |

Day 1's job is turning that count into a classified table. The number that matters
is not "37 producers" — it is however many survive classification, and some will
correctly be "must not emit".

### 3.2 New events (provisional)

Named from `delivery-framework.md §Event surface`, which lists twelve V1 events
against the one that exists. Final list is Day 1's output, not this plan's.

### 3.3 CI gate shape

Follows `ci.yaml`'s existing pattern: grep with a commented allowlist, error
message naming the fix. Consistent with `get_secret_value discipline (ADR-012)`
and the module-boundary checks around it.

---

## 4. Test strategy (for Murat 🧪)

**Backend:** 282 tests pass today. Each migrated producer needs: emits-in-same-
transaction, rolls-back-together, and payload-schema-validation-at-producer.
Regression: `demo_rehearsal.sh` green with the worker in the loop.

**The sweep is its own deliverable.** For each finding, the W8 discipline applies:
measure the failure rate before fixing, fix, then prove the fix in both directions
— a case that should pass and a case that should fail. Two of the three W8 flakes
were found only because someone looked at output rather than at a green tick.

**Not in W9:** load testing the worker (Phase 4), chaos-killing it mid-dispatch
(gated on the idempotency-table ask).

---

## 5. Handoffs and dependencies

**To 🏗️ Winston** — owns `docs/events.md` per `AINE-AGENTS.md §4`. Needs to review
the Day 1 classification before Day 2 migrates anything, and owns the event names.

**To ⚖️ Adaeze** — two items, both trust-story:
1. ADR-006 §W8 amendment, decrypt-not-worker-only. Needs a compliance read before
   any fix is scheduled. This is the one genuinely security-relevant gap W8 left.
2. Payload PII discipline on the new producers — W8 set the precedent of ids-only;
   confirm it holds for payment and wallet events.

**To 🛡️ Tobi** — the CI gate and worker probes are his domain per `AINE-AGENTS.md
§5` (CI gates, production deploy).

**To 📋 John + 🎨 Sally** — the seven dead sidebar links. Build, hide, or
coming-soon. Currently they 404 and are visible in the walkthrough.

**To 👤 Founder** — §9.

---

## 6. Risks

| # | Risk | Mitigation |
|---|---|---|
| 1 | Day 1 classification finds far more than 37 real producers, and Days 2–3 overrun | Classification is the deliverable; migration is scoped to what fits. A partial sweep with an accurate allowlist beats a rushed complete one. |
| 2 | The grep gate false-positives on legitimate non-emitters and blocks unrelated PRs | Same allowlist pattern as the existing ADR-012 check, which has held. Prove the failure mode Day 3. |
| 3 | Emitting from wallet/payment touches two-approval-gate modules (`AINE-AGENTS.md §6`) | Sequence those last; they need EL + Finance Lead. May slip to W10 by gate availability, not by effort. |
| 4 | The sweep finds a flake in a module nobody wants reopened | Report rate and mechanism; fixing is a separate call. Measuring is not optional. |

---

## 7. Cross-week dependencies

**W9 leaves for W10+:** Identity remainder (MFA, self-exclusion, KYC adapter once
ADR-007 lands); server-seed decrypt split pending Adaeze; multi-key Fernet
rotation; per-event idempotency table; WhatsApp producer.

**W9 unblocks:** every Phase 3 module, which per `delivery-framework.md §7` step 5
updates `docs/events.md` — cheap once the catalogue and the gate exist, expensive
if each module invents its own convention first.

---

## 8. Success gates

- [ ] Every state-changing service function classified, with a written reason for
      each "must not emit".
- [ ] Every "must emit" function emits in the caller's transaction.
- [ ] `docs/events.md` documents every event with producer, consumer and schema.
- [ ] CI grep gate live, **and its failure mode demonstrated**, not assumed.
- [ ] ADR-002 amendment updated: invariant enforced, allowlist recorded.
- [ ] Worker healthcheck fails when the poll loop is wedged, demonstrated.
- [ ] Flaky sweep complete; each finding has a measured rate and a two-directional fix.
- [ ] `demo_rehearsal.sh` green; 282+ tests green; CI green on `main`.
- [ ] W9 entry appended to `docs/AI-INTEGRATION-LOG.md`.

---

## 9. Asks to founder before Day 1 code starts

**Ask 1 — Is W9 a foundation week, or does Phase 3 Identity start now?**
Recommendation: foundation. Identity's remainder is gated on ADR-007, which has
not landed, and building five modules against an unenforced ADR-002 invariant
multiplies the debt. Counter-argument worth weighing: Phase 3 is eight weeks for
six modules and spending one on internals is real schedule.

**Ask 2 — How complete must the producer sweep be to call W9 done?**
Options: (a) every producer migrated; (b) gate live with an honest allowlist and
migration continuing into W10. Recommendation (b) — the gate is what stops the
debt growing; the allowlist makes the remainder visible instead of invisible.

**Ask 3 — ADR-006 decrypt split: schedule, or accept and document?**
Encryption at rest currently protects against a stolen dump or read-only DB
credential, not against compromise of the API process. Stage 1 of the ADR says
worker-only. Either amend the ADR to match what ships, or schedule the split.
Recommendation: get Adaeze's read first; this is her call more than mine.

**Ask 4 — Does the flaky sweep gate the week, or run best-effort?**
Recommendation: best-effort with a reported finding list. Rates are what matters;
a 1.6% flake is not worth blocking a week over, but a second 47% one is.

**Ask 5 — When does W9 start?**
W8's five planned days executed across two calendar days (2026-08-24 → 08-25).
Does W9 start immediately, or Monday 2026-08-31 on the nominal cadence?

---

## 10. Cross-references

- `_bmad-output/implementation-artifacts/week-8-build-plan.md` §7 (residuals), §0 ask 3
- `_bmad-output/planning-artifacts/delivery-framework.md` §7 (Phase 3, module lifecycle)
- `docs/adr/ADR-002-outbox-pattern-for-async-work.md` §Consequences, §W8 execution amendment
- `docs/adr/ADR-006-commit-reveal-protocol-and-public-entropy.md` §W8 execution amendment
- `docs/events.md` — catalogue this week populates
- `docs/AINE-AGENTS.md` §4 (artefact ownership), §5 (arbitration), §6 (gates)
- `_bmad-output/implementation-artifacts/v0.5-close.md` §Known follow-ups
