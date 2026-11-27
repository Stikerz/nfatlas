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
- ~~**Direct-call reveal notifications** via mailhog with try/except. V1 replaces with the outbox pattern per ADR-002.~~ **Closed W8 Day 3 (2026-08-24)** — `reveal_draw` now writes a `draw.winner_selected.v1` row in the same transaction (emitted in W8 as `notification.winner_selected.v1`; renamed W9 Day 1 per `docs/events.md §Naming and emission rules`); `atlas.outbox.worker` dispatches it. Measured dispatch latency 0.10-0.12s.
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
| 24 | 2026-08-25 | 📚 Paige + 🎨 Sally | Visual walkthrough — 14 screenshots from a running stack, generator script, mobile font bundling + 7 screen goldens | `docs/VISUAL-WALKTHROUGH.md`, `docs/screens/`, `infrastructure/scripts/capture_screens.py`, `mobile/assets/google_fonts/`, `mobile/test/design/` |
| 25 | 2026-08-25 | 💻 Amelia | W9 build plan drafted with 5 open asks; approved as a foundation week | `_bmad-output/implementation-artifacts/week-9-build-plan.md` |
| 26 | 2026-08-25 → 08-26 | 💻 Amelia + 🏗️ Winston | W9 Day 1 — outbox producer inventory (28 state-change sites) + architecture review: naming rule, emission rule, and why nothing migrates | `docs/events.md` §Naming and emission rules, §Producer inventory |
| 27 | 2026-08-26 | 💻 Amelia + 🛡️ Tobi | W9 Day 3 — ADR-002 invariant restated and enforced by an AST check in CI | `backend/tools/check_outbox_invariant.py`, `.github/workflows/ci.yaml`, ADR-002 §W9 amendment |
| 28 | 2026-08-26 | 🧪 Murat + 🛡️ Tobi | W9 Day 4 — test database isolated from the dev stack; real worker liveness probe | `Makefile`, `docker-compose.yaml`, `atlas.outbox.worker` |
| 29 | 2026-08-26 | 📚 Paige | W9 Day 5 — gate close, this entry, events catalogue status | `docs/AI-INTEGRATION-LOG.md`, `docs/events.md` |

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

### Week 9 (foundation: outbox invariant enforced + quality debt)

- Producer inventory: 28 audit-recorded state changes classified — 1 emitting, 13 deferred with named triggers, 14 correctly without a producer (`docs/events.md §Producer inventory`).
- Event naming rule: `<producing-domain>.<what-happened>.v<n>`. The shipped event was renamed off its consumer prefix to `draw.winner_selected.v1`.
- ADR-002 invariant restated to "every state change that triggers work outside its own transaction", and enforced by `backend/tools/check_outbox_invariant.py` in the `module-boundaries` job — the AST check `ci.yaml` anticipated.
- Test database isolated from the dev stack (`make test` targets `atlas_test`), closing a 20%-rate e2e flake.
- Outbox worker liveness probe replacing a healthcheck that only asserted the interpreter starts.
- `docs/events.md` created W8, populated W9; owner 🏗️ Winston per `AINE-AGENTS.md §4`.

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

### 2026-08-26 — Week 9 gate close (outbox invariant enforced)

```yaml
---
ts: 2026-08-26T00:00:00Z
agent: bmad-agent-dev (Amelia) + bmad-agent-architect (Winston) + bmad-tea (Murat)
session: continuous
artefact:
  - docs/events.md — naming rules, emission rules, producer inventory
  - backend/tools/check_outbox_invariant.py + .github/workflows/ci.yaml
  - docs/adr/ADR-002 §W9 amendment
  - Makefile, docker-compose.yaml, atlas.outbox.worker
operation: closed
inputs:
  - _bmad-output/implementation-artifacts/week-9-build-plan.md §8 success gates
  - §0 asks 1-5, all resolved on recommendations 2026-08-25
human_review:
  reviewer: S1408661
  status: approved
  comments: |
    Approved as a foundation week on recommendations. Ask 3 (ADR-006
    decrypt-not-worker-only) remains owed from Adaeze and is NOT closed by
    this entry.
notes: |
  Nine §8 gates. Seven met as written, two met differently, and the difference
  is the week's main finding.

  Met as written:
    1  28 state-change sites classified, a written reason on each non-emitter.
    4  CI gate live, failure mode demonstrated three ways: planted violation
       fails naming file/line/event; adding an emit passes; removing one
       allowlist entry fails on that entry.
    5  ADR-002 amended before the gate landed, so the gate enforces a rule the
       ADR states.
    6  Worker healthcheck proven in three directions — live healthy, SIGSTOP'd
       unhealthy, resumed healthy, RestartCount 0 throughout.
    7  Sweep found no new instances of the W8 "make it different" class. It did
       resolve the e2e intermittent: measured 3/15 with the worker running,
       0/15 stopped, 0/15 with an isolated DB.
    8  Rehearsal green; 282 backend + 5 admin tests green; CI green on main.
    9  This entry.

  Met differently, per §0 ask 2:
    2  "Every must-emit function emits" — none does, and none could. Of 13
       classified must-emit, 11 have no consumer and outbox/worker.py
       dead-letters an unregistered event on the first attempt with no retry;
       otp.issued cannot carry a plaintext code in a payload without breaking
       the invariant at otp_service.py:5. The founder decision chose the gate
       plus an honest allowlist over forced migration.
    3  "events.md documents every event" — it documents the one shipped event
       fully, and the 13 deferred with a named trigger each. Documenting a
       schema for an event with no consumer would be inventing a contract.

  The week's real finding is that ADR-002's gap was never 12 missing producers.
  It is 12 missing consumers, plus one security constraint nobody had written
  down. Discovering that on Day 1 rather than Day 4 is what the inventory was
  for.

  Two process notes worth carrying:
    - Stacked PRs get no CI. ci.yaml triggers on pull_request branches [main]
      only, so a PR targeting another branch runs nothing. Every W9 branch
      targeted main directly to work around it. Worth fixing if stacking
      continues.
    - A compose edit shipped a duplicate key that yaml.safe_load accepted and
      Compose rejected. Validate with the parser that matters.
---
```

---

### 2026-11-23 — Free-entry route unwired + Nigerian classification research

