# Project Atlas — Risk Register

**Established:** 2026-07-01
**Owner (Phase 0):** 📊 Mary (BMad Analyst)
**Owner (ongoing):** ⚖️ Adaeze (Atlas Compliance & Risk)
**Reviewer:** Engineering Lead (weekly), Founder (monthly), full-board (quarterly)
**Status:** Draft — pending EL + Founder review per `_bmad-output/planning-artifacts/delivery-framework.md §3` Phase 0 exit criterion
**Location:** `docs/risk-register.md` (BMad-mapped project knowledge)

---

## 0. How this register works

### Scoring

Every risk carries three markers:

- **Likelihood (L):** L=Low, M=Medium, H=High. Refers to probability within the next 12 months unless otherwise stated.
- **Impact (I):** L=Low, M=Medium, H=High, C=Catastrophic. Impact is measured against Atlas's mission (Nigeria launch and trust-first positioning), not just financial cost.
- **Score:** cross-tabulated. Anything scoring **C** on impact (regardless of likelihood) or **H×H** on likelihood-impact goes to the founder monthly and to the board quarterly.

### Score to action

| Score | Meaning | Action cadence |
|---|---|---|
| 🟢 **Low** (L×L, L×M, M×L) | Track only | Reviewed quarterly |
| 🟡 **Medium** (M×M, L×H, H×L) | Active mitigation required | Reviewed monthly |
| 🔴 **High** (M×H, H×M, H×H) | Named owner + timed mitigation + monitoring signal | Reviewed weekly |
| ⚫ **Catastrophic** (any × C) | Founder-level; kill switch if triggered | Reviewed weekly + escalated |

### Owner discipline

Every risk has a **named agent owner** (which of the 9 AINE agents leads the mitigation) and a **named human owner** (which human is accountable when the mitigation lags). "Adaeze / Founder" means: Adaeze runs the operational mitigation; Founder is accountable if it slips.

### Monitoring signal

Every non-trivial risk has a **monitoring signal** — a concrete metric, event, or check that fires when the risk is materialising. If we can't name the signal, we can't manage the risk.

### Change discipline

Adding a new risk, closing an existing one, or changing a score requires an entry in the AI Integration Log (`AINE-AGENTS.md §7`) with agent and reasoning.

---

## 1. Regulatory risks

These are the load-bearing risks. Q1 and Q7 of the counsel engagement (`legal/counsel-engagement-brief.md`) exist to resolve most of them — **Q7 first**, since it establishes which law governs.

> **Rescored 2026-11-24 (⚖️ Adaeze).** R-REG-01 and R-REG-02 were written against the National Lottery Act 2005 and the NLRC. That statute was nullified by the Supreme Court on 22 November 2024; lottery and gaming are now exclusively State matters. Both risks are restated below against State law. The underlying exposure did not change — Atlas's description of it was simply pointed at the wrong regulator for five months.

