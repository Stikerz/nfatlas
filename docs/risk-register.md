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

These are the load-bearing risks. Q1 of the counsel engagement (`legal/counsel-engagement-brief.md`) exists to resolve most of them.

| ID | Risk | Owner (agent / human) | L | I | Score | Mitigation | Monitoring signal | Review |
|---|---|---|---|---|---|---|---|---|
| **R-REG-01** | **NLRC classifies Atlas's prize-competition model as a lottery**, requiring an NLRC licence Atlas doesn't hold. Consequence: launch halt, potential enforcement, brand damage. **Founder-committed to the prize-competition model as Atlas's design on 2026-07-02**; risk remains ⚫ until counsel Q1 confirms and NLRC posture is understood. Founder commitment is a posture change (proceed against this assumption); it is not risk resolution. | Adaeze / Founder | M | C | ⚫ | (1) Counsel engagement Q1 as first-tranche deliverable (now a *confirmation* ask rather than a decide-whether ask); (2) Plan B (§8) drafted before counsel opinion lands so a rejection doesn't leave programme flat-footed; (3) prize-competition mechanics designed to maximise defensibility (documented free-route equality, substantive skill question, copy-ban discipline). | Counsel Q1 verdict; any NLRC public statement or circular mentioning prize-competition operators; any peer-operator enforcement action. | Weekly until Q1 opinion delivered; then quarterly |
| **R-REG-02** | Lagos State asserts separate lottery jurisdiction over Atlas's Lagos-resident users, requiring a second licence or notification even under prize-competition model. | Adaeze / Founder | M | H | 🔴 | Counsel Q7 covers this; pre-launch notification to LSLGA as a defensive measure if counsel recommends. | LSLGA public statements; peer-operator experience; counsel Q7 finding. | Monthly until launch |
| **R-REG-03** | **NDPA 2023 compliance gaps** — Atlas launches without proper NDPC registration, DPO appointment, or DPIA, exposing it to enforcement and blocking KYC/payment vendor onboarding (both require controller status). | Adaeze / Founder | M | H | 🔴 | Counsel Q4; NDPC registration in Phase 0; DPO named before Phase 3; DPIA before first real-money draw. | NDPC registration status; DPO named; DPIA signed off. | Monthly |
| **R-REG-04** | Tax mishandling on prize payouts (WHT rate wrong, remittance late, VAT position wrong) → FIRS enforcement + winner disputes. | Adaeze + Backend Engineer / Finance Lead | L | H | 🟡 | Counsel Q3; `tax_payable` ledger account (ADR-003) reserved from day one; reconciliation includes tax accrual verification; finance lead sign-off on payout tax mechanics before first real-money draw. | Nightly reconciliation report; first-real-payout audit. | Monthly |
| **R-REG-05** | Marketing copy inadvertently uses regulated terms ("lottery", "raffle") in a channel that survives — e.g. WhatsApp template message, influencer post, out-of-home ad — triggering NLRC attention regardless of Q1 outcome. | Adaeze + Frontend / Compliance Lead | M | M | 🟡 | Copy-ban is codified in `docs/compliance/copy/`; every consumer-facing copy change reviewed by Adaeze; influencer contracts include copy-restriction clause with liquidated damages; quarterly copy audit across all live channels. | Monthly copy audit; influencer-post spot-check; complaint intake. | Monthly |
| **R-REG-06** | Responsible-play stance (permanent self-exclusion, no reversal) is later declared over-restrictive by regulator or challenged by an excluded user in court, forcing a reversal mechanism to be built retroactively. | Adaeze + Backend / Founder | L | M | 🟢 | Counsel Q6; document Atlas's stance publicly with reasoning grounded in responsible-play literature; be ready to introduce a vetted cool-off reversal as V2 if needed. | Complaint intake; regulator statements; peer-operator practice. | Quarterly |
| **R-REG-07** | Cross-state operation as V2 regional expansion begins triggers licensing obligations in multiple new jurisdictions (Ghana, Kenya, SA, Rwanda, Uganda, Tanzania) that Atlas has not scoped. | Adaeze / Founder | H | M | 🔴 | Each V2 country gets its own regulatory workstream *before* engineering work begins; regional expansion plan does not commit publicly until per-country legal opinion is secured. | V2 planning gate; country-by-country counsel engagement. | Quarterly (V1); monthly once V2 planning begins |

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
| **R-VEN-04** | Managed platform (Fly/Railway/Render/App Runner — pick TBD Phase 0) has an outage during a live draw close or reveal window, halting a real-money draw mid-lifecycle. | DevSecOps / EL | L | H | 🟡 | Platform SLA verified before commit; runbook `docs/runbooks/platform-outage.md`; draw lifecycle designed so *close* and *reveal* are separate operator actions — a platform outage between them delays reveal but doesn't corrupt state; backup restore drilled. | Platform status page; uptime monitoring on `/healthz`. | Monthly |
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

