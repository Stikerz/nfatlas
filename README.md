# nf_atlas — Project Atlas

Premium prize-competition platform for Africa. Nigeria launch. Trust-first positioning.

**Status:** Phase 0 — planning, legal engagement, vendor selection. No implementation code yet.

---

## Read first

- **PRD (V1 scope):** [`_bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md`](_bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md)
- **Delivery framework (26-week phased plan):** [`_bmad-output/planning-artifacts/delivery-framework.md`](_bmad-output/planning-artifacts/delivery-framework.md)
- **Agent operating model:** [`docs/AINE-AGENTS.md`](docs/AINE-AGENTS.md)
- **Risk register:** [`docs/risk-register.md`](docs/risk-register.md)
- **Architectural decisions (12 ADRs, Proposed):** [`docs/adr/`](docs/adr/)
- **Runbooks (6 priority):** [`docs/runbooks/`](docs/runbooks/)
- **Counsel engagement brief:** [`_bmad-output/planning-artifacts/legal/counsel-engagement-brief.md`](_bmad-output/planning-artifacts/legal/counsel-engagement-brief.md)

## AI agents

This project is BMad-driven ([BMad Method](https://docs.bmad-method.org/)). Standing roster defined in [`_bmad/config.toml`](_bmad/config.toml):

| Icon | Name | Role | Skill |
|---|---|---|---|
| 📊 | Mary | Business Analyst | `bmad-agent-analyst` |
| 📚 | Paige | Technical Writer | `bmad-agent-tech-writer` |
| 📋 | John | Product Manager | `bmad-agent-pm` |
| 🎨 | Sally | UX Designer | `bmad-agent-ux-designer` |
| 🏗️ | Winston | System Architect | `bmad-agent-architect` |
| 💻 | Amelia | Senior Software Engineer | `bmad-agent-dev` |
| 🧪 | Murat | Master Test Architect & Quality Advisor | `bmad-tea` |

Atlas custom agents in [`_bmad/custom/config.toml`](_bmad/custom/config.toml):

| Icon | Name | Role |
|---|---|---|
| 🛡️ | Tobi | DevSecOps Engineer |
| ⚖️ | Adaeze | Compliance & Risk Officer |

Invoke via BMad skills (`bmad-agent-pm`, `bmad-tea`, etc.) or adopt persona in-context per [`docs/AINE-AGENTS.md`](docs/AINE-AGENTS.md).

## Legal model

Atlas operates as a **prize competition**, not a lottery. Every draw offers a free entry route with identical odds and requires a skill question on every paid entry. Marketing copy bans "lottery," "raffle," "luck." See PRD §1 and [`_bmad-output/planning-artifacts/legal/counsel-engagement-brief.md`](_bmad-output/planning-artifacts/legal/counsel-engagement-brief.md) for the legal opinion currently being commissioned to confirm the model under Nigerian law.

## Setup

Phase 0 planning — no local runtime yet. When Phase 2 (platform build) begins, this section will document one-command developer setup.

## Contributing

Human-approval gates and agent operating rules in [`docs/AINE-AGENTS.md §6`](docs/AINE-AGENTS.md). Do not merge to `main` without EL approval on any ADR-affecting change.
