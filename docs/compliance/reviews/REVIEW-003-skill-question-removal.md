# Compliance Review — REVIEW-003

**Subject:** Removal of the skill question (AMEND-003); confirmation that the free entry route is not returning; consequent consumer-copy changes.
**Drafted:** 2026-11-26
**Drafted by:** ⚖️ Adaeze (atlas-compliance-risk)
**Requested by:** 📋 John, per AMEND-003 §6.1.
**Status:** Draft — pending founder acknowledgement.
**Substrate:** AMEND-003; REVIEW-001 §2.1, §3.1; REVIEW-002; `research/nigerian-draw-classification-research-2026-11-23.md`; `docs/risk-register.md` R-REG-09/11.

---

## 0. Standing caveat

Not counsel, not a legal opinion, and Nigerian gaming counsel is still not engaged. Every classification statement here is a working position derived from single-pass desk research of self-reported medium confidence.

---

## 1. Verdict

| Item | Verdict |
|---|---|
| Removing the skill question | **Approved.** |
| Free route confirmed not returning | **Approved.** |
| Consumer copy changes | **Approved — and better than what they replace.** |
| Resulting compliance posture | **Approved with a recorded concentration of risk (§4).** |

**I approve this without reservation on the merits, which I have not been able to say about a change to the legal model before now.**

## 2. Why removing it is right, not merely acceptable

I rejected this skill question for real-user launch on 2026-07-08 (REVIEW-001 §3.1): *"the question does not filter; it is theatre."* That verdict was never lifted, and REVIEW-002 §3 recorded that the project had come to rest on the one leg I had already marked as failing.

The founder has now removed it. Three reasons that is the correct call and not a retreat:

1. **It never worked as a control.** Four-option multiple choice at ~25% blind pass, a small pool, per-minute rotation allowing immediate retries. My own §3.2 rotation invariants were never built. It filtered nobody.
2. **There was nothing for it to qualify for.** The 2026-11-23 research found no skill carve-out in the governing State law. Even a genuinely hard question would have bought Atlas nothing in Nigeria.
3. **It may have been adverse.** The Lagos advertising code appears to treat a suggestion that skill influences a game of chance as a misleading claim. A control that provides no protection while creating its own exposure is strictly worse than no control.

Atlas was paying conversion friction for all three of those. Removing it is the first change this year that reduces both cost **and** risk.

**Consequence I welcome:** `docs/compliance/skill-questions.md` is **cancelled, not overdue.** It was my artefact and it was late. It is now unnecessary, which is a better outcome than my delivering it.

## 3. Consumer copy — approved, with the reasoning recorded

AMEND-003 §2 asked me the right question: does the "prize competition" positioning survive?

**It does not, and the copy is correct to stop asserting it.**

My REVIEW-001 §2.1 ruling was that Atlas must not hold itself out as the arbiter of its own regulatory classification. That ruling was written when Atlas had two mechanics arguably supporting the claim. It now has none. Continuing to call itself a prize competition would be a bare assertion about the law, made by the party it benefits, with nothing behind it.

What landed instead is right:

| Was | Now |
|---|---|
| "A prize competition, not a lottery." | "Every draw is provably fair — and you can check it yourself." |
| "Provably fair prize competitions · Nigeria" | "Provably fair draws · Nigeria" |
| "Atlas is a prize competition. It should be fun…" | "Entering an Atlas draw should be fun…" |
| The whole "The skill question" section | Removed |

Each replacement describes **a mechanic or a verifiable property** rather than a legal conclusion. "Provably fair" is a claim Atlas can actually substantiate — the commit-reveal protocol and the public verifier make it checkable by anyone, which is the opposite of a classification assertion.

**The copy bans on "lottery", "raffle" and "luck of the draw" remain in force and unchanged.** Nothing here relaxes them. An unlicensed operator using the word "lottery" about itself would be worse off, not better.

One thing I checked specifically: the new entry screen in the mobile app tells the user the entry price before the purchase action and states that entries are not refundable after close. Nobody asked me to require that. It is right.

## 4. The risk this concentrates — recorded, not objected to

Atlas now has **no carve-out argument of any kind.** Its entire legal basis is a State gaming licence it does not yet hold.

I have opened **R-REG-11 (⚫)** for this and closed R-REG-09. Both the character and the shape of the risk have changed:

- **Before:** two arguable defences, both probably inert, propping up an unlicensed operation while nobody checked.
- **Now:** one correct answer — the licence — not yet obtained, with no fallback if refused, delayed, or priced beyond reach.

The second is more honest and more concentrated. I would not trade back.

**What this does not change, and I want it in writing:** the PRD §1 hard prerequisite stands in full, and AMEND-001 §2.2 extended it to bar **public marketing spend** as well as code against a real payment rail, because advertising an unlicensed scheme may itself be an offence. Removing the mechanics does not bring launch any closer. It clarifies what launch depends on.

## 5. Conditions

None blocking. Two standing:

1. **No engineering may assume a licence outcome.** If a design decision only makes sense under a particular licence category, it waits for counsel Q7/Q1.
2. **The "prize competition" phrase does not return to consumer copy** without counsel confirming the classification. It survives in historical artefacts — PRD, wireframes, prior reviews — as the record of what was once believed, which is correct and must not be edited away.

## 6. Position

Approved. This is the first change to the legal model I can sign off without attaching a standing objection, and it is worth saying why: it stops Atlas claiming protections it does not have. That has been the single recurring defect in this project — the free route with no P.O. box, self-exclusion with no registry, age checks that did not run, a skill question that filtered nobody. Four instances, one pattern.

Removing the last of them leaves Atlas with an honest description of itself and one real thing to go and get.

— ⚖️ Adaeze
