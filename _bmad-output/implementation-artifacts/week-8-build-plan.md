# Week 8 Build Plan — V1 hardening kickoff (server_seed + outbox + fallback recording)

**Drafted:** 2026-08-21 (V0.5 close + 3 weeks, after re-rehearsal confirmed green)
**Drafted by:** 💻 Amelia (BMad Dev)
**Status:** **Approved 2026-08-21** — founder resolved all §9 asks on recommendations (see §0). Day 1 kickoff 2026-08-24.
**Applies to:** first V1 hardening slice on top of the V0.5 demo baseline.
**Pairs with:** `v0.5-close.md §Known follow-ups`, `ADR-006 §Stage 1` (server_seed encrypted at rest), `ADR-002` (outbox), `ADR-012 §V1 mechanism` (secret manager).

---

## 0. Founder decisions

All 5 asks resolved on recommendations 2026-08-21.

| # | Ask | Decision | Impact |
|---|---|---|---|
| 1 | Week 8 scope split | **Hardening + fallback recording bundled** | Days 1-3 encrypted-seed + outbox; Day 4 Playwright recording + rehearsal; Day 5 gates + docs sync. |
| 2 | Server-seed encryption vendor | **Fernet (`cryptography.fernet`) keyed from `ATLAS_SERVER_SEED_KEY`** | New `atlas.draw.crypto` module. Aligns with ADR-012 env-var pattern; forward-compat with a cloud-KMS envelope in Phase 5. |
| 3 | Outbox scope for W8 | **Foundation + winner-notification producer only** | Writer + worker + one producer migrated + one runbook. Grep-CI enforcement + full producer sweep deferred to W9. |
| 4 | Playwright screen-recording script | **Build now, half-day cap, OBS fallback** | `infrastructure/scripts/record_demo.py`. If Chromium install stalls under Zscaler, pivot to OBS runbook. |
| 5 | Fresh-clone drill v6 | **Defer to a second-engineer laptop drill** | On this laptop the drill measures Zscaler, not Atlas — per [[feedback-zscaler-local-only]]. Not on the W8 punch-list. |

Adaeze's items in §5 (server-seed key handling, outbox event PII) owed by Day 2. Winston consult on the outbox producer boundary Day 3.

---

## 1. Scope

**In.**

