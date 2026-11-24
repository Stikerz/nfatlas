# CLAUDE.md — instructions for AI coding assistants on nf_atlas

Loaded into every Claude Code (and compatible AI-assistant) session on this repo. Keep terse — repo-wide, durable rules only. Per-user state belongs in per-user memory, not here.

## Project one-liner

**Project Atlas** — premium prize-competition platform for Africa, Nigeria first. Trust-first positioning. Modular monolith (FastAPI + Postgres + Redis + Flutter + Next.js) with commit-reveal draws + public entropy. Full context: [`README.md`](README.md), [`docs/AINE-AGENTS.md`](docs/AINE-AGENTS.md).

## This is a BMad agent project

- Use BMad skills for standard roles: `bmad-agent-pm` (John), `bmad-agent-architect` (Winston), `bmad-agent-dev` (Amelia), `bmad-agent-analyst` (Mary), `bmad-agent-tech-writer` (Paige), `bmad-agent-ux-designer` (Sally), `bmad-tea` (Murat).
- Two Atlas-specific complements for roles BMad doesn't ship: `atlas-devsecops` (Tobi), `atlas-compliance-risk` (Adaeze). Descriptors in `_bmad/custom/config.toml`; operating model in `docs/AINE-AGENTS.md`.
- Do **not** create custom subagents under `.claude/agents/`. BMad already covers the ceremony; a prior custom system was rolled back on 2026-06-29.
- Artefact layout is fixed:
  - Planning → `_bmad-output/planning-artifacts/`
  - Implementation (build plans, close-outs) → `_bmad-output/implementation-artifacts/`
  - Test → `_bmad-output/test-artifacts/`
  - Durable knowledge (ADRs, runbooks, compliance) → `docs/`

## Where the current work lives

- `_bmad-output/implementation-artifacts/week-N-build-plan.md` is the source of truth for the active sprint. Read the latest before starting anything.
- `docs/AI-INTEGRATION-LOG.md` — log of AI-generated changes per `docs/AINE-AGENTS.md §7`. Append an entry at the close of every substantive session.
- `docs/adr/ADR-NNN-*.md` — architecture decisions. Cite by number when touching a covered area; changes to a covered area follow the amendment process in `_bmad-output/planning-artifacts/delivery-framework.md §12 (Change process for versioned artefacts)`.
- Compliance-sensitive modules (Wallet & Ledger, Payment, Ticket, Draw Engine) require Adaeze as a reviewer per `docs/AINE-AGENTS.md §6 (Human-in-the-loop gates)`.

## Commit conventions

- **No `Co-Authored-By: Claude ...` trailers on git commits.** Founder rejected them on 2026-07-02. Applies to `git commit` message bodies only — the separate "🤖 Generated with Claude Code" footer on PR *descriptions* (from the default Claude Code system prompt) is untouched by this rule unless the founder later says otherwise.
- Subject style matches recent `git log`: `type(scope): W<week> Day <n> — <summary>` for build-plan work; `type(scope): <summary>` otherwise.
- Do not skip hooks (`--no-verify`) — diagnose the failure instead.

## Python style

- Backend is Python 3.13, strict mypy, ruff-clean. Tests follow red-green-refactor.
- On Python-only decisions (packaging, layout, typing, imports), present BOTH the "shorter/easier" and the "PEP/community-idiomatic" option — founder prefers idiomatic. The `backend/src/atlas/*` src-layout landed on exactly this signal on 2026-07-13.
- **Settled decisions — do not re-litigate:** Riverpod for mobile state, `pnpm` for admin, 8-hour session TTL, 90-second cold-start hard gate. All accepted in W3 planning.
- **Path drift caveat.** ADR-001 and ADR-012 still reference `backend/api/*` even though the actual layout is `backend/src/atlas/*` (drift noted in commit `0f2a97c`). Do NOT retroactively rewrite the ADRs to match the code — an ADR amendment through Winston (`bmad-agent-architect`) is required first.

## Local-env caveats

- **`make test` can report a false green — rebuild first.** The `backend` service bakes source into the image at build time and mounts no source volume (`docker-compose.yaml` mounts only `./infrastructure`). `make test` runs `docker compose run backend pytest` without building, so an image older than your working tree silently tests *stale code*. This bit a session on 2026-11-23: a deleted route still passed. Run `docker compose build backend worker` before `make test`, or run natively from `backend/.venv` against the `atlas_test` database.
- ~~Zscaler / corporate-proxy SSL failures inside docker builds~~ — resolved 2026-11-23, confirmed by a clean `docker compose build backend worker`. Docker builds work locally again; the native-run workaround is no longer required (still fine as a faster inner loop).

## Fresh-laptop setup (concurrent work)

1. `git clone` + `make setup` per [`README.md`](README.md#quickstart-15-min-on-a-fresh-clone).
2. Install BMad on your Claude Code:
   ```
   npx bmad-method install
   ```
   Versions pinned in `_bmad/_config/manifest.yaml` (bmm 6.9.0, tea v1.19.0 at time of writing).
3. Copy `.env.example` → `.env`, fill secrets.
4. Personal BMad overrides go in `_bmad/custom/config.user.toml` (gitignored); team-wide overrides in `_bmad/custom/config.toml` (committed).