```yaml
---
ts: 2026-11-23T00:00:00Z
agent: bmad-agent-architect (Winston) + general-purpose research subagent
session: claude-code
artefact:
  - _bmad-output/planning-artifacts/research/nigerian-draw-classification-research-2026-11-23.md
  - atlas.ticket.{routes,schemas,service,models,__init__}
  - backend/tests/ticket/test_free_entry.py (deleted)
  - backend/tests/e2e/test_flagship_flow.py (step 10 removed)
  - backend/tools/check_outbox_invariant.py (allowlist note)
  - admin/src/app/(public)/{how-it-works,responsible-play}/page.tsx
  - README.md §Legal model
operation: created + amended
inputs:
  - PRD.md §1, §3.1
  - _bmad-output/planning-artifacts/legal/counsel-engagement-brief.md §3 Q1
  - docs/adr/ADR-002, ADR-005, ADR-009, ADR-010
human_review:
  reviewer: Adaeze (atlas-compliance-risk) — NOT YET PERFORMED
  status: not-yet-reviewed
  comments: |
    BLOCKING. Ticket is a compliance-sensitive module (AINE-AGENTS.md §3);
    Adaeze is a mandatory reviewer. Public regulatory copy was edited, which
    is an AINE-AGENTS.md §6 gate (Adaeze -> Legal Counsel). Must not merge
    without her verdict.
notes: |
  Founder decision (Tier 3, AINE-AGENTS.md §5) to remove the free-entry
  route, leaving the skill question as the sole lottery-avoidance mechanism.
  Architect advised against on the evidence and the founder reaffirmed;
  recorded as a decision, not an omission.

  Implementation is UNWIRE-ONLY. Code paths removed (POST /tickets/free,
  issue_free, FreeEntrySlip ORM, free-entry schemas). Deliberately RETAINED:
  the free_entry_slips table, its UNIQUE (draw_id, slip_reference) index, and
  the 'free' member of the entry_source CHECK constraint — historical tickets
  carry entry_source='free', published commit-reveal proofs report the
  paid/free split (PRD §3.1), and the ADR-005 audit chain holds
  ticket.free_transcribed entries. No migration was written. Restoring the
  route is code-only.

  Research finding that supersedes the project's legal premise: the National
  Lottery Act 2005 was nullified by the Supreme Court of Nigeria in
  AG Lagos v AG Federation (22 Nov 2024); lottery/gaming is now exclusively
  a State matter. On the research's reading of the Lagos State Lotteries and
  Gaming Authority Law 2021, "Gaming" requires only chance and a prize with
  no payment element, and no skill or free-entry carve-out exists — so all
  three candidate models require a State licence. PRD §1 and counsel brief
  Q1/Q5/Q7 are framed against a void statute and need rewriting BEFORE the
  brief is transmitted. Nigerian gaming counsel not yet engaged.

  ADRs were NOT amended — ADR-001/004/005 reference the free route and
  require the delivery-framework.md §12 amendment process through Winston.
  PRD amendment likewise outstanding.

  Follow-up in the same session: REVIEW-002 raised at docs/compliance/
  reviews/REVIEW-002-free-entry-route-removal.md. Verdict — engineering
  approved, posture rejected (the sole surviving mechanism is the skill
  question, which REVIEW-001 §3.1 already rejected for real-user launch and
  never re-approved). Its §6 escalation was actioned immediately: the public
  responsible-play page asserted a permanent self-exclusion regime, an
  in-app self-exclude flow, and age verification at every purchase. None
  existed (no self_exclusions table, no closure endpoint, no purchase-time
  age check; mobile says self-exclude lands in V1). Copy corrected to state
  only what the platform does. "GamCare Nigeria" relabelled "GamCare (UK)"
  — the link was always the UK site. Restoring the stronger wording is
  gated on ADR-010 actually shipping.

  CLAUDE.md local-env caveats rewritten: Zscaler resolved 2026-11-23
  (confirmed by a clean `docker compose build backend worker`), replaced
  with the stale-image gotcha below.

  Verification: ruff clean; `make typecheck` green (mypy 75 files + admin
  tsc); `make lint` green (flutter analyze clean); `make test` green —
  274/274 backend (was 282, 8 free-entry tests removed) + 5/5 admin vitest;
  ADR-002 outbox gate green. NOTE: the first `make test` of this session was
  a FALSE GREEN — the docker backend service bakes source at build time with
  no bind mount, and the image was ~2 months stale, so it ran code that
  still contained the deleted route. Caught by grepping inside the
  container. Images rebuilt and the suite re-run; the gotcha is now recorded
  in CLAUDE.md §Local-env caveats.
---
```

---


### 2026-11-24 — REVIEW-002 follow-through: surface sweep, risk register, counsel brief

```yaml
---
ts: 2026-11-24T00:00:00Z
agent: atlas-compliance-risk (Adaeze)
session: claude-code
artefact:
  - docs/compliance/reviews/REVIEW-002-free-entry-route-removal.md (Addendum A)
  - docs/risk-register.md (R-REG-08/09/10)
  - _bmad-output/planning-artifacts/legal/counsel-engagement-brief.md (major revision)
  - docs/runbooks/payment-outage.md
  - docs/VISUAL-WALKTHROUGH.md
operation: amended
inputs:
  - docs/compliance/reviews/REVIEW-002 §5.2(b), §7
  - docs/compliance/reviews/REVIEW-001 §3.1, §6.1
  - _bmad-output/planning-artifacts/research/nigerian-draw-classification-research-2026-11-23.md
human_review:
  reviewer: S1408661 (Founder / EL)
  status: not-yet-reviewed
  comments: |
    Counsel brief must not be transmitted until the founder has read the
    revision. Risk-register change log entry marked "pending Founder".
notes: |
  Discharges REVIEW-002 §7 items 2 and 8.

  SURFACE SWEEP (Addendum A). No withdrawn free-route copy remains on any
  live surface. Two live operational docs were wrong and are corrected: the
  payment-outage runbook told on-call that the free postal route "remains
  available" during a Paystack outage, and VISUAL-WALKTHROUGH narrated
  free-route sections that no longer exist (screenshot-set caveat added).
  Versioned artefacts (PRD, delivery-framework, ADR-004/005) left for the
  §12 amendment process. Design wireframes, checkpoints, build plans, demo
  plan and REVIEW-001 left intact as historical records — editing them to
  match today's product would falsify the audit trail, the same objection
  that applies to rewriting a published proof.

  KEY FINDING — R-FREE-01. The free-entry route was never operable. No P.O.
  box was ever leased; Adaeze flagged it in REVIEW-001 §6.1 on 2026-07-08
  and it stayed open. For the whole V0.5 demo period the public surface
  advertised a free postal route with no address to post to. This softens
  the §2 dissent on substance (removing an inoperable route is more honest
  than keeping it) and establishes the real pattern: consumer copy shipping
  ahead of implementation. Three instances found this week, none caught by
  CI. Standing requirement added (Addendum A.4) and a mechanised
  copy-to-capability gate requested from Murat, modelled on the ADR-002
  outbox gate.

  RISK REGISTER. R-REG-08 (copy ahead of implementation), R-REG-09 (skill
  question is sole mechanism and fails this office's own standard),
  R-REG-10 (register's governing statute void for twelve months unnoticed)
  — all three scored BLACK. R-FREE-01 and R-SKILL-01 had been recorded only
  inside a Day-9 wireframe and never entered the register; Adaeze recorded
  that as her own omission. R-REG-01/02 and §8 remain STALE pending
  rescoring against Lagos State law — outstanding, should not wait on
  counsel.

  COUNSEL BRIEF. Substantial revision of §1, §2, Q1, Q5, Q6, Q7, §4 before
  transmission. Q7 promoted Medium -> CRITICAL and is now to be answered
  first (which regime governs); Q1 reframed from "is our carve-out valid"
  to "licensable, at what cost, and is the business viable at that cost";
  Q5 raised Medium -> HIGH (advertising an unlicensed scheme may itself be
  an offence, and a "skill influences chance" claim may be independently
  misleading). The brief now discloses, unprompted, that the skill question
  would probably fail the nearest published benchmark, that ADR-010 was
  never built, that the free route never had an address, and that the PRD
  and delivery framework are superseded-but-unamended with §2 of the brief
  governing on conflict. Counsel is told not to optimise toward a preferred
  outcome because Atlas does not have one, and is invited to pause after
  Q1/Q7 rather than bill through Q2-Q8 if the model cannot proceed.

  STILL OUTSTANDING: founder review of the brief before sending; Lagos
  gaming counsel not engaged; PRD §1/§3.1 and delivery-framework amendments
  via §12; ADR-004/005 amendments via Winston; ADR-010 build; REVIEW-001
  §3.1/§3.2 skill remediation; docs/compliance/skill-questions.md unwritten;
  R-REG-01/02 and §8 rescoring.
---
```

---


### 2026-11-24 — Risk rescore against Lagos State law + PRD amendment proposed

