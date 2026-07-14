# nf_atlas — Project Atlas

Premium prize-competition platform for Africa. Nigeria launch. Trust-first positioning.

**Status:** Week 3 (2026-07-13 → 07-17) — V0.5 investor demo scaffold in progress. Identity module lands this week.

---

## Quickstart (~15 min on a fresh clone)

**Prereqs:** Docker Desktop 4.x, Git, Node 20+ (for `corepack`), Flutter 3.24+ (for mobile), Python 3.13+ (only if you skip Docker).

```bash
git clone git@github.com:<org>/nf_atlas.git
cd nf_atlas
make setup     # copies .env.example → .env, installs admin deps
make dev       # docker compose up (postgres, redis, mailhog, backend, worker, admin)
```

Expected: cold-start `<60s` aspirational, `<90s` hard gate (per `_bmad-output/implementation-artifacts/week-3-build-plan.md §0.5`).

### Bootstrap the seeded operator (once per environment)

```bash
# 1. Set a real superadmin password in .env (>= 12 chars)
export ATLAS_SUPERADMIN_PASSWORD=$(openssl rand -base64 24)
make bootstrap    # seeds Adaobi Ibe with the superadmin role
```

Runbook: [`docs/runbooks/superadmin-bootstrap.md`](docs/runbooks/superadmin-bootstrap.md).

### Fresh-clone verification checklist (Week 3 gate, plan §6)

Run this on a second machine (borrowed laptop or Codespace) after `make dev` + `make bootstrap`:

