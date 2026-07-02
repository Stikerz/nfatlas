# Project Atlas — V1 Delivery Framework

**Status:** Draft, 2026-06-29
**Scope:** V1 (Nigeria launch). V2+ ambitions captured in §11.
**Supersedes:** the long-form delivery framework for V1 execution.
**Pairs with:** `PRD.md` (what), `AINE-AGENTS.md` (who).

---

## 1. Method

Atlas is built using **Specification-Driven Development (SDD)** powered by **BMAD** ceremony (Business, Modelling, Architecture, Delivery) and executed by **AINE agents** (`AINE-AGENTS.md`).

Each phase produces **versioned** artefacts. Downstream work consumes them as ground truth. The "immutable phase output" language from the original framework is softened to **versioned**: an artefact is the source of truth at any given moment, but learnings during build can flow back through an explicit change process (§9), not by ad-hoc edits.

V1 is a **modular monolith** with **6 business modules** delivered in a **26-week** schedule across **7 phases** (numbered 0–6 to match the original framework). The full 14-module ambition is preserved in §11 as a V2+ annex.

---

## 2. Phase summary (26 weeks)

| Phase | Name | Weeks | Wall-clock | Primary AINE owners | Gate to advance |
|---|---|---|---|---|---|
| 0 | Foundations & legal | 0–4 | 4 wks | PM, Compliance & Risk, DevSecOps | NLRC legal opinion + vendors contracted + infra baseline |
| 1 | Specification | 4–6 | 2 wks | PM, Solution Architect, QA | ADRs approved, stories generated for Phase 2 modules, test strategy signed off |
| 2 | Platform | 6–9 | 3 wks | DevSecOps, Backend, Frontend | One-command dev env, CI green, baseline observability, RBAC scaffolding |
| 3 | Module build (closed beta) | 9–17 | 8 wks | Backend, Frontend, QA, Compliance | All 6 modules functional, one real-money beta draw completed end-to-end |
| 4 | Quality engineering | 17–21 | 4 wks | QA, DevSecOps, Compliance | Coverage gates met, perf gates met, security review clean, accessibility AA |
| 5 | Containerisation & deploy | 21–23 | 2 wks | DevSecOps, Backend | Production environment live, blue-green deploy proven, rollback tested |
| 6 | Production readiness & launch | 23–26 | 3 wks | All agents + humans | Sign-off checklist complete, flagship vehicle-prize draw live |

Phases 3 and 4 overlap in practice (QA writes E2E in parallel with module build), but the **gate** for advancing from 3 to 4 is module completeness, not test completeness.

---

## 3. Phase 0 — Foundations & legal (weeks 0–4)

Nothing about the build can be planned reliably until five things are settled. Phase 0 is "do those five things."

### Activities

1. **Legal opinion on the prize-competition model in Nigeria** — Compliance & Risk Agent commissions, Founder + Legal Counsel approve. Written opinion from Nigerian gambling/promotions counsel covering: (a) does the model require an NLRC licence/permit, (b) free-entry route requirements under Nigerian law, (c) skill-question requirements under Nigerian law, (d) restrictions on marketing language. **Hard prerequisite for Phase 1 to start.**
2. **Vendor selection.** Compliance & Risk Agent shortlists, Founder approves: KYC vendor (Smile / Dojah / Prembly), Paystack merchant onboarding, WhatsApp Business API provider, managed-platform host (Fly / Railway / Render / AWS App Runner), Sentry, S3-compatible object storage.
3. **Infrastructure baseline.** DevSecOps Agent provisions: GitHub org + repo, managed-platform account, Postgres (dev + staging), Redis, S3 bucket, secrets management, DNS, one-command local dev (Docker Compose), GitHub Actions baseline CI (lint + build).
4. **Free-entry route operationalised.** Compliance & Risk Agent designs the workflow: P.O. box leased, entry slip template, transcription procedure, throughput target for V1 launch volumes.
5. **Schema kickoff.** Solution Architect Agent drafts initial ADRs for: outbox vs Redis Streams (decision: outbox in V1), monolith deployment topology, secret management, observability stack, audit log strategy.

### Deliverables