```yaml
---
ts: 2026-11-24T12:00:00Z
agent: atlas-compliance-risk (Adaeze)
session: claude-code
artefact:
  - docs/risk-register.md (§1 R-REG-01/02 restated; §8.1/§8.4 rewritten)
  - _bmad-output/planning-artifacts/amendments/AMEND-001-prd-free-entry-route-removal.md (new)
operation: amended + created
inputs:
  - _bmad-output/planning-artifacts/research/nigerian-draw-classification-research-2026-11-23.md
  - _bmad-output/planning-artifacts/delivery-framework.md §12
  - docs/compliance/reviews/REVIEW-001 §3.1, §6.1; REVIEW-002 Addendum A
human_review:
  reviewer: John (bmad-agent-pm) as PRD owner, then S1408661 (Founder/EL)
  status: not-yet-reviewed
  comments: |
    AMEND-001 is a PROPOSAL. The PRD is unchanged on disk. Per
    delivery-framework.md §12 step 2 the owner agent reviews before
    anything is applied.
notes: |
  RISK RESCORE. R-REG-01 restated: was "NLRC classifies Atlas as a lottery",
  now "Atlas operates inside a State gaming perimeter without a licence" —
  likelihood M -> H, stays BLACK. Mitigation (3) from the original row was
  STRUCK: mechanic design (free-route equality, substantive skill question)
  is legally inert if the governing definition needs only chance and a
  prize. R-REG-02 was inverted and is restated: Lagos is the FIRST licence,
  not a second, and per-State licensing may reduce V1's addressable market
  from Nigeria to Lagos — which invalidates any market sizing built on
  "Nigeria only". Likelihood M -> H.

  §8 Plan B rewritten. The old §8.1 treated a federal NLRC licence as its
  primary fallback; that path no longer exists and is struck, as is
  "redesign to strengthen the prize-competition case". Lagos State licensing
  is promoted from option 3 to option 1, with the reported ₦250-400m year-one
  cost flagged as the figure that decides whether Atlas exists in its current
  form. A promotional-competition permit (counsel Q7.4) is identified as the
  single highest-leverage unknown in the engagement — everything else should
  wait on that answer. "Abandon Nigeria for Ghana/Kenya/SA" rises in the
  order but is flagged as an unknown rather than an escape hatch: no
  regulatory research exists for any of those markets, and the Nigerian
  position was also assumed benign for five months. §8.4 now records
  directors' personal criminal exposure (founder is sole director) as a
  disclosure due BEFORE any launch decision, and notes that advertising
  exposure may precede operating exposure. §8.2/§8.3 unaffected — AML and
  NDPA obligations do not turn on classification.

  PRD AMENDMENT. AMEND-001 proposes rewriting PRD §1 (two mechanics -> one,
  with the removed one recorded rather than erased), the §1 Nigerian legal
  caveat (reframed off the void NLA 2005 onto Lagos State law, and extended
  to gate MARKETING spend as well as code, since promoting an unlicensed
  scheme may itself be an offence), and §3.1 (free-route bullets struck;
  entry_source documented as 'paid' | 'free', correcting a long-standing
  drift where the PRD said 'postal_free' and the schema always said 'free';
  retention of the table and enum value recorded as deliberate).

  §12 BREACH RECORDED. The hard rule is "no in-flight code change
  retro-justifies an artefact change — spec changes first, then code
  follows". The code shipped 2026-11-23; this amendment is the spec catching
  up. Recorded in AMEND-001 §0 rather than quietly retro-fitted. No remedy
  proposed beyond the record — reverting working code to restore process
  order would be theatre — but the next change of this class goes spec-first.
---
```

---


### 2026-11-24 — ADR-010 Phase A: self-exclusion built and enforced

```yaml
---
ts: 2026-11-24T15:00:00Z
agent: bmad-agent-architect (Winston) + bmad-agent-dev (Amelia)
session: claude-code
artefact:
  - docs/adr/ADR-010 (amendment 2026-11-24)
  - _bmad-output/implementation-artifacts/adr-010-self-exclusion-build-plan.md
  - backend/migrations/versions/20261124_0900_0012_self_exclusions.py
  - atlas.identity.self_exclusion (new module)
  - atlas.identity.{models,schemas,routes,session_service}
  - atlas.ticket.{service,routes}; atlas.skill.{service,routes}
  - backend/tests/identity/test_self_exclusion.py (13 tests)
  - admin/src/app/(public)/responsible-play/page.tsx
operation: created + amended
inputs:
  - docs/adr/ADR-010; ADR-007 (unbuilt — the blocker)
  - docs/compliance/reviews/REVIEW-002 §6, §7 item 3
  - docs/risk-register.md R-REG-08
human_review:
  reviewer: Adaeze (atlas-compliance-risk) + Murat (bmad-tea)
  status: not-yet-reviewed
  comments: |
    Identity is compliance-sensitive (AINE-AGENTS.md §3) — Adaeze is a
    mandatory reviewer and consumer copy changed again. NOT MERGED.
notes: |
  ADR-010 could not be built as written: its primary enforcement point is
  "at KYC submission" and there is no KYC module (ADR-007 approved, never
  built). BVN is collected nowhere — only an unused bvn_pepper in config.
  Amended to two phases; Phase A ships, Phase B blocked on ADR-007.

  SPEC FIRST THIS TIME. The ADR-010 amendment was written and committed to
  the ADR before any code, correcting the §12 sequencing failure recorded
  in AMEND-001 §0.

  PHASE A DELIVERED. Migration 0012 creates self_exclusions keyed on
  user_id (NOT bvn_hash as the base ADR specified — nothing to key on),
  with bvn_hash nullable+unique so Phase B is a backfill, not a migration
  of a live table. New sole-writer module atlas.identity.self_exclusion.
  exclude() is one transaction: registry row -> users.status='closed' ->
  revoke every session -> audit, returning (row, sessions_revoked) so the
  API reports what actually happened rather than guessing.

  FOUND FREE: users.status already permitted 'closed' and nothing had ever
  set it; session_service already refused any user whose status != 'active'.
  So ADR-010's login enforcement needed no new login code. This module is
  the first writer of 'closed' since migration 0001.

  DEFECT IN THE BASE ADR CLOSED. The ADR named KYC, registration and login
  as enforcement points and omitted PURCHASE entirely — a closed user
  holding a live session could have bought a ticket. Check added to
  ticket.service.issue_paid (service layer, because the webhook reaches it
  without the route) and to skill.service.next_question, plus a route-level
  403 pre-check so an excluded user never sees a checkout page.

  WALLET REFUND DELIBERATELY NOT IMPLEMENTED. ADR-010 requires refund to
  the originating method with escheatment fallback. There is no Paystack
  refund call and docs/compliance/escheatment-policy.md was never written.
  Phase A HOLDS the balance and surfaces it to support. Emitting a refund
  the system cannot perform is the exact defect the amendment corrects.
  Adaeze to confirm holding is acceptable; escheatment policy is hers and
  gates Phase B.

  COPY. responsible-play updated to the Phase A truth and only that: the
  account can be closed permanently (true, enforced), there is no in-app
  switch yet (true — A5 unbuilt, support is the route today), and closing
  one account does not stop a new one (true — needs BVN/KYC). The
  withdrawn "a fresh account cannot bypass it" sentence stays withdrawn.
  test_phase_a_does_not_block_reregistration pins that limit so it fails
  loudly if Phase B lands without the copy being updated in the same change.

  VERIFICATION: 287/287 backend tests pass (274 -> 287, +13), both natively
  and through a rebuilt docker image via `make test`; ruff clean; mypy src
  clean (76 files); ADR-002 outbox gate green (62 files, 29 allowlisted,
  self_exclusion.activated allowlisted as deferred); CI identity-table
  boundary grep clean; admin lint, tsc and vitest green.

  NOT DONE: A5 mobile settings flow, A6 admin read-only exclusion list.
  Phase A is therefore API-complete but not yet self-service — the copy
  says so rather than implying a control that does not exist.

  DEPLOY: not possible. There is no deploy pipeline and no production
  environment — .github/workflows/ contains only ci.yaml with no deploy
  job, infrastructure/ holds demo scripts only, and the Makefile has no
  deploy target. Managed-platform commitment was deferred by founder
  decision during the V0.5 demo-first pivot (risk register change log,
  2026-07-02). PRD §1 would block a real-money deploy regardless: counsel
  has not been engaged.
---
```