- [ ] `curl localhost:8000/healthz` → `{"status":"ok",...}`
- [ ] Open http://localhost:8000/docs — Swagger renders 7 identity endpoints.
- [ ] Open http://localhost:3000 — redirects to /login (wf-08 renders).
- [ ] Sign in with the seeded superadmin credentials → land at /admin dashboard.
- [ ] Open the Flutter app on an iOS simulator (`cd mobile && flutter run`) — register → OTP (grab from http://localhost:8025 Mailhog) → password → welcome → home.
- [ ] `docker compose logs backend | grep 'user.registered'` — audit event visible.
- [ ] `SELECT count(*) FROM audit_log WHERE prev_hash != 'GENESIS'` — chain intact.
- [ ] Total wall-clock from `git clone` to green checklist: **< 15 min** (target), **< 20 min** (hard).

**Verify healthy stack:**

| URL                          | What it is                                     |
|------------------------------|------------------------------------------------|
| http://localhost:8000/healthz | Backend health probe → `{"status":"ok",...}` |
| http://localhost:8000/docs    | FastAPI Swagger UI (dev only)                 |
| http://localhost:3000         | Admin (Next.js) — Day 1 shell                 |
| http://localhost:8025         | Mailhog inbox (OTP delivery target for V0.5)  |

**Common commands:**

```bash
make test          # backend pytest + admin vitest
make lint          # ruff + eslint + flutter analyze
make typecheck     # mypy + tsc
make demo-reset    # wipe DB volume and re-run migrations (< 30s target)
make clean         # stop stack, remove volumes and build caches
```

---

## Read first

### Planning
- **PRD (V1 scope):** [`_bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md`](_bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md)
- **Delivery framework (26-week phased plan):** [`_bmad-output/planning-artifacts/delivery-framework.md`](_bmad-output/planning-artifacts/delivery-framework.md)
- **V0.5 demo plan (investor demo focus):** [`_bmad-output/planning-artifacts/v0.5-demo-plan.md`](_bmad-output/planning-artifacts/v0.5-demo-plan.md)
- **Week 3 build plan (current):** [`_bmad-output/implementation-artifacts/week-3-build-plan.md`](_bmad-output/implementation-artifacts/week-3-build-plan.md)

### Design system
- **Tone doc:** [`_bmad-output/planning-artifacts/design/tone-doc.md`](_bmad-output/planning-artifacts/design/tone-doc.md)
- **Tokens (colour, type, space, radius, elevation):** [`_bmad-output/planning-artifacts/design/tokens.md`](_bmad-output/planning-artifacts/design/tokens.md)
- **Components (15 primitives + compositions):** [`_bmad-output/planning-artifacts/design/components.md`](_bmad-output/planning-artifacts/design/components.md)
- **Wireframes (15 screens):** [`_bmad-output/planning-artifacts/design/wireframes/`](_bmad-output/planning-artifacts/design/wireframes/)

### Governance
- **Agent operating model:** [`docs/AINE-AGENTS.md`](docs/AINE-AGENTS.md)
- **Risk register:** [`docs/risk-register.md`](docs/risk-register.md)
- **Architectural decisions (12 ADRs, Approved 2026-07-02):** [`docs/adr/`](docs/adr/)
- **Runbooks:** [`docs/runbooks/`](docs/runbooks/)
- **Compliance reviews:** [`docs/compliance/`](docs/compliance/)
- **Counsel engagement brief:** [`_bmad-output/planning-artifacts/legal/counsel-engagement-brief.md`](_bmad-output/planning-artifacts/legal/counsel-engagement-brief.md)

---

## Layout

```
nf_atlas/
├── backend/                 FastAPI + SQLAlchemy 2 async + Alembic (Python 3.13)
│   ├── pyproject.toml       hatch build; src-layout; strict ruff/mypy
│   └── src/atlas/           8 modules — audit_log, identity, wallet, payment,
│                            ticket, draw, admin, idempotency (ADR-001)
├── mobile/                  Flutter 3 + Riverpod (consumer app)
│   └── lib/design/tokens/   colours / typography / spacing / radii / elevation
├── admin/                   Next.js 14 App Router + Tailwind + pnpm (operator)
│   ├── tailwind.config.ts   Atlas tokens as theme.extend
│   └── src/design/tokens.css CSS custom-prop escape hatch
├── docker-compose.yaml      5 services: postgres, redis, mailhog, backend, worker, admin
├── Makefile                 setup / dev / test / lint / typecheck / demo-reset / clean
├── .github/workflows/ci.yaml lint + typecheck + tests + module-boundary invariants
├── docs/                    ADRs, runbooks, compliance, agent operating model
└── _bmad-output/            planning + implementation artefacts (BMad convention)
```

---

## AI agents

This project is BMad-driven ([BMad Method](https://docs.bmad-method.org/)). Standing roster in [`_bmad/config.toml`](_bmad/config.toml):

| Icon | Name | Role | Skill |
|---|---|---|---|
| 📊 | Mary | Business Analyst | `bmad-agent-analyst` |
| 📚 | Paige | Technical Writer | `bmad-agent-tech-writer` |
| 📋 | John | Product Manager | `bmad-agent-pm` |
| 🎨 | Sally | UX Designer | `bmad-agent-ux-designer` |
| 🏗️ | Winston | System Architect | `bmad-agent-architect` |
| 💻 | Amelia | Senior Software Engineer | `bmad-agent-dev` |
| 🧪 | Murat | Master Test Architect | `bmad-tea` |

Atlas custom agents in [`_bmad/custom/config.toml`](_bmad/custom/config.toml):

| Icon | Name | Role |
|---|---|---|
| 🛡️ | Tobi | DevSecOps Engineer |
| ⚖️ | Adaeze | Compliance & Risk Officer |

Invoke via BMad skills or adopt persona in-context per [`docs/AINE-AGENTS.md`](docs/AINE-AGENTS.md).

---

## Legal model

Atlas operates as a **prize competition**, not a lottery. Every draw offers a free entry route with identical odds and requires a skill question on every paid entry. Marketing copy bans "lottery," "raffle," "luck." See PRD §1 and [`_bmad-output/planning-artifacts/legal/counsel-engagement-brief.md`](_bmad-output/planning-artifacts/legal/counsel-engagement-brief.md) for the legal opinion currently being commissioned to confirm the model under Nigerian law.

---

## Contributing

Human-approval gates and agent operating rules in [`docs/AINE-AGENTS.md §6`](docs/AINE-AGENTS.md). Do not merge to `main` without EL approval on any ADR-affecting change.