- `docs/compliance/legal-opinion-nlrc.md` — written summary + scanned PDF reference (PDF not in repo).
- `docs/compliance/vendor-decisions.md` — shortlist comparison + decision rationale per vendor.
- `docs/risk-register.md` — risks identified during Phase 0 with owner + mitigation per risk.
- `docs/adr/ADR-001..00N-*.md` — kickoff ADRs (see Phase 1 for full ADR set).
- `docs/runbooks/local-dev.md` — one-command dev setup.
- Working CI on `main` running lint + build on every push.

### Phase 0 exit criteria

- ✅ Legal opinion received and risk-accepted (or model adjusted) by Founder.
- ✅ All vendors contracted; sandbox/test credentials in DevSecOps's secret manager.
- ✅ `git clone && make dev` (or equivalent) starts a working local stack.
- ✅ CI passes on `main`.
- ✅ Risk register reviewed by EL + Founder.

---

## 4. Phase 1 — Specification (weeks 4–6)

Two weeks where engineering agents specify everything Phase 2 and Phase 3 will implement. No code that isn't scaffolding.

### Activities

#### PM Agent
- Convert `PRD.md` into an epic catalogue: 6 modules → ~6 epics → ~40 stories (rough estimate).
- Each story in `docs/stories/STORY-*.md` per the shape in `AINE-AGENTS.md §4.1`.
- Backlog ordered by dependency (Identity → Wallet/Ledger → Payment → Ticket → Draw Engine → Admin runs in parallel from Phase 2 onwards).
- KPI targets committed to numbers (replace TODOs in `PRD.md §5`) — Founder input required.

#### Solution Architect Agent
- ADR set for V1 (target ~12):
  - ADR-001 Modular monolith deployment topology
  - ADR-002 Outbox pattern (vs Redis Streams) for V1
  - ADR-003 Double-entry ledger schema and chart of accounts
  - ADR-004 Idempotency strategy (client-supplied keys, request hash table)
  - ADR-005 Audit log: hash-chained append-only table
  - ADR-006 Commit-reveal protocol and public entropy source choice
  - ADR-007 KYC vendor adapter abstraction
  - ADR-008 Payment vendor adapter abstraction (Paystack-first, Flutterwave/Moniepoint shapes preserved)
  - ADR-009 RBAC model and permission grants
  - ADR-010 Self-exclusion enforcement (BVN-based block)
  - ADR-011 Observability baseline (Sentry + platform logs in V1)
  - ADR-012 Secret management approach
- Domain model in `docs/domain-model.md` (Mermaid).
- ERD in `docs/erd.md` (Mermaid).
- OpenAPI 3.1 spec scaffolded in `packages/shared/openapi.yaml` — paths defined per module, schemas deferred to Phase 3.
- Event catalogue in `docs/events.md` listing V1 events: `UserRegistered`, `KYCApproved`, `PaymentSucceeded`, `WalletCredited`, `TicketIssued`, `FreeEntryTranscribed`, `DrawCommitted`, `DrawClosed`, `DrawRevealed`, `WinnerSelected`, `PrizeClaimed`, `RefundIssued`.

#### QA Agent
- Test strategy in `docs/qa/strategy.md`:
  - Per-module coverage targets (domain ≥ 90%, overall ≥ 80% meaningful).
  - Integration tests against real Postgres (no mocks for ledger or draws — invariant from `AINE-AGENTS.md §9`).
  - Contract tests driven by OpenAPI.
  - E2E with Playwright Chromium against the running stack.
  - Performance gates (target table in §8).
- E2E spec skeletons for the V1 critical journeys (§5.3).

#### DevSecOps Agent
- Repository layout finalised (§6).
- Branching strategy: trunk + short-lived feature branches; PRs squash-merge.
- Definition of Done in `docs/definition-of-done.md` (mirrors the checklist in `AINE-AGENTS.md §4.1`).
- Engineering standards in `docs/engineering-standards.md` (linting, typing, naming).

#### Compliance & Risk Agent
- Skill-question content set v1 in `docs/compliance/skill-questions.md`. Reviewed by Legal Counsel.
- Free-entry route copy block in `docs/compliance/copy/free-entry-route.md`. Reviewed by Legal Counsel.
- Audit-log specification in `docs/compliance/audit-log-spec.md`.

### Phase 1 exit criteria

