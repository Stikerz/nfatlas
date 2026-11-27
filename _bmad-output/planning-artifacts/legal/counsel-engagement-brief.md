# Project Atlas — Counsel Engagement Brief

**Drafted:** 2026-06-30
**Revised:** 2026-11-24 — **substantial rewrite of §1, §2, Q1, Q5, Q7, §4.**
**Drafted by:** 📊 Mary (BMad Analyst) on behalf of Atlas founder S1408661
**Revised by:** ⚖️ Adaeze (atlas-compliance-risk)
**Status:** Draft — pending founder review before transmission to counsel. **NOT YET SENT.**

> **Why this was rewritten before it was ever sent.** The 2026-06-30 draft asked
> whether Atlas qualifies for a carve-out from the National Lottery Act 2005.
> On 2026-11-23 desk research established that the NLRA 2005 was nullified by
> the Supreme Court of Nigeria on 22 November 2024 (*AG Lagos State & Ors v
> AG Federation*, SC/1/2008), that lottery and gaming are now exclusively
> State matters, and that the NLRC holds no national licensing authority.
> Transmitting the original draft would have commissioned a fixed-fee opinion
> on a void statute, with Q1 — the question that gates the other seven —
> aimed at the wrong regime.
>
> Separately, Atlas removed its free-entry route on 2026-11-23 (founder
> decision). The original brief described two load-bearing mechanisms. There
> is now one. §2 and Q1 are rewritten accordingly.
>
> Nothing in this box is legal advice. The research is single-pass and
> self-reports medium to medium-high confidence; the SC/1/2008 judgment text
> was not retrieved. **Counsel should verify the judgment and its effect as
> the first substantive step of the engagement.**
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

Atlas seeks a written legal opinion from Nigerian counsel addressing **eight numbered questions** (§3 below), delivered within **4–6 weeks** of engagement, on a **fixed-fee or capped-fee basis**, in a format suitable for reliance by Atlas, its investors, and its auditors.

The two most consequential questions are **Q1** and **Q7**, and they have swapped places since the original draft. Atlas no longer asks counsel to confirm a federal carve-out, because Atlas's own research indicates there is no longer a federal statute to be carved out of. Atlas asks instead:

- **Q7 (now Critical):** which State regime or regimes govern an online prize-draw operator serving Nigerian users, and what does each require?
- **Q1 (now Critical, reframed):** under the governing State law — in Atlas's launch market, the Lagos State Lotteries and Gaming Authority Law 2021 — is Atlas's model licensable, prohibited, or outside scope; what licence applies; what does it cost; and how long does it take?

**Atlas is explicitly open to the answer being "you need a licence."** The founder would rather know the licensing cost and timeline now and decide whether the business is viable at that cost, than receive reassurance that a carve-out applies and discover otherwise after taking money from consumers. Counsel should not optimise their answer toward Atlas's preferred outcome. There isn't one.

---

## 2. Atlas at a glance

### What it is

A premium digital prize platform launching in Nigeria, positioned as a trusted lifestyle/entertainment brand rather than a gambling product. Users purchase entries into professionally managed prize draws for cash and vehicle prizes (V1); property, luxury goods, holidays, and scholarships are planned for V2+.

### Intended mechanics (the core legal-design choices)

Atlas's V1 design was modelled on **UK prize competitions** — BOTB (Best of the Best), Omaze, Raffle House, Aspire Competitions. Counsel should treat that lineage as *explanatory background only*, not as an argument Atlas is advancing. Atlas now understands the UK analogy may not survive contact with Nigerian State law.

**As the product stands on 2026-11-24, there is exactly one mechanism:**

1. **Skill question on every paid entry.** Each paid entry requires the entrant to answer a question before payment completes. Wrong answer = entry rejected, no charge.

Atlas must be candid with counsel about that mechanism's current quality, because overstating it would corrupt the opinion. As implemented today it is **four-option multiple choice drawn from a small pool**, deterministically rotated per user per draw per minute, with each request creating a fresh attempt — so a wrong answer can be retried immediately with the same question. Atlas's own Compliance & Risk function assessed it against the nearest published benchmark (UK Gambling Act 2005 s.14(5)) and concluded it would **probably fail** that test, and rejected it for real-user launch in an internal review dated 2026-07-08. That rejection has not been lifted. Remediation is scoped but unbuilt.

**Two mechanisms were described in the 2026-06-30 draft. Both have gone:**

- *Free entry route (removed 2026-11-23).* Every draw was to offer a non-paid postal route into the same pool at identical odds. Counsel should know two things about it. First, it was removed by founder decision. Second, and more importantly: **it was never operable.** The P.O. box was never leased. Atlas's internal review flagged this on 2026-07-08 and it remained open. For the duration of the V0.5 demo period, Atlas's public pages described a free entry route with no address to post to. Atlas is disclosing this rather than presenting the route as a mechanism it once had. No real-money draw has ever been run, and the demo period involved no public users.

