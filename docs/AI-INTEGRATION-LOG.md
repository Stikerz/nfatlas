# AI integration log

How AI was used to plan, design, build, test, and document **nf_atlas / Project Atlas** — the premium prize-competition platform for Nigeria.

Append-only per `docs/AINE-AGENTS.md §7`. Rotated annually into `docs/AI-INTEGRATION-LOG-YYYY.md` archives.

This log is the accountability record: what an AI agent produced, what a human reviewed, and where arbitration or overrides happened. It is a **companion** to the git commit history (which records mechanical file changes) and the per-week build plans in `_bmad-output/implementation-artifacts/` (which record scope + decisions). This document focuses on the **agent side**: which persona spoke, whose sign-off closed a decision, and which registry artefacts were touched.

---

## Tools

| Tool | Used for |
|---|---|
| Claude Code CLI | The interactive driver. Every plan, module, migration, and doc in this repo originated in a Claude Code session. |
| Claude Opus 4.x | Underlying model. |
| BMad-method skills | `bmad-agent-dev` (Amelia), `bmad-agent-architect` (Winston), `bmad-agent-pm` (John), etc. Skill-bound personas per `docs/AINE-AGENTS.md`. |
| Claude Code sub-agents | `Explore` for read-only code search. |
| Local shell / docker / uvicorn / pnpm / flutter | Verification harness. AI proposed commands; the user (or user-supervised agent) ran them and read output. |
| GitHub CLI (`gh`) | CI status polling, push confirmation, run-failure log fetch. |

No external AI services were used. No code was copy-pasted from external AI chats — every change was tool-call-driven inside the Claude Code session, which means every file modification is reviewable in the session transcript.

---

## Division of labour

### Decisions made by the human (kept verbatim, no override)

Framing calls elicited by BMad's asking discipline; the answer came from the founder. Each week's build plan §9 preserves the ask + the founder decision.

- **V0.5 scope pivot (2026-07-02).** Defer managed-platform commitment; build local Docker Compose demo first. Reframed Phase 2 as a scoped subset of Phase 3 modules. Documented in `_bmad-output/planning-artifacts/v0.5-demo-plan.md`.
- **BMad-project correction (2026-06-29).** Amelia had built a custom `.claude/agents/` system before realising the sibling nearform-tdapp used BMad. Founder correction landed as [[feedback-bmad-project]] in agent memory; the custom system was deleted and BMad personas adopted. See `docs/AINE-AGENTS.md §Introduction`.
- **Week 4 asks (2026-07-15).** All 5 asks approved on recommendations: Paystack fully stubbed, trust vendor `fees` field, direct call in Week 4 (outbox W6+), `WALLET_ALLOW_STUB_DRAW` flag, ADR-004 verbatim idempotency. See `week-4-build-plan.md §0`.
- **Week 5 asks (2026-07-22).** All 5 approved on recommendations: direct-to-Paystack per ticket, new-question-no-penalty, hybrid pool table, any-string slip, plaintext seed with TODO(week-6).
- **Week 6 asks (2026-07-27).** All 5 approved on recommendations: hybrid entropy (stub in CI + live in demo), skip 1h reveal delay in V0.5, rejection sampling for winner selection, curl-only admin in W6, notify-from-reveal with try/except.
- **Week 7 asks (2026-07-29).** 4/5 on recommendations. **Deviation: 10-min close instead of 3-min** — founder preferred a buffered window for pitches with Q&A. Recorded in `week-7-build-plan.md §0`.

### Arbitrations (where AI recommendation was overridden)

- **W7 §0 ask 3** (demo timing). Amelia recommended 3-min close; founder chose 10-min. Reason: buffer for Q&A during investor pitches. Impact: `Settings.demo_mode` + `seed_v0_5.py` compressed timing set to `close_time=now+10min`.

### Kept-in-code shortcuts (V0.5 explicit debts)