| ID | Risk | Owner (agent / human) | L | I | Score | Mitigation | Monitoring signal | Review |
|---|---|---|---|---|---|---|---|---|
| **R-REG-01** | **Atlas operates inside a State gaming perimeter without a licence.** *Restated 2026-11-24 — previously framed as "NLRC classifies Atlas's model as a lottery", which is now moot: there is no federal statute and no federal licence.* On the 2026-11-23 research, the Lagos State Lotteries and Gaming Authority Law 2021 defines "Gaming" as any scheme distributing prizes by lot or chance **with no payment element**, expressly classes promotional competitions as "Other lotteries", and prohibits operating or promoting such a scheme remotely without a licence. If correct, Atlas requires a licence and **no mechanic removes that requirement** — the mitigations listed in the 2026-07-01 version of this row (free-route equality, substantive skill question) are legally inert in Nigeria. Consequence: launch halt, criminal exposure for the sole director, brand damage. Likelihood raised M → H. | Adaeze / Founder | H | C | ⚫ | (1) Lagos gaming counsel engaged on licensing pathway, **not** carve-out validation — Q7 then Q1; (2) §8.1 rewritten around licence cost and availability rather than classification defence; (3) **struck as mitigation:** mechanic design. Harder skill questions and a rebuilt free route do not move Atlas outside a definition that needs only chance and a prize; (4) no real payment rail before sign-off (PRD §1). | Counsel Q7/Q1 verdict; LSLGA or FSGRN guidance; any State enforcement against a remote prize-draw operator; Central Gaming Bill reintroduction. | Weekly until counsel engaged and Q7/Q1 answered |
| **R-REG-02** | **Per-State licensing fragments the addressable market.** *Restated 2026-11-24 — previously "Lagos asserts a separate jurisdiction requiring a second licence", which inverted the position: State law is now the only law, so Lagos is the first licence, not a second.* With gaming a residual State matter, an operator serving users nationwide may need a licence in **every State it reaches**, or must geo-restrict to licensed States. If so, V1's "Nigeria only" scope is itself wrong — the real scope is "Lagos only, licensed", and the business plan's market sizing is overstated by the ratio of Nigeria to Lagos. | Adaeze / Founder | H | H | 🔴 | (1) Counsel Q7.2 — which State's law governs an online operator, and how does one comply with a nationwide user base; (2) Q7.5 — whether a staged single-State launch is available; (3) geo-restriction treated as a V1 engineering requirement pending the answer, not a V2 concern; (4) revenue model re-forecast against a single-State market before any funding conversation. | Counsel Q7.2/Q7.5; other States' remote-gaming regulations; peer-operator multi-State practice. | Weekly until Q7 answered; then monthly |
| **R-REG-03** | **NDPA 2023 compliance gaps** — Atlas launches without proper NDPC registration, DPO appointment, or DPIA, exposing it to enforcement and blocking KYC/payment vendor onboarding (both require controller status). | Adaeze / Founder | M | H | 🔴 | Counsel Q4; NDPC registration in Phase 0; DPO named before Phase 3; DPIA before first real-money draw. | NDPC registration status; DPO named; DPIA signed off. | Monthly |
| **R-REG-04** | Tax mishandling on prize payouts (WHT rate wrong, remittance late, VAT position wrong) → FIRS enforcement + winner disputes. | Adaeze + Backend Engineer / Finance Lead | L | H | 🟡 | Counsel Q3; `tax_payable` ledger account (ADR-003) reserved from day one; reconciliation includes tax accrual verification; finance lead sign-off on payout tax mechanics before first real-money draw. | Nightly reconciliation report; first-real-payout audit. | Monthly |
| **R-REG-05** | Marketing copy inadvertently uses regulated terms ("lottery", "raffle") in a channel that survives — e.g. WhatsApp template message, influencer post, out-of-home ad — triggering NLRC attention regardless of Q1 outcome. | Adaeze + Frontend / Compliance Lead | M | M | 🟡 | Copy-ban is codified in `docs/compliance/copy/`; every consumer-facing copy change reviewed by Adaeze; influencer contracts include copy-restriction clause with liquidated damages; quarterly copy audit across all live channels. | Monthly copy audit; influencer-post spot-check; complaint intake. | Monthly |
| **R-REG-06** | Responsible-play stance (permanent self-exclusion, no reversal) is later declared over-restrictive by regulator or challenged by an excluded user in court, forcing a reversal mechanism to be built retroactively. | Adaeze + Backend / Founder | L | M | 🟢 | Counsel Q6; document Atlas's stance publicly with reasoning grounded in responsible-play literature; be ready to introduce a vetted cool-off reversal as V2 if needed. | Complaint intake; regulator statements; peer-operator practice. | Quarterly |
| **R-REG-07** | Cross-state operation as V2 regional expansion begins triggers licensing obligations in multiple new jurisdictions (Ghana, Kenya, SA, Rwanda, Uganda, Tanzania) that Atlas has not scoped. | Adaeze / Founder | H | M | 🔴 | Each V2 country gets its own regulatory workstream *before* engineering work begins; regional expansion plan does not commit publicly until per-country legal opinion is secured. | V2 planning gate; country-by-country counsel engagement. | Quarterly (V1); monthly once V2 planning begins |
| **R-REG-08** | **Consumer-facing copy ships ahead of implementation.** Three live instances found 2026-11-23/24, all pre-existing and none caught by CI: permanent self-exclusion described with no `self_exclusions` table (ADR-010 approved 2026-07-02, never built); free-entry route advertised with no leased P.O. box (R-FREE-01, REVIEW-001 §6.1, open since July); age verification claimed "at every purchase" with no check in the purchase path. Consequence: demonstrable misstatement to consumers, independent of any classification question — the form of exposure that does not need a regulator to find it, only a complainant. | Adaeze / Founder | H | H | ⚫ | (1) All three corrected or removed (REVIEW-002 §6, Addendum A.3); (2) standing requirement per Addendum A.4 — no claim about a control, protection, or entry route ships unless implementing code exists AND a test asserts it; (3) mechanised copy-to-capability gate requested from 🧪 Murat, modelled on the ADR-002 outbox gate; (4) ADR-010 moved to Phase 3 critical path. | Any consumer surface describing a control; CI gate once built; my review of every copy diff. | Weekly until the gate exists; then per copy change |
| **R-REG-09** | ~~Skill question is the sole classification mechanism and does not meet the standard this office set.~~ **CLOSED 2026-11-26.** The skill question was removed (AMEND-003). A control that does not exist cannot fail a standard, and the founder accepted Atlas's own Q1.5 hypothesis — that it achieved nothing under the governing State law — rather than paying its conversion cost while waiting for counsel to say so. REVIEW-001 §3.1/§3.2 remediation is moot; `docs/compliance/skill-questions.md` is **cancelled, not overdue**. Superseded by R-REG-11. | Adaeze / Founder | — | — | ✅ closed | Closure is not mitigation: Atlas now relies on nothing but the licence. See R-REG-11. | — | Closed |
| **R-REG-11** | **Operating, or preparing to operate, without the licence the model now depends on.** Atlas has removed both carve-out mechanics (free route 2026-11-23, skill question 2026-11-26) and is pursuing a State gaming licence instead. That is a more honest posture than relying on mechanics the 2026-11-23 research indicates are legally inert — but it concentrates the entire legal basis into a single artefact Atlas **does not yet hold**, with no fallback argument if the application is refused, delayed, or priced beyond reach. The founder is pursuing the licence separately. | Adaeze / Founder | H | C | ⚫ | (1) PRD §1 hard prerequisite — no real payment rail before sign-off; (2) **extended by AMEND-001 §2.2 to bar public marketing spend**, since advertising an unlicensed scheme may itself be an offence; (3) counsel Q7.4 — whether a proportionate permit exists — remains the highest-leverage unknown; (4) no engineering may assume a licence outcome. | Licence application status; counsel Q7/Q1; any State enforcement against a remote operator. | Weekly until the application is filed and counsel has reported |
| **R-REG-10** | **The register's governing statute was void for twelve months before anyone noticed.** NLA 2005 was nullified by the Supreme Court on 22 Nov 2024 (*AG Lagos v AG Federation*, SC/1/2008); lottery/gaming is now exclusively a State matter and the NLRC holds no national licensing authority. R-REG-01, R-REG-02 and §8 were all framed against a federal statute and a federal regulator. The scoped desk research that would have caught this (`research/domain-nigerian-prize-competition-licensing-research-2026-06-30.md`) was never run — `stepsCompleted: []`. | Adaeze / Founder | H | C | ⚫ | (1) Research run 2026-11-23, report at `research/nigerian-draw-classification-research-2026-11-23.md`; (2) R-REG-01/02 and §8 require rescoring against Lagos State Lotteries and Gaming Authority Law 2021 — **not yet done**; (3) counsel brief Q1/Q5/Q7 rewrite before transmission; (4) engage Lagos gaming counsel, reframed from carve-out validation to licensing pathway and viability at reported cost (₦250–400m year one, unverified). | Any further Supreme Court or State legislative movement; Central Gaming Bill reintroduction; counsel engagement status. | Weekly until counsel engaged |