- **Encrypted `server_seed` at rest** per ADR-006 §Stage 1 first bullet. Today `draws.server_seed_encrypted` stores plaintext hex (`atlas.draw.service.py:100`). W8 flips the column to encrypted-at-rest via Fernet, keyed from `ATLAS_SERVER_SEED_KEY` (32 url-safe bytes). Column keeps its name; the read/write helpers move into a single `atlas.draw.crypto` module. Migration re-encrypts any existing row on upgrade (V0.5 seeded draws only). Decrypt path used by reveal (`service.py:251`) and by the proof endpoint (`service.py:313`).
- **Outbox foundation** per ADR-002 — first slice, not the full grep-CI-enforced version:
  - Migration 0010: `outbox` table matching the ADR-002 §Decision schema.
  - `atlas.outbox.writer.emit(event_name, payload_json, session)` — the sole write helper. Same-transaction with the caller's DB session, per ADR-002 §Idempotency.
  - `atlas.outbox.worker` — a long-lived polling loop using `FOR UPDATE SKIP LOCKED`, exponential backoff, 10-attempt dead-letter migration.
  - First producer migrated: **winner notification**. `reveal_draw` currently direct-calls `notify_winner` with try/except (`service.py:348`, kept as a V0.5 debt in `AI-INTEGRATION-LOG.md §Kept-in-code shortcuts`). W8 replaces this with `outbox.emit("notification.winner_selected.v1", ...)`; the worker consumes and calls the existing `mailhog_sender.send_notification`.
  - Runbook: `docs/runbooks/outbox-dead-letter.md` per ADR-002 §Trade-offs bullet 3.
  - **Out of W8:** grep-CI enforcement that every state-change writes an outbox row (that's W9 — needs a producer inventory pass first).
- **Playwright screen-recording script** (deferred W7 §0 ask 4). `infrastructure/scripts/record_demo.py` — headless Chromium walks register → skill → pay (webhook-driven) → admin close → admin reveal → public `/proof`. Saves mp4 to `_bmad-output/demo/atlas-hero-flow.mp4`. Half-day cap; if it stalls, OBS remains the fallback.
- **AI Integration Log entry for Week 8** appended at close per `AINE-AGENTS.md §7`.
- **Cross-week residuals from `v0.5-close.md`** I can action from this laptop:
  - Gate 4 (verifier reproduces winner) already re-verified 2026-08-21 in today's rehearsal. Line item closed.
  - Gate 8 (screen-recording fallback) lands as scope bullet 3 above.
  - Gate 5 (design pass sign-off) is a Sally-and-founder walkthrough — surfaced as a §5 handoff, not W8 code.
  - Gate 6 (founder walks demo 20+ times) is a founder activity — surfaced as a §5 handoff.

**Out** (deferred to W9+):

- Full outbox grep-CI enforcement + migration of all remaining direct-call sites (`atlas.identity` OTP send, any payment webhook side-effects, `atlas.audit_log` writer stays direct per ADR-005 — the audit chain is intentionally synchronous).
- Multi-draw browse (V1).
- WhatsApp notification channel (V1 — separate producer once the outbox exists).
- Prize-claim state machine beyond `pending → contacted → claimed` (V1).
- Refund UX (V1).
- Admin RBAC 5-role split (V1).
- Real KYC vendor swap (V1 per ADR-007).
- Sentry / observability (Phase 5 per ADR-011).
- Fresh-clone drill on this laptop — see §0 ask 5 recommendation.
- Corporate-proxy docker-build fix — local-env only, not project scope ([[feedback-zscaler-local-only]]).

---

## 2. Day-by-day breakdown

### Day 1 (Mon 2026-08-24) — `atlas.draw.crypto` + Fernet-encrypted server_seed

- New module `backend/src/atlas/draw/crypto.py`:
  - `encrypt_server_seed(seed: bytes) -> str` — returns Fernet token string.
  - `decrypt_server_seed(token: str) -> bytes` — raises on tamper (Fernet enforces HMAC).
  - Key sourced from `Settings.server_seed_key` (32 url-safe bytes b64). Config validator refuses empty in dev/staging/prod (test may stub).
- `atlas.draw.service.commit_draw` — encrypt before write.
- `atlas.draw.service.reveal_draw` + `proof_for_draw` — decrypt on read.
- Migration 0010: no schema change; **data migration** re-encrypts any existing `server_seed_encrypted` value that decodes as raw hex (32 bytes). Idempotent — a second run detects Fernet token prefix and no-ops.
- Config: `ATLAS_SERVER_SEED_KEY` added to `.env.example` with the "generate via `cryptography.fernet.Fernet.generate_key()`" comment.
- Tests: round-trip encrypt/decrypt; tamper rejects; commit → reveal → proof still produces the same primary winner (golden-vector regression); empty key fails startup.
- Module docstring update in `atlas.draw.models` — remove the V0.5 plaintext debt note (`models.py:5-10`).
- `AI-INTEGRATION-LOG.md §Kept-in-code shortcuts` — strike-through the "`server_seed` stored as plaintext hex" bullet.

**Verified EOD:** `pytest -k "encrypt or reveal"` green; a fresh `make demo-reset` (or the native-venv equivalent) seeds a draw whose `server_seed_encrypted` column is a Fernet token, not hex; `reveal_draw` reproduces the pre-W8 primary for the golden-vector seed.

### Day 2 (Tue) — Outbox table + writer + tests

- Migration 0011: create `outbox` per ADR-002 §Decision (`id`, `event_name`, `payload`, `created_at`, `next_attempt_at`, `attempts`, `processed_at`, `error`); partial index `outbox_unprocessed_idx` on `next_attempt_at WHERE processed_at IS NULL`. Also `outbox_dead_letter` with the same shape + `moved_at`.
- `atlas.outbox.writer.emit(session, event_name, payload)` — inserts the row on the caller's session; commit is the caller's responsibility (same-transaction semantics).
- `atlas.outbox.models.OutboxRow` + `OutboxDeadLetterRow` SQLAlchemy models.
- `atlas.events` module — `docs/events.md` sibling: constants for event names (`WINNER_SELECTED_V1 = "notification.winner_selected.v1"`), pydantic payload schemas so producer + consumer stay pinned.
- Tests: emit inside a rolled-back transaction is not persisted; emit inside a committed transaction is; two emits in one txn both land; payload schema is validated on write.
- **Adaeze handoff blocking:** confirm no PII beyond `user_id` (a UUID, not the email) lands in the `notification.winner_selected.v1` payload. Recommendation: pass `user_id` + `draw_id` + `ticket_id` only; the worker re-hydrates the email at delivery time.

**Verified EOD:** `pytest tests/outbox/` green; new migration up-and-down clean.

### Day 3 (Wed) — Outbox worker + reveal producer migration

- `atlas.outbox.worker` module:
  - `run_once(session)` — pick up to N rows with `FOR UPDATE SKIP LOCKED` where `next_attempt_at <= now() AND processed_at IS NULL`; dispatch each; on success mark `processed_at`; on failure bump `attempts`, set `next_attempt_at = now + backoff(attempts)`, write `error`; on `attempts >= 10` move to `outbox_dead_letter`.
  - `run_forever()` — 1-second poll floor per ADR-002 §Trade-offs.
- `atlas.outbox.dispatcher` — event-name → handler map. Registers `WINNER_SELECTED_V1 → atlas.notification.winner.deliver_from_payload`.
- `atlas.notification.winner.deliver_from_payload(payload) -> None` — re-hydrates email + calls the existing `mailhog_sender.send_notification`. Original `notify_winner(...)` deprecated but kept for one release for parity tests.
- `atlas.draw.service.reveal_draw`:
  - Delete the direct-call block (`service.py:342-348`).
  - Replace with `await outbox.emit(session, WINNER_SELECTED_V1, {"draw_id": ..., "winners": [...]})` inside the same transaction as the winner insert.
- Compose: `worker` service already exists in `docker-compose.yaml` — its command switches from the current stub (no-op sleep loop per Dockerfile.worker) to `python -m atlas.outbox.worker`.
- Runbook: `docs/runbooks/outbox-dead-letter.md` — how to inspect dead-letter rows + replay (SQL to reset `attempts = 0, processed_at = NULL, error = NULL` after fixing the underlying issue).
- **Winston consult (blocking):** confirm the producer/consumer split is idempotent per ADR-004 — specifically, if the worker crashes after `send_notification` but before `processed_at`, we resend. Options: (a) accept duplicate emails as V1 (MailHog + investors won't notice, prod uses idempotency key at vendor), (b) add a per-event idempotency table. Recommend (a) for W8; (b) is a W9+ story.
- Tests: worker picks up + dispatches + marks processed; retry-on-failure + backoff; 10th failure moves to dead-letter; concurrent workers don't double-dispatch (SKIP LOCKED integration test using two connections).

**Verified EOD:** rehearsal script runs green with the worker up — reveal completes, winner email lands in mailhog via the worker not via reveal_draw.

### Day 4 (Thu) — Playwright screen-recording script + fresh V0.5 rehearsal

- `infrastructure/scripts/record_demo.py`:
  - Uses `playwright.async_api` with headless Chromium + `--record-video-dir`.
  - Reuses the API-driven flow from `demo_rehearsal.sh` for the backend heavy lifting (register + skill + purchase + webhook) — the browser only records the *visible* surfaces: admin close/reveal + `/proof/[drawId]` copy-verify.
  - Output: `_bmad-output/demo/atlas-hero-flow.webm` (Playwright's native format); `ffmpeg` re-encode to mp4 if `ffmpeg` is on PATH (best-effort — the founder can screen-share the webm directly if the re-encode fails).
- Half-day cap. If Playwright browser install stalls on this laptop (likely — see [[feedback-zscaler-local-only]]), pivot to documenting the OBS session per `v0.5-close.md §8`.
- Re-run `bash infrastructure/scripts/demo_rehearsal.sh` end-to-end against a fresh reset to confirm nothing regressed under the encrypted-seed + outbox-worker changes.

**Verified EOD:** either `atlas-hero-flow.webm` exists in `_bmad-output/demo/` OR OBS runbook in the same location documents the manual fallback. Rehearsal script green post-changes.

### Day 5 (Fri) — Week 8 exit gates + AI Integration Log entry + docs sync

- Success gates (§8) verified.
- `docs/AI-INTEGRATION-LOG.md`:
  - Append Sessions table row #20 (Week 8: encrypted-seed + outbox + fallback recording).
  - Append §YAML entries block for the W8 gate close.
  - Update §Registry artefacts by week with a "Week 8" subsection.
  - Strike the "encrypted-at-rest" debt from §Kept-in-code shortcuts.
- `README.md` — brief mention of `ATLAS_SERVER_SEED_KEY` in the required-env section.
- `_bmad-output/planning-artifacts/v0.5-demo-plan.md §Follow-ups` — mark encrypted-seed + fallback-recording as landed.
- Amendment blocks on ADR-002 + ADR-006 noting the W8 execution (per the `AI-INTEGRATION-LOG.md §Registry artefacts by week` pattern used for ADR-002 in W4 and ADR-006 in W5).

**Verified EOW:** `git log --since=2026-08-24` shows one commit per day (5-6 total). CI green. Rehearsal green. W8 line items on `v0.5-close.md §Known follow-ups` struck through.

---

## 3. Module contracts

### 3.1 New backend modules

| Path | Purpose | Owner test file |
|---|---|---|
| `atlas.draw.crypto` | Fernet round-trip for `server_seed_encrypted` | `tests/draw/test_crypto.py` |
| `atlas.outbox.writer` | Sole outbox-write API | `tests/outbox/test_writer.py` |
| `atlas.outbox.worker` | Poll + dispatch + backoff + dead-letter | `tests/outbox/test_worker.py` |
| `atlas.outbox.dispatcher` | event_name → handler map | `tests/outbox/test_dispatcher.py` |
| `atlas.events` | Event-name constants + pydantic payloads | `tests/outbox/test_events.py` |
| `atlas.notification.winner.deliver_from_payload` | Outbox-consumer entry | `tests/notification/test_winner_delivery.py` |

### 3.2 New backend config (`atlas.config.Settings`)

| Field | Default | Prod validator |
|---|---|---|
| `server_seed_key` | *(empty)* | Non-empty; valid Fernet key (44 url-safe b64 chars). |
| `outbox_poll_interval_seconds` | `1.0` | `>= 1.0` per ADR-002. |
| `outbox_batch_size` | `50` | `>= 1`. |
| `outbox_max_attempts` | `10` | Matches ADR-002 §Retry policy. |

### 3.3 Migrations

| # | Content |
|---|---|
| `0010_encrypted_server_seed` | Data migration: re-encrypt any raw-hex `server_seed_encrypted` with Fernet. Idempotent. |
| `0011_outbox` | Create `outbox` + `outbox_dead_letter` + partial index per ADR-002. |

### 3.4 Compose services

- `worker` service command flipped from stub to `python -m atlas.outbox.worker`.
- `Dockerfile.worker` unchanged (installs the same package; command comes from compose).

### 3.5 Module boundary invariants (extend W7 §3.5)

- The Fernet key **never** appears in application logs or audit-log payloads (add grep-CI rule: no `ATLAS_SERVER_SEED_KEY` substring outside `atlas.config` and `.env.example`).
- No code path writes `notification.*` audit events except from inside a worker-dispatched handler. (Grep-CI addition in W9; W8 is a hand-review.)
- The reveal transaction MUST commit before the worker can pick up the outbox row — enforced by same-txn `outbox.emit` + the caller's commit boundary.

---

## 4. Test strategy (for Murat 🧪)

**Backend:**
- Existing 254 tests continue to pass.
- Add: `test_crypto` (round-trip + tamper), `test_writer` (same-txn semantics + rollback), `test_worker` (dispatch + retry + dead-letter + SKIP LOCKED concurrency), `test_dispatcher` (missing handler is a per-row failure, not a worker crash), `test_events` (payload schema validation), `test_winner_delivery` (reads a well-formed payload and calls mailhog).
- Regression: `test_proof_and_notification.py` runs the full lifecycle with the outbox worker as a subprocess and asserts the mailhog message lands within N seconds.

**Frontend:**
- No frontend surface changes → no new Playwright/vitest cases beyond regression runs.

**E2E:**
- `bash infrastructure/scripts/demo_rehearsal.sh` — must remain green post-Day 3 with the worker in the loop.
- New: `infrastructure/scripts/record_demo.py` produces a video on Day 4 (existence check in CI is skipped; artifact-only for founder use).

**Not in Week 8:**
- Load testing on the outbox worker (V1 §Phase 4).
- Chaos test: kill the worker mid-dispatch (W9 candidate, gates on §0 ask 3 Option (b)).

---

## 5. Handoffs and dependencies

### To 🎨 Sally (UX)

- **Non-blocking:** design-pass sign-off owed from V0.5 (`v0.5-close.md §5`). Please schedule the pair-review with the founder when time allows — the mobile hero flow + admin CRUD both consume Sally's tokens and haven't been walked with fresh eyes since W3.

### To 🛡️ Tobi (DevSecOps)

- **Day 1 blocking:** confirm the `ATLAS_SERVER_SEED_KEY` env-var pattern for local + CI + prod, per ADR-012 §V1 mechanism. In particular: does prod get its Fernet key from platform secret manager as a rotated secret, and what is the rotation cadence (recommend: annual + on-incident, per ADR-006 §Trade-offs bullet).
- **Day 3 blocking:** review `docs/runbooks/outbox-dead-letter.md`. First draft by Amelia; Tobi is the runbook-owner per ADR-002 §Trade-offs bullet 3.
- **Day 5 non-blocking:** confirm the worker service's Docker health-check pattern (currently a no-op `sys.exit(0)`; upgrade to a liveness probe against the poll loop).

### To 🏗️ Winston (Architect)

- **Day 3 blocking (small):** confirm the "accept duplicate emails on worker crash" trade for W8 (§Day 3 Winston consult). Alternative is a per-event idempotency table which pushes work into W9.

### To ⚖️ Adaeze (Compliance & Risk)

- **Day 2 blocking-ish:** confirm no PII beyond `user_id` in the `notification.winner_selected.v1` payload. Recommendation in §Day 2 stands.
- **Day 5 non-blocking:** compliance re-read of the W8 amendment blocks on ADR-002 + ADR-006.

### To 👤 Founder (S1408661)

- **Between W7 close and W8 Day 1:** the mobile + admin walkthroughs from `v0.5-close.md §Success gate 1` are still owed. Recommend walking all 16 flagship steps in the mobile simulator + admin browser before W8 Day 1 so any friction lands as W8 issues rather than being discovered mid-hardening.
- **Founder rehearsal count (`v0.5-close.md §Success gate 6`):** still not started. Not a W8 code item but a real gate — 20+ walkthroughs remain the demo-readiness signal.

---

## 6. Risks

Ranked by likelihood × slip-impact.

1. **Worker crash-recovery edge cases (Day 3, medium likelihood, half-day slip).** The dispatcher + SKIP LOCKED integration test is easy to write shallowly and miss subtle races. *Mitigation:* the concurrent-workers test uses two real Postgres connections, not mocks; if flaky, escalate to Winston.
2. **Fernet key rotation story unclear (Day 1, medium likelihood, quarter-day design slip).** ADR-006 §Trade-offs mentions rotation but ADR-012 §V1 mechanism is env-var-based, which makes rotation = process restart + re-encrypt-in-place. If we want online rotation, we need a `key_version` column and a decryption fallback chain. *Mitigation:* W8 ships single-key; multi-key is a W9+ story flagged in the ADR-006 amendment.
3. **Playwright install friction (Day 4, high likelihood on this laptop per [[feedback-zscaler-local-only]], half-day slip).** Chromium download hits the same corporate-proxy SSL block that the docker build does. *Mitigation:* half-day cap; OBS runbook is the always-works fallback per `v0.5-close.md §8`.
4. **Outbox producer-inventory gap (background, low likelihood, no W8 slip).** W8 migrates one producer only. Any code path that lives on outside-outbox after W8 stays direct-call — the grep-CI enforcement in W9 will find them. *Mitigation:* Winston consult Day 3 also frames W9 scope; producer inventory is a Winston pre-work item.
5. **Data-migration re-encrypt collision (Day 1, low likelihood, quarter-day slip).** If a dev has an in-flight branch that seeded a draw with a Fernet-token-shaped hex string (44 chars starting `gAAAAA`), the migration will mistake it for already-encrypted and skip. *Mitigation:* migration checks the string decodes as 32-byte raw hex OR as a valid Fernet token; anything else fails migration with a diagnostic.

---

## 7. Cross-week dependencies

**Week 8 leaves in place for W9+:**
- Outbox grep-CI enforcement + migration of remaining direct-call producers.
- Per-event idempotency table (if founder picks §0 ask 3 Option (b) later).
- Multi-key Fernet rotation with `key_version` column.
- Worker liveness/readiness probes for platform deploy.
- WhatsApp notification producer once ADR-007 KYC vendor lands (WhatsApp Business needs a verified sender identity).

**Week 8 explicitly leaves for later (Phase 4-5):**
- Real KYC vendor swap (ADR-007).
- Sentry / structured log aggregation (ADR-011).
- Managed-platform deploy (Phase 5).
- Load / performance testing (V1 Phase 4).

---

## 8. Success gates

- [ ] `atlas.draw.crypto` round-trip encrypt/decrypt passes; tampered ciphertext rejects.
- [ ] After Day 1 migration, no `draws.server_seed_encrypted` row is raw hex.
- [ ] `verify_draw.py` reproduces the golden-vector primary winner unchanged (encrypted-seed refactor is transparent).
- [ ] `outbox` table + partial index landed; migration up/down clean.
- [ ] `atlas.outbox.worker` picks up a `notification.winner_selected.v1` row within 2s of reveal commit.
- [ ] `docker compose up worker` stays up ≥ 5 min with no crashes on an idle queue.
- [ ] `bash infrastructure/scripts/demo_rehearsal.sh` runs end-to-end green with the worker in the loop (no direct-call from `reveal_draw`).
- [ ] `docs/runbooks/outbox-dead-letter.md` exists + reviewed by Tobi.
- [ ] `_bmad-output/demo/atlas-hero-flow.webm` exists OR OBS-only runbook committed as fallback.
- [ ] `docs/AI-INTEGRATION-LOG.md` W8 entry appended; V0.5 kept-in-code shortcut for `server_seed` struck.
- [ ] CI green on `main`.

---

## 9. Asks to founder before Day 1 code starts

1. **Week 8 scope — V1 hardening only, or bridge V0.5 residuals as well?**
   Options: (a) hardening only — encrypted-seed + outbox + worker, ship demo-fallback recording as its own W9 slot; (b) hardening + fallback recording + Adaeze/Sally reviews packaged as Day 4-5 (as scoped above); (c) demo-day residuals only (walkthrough, recording, timing drills) — defer all hardening to W9.
   **Recommendation: (b) hardening + fallback recording.** Encrypted-seed is the highest-priority ADR-006 debt (real-money draws cannot ship without it) and the outbox unlocks the WhatsApp channel and any real-vendor integration downstream. Fallback recording is small and closes the last unshipped V0.5 §6 gate. (c) is a rest week disguised as a plan — not useful given the demo is already validated green.

2. **Server-seed encryption vendor for the V0.5→V1 bridge.**
   Options: (a) Fernet (Python `cryptography.fernet.Fernet` — AES-128-CBC + HMAC-SHA-256, url-safe token) with key from `ATLAS_SERVER_SEED_KEY` env var; (b) libsodium sealed box; (c) cloud KMS envelope encryption directly (deferred per ADR-012 §Alternatives — needs a platform choice); (d) keep plaintext until platform-select in Phase 5.
   **Recommendation: (a) Fernet.** Standard, well-audited, sits neatly on top of ADR-012's "env-var-injected secrets" mechanism, and forward-compatible with a KMS-envelope migration in Phase 5 (Fernet token becomes the inner-layer ciphertext under a KEK). (d) is the wrong signal for the compliance narrative on the trust page.

3. **Outbox scope for W8 — foundation + one producer, or all producers migrated?**
   Options: (a) foundation + winner-notification producer only, W9 does the CI enforcement + producer sweep (as scoped above); (b) foundation + all identifiable producers in one hit (OTP send, webhook side-effects, winner) — larger blast radius; (c) writer + worker only, no producer migrated — pure infrastructure.
   **Recommendation: (a).** Migrates the exact producer that the V0.5 debt-list called out (`AI-INTEGRATION-LOG.md §Kept-in-code shortcuts`), keeps the diff auditable, and defers the producer inventory to Winston's W9 pre-work where it belongs.

4. **Playwright screen-recording script — build now, defer, or drop for OBS-only?**
   Options: (a) build now with a half-day cap + OBS fallback (as scoped above); (b) defer to W9; (c) drop — commit to OBS-only + write the runbook.
   **Recommendation: (a).** It was the only unshipped V0.5 §6 gate; the fallback video is small and useful, and the half-day cap + OBS-fallback bounds the downside. On this laptop the Playwright Chromium download may hit the local-only Zscaler friction — the cap is what protects the week.

5. **Fresh-clone drill v6 — measure on this laptop or defer to a second-engineer laptop?**
   Options: (a) defer to a real second-engineer laptop (as recommended above); (b) measure on this laptop under the local-env workarounds — reported as-is; (c) measure with a repo-level docker fix applied first (violates [[feedback-zscaler-local-only]], not recommended).
   **Recommendation: (a) defer.** A fresh-clone drill on this laptop measures Zscaler behaviour more than Atlas behaviour; the drill only signals V1 readiness when it runs on a laptop that isn't the primary dev machine.

Adaeze's items in §5 (server-seed key handling, outbox event PII) owed by Day 2. Winston consult on producer/consumer split Day 3.

---

## 10. Cross-references

- `v0.5-close.md §Known follow-ups` — W8 closes 2 of the 5 items (encrypted-seed, fallback recording).
- `docs/adr/ADR-002-outbox-pattern-for-async-work.md` — schema + processing model.
- `docs/adr/ADR-006-commit-reveal-protocol-and-public-entropy.md §Stage 1` — encrypted-at-rest requirement.
- `docs/adr/ADR-012-secret-management.md §V1 mechanism` — env-var-injected secret pattern.
- `docs/AI-INTEGRATION-LOG.md §Kept-in-code shortcuts` — V0.5 debts, two of which W8 closes.
- `week-6-build-plan.md §6 risk 3` — flagged the plaintext-seed debt at the point it landed.
- `backend/src/atlas/draw/service.py:83-100, 251, 313` — current plaintext-hex sites to migrate.
- `backend/src/atlas/draw/service.py:342-348` — current direct-call notification site to migrate.
- `infrastructure/scripts/demo_rehearsal.sh` — the regression harness for Day 3 and Day 4 verification.

---

💻 *End of Week 8 draft. Awaiting sign-off on §9 (5 asks) before Day 1 Monday 2026-08-24. Ping when ready.*
