# Project Atlas — Counsel Engagement Brief

**Drafted:** 2026-06-30
**Drafted by:** 📊 Mary (BMad Analyst) on behalf of Atlas founder S1408661
**Status:** Draft — pending founder review before transmission to counsel
**Audience:** Nigerian gambling/promotions/regulatory counsel (intended recipients: senior partner at one of Banwo & Ighodalo, Aluko & Oyebode, Templars, Olaniwun Ajayi, or comparable firm)
**Length:** ~6 pages
**Pairs with:** `_bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md`, `_bmad-output/planning-artifacts/delivery-framework.md`, the (currently blocked) regulatory research at `_bmad-output/planning-artifacts/research/domain-nigerian-prize-competition-licensing-research-2026-06-30.md`

---

## 0. About this brief

This document is the package Atlas will hand to counsel when commissioning a written legal opinion for the Nigerian launch. It exists to:

1. Pre-load counsel with Atlas's intended business model so the engagement does not start with billable scoping calls.
2. State precisely the questions on which counsel is being asked to opine, ranked by criticality.
3. Set out Atlas's working hypothesis on each question, so counsel reacts to a position rather than starting from a blank page.
4. List supporting documents already prepared, and identify the documents counsel will need to draft or co-draft.

The brief is **not** legal advice, **not** a finished legal position, and **not** binding on either party until an engagement letter is signed.

---

## 1. The ask in one paragraph

Atlas seeks a written legal opinion from Nigerian counsel addressing **seven numbered questions** (§3 below), delivered within **4–6 weeks** of engagement, on a **fixed-fee or capped-fee basis**, in a format suitable for reliance by Atlas, its investors, and its auditors. The most consequential question is Q1 — whether Atlas's intended model qualifies as a prize competition (no NLRC licence required) or as a lottery (NLRC licence required), under the National Lottery Act 2005 and current NLRC interpretive practice. Q1's outcome determines whether the rest of the engagement is implementation-of-prize-competition or licensing-pathway-for-a-lottery.

---

## 2. Atlas at a glance

### What it is

A premium digital prize platform launching in Nigeria, positioned as a trusted lifestyle/entertainment brand rather than a gambling product. Users purchase entries into professionally managed prize draws for cash and vehicle prizes (V1); property, luxury goods, holidays, and scholarships are planned for V2+.

### Intended mechanics (the core legal-design choices)

Atlas's V1 product design follows a **UK-style prize-competition model**, analogous to BOTB (Best of the Best), Omaze, Raffle House, and Aspire Competitions in the UK market. The two load-bearing design choices are:

1. **Free entry route on every draw.** Every draw offers a non-paid route (V1: postal entry to a leased P.O. box with a handwritten entry slip, transcribed by operations within 24 hours). Free-route tickets enter the same prize pool with identical odds to paid tickets. The free route is disclosed prominently on every draw page, not buried in T&Cs.
2. **Skill question on every paid entry.** Every paid entry path requires the entrant to answer a substantive skill question (multiple-choice, rotated, of non-trivial difficulty) before payment can complete. Wrong answer = entry rejected, no charge. The skill-question content set is operator-curated and rotated.

### Other design choices counsel should know

- **Marketing copy bans:** the words "lottery," "raffle," "luck of the draw," and equivalents are excluded from all consumer-facing copy. Style guide and copy-approval process are operated by Atlas's Compliance & Risk function.
- **Provably fair draws:** every draw runs a commit-reveal cryptographic protocol (server-seed commitment hash published at draw creation; revealed at draw conclusion with public-entropy inputs from Bitcoin block hashes and the drand randomness beacon). Anyone with the published inputs can independently verify the winner. Full design in ADR-006.
- **Double-entry ledger:** all financial movement runs through a double-entry ledger with derived balances; no mutable balance field anywhere. Reconciliation against Paystack settlement reports runs nightly. Design in ADR-003.
- **KYC:** every winner above a configurable prize-value threshold completes enhanced KYC (BVN + document + selfie via a vendor — Smile Identity, Dojah, or Prembly; vendor pick is Phase 0). Self-exclusion is BVN-keyed and permanent (no reversal in V1). Designs in ADR-007, ADR-010.
- **Payments:** V1 ships Paystack only. Other Nigerian rails (Flutterwave, Moniepoint, USSD-direct) are planned for V2+.
- **Distribution:** mobile-first (Flutter app on iOS + Android); admin/operator web app (Next.js); no consumer web app in V1.
- **Prize categories V1:** cash and vehicle prizes only. Property prizes are deferred to V2+ due to title-transfer and stamp-duty operational complexity.
- **Geographic scope V1:** Nigeria only. V2+ regional expansion plan covers Ghana, Kenya, South Africa, Rwanda, Uganda, Tanzania.

