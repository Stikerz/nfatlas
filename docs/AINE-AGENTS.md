# AINE — Atlas AI Engineering Agent Operating Model

**Status:** Draft, 2026-06-29 (revised to reflect BMad install)
**Scope:** V1 (Nigeria launch).
**Pairs with:** `_bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md`, `_bmad-output/planning-artifacts/delivery-framework.md`, `_bmad/config.toml`, `_bmad/custom/config.toml`.

---

## 1. Substrate: BMad + 2 Atlas complements

Atlas is a **BMad agent project**. The standing agent roster, the workflow ceremony, and the planning-artefact directory structure all follow the BMad Method (`bmm`) and Test Engineering Agent (`tea`) modules installed in `_bmad/`.

This document does **not** redefine those agents — `_bmad/config.toml` is the authoritative definition. This document does two things:

1. Names the V1 roster (which BMad agents are active + the 2 Atlas-specific complements).
2. Adds Atlas-specific operating conventions that BMad doesn't cover: arbitration precedence, human-approval gates, the AI Integration Log, and per-module ownership.

### What we previously built and what changed

A prior version of this document (and 7 `.claude/agents/*.md` files) defined a custom agent system from scratch — that was the wrong call. BMad already provides 7 agent personas with named voices, descriptors, and skill-bound invocation. The custom files have been removed; the 7 BMad personas plus 2 Atlas custom descriptors registered in `_bmad/custom/config.toml` are the V1 roster.

---

## 2. V1 roster (9 agents)

### BMad personas (7) — from `_bmad/config.toml`

| Icon | Name | Skill | Standing role in Atlas |
|---|---|---|---|
| 📊 | **Mary** | `bmad-agent-analyst` | Phase 0 market and domain research; competitor analysis; risk-register entries with strategic framing. |
| 📚 | **Paige** | `bmad-agent-tech-writer` | Documentation across all phases — API docs, runbooks, the AI Integration Log, public-facing transparency pages. |
| 📋 | **John** | `bmad-agent-pm` | Product scope, PRD ownership, story creation, backlog ordering, KPI tracking. |
| 🎨 | **Sally** | `bmad-agent-ux-designer` | Consumer mobile (Flutter) flows; admin UX; accessibility-first design. |
| 🏗️ | **Winston** | `bmad-agent-architect` | Module boundaries, ADRs, OpenAPI contract, event catalogue, schema. |
| 💻 | **Amelia** | `bmad-agent-dev` | FastAPI backend + Flutter mobile + Next.js admin implementation; tests; migrations. |
| 🧪 | **Murat** | `bmad-tea` | Risk-based test strategy, Playwright/k6/contract testing, NFR audits, traceability matrices. |

### Atlas custom agents (2) — registered in `_bmad/custom/config.toml`

| Icon | Name | Identifier | Standing role in Atlas |
|---|---|---|---|
| 🛡️ | **Tobi** | `atlas-devsecops` | Docker, CI/CD, managed-platform configuration, observability baseline, secret management, security tooling, runbooks, production deploy. |
| ⚖️ | **Adaeze** | `atlas-compliance-risk` | Prize-competition mechanics correctness, KYC integration, ledger correctness, audit-log integrity, regulatory copy review, skill-question rotation, fraud controls. |

**Why these two are custom:** BMad doesn't ship DevSecOps or domain-compliance personas, and both are first-class for a Nigerian prize-competition platform. Murat (TEA) covers test quality; Tobi covers infrastructure and security tooling; Adaeze owns regulatory and financial-integrity correctness.

**Why named (Tobi, Adaeze):** matches BMad's convention of named personas with voice. Both names are commonly used Nigerian names — appropriate for a Nigeria-launching platform.

### BMad workflow skills available