---

## 8. Legal-opinion-outcome risks (Plan B thinking)

This section anticipates the counsel-opinion outcomes and pre-thinks Atlas's response. Written now — before the opinion is commissioned — so that a rejection or unexpected finding on any question doesn't leave the programme flat-footed.

### 8.1 If Q1 rejects the prize-competition model

**Meaning:** counsel concludes Atlas's UK-style design is a lottery under Nigerian law and requires an NLRC licence.

**Plan B options, in decreasing order of appeal:**

1. **Redesign to strengthen the prize-competition case.** If the rejection turns on specific design deficiencies (e.g. skill question insufficiently substantive; free-entry route not equal-odds enough), rework those design elements and seek re-opinion. Timeline impact: +6–8 weeks. Cost: <£10k additional counsel + re-work in design.
2. **Pursue federal NLRC lottery licence.** Timeline impact: +6–12 months. Cost: licence fees + prize-pool contribution obligations (typically % of gross) + ongoing reporting overhead. Product impact: needs licensed-lottery UX (different disclosures, different consumer expectations). This is a strategic pivot, not a tweak.
3. **Pursue state-level (Lagos LSLGA) licence** and geo-restrict to Lagos initially. Timeline: +3–6 months. Enables partial launch. Fragmented for V2 scaling.
4. **Pivot the model to a genuine promotional competition tied to a purchase** (buy X product, get free draw entry). Requires a primary product Atlas doesn't currently sell. Effectively a different business.
5. **Abandon Nigeria and target a different launch market** (Ghana, Kenya, SA) where the prize-competition model may translate more cleanly.

**Recommendation for Plan B trigger:** if counsel rejects with score = "unlikely to survive," go to option 2 (licensed lottery). If rejection is "possible to defend with design changes," go to option 1. Founder decision — Adaeze surfaces the choice with an evidence pack the day the opinion lands.

### 8.2 If Q2 imposes higher AML burden than assumed

**Likely form:** Atlas classified as a "DNFBP" or analogous under NFIU, requiring formal compliance programme, appointed MLRO, ongoing STR reporting.

**Response:** MLRO named before Phase 3 exit; STR reporting workflow built into admin app before beta draw; annual AML training scheduled. Modest programme impact.

### 8.3 If Q4 (NDPA) finds tension with append-only audit log

**Likely form:** counsel concludes the immutable audit log violates data-subject erasure rights in some scenarios.

**Response:** hybrid design — PII in audit log is stored as opaque hashes; the plaintext-PII record is separately erasable. ADR-005 amendment required. Timeline: +2–3 weeks of design work.

### 8.4 If Q7 (Lagos jurisdiction) requires LSLGA notification/licence

**Response:** notify LSLGA before public launch as a defensive move; if licence required, treat as Plan B option 3 above.

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

---

📊 *End of register. Mary handing off ongoing ownership to Adaeze (Compliance & Risk) per `docs/AINE-AGENTS.md §3` — Mary populates in Phase 0; Adaeze maintains from Phase 1 onwards.*