### Where the product sits on the legal-risk spectrum

Atlas's design choices are deliberately closer to UK prize competitions (BOTB/Omaze) than to traditional lotteries. **Atlas does not yet know whether Nigerian law and NLRC interpretive practice accept this distinction.** That is the central question this engagement must resolve.

---

## 3. Questions for opinion

Numbered. Ranked by criticality. Each question states *why it matters*, *Atlas's working hypothesis*, and *the specific opinion sought*. Counsel is free to challenge hypotheses, restate questions, or surface adjacent issues we have missed.

### Q1 (Critical) — Classification: prize competition vs lottery

**Why it matters.** This determines whether Atlas operates under a prize-competition framework (no NLRC licence required, presumed) or under a lottery framework (NLRC licence required, with the attendant licensing fees, prize-pool contribution obligations, and ongoing reporting). The two paths produce different products, different unit economics, different vendor decisions, and different launch timelines.

**Atlas's working hypothesis.** Under the National Lottery Act 2005's statutory definitions of "lottery" — and the NLRC's interpretive practice — the combination of (a) a *free entry route* with identical odds and (b) a *substantive skill question* on every paid entry path is sufficient to remove an arrangement from the "lottery" classification under Nigerian law, by analogy with the position under the UK Gambling Act 2005 (where prize competitions involving genuine skill, or paid entries with a free entry route of equal odds, fall outside the regulated gambling framework). **We assess this as a hypothesis with low-to-medium confidence** because the analogy from UK law to Nigerian law is not automatic, and because the NLRC's posture on prize competitions specifically (as distinct from promotional competitions tied to a primary product purchase) is unclear from public sources.

**Specific opinion sought.**
1. Does the NLRA 2005 (and any subsidiary regulation or NLRC circular) define "lottery" in terms that *do* or *do not* capture Atlas's intended model?
2. Has the NLRC published, or otherwise communicated, a position on prize competitions that include both a free entry route and a skill question?
3. If Atlas's hypothesis is correct, what are the **minimum design conditions** Atlas must meet to defend the prize-competition classification (e.g. demonstrable equality of odds between free and paid routes; difficulty threshold for the skill question; specific disclosure language)?
4. If Atlas's hypothesis is wrong, what licensing path applies — federal NLRC, state-level (Lagos State Lotteries and Gaming Authority for Lagos-resident operations), or both? What is the realistic timeline and cost of obtaining the necessary licence?
5. Have any prior operators tested the prize-competition model in Nigeria? If so, with what outcome?

### Q2 (High) — KYC and AML obligations

**Why it matters.** Atlas processes user identity verification before paying out prizes above threshold and runs a double-entry financial ledger. Both fall within scope of Nigerian KYC/AML regulation (CBN AML/CFT Regulations, NFIU Act 2018, FATF-aligned obligations). Vendor selection (KYC + payments) cannot be finalised without clarity on what Atlas itself must do.

**Atlas's working hypothesis.** Atlas is a non-bank financial-facing operator that should: (a) register or designate compliance with the NFIU as a "designated non-financial business or profession" or analogous classification; (b) implement risk-based customer due diligence with BVN verification at a minimum and enhanced due diligence on high-value winners; (c) maintain a sanctions screening process against domestic and international lists; (d) operate suspicious-transaction reporting workflows.

**Specific opinion sought.**
1. Confirm Atlas's regulatory classification for AML purposes.
2. Enumerate the specific KYC/AML obligations applicable (registration, programme, reporting, recordkeeping).
3. Comment on whether BVN-only verification is sufficient for entry, or whether document-and-selfie is required at deposit / before play.
4. Identify any sector-specific guidance from the CBN or NFIU applicable to a prize-platform operator.

### Q3 (High) — Taxation of prizes and operator revenue

**Why it matters.** Drives net-of-tax prize values communicated to entrants, operator margin assumptions, and the wallet/ledger design for tax accruals (`tax_payable` account already provisioned in ADR-003).

**Atlas's working hypothesis.** Cash prizes attract Withholding Tax at the prescribed rate, withheld by Atlas on payout. Vehicle prizes attract WHT on the cash equivalent at the time of award. Operator revenue (entry fees retained) is corporate-income-taxable in the ordinary course. VAT may apply to certain operational inputs (technology services, marketing services) but not to the entry-fee transaction itself.

