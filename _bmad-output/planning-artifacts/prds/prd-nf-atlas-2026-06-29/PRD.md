# Project Atlas — PRD v1 (Nigeria Launch)

**Status:** Draft, 2026-06-29
**Supersedes:** the long-form PRD (architectural catalog) for V1 scope decisions.
**Audience:** founders, V1 build team, prospective legal counsel.

---

## 1. The product decision

> **Amended 2026-11-26 (AMEND-001, AMEND-003), applied 2026-11-27.** The 2026-06-29 version of this section named two mechanics that kept Atlas outside gambling regulation. Both have been removed. The strikethroughs below are deliberate: this PRD records the decision, it does not pretend the mechanics were never specified.

Atlas is a **paid prize draw platform** intending to operate under a Nigerian State gaming licence.

**It does not rely on any exemption, carve-out or mechanic to sit outside gambling regulation.** The two that were specified are gone:

1. ~~A free entry route on every draw, producing tickets that go into the same pool with the same odds as paid entries.~~ **Removed 2026-11-23** by founder decision. It was never operable — no P.O. box was ever leased (R-FREE-01, flagged in REVIEW-001 §6.1 and left open). Confirmed 2026-11-26 as not returning, irrespective of counsel Q1.6.
2. ~~A skill question on every paid entry, requiring genuine knowledge or judgment.~~ **Removed 2026-11-26** by founder decision. The implementation never met the standard this section set — REVIEW-001 §3.1 rejected it for real-user launch on 2026-07-08 and that verdict was never lifted — and the 2026-11-23 research found no skill carve-out in the governing State law for it to qualify for. It was friction with no legal return, and may have carried exposure of its own under the Lagos advertising code.

**Lawfulness rests on holding a State gaming licence. Atlas does not yet hold one.**

**Marketing copy must never use "lottery," "raffle," "luck of the draw," or equivalent.** Unchanged and still binding. Compliance copy is part of the design system, not an afterthought.

**Atlas must not assert its own regulatory classification in consumer copy** (REVIEW-001 §2.1). With no mechanic left to support a "prize competition" claim, describe the mechanic and let the licence speak to the classification.

### Nigerian legal caveat (must be resolved before launch)

> **Rewritten 2026-11-27.** The 2026-06-29 version of this caveat was framed against a statute that no longer exists.

The prize-competition carve-out is **UK-derived and may have no Nigerian equivalent at all.**

The **National Lottery Act 2005 was nullified** by the Supreme Court of Nigeria on 22 November 2024 (*AG Lagos State & Ors v AG Federation*, SC/1/2008). Lottery and gaming are now **exclusively State matters** and the NLRC holds no national licensing authority. The President declined assent to the Central Gaming Bill 2025 in reliance on that judgment, so there is no federal statute for Atlas to be exempt from.

The operative law in Atlas's launch market is the **Lagos State Lotteries and Gaming Authority Law 2021**, which on Atlas's own desk research defines "Gaming" as any scheme distributing prizes **by lot or chance with no payment element**, and expressly classes promotional competitions as "Other lotteries". On that reading **neither a skill question nor a free entry route removes Atlas from the perimeter, and a State licence is required.**

Source: `research/nigerian-draw-classification-research-2026-11-23.md`. Single-pass desk research, not legal advice, self-reporting medium confidence on several findings; the SC/1/2008 judgment text was not retrieved. **Counsel must verify it first.**

**Hard prerequisite for V1 (unchanged and reaffirmed):** Nigerian gaming counsel signs off on the model and any licence/permit obligations **before any code touches a real payment rail.** Counsel has **not** been engaged as at 2026-11-27.

**Additional prerequisite (new, AMEND-001 §2.2):** because advertising or promoting an unlicensed scheme may itself be an offence under the Lagos regime, **no public marketing spend before counsel sign-off either.** The original caveat gated code; it should have gated promotion too.

---

## 2. V1 scope (what we ship in 6 months)

### What V1 is

A mobile-first paid prize draw platform that lets a user in Nigeria:

- Register, verify identity (light KYC), and log in.
- Browse currently active draws and view a single past draw archive.
- Pay for entries via Paystack (card + bank transfer).
- ~~Enter for free via a documented free-entry route (see §3).~~ **Struck 2026-11-23** — the free entry route was removed and was never operable (R-FREE-01).
- Buy an entry and receive a ticket, visible in their account. *(Was "answer the skill question, receive a ticket" — the skill question was removed 2026-11-26.)*
- Watch a published draw result and, if they won, follow a guided claim flow.
- Contact support.

A back-office that lets the operator:

- Configure and schedule a draw (prize, ticket price, close date, draw date). *(`max entries` struck 2026-11-23 — the `entries_cap` field existed but was never enforced, and the founder decided V1 operates with no per-draw cap. `skill question` struck 2026-11-26.)*
- Review and approve KYC submissions.
- Run a draw (commit, sell, close, reveal, publish, audit).
- Manage prize fulfilment workflow (contact winner, verify, dispatch, sign-off).
- Handle support tickets and refunds.

### What V1 is NOT

Explicit cuts from the long-form PRD. These all have a place; none of them ship in V1:

- ❌ Subscriptions / recurring entries
- ❌ Referral programme and commission rules
- ❌ Loyalty tiers, cashback, bonus credits, promotional balances
- ❌ Instant-win games
- ❌ Consumer web app (admin web only; consumer is Flutter only)
- ❌ Marketing automation, segmentation, lifecycle journeys
- ❌ Push notifications and SMS (V1 uses email + WhatsApp Business outbound only)
- ❌ Multi-rail payments (V1 is Paystack only — defer Flutterwave, Moniepoint, USSD direct, M-Pesa)
- ❌ Multi-region support (V1 is Nigeria only — but module boundaries leave room)
- ❌ AI/ML personalisation, recommendations, fraud models
- ❌ pgvector, OpenSearch, distributed tracing, Kafka
- ❌ Kubernetes, Argo CD, Helm, multi-cluster
- ❌ Live-streamed draws with on-camera observers (V1 publishes a recorded draw with full audit log + commit-reveal proof; live streaming is a V2 trust upgrade)
- ❌ Property prizes (V1 prizes are **cash and vehicles only** — property introduces title transfer, stamp duty, and ownership-vehicle complexity that should not be on the launch critical path)

### Why these cuts

V1 must prove three things and nothing else:

1. **Trust:** users believe the draw is fair, payments are safe, and winners actually get paid.
2. **Compliance:** Atlas holds the State gaming licence its model requires. *(Rewritten 2026-11-27 — was "the prize-competition model holds up under NLRC scrutiny". The NLRC has no national licensing authority since SC/1/2008, and Atlas no longer claims a carve-out.)*
3. **Unit economics:** at modest scale (see §5), a single Paystack-driven funnel produces predictable CAC and AOV.

Everything cut above is a growth/retention/scale lever. None of them matter if V1 fails at any of the three above.

---

## 3. Functional requirements (V1)

### 3.1 Draw mechanics (first-class)

> **Retitled from "Prize-competition mechanics" and rewritten 2026-11-27** (AMEND-001 §2.3, AMEND-003 §3.3).

- ~~Every draw has a **free entry route** (postal entry to a P.O. box, transcribed within 24h). One free entry per person per draw.~~ **Struck 2026-11-23.** Never implemented as specified — no P.O. box was ever leased.
- ~~Every paid entry path requires a **skill question** answered before payment confirmation.~~ **Struck 2026-11-26.**
- **Tickets are stored with an `entry_source` field** (`paid` | `free`). The draw engine treats both identically. Audit logs and the post-draw proof include the split. *(Corrects a long-standing drift: this said `postal_free`; the schema has always said `free`.)*
- **The `'free'` enum value, the `free_entry_slips` table and the `skill_question_*` tables are retained deliberately and must not be dropped.** Historical tickets carry `entry_source='free'`, published commit-reveal proofs report the paid/free split, and the ADR-005 hash-chained audit log references rows in those tables. A published proof must never be rewritten.
- Every draw page displays the total entries at close.
- **Lawfulness rests on holding a State gaming licence, not on draw mechanics.** No mechanic in this section is load-bearing for classification. Do not reintroduce one as a compliance measure without an amendment and counsel sign-off.