---


### 2026-11-24 — Phase A completed (A5 mobile, A6 admin) + compliance approval

```yaml
---
ts: 2026-11-24T17:00:00Z
agent: bmad-agent-dev (Amelia) + atlas-compliance-risk (Adaeze)
session: claude-code
artefact:
  - mobile/lib/features/account/self_exclusion_screen.dart (new)
  - mobile/lib/features/identity/identity_api.dart
  - mobile/lib/features/home/home_screen.dart
  - admin/src/app/(admin)/admin/self-exclusions/page.tsx (new)
  - admin/src/design/components/Sidebar.tsx
  - atlas.identity.{routes,schemas} — GET /api/v1/self-exclusions
  - backend/tests/identity/test_self_exclusion.py (17 tests)
  - admin/src/app/(public)/responsible-play/page.tsx
  - docs/compliance/reviews/REVIEW-002 (Addendum B)
operation: created + amended + reviewed
inputs:
  - docs/adr/ADR-010 (amendment 2026-11-24)
  - _bmad-output/implementation-artifacts/adr-010-self-exclusion-build-plan.md A5/A6
human_review:
  reviewer: Adaeze (atlas-compliance-risk) — COMPLETE, approved
  status: approved
  comments: |
    REVIEW-002 Addendum B. First change this week approved without a
    standing objection. Murat sign-off still outstanding. Founder/EL
    approval still required for merge.
notes: |
  A5 + A6 close out ADR-010 Phase A, which is now self-service rather than
  API-only.

  A5 — mobile. New SelfExclusionScreen reached from an underlined text
  button on the account panel, replacing the "Self-exclusion + profile
  settings land in V1" placeholder. Typed EXCLUDE + login_mfa OTP, both
  re-checked server-side. The limitation panel ("What this does not do")
  sits ABOVE the confirmation field, not below: no retention offer, no
  softer alternative, and a line pointing at independent support as more
  useful than the button itself.

  A6 — admin. GET /api/v1/self-exclusions, superadmin-gated, read-only.
  New admin page states the Phase A limitation where the operator reads
  it. test_registry_has_no_mutation_verbs asserts DELETE/PATCH/PUT are
  absent, so adding an un-exclude control is a failing test rather than a
  code-review catch.

  SWEEP MISS CORRECTED. The Addendum A sweep missed the sidebar link to
  /admin/free-entries — my grep matched "free entry"/"free-entry" but not
  "free-entries". Removed, and a Self-exclusions link added in its place.

  COMPLIANCE REVIEW. Adaeze approved the amendment, implementation,
  enforcement coverage, copy and admin surface, and discharged REVIEW-002
  §7 item 3. She recorded that the purchase-path enforcement gap was a
  defect she had not caught in REVIEW-001 or REVIEW-002 §6, and singled out
  test_phase_a_does_not_block_reregistration — a test asserting a
  LIMITATION, designed to fail when Phase B lands — as the pattern she
  wants generalised from Addendum A.4.

  HER TWO CONDITIONS, BOTH CLOSED IN-SESSION. (B.4) the page still said
  there was no in-app switch, which A5 had just made false — understating a
  capability, the opposite of this week's other defects, but corrected
  anyway because the standing requirement has no size threshold. (B.3) a
  user closing an account with a balance was told nothing about it; both
  the web page and the mobile screen now state the balance is held and paid
  out by support, not forfeited. The mobile placement was deliberate: the
  decision is taken there.

  VERIFICATION: 291/291 backend tests (287 -> 291), green natively and via
  `make test` on a rebuilt image; ruff clean; make typecheck clean (mypy 76
  files + admin tsc); make lint clean (flutter analyze no issues, ESLint
  clean); ADR-002 outbox gate green; CI identity-boundary grep clean.

  STILL OPEN: Murat sign-off; docs/compliance/skill-questions.md and
  escheatment-policy.md (both Adaeze, overdue); R-REG-09 (skill question
  remains sole classification mechanism, still rejected for real-user
  launch); no per-user cap or spend ceiling (founder decision); Phase B
  blocked on ADR-007. Deploy remains impossible — no pipeline, no
  environment, counsel not engaged.
---
```

---


### 2026-11-26 — Test review TR-001: P0 enforcement gap found and closed

```yaml
---
ts: 2026-11-26T12:00:00Z
agent: bmad-tea (Murat)
session: claude-code
artefact:
  - _bmad-output/test-artifacts/test-reviews/TR-001-adr-010-phase-a.md
  - backend/tests/identity/test_self_exclusion.py
operation: reviewed + amended
inputs:
  - PR #15; docs/adr/ADR-010 (amendment 2026-11-24)
  - docs/compliance/reviews/REVIEW-002 Addendum A.4, B
  - TEA knowledge: test-quality, test-priorities-matrix, risk-governance
human_review:
  reviewer: S1408661 (Founder / EL)
  status: not-yet-reviewed
  comments: |
    Gate: CONCERNS — approved for merge. Clears the Murat sign-off that
    Adaeze's REVIEW-002 Addendum B approval was conditional on. EL
    approval still outstanding.
notes: |
  P0 GAP FOUND AND CLOSED. Self-exclusion is regulatory compliance, so P0
  on the priorities matrix. The service-layer check in issue_paid was
  tested; the 403 pre-check on POST /tickets/purchase was NOT. Deleting
  that block left all 291 tests green — an enforcement path with no
  signal. Risk P2 x I3: an excluded user reaches a live checkout and a
  payment intent is created against a closed account. Two tests added
  (TestPurchaseRouteEnforcement), plus one for the same gap on
  GET /draws/{id}/skill-questions/next.

  MY OWN FIRST TEST WAS TOO WEAK, AND I REWROTE IT. The initial version
  posted random draw/entitlement ids. It went red on mutation — but with
  404, because it fell through to the draw lookup. A red for the wrong
  reason would also fire on an unrelated routing change and never
  demonstrates the property. Rewritten to issue an otherwise-VALID
  purchase (real sales_open draw, real entitlement earned before
  exclusion). Mutation now yields `assert 201 == 403` — without the guard,
  an excluded user successfully buys a ticket. Also asserts no
  payment_intents row is created. Principle: a test going red is not the
  same as a test proving something; check what the red says.

  COMMENDED: enforcement tested at the service layer because the payment
  webhook reaches issue_paid without the route;
  test_phase_a_does_not_block_reregistration asserting a LIMITATION built
  to fail when Phase B lands (the mechanised copy-to-capability check
  Adaeze asked for in Addendum A.4 — generalise it); absence-of-capability
  tests for the missing un-exclude path; idempotency asserted by counting
  side effects (0 sessions revoked, no second audit event) rather than
  just not erroring.

  DELETED COVERAGE AUDITED. test_free_entry.py's 8 tests went with the
  route. No orphaned coverage — paid-ticket ticket_number monotonicity
  survives in test_purchase_flow.py; the mixed paid/free numbering case
  died with the feature, correctly.

  OPEN, NON-BLOCKING: no E2E exclusion path (P1); no widget test for
  SelfExclusionScreen, compliance-critical UI with zero coverage while
  the pattern already exists in password_screen_test.dart (P1); test file
  482 lines vs <300 DoD, split along the existing class seam.

  PRE-EXISTING DEBT RECORDED, NOT THIS PR'S: _register_login
  reimplemented across 10 test files (this change added the tenth);
  phone generation uses `uuid4().int % 1_000_000` — random data that can
  collide, the exact bug class behind W8's three flaky tests, held
  harmless today only by function-scoped truncation; admin UI has 5 tests
  in total.

  VERIFICATION: 293/293 backend (291 -> 293) + 5/5 admin, green natively
  and via `make test` on a rebuilt image. No flakes across repeated runs.
---
```

---


