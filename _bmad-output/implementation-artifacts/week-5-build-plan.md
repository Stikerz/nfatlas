# Week 5 Build Plan — Ticket module + first seed draw end-to-end

**Drafted:** 2026-07-21 (Week 4 close; Week 5 kickoff on founder sign-off)
**Drafted by:** 💻 Amelia (BMad Dev)
**Status:** **Approved 2026-07-22** — founder resolved all §9 asks on Amelia's recommendations; ready to start Day 1 Monday.
**Applies to:** V0.5 investor demo; Ticket + Draw-skeleton slices of the flagship flow (`v0.5-demo-plan.md §2.2, §2.4, §2.5, §2.10`).
**Pairs with:** `v0.5-demo-plan.md §5 Week 5`, `week-4-build-plan.md` (foundation — wallet, payment, webhook already live), `docs/adr/ADR-{003,004,005,006,008}.md`, `_bmad-output/planning-artifacts/design/wireframes/{02,04,10}.md`.

---

## 0. Founder decisions (2026-07-22)

Resolves §9 asks. All five adopted on Amelia's recommendations.

| # | Ask | Decision | Impact |
|---|---|---|---|
| 1 | Ticket payment path | **Direct-to-Paystack per ticket** | Each ticket = new Paystack checkout intent. `payment_intents.purpose` extended (`deposit` \| `ticket`). Wallet holds winnings + refunds only in V0.5. W4 `wallet.record_ticket_purchase` stays in the code but dormant; `WALLET_ALLOW_STUB_DRAW=false` in env=dev + env=test now that real `draws.id` exists. |
| 2 | Skill-question retry semantics | **New question, no penalty** | Wrong → next question served. Attempts logged for audit. Anti-abuse deferred to V1. |
| 3 | Skill-question pool source | **Hybrid: table now, no admin UI** | `skill_questions` + `skill_question_options` tables. Seed script populates 10 questions. Admin CRUD is a V1 ticket. |
| 4 | Free-entry slip reference format | **Any string, unique per draw** | DB unique index on `(draw_id, slip_reference)`. Real format is a Phase 3 counsel + printer decision. |
| 5 | Draw seed `server_seed` handling | **Plaintext in seed script + TODO(week-6)** | V0.5 doesn't run a real reveal; seed is a placeholder. TODO markers in migration comment + seed script. Encrypted-at-rest per ADR-006 §Stage 1 lands with the draw-engine module Week 6. |

Adaeze's items in §5 (skill-question standard clarity, free-entry parity by construction, audit-payload redaction) still owed by Day 4.

---

## 1. Scope

**In.**

- Migration 0006: `draws` (minimal — Week 6 draw engine extends), `skill_questions`, `skill_question_attempts`, `tickets`, `free_entry_slips`. `draws.commitment` + `server_seed_encrypted` present per ADR-006 §Protocol stages 1 but *the seed is generated and committed by the seed script, not the draw-engine module which lands Week 6*.
- `atlas.draw.models` + `atlas.draw.service` — read-only surface this week: `get(draw_id)`, `list_active()`, `is_sales_open(draw_id)`. Draw state machine (commit → sales_open → sales_closed → revealed) present in schema; only `sales_open` is exercised in V0.5 seed data. `close_draw` + `reveal_draw` are Week 6 wiring.
- `atlas.skill.service`: `next_question(user_id, draw_id)` (rotated deterministically from the seed pool with a per-user-per-draw offset), `verify_answer(attempt_id, choice_id)`. Attempts persisted for audit; a correct answer produces a short-lived (5-minute) `entitlement` token that the ticket-purchase route consumes.
- `atlas.ticket.service`: `issue_paid(session, *, user_id, draw_id, payment_intent_id, entitlement)`; `issue_free(session, *, actor_operator_id, subject_user_id, draw_id, slip_reference)`. Both go through a shared `_mint_ticket(...)` that assigns the next `ticket_number` (draw-scoped monotonically increasing per ADR-006 §Reserve algorithm — the ordered list matters for reveal).
- `atlas.payment.service.create_intent` extension: accepts an optional `purpose: Literal["deposit", "ticket"]` + `draw_id` + `entitlement_id`; on `purpose="ticket"`, the webhook handler mints the ticket in the same transaction as `record_deposit`-style crediting.
- Routes (all Idempotency-Key-required per ADR-004 §Scope):
  - `GET /api/v1/draws` — list draws with `state IN ('sales_open')` (V0.5: exactly one).
  - `GET /api/v1/draws/{id}` — detail (prize, close_time, entry counts split by paid/free, commitment).
  - `GET /api/v1/draws/{id}/skill-questions/next` — issue a skill-question attempt.
  - `POST /api/v1/skill-questions/attempts/{attempt_id}/answer` — submit answer.
  - `POST /api/v1/tickets/purchase` — mint a paid ticket (Idempotency-Key required per ADR-004 §Scope).
  - `POST /api/v1/tickets/free` — admin-only; mint a free ticket from a transcribed slip.
  - `GET /api/v1/tickets/me` — my tickets across all draws.
  - `GET /api/v1/users/me/wallet` — balance chip for mobile home (Week 4 held this back — arrives here).