Each surfaces in the relevant module docstring + at least one runbook or ADR amendment. All are targeted at V1 hardening.

- ~~**`server_seed` stored as plaintext hex** in `draws.server_seed_encrypted`. TODO(week-6+) — encrypt at rest per ADR-006 §Stage 1.~~ **Closed W8 Day 1 (2026-08-24)** — Fernet encryption via `atlas.draw.crypto`, keyed from `ATLAS_SERVER_SEED_KEY`. Migration 0010 re-encrypted the seeded demo row.
- **Paystack stub mode** (`ATLAS_PAYSTACK_STUB_MODE=true`) default in V0.5. Production must be `false` (config validator enforces).
- ~~**Direct-call reveal notifications** via mailhog with try/except. V1 replaces with the outbox pattern per ADR-002.~~ **Closed W8 Day 3 (2026-08-24)** — `reveal_draw` now writes a `notification.winner_selected.v1` row in the same transaction; `atlas.outbox.worker` dispatches it. Measured dispatch latency 0.10-0.12s.
- **BLS drand signature verification** deferred. `drand_signature` persisted for later replay-verify per week-6-build-plan §6 risk 3.
- **Demo mode** (`ATLAS_DEMO_MODE=true`) compresses seed-draw timings to 10 min. Prod-safety validator refuses `demo_mode=true` in production.
- **`WALLET_ALLOW_STUB_DRAW`** was true through W4, flipped to false in W5 Day 1 when real `draws.id` existed.

---

## Sessions, in order

Each row corresponds to one visible unit of scoped work in the Claude Code session. Commit-level history is in `git log`; this table records what week/day was in flight, which BMad persona spoke, and which registry artefacts were touched.