### 2026-11-26 — AMEND-001 owner review (John): approved with required additions

```yaml
---
ts: 2026-11-26T13:00:00Z
agent: bmad-agent-pm (John)
session: claude-code
artefact:
  - _bmad-output/planning-artifacts/amendments/AMEND-001-prd-free-entry-route-removal.md
operation: reviewed
inputs:
  - PRD.md §1, §2, §3.1, §3.2, §10
  - docs/adr/ADR-010 (amendment 2026-11-24)
  - docs/compliance/reviews/REVIEW-002 §6.1
  - docs/risk-register.md R-REG-02
  - _bmad-output/planning-artifacts/research/nigerian-draw-classification-research-2026-11-23.md
human_review:
  reviewer: S1408661 (Founder / EL)
  status: not-yet-reviewed
  comments: |
    §12 step 2 complete — PRD owner has reviewed. Passes to founder as EL
    approver. PRD still UNCHANGED on disk; AMEND-001 is not applied.
notes: |
  VERDICT: approved subject to four additional sections being incorporated.
  The proposal amended two sections of a document wrong in five places;
  applying it as drafted would have left the PRD internally inconsistent —
  §1 stating one mechanic while §2 still promised users a free entry route
  and §3.2 still promised a protection that does not exist.

  REQUIRED ADDITIONS, now drafted into AMEND-001 §6:
  - §3.2 was untouched and is now false. It reads "a user can self-exclude
    permanently from settings. Re-registration with the same BVN is
    blocked." ADR-010 cites §3.2 as its source requirement; its amendment
    split delivery, so sentence one is shipped and sentence two is blocked
    on ADR-007 with no date. Rewritten as two explicit bullets — Phase A
    shipped, Phase B NOT DELIVERED — so the spec states the boundary that
    test_phase_a_does_not_block_reregistration enforces. This is the
    omission that mattered: the proposal corrected a removed feature while
    leaving a never-built protection described as real, which is the exact
    defect that produced REVIEW-002 §6.
  - §2 consumer bullet still sells "Enter for free via a documented
    free-entry route" as V1 scope.
  - §2 operator bullet still lists "max entries" in draw configuration;
    entries_cap was never enforced and the founder decided against caps.
  - §10 Phase 0 exit still requires "Free-entry route operationalised:
    P.O. box leased" — a criterion that can never be met, sitting in a
    checklist nobody reads until someone tries to close Phase 0. Replaced
    with "Nigerian gaming counsel engaged and Q7/Q1 answered".

  DISAGREEMENT RECORDED. The proposal treated market sizing as "not a PRD
  section". Rejected: "Nigeria only" is a §2 scope statement, §3 is
  written against it, and §7's V2 plan depends on it. R-REG-02 says
  per-State licensing may reduce V1's market to Lagos. Tracked as
  AMEND-002-pending, gated on counsel Q7.2.

  PRODUCT QUESTION RAISED, OUTSIDE THE AMENDMENT PROCESS. PRD §1 is "The
  product decision" and its rationale was that two mechanics kept Atlas
  outside gambling regulation. One is removed; the other is legally inert
  in Nigeria on current research; the removed one would have been inert
  too. The decision now rests on nothing that survives the governing law.
  John's recommendation: do not apply AMEND-001 or build further product
  against this PRD until counsel answers Q7 and Q1 — amending §1 is
  accurate bookkeeping, but the premise is pending a verdict from a firm
  that has not been engaged. "The smallest thing that validates the
  assumption here is not a feature. It is an email to a Lagos gaming firm."
---
```

---


### 2026-11-26 — Skill question removed; Atlas stops claiming a carve-out

```yaml
---
ts: 2026-11-26T16:00:00Z
agent: bmad-agent-pm (John) + bmad-agent-dev (Amelia) + atlas-compliance-risk (Adaeze)
session: claude-code
artefact:
  - _bmad-output/planning-artifacts/amendments/AMEND-003-prd-skill-question-removal.md (new)
  - docs/compliance/reviews/REVIEW-003-skill-question-removal.md (new)
  - docs/risk-register.md (R-REG-09 closed, R-REG-11 opened)
  - atlas.skill (unwired; routes.py deleted), atlas.ticket.{service,routes,schemas}
  - atlas.payment.service (webhook), atlas.main (router unregistered)
  - mobile: features/tickets/entry_purchase_screen.dart (new), features/skill (deleted)
  - admin: how-it-works, responsible-play, (public)/layout, Sidebar
  - infrastructure/scripts/seed_v0_5.py
operation: created + amended
inputs:
  - counsel-engagement-brief Q1.5, Q1.6
  - research/nigerian-draw-classification-research-2026-11-23.md
  - REVIEW-001 §2.1, §3.1; REVIEW-002
human_review:
  reviewer: Adaeze — COMPLETE, approved without reservation (REVIEW-003)
  status: approved
  comments: |
    Founder/EL approval still required. AMEND-001 and AMEND-003 both
    remain PROPOSED — the PRD is unchanged on disk.
notes: |
  FOUNDER DECISIONS: skill question removed; free entry route confirmed
  not returning; State gaming licence pursued separately.

  Atlas now relies on NO mechanic to sit outside gambling regulation. It
  is a paid prize draw intending to operate under a State licence it does
  not yet hold. More coherent than what preceded it — the research
  indicates both mechanics were legally inert in Nigeria, so Atlas was
  paying conversion friction and postal operations for protection that
  probably did not exist.

  SPEC FIRST AGAIN. AMEND-003 was written before any code.

  CODE. Purchase is now gated only on an open draw and a non-excluded
  buyer. Removed: PurchaseTicketRequest.entitlement_id, check_entitlement,
  _validate_and_consume_entitlement, the three Entitlement* errors, the
  entitlement arg to issue_paid, the entitlement_id in payment metadata
  and the webhook read of it, the skill router registration and
  skill/routes.py. UNWIRED NOT DELETED: skill_questions,
  skill_question_options and skill_question_attempts are retained — the
  ADR-005 audit chain carries skill_question.* events whose subject_id
  references attempt rows. No migration. Seed script's question pool is
  now a documented no-op.

  MOBILE. SkillQuestionScreen WAS the purchase flow, so it was replaced
  rather than deleted: new EntryPurchaseScreen shows the prize, the price
  and the non-refundable terms, then opens Paystack checkout. Golden
  renamed skill-question -> entry-purchase and regenerated (the screen
  genuinely changed; regenerating is correct, not a workaround).

  COPY — the part Adaeze judged. With no mechanic left, "prize
  competition" became a bare legal assertion by the party it benefits.
  Per REVIEW-001 §2.1 Atlas must not arbitrate its own classification, so
  every classification claim was replaced with a mechanic or a verifiable
  property: "A prize competition, not a lottery" -> "Every draw is
  provably fair — and you can check it yourself"; "Provably fair prize
  competitions · Nigeria" -> "Provably fair draws · Nigeria". The skill
  question section is gone. Copy bans on lottery/raffle/luck UNCHANGED
  and still binding.

  RISK. R-REG-09 CLOSED — no skill question remains to fail a standard;
  docs/compliance/skill-questions.md is CANCELLED, not overdue (Adaeze's
  own late artefact, now unnecessary). R-REG-11 OPENED ⚫ — the entire
  legal basis is now a single licence Atlas does not hold, with no
  fallback if refused, delayed or priced out. Adaeze: "more honest and
  more concentrated. I would not trade back."

  UNCHANGED: PRD §1 hard prerequisite, extended by AMEND-001 §2.2 to bar
  public marketing spend as well as a real payment rail. Removing the
  mechanics does not bring launch closer; it clarifies what launch
  depends on.

  VERIFICATION: 267/267 backend (293 -> 267; 26 entitlement/skill tests
  removed with the feature) + 5/5 admin + 42/42 mobile, green natively and
  via `make test` on a rebuilt image. ruff (src tests), mypy src, ESLint,
  tsc, flutter analyze all clean. ADR-002 outbox gate green.
---
```

