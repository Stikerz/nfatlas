# Project Atlas — Counsel Selection Framework

**Drafted:** 2026-06-30
**Drafted by:** 📊 Mary (BMad Analyst)
**Status:** Draft — framework for S1408661 to operate
**Pairs with:** `_bmad-output/planning-artifacts/legal/counsel-engagement-brief.md` (the document being sent to candidate firms)
**Length:** ~4 pages

---

## 0. Purpose

This framework operationalises how Atlas selects the Nigerian gambling/regulatory counsel that will deliver the legal opinion scoped in `counsel-engagement-brief.md`. It is designed to:

1. Construct a defensible shortlist without subjective drift.
2. Run a parallel RFP that surfaces fee, scope, and partner-availability differences fast.
3. Score responses against weighted criteria, with the scoring rubric public to all evaluators.
4. Reduce risk of the wrong pick (which is high — the wrong counsel produces an opinion that's either ignored or wrong, both of which damage Atlas).

This is procurement discipline applied to a legal engagement. The cost of running it (≈8 founder hours over 2 weeks) is small relative to the cost of a bad counsel pick (≈£15k–£30k wasted fees + 4–6 weeks of programme slippage + the residual risk of a wrong opinion shaping Phase 1).

---

## 1. Process at a glance

```
Week 1                    Week 2                    Week 3
────────────────────      ────────────────────      ────────────────────
Day 1   Shortlist          Day 8   Responses        Day 15  Final pick
Day 2   Send RFP                   evaluated                signed
Day 3   …                  Day 9   Top-2 interviews Day 16  Kickoff call
Day 4   …                  Day 10  …
Day 5   …                  Day 11  Reference checks
Day 6   …                  Day 12  Decision matrix
Day 7   …                  Day 13  Engagement
        (firms reading)            letter execution
```

**Total founder time:** ~8 hours across 2 weeks (shortlist construction 1h, RFP send 30min, response evaluation 2h, two 60-min interviews, two 30-min reference calls, 1h decision and engagement-letter review).

---

## 2. Stage 1 — Shortlist construction (Day 1)

### Target shortlist size: **4 firms**

Three is too few (one withdraws, two left makes the comparison thin). Five-plus is too many (founder time evaluating 5+ proposals at quality is a week of work). **Four** lets you withstand one withdrawal and still have a real choice.

### How to populate the shortlist

Combine three sourcing channels; the goal is *diversity of profile*, not four similar firms.

**Channel A — Tier-1 commercial firms with regulated-sector practice (target: 2 of the 4 slots).**

Candidate profile: full-service Nigerian firms with an established regulatory/gaming practice, partner-led, used to advising international investors. Public-source candidate names: Banwo & Ighodalo; Aluko & Oyebode; Templars; Olaniwun Ajayi; G. Elias; Udo Udoma & Belo-Osagie. **You can populate this from any Chambers, Legal 500, or IFLR ranking for Nigeria's regulatory/gaming category.**

Why this channel: depth, reputation, reliability of opinion. Investors and auditors recognise the names, which helps later.
Risk of this channel: high fees, junior-associate-heavy delivery, slow turnaround.

**Channel B — Specialist boutique or partner-led firm (target: 1 of the 4 slots).**

Candidate profile: smaller firm where a senior partner has specific gambling or fintech regulatory expertise and will personally do the work. Often a former senior counsel from a Tier-1 firm or a former regulator who has set up independently.

Why this channel: substantive expertise above what a generalist Tier-1 might offer; partner-led delivery; often faster.
Risk of this channel: smaller bench means less resilience if the named partner is unavailable; weaker investor-recognition of the firm name.

**Channel C — Recommendation from network (target: 1 of the 4 slots, possibly overlapping A or B).**

Direct referral from someone in S1408661's network who has used Nigerian regulatory counsel for a *comparable* matter (fintech, lottery, gaming, consumer marketplace). Personal recommendation is the highest-signal sourcing channel — but only if the recommender has *direct experience* with the firm, not "I've heard of them."

If no network referral is available, allocate this slot to a second Tier-1 firm (Channel A).

### Hard constraints on shortlist

A firm is **out** if any of:
- Active or recent representation of the NLRC, Lagos State Lotteries and Gaming Authority, or any direct competitor identifiable to Atlas.
- No public-source evidence of regulatory/gaming or fintech practice (the engagement is too specific to commission cold from a generalist firm).
- Estimated minimum hourly billing rate above what Atlas's fee envelope can plausibly accommodate (set a ceiling before sending RFPs — see §4).

### Shortlist artefact

Capture the shortlist in a small markdown table before sending the RFP:

```markdown
| Slot | Firm | Channel | Named partner (if known) | Conflict check status | Sourcing evidence |
|---|---|---|---|---|---|
| 1 | [Firm A] | A (Tier-1) | [Partner name] | not yet asked | Chambers 2026 ranking, Nigeria regulatory |
| 2 | [Firm B] | A (Tier-1) | [Partner name] | not yet asked | Legal 500 2026, Nigeria gaming |
| 3 | [Firm C] | B (boutique) | [Partner name] | not yet asked | [How identified] |
| 4 | [Firm D] | C (network) | [Partner name] | not yet asked | [Referrer + their experience] |
```

Save at `_bmad-output/planning-artifacts/legal/counsel-shortlist.md`.

---

## 3. Stage 2 — RFP transmission (Day 2)

### What gets sent

Each firm receives:

1. **A short cover email** (template in Appendix A).
2. **The engagement brief** (`counsel-engagement-brief.md`, exported to PDF — strip Appendix B "drafting notes" first).
3. **A response template** (Appendix B of this framework) — asking five specific questions to standardise comparison.
4. **An NDA** (mutual, standard form) — Atlas executes first.

### What does NOT get sent

- The full PRD (too much; counsel can request if needed after engagement).
- Investor identities or financial projections.
- Atlas's internal cost ceiling or scoring weights.
- This selection framework itself (process is Atlas's; not their concern).

### Transmission cadence

Send all 4 RFPs **on the same day**, with the same response deadline (7 calendar days). Parallel transmission protects against the founder anchoring on whichever firm responds first.

### Response deadline

7 calendar days from transmission. State this explicitly in the cover email. A firm that cannot return a fee proposal in 7 days is likely too capacity-constrained to deliver the 4–6 week opinion timeline.

---

## 4. Stage 3 — Evaluation criteria and scoring rubric (Day 8)

### Criteria, weights, and scoring (5-point scale per criterion)

| # | Criterion | Weight | What "5" looks like | What "1" looks like |
|---|---|---|---|---|
| 1 | **Substantive expertise on prize platforms / gambling / promotional competitions** | **25%** | Named partner has personally advised on prize-competition or gambling matters in past 24 months, can cite anonymised examples | No prior gambling/promotional-competition exposure; generalist response |
| 2 | **Named senior partner will personally lead the engagement** | **15%** | Partner named, partner cited in response, partner availability confirmed for the engagement window | Response in firm's name only; associate-led delivery implied |
| 3 | **Fee proposal — fixed or capped, within Atlas's envelope** | **15%** | Fixed-fee, broken out per question, within envelope, no scope creep clauses | Hourly with no cap; or fixed-fee above envelope with no negotiation |
| 4 | **Timeline confidence (4–6 weeks for full opinion, Q1 milestoned earlier)** | **10%** | Commits to Q1 in 2–3 weeks, full opinion in 4–6 weeks, with named delivery dates | Vague timeline; cannot commit to Q1 milestone |
| 5 | **Reliance terms (Atlas + investors + auditors)** | **10%** | Standard reliance language accepted, indemnity reasonable | Refuses reliance beyond Atlas; over-broad indemnity ask |
| 6 | **NLRC and state-regulator working knowledge** | **10%** | Demonstrates current, specific knowledge of NLRC posture and federal-vs-Lagos dynamics in §6 of brief; offers informal intelligence | Generic; no demonstrated practitioner-level insight |
| 7 | **Communication style + founder fit** | **10%** | Response is well-structured, surfaces issues we hadn't asked, treats founder as sophisticated client | Boilerplate; defensive scoping; talks down |
| 8 | **Conflict cleared** | **5%** | Cleared cleanly | Cleared with disclosures Atlas needs to evaluate |

**Total: 100%.** Weighted score per firm = Σ(criterion score × weight).

### Why these weights

- **Substantive expertise dominates (25%)** because the rest is undone by a wrong opinion on Q1.
- **Partner-led delivery (15%)** because a partner-promised, associate-delivered engagement is the most common dissatisfier in Nigerian legal procurement.
- **Fee discipline (15%)** matters because open-ended hourly destroys the predictability Phase 1 planning needs.
- **NLRC working knowledge (10%)** is high but not dominant — it's a tiebreaker among substantively qualified firms.
- **Communication fit (10%)** is non-trivial because S1408661 will work with this partner for 6+ weeks of intense back-and-forth and (later) for ongoing matters.

### Configurable

These weights are **defaults Mary recommends**. S1408661 should review and adjust before scoring. Common adjustments:
- Raise weight on (1) if confidence in the regulatory ambiguity is especially low.
- Raise weight on (3) if fee envelope is tight.
- Lower weight on (6) if you separately have informal NLRC intelligence (e.g. via investor network).

### Cost ceiling (set before RFP transmission)

Atlas should set an **internal fee ceiling** before sending the RFP and not disclose it. Mary recommends:
- **Q1 (Critical) ceiling: ~£8,000–£12,000 equivalent (₦16M–₦24M at current rate).**
- **Q2–Q7 bundle ceiling: ~£12,000–£20,000 equivalent.**
- **Q8 (light touch) ceiling: ~£1,500–£3,000 equivalent.**
- **Total engagement ceiling: ~£25,000–£35,000.**

These are practitioner-norm ranges for Tier-1 Nigerian firm work; boutiques may come in 30–40% below; out-of-range proposals should be questioned, not auto-rejected. **Confirm these with one informal sounding before transmission** if S1408661 has access to anyone who has commissioned comparable work recently.

---

## 5. Stage 4 — Interviews and reference checks (Days 9–11)

### Score, then interview top 2

After scoring (Day 8), the top 2 firms advance to interview. Bottom 2 receive a polite "not progressing" email; keep them warm for future matters.

### Interview format (60 min per firm)

- **00–10 min** — partner introduces themselves and their team's relevant experience (don't accept marketing slides; ask for anonymised case discussion).
- **10–30 min** — partner walks through their proposed approach to Q1 specifically (Atlas listens for: do they distinguish prize competition from lottery in Nigerian law correctly? do they reference NLRA sections? do they cite case law or NLRC guidance?). This is the most discriminating signal.
- **30–45 min** — Atlas asks: who exactly will do the work? what's their backup if the named partner is suddenly unavailable? how do they handle scope expansion?
- **45–55 min** — Atlas asks the §6 "counsel intelligence" questions from the engagement brief. Listen for substance.
- **55–60 min** — close: next steps, references.

### Reference checks (2 per firm, 30 min each)

Ask each firm for **2 references** from comparable matters in the past 24 months. Speak to both. Questions:

1. What did counsel deliver and was it on time?
2. Did the named partner do the work or hand to associates?
3. Was the fee proposal honoured, or did scope expansion produce surprise invoices?
4. Would you re-engage?
5. What surprised you (good or bad) about working with this firm?

A firm that cannot produce 2 comparable references is a yellow flag — not necessarily a stop, but worth probing.

---

## 6. Stage 5 — Decision and engagement (Days 12–15)

### Decision matrix

Combine post-interview revised scores + reference findings into a final decision matrix. Mary's template:

```markdown
| Criterion | Weight | Firm A score | Firm B score |
|---|---|---|---|
| Substantive expertise | 25% | 4 | 5 |
| Partner-led delivery | 15% | 5 | 3 |
| Fee | 15% | 4 | 4 |
| Timeline | 10% | 4 | 5 |
| Reliance | 10% | 5 | 5 |
| NLRC working knowledge | 10% | 3 | 5 |
| Communication / founder fit | 10% | 5 | 3 |
| Conflict cleared | 5% | 5 | 5 |
| **Weighted total** | **100%** | **4.30** | **4.30** |
| Reference signal | — | 2/2 strong | 1/2 mixed |
| Final decision rationale | — | [pick + 1-paragraph why] | [non-pick + 1-paragraph why] |
```

If weighted scores tie or are within 0.2 of each other, **reference signal is the tiebreaker**.

If weighted scores are still close after references, **partner-led delivery (criterion 2) is the second tiebreaker** — Atlas would rather have the right partner at a marginally less-deep firm than a generalist partner at a deeper firm.

### Engagement letter — non-negotiables

Before signing, confirm the engagement letter contains:

- ✅ Fixed-fee or capped-fee structure matching the RFP response.
- ✅ Reliance language covering Atlas, named investors, and statutory auditors.
- ✅ Q1 as a milestone with a named delivery date.
- ✅ Conflicts clause requiring counsel to disclose new conflicts arising during the engagement.
- ✅ Confidentiality at least matching the NDA terms.
- ✅ Termination right for Atlas if scope materially shifts.
- ⚠️ Indemnity capped at fees paid (refuse uncapped indemnity).
- ⚠️ Out-of-scope work requires written change-order before billable hours begin (refuse "scope creep is billed as incurred" language).

### Decision logging

Final decision and rationale recorded at:
`_bmad-output/planning-artifacts/legal/counsel-selection-decision.md`

This becomes an audit-trail artefact for investors and (later) auditors. Mary recommends a single page covering: shortlist, scored matrix, interview findings, reference findings, named partner, fee, engagement letter date, and the *reason* for the pick (not just the score).

---

## 7. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| All 4 firms decline (conflict / capacity) | Low | Have 2 backup names ready before transmission |
| All 4 fee proposals exceed ceiling | Medium | Negotiate, or re-scope (Q1 only as first tranche; Q2–Q7 as second engagement) |
| Top-scored firm cannot start in the engagement window | Medium | Always interview top 2, not just top 1; have a fallback ready |
| Named partner leaves the firm mid-engagement | Low but consequential | Engagement letter should permit Atlas termination if named partner exits; secure backup at engagement-letter stage |
| Counsel's opinion contradicts Atlas's working hypothesis on Q1 (prize-competition model rejected) | Material | This is exactly what we're paying for — but Atlas should pre-think the licensed-lottery pivot path so a rejection doesn't catch the programme flat-footed. Mary recommends a 2-page "Plan B" outline before counsel's opinion lands |
| Founder time over-runs (>8 hours across 2 weeks) | High | The process is well-scoped to 8h — if it's running long, the bottleneck is usually shortlist construction. Cap shortlist time at 1h and ask Mary to backfill missing candidates from public-source rankings |

---

## Appendix A — Cover email template (for transmission to each firm)

```
Subject: Project Atlas — Request for fee proposal: Nigerian regulatory opinion

Dear [Partner Name],

[Firm Name] was identified via [Channel: ranking / referral / direct recommendation by NAME] as a candidate firm for a written legal opinion on the Nigerian regulatory framework applicable to a premium prize-draw platform launching in Nigeria.

The attached Engagement Brief sets out:
- Atlas's business model and intended legal-design choices;
- Seven numbered questions for opinion (Q1 critical, Q2–Q7 high–medium, Q8 light touch);
- Engagement parameters, including target timeline (4–6 weeks) and preferred fee structure (fixed or capped).

Please confirm by [DATE = transmission + 2 days]:
1. Conflicts cleared (yes / disclosures required / cannot proceed).
2. Capacity to deliver within the proposed window.

If both confirm, please return by [DATE = transmission + 7 days]:
3. Fee proposal — fixed or capped — with breakdown per question grouping (Q1 separately; Q2–Q7 bundle; Q8 light touch).
4. Named senior partner who will lead, and their availability during the engagement window.
5. Two references from comparable matters in the past 24 months (we will reach out only if you advance to the interview stage; we will not contact references without telling you first).

An NDA is attached for execution at your earliest convenience; we will counter-execute on receipt.

Atlas is shortlisting [4] firms in parallel; we will advance two to a 60-minute interview before final selection.

Atlas's founder, [S1408661], is the primary contact for this engagement; reachable at [EMAIL] and [PHONE].

Thank you for considering this work.

Kind regards,
[S1408661]
Founder, Project Atlas
```

---

## Appendix B — Response template (sent to each firm with the cover email)

```markdown
# [Firm Name] — Response to Atlas Engagement Brief

**Responding partner:** [Name, title]
**Date:** [Date]

## 1. Conflicts
[Clear / disclosures / cannot proceed]

## 2. Capacity confirmation
[Yes / no, with engagement window]

## 3. Fee proposal
- Q1 (critical): £[amount] (fixed / capped)
- Q2–Q7 (bundle): £[amount] (fixed / capped)
- Q8 (light touch): £[amount] (fixed / capped)
- Total: £[amount]
- Out-of-scope policy: [describe]
- Disbursements: [describe]

## 4. Named partner and team
- Lead partner: [Name, CV link or short bio]
- Supporting team: [Names and roles]
- Availability commitment: [% of partner's time during engagement window]
- Backup if lead partner unavailable: [Name + arrangement]

## 5. Approach to Q1
[150–300 word substantive answer — counsel's initial view on the lottery-vs-prize-competition question under Nigerian law, including section references to the NLRA 2005 and any NLRC guidance counsel considers relevant. This is the most discriminating part of the response.]

## 6. Timeline
- Q1 milestone: [Date]
- Q2–Q7 delivery: [Date]
- Q8 light touch: [Date]
- Interim check-in: [Yes / no, when]

## 7. Reliance
- Standard reliance by Atlas: [Yes / no]
- Reliance by named investors: [Yes / no, with what restrictions]
- Reliance by statutory auditors: [Yes / no]

## 8. References
- Reference 1: [Comparable matter description; contact name and email]
- Reference 2: [Comparable matter description; contact name and email]

## 9. Anything else Atlas should know
[Free text — counsel's chance to flag adjacent issues, suggested re-scoping, or matters Atlas may have missed]
```

---

📊 *End of framework. Mary's recommendation: review the weights in §4 with your priorities, set the cost ceiling in §4 before transmission, and have Adaeze (Atlas's Compliance & Risk persona) cross-check the engagement-letter non-negotiables in §6 before any signing.*