- Seed script upgrade: `infrastructure/scripts/seed_v0_5.py` adds one `sales_open` draw (prize copy, close_time = demo-time + 3 days, ticket_price = ₦500), a pool of 10 skill questions, and the commit-phase artifacts (server_seed + commitment) per ADR-006 §Protocol stages 1.
- CI grep additions per §Module boundaries §3.4.
- Integration tests: real Postgres, full flagship-flow happy path + idempotency + skill-question rotation + free-entry-slip uniqueness.

**Out** (V0.5 stubs / deferred to Week 6+).

- Draw close + reveal (Week 6). Sales stay `sales_open` for V0.5.
- Real Bitcoin + drand entropy fetching (Week 6).
- Verifier CLI (`backend/tools/verify_draw.py`) — Week 6 alongside reveal.
- Multiple active draws (V1).
- Ticket cancellation / partial refunds (V1).
- Skill-question adaptive difficulty (V1).
- Anti-abuse: rate-limiting the skill-question attempts endpoint (V1 with the observability stack).
- Winner-claim UX (Week 7 polish).

---

## 2. Day-by-day breakdown

Each day ends demoable to founder over Zoom in < 3 minutes.

### Day 1 (Mon 2026-07-28) — Draw + skill-question schema + seed

- Migration 0006 `draws` + `skill_questions` (+ `skill_question_options`) tables.
- `atlas.draw.models` + `atlas.skill.models`.
- `atlas.draw.service.list_active` + `get(draw_id)` + `is_sales_open`.
- `infrastructure/scripts/seed_v0_5.py` extended with the seed draw + 10 skill questions + commit-phase artifacts per ADR-006 §Protocol stages 1. Seed script is idempotent (safe to re-run; drops+recreates by well-known IDs).
- `GET /api/v1/draws` + `GET /api/v1/draws/{id}` land with tests.
- Flip `ATLAS_WALLET_ALLOW_STUB_DRAW = false` in the seeded test env (real `draws.id` exists now — the stub gate is no longer needed and the founder decision from W4 §0.4 said "Week 5 flips the flag off as ticket module lands and real draws exist").

**Demoable EOD:** `curl http://localhost:8000/api/v1/draws` returns the seeded draw with commitment hash visible.

### Day 2 (Tue) — Skill question surface

- Migration 0006 adds `skill_question_attempts` (with `user_id`, `draw_id`, `question_id`, `issued_at`, `expires_at`, `answered_at`, `is_correct`, `entitlement_id`).
- `atlas.skill.service.next_question(user_id, draw_id)` — deterministic rotation: `question_index = HMAC(user_id || draw_id || attempt_epoch_minute) % pool_size` — same user in the same minute sees the same question (avoids "click refresh until you get an easy one"), across minutes rotates deterministically.
- `atlas.skill.service.verify_answer` — on correct answer, mints a 5-minute entitlement (opaque UUID stored on the attempt row; consumed by ticket purchase). On wrong answer, attempt marked `is_correct = false`; user can request a new question but the entitlement is not issued.
- `GET /api/v1/draws/{id}/skill-questions/next`
- `POST /api/v1/skill-questions/attempts/{attempt_id}/answer` (Idempotency-Key)
- Audit events: `skill_question.issued`, `skill_question.answered_correct`, `skill_question.answered_wrong`.

