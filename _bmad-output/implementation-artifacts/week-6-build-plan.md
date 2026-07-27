# Week 6 Build Plan — Draw Engine (close, reveal, verify)

**Drafted:** 2026-07-27 (Week 5 close; Week 6 kickoff on founder sign-off)
**Drafted by:** 💻 Amelia (BMad Dev)
**Status:** **Approved 2026-07-27** — founder resolved all §9 asks on Amelia's recommendations; ready to start Day 1 Monday.
**Applies to:** V0.5 investor demo; the trust-story path — commit → sale → close → reveal → verify.
**Pairs with:** `v0.5-demo-plan.md §5 Week 6`, `week-5-build-plan.md` (foundation: draw skeleton, tickets, wallet), `docs/adr/ADR-{002,005,006}.md`, `_bmad-output/planning-artifacts/design/wireframes/{11,12,13,14}.md`.

---

## 0. Founder decisions (2026-07-27)

Resolves §9 asks. All five adopted on Amelia's recommendations.

| # | Ask | Decision | Impact |
|---|---|---|---|
| 1 | Entropy sources | **Hybrid: stub in tests+CI, live in demo** | `ATLAS_DRAW_ENTROPY_MODE=stub` (default) for tests + CI; `=live` for demo dev sessions. Live-mode fetch failure logs + falls back to stub with a visible banner. Investor demo shows real mempool.space + blockstream.info + drand fetch. |
| 2 | Reveal timing | **Skip 1h delay in V0.5 demo; honour in prod** | Reveal endpoint accepts admin override; `Settings.draw_reveal_delay_enforced` = false in dev + test, true in prod. Documented as demo shortcut in AI Integration Log. |
| 3 | Winner selection | **Rejection sampling** | Spec-correct per ADR-006. One extra loop; unbiased regardless of ticket count. Avoids V1 rewrite. |
| 4 | Admin surface | **Curl-only in W6, Next.js in W7** | Backend endpoints (POST /draws, /draws/{id}/close, /draws/{id}/reveal) are the interface. Founder demos via terminal + admin audit-log viewer. Frees ~1.5d for backend hardening. |
| 5 | Winner notification | **V0.5 shortcut with try/except** | `atlas.notification.notify_winner` sends via mailhog_sender from reveal handler; wrapped in try/except so SMTP failure never aborts reveal. `notification.winner_selected` audit event always fires. Full outbox is V1. |

Adaeze's items in §5 (winner-selection algorithm sign-off, proof-endpoint PII posture) still owed by Day 4.

---

## 1. Scope

**In.**

- `atlas.draw.state_machine`: guarded transitions `sales_open → sales_closed → revealed`. Illegal transitions raise typed errors. `commit → sales_open` is a Week 5 seed-time transition; Week 6 leaves the `draft → committed` path in the state enum but not wired to a route (V0.5 demo starts with a seeded `sales_open` draw).
- `atlas.draw.service.close_draw(draw_id)`: computes `tickets_hash = SHA-256(JCS-canonical(ordered_ticket_id_list))` per ADR-006 §Protocol stage 3. Writes `tickets_hash` + flips state to `sales_closed`. Emits `draw.entries_snapshot` audit event.
- `atlas.draw.entropy` module — public entropy fetch:
  - `bitcoin.py`: block-header fetch from **two independent explorers** (mempool.space + blockstream.info). Values must match or the reveal aborts. HTTP boundary mocked in tests; real fetch in demo dev mode behind `ATLAS_DRAW_ENTROPY_MODE=live` (default `stub` for tests + CI).
  - `drand.py`: League of Entropy randomness fetch with signature verification against the published group public key. Same live/stub gating.