- ✅ All ADRs (001–012) drafted and **approved by EL** (`AINE-AGENTS.md §6`).
- ✅ All Phase 2/3 stories in `ready` state, with technical context from Architect attached.
- ✅ KPI targets committed (no TODOs in PRD §5).
- ✅ Test strategy signed off by EL.
- ✅ Skill-question content set + free-entry copy approved by Legal Counsel.

---

## 5. Phase 2 — Platform (weeks 6–9)

Three weeks. Build only the engineering platform — no business modules yet.

### Activities

- **DevSecOps Agent** finalises:
  - Production-grade multi-stage Dockerfiles (backend, admin web).
  - GitHub Actions: lint → typecheck → test → build → security scan → deploy-to-staging (auto on `main`).
  - Managed-platform staging environment live.
  - Sentry wired into backend, mobile, admin.
  - Secrets fully in the platform's secret manager (no `.env` in repo).
  - Backup baseline: nightly Postgres dump to S3, 7-day retention. Restore drill scripted.
- **Backend Engineer Agent** builds:
  - FastAPI app shell with module folders (`identity/`, `wallet/`, `payment/`, `ticket/`, `draw/`, `admin/`) — each empty but structured per the agreed module layout.
  - Alembic baseline migration (empty schema).
  - Outbox table + worker process running and idle (no consumers yet).
  - Health check endpoints (`/healthz`, `/readyz`).
  - Request correlation ID middleware.
  - RBAC scaffolding (tables, permission decorator, no real roles assigned yet).
- **Frontend Engineer Agent** builds:
  - Flutter app shell with bottom nav, theme, splash, and a stubbed home screen. Riverpod scaffold.
  - Next.js admin shell with auth scaffolding, layout, and a stubbed dashboard. TanStack Query scaffold.
  - API client generated from the Phase 1 OpenAPI scaffold (regenerated on every OpenAPI change in CI).
- **QA Agent** sets up:
  - Vitest / Pytest / Flutter Test runners in CI with coverage reporting.
  - Playwright runner against the staging URL.
  - Coverage badges on PRs.
  - The CI lint job for artefact shape (`AINE-AGENTS.md §9.1`) — stories, ADRs, runbooks rejected if they don't match the required sections.

### Phase 2 exit criteria

- ✅ One-command developer setup verified by a second engineer (not the author).
- ✅ Every PR runs the full pipeline; main is always deployable to staging.
- ✅ Sentry receiving events from all three apps in staging.
- ✅ Outbox worker running idle without errors for 24h.
- ✅ Staging URL serves the admin shell and Flutter app builds for both iOS and Android.

---

## 6. Repository structure (V1)

```
nf_atlas/
├── .claude/
│   ├── agents/                   # AINE agent definitions (AINE-AGENTS.md §8)
│   ├── settings.json             # Tool perms, hooks
│   └── settings.local.json       # Personal overrides (gitignored)
├── apps/
│   ├── mobile/                   # Flutter consumer app
│   └── admin/                    # Next.js admin (only frontend that ships in V1)
├── backend/
│   ├── api/                      # FastAPI modular monolith
│   │   ├── identity/
│   │   ├── wallet/
│   │   ├── payment/
│   │   ├── ticket/
│   │   ├── draw/
│   │   ├── admin/
│   │   ├── shared/               # cross-module utilities (correlation, logging, errors)
│   │   └── main.py               # app factory
│   ├── migrations/               # Alembic
│   └── tests/                    # backend unit + integration
├── packages/
│   └── shared/
│       └── openapi.yaml          # source of truth — API client + admin types generated from this
├── infrastructure/
│   ├── terraform/                # cloud resources
│   └── docker/
│       ├── Dockerfile.backend
│       ├── Dockerfile.admin
│       └── compose.yaml          # local dev
├── e2e/                          # Playwright specs + MANUAL.md (mirrors nearform-tdapp)
├── _bmad/                        # BMad installer-managed; do not edit
│   ├── config.toml
│   └── custom/                   # team customisations (atlas-* custom agents live here)
├── _bmad-output/
│   ├── planning-artifacts/       # BMad bmm module outputs
│   │   ├── briefs/
│   │   ├── prds/prd-nf-atlas-2026-06-29/PRD.md
│   │   ├── delivery-framework.md
│   │   ├── architecture.md
│   │   ├── epics.md
│   │   └── stories/
│   ├── implementation-artifacts/ # BMad bmm module outputs
│   └── test-artifacts/           # BMad tea module outputs (Murat)
│       ├── test-design/
│       ├── test-reviews/
│       └── traceability/
├── docs/                         # project knowledge (BMad-mapped)
│   ├── AINE-AGENTS.md
│   ├── AI-INTEGRATION-LOG.md
│   ├── adr/
│   ├── runbooks/
│   ├── compliance/
│   ├── domain-model.md
│   ├── erd.md
│   ├── events.md
│   ├── engineering-standards.md
│   └── definition-of-done.md
├── .github/
│   └── workflows/
├── main.py                       # legacy — to be removed in Phase 2
└── README.md
```