**Demoable EOD:** Postman-scripted user flow: register → login → GET next question → POST answer (wrong) → GET next question (rotates) → POST answer (correct) → response contains `entitlement_id` valid for 5 min.

### Day 3 (Wed) — Ticket module — paid path

- Migration 0006 adds `tickets` + `free_entry_slips`.
- `atlas.ticket.models` (LedgerEntry-adjacent — the mint is a single INSERT, ticket_number auto-assigned per draw via SEQUENCE).
- `atlas.ticket.service._mint_ticket(session, *, user_id, draw_id, entry_source, external_ref)` — the sole INSERT path. Grep-enforced.
- `atlas.ticket.service.issue_paid(session, *, user_id, draw_id, payment_intent_id, entitlement)` — consumes the entitlement, mints the ticket, sets `entry_source='paid'`.
- Extend `atlas.payment.service.create_intent` to accept `purpose="ticket" | "deposit"` (default `"deposit"` preserving W4 shape) + `draw_id` + `entitlement_id` in metadata. Webhook handler on `charge.success` with `metadata.purpose == "ticket"` calls `ticket.service.issue_paid` in the same transaction, then posts the fee as before.
- `POST /api/v1/tickets/purchase` — consumes an entitlement + creates a payment intent → returns `{payment_intent_id, checkout_url, expires_at}` (same shape as Day 3 W4 intent endpoint).
- `GET /api/v1/tickets/me` — user's tickets.
- Audit events: `ticket.paid_purchase_initiated`, `ticket.issued`.

**Demoable EOD:** Full flow: register → login → next-question → answer correctly → POST /tickets/purchase (returns checkout_url) → simulate webhook via `sign_paystack_webhook.py` → GET /tickets/me shows the newly-minted ticket with `entry_source: "paid"`.

### Day 4 (Thu) — Ticket module — free-entry path + wallet balance chip

- `atlas.ticket.service.issue_free(session, *, actor_operator_id, subject_user_id, draw_id, slip_reference)` — checks `free_entry_slips` uniqueness (grep + DB unique on `(draw_id, slip_reference)`), mints the ticket with `entry_source='free'`, records the operator actor.
- `POST /api/v1/tickets/free` — admin-only (uses the RBAC `superadmin` role check from Week 3 Day 5).
- `GET /api/v1/users/me/wallet` — the mobile-home balance chip. Returns `{ balance_minor, currency, last_updated_at }`. Reads via `wallet.queries.balance_of` on the user's `user_wallet` account.
- Audit events: `ticket.free_transcribed`.
- Runbook stub: `docs/runbooks/skill-question-abuse.md` — placeholder for V1 velocity checks; Week 5 has no rate-limit but the runbook documents the escalation path if abuse is suspected during demo.

**Demoable EOD:** Admin login → POST /tickets/free with a slip reference → user's `GET /tickets/me` shows the free ticket alongside their paid one. `GET /users/me/wallet` shows current balance.

### Day 5 (Fri) — E2E + wiring + Week 5 exit gates

- E2E integration test (`tests/e2e/test_flagship_flow.py`): register → login → wallet balance = 0 → skill question → purchase intent → signed webhook → ticket minted → wallet balance still 0 (ticket purchase debits operator_revenue side, NOT user_wallet — see §0.1 founder ask) → tickets list shows the paid ticket → operator transcribes free entry → tickets list shows the free ticket → audit chain intact across the full flow.
- CI grep additions:
  - `tickets` table writes outside `atlas.ticket.service` fail the build.
  - No direct manipulation of `draws.state` outside `atlas.draw.service`.
- Fresh-clone drill v3 with tickets in the path. Target < 15 min.
- Week 5 exit gates verified (§8).
- `_bmad-output/test-artifacts/test-design/week-5-tickets-draws.md` stub for Murat (Test Architect) — sequence diagrams + coverage matrix.

**Demoable EOW:** `git clone && make setup && make dev && make bootstrap && make demo-seed` → complete the flagship flow steps 1, 2, 4, 5, 10 from the demo plan end-to-end, all green.

---

## 3. Module contracts

### 3.1 Draw endpoints

| Method | Path | Idempotency | Purpose |
|---|---|---|---|
| `GET` | `/api/v1/draws` | n/a | Active draws (V0.5: exactly one). |
| `GET` | `/api/v1/draws/{id}` | n/a | Detail: prize, close_time, entry counts, commitment. |