- `atlas.draw.reveal.select_winners(server_seed, entropy, tickets_hash, ordered_ticket_ids, reserves=5)`: pure function per ADR-006 §Reserve algorithm. Deterministic HMAC-SHA-256 stream → distinct winning indices → ordered `[primary, r1, r2, r3, r4, r5]`. Unit tests with golden vectors.
- `atlas.draw.service.reveal_draw(draw_id)`: fetches entropy, decrypts server_seed, calls `select_winners`, writes winner + reserves rows to a new `draw_winners` table, flips state to `revealed`. Emits `draw.revealed` + `draw.winner_selected` audit events with the full proof inputs.
- Migration 0009: `draw_winners` (draw_id, position [0..N], ticket_id, user_id, is_primary, contact_status default 'pending', created_at). UNIQUE (draw_id, position). UNIQUE (draw_id, ticket_id).
- `POST /api/v1/draws/{id}/close` — admin-only + Idempotency-Key.
- `POST /api/v1/draws/{id}/reveal` — admin-only + Idempotency-Key.
- `GET /api/v1/draws/{id}/proof` — public (no auth). Returns full proof inputs per ADR-006 §Protocol stage 4: `commitment`, `server_seed` (post-reveal only), `bitcoin_hash`, `drand_round`, `tickets_hash`, `ordered_ticket_ids`, `winners[]`, algorithm reference.
- `backend/tools/verify_draw.py`: standalone verifier CLI. Accepts a draw_id (or a proof-JSON blob), re-runs `select_winners`, returns the same winner. Runnable without the full app stack.
- Winner notification stub: on `draw.winner_selected`, emit a `notification.winner_selected` event and (V0.5) send an email via Mailhog to the winner. `atlas.notification` skeleton module lands here.
- CI grep additions per §Module boundaries §3.4.
- Integration tests: real Postgres. Entropy stubbed at HTTP boundary. Deterministic golden vectors for winner selection.

**Out** (V0.5 stubs / deferred).

- Prize claim UX (Week 7 — mobile screen for the winner to submit claim details; V0.5 shows "claim received" state only).
- Real WhatsApp notification (V1).
- Full outbox refactor (ADR-002) — Week 6 posts notifications direct-call from the reveal handler; ADR-002 amendment notes the continuing debt.
- Nightly reconciliation cron (deferred to Week 7 or V1 — the `compute_diff` helper is already tested from W4).
- Encrypted-at-rest `server_seed` (V1). V0.5 continues to store hex plaintext per W5 §0 ask 5.
- Multi-currency prizes (V1).
- Bracket / multi-tier prizes (V1).
- Admin Next.js UI for close + reveal buttons (Week 7 — V0.5 demo can drive via curl; the endpoints are the interface).

---

## 2. Day-by-day breakdown

### Day 1 (Mon 2026-08-04) — Draw state machine + close_draw

- `atlas.draw.state_machine`: pure functions returning next-state given current + action; typed errors on illegal transitions.
- `atlas.draw.service.close_draw`: reads all ticket rows for the draw ordered by `ticket_number`, computes `tickets_hash`, writes to `draws.tickets_hash`, flips state to `sales_closed`. Emits `draw.entries_snapshot` audit event with `{draw_id, ticket_count, tickets_hash}`.
- Blocks new ticket inserts once state ≠ 'sales_open' (already enforced by `is_sales_open` guard in ticket.service — Week 5).
- `POST /api/v1/draws/{id}/close` route.
- Extend the CI ticket-write grep with a state-guard test: submitting to `/tickets/purchase` on a closed draw returns 409.
- Tests: happy path close; double-close is idempotent no-op; close-then-purchase returns 409; tickets_hash is deterministic (same tickets → same hash across runs).

**Demoable EOD:** `curl -X POST /api/v1/draws/{id}/close` (admin auth) → `GET /api/v1/draws/{id}` shows state='sales_closed' + tickets_hash populated.

### Day 2 (Tue) — Entropy adapters (bitcoin + drand)

- `atlas.draw.entropy.protocol`: `EntropyProvider` protocol with `fetch(close_time) → EntropyInputs` (bitcoin_hash + drand_round + verified_at).
- `atlas.draw.entropy.bitcoin`: fetch the first Bitcoin block header with `timestamp >= close_time` from mempool.space + blockstream.info; values must match or raise `EntropyMismatchError`.
- `atlas.draw.entropy.drand`: fetch drand round for the epoch >= close_time from the public League of Entropy endpoint. Verify BLS signature against the published group public key.
- `ATLAS_DRAW_ENTROPY_MODE`: `stub` (default, tests + CI) → returns deterministic canned values per draw_id; `live` (demo dev) → real HTTP fetch.
- Config additions: `atlas_draw_entropy_mode` + `atlas_drand_group_public_key` (optional in stub mode).
- Fixtures for stub mode: deterministic bitcoin_hash + drand_round per draw_id so verifier CLI runs stay reproducible.
- Tests: stub mode returns fixture shape; live mode with pytest-httpx mocks the two Bitcoin endpoints + drand endpoint; signature verify happy path + tamper-detection.