Beyond the agent personas, the install provides workflow skills used throughout the phased plan. Non-exhaustive: `bmad-prd`, `bmad-architecture`, `bmad-create-story`, `bmad-create-epics-and-stories`, `bmad-dev-story`, `bmad-code-review`, `bmad-checkpoint-preview`, `bmad-sprint-planning`, `bmad-sprint-status`, `bmad-retrospective`, `bmad-shard-doc`, `bmad-investigate`, `bmad-correct-course`, `bmad-domain-research`, `bmad-market-research`, `bmad-technical-research`, `bmad-product-brief`, `bmad-testarch-test-design`, `bmad-testarch-atdd`, `bmad-testarch-automate`, `bmad-testarch-ci`, `bmad-testarch-nfr`, `bmad-testarch-test-review`, `bmad-testarch-trace`, `bmad-qa-generate-e2e-tests`, `bmad-party-mode` (multi-agent roundtable).

See `_bmad/_config/skill-manifest.csv` for the complete list.

---

## 3. Module ownership

Each V1 module has a **primary agent**, mandatory **reviewers**, and a **human approver**. Mirrors `PRD.md §4` Module ownership table; reproduced here so this doc is self-contained.

| Module | Primary | Reviewers | Human approver(s) |
|---|---|---|---|
| Identity | 💻 Amelia | 🏗️ Winston; ⚖️ Adaeze (KYC, self-exclusion, age gate) | Engineering Lead |
| Wallet & Ledger | 💻 Amelia | 🏗️ Winston; ⚖️ Adaeze; 🧪 Murat | Engineering Lead + Finance Lead |
| Payment | 💻 Amelia | 🏗️ Winston; ⚖️ Adaeze; 🧪 Murat | Engineering Lead + Finance Lead |
| Ticket | 💻 Amelia | 🏗️ Winston; ⚖️ Adaeze (skill-question + free-entry route); 🧪 Murat | Engineering Lead |
| Draw Engine | 💻 Amelia | 🏗️ Winston; ⚖️ Adaeze; 🧪 Murat | Engineering Lead + Compliance Lead |
| Admin | 💻 Amelia + 🎨 Sally | 🏗️ Winston; 🧪 Murat; ⚖️ Adaeze on money/draw operator actions | Engineering Lead |

Cross-cutting agents (not module-specific):
- 📋 **John** — backlog, scope, KPIs across all modules.
- 📊 **Mary** — Phase 0 research; risk-register entries throughout.
- 📚 **Paige** — docs across all modules.
- 🛡️ **Tobi** — CI/CD, infra, observability, security across all modules.

---

## 4. Artefact registry

Atlas extends BMad's artefact conventions with a couple of Atlas-specific paths. The registry is the only authorised handoff mechanism — agents communicate by producing artefacts at known paths, not by direct calls.

| Artefact | Path | Producer | Consumers |
|---|---|---|---|
| Project brief | `_bmad-output/planning-artifacts/briefs/` | 📊 Mary (Phase 0) | All |
| PRD | `_bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md` | 📋 John | All |
| Delivery framework | `_bmad-output/planning-artifacts/delivery-framework.md` | 📋 John + 🏗️ Winston | All |
| Architecture | `_bmad-output/planning-artifacts/architecture.md` | 🏗️ Winston | All |
| Epics | `_bmad-output/planning-artifacts/epics.md` | 📋 John + 🏗️ Winston | 💻 Amelia, 🧪 Murat |
| Stories | `_bmad-output/planning-artifacts/stories/STORY-*.md` | 📋 John (initial) → 🏗️ Winston (technical context) → owner | Implementing agent, 🧪 Murat, ⚖️ Adaeze (if money/draws) |
| ADRs | `docs/adr/ADR-NNN-<slug>.md` | 🏗️ Winston | All |
| OpenAPI spec | `packages/shared/openapi.yaml` | 🏗️ Winston (proposes) → 💻 Amelia (maintains) | 💻 Amelia, 🧪 Murat |
| Event catalogue | `docs/events.md` | 🏗️ Winston | 💻 Amelia, 🧪 Murat, ⚖️ Adaeze |
| Domain model | `docs/domain-model.md` | 🏗️ Winston | All |
| ERD | `docs/erd.md` | 🏗️ Winston | 💻 Amelia, ⚖️ Adaeze |
| Test strategy | `_bmad-output/test-artifacts/test-design/` | 🧪 Murat | All |
| Test reviews | `_bmad-output/test-artifacts/test-reviews/` | 🧪 Murat | 💻 Amelia |
| Traceability matrix | `_bmad-output/test-artifacts/traceability/` | 🧪 Murat | All |
| E2E specs | `e2e/**` | 🧪 Murat | CI |
| Runbooks | `docs/runbooks/<scenario>.md` | 🛡️ Tobi | On-call humans |
| Compliance reviews | `docs/compliance/reviews/REVIEW-NNN.md` | ⚖️ Adaeze | PR author, human approver |
| Regulatory copy | `docs/compliance/copy/**` | ⚖️ Adaeze (drafts) → Legal Counsel (approves) → 🎨 Sally / 💻 Amelia (consumes) | Frontend |
| Skill-question content | `docs/compliance/skill-questions.md` | ⚖️ Adaeze + Legal Counsel | 💻 Amelia |
| Risk register | `docs/risk-register.md` | 📊 Mary (Phase 0) + ⚖️ Adaeze (ongoing) | All |
| AI Integration Log | `docs/AI-INTEGRATION-LOG.md` | All (append-only) | Humans, retro |