| # | Date | Persona | Activity | Key artefacts |
|---|---|---|---|---|
| 1 | 2026-06-29 | 📊 Mary + 🏗️ Winston | V1 planning artefacts + 12 ADRs authored | `_bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md`, `docs/adr/ADR-001..012.md`, `docs/AINE-AGENTS.md`, `docs/risk-register.md` |
| 2 | 2026-06-29 | (arbitration) | `.claude/agents/` custom system removed; BMad personas adopted | `_bmad/custom/config.toml` (Tobi + Adaeze descriptors), memory feedback entry |
| 3 | 2026-07-02 | 🛡️ Tobi + 📋 John | V0.5 demo-first pivot | `_bmad-output/planning-artifacts/v0.5-demo-plan.md`, delivery-framework amendment, ADR-001 amendment |
| 4 | 2026-07-02 | 📋 John | 12 ADR approvals under founder EL + two-approval gate | `docs/adr/ADR-*.md` (all status → Approved) |
| 5 | 2026-06-29 → 2026-07-13 | 🎨 Sally | 14-day design pass: tokens + 15 wireframes + component review | `_bmad-output/planning-artifacts/design/{wireframes,components,tokens}/*` |
| 6 | 2026-07-13 → 2026-07-14 | 💻 Amelia | W3 Day 1 scaffold — backend FastAPI + Flutter + Next.js + docker-compose + CI + Makefile | Repo scaffold commits `0f2a97c` / `58d5d49` / `6d60582` |
| 7 | 2026-07-14 → 2026-07-16 | 💻 Amelia | W3 Days 2-5 identity + design primitives + admin RBAC | `atlas.identity`, `atlas.audit_log`, `atlas.idempotency`, `atlas.admin`; Flutter + Next.js identity flows |
| 8 | 2026-07-14 | 💻 Amelia | W4 build plan draft + approval | `_bmad-output/implementation-artifacts/week-4-build-plan.md` |
| 9 | 2026-07-15 → 2026-07-21 | 💻 Amelia | W4 Days 1-5 wallet + payment (Paystack stub) + webhook + runbook | `atlas.wallet`, `atlas.payment`, migrations 0004+0005, `docs/runbooks/paystack-webhook-outage.md` |
| 10 | 2026-07-21 | 💻 Amelia | W4 close: 107 pytest passing; CI red on latent debt exposed by first push | Discovered admin cache lookup / backend ruff / mobile lint / audit_log grep false-positive |
| 11 | 2026-07-21 | 💻 Amelia | CI hardening: `ruff --fix` + pnpm lockfile + audit_log grep word-boundary + `--no-fatal-infos` on flutter | `bbbd16f` (last of the hardening chain) |
| 12 | 2026-07-21 | 💻 Amelia | W5 build plan draft + approval | `_bmad-output/implementation-artifacts/week-5-build-plan.md` |
| 13 | 2026-07-22 → 2026-07-27 | 💻 Amelia | W5 Days 1-5 draws + skill questions + tickets + wallet chip + E2E | `atlas.draw`, `atlas.skill`, `atlas.ticket`, migrations 0006+0007+0008, `tests/e2e/test_flagship_flow.py` |
| 14 | 2026-07-27 | 💻 Amelia | W6 build plan draft + approval | `_bmad-output/implementation-artifacts/week-6-build-plan.md` |
| 15 | 2026-07-27 → 2026-07-29 | 💻 Amelia + 🏗️ Winston | W6 Days 1-5 state machine + entropy adapters + winner selection + proof endpoint + verifier CLI + notification + lifecycle E2E | `atlas.draw.{state_machine,entropy,reveal}`, `atlas.notification`, `backend/tools/verify_draw.py`, `docs/runbooks/reveal-abort.md`, migration 0009 |
| 16 | 2026-07-29 | 💻 Amelia | W7 build plan draft + approval | `_bmad-output/implementation-artifacts/week-7-build-plan.md` |
| 17 | 2026-07-29 → 2026-07-31 | 💻 Amelia | W7 Days 1-5 demo-mode + public /proof SSR + trust-story pages + admin CRUD + mobile write-side + rehearsal script | `admin/src/app/(public)/proof/[drawId]`, `admin/src/app/(admin)/admin/{draws,audit-log}`, mobile `skill_question_screen` + `winner_claim_screen`, `infrastructure/scripts/demo_rehearsal.sh` |
| 18 | 2026-07-31 | 💻 Amelia | V0.5 close doc + rehearsal validated end-to-end | `_bmad-output/implementation-artifacts/v0.5-close.md`, `9d28403` rehearsal-fixes commit |
| 19 | 2026-08-03 | 💻 Amelia | Mobile analyzer cleanup — all 30 info-level lints resolved; CI tightened | `87ae231` + `de25353`; `flutter analyze --no-fatal-infos` escape hatch removed |
| 20 | 2026-08-24 | 💻 Amelia | W8 Days 1-3 — Fernet-encrypted `server_seed` at rest; outbox table + writer; worker + dispatcher, reveal producer migrated off direct-call | `atlas.draw.crypto`, `atlas.outbox.{writer,worker,dispatcher}`, migrations 0010+0011, `docs/runbooks/outbox-dead-letter.md`, `docs/events.md` (created W8 Day 5 — cited by ADR-001/002 but had never existed) |
| 21 | 2026-08-24 | 💻 Amelia | W8 Day 4 — Playwright hero-flow recording script + OBS fallback runbook | `infrastructure/scripts/record_demo.py`, `docs/runbooks/demo-recording-obs-fallback.md` |
| 22 | 2026-08-24 | 🛡️ Tobi + 💻 Amelia + 🧪 Murat | Fresh-machine dev setup on a bare laptop; five blocking defects fixed; `main` returned to green after 4 red commits | PRs #1-#5: `backend/Dockerfile.backend` (dev stage), `admin/src/middleware.ts`, `.github/workflows/ci.yaml` (ADR-012 whitelist), `mobile/{ios,android,web}` scaffolding, three flaky-test fixes |
| 23 | 2026-08-25 | 📚 Paige | W8 Day 5 — success gates verified with evidence; this log, ADR-002/006 amendments, README + close-doc sync | `docs/AI-INTEGRATION-LOG.md`, `docs/adr/ADR-002*.md`, `docs/adr/ADR-006*.md`, `README.md`, `_bmad-output/implementation-artifacts/v0.5-close.md` |