**Demoable EOD:** Python REPL: `EntropyProvider().fetch(...)` in stub mode returns a `(bitcoin_hash, drand_round)` tuple that's deterministic per draw_id.

### Day 3 (Wed) — Winner selection + reveal_draw

- `atlas.draw.reveal.select_winners` — pure function per ADR-006 §Reserve algorithm:
  ```
  prng_seed = HMAC-SHA-256(key=server_seed, msg=entropy || tickets_hash)
  # produces a deterministic byte stream in 32-byte blocks
  # each block interpreted as big-endian int, modulo ticket count
  # dedup across selections; produce N distinct indices
  ```
- Golden-vector tests: fixed inputs → fixed winner order. Any regression on the hash or the modulo math is caught.
- Migration 0009: `draw_winners` table.
- `atlas.draw.service.reveal_draw`: state guard (must be `sales_closed`), fetch entropy, decrypt server_seed (V0.5: read plaintext hex), read ordered tickets, call select_winners, insert winner rows in a single transaction, flip state to `revealed`, emit `draw.revealed` + `draw.winner_selected` audit events (one per winner).
- `POST /api/v1/draws/{id}/reveal` — admin-only + Idempotency-Key.
- Tests: reveal on `sales_open` returns 409; reveal on `revealed` is idempotent; golden-vector winner selection; audit events carry the full proof inputs.

**Demoable EOD:** close a draw → reveal it → `GET /api/v1/draws/{id}/winners` (a simple read endpoint added here) shows the winner + 5 reserves.

### Day 4 (Thu) — Proof endpoint + verifier CLI + notification stub