---


### 2026-11-27 — Live app verification: two defects tests did not catch

```yaml
---
ts: 2026-11-27T10:00:00Z
agent: bmad-agent-dev (Amelia)
session: claude-code
artefact:
  - infrastructure/scripts/demo_rehearsal.sh
  - atlas.identity.session_service (AccountClosed)
  - backend/tests/identity/test_self_exclusion.py
operation: amended
inputs:
  - docs/adr/ADR-010 §Enforcement points
  - AMEND-003 (skill question removal)
human_review:
  reviewer: Adaeze (login copy is consumer-facing) + S1408661 (EL)
  status: not-yet-reviewed
notes: |
  Ran the actual stack rather than only the suite. Two defects surfaced
  that 268 green tests did not.

  1. DEMO REHEARSAL WAS BROKEN BY AMEND-003. The repo's own flagship smoke
     script still answered a skill question and posted entitlement_id.
     Nothing in CI runs it, so the suite stayed green while the script that
     proves the demo honest was dead. It is a W9 §8 gate. Fixed: the
     answer-key helper is gone (and with it the ~47%-of-runs flake it once
     caused) and purchase posts draw_id alone. All 9 steps green.

  2. LOGIN CONTRADICTED ADR-010. §Enforcement points says a self-excluded
     user gets "this account has been closed"; live, they got
     invalid_credentials — indistinguishable from a typo, so a person who
     chose to stop is nudged to retry or contact support. The cause was
     ordering: status was checked BEFORE the password, so returning a
     distinct message there would have let anyone enumerate closed
     accounts by email alone. Reordered to verify the password first, then
     raise AccountClosed (403) only for a caller who has proved they hold
     the credentials; a wrong password on a closed account still returns
     invalid_credentials. Also the more timing-uniform order. Two tests
     added, including one asserting the non-disclosure.

  THIRD FINDING, PROCESS NOT PRODUCT. The rehearsal discarded the webhook
  response with >/dev/null, so a signature rejection surfaced three steps
  later as "no ticket minted for first consumer". That cost a debug cycle
  chasing a phantom bug in my own change. It now checks the status and
  names the likely cause (the caller's shell lacking
  ATLAS_PAYSTACK_WEBHOOK_SECRET while docker compose reads it from .env).
  Demonstrated both ways: fails at step 2 with HTTP 401 without the
  secret, green with it.

  DRIVEN LIVE, NOT JUST LAUNCHED:
  - OpenAPI confirms no skill routes and no /tickets/free remain.
  - Full flagship flow: register -> purchase (no entitlement) -> signed
    webhook -> ticket minted -> close -> reveal -> proof -> independent
    verifier reproduces the winner -> audit chain verified. 6 winners.
  - Self-exclusion end to end: purchase 201 before; wrong MFA 400 with no
    state change; real MFA 201 (sessions_revoked 1, reversible false,
    cross_account_enforced false); old session 401; re-login 403
    account_closed; DB shows status=closed, bvn_hash NULL,
    excluded_by=user_self; audit carries bvn_enforced=false;
    re-registration with a new email returns 201 — the documented Phase A
    limit, observed rather than assumed.
  - Admin UI: /admin/self-exclusions is 307 to /login when unauthenticated
    and renders the live exclusion row as superadmin. Sidebar no longer
    offers Free entries or Skill questions.
  - Public pages: no "skill question", "prize competition", "free entry"
    or "not a lottery" anywhere in the rendered text; responsible-play
    carries the balance disclosure and the in-app route.

  NOT VERIFIED LIVE: the Flutter app. flutter analyze, 42 widget/golden
  tests and a regenerated golden cover EntryPurchaseScreen, but no
  simulator was driven. That gap stands.

  VERIFICATION: 268/268 backend + 5/5 admin + 42/42 mobile; make typecheck,
  make lint, ADR-002 outbox gate all green; demo_rehearsal.sh green.
---
```

---


### 2026-11-27 — Flutter app driven on a simulator; REVIEW-004

```yaml
---
ts: 2026-11-27T11:30:00Z
agent: bmad-agent-dev (Amelia) + atlas-compliance-risk (Adaeze)
session: claude-code
artefact:
  - docs/compliance/reviews/REVIEW-004-closed-account-login-message.md (new)
  - mobile/lib/services/api_client.dart (docstring correction)
operation: reviewed + amended
human_review:
  reviewer: S1408661 (Founder / EL)
  status: not-yet-reviewed
notes: |
  CLOSED THE GAP NAMED YESTERDAY. The Flutter app had been verified only
  by analyze and widget/golden tests. It has now been built for iOS and
  launched on a booted iPhone 17 Pro simulator (iOS 26.5) against the live
  backend; a screenshot confirms the registration screen renders — a real
  launch, not a blank frame. The regenerated entry-purchase golden was
  also inspected rather than trusted: prize copy, "One entry", correct
  ₦500 formatting from 50000 minor units, the non-refundable disclosure
  and the "Pay ₦500 and enter" action all render, with no skill question
  anywhere.

  NOT FULLY DRIVEN, AND WHY. Automating the simulator UI to reach
  EntryPurchaseScreen needs accessibility permission for osascript, which
  macOS refuses (-1719) and which is a system privacy setting I declined
  to change on the founder's machine to serve a test. idb is not
  installed. So the screen is verified by golden render plus direct API
  exercise, not by a tap-through. The gap is narrower than yesterday, not
  closed.

  NEW FINDING — api_client docstring was wrong. It claimed
  "iOS simulator, Android emulator + Chrome dev: http://localhost:8000
  works". Chrome does NOT work: the backend registers no CORS middleware,
  and a live probe returned OPTIONS 405 with no Access-Control-Allow-Origin
  header, so any browser-hosted build is blocked at preflight. Corrected,
  and the remedy flagged as Tobi's — CORS allowed-origins is
  security-relevant config, not a dev convenience, and I would not add it
  merely to make my own verification pass. Flutter web DOES build
  successfully; it just cannot reach the API from a browser.

  REVIEW-004 (Adaeze) — approved the closed-account login message. She
  recorded that she had missed it herself in REVIEW-002 Addendum B:
  she verified login was REFUSED but not what the refused user was TOLD,
  and those are different questions. Her note on why it matters: a person
  returning after self-excluding, often at the point of weakest resolve,
  was told their password was wrong — predictably prompting a retry, a
  reset, or a support contact, three further touchpoints with a platform
  they asked to be shut out of. The control worked; the communication
  undermined it.

  She also notes the disclosure risk the fix had to avoid: exclusion
  status indicates a user's relationship with gambling harm and is
  plausibly NDPA special-category data (counsel Q4), so the closed-account
  message is gated behind the password check and a test asserts the
  non-disclosure.

  STANDING REQUIREMENT EXTENDED. Addendum A.4 required code plus a test
  behind every claim. Adaeze extends it: where an ADR specifies what a
  user is TOLD, the assertion must cover the message, not merely the
  outcome. Fourth defect this month in the same family — a documented
  behaviour the system did not exhibit — but the first where the ADR was
  right and the implementation drifted, rather than copy overclaiming.
### 2026-11-27 — AMEND-001 and AMEND-003 applied to the PRD

```yaml
---
ts: 2026-11-27T13:00:00Z
agent: bmad-agent-pm (John)
session: claude-code
artefact:
  - _bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md
  - _bmad-output/planning-artifacts/amendments/AMEND-001 (status -> APPLIED)
  - _bmad-output/planning-artifacts/amendments/AMEND-003 (status -> APPLIED)
operation: amended
inputs:
  - AMEND-001 (owner review 2026-11-26), AMEND-003
  - docs/compliance/reviews/REVIEW-002, REVIEW-003, REVIEW-004
  - research/nigerian-draw-classification-research-2026-11-23.md