### 3.2 Identity

- Email + phone registration. Phone OTP verification on signup.
- Login: email/phone + password. MFA via TOTP optional, mandatory for accounts that have won a prize before claim.
- KYC: BVN-based identity check via a vendor (Smile Identity / Dojah / Prembly — vendor selection is Phase 0). Document upload for prize claims above a configurable threshold.
- Age gate: 18+. Hard block at registration.
- **Self-exclusion (Phase A — shipped 2026-11-24):** a user can permanently close their account from settings. Closure is enforced at login and at ticket purchase, every session is revoked, and the account cannot enter any draw. **There is no reversal.** A closed account's login returns an explicit "this account has been closed" message, gated behind the password check so exclusion status cannot be enumerated (REVIEW-004).
- **Self-exclusion (Phase B — NOT DELIVERED):** blocking re-registration by the same person requires BVN matching and is **blocked on ADR-007 (KYC), which is unbuilt.** Until Phase B ships, a closed account does not prevent the same person opening a new one with a different email and phone. **Consumer copy must not claim otherwise** — see REVIEW-002 §6.1 for the withdrawn wording, and `test_phase_a_does_not_block_reregistration` for the test that enforces the boundary.

### 3.3 Wallet & ledger

- Single Naira balance, derived from a **double-entry ledger.** No mutable balance field anywhere.
- Account types in the chart of accounts: `user_wallet`, `operator_revenue`, `prize_pool`, `refund_payable`, `payment_gateway_clearing`.
- Every state change is two journal entries (debit + credit). Balance = sum of journal entries for that account.
- V1 holds **only money paid by the user** — no bonus, no cashback, no promotional credits. (Those introduce convertibility/expiry/tax rules that should not be on the launch path.)
- Reconciliation job runs nightly: ledger balance per gateway clearing account must match Paystack's settlement report.

### 3.4 Payment

- **Paystack only** in V1 (card + bank transfer). Inline checkout for card; redirect for bank transfer.
- Every payment intent has a **client-supplied idempotency key.** Double-clicking "Pay" cannot produce two charges.
- Webhook-driven confirmation. Signed webhooks; verify HMAC.
- Failed payments roll back the pending ticket. *(The skill-question resume window was struck 2026-11-26 — there is no skill question to resume.)*

### 3.5 Ticket

- A ticket is issued **only after** (a) confirmed payment, (b) the draw still open, (c) the buyer not self-excluded. *(Rewritten 2026-11-27: the skill-answer and free-entry-transcription conditions were struck with those features; the self-exclusion condition was added by ADR-010 Phase A.)*
- Ticket purchase is **end-to-end idempotent** on a client-supplied request key, not just at the payment layer.
- Ticket numbers are assigned at issuance, not at purchase intent. No reservation of numbers.

### 3.6 Draw engine (provably fair)

- For each draw:
  1. **Commit phase** (when draw is created): operator generates server seed, publishes `commit = SHA-256(server_seed || draw_id)`. Commit is timestamped and immutable.
  2. **Sale phase:** users buy/earn tickets. Entry counts (paid + free) are public.
  3. **Close phase:** sales close at the configured time. The full ticket list is hashed and the hash is published.
  4. **Reveal phase:** operator publishes `server_seed`, the **public entropy source** at the close time (Bitcoin block hash at height H closest to close + drand round R closest to close — both, concatenated), and the deterministic algorithm that combines `server_seed + entropy + ticket_list_hash` into a winning ticket index via HMAC-SHA-256.
  5. **Audit:** anyone with the published inputs can re-run the algorithm and verify the same winner.
- A draw can be **replayed** from stored inputs to reproduce the same winner, byte-for-byte.
- All draw events emit immutable audit-log entries (append-only table, hash-chained).
- "Reserve winners" are defined: if the primary winner fails KYC, can't be contacted within 14 days, or declines, the **next deterministic ticket from the same seed-and-entropy run** wins. The algorithm produces an ordered list of N winners on the same inputs; reserves are not a separate draw.