---

## Registry artefacts by week

### Week 3 (backend + identity + admin RBAC + design primitives)

- `docs/adr/ADR-005-hash-chained-audit-log.md` — writer implementation. `atlas.audit_log.writer` is the sole INSERT path (grep-enforced).
- `docs/adr/ADR-004-idempotency-strategy.md` — `atlas.idempotency.dependency.idempotency_guard` shipped as reusable FastAPI dep.
- `docs/adr/ADR-009-rbac-model.md` — `atlas.admin` module + superadmin bootstrap.
- Migrations 0001-0003 landed (users + audit_log + idempotency, OTPs + sessions, RBAC).

### Week 4 (wallet + payment)

- ADR-002 (outbox) — deferred to W6+; W4 uses direct-call from webhook. Amelia added §Amendment noting the V0.5 deferral.
- ADR-003 (ledger) — schema + trigger + append-only enforcement in migration 0004.
- ADR-008 (payment adapter) — `atlas.payment.providers.protocol` + Paystack adapter (stub mode). ADR-008 §Fee handling implemented as separate ledger tx.
- Runbook: `docs/runbooks/paystack-webhook-outage.md` (Draft, awaiting Tobi).

### Week 5 (draws + skill questions + tickets)

- ADR-006 §Protocol stage 1 partially implemented (commitment; server_seed plaintext per debt above).
- New test-design doc: `_bmad-output/test-artifacts/test-design/week-5-tickets-draws.md`.
- Runbook: `docs/runbooks/skill-question-abuse.md` (Draft, V1 placeholder).

### Week 6 (draw engine)

- ADR-006 stages 3-5 implemented: close_draw + reveal_draw + verify. Winner selection uses rejection sampling per founder ask 3.
- New test-design doc: `_bmad-output/test-artifacts/test-design/week-6-draw-engine.md`.
- Runbook: `docs/runbooks/reveal-abort.md` (Draft, awaiting Tobi).
- CI grep additions: DrawWinner constructor + `secrets.token_bytes` whitelist.

### Week 7 (polish + demo)

- Public trust surface: `/proof/[drawId]`, `/how-it-works`, `/responsible-play`.
- Admin CRUD surface: `/admin/draws`, `/admin/draws/[id]`, `/admin/audit-log`.
- Mobile hero flow: home wallet chip + draw browse + skill question + Paystack checkout → external browser + tickets + winner claim.
- New helper: `infrastructure/scripts/demo_rehearsal.sh` (14-step API smoke).
- Gate close doc: `_bmad-output/implementation-artifacts/v0.5-close.md`.

### Week 8 (V1 hardening: encrypted seed + outbox + fallback recording)

- Server-seed encryption at rest: `atlas.draw.crypto` (Fernet, keyed from `ATLAS_SERVER_SEED_KEY`), migration 0010 re-encrypts legacy rows.
- Outbox: `outbox` + `outbox_dead_letter` tables (migration 0011, partial index on unprocessed rows), `atlas.outbox.{writer,worker,dispatcher}`, `atlas.events`.
- Reveal notifications migrated from direct-call to outbox producer/consumer per ADR-002.
- Demo-day fallback: `infrastructure/scripts/record_demo.py` + `docs/runbooks/demo-recording-obs-fallback.md`.
- Operations: `docs/runbooks/outbox-dead-letter.md`.
- Local dev + CI: backend `dev` image stage, mobile platform scaffolding, ADR-012 `get_secret_value` whitelist extended to `draw/crypto.py` + `outbox/worker.py`.

---

## YAML entries (gate closes + arbitrations)