### 3.2 Skill-question endpoints

| Method | Path | Idempotency | Purpose |
|---|---|---|---|
| `GET` | `/api/v1/draws/{id}/skill-questions/next` | n/a | Issue an attempt row + return the question. |
| `POST` | `/api/v1/skill-questions/attempts/{attempt_id}/answer` | required | Grade an answer; on correct, issue entitlement. |

### 3.3 Ticket endpoints

| Method | Path | Idempotency | Purpose |
|---|---|---|---|
| `POST` | `/api/v1/tickets/purchase` | required | Consume entitlement + create ticket-purpose payment intent. |
| `POST` | `/api/v1/tickets/free` | required | Admin-only: transcribe a free entry slip. |
| `GET` | `/api/v1/tickets/me` | n/a | User's tickets across draws. |

### 3.4 Wallet read

| Method | Path | Idempotency | Purpose |
|---|---|---|---|
| `GET` | `/api/v1/users/me/wallet` | n/a | Balance chip — kobo, currency, updated_at. |

### 3.5 Module boundary invariants (extend W4 §3.4)

- No INSERT/UPDATE/DELETE on `tickets` outside `atlas.ticket.service`. CI grep.
- No UPDATE on `draws.state` outside `atlas.draw.service`. CI grep.
- No INSERT on `free_entry_slips` outside `atlas.ticket.service`. CI grep.
- `skill_question_attempts.entitlement_id` is only ever set by `atlas.skill.service.verify_answer`, and only ever consumed by `atlas.ticket.service.issue_paid`. Grep both directions.
- `wallet.record_ticket_purchase` (Day 2 W4 helper) — decision below (§0.1) determines whether this remains live or is deprecated for V0.5.

---

## 4. Test strategy (for Murat 🧪)

Real Postgres end-to-end. Payment webhook uses the same signed-body fixture path from Week 4.

**Unit** (`backend/tests/unit/`):
- Skill-question rotation: deterministic per (user_id, draw_id, minute).
- Entitlement TTL: expired entitlements rejected.
- Ticket-number monotonicity (SEQUENCE per draw).

**Integration** (`backend/tests/draw/`, `backend/tests/skill/`, `backend/tests/ticket/`, `backend/tests/payment/`):
- All Day 2-4 scenarios above.
- `test_e2e_flagship_flow.py` (Day 5): the full end-to-end chain.

**Not in Week 5:**
- Draw reveal path (Week 6).
- Load / performance (V1).
- Multi-user concurrency on the same draw (V1).

---

## 5. Handoffs and dependencies

### To 🛡️ Tobi (DevSecOps)

- **Day 1 blocking:** confirm the seed-draw `server_seed` storage approach. V0.5 stores it plaintext in the seed script (source-controlled) so the demo is deterministic — the ADR-006 encrypted-at-rest requirement is a Week 6+ ticket. Confirm this is an acceptable V0.5 shortcut.
- **Day 4 non-blocking:** first pass at `docs/runbooks/skill-question-abuse.md`.
- **Day 5 non-blocking:** Fresh-clone drill v3 timing.

### To 🏗️ Winston (Architect)

- **Day 1 blocking (small):** sign off on the minimum `draws` state machine for W5 (`sales_open` only). Confirm the fuller ADR-006 state list is a Week 6 concern.
- **Day 3 blocking:** the payment-intent-purpose extension (deposit vs ticket) — confirm keeping one payment_intents table with a `purpose` column is preferable to two separate tables.
- **Day 4 blocking:** confirm the entitlement-token approach vs a stateful session-attribute approach for gating ticket purchase after skill-question success.

### To 🎨 Sally (UX)

- **Day 2 blocking:** the skill-question wireframe from `_bmad-output/planning-artifacts/design/wireframes/02-skill-question.md` — confirm the "wrong answer → new question, no penalty" copy is still current.
- **Day 4 non-blocking:** wallet balance chip copy — "Available: ₦X,XXX" vs "Balance: ₦X,XXX".

### To ⚖️ Adaeze (Compliance & Risk)