### 3.7 Admin / operations

- RBAC: at minimum `operator`, `draw_admin`, `kyc_reviewer`, `finance`, `support`. Single-screen role assignment.
- Draw lifecycle screens map 1:1 to the commit/sale/close/reveal phases above. Manual operator approval to advance each phase.
- KYC queue: pending reviews surfaced with vendor results; manual override + reason logged.
- Prize fulfilment workflow: a state machine (`winner_selected → winner_contacted → kyc_cleared → fulfilment_in_progress → delivered → signed_off`). Each transition is logged with operator ID.
- Refunds: only operator-initiated in V1; produces both a Paystack refund and the matching ledger entries.

### 3.8 Notifications (V1 only)

- **Email** (transactional only — receipt, KYC update, winner notification, refund confirmation).
- **WhatsApp Business outbound** for the winner notification flow (template messages).
- No push, no SMS, no marketing emails in V1.

---

## 4. Architecture for V1

Same modular-monolith-first stance as the long PRD, with the stack trimmed to what V1 actually needs:

- **Backend:** FastAPI + Python 3.13 + SQLAlchemy 2 + Pydantic v2 + Alembic. Single deployable.
- **Data:** PostgreSQL (primary), Redis (cache + rate limits — **not** an event broker in V1). S3-compatible object storage for KYC docs and audit-log archives.
- **Async work:** **Outbox table polled by a worker process** — no Celery, no Kafka, no Redis Streams in V1. The outbox gives at-least-once with idempotent consumers, which is the only guarantee V1 needs.
- **Mobile:** Flutter (iOS + Android), Riverpod for state.
- **Admin:** Next.js, Tailwind, TanStack Query.
- **Infra:** Docker + a managed platform (Fly.io / Railway / Render / AWS App Runner) — **not** Kubernetes in V1. Terraform for the cloud resources that exist (DB, S3, DNS, secrets).
- **CI/CD:** GitHub Actions. Blue/green or rolling, via the managed platform's primitives.
- **Observability:** OpenTelemetry SDK in code (so it's free later), but V1 ships with **Sentry + the managed platform's logs and metrics**. Don't operate a Prometheus/Grafana/Loki stack in V1.
- **Secrets:** the platform's secret manager (e.g. Fly secrets, AWS Secrets Manager). Vault is V2+.

### Modules in V1

Six modules. Each one owns its tables, services, and HTTP routes. Communication is direct function calls within the monolith plus events written to the outbox.

1. **Identity** — registration, login, OTP, MFA, KYC adapter, self-exclusion.
2. **Wallet & Ledger** — accounts, journal entries, balance queries, reconciliation.
3. **Payment** — Paystack adapter, intents, webhooks, refunds.
4. **Ticket** — idempotent issuance, ownership, self-exclusion enforcement at purchase. *(Skill question and free-entry transcription struck 2026-11-26 / 2026-11-23.)*
5. **Draw Engine** — commit/sale/close/reveal lifecycle, CSPRNG, public entropy fetcher, replay, audit log.
6. **Admin** — RBAC, operator workflows, prize fulfilment, support tickets.

Notifications, fraud, compliance, marketing, reporting, referrals, prize catalogue beyond cash+vehicles, AINE personalisation — **none of these are modules in V1.** Where their concerns appear (e.g. a "prize" entity to attach to a draw), they live as thin tables inside the modules above until they earn their own boundary.

### Module ownership (AINE agents)

Each module has one **primary owner agent** (drives implementation), one or more **reviewer agents** (must approve before merge), and a **human approver** (final sign-off on merge). Defined in `AINE-AGENTS.md`; tabulated here so this PRD stays self-contained.

| Module | Primary owner | Mandatory reviewers | Human approver(s) |
|---|---|---|---|
| Identity | Backend Engineer Agent | Solution Architect; Compliance & Risk (KYC adapter, self-exclusion, age gate) | Engineering Lead |
| Wallet & Ledger | Backend Engineer Agent | Solution Architect; Compliance & Risk; QA | Engineering Lead + Finance Lead (two approvals) |
| Payment | Backend Engineer Agent | Solution Architect; Compliance & Risk; QA | Engineering Lead + Finance Lead (two approvals) |
| Ticket | Backend Engineer Agent | Solution Architect; Compliance & Risk (entry mechanics + self-exclusion enforcement); QA | Engineering Lead |
| Draw Engine | Backend Engineer Agent | Solution Architect; Compliance & Risk; QA | Engineering Lead + Compliance Lead (two approvals) |
| Admin | Frontend Engineer Agent (Next.js admin UI) + Backend Engineer Agent (RBAC + workflows) | Solution Architect; QA; Compliance & Risk for any operator action that touches money or draws | Engineering Lead |

**Frontend Engineer Agent** owns the consumer-facing flows in the Flutter mobile app for every module that has a user-facing surface (Identity, Payment, Ticket, Draw Engine), pairing with the Backend owner agent per story.

**QA Agent** is a mandatory reviewer on every module's PRs for test sufficiency (per `docs/qa/strategy.md`).

**DevSecOps Agent** is not module-specific — owns CI/CD, infrastructure, observability, and security tooling across all modules.

**PM Agent** is not module-specific — owns the backlog, stories, scope decisions, and KPI tracking across all modules.

Two-approval rules (Wallet & Ledger, Payment, Draw Engine) reflect the irreversibility of money and the trust-criticality of draws. See `AINE-AGENTS.md §6` for the full gate matrix.

### Forward-compat guarantees

Two invariants enforce future extraction:

- **No cross-module direct DB access.** Every module's tables are only read/written by its own service layer. Other modules call its service interface.
- **Every state change emits an outbox event.** The outbox row format is the same shape an external broker would carry. Switching to Kafka later is a transport swap, not a redesign.

A handful of grep checks in CI enforce these (modelled on `nearform-tdapp`'s E2E-9 invariant grep).

---

## 5. KPIs and targets (V1)

The long-form PRD listed metrics with no targets. Targets need to come from the founders' financial model, but the **format** should be:

| KPI | V1 target (3 months post-launch) | V1 target (6 months post-launch) |
|---|---|---|
| Registered users | TODO | TODO |
| KYC completion rate (of registered) | ≥ 60% | ≥ 70% |
| Paid entries per active draw | TODO | TODO |
| Free entries per active draw | track for ratio | track for ratio |
| Average paid entries per buyer per draw | TODO | TODO |
| Payment success rate (Paystack) | ≥ 95% | ≥ 98% |
| Prize claim completion (winner contacted → delivered) | 100% within 30 days | 100% within 21 days |
| API p95 latency | < 500 ms | < 300 ms |
| Uptime | ≥ 99.5% | ≥ 99.9% |
| Open critical bugs in production | 0 sustained > 24h | 0 sustained > 12h |

Targets marked TODO need the founders to commit numbers from the financial model — this PRD won't make them up.

---

## 6. Phased delivery (6 months)

### Phase 0 — Foundations (weeks 0–4)
- Nigerian **gaming** counsel engaged; written opinion on which **State** regime governs an online operator (counsel Q7) and what licence it requires, at what cost (Q1). *(Rewritten 2026-11-27 — the NLRC framing is void.)*
- KYC vendor selected and contracted (Smile / Dojah / Prembly).
- Paystack merchant account live with settlement bank set up.
- ~~Skill-question content set drafted and reviewed by counsel.~~ **Struck 2026-11-26** — there is no skill question. `docs/compliance/skill-questions.md` is cancelled, not outstanding.
- ~~Free-entry route operationalised: P.O. box leased, entry slip designed, transcription workflow documented.~~ **Struck 2026-11-23** — never completed, no longer applicable.
- **Nigerian gaming licence application submitted, and counsel Q7/Q1 answered.** This replaces both struck criteria and is now the whole of the Phase 0 legal gate. It is the harder of the two it replaces.
- Infrastructure baseline: GitHub org, managed platform account, Postgres + Redis + S3 provisioned, CI green.
- Schema for Identity + Wallet/Ledger merged and migrated.

### Phase 1 — Closed beta (weeks 4–12)
- Identity, Wallet/Ledger, Payment, Ticket modules functionally complete.
- Flutter app: signup → KYC → browse one draw → pay → see ticket. *(Skill-question step struck 2026-11-26.)*
- Admin Next.js app: create draw, review KYC, view tickets.
- **One real-money draw** with a small (~₦100k) cash prize. Invited beta users only. Run end-to-end including KYC, ticket purchase, winner notification, payout. **Gated on the State licence** — see §1. *(Free-entry route validation struck 2026-11-23.)*
- Nightly reconciliation job operational.
- Sentry, logs, basic uptime monitoring live.

### Phase 2 — Public soft launch (weeks 12–20)
- Draw Engine with full commit-reveal provably-fair lifecycle live.
- Public entropy fetcher (Bitcoin block hash + drand) integrated and tested with replay.
- Audit-log export and post-draw proof page live.
- Prize fulfilment state machine and admin tooling complete.
- WhatsApp Business outbound integrated for winner notifications.
- First public draw: cash prize, no marketing spend, organic only. Goal is **operational readiness verification**, not growth.

### Phase 3 — Launch (weeks 20–26)
- First flagship draw: a **vehicle prize** (not property — see §2 cuts). Marketing turned on.
- Customer support team trained and rostered.
- Incident runbook complete. On-call rotation in place.
- Post-launch retro at 4 weeks → input to V2 backlog.

---

## 7. Open decisions still required (before Phase 0 ends)

Tracked separately, but listed here so they don't get lost:

1. **Legal:** which **State** regime governs (counsel Q7), and under it does Atlas need a full gaming licence or a proportionate promotional permit, at what cost and timeline (counsel Q1)? Atlas's working position is that a licence is required and no mechanic avoids it. Counsel-driven. *(Rewritten 2026-11-27.)*
2. **Tax:** Nigerian WHT obligations on cash prizes (and on the value of vehicle prizes). Who files? Who pays? Net-of-tax vs gross-of-tax prize advertising.
3. **Vehicle prize logistics:** dealer partnership vs operator-owned fleet. Title transfer process. Logbook / insurance handover.
4. ~~**Free-entry route specifics:** P.O. box vs scanned email submission vs both.~~ **Closed 2026-11-23** — the route was removed and is not returning. Reopens only if counsel Q1.6 says a genuine free route is load-bearing, which would be roughly a week of engineering.
5. ~~**Skill question authoring policy:** who writes them, how often they rotate, what the difficulty floor is.~~ **Closed 2026-11-26** — there is no skill question. `docs/compliance/skill-questions.md` is cancelled.
6. **Live-streamed draws (V2 trigger):** when does volume justify the cost? Probable trigger is **first prize value above ₦25M**.
7. **Customer support staffing:** in-house or outsourced. Hours of coverage. WhatsApp inbound vs email-first.
8. **KPI targets** marked TODO in §5.

---

## 8. What was deliberately NOT changed from the long-form PRD

These are decisions from the original PRD that this V1 keeps as-is — they're senior calls that pay off later:

- Modular monolith first, with strict internal module boundaries and event-driven internal communication.
- Double-entry ledger with derived balances (no mutable balance fields).
- Outbox pattern for reliable event publication.
- Commit-reveal + public entropy for provably-fair draws.
- DDD-style module ownership of tables, services, and APIs.
- API-first development with OpenAPI generated from FastAPI.

The disagreement is **scope and timing**, not architecture.

---

## 9. Cross-references

- **`docs/AINE-AGENTS.md`** — the AI engineering agents that build this V1: substrate, roster, handoff artefacts, arbitration model, human-approval gates, AI Integration Log format.
- **`_bmad-output/planning-artifacts/delivery-framework.md`** — the 26-week, 7-phase delivery ceremony that produces this V1, including the V2+ annex with triggers for every deferred capability.
- Long-form PRD (architectural catalog): the document this V1 was scoped from.
- Sibling project for workflow reference: `/Users/S1408661/Projects/nearform-tdapp` (BMad full-stack workflow with frozen planning artifacts under `_bmad-output/`).