human_review:
  reviewer: S1408661 (Founder / Engineering Lead) — APPROVED
  status: approved
  comments: |
    Founder instruction "update the prd that describes what no longer
    exist" taken as the EL approval that delivery-framework §12 step 2
    was waiting on. Owner review was John's, 2026-11-26.
notes: |
  §12 step 3 complete for both amendments. §12 step 4 is this entry.

  SECTIONS APPLIED: §1 product decision (both mechanics struck through,
  not deleted — the PRD records the decision rather than pretending the
  mechanics were never specified); §1 Nigerian legal caveat (rewritten off
  the void NLA 2005 onto Lagos State law, and extended to gate MARKETING
  spend as well as a real payment rail); §2 consumer and operator bullets;
  §3.1 retitled "Draw mechanics" with the retention rule for entry_source
  'free', free_entry_slips and skill_question_* made explicit; §3.2
  self-exclusion split into Phase A shipped / Phase B NOT DELIVERED; §10
  Phase 0 exit criteria.

  SWEPT BEYOND THE NAMED SECTIONS. The amendments named seven sections;
  the PRD described the removed features in eleven more. Also corrected:
  §2 "mobile-first prize competition platform"; §2 success criterion 2
  ("holds up under NLRC scrutiny" — the NLRC has no national licensing
  authority); §3.3 skill-question resume window; §3.3 ticket-issue
  preconditions (now payment + open draw + not self-excluded); §4 Ticket
  module scope and module-ownership reviewer note; §10 Phase 0 counsel
  criterion and beta-phase flows; §11 open questions 1, 4 and 5 (4 and 5
  closed outright). Leaving these would have produced exactly the
  half-corrected specification John warned about in his owner review §1.

  CORRECTION TO AMEND-001'S OWN TEXT, caught while applying it. The §3.2
  wording proposed in §6.3 said closure is enforced "at login, at ticket
  purchase and at skill-question issue". That third point no longer
  exists — AMEND-003 unwired the skill module, so the check is
  unreachable. The applied text names login and ticket purchase only. An
  amendment drafted before a sibling amendment landed described a state
  that no longer held by the time it was applied.

  STILL OUTSTANDING, deliberately not in this change:
  - delivery-framework.md §§49-52, 122, 131, 260, 321, 394 — free-route
    operationalisation and Legal-Counsel-approved free-entry copy in phase
    gates. Needs its own amendment (Winston + John).
  - ADR-004 §51 and ADR-005 §67 free-entry references — Winston's, per
    CLAUDE.md's rule against retroactive ADR edits.
  - AMEND-002 (V1 market scope: "Nigeria only" vs per-State licensing),
    gated on counsel Q7.2.
---
```

---


### 2026-11-27 — Draws tab: swipeable carousel for concurrent draws

```yaml
---
ts: 2026-11-27T17:00:00Z
agent: bmad-agent-dev (Amelia)
session: claude-code
artefact:
  - mobile/lib/features/home/home_screen.dart (_DrawCarousel)
  - mobile/test/features/draws/draw_carousel_test.dart (new, 7 tests)
  - mobile/test/design/screen_goldens_test.dart + goldens/draws-carousel.png
operation: created
inputs:
  - PRD.md §2 "Browse currently active draws" (plural — already in scope)
human_review:
  reviewer: Sally (bmad-agent-ux-designer) — not yet reviewed
  status: not-yet-reviewed
  comments: |
    UI-only. No schema, no API, no spec amendment: the backend already
    returned a list and the PRD already said "draws". Sally should see the
    carousel treatment since no wireframe covers it.