### 2026-06-29 — BMad-project agent correction

```yaml
---
ts: 2026-06-29T00:00:00Z
agent: manual  # was Amelia, corrected by founder
session: manual
artefact: docs/AINE-AGENTS.md + _bmad/custom/config.toml
operation: reset
inputs:
  - Founder message: "remember this is a bmad agent project"
  - Sibling repo precedent: nearform-tdapp
human_review:
  reviewer: S1408661
  status: approved
  comments: Custom .claude/agents/ system removed; BMad personas + 2 Atlas custom (Tobi, Adaeze) adopted.
notes: |
  Amelia had authored a custom AINE agent system (7 .claude/agents/*.md
  files) before realising nf_atlas is a BMad project. Founder correction
  landed as [[feedback-bmad-project]] in agent memory; the custom files
  were deleted and BMad's 7-persona roster + 2 Atlas-specific
  complements (Tobi DevSecOps, Adaeze Compliance) were registered.
---
```

### 2026-07-02 — V0.5 demo-first pivot

```yaml
---
ts: 2026-07-02T00:00:00Z
agent: atlas-devsecops (Tobi) + bmad-agent-pm (John)
session: manual
artefact: _bmad-output/planning-artifacts/v0.5-demo-plan.md
operation: created
inputs:
  - _bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md
  - _bmad-output/planning-artifacts/delivery-framework.md
human_review:
  reviewer: S1408661
  status: approved
  comments: Managed-platform deferred to Phase 5; V0.5 is a local Docker Compose demo for investors.
notes: |
  Reframes Phase 2 as a scoped subset of Phase 3 modules. Not throwaway
  — extending V0.5 → V1 is additive (real vendors, missing flows,
  hardening), not a rewrite. Triggered amendments to delivery-framework
  and ADR-001.
---
```

### 2026-07-21 — Week 4 gate close (V0.5 wallet + payment)

```yaml
---
ts: 2026-07-21T00:00:00Z
agent: bmad-agent-dev (Amelia)
session: continuous
artefact: _bmad-output/implementation-artifacts/week-4-build-plan.md §8 gates
operation: closed
inputs:
  - All Day 1-5 commits (7d9022d..bbbd16f)
  - pytest 107 passing, CI green after bbbd16f
human_review:
  reviewer: S1408661
  status: approved
  comments: |
    All §8 gates met except the "real Paystack sandbox checkout_url"
    which is deferred per §0.1 stub decision. Latent lint debt from
    Days 1-2 exposed on first CI push; hardening commits landed same
    day.
notes: |
  Trigger for exposing latent CI: repo was 16 commits ahead of origin
  until Day 3; first push surfaced admin lockfile miss + backend ruff
  drift + audit_log grep false-positive on "writer". All fixed.
---
```

### 2026-07-27 — Week 5 gate close (tickets + draw skeleton)

```yaml
---
ts: 2026-07-27T00:00:00Z
agent: bmad-agent-dev (Amelia)
session: continuous
artefact: _bmad-output/implementation-artifacts/week-5-build-plan.md §8 gates
operation: closed
inputs:
  - All W5 Day 1-5 commits (36c2133..306fca1)
  - pytest 160 passing, CI green
human_review:
  reviewer: S1408661
  status: approved
  comments: All §8 gates met. WALLET_ALLOW_STUB_DRAW=false in dev + test + CI now that real draws.id exists.
notes: |
  End-to-end flagship flow (register → skill → paid + free ticket) covered
  by tests/e2e/test_flagship_flow.py. CI greps added: Ticket +
  FreeEntrySlip + Draw construction outside their modules blocked.
---
```

### 2026-07-29 — Week 6 gate close (draw engine + verifier)