- **Day 2 blocking-ish (by Wed EOD):** confirm the skill-question mechanic as-implemented (multiple choice, no penalty for wrong answers, rotated pool) satisfies the "genuine skill test" standard for prize-competition status. If not, the mechanic changes — that would move the schedule.
- **Day 3 blocking-ish:** free-entry parity — the free entry must not disadvantage the paid entry in the draw pool (same odds per entry). Confirm the shared `tickets` table + shared `_mint_ticket` primitive satisfies this by construction.
- **Day 4 non-blocking:** free-entry audit-payload — what identifiers land on `ticket.free_transcribed`? Recommend `{slip_reference_hash, actor_operator_id, subject_user_id, draw_id}` — no PII on the entry slip itself beyond the hash.
- **Day 5 non-blocking:** review the E2E audit-chain output for gaps.

---

## 6. Risks

Ranked by likelihood × slip-impact.

1. **Skill-question standard clarity (Day 2, high likelihood, half-day slip if Adaeze pushes back).** UK Gambling Commission's "genuine skill" standard is not codified for Nigeria; counsel's Q1 opinion (per `legal/counsel-engagement-brief.md`) will land after Week 5. V0.5 uses the strictest interpretation (multiple choice from a curated pool + no penalty) but if Adaeze reads it differently, the mechanic must change.
2. **Payment intent purpose split (Day 3, medium likelihood, half-day slip).** Adding a `purpose` column to `payment_intents` may surface Week 4 assumptions that a payment intent is always a deposit. Grep for those before Day 3. *Mitigation:* Day 3 morning grep + tighten the webhook dispatch tests.
3. **Ticket-number monotonicity across concurrent purchases (Day 3, low likelihood, quarter-day slip).** V0.5 demo is single-user so no real contention, but the SEQUENCE-per-draw approach must be correct now — Week 6 draw-reveal reads the ticket list ordered by number and hashes it. *Mitigation:* SEQUENCE is Postgres's natural concurrency primitive; test with two concurrent tx.
4. **Free-entry slip reference collisions (Day 4, low likelihood, quarter-day slip).** DB unique index catches this. Test: attempt to submit the same slip twice → 409.
5. **Entitlement leakage across users (Day 3, low likelihood, high blast radius if it happens).** An entitlement issued to user A must not be redeemable by user B. *Mitigation:* entitlement is bound to `user_id` on the `skill_question_attempts` row; ticket purchase route asserts `attempt.user_id == session.user_id`. Test explicitly.
6. **Wallet-balance-chip stale reads under commit lag (Day 4, low likelihood, quarter-day slip).** `balance_of` is a SUM query — should see the just-committed rows. Confirm read-your-writes via a test that deposits + reads in sequence.

---

## 7. Cross-week dependencies

**Week 5 leaves in place for Week 6:**
- `draws.commitment` + `server_seed_encrypted` — the reveal path consumes these.
- `tickets` table with monotonic ticket_number per draw — winner-selection reads ordered by number.
- `atlas.draw.service` — extends with `close_draw` + `reveal_draw` (Week 6).
- `atlas.payment.service` — no schema changes; new payment_intent purposes only.

**Week 5 explicitly leaves for later:**
- Full draw state machine execution (Week 6).
- Bitcoin + drand entropy fetch (Week 6).
- Verifier CLI (Week 6).
- Multi-draw browsing (V1).
- Ticket cancellation (V1).
- Winner claim UX (Week 7).

---

## 8. Success gates (Week 5 exit criteria — for founder sign-off Fri EOD)

- [ ] Migration 0006 lands clean; `alembic upgrade head` from empty DB succeeds.
- [ ] `GET /api/v1/draws` returns the seeded draw with commitment hash.
- [ ] Skill-question flow: correct answer → entitlement; wrong answer → new question, no penalty.
- [ ] `POST /api/v1/tickets/purchase` requires + consumes a valid entitlement; entitlement is single-use.
- [ ] Signed test webhook with `metadata.purpose="ticket"` mints the ticket + posts the fee entry.
- [ ] `POST /api/v1/tickets/free` (admin) mints the ticket with `entry_source='free'`; slip is unique per draw.
- [ ] `GET /api/v1/tickets/me` shows both a paid and a free ticket for the demo user.
- [ ] `GET /api/v1/users/me/wallet` returns balance in kobo.
- [ ] E2E flagship-flow test green — full audit chain from register → paid ticket + free ticket.
- [ ] CI grep additions active: ticket writes, draws.state writes, free_entry_slips writes.
- [ ] CI green on push (backend, admin, mobile, module-boundaries).
- [ ] `ATLAS_WALLET_ALLOW_STUB_DRAW=false` in tests and dev — real draws exist now.
- [ ] `docs/AI-INTEGRATION-LOG.md` has entries for Week 5 Days 1-5.