The `main.py` at the root (current PyCharm boilerplate) is removed in Phase 2 cleanup.

---

## 7. Phase 3 — Module build & closed beta (weeks 9–17)

Eight weeks. The 6 modules are built in **dependency order with parallelism where possible**.

### Module build order

```
Identity ──► Wallet & Ledger ──► Payment ──► Ticket ──► Draw Engine
   │                                                          │
   └─────────────────────────► Admin ◄───────────────────────┘
```

- **Identity** (weeks 9–10) — registration, OTP, login, MFA, KYC adapter, self-exclusion. Mobile + admin login flows.
- **Wallet & Ledger** (weeks 10–11) — chart of accounts, journal entries, balance queries, reconciliation job skeleton. **Two-approval gate enforced from first commit** (`AINE-AGENTS.md §6`).
- **Payment** (weeks 11–13) — Paystack inline + bank transfer, idempotency, webhook handler, refund flow, ledger integration. Paystack sandbox only in this phase.
- **Ticket** (weeks 13–14) — skill question delivery, free-entry transcription, idempotent issuance, ownership history. Mobile purchase flow.
- **Draw Engine** (weeks 14–16) — commit/sale/close/reveal lifecycle, CSPRNG, public entropy fetcher (drand + Bitcoin block hash), reserve-winner algorithm, replay tooling, hash-chained audit log. **Two-approval gate enforced from first commit.**
- **Admin** (weeks 9–17 in parallel) — RBAC, draw config, KYC review queue, prize fulfilment state machine, support tickets, refund initiation.

### Per-module lifecycle (every module follows this)

1. **Story refinement** — PM + Architect finalise stories for the module.
2. **Domain model** — Architect amends `docs/domain-model.md` for this module's bounded context.
3. **Schema** — Architect specifies tables in `docs/erd.md`; Backend writes the Alembic migration; EL approves migration before merge.
4. **API surface** — Architect updates `packages/shared/openapi.yaml`; CI regenerates clients; admin and mobile pick up new types.
5. **Event surface** — Architect updates `docs/events.md` for any new events.
6. **Implementation** — Backend (modules listed in §7) + Frontend (mobile + admin surfaces). Each story lands as a single PR.
7. **Testing** — QA adds tests at the levels in `docs/qa/strategy.md`. No mocks for ledger or draw paths.
8. **Compliance review** — Compliance & Risk Agent reviews every Wallet, Payment, Ticket, Draw Engine PR before merge.
9. **Docs** — ADRs amended if architectural choices made during build; runbooks added for any operational scenario the module introduces.
10. **AI log entry** appended per `AINE-AGENTS.md §7`.

### Closed beta milestone (end of week 17)

One real-money draw with a small (~₦100k) cash prize, invited beta users only. Runs end-to-end through every V1 module:
- Beta users register, complete KYC, deposit, answer skill question, buy paid entries.
- A small number of free-route postal entries are transcribed and join the same pool.
- Draw runs through commit/sale/close/reveal with full audit log.
- Winner notified via WhatsApp + email, claims the prize, payout settles in the ledger.
- Reconciliation job confirms ledger matches Paystack settlement.

### Phase 3 exit criteria

- ✅ All 6 modules functional and merged to `main`.
- ✅ Closed beta draw completed successfully end-to-end.
- ✅ Reconciliation reports clean.
- ✅ Audit-log replay verified for the beta draw.
- ✅ No open SEV-1 or SEV-2 issues.

---

## 8. Phase 4 — Quality engineering (weeks 17–21)

Four weeks. Quality work that's been continuous through Phase 3 gets driven to launch-ready gates.