```yaml
---
ts: 2026-07-29T00:00:00Z
agent: bmad-agent-dev (Amelia) + bmad-agent-architect (Winston)
session: continuous
artefact: _bmad-output/implementation-artifacts/week-6-build-plan.md §8 gates
operation: closed
inputs:
  - All W6 Day 1-5 commits (d3458a8..4a86dc5)
  - pytest 241 passing, CI green
  - E2E lifecycle: create → sell → close → reveal → verify_draw.py match
human_review:
  reviewer: S1408661
  status: approved
  comments: |
    Full ADR-006 commit-reveal cycle live. Third-party reproducibility
    proven end-to-end. Live-mode entropy (mempool.space + api.drand.sh)
    wired but only stub-mode exercised in CI per §0 ask 1.
notes: |
  Winner selection uses rejection sampling per §0 ask 3 — spec-correct
  regardless of ticket count. Golden vectors pin the algorithm; any
  behaviour change red-tests. verify_draw.py stdlib-only so third
  parties don't need pip installs.
---
```

### 2026-07-29 — Arbitration: Week 7 demo timing

```yaml
---
ts: 2026-07-29T00:00:00Z
agent: bmad-agent-dev (Amelia) recommendation overridden
session: continuous
artefact: _bmad-output/implementation-artifacts/week-7-build-plan.md §0 ask 3
operation: recorded
inputs:
  - Amelia recommendation: 3-min close (compressed for 5-min pitch)
human_review:
  reviewer: S1408661
  status: approved-with-changes
  comments: Chose 10-min close for Q&A buffer instead of 3-min.
notes: |
  Only §9 deviation from Amelia's recommendations across Weeks 4-7.
  seed_v0_5.py + config.demo_mode implement the 10-min close_time /
  11-min draw_time when ATLAS_DEMO_MODE=true.
---
```

### 2026-07-31 — Week 7 gate close + V0.5 demo close

```yaml
---
ts: 2026-07-31T00:00:00Z
agent: bmad-agent-dev (Amelia)
session: continuous
artefact:
  - _bmad-output/implementation-artifacts/week-7-build-plan.md §8 gates
  - _bmad-output/implementation-artifacts/v0.5-close.md
operation: closed
inputs:
  - All W7 Day 1-5 commits (d1865cb..3e37ca5) + rehearsal fix (9d28403)
  - pytest 254 passing, admin lint + tsc + 5 vitest passing, CI green
  - demo_rehearsal.sh runs 9 steps end-to-end against live stack
human_review:
  reviewer: S1408661
  status: approved-conditional
  comments: |
    V0.5 demo-ready pending Monday's founder walkthrough (mobile/admin
    UI in browser + iOS Simulator) + cold-start timing + fresh-clone
    re-time. All backend + trust-surface exit gates green.
notes: |
  Rehearsal script surfaced 3 portability issues in first live run
  (system python vs venv, reveal needs 6 tickets, mailhog scrape
  raced across consumers). All fixed in 9d28403 before this gate
  close. Post-fix rehearsal walked all 9 steps green + verifier
  CLI reproduced the primary winner.
---
```

### 2026-08-03 — Mobile analyzer cleanup + CI tightening

```yaml
---
ts: 2026-08-03T00:00:00Z
agent: bmad-agent-dev (Amelia)
session: continuous
artefact:
  - mobile/lib/**/*.dart (13 files touched)
  - .github/workflows/ci.yaml (mobile job)
operation: cleaned
inputs:
  - CI run 30628749202 flutter-analyze output — 30 info-level lints
human_review:
  reviewer: S1408661
  status: approved
  comments: Requested explicitly ("mobile analyze fixes"). CI escape hatch removed.
notes: |
  All 30 info-severity findings addressed: 13 withOpacity → withValues,
  12 prefer_const_constructors, 5 require_trailing_commas. CI's
  --no-fatal-infos escape hatch (added W7 Day 5 as a scope trade)
  removed — future accidental drift now fails the build. Backfill
  commit for the escape-hatch decision is the closing gate on the
  W7 "CI green" success criterion (§6 gate #9).
---
```