- `GET /api/v1/draws/{id}/proof` (public, no auth). Response includes: `commitment`, `server_seed`, `bitcoin_hash`, `drand_round`, `tickets_hash`, `ordered_ticket_ids`, `winners[]` (position + ticket_id + user_id_hash), algorithm reference URL (docs/adr/ADR-006). Only returns the full proof when state=`revealed`; pre-reveal returns `commitment` + `close_time` + `state` only.
- `backend/tools/verify_draw.py`: CLI that either reads `--proof <path.json>` from disk (offline verification) or `--proof-url <url>` to fetch and verify. Re-runs `select_winners`. Exits 0 on match, non-zero + diff on mismatch. Prints the recomputed winner ticket_id for cross-check.
- `atlas.notification` skeleton module: `notify_winner(user_id, draw_id)` sends via `mailhog_sender` (reuses W3's SMTP stub). Emits `notification.winner_selected` audit event. Called from reveal_draw's transaction.
- Runbook: `docs/runbooks/reveal-abort.md` — what to do if entropy fetch fails or explorers disagree.
- Tests: proof endpoint pre-reveal (minimal) vs post-reveal (full); verifier CLI happy path with golden-vector proof; verifier CLI mismatch exits non-zero.

**Demoable EOD:** `python backend/tools/verify_draw.py --proof-url http://localhost:8000/api/v1/draws/{id}/proof` → prints the winner + returns exit 0.

### Day 5 (Fri) — E2E + admin endpoints + exit gates

- `POST /api/v1/draws` (admin-only, Idempotency-Key): create a fresh `sales_open` draw. Generates server_seed via `secrets.token_bytes(32)`, computes commitment, stores hex plaintext (V0.5 shortcut). Emits `draw.committed` audit event.
- E2E integration test `tests/e2e/test_draw_lifecycle.py`: create draw → 3 users buy tickets (mix of paid + free) → close → reveal → GET /proof → verifier CLI re-runs against the returned proof → winner ticket_id matches.
- Fresh-clone drill v4: `git clone && make setup && make dev && make demo-seed && make demo-close-reveal` — the last make target runs a scripted close+reveal against the seeded draw for a deterministic demo.
- Week 6 exit gates verified (§8).
- Test-design stub extension for Murat: `_bmad-output/test-artifacts/test-design/week-6-draw-engine.md`.

**Demoable EOW:** the full Week 6 story: operator closes, reveals, publishes proof; verifier CLI independently reaches the same winner from the published inputs.

---

## 3. Module contracts

### 3.1 Draw admin endpoints

| Method | Path | Idempotency | Auth |
|---|---|---|---|
| `POST` | `/api/v1/draws` | required | superadmin |
| `POST` | `/api/v1/draws/{id}/close` | required | superadmin |
| `POST` | `/api/v1/draws/{id}/reveal` | required | superadmin |
| `GET` | `/api/v1/draws/{id}/winners` | n/a | any authed |

### 3.2 Public proof endpoint

| Method | Path | Idempotency | Auth |
|---|---|---|---|
| `GET` | `/api/v1/draws/{id}/proof` | n/a | **public** (no auth) |

### 3.3 Winner-selection contract

`select_winners(server_seed, bitcoin_hash, drand_round, tickets_hash, ordered_ticket_ids, reserves=5) → list[uuid.UUID]`

- Pure function; no I/O, no clock, no random source beyond inputs.
- Returns `[primary, r1, r2, r3, r4, r5]` — exactly `1 + reserves` distinct ticket IDs.
- Raises `NotEnoughTicketsError` if `len(ordered_ticket_ids) < 1 + reserves`.
- Golden-vector tests pin exact outputs for a fixed input set — any behaviour change is a red test.

### 3.4 Module boundary invariants (extend W5 §3.5)

- No direct construction of `DrawWinner` outside `atlas.draw.service`. CI grep.
- No `secrets.token_bytes` calls outside `atlas.draw.service` + `atlas.identity` (already existing). CI grep (whitelist).
- No `.state = ` mutations of `draws` rows outside `atlas.draw.state_machine.transition`. CI grep.
- Entropy providers only called from `atlas.draw.service.reveal_draw`. CI grep.

---

## 4. Test strategy (for Murat 🧪)

Real Postgres end-to-end. Entropy adapters stubbed at HTTP boundary via `pytest-httpx` (same pattern as Paystack adapter). Winner selection is pure — unit-tested with golden vectors.

**Unit:**
- `select_winners` golden vectors (multiple ticket-count + reserves configurations).
- HMAC stream determinism.
- Bitcoin explorer mismatch → `EntropyMismatchError`.
- drand signature tamper-detection.
- State-machine transition table.

**Integration:**
- Full close → reveal cycle with a seeded draw + N tickets.
- Idempotent close, idempotent reveal.
- 409 on illegal transitions.
- Proof endpoint pre- vs post-reveal shape.
- Verifier CLI against a real proof.

**E2E (Day 5):**
- The end-to-end lifecycle test above.

**Not in Week 6:**
- Load / performance testing (V1).
- Multi-draw concurrency (V1).
- Real drand signature-verification proof against network fetch (Week 6 in `stub` mode; live mode tests + demo run separately).

---

## 5. Handoffs and dependencies

### To 🛡️ Tobi (DevSecOps)

- **Day 1 blocking (small):** confirm the reveal endpoint stays admin-only + Idempotency-Key + local-only in V0.5. Real signed request-URL flow is V1.
- **Day 2 blocking:** confirm the two Bitcoin explorer choices (mempool.space + blockstream.info). Both are widely trusted; both have public rate limits. V0.5 makes exactly one request per reveal, so rate limits are not a concern.
- **Day 4 non-blocking:** first pass at `docs/runbooks/reveal-abort.md`.
- **Day 5 non-blocking:** fresh-clone drill v4 timing.

### To 🏗️ Winston (Architect)

- **Day 1 blocking:** confirm the state-machine approach — pure functions returning next-state, no shared mutable state. Confirms ADR-006 semantics.
- **Day 3 blocking:** review the `select_winners` implementation against ADR-006 §Reserve algorithm. Any deviation is a trust-story bug.
- **Day 4 blocking:** confirm the proof-endpoint shape — what MUST be public, what MUST NOT (e.g. user emails on winner rows — recommend hashing user_id).

### To 🎨 Sally (UX)

- **Day 3 non-blocking:** wireframe `12-reveal-draw.md` — confirm the "reveal complete" UI still shows the recomputable proof inputs prominently (public trust surface).
- **Week 7 handoff:** admin Next.js pages for close + reveal + audit-log viewer. V0.5 backend supports these; UI is Sally + Amelia Week 7.

### To ⚖️ Adaeze (Compliance & Risk)

- **Day 3 blocking-ish (by Wed EOD):** confirm the winner-selection algorithm satisfies "provably fair" + regulatory expectations for prize competitions. If the specific hash / modulo approach needs tweaking (e.g. rejection sampling vs modulo bias), that's a Day 3 fix.
- **Day 4 blocking:** proof-endpoint content — confirm hashed user_id (not raw) satisfies data-protection requirements while still allowing a claimant to verify their win by cross-referencing their user_id hash.
- **Day 5 non-blocking:** review the E2E proof + verifier output for any regulatory-disclosure gaps.

---

## 6. Risks

Ranked by likelihood × slip-impact.

1. **Modulo bias in winner selection (Day 3, medium likelihood, half-day slip).** Naive `int % ticket_count` biases early indices when 2^256 mod ticket_count ≠ 0. For prize-competition mechanics with small ticket counts (V0.5 demo has 1-3 tickets), the bias is negligible; for realistic V1 counts (thousands), rejection sampling is needed. *Mitigation:* implement rejection sampling from Day 3 — cost is one line of code, avoids a V1 rewrite.
2. **Bitcoin explorer disagreement (Day 2, low likelihood, quarter-day slip).** Reorgs happen; two explorers may briefly disagree. V0.5 demo runs in stub mode so this is moot; live-mode retries after 60s + fails hard if still disagreeing. Documented in the runbook.
3. **drand round selection off-by-one (Day 2, medium likelihood, quarter-day slip).** drand rounds tick every 30s; the "smallest round with epoch >= close_time" needs precise arithmetic against drand's start-time + period. *Mitigation:* use drand's own client library for the arithmetic if it's small, else golden-vector test the epoch → round calculation.
4. **Verifier CLI drift from backend implementation (Day 4, medium likelihood, half-day slip).** The verifier imports the same `select_winners` from `atlas.draw.reveal` — if the backend changes it, the verifier picks up the change automatically. *Mitigation:* Day 4 test asserts the CLI and the backend produce the same winner for a canned proof; regression on either surface catches it.
5. **Public proof endpoint leaking PII (Day 4, low likelihood, high blast radius).** A misspelled response schema could expose winner emails. *Mitigation:* explicit Pydantic response model with only the public fields; test asserts no email / phone_e164 in the response body.
6. **Reveal transaction size (Day 3, low likelihood, quarter-day slip).** A draw with 10,000 tickets inserts 1 winner + 5 reserves in one transaction — trivial. But the ordered-ticket-id read + tickets_hash computation happens on close, not reveal, so the reveal transaction stays small. *Mitigation:* already correct by design.
7. **Notification failure aborts the reveal transaction (Day 4, medium likelihood, half-day slip if we discover late).** Winner notification via SMTP inside the reveal transaction couples the reveal to Mailhog uptime. *Mitigation:* wrap the notification call in a try/except that logs the failure but does NOT abort the reveal. The `notification.winner_selected` audit event still fires; V1 outbox will make this asynchronous properly.

---

## 7. Cross-week dependencies

**Week 6 leaves in place for Week 7:**
- `draw_winners` table — Week 7 winner-claim UX reads from it.
- `GET /api/v1/draws/{id}/proof` — Week 7 public proof page consumes it.
- `atlas.notification` — Week 7 hardens with real WhatsApp integration (deferred to V1).

**Week 6 explicitly leaves for later:**
- Full outbox refactor (V1 with Phase 3 async work).
- Admin Next.js UI for close + reveal (Week 7 polish).
- Prize-claim state machine beyond `pending → contacted → claimed` (V1).
- Encrypted-at-rest server_seed (V1).
- Multi-tier prize brackets (V1).

---

## 8. Success gates (Week 6 exit criteria — for founder sign-off Fri EOD)

- [ ] Migration 0009 lands clean; `alembic upgrade head` from empty DB succeeds.
- [ ] `POST /api/v1/draws/{id}/close` produces a deterministic `tickets_hash` (same tickets → same hash across runs).
- [ ] `POST /api/v1/draws/{id}/reveal` produces the same winner + reserves for a fixed proof input set (golden vector).
- [ ] `GET /api/v1/draws/{id}/proof` returns the full proof for a revealed draw; returns minimal state pre-reveal; no PII in either shape.
- [ ] `python backend/tools/verify_draw.py --proof-url ...` re-runs the algorithm and reaches the same winner.
- [ ] E2E lifecycle test green: create → sell → close → reveal → verify.
- [ ] CI grep additions active: DrawWinner writes, secrets.token_bytes whitelist, .state mutations, entropy provider imports.
- [ ] `docs/runbooks/reveal-abort.md` exists in Draft.
- [ ] CI green on push (backend, admin, mobile, module-boundaries).
- [ ] `docs/AI-INTEGRATION-LOG.md` has entries for Week 6 Days 1-5 (owed by Paige — not blocking Amelia's exit).

---

## 9. Asks to founder before Day 1 code starts

**All 5 resolved 2026-07-27 — see §0.** Preserved below as historical record.

1. **Entropy sources — real fetch in demo, or stubbed?**
   Options: (a) full stub mode in V0.5 (deterministic fixtures per draw_id); (b) real fetch against mempool.space + blockstream.info + drand for the demo; (c) stub in tests + CI, real fetch in demo dev with a `ATLAS_DRAW_ENTROPY_MODE=live` flag.
   **Recommendation: (c) hybrid.** Tests + CI stay deterministic and fast; demo actually shows real Bitcoin + drand fetching (much better story for investors — "here's the block header from mempool.space, here's the drand signature verifying"). Failure of a live fetch during demo drops back to stub with a visible banner.

2. **Reveal timing constraint (ADR-006 says ≥ T+1h after close).**
   Options: (a) enforce the 1-hour delay literally (demo pauses); (b) honour the delay for real launches but skip in V0.5 demo mode; (c) shorten to T+1min for demo purposes with a config flag.
   **Recommendation: (b).** V0.5 demo mode ignores the constraint; the reveal endpoint accepts an admin-supplied override. Production hardening reads the flag from config and enforces the 1-hour minimum. Document the demo shortcut in the AI Integration Log.

3. **Winner selection: modulo vs rejection sampling.**
   Options: (a) naive `int % ticket_count` (fastest, biased); (b) rejection sampling (spec-correct; one extra loop); (c) constant-time reduction (overkill).
   **Recommendation: (b) rejection sampling.** Cost is one line; avoids a V1 rewrite when Adaeze reads the algorithm.

4. **Admin surface: curl-only or minimal Next.js page for close + reveal?**
   Options: (a) V0.5 demo drives close + reveal via curl (backend endpoints are enough); (b) minimal Next.js admin page in W6 (form + button); (c) full Next.js admin surface in W6 (deferred W7 polish per plan).
   **Recommendation: (a) curl-only for W6.** Week 7 owns admin UI polish per demo plan §5. Founder can demo via curl in one terminal + the admin log viewer in another. Saves 1-1.5 days of frontend work.

5. **Winner notification: send email in W6 or defer to W7?**
   Options: (a) send Mailhog email from reveal handler (V0.5 shortcut, coupled to SMTP); (b) audit event only in W6, notification consumer lands W7; (c) full outbox pattern with async worker (V1).
   **Recommendation: (a) V0.5 shortcut, hardened.** Send email inside try/except so notification failure never aborts the reveal. `notification.winner_selected` audit event still fires. Full outbox is V1.

Adaeze's items in §5 (winner-selection algorithm sign-off, proof-endpoint PII posture) still owed by Day 4.

---

## 10. Cross-references

- `v0.5-demo-plan.md §5 Week 6`, §2 (steps 6, 9, 11, 12, 13, 14).
- `week-5-build-plan.md` — foundation this plan extends (draw skeleton, tickets, wallet).
- `docs/adr/ADR-002` (outbox — still deferred), `ADR-005` (audit chain), `ADR-006` (commit-reveal — Week 6 exercises stages 3-4-5).
- Wireframes: `11-close-draw.md`, `12-reveal-draw.md`, `13-audit-log-admin.md`, `14-public-proof-page.md`.

---

💻 *End of Week 6 build plan. Awaiting sign-off on §9 (5 asks) to start Day 1 Monday 2026-08-04.*