notes: |
  SCOPE CHECK FIRST. The founder asked for swipe-browsing of concurrent
  draws, not multiple prizes within one draw. Those are very different:
  multi-prize would need a prizes table, a prize_id on draw_winners, and an
  ADR-006 amendment because select_winners returns [primary, reserves] and
  changing that changes what a published proof asserts. Swipe-browsing is
  UI-only — GET /api/v1/draws already returns every sales_open draw with no
  cap, ordered by close_time ascending, and PRD §2 already says "Browse
  currently active draws", plural. Nothing to amend.

  WHAT CHANGED. The Draws tab was a vertical ListView; it is now a
  PageView carousel with viewportFraction 0.88 so the next card peeks —
  without that a carousel reads as a single static card and nobody swipes.

  ACCESSIBILITY DRIVEN THE DESIGN, not decorated it. A swipe-only surface
  hides inventory from anyone who cannot perform a horizontal drag, so:
  the page-indicator dots are real controls with 44pt touch targets and
  Semantics labels ("Go to draw 3 of 3"), and each page announces its
  position ("Draw 1 of 3") because a bare PageView gives a screen reader
  no signal that more draws exist. With one draw the indicator and the
  count are hidden entirely — dots that cannot move are noise, and
  "1 draws open" is wrong anyway.

  TESTS: 7, including the ordering contract (first page is the draw
  closing soonest, matching the backend's order_by close_time) and the
  single-draw and empty cases. Mutation-checked: setting the dots'
  onTap to null fails exactly one test — "every draw is reachable WITHOUT
  swiping" — and nothing else. The test guards the claim it names.

  GOLDEN ADDED AND INSPECTED, not merely passed: three draws, the count,
  the peeking second card, the elongated active dot.

  FINDING SURFACED BY LOOKING AT THE GOLDEN — pre-existing, NOT fixed
  here. _DrawCard derives its close label from close_time but its enter
  affordance from state, so a draw past close_time whose state is still
  sales_open renders "closed" AND "TAP TO ENTER" together. The backend
  agrees with the CTA (it accepts purchases while state is sales_open),
  so this is a labelling inconsistency during the window between
  close_time passing and the operator closing the draw. Left alone
  deliberately: it predates this change, it is not a carousel concern, and
  "should a past-close draw still be enterable" is a product question.
  Flagged for Sally and the founder.

  VERIFICATION: 50/50 mobile (43 -> 50), 268/268 backend, 5/5 admin;
  flutter analyze, make lint all green. Also exercised live — three
  concurrent draws seeded through the admin API and confirmed returned in
  close_time order by GET /api/v1/draws.
---
```

---


### 2026-11-27 — Sally's design review of the draws carousel (wireframe 16)

```yaml
---
ts: 2026-11-27T18:30:00Z
agent: bmad-agent-ux-designer (Sally)
session: claude-code
artefact:
  - _bmad-output/planning-artifacts/design/wireframes/16-draws-carousel.md (new)
  - mobile/lib/features/home/home_screen.dart
  - mobile/test/features/draws/draw_carousel_test.dart
  - mobile/test/design/goldens/draws-carousel.png (regenerated)
operation: reviewed + amended
inputs:
  - PR #20; tone-doc.md Anchor 1 and §Palette; wireframe 02; tokens.md
human_review:
  reviewer: S1408661 (Founder / EL)
  status: not-yet-reviewed
  comments: |
    §3 applied in this change. §4 are product decisions for the founder.
notes: |
  Design intent recorded for a surface that shipped before it was
  specified — no wireframe covered a carousel.

  THE RESERVATION WORTH KNOWING ABOUT. tone-doc Anchor 1 explicitly
  rejects "the busy comparison-shopping bar of alternative prizes" from
  BOTB, and a swipeable row of alternative prizes is structurally that
  pattern. Approved anyway, with the distinction written down: BOTB's bar
  sits ON the draw page, waving alternatives at someone mid-decision. This
  is a dedicated browse tab a user chose to open. The boundary is hard —
  this pattern must never appear on the draw detail page or in the entry
  flow. A future "related draws" block under the entry CTA is the BOTB bar
  and is out.

  CHANGES APPLIED (§3):
  - "3 draws open" removed. Quantity-as-signal is the register the tone
    doc rejects, and it was redundant: the dots say "three" and the
    Semantics labels say "of 3". Replaced with "Closing soonest first",
    which names the ORDERING — the one thing the dots cannot communicate,
    and which makes the close_time ordering legible without urgency copy.
  - `primary: i == _page` removed. On Home that bordered treatment means
    "the featured draw"; in the carousel it was being reused to mean "the
    page you are on" — one visual, two meanings, two screens. Position,
    cropped neighbours and the filled dot already say which page is
    active.

  §3.3 — CONSEQUENCE RECORDED RATHER THAN HIDDEN. Dropping `primary`
  shrinks the display face, so the card now fills about a third of the
  viewport and the rest is empty. I regenerated the golden and looked: it
  reads sparse, not restrained. Not reversing — a misleading token is the
  worse problem, and padding to fill space is not a reason to keep one —
  but it is real, visible today, and resolves when §4.1 lands.

  §4 RAISED FOR THE FOUNDER, not fixed:
  - 4.1 There is no prize photography anywhere. DrawSummary has no image
    field. tone-doc Anchor 1 says "prize photography dominates the fold".
    Text-only reads as restrained for ONE featured draw; in a carousel of
    three near-identical text cards it reads as a spreadsheet, which
    defeats the emotional job of the surface. This is now the largest gap
    between the tone doc and what ships. Needs prize_image_url, an
    operator upload flow and a hero card treatment — Winston + John.
  - 4.2 "closed" shown beside "TAP TO ENTER" (Amelia's finding, confirmed).
    Recommendation: show "closing now" during the window between
    close_time passing and the operator closing the draw, and keep the
    CTA. Saying "closed" while accepting entries is the worse of the two
    inconsistencies — a user who taps anyway and succeeds trusts us less.

  COMMENDED: the peek (viewportFraction 0.88) is what makes a carousel
  discoverable at all; the dots are real controls with 44pt targets rather
  than decoration, which most carousels get wrong and which locks out
  anyone who cannot drag horizontally; position is announced to screen
  readers; the single-draw state hides the chrome. Also: no auto-advance
  and no looping — both correct, and auto-advance would read as exactly
  the urgency the tone doc bans.

  VERIFICATION: 50/50 mobile, 268/268 backend, 5/5 admin; analyze and lint
  green. Golden regenerated and inspected after the changes.
---
```

---


### 2026-11-27 — Winston + John scope prize photography

```yaml
---
ts: 2026-11-27T19:30:00Z
agent: bmad-agent-architect (Winston) + bmad-agent-pm (John)
session: claude-code
artefact:
  - _bmad-output/planning-artifacts/prize-photography-scope.md (new)
operation: created
inputs:
  - design/wireframes/16-draws-carousel.md §4.1 and the spike evaluation
  - ADR-001 §Decision + §V0.5 amendment; ADR-005 §Alternatives; ADR-007 §Adapters
  - PRD §2; delivery-framework §Phase 0 (amended 2026-11-27)
human_review:
  reviewer: S1408661 (Founder / EL)
  status: not-yet-reviewed
  comments: |
    Four decisions in §5. Nothing proposed for build until they are made.
notes: |
  THE FINDING THAT REFRAMED IT. Atlas has already decided its object
  storage three times and provisioned it zero times. ADR-001 §Decision
  commits to "S3-compatible storage" as part of the managed-platform
  stack; ADR-007 §Adapters puts KYC document images in S3 "under strict
  access control"; ADR-005 §Alternatives names S3-with-object-lock for
  audit-log export. ADR-001's V0.5 amendment records why none exists:
  storage was stubbed because KYC was deferred.

  So prize photography is not a new storage decision. It is the THIRD
  caller for a facility already chosen and never stood up — and the first
  with a demonstrated product reason to stand it up. That argues for it,
  not against.

  THE DESIGN POINT WINSTON WOULD NOT WANT LOST. Prize images and KYC
  documents must not share a bucket or a policy. KYC: one operator, strict
  time-limited logged access, contains a face and an ID, NDPA retention
  rules. Prize images: every visitor, logged out, CDN-cacheable, no PII,
  delete when the draw archives. One policy gets one of them wrong, and
  the expensive direction is making KYC documents public. Two buckets from
  the first line of Terraform, not as a later refinement.

  THE URL COLUMN IS THE WRONG SHAPE TO SHIP. It trusts whatever is pasted:
  availability becomes a third party's, nothing validates content type,
  dimensions or size, and an operator pasting http:// is invisible to the
  app. Winston would accept it for INTERNAL DEMOS with Atlas-controlled
  assets, never in front of real users.

  JOHN'S SCOPE POSITION. PRD §2 does not mention prize imagery anywhere —
  not in scope, not in the draw-configuration bullet, not as a cut item.
  It was never considered, which is how a text-only card got built
  contradicting the tone doc. That makes this a PRD AMENDMENT, not a
  defect fix; "the tone doc implies it" is not authority to add scope. His
  position: yes to V1, close to table stakes for the category — but the
  real risk is the unowned row in the cost table. Somebody must photograph
  a Corolla for every draw, forever, and that recurring content obligation
  has not been costed.

  TIMING IS DOWNSTREAM OF THE LICENCE, indirectly. Object storage needs
  the managed-platform choice, deferred in the V0.5 demo-first pivot;
  ADR-001 puts that choice in Phase 0; Phase 0 is now gated on the State
  gaming licence. Not because photography is legally sensitive — because
  it needs infrastructure that needs a platform that needs Phase 0 to
  close.

  RECOMMENDATION: do it, but not yet and not in that order. Two things
  that cost nothing now — John raises the PRD amendment so the requirement
  is recorded rather than living in a wireframe footnote, and Tobi adds
  the two-bucket split to the platform-selection criteria so that decision
  is made once, correctly, whenever it is finally made. What NOT to do:
  ship the URL column to real users to get photography sooner.
---
```

---


## What's next

Post-V0.5 items tracked in `v0.5-close.md`:

- Monday founder walkthrough (all 16 flagship steps in mobile + admin, single sitting).
- Cold-start + fresh-clone timing on a second engineer's laptop.
- ~~Optional: Playwright automated recording of the operator flow.~~ Landed W8 Day 4 — `infrastructure/scripts/record_demo.py`.
- V1 hardening path: real KYC vendor, WhatsApp, reconciliation cron, multi-draw browsing, refund UX. ~~Encrypted server_seed at rest~~ closed W8 Day 1; the outbox is ~~scaffolded~~ but only the reveal producer is migrated — payment, ticket and wallet producers plus the CI grep gate are W9+ (ADR-002 §W8 execution amendment).
- ~~W9 candidate: sweep the suite for the flaky-test pattern found three times in W8.~~ Done W9 Day 4 — no new instances of that class. A **second** class surfaced instead: a test assuming it is the only consumer of shared state (`make test` racing the worker container, 20% failure). Both are worth watching for.
- W10 candidates, in the order they block things:
  - **Outbox consumers.** 13 producers are classified and deferred purely because nothing listens. Each consumer built unlocks its producer; `backend/tools/check_outbox_invariant.py` names the trigger for each.
  - **ADR-006 decrypt split** — owed from ⚖️ Adaeze since W8. The one genuinely security-relevant gap: encryption at rest protects a stolen dump, not a compromised API process.
  - **Identity remainder** — MFA and self-exclusion can proceed; the KYC adapter is gated on ADR-007 vendor selection, which has not landed.
  - **Stacked-PR CI.** `ci.yaml` triggers on `branches: [main]` only, so a stacked PR runs no checks at all.
  - **Seven dead admin sidebar links** — a 📋 John / 🎨 Sally product call, visible in `docs/VISUAL-WALKTHROUGH.md`.
  - **Pin the dev-tool floors** — unpinned `ruff`/`mypy` drift produced two W8 findings.

Every new session appends here per the AINE-AGENTS.md §7 discipline.