Atlas would also welcome counsel's view on whether **reinstating a genuine, properly operated free entry route** (self-service and online, rather than postal) would change the analysis — see Q1.6.

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

Atlas's own position, revised 2026-11-24 and stated plainly so counsel can disagree with something concrete:

**Atlas now believes it probably requires a State gaming licence, and that no mechanic available to it changes that.** Its desk research found that the Lagos State Lotteries and Gaming Authority Law 2021 defines "Gaming" as any scheme for distributing prizes by lot or chance **with no payment or consideration element in the definition at all**, expressly classes promotional competitions as "Other lotteries", prohibits operating or promoting any "plan, scheme, competition, prize... whether remotely or otherwise in the State" without a licence, and — via the Remote Gaming Regulations 2021 — reaches remote providers serving a Lagos customer even where the customer plays free for a chance at a prize. If that reading is right, the free-entry argument fails for want of a payment element to negate, and the skill argument has nothing to attach to.

Atlas is not asking counsel to validate that pessimism. Atlas is asking counsel to **correct it or confirm it, and if confirmed, to price the licensed path.**

Two commercial gatekeepers may bind before any regulator does, and Atlas flags them so counsel can factor them into sequencing: Paystack's merchant terms prohibit "any other activity with an entry fee and a prize... games of skill (whether or not it is legally defined as a lottery) and sweepstakes" absent prior approval, and Google Play treats a game accepting money for a chance at a prize as a policy violation without a gambling licence. Atlas ships Paystack-only and mobile-only. Either gatekeeper can stop the product without a regulator being involved.

---

## 3. Questions for opinion

Numbered, with criticality marked. Each question states *why it matters*, *Atlas's working hypothesis*, and *the specific opinion sought*. Counsel is free to challenge hypotheses, restate questions, or surface adjacent issues we have missed — and Atlas would rather be told it has asked the wrong questions than receive precise answers to poor ones.

**Reading order.** The numbering is historical and no longer matches priority. **Please answer Q7 first, then Q1** — Q7 establishes which law governs and Q1 applies it. Q2-Q6 and Q8 largely presuppose that Atlas is operating; if Q1 and Q7 conclude it cannot operate as designed, counsel should say so and pause rather than working through the remainder at Atlas's expense.

### Q1 (Critical) — Classification and licensability under the governing State law

**Why it matters.** This determines whether Atlas can lawfully operate at all, and if so at what cost. The original draft framed this as prize competition (no licence) versus lottery (licence). Atlas no longer believes that is the live question. Please read Q7 first — it establishes *which* law governs; Q1 then asks what that law does to Atlas.

**Atlas's working hypothesis (revised 2026-11-24, low-to-medium confidence).** Under the Lagos State Lotteries and Gaming Authority Law 2021, Atlas's model falls **inside** the regulated perimeter and requires a licence, because the statutory definition of "Gaming" requires only chance and a prize and contains no payment or consideration element, and because promotional competitions are expressly classed as "Other lotteries". Atlas further assumes that neither a skill element nor a free entry route removes it from that perimeter, there being no equivalent to UK Gambling Act 2005 s.14 in the State law examined. **Atlas holds this hypothesis without confidence and would welcome being wrong.**

**Specific opinion sought.**

1. Confirm or correct Atlas's reading of the NLRA 2005's nullification: is there any residual federal lottery statute, any saving provision, any application to the FCT, or any pending legislative replacement (the Central Gaming Bill 2025 and its non-assent) that bears on an online operator serving users nationwide?
2. Under the governing State law identified in Q7, does Atlas's model fall inside the regulated perimeter? Quote the operative definitional language and apply it to the facts in §2.
3. If inside: **which licence category, what does it cost, what capital or guarantee is required, what certification, and what is a realistic end-to-end timeline?** Atlas has seen unverified third-party figures suggesting ₦250–400m in year one for Lagos. Please confirm, correct, or replace them with figures counsel will stand behind. This number may determine whether the business proceeds.
4. If outside, or capable of being brought outside: what are the **minimum design conditions** Atlas must meet and maintain? Please be specific enough to build against — Atlas's engineering team will implement exactly what counsel specifies, and nothing counsel does not.
5. **Does the skill question, as honestly described in §2, achieve anything under the governing law?** Atlas's own assessment is that it does not, and may carry its own exposure: Atlas understands the Lagos advertising code may treat a suggestion that skill influences a game of chance as a misleading claim. If the skill question is legally inert or actively adverse in Nigeria, Atlas would rather remove it and recover the conversion it costs.
6. **Would reinstating a genuine free entry route change the analysis** — and if so, what would make it "genuine" (self-service versus postal, prominence, odds parity, volume parity with paid entries)? Atlas removed its route and can rebuild it properly in roughly a week of engineering if counsel says it is load-bearing.
7. Has any operator tested a model like Atlas's in Nigeria, under the federal regime before November 2024 or under State regimes since? With what outcome?
8. What is the exposure for the V0.5 demo period already elapsed — no public users, no real money, no completed real-money draw, but a publicly reachable website describing paid prize draws? Atlas asks so it can disclose accurately to investors, not to seek comfort.