---

## 2. Financial and operational risks

| ID | Risk | Owner | L | I | Score | Mitigation | Monitoring signal | Review |
|---|---|---|---|---|---|---|---|---|
| **R-FIN-01** | **Ledger integrity break** — a bug produces a state where the double-entry ledger and the derived balance disagree, or a transaction fails to balance. Consequence: at best refund confusion, at worst missing/duplicated funds. | Backend Engineer + Adaeze / EL + Finance Lead | L | C | ⚫ | ADR-003 invariants enforced at DB level (transaction-balance trigger; append-only revocation of UPDATE/DELETE; no `balance` column); nightly reconciliation against Paystack settlement; two-approval gate on every Wallet & Ledger PR; integration tests use real Postgres, no mocks. | Nightly reconciliation report; ledger integrity CI job; Sentry ledger errors. | Weekly (pre-launch), then monthly |
| **R-FIN-02** | Paystack reconciliation drift beyond tolerance — either implementation bug, Paystack settlement lag, or refund handling breaks the daily match. | Backend Engineer + DevSecOps / Finance Lead | M | H | 🔴 | Nightly reconciliation job; tolerance threshold in `docs/qa/strategy.md`; SEV-1 alert on any breach; Compliance review of every breach. | Nightly reconciliation report | Monthly |
| **R-FIN-03** | Winner unable to claim prize within contact window (14-day per PRD §3.6) → prize passes to reserve; if all reserves exhausted, prize rolls to next equivalent draw. Risk: reserve-cascade produces reputational damage if flagship prizes recycle repeatedly. | Adaeze + Frontend / Ops Lead | M | M | 🟡 | Multi-channel winner contact (WhatsApp + email + phone); 14-day window generous relative to peer operators; reserve algorithm publishes ordered list from same seed (ADR-006); if cascade occurs, transparent disclosure on draw page. | Prize claim completion rate KPI; time-to-first-contact; cascade incidence. | Monthly |
| **R-FIN-04** | Prize fulfilment for vehicle prizes fails operationally (dealer partnership breakdown, title transfer bureaucratic delay, insurance gap during handover). | Adaeze + Ops / Founder | M | M | 🟡 | Vehicle prizes are V1's flagship — dealer partnership needs to be locked with SLA before first vehicle-prize draw; title-transfer process documented and tested with a mock claim before public draw. | Vehicle-prize partnership contract status; dry-run of end-to-end vehicle handover. | Monthly (V1); quarterly (post-launch) |
| **R-FIN-05** | Refund flow bug causes over-refund or double-refund → net loss + user confusion. | Backend Engineer + Adaeze / Finance Lead | L | M | 🟢 | ADR-004 idempotency on refund operations; refunds require operator initiation in V1 (no user-triggered refunds); two-approval gate on Payment module PRs. | Refund count vs Paystack refund-issued count; ledger `refund_payable` net position. | Monthly |
| **R-FIN-06** | Escheatment of un-refundable wallet balances (from self-excluded users beyond 90-day refund window) sits unresolved because escheatment policy is not written. | Adaeze / Founder | M | L | 🟢 | Escheatment policy in `docs/compliance/escheatment-policy.md` drafted in Phase 0 per ADR-010 mitigation note. | Escheatment policy file exists and is legal-reviewed. | Quarterly |

---

## 3. Vendor risks

| ID | Risk | Owner | L | I | Score | Mitigation | Monitoring signal | Review |
|---|---|---|---|---|---|---|---|---|
| **R-VEN-01** | **Paystack outage during a live draw** — payment rail unavailable while draw is open for sales, either blocking entries or corrupting in-flight intents. | DevSecOps + Backend / EL | M | H | 🔴 | Paystack status page monitored; runbook `docs/runbooks/payment-outage.md` written and drilled; V2 adds Flutterwave as fallback rail (trigger: Paystack downtime > 4 hrs cumulative in a month, or user demand); user-facing UX gracefully surfaces "payments temporarily unavailable" without failing tickets already issued. | Paystack status page; payment success rate < 95% for 10 min → SEV-2. | Weekly (post-launch), then monthly |
| **R-VEN-02** | KYC vendor (selection TBD Phase 0) mis-verifies a winner — either false approval (grants prize to fraudulent claimant) or false rejection (blocks legitimate winner). | Adaeze + Backend / EL | M | H | 🔴 | Vendor selection process weights on false-positive/negative rates and manual-override path (ADR-007); Adaeze reviews every manual override; two-vendor fallback in V2 for cross-verification of high-value winners. | Manual override rate; verified-user complaint rate; prize-claim rejection rate. | Monthly |
| **R-VEN-03** | KYC vendor unilaterally changes API, pricing, or data-handling terms mid-engagement, forcing rebuild or renegotiation. | DevSecOps + Adaeze / Founder | M | M | 🟡 | Adapter pattern (ADR-007) insulates code; contract terms include 90-day notice on material changes; V2 second-vendor optionality preserved. | Vendor communication; contract review cadence. | Quarterly |
| **R-VEN-04** | Managed platform (Fly/Railway/Render/App Runner — pick deferred to Phase 5 entry per 2026-07-02 pivot) has an outage during a live draw close or reveal window, halting a real-money draw mid-lifecycle. | DevSecOps / EL | L | H | 🟡 (not-yet-applicable during Phase 2 V0.5 — no cloud) | Platform SLA verified before commit; runbook `docs/runbooks/platform-outage.md`; draw lifecycle designed so *close* and *reveal* are separate operator actions — a platform outage between them delays reveal but doesn't corrupt state; backup restore drilled. | Platform status page; uptime monitoring on `/healthz`. | Monthly (from Phase 5 entry onwards) |
| **R-VEN-05** | WhatsApp Business API provider suspends Atlas's account (Meta template policy violation, complaint volume, or Meta policy change targeting prize-platform operators). | Adaeze + DevSecOps / Founder | M | M | 🟡 | Template messages pre-approved with Meta; copy pre-reviewed by Adaeze; email fallback for winner notifications; a per-user quiet-hours policy to reduce complaint likelihood. | Meta account status; complaint rate on WhatsApp channel. | Monthly |
| **R-VEN-06** | Public entropy source failure — Bitcoin block explorer(s) or drand endpoint unavailable at the exact reveal time of a draw, forcing postponement. | DevSecOps + Backend / EL | L | M | 🟢 | Two-source combination (ADR-006) means one source failing is tolerable; three block-explorer providers configured with the first two required to match; runbook `docs/runbooks/draw-entropy-unavailable.md`; postponement is graceful (publish new reveal time; commitment remains valid). | Reveal-time entropy fetch success rate. | Monthly (per draw) |