---

## 9. Asks to founder before Day 1 code starts

**All 5 resolved 2026-07-22 — see §0.** Preserved below as historical record.

1. **Ticket payment path: direct-to-Paystack or wallet-first?**
   The demo plan §2.4 reads "Buy paid ticket → Paystack checkout → ticket appears" — implying each ticket = new Paystack checkout. Alternative: user deposits into wallet once, subsequent ticket purchases debit the wallet (matches `wallet.record_ticket_purchase` built Day 2 W4).
   **Recommendation: direct-to-Paystack per ticket.** Matches the demo plan verbatim; the wallet story becomes "wallet holds winnings (prize awards + refunds) rather than an intermediate purse". Simpler user mental model; less to explain in the demo. The Day 2 W4 `record_ticket_purchase` helper stays in the code for the V1 case where wallet-based purchase becomes real, but is not exercised in V0.5. `WALLET_ALLOW_STUB_DRAW` flag stays useful only for tests that still call this helper — flip to `false` for env=dev and env=test now that real `draws.id` exist.

2. **Skill-question retry semantics.**
   Options: (a) wrong answer → new question, no penalty (max friction is time); (b) wrong answer → same question, one more try then lockout for N minutes; (c) wrong answer → new question, but track attempts-per-user-per-draw for anti-abuse.
   **Recommendation: (a) — new question, no penalty.** Aligns with UK Gambling Commission's "genuine skill" bar as commonly interpreted (skill test, not a gate). Attempts are logged for the audit trail regardless; anti-abuse can be added V1 without changing the mechanic.

3. **Skill-question pool source.**
   Options: (a) hardcoded in the seed script (10-20 questions); (b) `skill_questions` table with admin CRUD; (c) hybrid — table now, no admin UI until V1.
   **Recommendation: (c) hybrid.** Table gives us the shape for V1 without building the admin UI now. Seed script populates 10 questions.

4. **Free-entry slip reference validation.**
   Options: (a) admin transcribes a free-text reference (postal code + date, or whatever the slip carries); (b) enforce a specific format (`FE-\d{8}` etc); (c) V0.5 accepts any string, unique-per-draw.
   **Recommendation: (c) — any string, unique per draw.** The real-slip format is a Phase 3 decision (needs counsel + printer sign-off). V0.5 needs the shape, not the format.

5. **Draw seed script — server_seed handling.**
   Options: (a) seed script generates a random `server_seed` and writes the plaintext into the DB (V0.5 shortcut, ADR-006 §Protocol stage 1 explicitly requires encrypted-at-rest); (b) seed script generates + encrypts with a demo key baked into the repo (defeats the point but matches shape); (c) seed script generates + prints the seed to stdout for founder to copy into a `.env` var read by the demo reveal.
   **Recommendation: (a) V0.5 shortcut.** V0.5 doesn't run a real reveal (Week 6 does); the seed is a placeholder. Add a `TODO(week-6)` in the seed script + the migration comment. Document as a debt item in the AI Integration Log.

Adaeze's items in §5 (skill-question standard, free-entry parity, free-entry audit payload) still owed by Day 4.

---

## 10. Cross-references

- `v0.5-demo-plan.md §5 Week 5`, §6 (success gates).
- `week-4-build-plan.md` — the foundation this plan extends (wallet, ledger, payment, webhook, RBAC).
- `docs/adr/ADR-003` (ledger schema), `ADR-004` (idempotency), `ADR-005` (audit chain), `ADR-006` (commit-reveal — Week 5 only touches stage 1), `ADR-008` (payment adapter).
- Wireframes: `02-skill-question.md`, `04-buy-ticket-skill-payment.md`, `10-my-tickets.md`.

---

💻 *End of Week 5 build plan. Awaiting sign-off on §9 (5 asks) to start Day 1 Monday 2026-07-28.*