**Consequence of each answer, so counsel can see what rides on it.** Licensable at a cost Atlas can bear → Atlas licenses and proceeds. Licensable but uneconomic → Atlas restructures or does not launch in Nigeria. Prohibited → Atlas does not launch. Outside scope on stated conditions → Atlas builds precisely those conditions and asks counsel to confirm the build.

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

### Q5 (HIGH — raised from Medium 2026-11-24) — Marketing and advertising restrictions

**Why it matters.** Atlas's brand positioning depends on a specific lexicon (avoiding "lottery," "raffle," "luck"). Public-facing copy on draws must satisfy both consumer-protection norms and any sector-specific advertising standards. Channel-specific restrictions (WhatsApp Business, SMS, in-app push) may apply.

**Atlas's working hypothesis (revised 2026-11-24).** Atlas no longer assumes its copy bans are sufficient. Two specific concerns now sit above the lexicon question. First, Atlas understands the Lagos State regime may prohibit *advertising or promoting* an unlicensed scheme independently of operating one — meaning marketing could create exposure before a single entry is sold. Second, Atlas understands the Lagos advertising code may treat a suggestion that **skill influences a game of chance** as a misleading claim, which would make Atlas's own skill-question messaging adverse rather than protective.

Atlas also discloses, for completeness, that an internal compliance review on 2026-11-23 found three live consumer-facing claims unsupported by implementation: a permanent self-exclusion regime that was not built, a free entry route with no postal address, and age verification described as occurring "at every purchase" when it occurred only at registration. All three have been corrected or removed. No real-money draw was ever run and the site had no public user base. Atlas raises this unprompted because counsel's advice on remediation and disclosure is worth more than counsel's goodwill.

**Specific opinion sought.**
1. Identify the advertising and promotional rules that apply under the governing State regime (and any FCCPC or ARCON/APCON overlay), **including whether advertising or promoting an unlicensed scheme is itself an offence**, and what that means for pre-licence marketing.
1a. Advise on whether Atlas's skill-question messaging creates exposure under any "skill influences chance" misleading-claim provision, and how such messaging should be worded if the mechanic is retained.
1b. Advise on Atlas's remediation and disclosure obligations, if any, arising from the three corrected claims above.
2. Confirm the disclosure obligations on draw pages (odds, prize value, free-entry route, T&Cs link).
3. Comment on influencer / affiliate marketing rules.
4. Comment on channel-specific rules — WhatsApp Business Meta policy compliance for prize-draw operators in Nigeria.

### Q6 (Medium) — Responsible play and self-exclusion

**Why it matters.** Atlas is trust-first and positions itself adjacent to gambling without being gambling. The product carries responsible-play obligations regardless of classification.

**Correction to the 2026-06-30 draft, which counsel must not be misled by.** That draft described self-exclusion as "operationally implemented through BVN-keyed permanent self-exclusion (ADR-010)". **It is not implemented.** ADR-010 was approved on 2026-07-02 and never built: there is no exclusion registry, no enforcement at purchase, and no in-app flow. Until 2026-11-23 Atlas's public responsible-play page described the regime as live; that copy has been corrected to say it is in development. Age gating at registration **is** real and enforced in code. Atlas also operates no per-user entry cap and no spend ceiling, and removed the free entry route that page had cited as a harm-reduction control.