---

## 4. Technical risks

| ID | Risk | Owner | L | I | Score | Mitigation | Monitoring signal | Review |
|---|---|---|---|---|---|---|---|---|
| **R-TEC-01** | **Draw engine integrity break** — winner-selection algorithm produces different result on replay than on live run, undermining the "provably fair" claim and creating fraud allegation surface. | Backend Engineer + Adaeze / EL + Compliance Lead | L | C | ⚫ | ADR-006 protocol is deterministic and specified byte-for-byte; verifier script (`backend/tools/verify_draw.py`) published; integration test replays every completed draw in CI and asserts identical winner; Compliance & Risk Agent reviews every real-money draw's proof before public announcement. | Draw replay CI job pass rate (must be 100%); post-draw proof verification by Adaeze. | Weekly during launch; then per-draw |
| **R-TEC-02** | Audit-log chain integrity break — hash chain broken by an unexpected DB event (manual DBA action, corruption, replication error), invalidating the tamper-evidence guarantee. | Backend Engineer + DevSecOps / EL | L | H | 🟡 | INSERT-only application role; trigger verifies chain on every insert; nightly chain-verification job; break is SEV-1 → Compliance triage; periodic export to S3 object-lock for anchoring. | Nightly chain verification; alert on any break. | Weekly |
| **R-TEC-03** | Idempotency race under high concurrency — Paystack sends duplicate webhooks for the same payment intent in a burst, both processed before the idempotency record is written, resulting in double-crediting. | Backend Engineer + QA / EL | L | H | 🟡 | ADR-004 idempotency table + unique index at both application and DB layer; QA critical journey #8 covers concurrent double-click; Paystack webhook secret verified before any DB write; load test in Phase 4 exercises this specific scenario. | Ledger reconciliation; duplicate-webhook incidence in Sentry. | Monthly |
| **R-TEC-04** | Self-exclusion enforcement bypass — user re-registers with a different BVN (identity fraud), or the pepper hash fails to catch a match due to normalisation bug. | Adaeze + Backend / Compliance Lead | L | M | 🟢 | Normalisation logic covered by unit tests; the deeper mitigation is that identity fraud with a different BVN is a criminal act with high friction (ADR-010); pepper is stored in secret manager with restricted access. | Self-exclusion match-hit rate vs KYC volume; Sentry errors on the exclusion-check path. | Quarterly |
| **R-TEC-05** | OpenAPI-generated client drift — server changes an endpoint's contract without regenerating clients; mobile/admin start hitting the wrong shape in production. | Backend Engineer + Frontend + QA / EL | M | M | 🟡 | CI regenerates clients on every OpenAPI change; contract tests fail the build if server drifts; Solution Architect ownership of the spec; QA contract test covers every implemented route. | Contract test pass rate; client-regeneration CI job. | Monthly |
| **R-TEC-06** | Migration failure in production — Alembic migration fails mid-application, leaving DB in inconsistent state. | Backend Engineer + DevSecOps / EL | L | H | 🟡 | Every migration reviewed by EL before it runs against staging (ADR-009); staging migration must pass before production; blue-green deploy allows rapid revert; backup restore drilled. | Migration outcome logging; staging vs production schema divergence check. | Monthly |
| **R-TEC-07** | Legacy `main.py` PyCharm boilerplate at repo root confuses a new engineer or gets deployed. | DevSecOps / EL | L | L | 🟢 | Removed in Phase 2 cleanup per `delivery-framework.md §6`. | File existence in main branch after Phase 2 exit. | Once (Phase 2 exit) |

---

## 5. Security risks