### Coverage and quality gates (gated by CI)

| Gate | Target | Enforced |
|---|---|---|
| Domain logic coverage (Wallet, Ticket, Draw Engine) | ≥ 90% | CI fails PR |
| Overall meaningful coverage | ≥ 80% | CI fails PR |
| API contract compliance | 100% (OpenAPI ↔ implementation) | CI fails PR |
| E2E pass rate | 100% on `main` | CI fails PR |
| Lint + typecheck | 0 errors | CI fails PR |
| OWASP dependency scan | 0 critical, 0 high | CI fails PR |
| Container scan (Trivy) | 0 critical, 0 high | CI fails PR |
| Secrets scan (gitleaks) | 0 findings | CI fails PR |
| Accessibility (axe-core on admin + mobile) | 0 WCAG 2.2 AA violations | CI fails PR |
| API p95 latency (k6 against staging) | < 300 ms | weekly perf run, alerts if regressed |
| Ticket purchase concurrency (k6) | 500 concurrent purchases without error | weekly perf run |

### Critical journeys covered by E2E (Playwright)

1. New user → register → OTP → KYC submit → KYC approved → login.
2. Logged-in user → browse active draw → skill question → Paystack sandbox payment → ticket appears.
3. Operator → create draw (commit) → users buy → close → reveal → winner displayed.
4. Free-entry route: operator transcribes postal entry → ticket appears in pool → can win.
5. Winner → notification → KYC verify (if not already) → prize claim flow → payout recorded in ledger.
6. Refund path: operator-initiated refund → Paystack refund → ledger entries balanced.
7. Failed payment: payment fails at Paystack → no ticket issued → user sees clear error.
8. Idempotency: double-clicked "Buy 10 tickets" produces exactly 10 tickets.
9. Self-exclusion: excluded user cannot register again with same BVN.
10. Audit replay: a completed draw is replayed from stored inputs and produces the same winner.

### Security review

- **Independent third-party penetration test** (paid human firm — not an agent) against staging covering: API surface, auth flows, Paystack integration, draw engine, admin RBAC.
- **Threat modelling session** led by Compliance & Risk Agent + EL, covering fraud vectors specific to prize platforms (entry inflation, identity rotation, collusion).
- Findings go to backlog with severity; **0 critical / 0 high** is a Phase 5 gate.

### Phase 4 exit criteria

- ✅ All CI gates green on `main`.
- ✅ All 10 critical journeys passing in Playwright.
- ✅ Penetration test report received; 0 critical / 0 high findings open.
- ✅ Performance gates met under k6 load.

---

## 9. Phase 5 — Containerisation & deploy (weeks 21–23)

Two weeks. Move from staging to production.

### Activities

- **Production environment** provisioned on the managed platform.
- **Blue-green deploy** primitives configured. **Rollback drill** performed and timed.
- **Production secrets** rotated and stored in the platform's secret manager.
- **Production Paystack** merchant account switched live (was sandbox through Phase 3–4).
- **Production KYC vendor** environment switched live.
- **DNS** cut over to production. SSL/TLS 1.3 verified.
- **Backup** verified against production: nightly Postgres dump to S3, restore drill completed end-to-end.
- **Domain-name + brand assets** loaded into admin and mobile build configs.

### What V1 does NOT use (deferred to V2+)

- ❌ Kubernetes. The managed platform's primitives handle V1's scale and operational load.
- ❌ Helm charts. Not needed without K8s.
- ❌ Terraform modules beyond cloud resources (no Helm chart Terraform).
- ❌ Argo CD / GitOps. Platform-native deploy is sufficient.
- ❌ Horizontal pod autoscaling. Platform autoscaling primitives sufficient at V1 scale.

When the V2 trigger fires (defined in §11), DevSecOps Agent leads the K8s migration.

### Phase 5 exit criteria

- ✅ Production environment running with feature flag set to `internal-only`.
- ✅ Smoke test against production passes for every critical journey from §8.
- ✅ Rollback drill completed under 5 minutes.
- ✅ Backup restore drill completed under 1 hour.

---

## 10. Phase 6 — Production readiness & launch (weeks 23–26)

Three weeks. The actual launch.

### Go-live checklist (signed off line-by-line before launch)