**Atlas's working hypothesis.** Nigerian law does not yet impose prize-competition-specific responsible-play obligations as comprehensive as the UK's framework (Gambling Commission's responsible-gambling requirements). However, generic consumer-protection obligations apply, and best-practice voluntary measures (self-exclusion, deposit limits, cool-off periods) are anticipated by the market. V1 ships self-exclusion only; deposit limits and cool-off are V2 candidates.

**Specific opinion sought.**
1. Confirm any statutory responsible-play obligations applicable.
2. Comment on whether Atlas's permanent-only self-exclusion (no reversal mechanism in V1) is lawful, recommended, or potentially over-restrictive.
3. Identify any age-verification rules beyond BVN-confirmed adult status.

### Q7 (CRITICAL — promoted from Medium 2026-11-24) — Which regime governs

**Why it matters.** This now precedes Q1 logically and should be answered first. The 2026-06-30 draft treated State jurisdiction as a secondary clean-up question on the assumption that a federal regime governed. If the Supreme Court nullified the NLRA 2005 and lottery/gaming is a residual State matter, then **State law is the only law**, and "which State" is the question that determines everything downstream. The original draft did ask counsel to cover "any recent Supreme Court or Federal High Court decisions" — Atlas simply never ran the research that would have shown how much turned on it.

**Atlas's working hypothesis (revised 2026-11-24, medium confidence).** Lottery and gaming are now exclusively within State legislative competence following *AG Lagos State & Ors v AG Federation* (SC/1/2008, 22 November 2024). An online operator has no single federal licence available to it and must instead address each State whose residents it serves. Lagos is Atlas's launch market and the Lagos State Lotteries and Gaming Authority Law 2021, with its Remote Gaming Regulations 2021, is the governing instrument.

**Specific opinion sought.**
1. Verify the judgment and state its ratio and effect precisely. Is the NLRA 2005 void in whole or in part? Does anything survive for the FCT? What is the status of the Central Gaming Bill 2025 following non-assent, and is a replacement expected?
2. **Which State's law governs an online operator incorporated in Nigeria serving users across multiple States?** Is it the State of incorporation, the State of each user's residence, every State in which the service is reachable, or something else? How does an operator comply with a nationwide user base in practice — a licence per State, a lead-State approach, or geo-restriction to licensed States only?
3. Set out what the Lagos State Lotteries and Gaming Authority Law 2021 and its Remote Gaming Regulations 2021 require of a remote operator serving a Lagos customer: registration, licensing, fees, gaming tax or GGR levy, local-entity and share-capital requirements, bank guarantee, technical certification (GLI/BMM or equivalent), and reporting.
4. Is there a **promotional-competition permit** or lighter-touch registration distinct from a full gaming licence, and would Atlas qualify for it? If so, what does it cost? Atlas's research could not establish this and flags it as the single highest-leverage unknown in the whole engagement — a cheap permit and a ₦250m licence are different businesses.
5. **Is a staged or limited launch available** — a single State, a capped prize value, an invite-only beta — that would let Atlas operate lawfully at smaller scale while a full licence is pursued?
6. Penalties for unlicensed operation and for unlicensed advertising: civil, criminal, or both; who is personally liable (directors, officers); and whether voluntary pre-licence disclosure to the regulator mitigates.
7. V2 expansion: what changes as Atlas reaches users in further States, and is there any inter-State recognition or passporting?

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
| ADR-010 Self-exclusion (BVN-keyed) | `docs/adr/ADR-010-self-exclusion-bvn-enforcement.md` | Relevant to Q6. **Approved but NOT IMPLEMENTED** — no registry exists |
| **Classification research (2026-11-23)** | `_bmad-output/planning-artifacts/research/nigerian-draw-classification-research-2026-11-23.md` | **Read before Q1 and Q7.** Atlas's own desk research, with sources and per-finding confidence levels. Single-pass, not legal advice; the SC/1/2008 judgment text was not retrieved |
| **Compliance review REVIEW-001** | `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md` | §3.1 — Atlas's own rejection of its skill question for real-user launch |
| **Compliance review REVIEW-002** | `docs/compliance/reviews/REVIEW-002-free-entry-route-removal.md` | The free-route removal, and §6 / Addendum A.2 on claims that shipped ahead of implementation |
| **Risk register** | `docs/risk-register.md` | §1 regulatory risks, incl. R-REG-08/09/10 raised 2026-11-24 |

**Two caveats on the supporting set, stated so counsel does not have to discover them.**

The PRD and the delivery framework are **superseded in part and not yet amended.** Both still describe a free entry route and a two-mechanism prize-competition model. Atlas's change-control process requires a formal amendment that has not yet been executed. Where those documents conflict with §2 of this brief, **§2 is current.**

Atlas's compliance copy block for the skill-question content set is still in drafting and the free-entry copy block has been withdrawn. `docs/compliance/skill-questions.md`, referenced in Atlas's internal reviews as the governing policy artefact, **has not been written.**

---

## 5. Engagement parameters

### Deliverable shape

- **Form:** written legal opinion, PDF + editable Word.
- **Length:** as needed for the eight numbered questions; Atlas's expectation is 30–60 pages including statutory references and case citations. Atlas would accept — and would value — a short early note on Q7 and Q1 ahead of the full opinion, if counsel can give a preliminary view sooner. Those two answers gate engineering and spend.
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