| ID | Risk | Owner | L | I | Score | Mitigation | Monitoring signal | Review |
|---|---|---|---|---|---|---|---|---|
| **R-SEC-01** | **BVN pepper compromise** — the peppered SHA-256 secret used for self-exclusion lookups (ADR-010) is leaked, allowing an attacker to enumerate excluded users by BVN. | DevSecOps + Adaeze / EL | L | H | 🟡 | Pepper in platform secret manager, restricted to worker + API roles; never logged, never in code, never in CI artefacts; gitleaks in CI; pepper is not rotated (rotation would invalidate registry — ADR-010) so mitigation is prevention, not recovery. | Secret manager audit log; secret-scanning CI job. | Monthly |
| **R-SEC-02** | **Server-seed leakage before reveal** — if the encrypted server seed for a live draw is decrypted or leaked before its scheduled reveal, an attacker could predict the winner and buy the winning ticket. | Backend Engineer + DevSecOps + Adaeze / EL + Compliance Lead | L | C | ⚫ | Server seed encrypted at rest with envelope key in secret manager (ADR-006); decrypt permission granted only to the worker process at reveal time; envelope key access audit-logged; no operator role can decrypt. | Secret manager access log; audit-log `draw.revealed` events. | Weekly during launch, then monthly |
| **R-SEC-03** | Paystack webhook signature bypass — attacker forges a webhook to trigger credit without payment. | Backend Engineer + DevSecOps / EL | L | H | 🟡 | HMAC verification on every webhook body before any parsing (ADR-008); webhook secret in secret manager; integration test with invalid signature must return 401. | Webhook rejection rate; Sentry webhook errors. | Monthly |
| **R-SEC-04** | KYC document exfiltration — an attacker gains access to S3 objects containing user identity documents. | DevSecOps + Adaeze / EL + Compliance Lead | L | H | 🟡 | S3 bucket private; access via time-bound signed URLs only; bucket policy denies public access; KMS encryption at rest; access logging enabled; quarterly access-log audit by Adaeze. | S3 access logs; unusual object-fetch patterns. | Monthly |
| **R-SEC-05** | Session hijacking / token theft on an operator account with sensitive permissions (KYC override, refund issue, draw commit). | DevSecOps + Backend / EL | L | H | 🟡 | MFA mandatory on all operator accounts (ADR-009); session anomaly detection; RBAC least-privilege; every sensitive permission use audit-logged. | Sensitive-permission-use audit; MFA challenge rate. | Monthly |
| **R-SEC-06** | Third-party dependency (Python package, Docker base image) ships a critical vulnerability that lands in production. | DevSecOps / EL | H | M | 🔴 | Dependency scan + Trivy container scan in CI, fail-build on critical/high; monthly patch cycle; SBOM per image; on-call rotation reads security advisories weekly. | Scan reports; time-to-patch after CVE disclosure. | Weekly |
| **R-SEC-07** | Botnet / DoS attack on the draw close moment (attacker aims to flood the close window and produce inconsistent ticket-list hash). | DevSecOps + Backend / EL | L | H | 🟡 | Rate limiting at platform edge; the entries-snapshot happens at close time server-side (attacker cannot manipulate a snapshot taken after sales stop); scaling headroom for peak-second close windows; runbook for volumetric events. | Request rate at close moments; error rate spike at close. | Monthly |

---

## 6. Product and market risks

| ID | Risk | Owner | L | I | Score | Mitigation | Monitoring signal | Review |
|---|---|---|---|---|---|---|---|---|
| **R-PRD-01** | Consumer trust incident — an early winner alleges impropriety, an audit finds a discrepancy, or a viral social-media narrative frames Atlas as "just a lottery." Consequence: user acquisition stalls, cost per install spikes, existing users churn. | Frontend + Adaeze + Founder / Founder | M | H | 🔴 | Provably-fair proof publication on every draw (ADR-006); transparent claim journey; incident-communications template ready pre-launch (`delivery-framework.md §10`); social monitoring; response-team on standby for launch week. | Social sentiment; support ticket theme mix; press mentions. | Weekly at launch; then monthly |
| **R-PRD-02** | First flagship draw (vehicle prize per delivery-framework Phase 3) undersells — insufficient paid entries relative to prize value → unit economics negative + reputational hit. | Frontend + Adaeze + Founder / Founder | M | H | 🔴 | Beta draw (Phase 3 week 17) proves funnel first with small cash prize; flagship draw sizing based on beta conversion data + a floor entries threshold below which draw is postponed (transparently) rather than run underwater. | Entries vs breakeven curve during sale window. | Per draw (post-launch) |
| **R-PRD-03** | Competitor emerges in Nigeria copying the prize-competition model, potentially with a licensed-lottery legal structure that makes them harder to challenge on trust grounds. | Adaeze + Founder / Founder | M | M | 🟡 | Continuous competitive monitoring (Mary picks this up as a rolling market-research assignment); trust-first positioning is the moat, not the mechanic; V2 features (subscriptions, loyalty, referrals) are the retention layer that a copycat can't fast-follow. | Market watch; App Store new-entrant scanning. | Monthly |
| **R-PRD-04** | Nigerian consumer payment preferences shift (e.g. USSD adoption spikes, Paystack loses share to Moniepoint) → Atlas's Paystack-only V1 leaves conversion on the table. | Backend + Adaeze / Founder | L | M | 🟢 | ADR-008 payment vendor adapter is designed for multi-rail from day one; V2 second rail trigger tied to Paystack downtime OR user demand; monthly payment method mix report post-launch. | Payment method mix; Paystack failure rate; drop-off at payment step. | Monthly |
| **R-PRD-05** | KPI targets in PRD §5 (TODOs pending founder input) are unrealistic once set — either too aggressive (team demoralisation) or too conservative (weak Series A story). | John + Founder / Founder | M | M | 🟡 | KPI targets committed before Phase 1 exit per delivery-framework; John reviews against comparable operator benchmarks; reset at each phase gate if reality diverges materially. | KPI dashboard vs target; monthly variance report. | Monthly |
| **R-PRD-06** | **V0.5 investor demo underperforms** — bugs, wrong story, fails to land the trust proof, crashes on Zoom, or takes too long from `docker compose up` to first meaningful frame. Consequence: fundraising cycles slip, hires wait, counsel-demo purpose also compromised. Demo is now on the fundraising critical path per 2026-07-02 pivot. | Sally + Amelia + Tobi + Founder / Founder | M | H | 🔴 | (1) Scope kept deliberately tight (`v0.5-demo-plan.md §2` vs §3); (2) 20+ rehearsals with founder before any external showing; (3) screen-recording of hero flow as fallback for demos where live sharing fails; (4) success gates in `v0.5-demo-plan.md §6` gate demo readiness; (5) every demo shortcut ticketed for V1 removal at time of introduction so shortcuts don't harden into design. | Rehearsal count; number of open demo-blocking bugs; time-to-first-meaningful-frame on clean laptop; investor-feedback theme mix post-demo. | Weekly during Phase 2 build |
| **R-PRD-07** | **Demo shortcuts harden into V1 design.** V0.5 uses stubs (KYC manual approve, WhatsApp skipped, RBAC 2-role) that are architecturally acceptable for demo but not for launch. Risk: "it worked in the demo" becomes an argument for skipping the real V1 work in Phase 3. | Amelia + Adaeze / EL | M | M | 🟡 | Every V0.5 shortcut is documented and ticketed at time of introduction; ticketed items are Phase 3 exit blockers; ADR-001 V0.5 addendum explicitly names what remains stubbed and where it is replaced. | Ticketed shortcut count vs closed-in-Phase-3 count; Phase 3 exit checklist enforcement. | Weekly during Phase 3 |