**Specific opinion sought.**
1. Confirm WHT rate, withholding mechanism, and remittance cadence for cash prizes paid to individuals.
2. Confirm tax treatment of non-cash prizes (vehicle, future property) — who values, who pays, whether stamp duty applies on title transfer.
3. Confirm VAT treatment of entry fees (taxable supply, exempt, outside scope).
4. Identify any prize-platform-specific tax provisions or recent FIRS circulars applicable.

### Q4 (High) — Data protection (NDPA 2023)

**Why it matters.** Atlas collects PII (name, phone, email), national identifiers (BVN), biometric data (selfie), and document images. The Nigeria Data Protection Act 2023 governs processing. KYC vendor selection, audit-log retention, right-to-erasure workflows, and cross-border data transfer (if any vendor processes offshore) all turn on this.

**Atlas's working hypothesis.** Atlas is a data controller under the NDPA 2023; KYC vendors and payment vendors are data processors. Atlas must: (a) register with the NDPC (or its designated platform); (b) appoint a Data Protection Officer (DPO) or comparable role; (c) implement lawful basis (likely consent + contract performance); (d) honour data-subject rights including access and erasure where legally applicable; (e) operate breach notification per NDPA timelines.

**Specific opinion sought.**
1. Confirm Atlas's classification (data controller, joint controller, or processor) under NDPA 2023.
2. Identify the specific obligations Atlas must meet before launch (registration, DPO, DPIA).
3. Comment on cross-border transfer of KYC data if vendors process outside Nigeria — what is the regime, what consent or contractual mechanism is required?
4. Confirm data retention obligations and limits — particularly for KYC records (regulatory minimum vs maximum) and the self-exclusion registry (Atlas's stance is permanent retention; counsel confirm this is lawful).
5. Comment on whether Atlas's hash-chained append-only audit log (ADR-005) creates any data-protection tension with right-to-erasure obligations.

### Q5 (Medium) — Marketing and advertising restrictions

**Why it matters.** Atlas's brand positioning depends on a specific lexicon (avoiding "lottery," "raffle," "luck"). Public-facing copy on draws must satisfy both consumer-protection norms and any sector-specific advertising standards. Channel-specific restrictions (WhatsApp Business, SMS, in-app push) may apply.

**Atlas's working hypothesis.** Atlas's copy bans are sufficient to avoid sector-specific advertising rules that would otherwise apply to lotteries. Standard Nigerian consumer-protection norms (truth in advertising, non-misleading representations of odds and prize values) apply. Influencer marketing carries its own disclosure obligations.

**Specific opinion sought.**
1. Identify any sector-specific advertising rules (NLRC, APCON, FCCPC) that apply to Atlas under the prize-competition framework — and how those differ from the rules that would apply if classified as a lottery.
2. Confirm the disclosure obligations on draw pages (odds, prize value, free-entry route, T&Cs link).
3. Comment on influencer / affiliate marketing rules.
4. Comment on channel-specific rules — WhatsApp Business Meta policy compliance for prize-draw operators in Nigeria.

### Q6 (Medium) — Responsible play and self-exclusion

**Why it matters.** Atlas is trust-first and positions itself adjacent to gambling without being gambling. The product carries responsible-play obligations regardless of classification — operationally implemented through BVN-keyed permanent self-exclusion (ADR-010) and age gating (18+). Counsel should confirm whether Nigerian law imposes additional specific obligations.

**Atlas's working hypothesis.** Nigerian law does not yet impose prize-competition-specific responsible-play obligations as comprehensive as the UK's framework (Gambling Commission's responsible-gambling requirements). However, generic consumer-protection obligations apply, and best-practice voluntary measures (self-exclusion, deposit limits, cool-off periods) are anticipated by the market. V1 ships self-exclusion only; deposit limits and cool-off are V2 candidates.

**Specific opinion sought.**
1. Confirm any statutory responsible-play obligations applicable.
2. Comment on whether Atlas's permanent-only self-exclusion (no reversal mechanism in V1) is lawful, recommended, or potentially over-restrictive.
3. Identify any age-verification rules beyond BVN-confirmed adult status.

### Q7 (Medium) — Federal vs Lagos State jurisdiction

**Why it matters.** There has been ongoing tension between federal lottery regulation (NLRC, under the NLRA 2005) and state-level lottery regulation, particularly in Lagos State (Lagos State Lotteries and Gaming Authority). Operators have faced enforcement from both. The position has been litigated. Atlas needs to know whether to register/license/notify at federal level only, state level only, or both — and how that scales across V2 expansion to additional states.

**Atlas's working hypothesis.** If Q1 confirms Atlas operates as a prize competition outside the lottery framework, Atlas should still proactively engage Lagos State authorities for clarity, given Lagos's established posture of asserting jurisdiction over gaming activities reaching Lagos residents. We hypothesise that prize-competition classification removes the licensing obligation but may not remove a notification or registration obligation at state level.

**Specific opinion sought.**
1. Summarise the current state of federal-vs-state lottery jurisdiction in Nigeria, including any recent Supreme Court or Federal High Court decisions.
2. Identify the Lagos State posture toward prize competitions (as distinct from lotteries).
3. Comment on whether Atlas's Lagos-resident users trigger Lagos State notification or registration obligations.
4. Comment on the V2 expansion path — what changes when Atlas reaches users in additional states with their own lottery regulators (Oyo, FCT, etc.)?

### Q8 (Deferred to V2 — counsel may comment briefly) — Property prizes

**Why it matters.** V1 cuts property out (cash and vehicles only). V2+ reintroduces property as a flagship category. Title transfer, stamp duty, and dispute-resolution architecture for property prizes will be its own legal workstream.

**Specific opinion sought (light touch only).**
1. At a *flag level* (not a full analysis), are there structural legal obstacles to property prizes that would inform whether to pursue this in V2?
2. Pointers to areas counsel would want to study in depth when V2 work begins.

---

## 4. Supporting documents (provided with this brief)

| Document | Path in Atlas repo | What counsel should look at first |
|---|---|---|
| Product Requirements Document (V1) | `_bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md` | §1 product decision; §3 functional requirements; §4 module architecture |
| Delivery framework | `_bmad-output/planning-artifacts/delivery-framework.md` | §3 Phase 0 activities (incl. this brief); §10 launch checklist |
| ADR-003 Double-entry ledger | `docs/adr/ADR-003-double-entry-ledger-schema.md` | Confirms financial-controls posture for AML Q2 |
| ADR-005 Hash-chained audit log | `docs/adr/ADR-005-hash-chained-audit-log.md` | Relevant to NDPA tension in Q4 |
| ADR-006 Commit-reveal draw protocol | `docs/adr/ADR-006-commit-reveal-protocol-and-public-entropy.md` | Provably-fair design — relevant to Q1 (fairness claim defensibility) |
| ADR-007 KYC vendor adapter | `docs/adr/ADR-007-kyc-vendor-adapter.md` | KYC architectural design; not vendor choice (that is procurement) |
| ADR-009 RBAC model | `docs/adr/ADR-009-rbac-model.md` | Operator-action audit trail design |
| ADR-010 Self-exclusion (BVN-keyed) | `docs/adr/ADR-010-self-exclusion-bvn-enforcement.md` | Relevant to Q6 (permanent exclusion stance) |

Atlas's compliance copy block for the free-entry route and the skill-question content set are still in drafting (Phase 0 work in parallel to this engagement). Counsel review will be requested when drafted.

---

## 5. Engagement parameters

### Deliverable shape

- **Form:** written legal opinion, PDF + editable Word.
- **Length:** as needed for the seven numbered questions; Atlas's expectation is 30–60 pages including statutory references and case citations.
- **Reliance:** opinion to be reliable upon by Atlas, its officers, its institutional investors, and its statutory auditors. Counsel may scope reliance via standard wording.
- **Confidentiality:** standard. Atlas will execute mutual NDA before transmitting confidential business model details beyond this brief.

### Timeline

- **Target delivery:** 4–6 weeks from engagement letter execution.
- **Atlas's milestone dependency:** Atlas Phase 1 (specification phase) cannot exit, and Phase 2 (platform build) cannot begin work on the Wallet & Ledger, Payment, Ticket, or Draw Engine modules, until counsel has delivered opinion on Q1 at a minimum. Q2–Q7 can follow within a second tranche if needed.

### Fee structure

- **Preferred:** fixed-fee, broken out by question (Q1 separately, Q2–Q7 as bundle, Q8 as light touch).
- **Acceptable alternative:** capped-fee with stage gates.
- **Not preferred:** open-ended hourly without cap.

### Communication

- **Primary contact at Atlas:** S1408661 (founder).
- **Working sessions:** Atlas requests one 60-minute kickoff session and one 60-minute interim Q1 walkthrough before final delivery.
- **Asynchronous Q&A:** by email, Atlas commits to <24-hour response on counsel questions during the engagement window.

---

## 6. Counsel intelligence Atlas would value

These are not the formal opinion ask; they are the things a senior practitioner is likely to know that public sources won't reveal. Atlas would welcome counsel's views, even informally, on:

1. **Recent NLRC enforcement posture.** Has the NLRC pursued enforcement against unlicensed operators in the past 24 months? Against prize-competition-style operators specifically? Patterns?
2. **Operator informal sounding.** Has counsel had recent informal contact with NLRC staff regarding new operator categories? Any indication of policy direction?
3. **Pending legislation.** Is there a known legislative pipeline (federal or state) that could materially change the regulatory landscape in the next 12–24 months?
4. **Competitor experience.** Are there operators in market with prize-competition-style models? What has their licensing experience been?
5. **NDPC capacity.** Practical view on NDPC registration timelines and DPO requirements in the current cycle.
6. **Lagos State posture.** Current Lagos State Lotteries and Gaming Authority temperament re prize competitions specifically.

Atlas understands this section is qualitative and not part of the formal opinion. It informs Atlas's risk posture and helps prioritise V1 design choices.

---

## 7. Logistics

### Documents access

Atlas will provide read access to the repository sections listed in §4 above. Confidential business model details (pricing model, projected unit economics, investor identities) are held back pending NDA.

### Engagement administration

- **Engagement letter:** Atlas will accept counsel's standard form; reliance and indemnity terms negotiable.
- **Payment terms:** 50% on engagement letter execution, 50% on opinion delivery.
- **Conflict check:** Atlas requests confirmation that counsel has not represented (or is not currently representing) any party with a material adverse interest, including any direct competitor, the NLRC, or any party in active dispute with Atlas's intended payment or KYC vendors (Paystack, Smile Identity, Dojah, Prembly).

### Next step after this brief lands

1. Counsel acknowledges receipt and conflicts-clears (Atlas commits to 48-hour responsiveness).
2. Atlas + counsel hold 60-minute scoping call to confirm scope, fee, and timeline.
3. Engagement letter executed.
4. Atlas opens repository access.
5. Counsel begins Q1 work first; interim walkthrough at the midpoint.
6. Final opinion delivered.
7. Atlas's Compliance & Risk function (Adaeze) consumes the opinion and amends ADRs accordingly. Any opinion finding that contradicts an existing ADR will trigger an ADR amendment per `docs/AINE-AGENTS.md §6`.

---

## Appendix A — What Atlas has deliberately *not* asked counsel to opine on (and why)

For scope clarity:

| Out of scope | Why excluded from this engagement |
|---|---|
| Commercial vendor selection (KYC, payments) | Procurement, not legal. Atlas's procurement process selects vendors; counsel's role is to confirm vendor contracts and AML obligations once selected. |
| Detailed terms-and-conditions drafting | Atlas will draft T&Cs in-house using counsel's opinion as input; counsel review of final T&Cs is a separate, smaller engagement. |
| Employment law for Atlas's Nigerian team | Separate workstream, separate counsel may be more appropriate. |
| Cross-border tax planning for V2 regional expansion | Out of scope until V2 country selection is finalised. |
| Property prize legal architecture (V2) | Light touch only in Q8; full engagement when V2 planning begins. |
| Intellectual property (brand, trade mark) | Separate workstream. |

---

## Appendix B — Drafting notes (for Atlas internal use; remove before sending to counsel)

- This brief is drafted at confidence-level "best effort by a non-lawyer AI agent" — every legal-substance claim in §3 is *Atlas's hypothesis*, not a representation of law. Counsel will correct.
- The list of supporting documents in §4 references ADRs that are currently in `Proposed` status (pending EL approval). Before transmission to counsel, Atlas should either (a) confirm those ADRs are still the active design, or (b) flag any subsequent amendments.
- Section 6's "counsel intelligence" requests are *informal* and counsel is free to decline. Including them signals Atlas is sophisticated about the limits of public-source research and values practitioner judgement.
- This brief should be paired with a one-page transmittal email summarising who Atlas is, who S1408661 is, and how counsel was identified (referral, market shortlist, prior relationship).
- Estimated counsel time to consume this brief and respond with fee proposal: 90 minutes. If counsel cannot turn that around in 5 working days, Atlas should consider whether they have capacity for the engagement.

---

📊 *End of brief. Mary delivering this to S1408661 for review before any counsel approach is made.*