### 2026-08-25 — Week 8 gate close (encrypted seed + outbox + fallback recording)

```yaml
---
ts: 2026-08-25T00:00:00Z
agent: bmad-agent-dev (Amelia) + bmad-tea (Murat) + bmad-agent-tech-writer (Paige)
session: continuous
artefact:
  - atlas.draw.crypto + migration 0010
  - atlas.outbox.{writer,worker,dispatcher} + atlas.events + migration 0011
  - infrastructure/scripts/record_demo.py
  - docs/runbooks/{outbox-dead-letter,demo-recording-obs-fallback}.md
  - docs/adr/ADR-002 + ADR-006 (W8 execution amendments)
operation: closed
inputs:
  - _bmad-output/implementation-artifacts/week-8-build-plan.md §8 success gates
  - CI run on main @ e3cfad4 — all four jobs green
human_review:
  reviewer: S1408661
  status: approved
  comments: |
    Gate 8 (outbox dead-letter runbook reviewed by Tobi) is a human gate and
    is recorded as "exists"; it is not self-certifiable by an agent.
notes: |
  All 11 §8 gates verified with evidence rather than assertion:

    1. crypto round-trip + tamper reject — 17 tests pass.
    2. no raw-hex server_seed — 0 raw hex, 1 Fernet token (gAAAAAB...).
    3. golden-vector winner unchanged — 10 reveal-algorithm tests pass.
    4. outbox migration up/down — downgrade dropped both tables, upgrade
       restored them plus the outbox_unprocessed_idx partial index.
    5. worker dispatch within 2s — measured 0.101-0.124s across 6 rows,
       attempts=0, zero dead letters, 6 winner emails delivered.
    6. worker stable on an idle queue — 0 restarts, 0 tracebacks, ~22h up.
    7. demo_rehearsal.sh green with the worker in the loop.
    8. docs/runbooks/outbox-dead-letter.md exists (Tobi review is a human gate).
    9. OBS fallback runbook committed; record_demo.py additionally produces
       an 18.6s 1440x900 webm now that its three blocking defects are fixed.
   10. this entry.
   11. CI green on main @ e3cfad4.

  Gate 11 is the notable one: main had been red since W8 Day 1 (80cffce).
  The module-boundaries job failed its ADR-012 get_secret_value step because
  Day 1 and Day 3 each added a legitimate SecretStr unwrap without extending
  the whitelist. Four consecutive commits reported failure while the gate
  enforced nothing. Closed in PR #2.

  Three flaky tests were found and fixed in the same window, all one bug
  class — a "make it different" step that can silently produce something
  identical:
    - skill-question answer collision, ~47% (v0.5-close gate #1 was passing
      on a coin flip),
    - test_different_minute_may_rotate, ~4%,
    - test_tampered_signature_rejected, ~1.6% (measured 1.56% over 50k
      signatures, matching 1/64 exactly).
  A deliberate sweep for the pattern is worth a slot in W9.
---
```

---

## What's next

Post-V0.5 items tracked in `v0.5-close.md`:

- Monday founder walkthrough (all 16 flagship steps in mobile + admin, single sitting).
- Cold-start + fresh-clone timing on a second engineer's laptop.
- ~~Optional: Playwright automated recording of the operator flow.~~ Landed W8 Day 4 — `infrastructure/scripts/record_demo.py`.
- V1 hardening path: real KYC vendor, WhatsApp, reconciliation cron, multi-draw browsing, refund UX. ~~Encrypted server_seed at rest~~ closed W8 Day 1; the outbox is ~~scaffolded~~ but only the reveal producer is migrated — payment, ticket and wallet producers plus the CI grep gate are W9+ (ADR-002 §W8 execution amendment).
- W9 candidate: sweep the suite for the flaky-test pattern found three times in W8 — a "make it different" step that can silently produce something identical.

Every new session appends here per the AINE-AGENTS.md §7 discipline.