**Operations**
- [ ] Dashboards for: payment success rate, ticket purchase rate, draw lifecycle state, ledger reconciliation status, KYC queue depth, p95 latency, error rate, Sentry top issues.
- [ ] Alerts for: payment success < 95%, KYC queue > N pending, ledger reconciliation mismatch, p95 > 500ms, error rate > 1%, Sentry SEV-1 issue created.
- [ ] On-call rotation defined; PagerDuty (or equivalent) set up.
- [ ] Runbooks complete for: payment provider outage, KYC vendor outage, ledger reconciliation mismatch, draw engine stuck, audit-log integrity break, hot-rolling secrets, restoring from backup.
- [ ] Incident communications template ready (Twitter/X, in-app banner, customer email).

**Compliance**
- [ ] Final legal counsel sign-off on launch copy and prize terms.
- [ ] T&Cs and privacy policy published and linked from every relevant screen.
- [ ] Free-entry route documented on every draw page with the exact wording counsel approved.
- [ ] KYC procedure verified against AML requirements.
- [ ] Data retention policy in place; right-to-erasure flow tested.
- [ ] Audit-log export capability tested with a sample draw.

**Security**
- [ ] All pen-test findings closed or risk-accepted with mitigation.
- [ ] Secrets rotated post-Phase 5.
- [ ] Admin RBAC reviewed; least-privilege confirmed.
- [ ] Backup encryption verified.

**Product**
- [ ] Flagship vehicle-prize draw configured in production (commit not yet published).
- [ ] Marketing site / store listings live.
- [ ] Customer support team trained and rostered with first day's coverage.
- [ ] WhatsApp Business outbound templates approved by Meta.

**Sign-off**
- [ ] EL signs off on engineering readiness.
- [ ] Compliance Lead signs off on regulatory readiness.
- [ ] Finance Lead signs off on operational readiness.
- [ ] Founder signs off on go.

### Launch

- T-7 days: production feature flag flipped from `internal-only` to `private-beta` (existing beta users get access first; soak for 5 days).
- T-2 days: flagship draw commit hash published.
- T-0: flagship draw goes live to the public.
- T+4 weeks: post-launch retro feeds the V2 backlog.

---

## 11. V2+ annex (preserved from the original framework)

What's deliberately NOT in V1, with the trigger that moves each item to V2+.

| V2+ work | Trigger to start planning |
|---|---|
| Subscriptions / recurring entries | After 3 months of stable V1 operation + cohort retention data |
| Referral programme | After CAC data from V1 indicates referrals would lower it |
| Loyalty tiers, cashback, bonus, promo balances | After product proves repeat purchase behaviour |
| Instant-win games | After regulator sign-off on the model (separate to the prize-competition opinion) |
| Consumer web app (Next.js consumer surface) | When analytics show > 20% of intent-to-purchase coming from non-app sources |
| Marketing automation, segmentation, lifecycle | After CRM data volume justifies it (proxy: > 10k MAU) |
| Push notifications + SMS | After mobile MAU > 5k (push), and when transactional volume justifies SMS cost |
| Multi-rail payments (Flutterwave, Moniepoint, USSD direct) | Each rail triggered by either user demand or Paystack downtime metrics |
| Multi-region (Ghana, Kenya, SA, Rwanda, Uganda, Tanzania) | After Nigerian launch hits MAU and MRR thresholds defined in V2 roadmap |
| AI/ML personalisation, recommendations, fraud models, pgvector | After enough data to make the models non-trivial (proxy: 6 months of behavioural data) |
| OpenSearch | When log volume or search query needs outgrow Postgres + platform logs |
| Kubernetes + Helm + Argo CD | When the managed platform cannot handle scale, or when a second cluster (DR) is genuinely needed |
| Distributed tracing (full OTel collector + Tempo/Jaeger) | When > 3 services exist (i.e. when modules start being extracted from the monolith) |
| Standalone Web Engineering Agent | When consumer web ships |
| Growth & CRM Agent | When marketing automation ships |
| AI & Personalisation Agent | When AI/ML features ship |
| Data & Analytics Agent | When BI / data warehouse work ships |
| Standalone Tech Writer Agent | When docs surface area outgrows distributed ownership (proxy: > 100 pages, > 5 distinct external doc consumers) |
| Live-streamed draws with on-camera observers | When a single prize value exceeds ₦25M |
| Property prizes | After legal + ops capability for title transfer is established |
| MCP server integration (Playwright, PostgreSQL, GitHub, Docker, etc.) | When automation friction in V1 build justifies the investment |