BMad's `bmm` module maps `_bmad-output/planning-artifacts/` for planning outputs, `_bmad-output/implementation-artifacts/` for build outputs, and `docs/` for project knowledge — see `_bmad/config.toml`. The TEA module maps `_bmad-output/test-artifacts/`.

---

## 5. Arbitration

Atlas-specific (BMad doesn't define inter-agent arbitration).

### Tier 1 — automatic resolution by precedence

1. ⚖️ **Adaeze (Compliance & Risk)** wins on money, draws, audit, KYC, regulatory copy.
2. 🏗️ **Winston (Architect)** wins on module boundaries, API/event contracts, schema.
3. 📋 **John (PM)** wins on scope and acceptance criteria.
4. 🧪 **Murat (TEA)** wins on what counts as tested.
5. 🛡️ **Tobi (DevSecOps)** wins on production deploy, secret handling, CI gates.

### Tier 2 — human arbitration

Cross-domain disagreement escalates to the **Engineering Lead (human)** with: short statement, each agent's position, recommended decision.

### Tier 3 — founder arbitration

Reserved for irreversible/expensive calls: legal model, KYC vendor switch mid-build, prize category additions (e.g. property), launch date. EL escalates.

---

## 6. Human-in-the-loop gates

Anything not listed here, an agent can do alone.

| Gate | Approver | Recorded in |
|---|---|---|
| **ADR sign-off** — any new/amended ADR before it becomes immutable | Engineering Lead | ADR file footer |
| **Schema migration** — before it runs against staging | Engineering Lead | PR review |
| **Wallet & Ledger merge** | Engineering Lead + Finance Lead | PR review (two approvals) |
| **Payment module merge** | Engineering Lead + Finance Lead | PR review (two approvals) |
| **Draw Engine merge** | Engineering Lead + Compliance Lead | PR review (two approvals) |
| **Production deploy** affecting real money / KYC / live draw | Engineering Lead | Deploy log + PR link |
| **KYC vendor selection** (Phase 0) | Founder + Legal | Procurement contract + ADR |
| **Payment provider contract** | Founder + Finance Lead | Procurement contract |
| **Prize fulfilment payout > ₦5M** | Founder + Finance Lead | Prize ledger + signed authorisation |
| **Phase gate advancement** | Engineering Lead | Phase exit report |
| **Regulatory copy** | ⚖️ Adaeze → Legal Counsel | `docs/compliance/copy/` |
| **Skill-question content** | ⚖️ Adaeze → Legal Counsel | `docs/compliance/skill-questions.md` |
| **Live real-money draw execution** (commit / close / reveal) | Draw Admin (named RBAC) | Audit log + UI capture |

### What requires NO permission

- Refactor within an existing module without changing public interface or schema.
- Add tests.
- Update docs that don't change committed contracts.
- Generate drafts (anything in `draft` status — transitions to `ready`/`approved` are gated).
- Anything in `docs/exploration/` (working notes, not artefacts of record).

---

## 7. AI Integration Log

Single append-only file at `docs/AI-INTEGRATION-LOG.md`. Pattern lifted from `nearform-tdapp/docs/AI-INTEGRATION-LOG.md`.

### Entry shape

```markdown
---
ts: 2026-06-29T14:32:11Z
agent: solution-architect            # the BMad agent or atlas-* identifier
session: <claude-code-session-id or "manual">
artefact: docs/adr/ADR-007-...md
operation: created | amended | reviewed
inputs:
  - _bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md §4
  - docs/events.md
human_review:
  reviewer: <name>
  status: approved | requested-changes | not-yet-reviewed
  comments: <free text or link>
notes: <one-line summary of what the agent did and why>
---
```

### When to append

- Any time an agent produces or modifies a registry artefact (§4).
- Any time an invocation crosses a gate (§6).
- Any time arbitration (§5) fires.

### When NOT to append

- Trivial code edits within a single PR (the PR history is the record).
- Exploration / drafting that doesn't land an artefact.
- Within-session iterations on the same artefact — log the final state.

### Retention

Append-only for the life of the project. Rotated annually into `docs/AI-INTEGRATION-LOG-YYYY.md` archives.

---

## 8. Validation: what stops an agent from being wrong

1. **Schema-bound outputs.** Story files, ADRs, runbooks, AI log entries all have required sections (§7). A CI lint rejects PRs that violate shape.
2. **Cross-agent review.** Every artefact has a reviewer (§3). Reviewer runs as a separate invocation, refute-by-default.
3. **Human gates** (§6) on everything irreversible or money-related.
4. **Adversarial verification.** Draw Engine, ledger, payment, KYC code each gets a second independent invocation tasked specifically with finding bugs/regressions before human review.
5. **Grep invariants** from `PRD.md §4`: no cross-module direct DB access; every state change emits an outbox event. Hard-fail in CI.
6. **No mocks** for ledger or draw paths in tests — real Postgres test DB with per-test truncation. Pattern from `nearform-tdapp`.

---

## 9. What is NOT in this V1 operating model

- ❌ Automated agent-to-agent message bus.
- ❌ Multi-agent voting / consensus beyond §5's fixed precedence.
- ❌ Long-running autonomous agents (each invocation is bounded; produces a discrete artefact).
- ❌ Agents that deploy to production unattended.
- ❌ Agents that call external paid APIs without a human-approved budget cap.
- ❌ Re-invoking the 5 removed roles from the long-form PRD (Web standalone, Growth & CRM, AI & Personalisation, Data & Analytics, Tech Writer standalone — the BMad install brings Paige back into the V1 roster).
- ❌ MCP server integration in V1 (deferred — see delivery framework §11 trigger).
- ❌ Custom `.claude/agents/*.md` files (BMad is the agent substrate).

Each becomes a V2 candidate when a concrete pain point triggers it.

---

## 10. Open questions

1. Engineering Lead role: one named human or rotated? V1 default — one named human.
2. AI Integration Log review cadence: proposed weekly retro reads past week's entries; flagged items become backlog actions.
3. Cost ceiling per agent invocation: defer numeric ceiling until Phase 0 data; agents flag if projected above £X.
4. Whether `atlas-devsecops` and `atlas-compliance-risk` need full BMad-style `SKILL.md` files (we currently register descriptors only in `_bmad/custom/config.toml`) — defer until the descriptor-only approach is shown insufficient.

---

## 11. Cross-references

- **`_bmad/config.toml`** — installer-managed agent definitions (read-only).
- **`_bmad/custom/config.toml`** — team customisations including the 2 Atlas custom agents.
- **`_bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md`** — V1 product scope.
- **`_bmad-output/planning-artifacts/delivery-framework.md`** — 26-week phased plan.
- **`docs/adr/`** — V1 architectural decisions (ADR-001 through ADR-012).
- **`/Users/S1408661/Projects/nearform-tdapp/`** — BMad sibling project; convention and workflow precedent.