---

## 7. Organisational and delivery risks

| ID | Risk | Owner | L | I | Score | Mitigation | Monitoring signal | Review |
|---|---|---|---|---|---|---|---|---|
| **R-ORG-01** | Small team → key-person risk. The named Engineering Lead becomes unavailable (health, departure) mid-Phase 3 build. | Founder | L | H | 🟡 | Documentation discipline is high (ADRs, runbooks, AI Integration Log) so replacement onboarding is faster than average; identify a backup EL candidate before Phase 3 starts; consider fractional CTO advisor. | EL availability; documentation coverage per module. | Quarterly |
| **R-ORG-02** | AINE agent invocation goes wrong at scale — an agent produces a plausible-but-incorrect artefact, and the human approver signs off without catching it. | All agents / EL | M | M | 🟡 | Human-approval gates on everything irreversible (`AINE-AGENTS.md §6`); adversarial verification on flagship outputs (§8); AI Integration Log; weekly retro reads the log's flagged items. | AI Integration Log; PR revert rate; incident post-mortems. | Weekly |
| **R-ORG-03** | Founder time overrun — S1408661 becomes bottleneck on decisions (vendor picks, ADR approvals, phase-gate sign-offs), causing programme slippage. | Founder | H | M | 🔴 | Delegate ADR sign-off for non-money/non-draw ADRs to EL; batch decision reviews weekly; agents pre-cook decision matrices with recommendations so founder is confirming not researching. | Weekly velocity vs plan; blocked-on-founder ticket count. | Weekly |
| **R-ORG-04** | Customer support at launch is under-resourced — ticket volume in first week overwhelms one person, quality suffers, brand takes hit. | Founder + Adaeze | M | M | 🟡 | Support staffing plan finalised in Phase 6 launch checklist; two-person coverage for launch week minimum; response-time SLA with escalation ladder; template answers pre-drafted for the top-20 predictable questions. | Support response time; ticket volume vs staffing. | Weekly at launch |
| **R-ORG-05** | On-call rotation gap — an SEV-1 fires (e.g. ledger reconciliation mismatch) outside working hours and nobody responds. | DevSecOps / EL | L | H | 🟡 | On-call rotation named in Phase 6 checklist; PagerDuty or equivalent; escalation ladder documented in runbooks. | On-call rotation coverage %; SEV-1 response time. | Monthly |
| **R-ORG-06** | The 7 custom subagents I deleted from `.claude/agents/` reappeared as available agent types — origin unknown. Risk: an agent invocation uses a stale definition that duplicates or conflicts with a BMad-registered agent. | DevSecOps + EL | L | L | 🟢 | Tracked as a housekeeping item — locate registration source, remove or align with BMad. Non-blocking. | Agent-type list divergence from `_bmad/config.toml` + `_bmad/custom/config.toml`. | Once (housekeeping) |
| **R-ORG-07** | **Two-approval gates operated by a single human (founder wearing EL + Finance Lead + Compliance Lead hats)** during pre-hire period. Consequence: approval intent (two independent heads catching each other's mistakes on money and trust-critical designs) is degraded to procedural sign-off. Applies to ADR-003, ADR-005, ADR-006, ADR-008, ADR-010 and to any Wallet & Ledger, Payment, or Draw Engine PR merged during the solo-founder period. | Founder | H | M | 🔴 | (1) As soon as a second engineer / operator is hired, they take the second-approver seat on money and draw decisions; (2) historical approvals from the solo-founder period are re-reviewed by the second hire and re-approved (or amended) where practical before any real-money draw runs; (3) any material design choice affecting money or draws made during the solo-founder period is flagged in the ADR footer with a "re-review at first hire" marker. | New-hire onboarding checklist item; count of ADRs / PRs marked "re-review at first hire" pending re-approval. | On every hire; quarterly otherwise |

---

## 8. Legal-opinion-outcome risks (Plan B thinking)

This section anticipates the counsel-opinion outcomes and pre-thinks Atlas's response. Written now — before the opinion is commissioned — so that a rejection or unexpected finding on any question doesn't leave the programme flat-footed.

> **Rescored 2026-11-24 (⚖️ Adaeze).** §8 was written on 2026-07-01 against a federal regime. The National Lottery Act 2005 was nullified by the Supreme Court on 22 November 2024 and lottery/gaming is now exclusively a State matter, so **the federal licensing path §8.1 treated as its primary fallback no longer exists.** §8.1 and §8.4 are rewritten below. §8.2 and §8.3 are unaffected — AML and data-protection obligations do not turn on the lottery classification.
>
> One structural correction worth stating: §8 was built around *"if counsel rejects the model."* On the 2026-11-23 research, there is no carve-out in the governing State law to be rejected *from*. The question is no longer whether Atlas survives a classification test; it is which licence Atlas needs and whether the business is viable at that price. §8.1 is reframed accordingly.

### 8.1 If Q1/Q7 confirm Atlas requires a State gaming licence

**Rewritten 2026-11-24.** The 2026-07-01 version of this subsection assumed a federal NLRC licence was available as the fallback. It is not. Treat a licence requirement as the **base case**, not the rejection case.

**Meaning:** counsel confirms that under the governing State law — in Atlas's launch market, the Lagos State Lotteries and Gaming Authority Law 2021 — Atlas's model sits inside the regulated perimeter, and no mechanic (skill question, free entry route, or both) removes it.

**Plan B options, reordered for the post-2024 position:**

1. **Pursue the Lagos State licence and geo-restrict to Lagos at launch.** Was option 3; now the primary path. Reported cost (unverified, counsel Q7.3 to confirm): ~₦100m/yr per category, ~₦150m initial, ₦100m share capital, ₦100m bank guarantee, plus GLI/BMM technical certification — order ₦250–400m in year one. Timeline +3–6 months at best. **This is the option that decides whether Atlas exists in its current form**, because that cost against a pre-revenue startup is a different financing conversation, not a compliance line item.
2. **Seek a promotional-competition permit or lighter-touch registration**, if one exists distinct from a full gaming licence (counsel Q7.4). Atlas's research could not establish whether it does. **This is the single highest-leverage unknown in the entire engagement** — a cheap permit and a ₦250m licence are different businesses. Everything else in this list should be deferred until Q7.4 is answered.
3. **Staged or limited launch** — single State, capped prize value, invite-only beta — lawful at smaller scale while a full licence is pursued (counsel Q7.5). Unknown whether available; worth asking because it preserves momentum.
4. **Pivot to a genuine promotional competition tied to a product purchase.** Requires a primary product Atlas does not sell. Effectively a different business, and the Lagos Law expressly classes promotional competitions as "Other lotteries" — so this may not even relocate Atlas outside the perimeter. Lower in the order than it was.
5. **Abandon Nigeria for a different launch market** (Ghana, Kenya, SA). Rises in appeal relative to 2026-07-01 purely because the Nigerian cost base may be prohibitive. **Caveat: Atlas has done no regulatory research on any of those markets.** Treat as an unknown, not an escape hatch — the Nigerian position was also assumed benign for five months.
6. ~~Redesign to strengthen the prize-competition case.~~ **Struck.** Was option 1. If the governing definition requires only chance and a prize, there is no design change that moves Atlas outside it, and spending engineering effort on a harder skill question or a better free route would be motion without progress. Reinstate only if counsel identifies genuine design conditions (Q1.4, Q1.6).
7. ~~Pursue federal NLRC lottery licence.~~ **Struck — no longer available.** The NLRC holds no national licensing authority following SC/1/2008, and the Central Gaming Bill 2025 did not receive assent.

**Plan B trigger, revised.** The old trigger keyed off the *strength* of counsel's rejection. The new trigger keys off **cost and availability**: if Q7.4 reveals a proportionate permit, take it. If only a full licence is available, the founder decides between option 1 (raise and license), option 3 (staged launch if available) and option 5 (relocate) on an evidence pack I produce the day the opinion lands — including a funding requirement, because option 1 is not self-fundable from a standing start.

**What does not change:** PRD §1's hard prerequisite stands in every branch. No code touches a real payment rail before counsel sign-off. And the two commercial gatekeepers (Paystack's prohibited-business terms; Google Play's real-money-gambling policy) bind on licence evidence regardless of which option is chosen — a licence is the unlock for distribution as much as for legality.

### 8.2 If Q2 imposes higher AML burden than assumed

**Likely form:** Atlas classified as a "DNFBP" or analogous under NFIU, requiring formal compliance programme, appointed MLRO, ongoing STR reporting.

**Response:** MLRO named before Phase 3 exit; STR reporting workflow built into admin app before beta draw; annual AML training scheduled. Modest programme impact.

### 8.3 If Q4 (NDPA) finds tension with append-only audit log

**Likely form:** counsel concludes the immutable audit log violates data-subject erasure rights in some scenarios.

**Response:** hybrid design — PII in audit log is stored as opaque hashes; the plaintext-PII record is separately erasable. ADR-005 amendment required. Timeline: +2–3 weeks of design work.

### 8.4 If Q7 (which regime governs) is confirmed as State-only

**Rewritten 2026-11-24.** Q7 has been promoted to CRITICAL in the counsel brief and is now to be answered **before** Q1. This is no longer a defensive-notification question; it is the question that establishes which law applies at all.

**Response if State-only is confirmed:**

- **Licensing becomes §8.1 option 1**, not a secondary notification step. "Notify LSLGA defensively" is no longer a sufficient response — the Remote Gaming Regulations 2021 appear to require registration and a gaming fee from any remote provider serving a Lagos customer, even where the customer plays free for a chance at a prize.
- **A nationwide user base may require a per-State approach.** Counsel Q7.2 asks how an online operator complies across States — licence per State, lead-State approach, or geo-restriction to licensed States only. If per-State licensing is the answer, Atlas's addressable market at launch is one State, and the V1 plan's "Nigeria only" scope statement is itself wrong: it is "Lagos only, licensed" or nothing.
- **Directors' personal exposure must be established before any launch decision** (counsel Q7.6). Penalties for unlicensed operation are reported as criminal — minimum ₦5m and up to 3 years, ₦10m for unregistered remote providers. The founder is sole director. That is a personal-risk disclosure, not a corporate one, and it should be in front of the founder before, not after, a launch call.
- **Advertising exposure may precede operating exposure.** If promoting an unlicensed scheme is itself an offence (counsel Q5.1), then pre-launch marketing — not the first paid entry — is the point at which risk begins. Any marketing spend before the opinion lands should be treated as carrying that risk.

**V2 expansion implication:** R-REG-07 was scored on the assumption of per-country regulatory workstreams for regional expansion. It now also needs per-State workstreams *within* Nigeria. That is a material scope increase to a risk already scored 🔴, and R-REG-07 should be rescored at the next review.

---

## 9. Aggregate risk posture

**Current heat map:**

| Score | Count | IDs |
|---|---|---|
| ⚫ Catastrophic | 3 | R-REG-01, R-FIN-01, R-TEC-01, R-SEC-02 (4 — count corrected) |
| 🔴 High | 9 | R-REG-02, R-REG-03, R-REG-07, R-FIN-02, R-VEN-01, R-VEN-02, R-SEC-06, R-PRD-01, R-PRD-02, R-ORG-03 (10 — count corrected) |
| 🟡 Medium | ~14 | Distributed |
| 🟢 Low | ~7 | Distributed |

*(counts are rough — the register is a working document, not audit-graded, at Phase 0)*

**Concentration:** the ⚫ catastrophic risks cluster around three axes: **regulatory classification (R-REG-01)**, **financial integrity (R-FIN-01)**, and **draw fairness (R-TEC-01, R-SEC-02)**. This is exactly the risk shape Atlas's architecture was designed to survive — double-entry ledger, hash-chained audit, commit-reveal draws, prize-competition mechanics. The register is telling us the design is aimed at the right threats. It also tells us the counsel engagement (R-REG-01 mitigation) is the highest-leverage single investment in Phase 0.

**Top-3 monitoring signals to instrument before any real-money draw runs:**
1. Nightly ledger reconciliation report.
2. Nightly audit-log chain-verification job.
3. Payment success rate + reconciliation drift alerts.

If any of these three cannot run reliably, the launch date does not hold.

---

## 10. Review cadence and change log

- **Weekly:** DevSecOps runs the automated risk checks (reconciliation, chain verification, dependency scan) and reports exceptions to EL.
- **Monthly:** Adaeze reviews the register in full with EL; changes logged in AI Integration Log.
- **Quarterly:** Founder reviews the register and re-scores; any ⚫ catastrophic escalated to board.
- **Ad hoc:** any new information (counsel opinion delivered, vendor decision made, phase gate advanced) triggers a targeted review of the affected risks within one week.

### Change log

| Date | Change | Agent | Human reviewer |
|---|---|---|---|
| 2026-07-01 | Register established at draft status; 40+ risks populated from PRD, ADRs, counsel engagement brief, delivery framework | 📊 Mary | pending EL + Founder |
| 2026-07-02 | R-REG-01 updated: founder-committed to prize-competition model as Atlas's design; risk remains ⚫ pending counsel confirmation; Q1 reframed as confirmation ask | 🛡️ Tobi | Founder (self-noted) |
| 2026-07-02 | Demo-first pivot: R-VEN-04 posture note added (not-yet-applicable during Phase 2 V0.5); R-PRD-06 added (V0.5 demo underperforms, 🔴); R-PRD-07 added (demo shortcuts harden into V1, 🟡). Reflects founder decision to defer managed-platform commitment and build local demo first. See `_bmad-output/planning-artifacts/v0.5-demo-plan.md`. | 🛡️ Tobi | Founder (self-noted) |
| 2026-07-02 | Founder confirmed as Engineering Lead. All 12 V1 ADRs status Proposed → Approved (S1408661 sole approver; two-approval ADRs 003/005/006/008/010 record founder wearing second-approver hat pre-hire). New R-ORG-07 added (🔴) — two-approval gates operated by single human is a governance shortcut with a defined un-shortcutting path at first hire. Amelia now unblocked to start V0.5 build per V0.5 demo plan. | 🛡️ Tobi | Founder (self-noted as EL) |
| 2026-11-24 | **R-REG-08/09/10 added, all ⚫.** Free-entry route unwired 2026-11-23 (founder Tier 3 decision) — REVIEW-002. R-FREE-01 surfaced from REVIEW-001 §6.1: the free route was never operable, no P.O. box was ever leased. R-FREE-01 and R-SKILL-01 had been recorded only inside a Day-9 wireframe and never entered this register — my omission, now closed. R-REG-01, R-REG-02 and §8 are **stale**: they are framed against the National Lottery Act 2005, which the Supreme Court nullified in November 2024. Rescoring against Lagos State law is outstanding and should not wait on counsel. | ⚖️ Adaeze | pending Founder |
| 2026-11-26 | **Founder decisions: skill question removed (AMEND-003); free entry route confirmed not returning; State licence pursued separately.** R-REG-09 **CLOSED** — no skill question remains to fail a standard, and `docs/compliance/skill-questions.md` is cancelled rather than overdue. **R-REG-11 opened ⚫** — Atlas now has no carve-out argument at all and its entire legal basis is a licence it does not yet hold, with no fallback if refused or priced out. I record that this is a *more honest* posture than the one it replaces, and a more concentrated risk. R-REG-01's mitigation set is unchanged but its character has shifted: the answer is no longer "defend the classification", it is "hold the licence". | ⚖️ Adaeze | pending Founder |

---

📊 *End of register. Mary handing off ongoing ownership to Adaeze (Compliance & Risk) per `docs/AINE-AGENTS.md §3` — Mary populates in Phase 0; Adaeze maintains from Phase 1 onwards.*