The point of this annex: **none of these are forgotten**. They have triggers, not just hopes.

---

## 12. Change process for versioned artefacts

How an artefact gets updated mid-build without breaking the "specifications drive code" discipline.

1. **Anyone (agent or human) can propose** a change to a versioned artefact by opening a PR against the artefact file.
2. **The artefact's owner agent** reviews the proposed change (e.g. Architect reviews ADR changes, PM reviews story changes).
3. **If approved**, the artefact is updated. If the change has cascading implications (e.g. an ADR change affecting multiple modules), the owner agent identifies the affected stories/code and opens follow-up issues.
4. **The AI Integration Log records** the change with reviewer + approver.
5. **Phase exit criteria** referenced from the new version of the artefact apply to all subsequent work; in-flight PRs against the old version are reviewed for impact.

Hard rule: **no in-flight code change retro-justifies an artefact change.** Spec changes first, then code follows.

---

## 13. Success criteria (V1 launch)

Replaces the original framework's success criteria with V1-specific gates. Targets without numbers are deferred to the founder-input KPIs in `PRD.md §5`.

| Category | V1 target | Measured at |
|---|---|---|
| PRD & Architecture | All ADRs approved, no critical gaps | Phase 1 exit |
| Story coverage | 100% of V1 scope decomposed into stories | Phase 1 exit |
| Domain logic coverage | ≥ 90% (Wallet, Ticket, Draw Engine) | Phase 4 exit |
| Overall test coverage | ≥ 80% meaningful | Phase 4 exit |
| API contract compliance | 100% | Continuous (CI) |
| E2E coverage | All 10 critical journeys (§8) automated | Phase 4 exit |
| Performance | API p95 < 300ms | Phase 4 exit (k6) |
| Availability | ≥ 99.5% over first 30 days post-launch | T+30 |
| Security | 0 critical / 0 high open after pen test | Phase 5 entry |
| Accessibility | WCAG 2.2 AA on admin and mobile | Phase 4 exit |
| CI/CD | Fully automated, rollback drilled | Phase 5 exit |
| Deployment | One-command local + production-ready managed-platform deploy | Phase 5 exit |
| Documentation | All artefacts in §6's `docs/` tree present and current | Phase 6 sign-off |
| Compliance | Legal sign-off on launch copy and prize terms | Phase 6 sign-off |
| Launch | Flagship vehicle-prize draw runs end-to-end without intervention | T+0 |

The original framework's "≥ 99.9% in production" target is **deferred to V2**. V1 launches at 99.5% with a path to 99.9% as the platform matures.

---

## 14. What was deliberately changed from the original framework

For traceability:

- **Phase 0 expanded** to explicitly include legal opinion as a hard gate (was implicit).
- **Phase 1 quantified** — specific ADRs listed, specific story counts targeted.
- **Phase 2 trimmed** — removed Prometheus / Grafana / Loki / OpenSearch from V1; kept OTel SDK in code so V2 migration is one config change.
- **Phase 3 scoped to 6 modules** with explicit dependency order; the other 8 modules moved to §11.
- **Phase 4 gates given numeric thresholds and made CI-enforced**.
- **Phase 5 removed K8s/Helm/Argo** for V1 (managed platform instead).
- **Phase 6 expanded** with a real go-live checklist instead of "Go-Live Checklist" as a one-liner.
- **AI Engineering Integration** moved to `AINE-AGENTS.md` (dedicated doc) and §7 of that doc defines the log format.
- **MCP usage** deferred to V2 trigger (§11) rather than baked into V1.
- **Success criteria** rewritten with V1 targets and explicit measurement points.
- **Change process for artefacts** (§12) added; "immutable" language softened to "versioned."
- **V2+ annex** (§11) preserves every cut item with a trigger condition, so nothing is forgotten.

---

## 15. Cross-references

- `_bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md` — what is being built and why.
- `docs/AINE-AGENTS.md` — who builds it and how they coordinate.
- `/Users/S1408661/Projects/nearform-tdapp/` — BMad workflow precedent (testing approach, doc patterns, AI Integration Log format).
