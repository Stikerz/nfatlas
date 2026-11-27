# Amendment Proposal AMEND-003 — PRD §1, §2, §3.1, §10

**Artefact:** `_bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md`
**Proposed:** 2026-11-26
**Proposed by:** 📋 John (bmad-agent-pm), on founder instruction
**Owner agent:** 📋 John (PRD owner — self-reviewed; see §5 on why that is acceptable here)
**Mandatory reviewer:** ⚖️ Adaeze (regulatory copy, `AINE-AGENTS.md §6`)
**Approver:** S1408661 (Founder / EL)
**Status:** PROPOSED. PRD unchanged on disk.
**Supersedes in part:** AMEND-001 §2.1 (which retained the skill question as the one surviving mechanic).

---

## 0. Founder decisions being recorded

Two, taken 2026-11-26 after reviewing the Q1/Q7 explanation:

1. **The skill question is removed.** The founder accepts Atlas's own Q1.5 hypothesis — that the skill question achieves nothing under the governing State law, and may carry its own exposure under the Lagos advertising code's treatment of "skill influences chance" claims. Rather than wait for counsel to confirm, the founder has decided to stop paying the conversion cost of a control that buys nothing.
2. **The free entry route is not coming back.** AMEND-001 struck it; counsel Q1.6 asked whether reinstating it would change the analysis. The founder has pre-empted that: it stays removed regardless of the answer.
3. **The licence is being pursued separately**, outside this workstream.

## 1. What this means — stated plainly, because it is a larger change than it looks

PRD §1 named two mechanics that let UK operators sit outside gambling regulation. **After this amendment, Atlas has neither.**

Atlas is no longer attempting to sit outside the regulated perimeter. It is a **paid prize draw that intends to operate under a State gaming licence.** Pay, chance, prize — and a licence that makes that lawful.

**This is more coherent than what preceded it, not less.** The carve-out strategy was resting on two mechanics that the 2026-11-23 research indicates are both legally inert in Nigeria: the governing definition of "Gaming" needs only chance and a prize, with no payment element for a free route to negate and no skill exemption for a question to qualify for. Carrying both was paying real costs — conversion friction, postal operations, engineering — for protection that probably did not exist. Dropping them and buying a licence is the honest version of the same business.

**What does not change: Atlas is not licensed yet.** Until it is, the PRD §1 hard prerequisite stands in full — no code touches a real payment rail, and (per AMEND-001 §2.2) no public marketing spend either, since advertising an unlicensed scheme may itself be an offence.

## 2. Consequence that needs a decision from Adaeze, not from me

**The "prize competition, not a lottery" positioning no longer has a mechanism behind it.**

That phrase is in PRD §1, the README, the page titles, the metadata and the brand lexicon, and the copy bans on "lottery", "raffle" and "luck" were built on top of it. If Atlas is a licensed gaming operator, calling itself a prize competition is a classification claim with nothing supporting it.

I am **not** proposing new marketing language. REVIEW-001 §2.1 already settled the governing principle and it does the work here:

> **Atlas must not hold itself out as the arbiter of its own regulatory classification.**

So the minimum safe change is to **stop asserting a classification at all** and describe the mechanic instead. Whether the brand keeps the phrase in marketing is Adaeze's call with counsel, not mine, and it is gated behind which licence category Atlas lands in.

**The copy bans stay in force unchanged.** Nothing here licenses the word "lottery" in consumer copy — if anything, an unlicensed operator using it is worse.

## 3. Proposed changes

### 3.1 §1 — The product decision

> Atlas is a **paid prize draw platform** intending to operate under a Nigerian State gaming licence.
>
> **It does not rely on any exemption, carve-out or mechanic to sit outside gambling regulation.** Two such mechanics were specified in the 2026-06-29 version of this PRD and both have been removed:
>
> 1. ~~A skill question on every paid entry.~~ **Removed 2026-11-26.** The implementation never met the standard this PRD set (REVIEW-001 §3.1 rejected it for real-user launch on 2026-07-08), and the 2026-11-23 research found no skill carve-out in the governing State law for it to qualify for. It was friction with no legal return, and may have carried exposure of its own under the Lagos advertising code.
> 2. ~~A free entry route on every draw.~~ **Removed 2026-11-23.** Never operable — no P.O. box was ever leased (R-FREE-01). Confirmed 2026-11-26 as not returning, irrespective of counsel Q1.6.
>
> **Marketing copy must never use "lottery," "raffle," "luck of the draw," or equivalent.** Unchanged and still binding. Compliance copy is part of the design system, not an afterthought.
>
> **Atlas must not assert its own regulatory classification in consumer copy** (REVIEW-001 §2.1). Describe the mechanic; let the licence speak to the classification.

### 3.2 §2 — scope bullets

> - ~~Answer the skill question, receive a ticket~~ → **Buy an entry and receive a ticket, visible in their account.**
> - Operator draw configuration: ~~prize, ticket price, max entries, close date, draw date, skill question~~ → **prize, ticket price, close date, draw date.**

*(Subsumes AMEND-001 §6.1 and §6.2, which struck the free-route and max-entries bullets.)*

### 3.3 §3.1 — mechanics

Section retitled **"Draw mechanics"** (from "Prize-competition mechanics"), with the skill-question and free-route bullets struck and this added:

> - **Lawfulness rests on holding a State gaming licence, not on draw mechanics.** No mechanic in this section is load-bearing for classification. Do not reintroduce one as a compliance measure without an amendment and counsel sign-off.

`entry_source` retention is unchanged from AMEND-001 §2.3 — the column, the `'free'` value and the `free_entry_slips` table stay for historical tickets and published proofs.

### 3.4 §10 — Phase 0 exit criteria

> - ~~Skill-question content set drafted and reviewed by counsel.~~ **Struck 2026-11-26** — no skill question.
> - ~~Free-entry route operationalised…~~ **Struck 2026-11-23** (AMEND-001 §6.4).
> - **Nigerian gaming licence application submitted**, and counsel Q7/Q1 answered. This is now the whole of the Phase 0 legal gate.

## 4. What this closes

| Item | Effect |
|---|---|
| **R-REG-09** (skill question is sole mechanism and fails our own standard) | **Closes.** There is no skill question to fail a standard. Replaced by R-REG-11 — operating unlicensed while the application is pending |
| REVIEW-001 §3.1 / §3.2 remediation | Moot. No question pool to harden, no rotation invariants to build |
| `docs/compliance/skill-questions.md` | **No longer required.** Adaeze's overdue artefact, cancelled rather than delivered |
| Counsel Q1.5 | Answered by the founder instead. Keep it in the brief — counsel should confirm removal carries no residual exposure |
| Counsel Q1.6 | Keep, but note the founder's position: the free route is not returning whatever the answer |

## 5. On self-review

I am the PRD owner reviewing my own proposal, which `§12` step 2 does not contemplate. I am recording it rather than disguising it: this amendment carries no product judgement of mine — it transcribes two founder decisions and works out their consequences. The judgement that matters is Adaeze's, on §2, and she is a mandatory reviewer.

If the founder would rather Winston review it as an independent agent, that is a reasonable ask and costs an hour.

## 6. Action required

1. ⚖️ **Adaeze** — §2 and §3.1. Does removing the last mechanic change what consumer copy may say, and does the "prize competition" phrase survive?
2. **Founder** — approve as EL, then AMEND-001 and AMEND-003 apply together.
3. On approval — apply both, open AMEND-002 (market scope) when counsel Q7.2 lands.

— 📋 John
