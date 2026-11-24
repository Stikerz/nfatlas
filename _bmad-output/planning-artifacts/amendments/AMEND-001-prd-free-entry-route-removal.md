# Amendment Proposal AMEND-001 — PRD §1 and §3.1

**Artefact:** `_bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md`
**Sections:** §1 (The product decision), §1 Nigerian legal caveat, §3.1 (Prize-competition mechanics)
**Proposed:** 2026-11-24
**Proposed by:** ⚖️ Adaeze (atlas-compliance-risk)
**Owner agent (must review per `delivery-framework.md §12` step 2):** 📋 **John** (bmad-agent-pm)
**Approver:** S1408661 (Founder / Engineering Lead)
**Status:** **PROPOSED — NOT APPLIED.** The PRD is unchanged on disk.

---

## 0. Process note — a §12 breach to record, not to hide

`delivery-framework.md §12` carries a hard rule:

> **no in-flight code change retro-justifies an artefact change.** Spec changes first, then code follows.

**That rule was broken.** The free-entry route was unwired in code on 2026-11-23, on founder instruction, before any amendment to the PRD was proposed. This document is the spec catching up to the code, which is the wrong order.

I am recording it rather than presenting this as a normal amendment because the §12 rule exists precisely to stop specifications drifting into fiction, and a silent retro-fit would be the second instance this week of a document describing something other than reality. The founder has the authority to direct the change; the sequencing is still a process failure and belongs in the log.

**Recommended remedy:** none beyond this note. Reverting working code to restore process order would be theatre. But the next change of this class should go spec-first, and if a decision is urgent enough to need code immediately, the amendment proposal should be opened in the same session rather than a day later.

---

## 1. Why this amendment is needed

Two independent reasons, either sufficient:

1. **The free-entry route no longer exists.** Removed by founder decision 2026-11-23 (Tier 3, `AINE-AGENTS.md §5`). PRD §1 presents it as one of two load-bearing mechanics and §3.1 specifies its operation in detail. Both now describe a capability the product does not have.
2. **The route never actually operated.** Per REVIEW-001 §6.1 and R-FREE-01, no P.O. box was ever leased. §3.1's postal mechanic was never true, not merely newly untrue.

A third reason affects §1's legal caveat specifically: the National Lottery Act 2005 was nullified by the Supreme Court on 22 November 2024 and the NLRC holds no national licensing authority. §1's caveat names both.

---

## 2. Proposed changes

### 2.1 §1 — The product decision

**Current:**

> Every draw operates under the same two mechanics that let UK operators (BOTB, Omaze, Raffle House, Aspire) sit outside gambling regulation:
> 1. **A free entry route on every draw** […]
> 2. **A skill question on every paid entry** […]

**Proposed:**

> Atlas is positioned as a **prize competition** platform, not a lottery and not gambling. **Whether Nigerian law accepts that positioning is unresolved — see the legal caveat below, which governs this section.**
>
> Atlas's design was modelled on UK operators (BOTB, Omaze, Raffle House, Aspire) who sit outside gambling regulation on two mechanics. **As of 2026-11-23 Atlas operates one of them:**
>
> 1. **A skill question on every paid entry,** requiring genuine knowledge or judgment. "What colour is the sky" does not qualify — the question must be substantive enough that a non-trivial fraction of entrants get it wrong if they don't try. **The implementation does not currently meet this standard: REVIEW-001 §3.1 rejected it for real-user launch on 2026-07-08 and that verdict has not been lifted.**
> 2. ~~A free entry route on every draw.~~ **Removed 2026-11-23** by founder decision. Note for the record that it was never operable — no P.O. box was ever leased (R-FREE-01).
>
> **Marketing copy must never use "lottery," "raffle," "luck of the draw," or equivalent.** Compliance copy is part of the design system, not an afterthought.

*Rationale:* states what is true, preserves the history rather than erasing it, and stops the PRD asserting a standard the build does not meet. The copy ban is retained verbatim — nothing about the classification question weakens it.

### 2.2 §1 — Nigerian legal caveat

**Current:** names the National Lottery Act 2005 and NLRC licensing as the risk.

**Proposed:**

> ### Nigerian legal caveat (must be resolved before launch)
>
> **Rewritten 2026-11-24. The 2026-06-29 version of this caveat was framed against a statute that no longer exists.**
>
> The prize-competition carve-out is **UK-derived and may have no Nigerian equivalent at all.** The National Lottery Act 2005 was nullified by the Supreme Court of Nigeria on 22 November 2024 (*AG Lagos State & Ors v AG Federation*, SC/1/2008); lottery and gaming are now exclusively State matters and the NLRC holds no national licensing authority. The operative law in Atlas's launch market is the **Lagos State Lotteries and Gaming Authority Law 2021**, which on Atlas's own desk research defines "Gaming" as any scheme distributing prizes by lot or chance **with no payment element**, and expressly classes promotional competitions as "Other lotteries". On that reading **neither a skill question nor a free entry route removes Atlas from the perimeter, and a State licence is required.**
>
> See `research/nigerian-draw-classification-research-2026-11-23.md`. That research is single-pass desk work, not legal advice, and self-reports medium confidence on several findings.
>
> **Hard prerequisite for V1 (unchanged and reaffirmed):** Nigerian gaming counsel signs off on the model and any licence/permit obligations **before any code touches a real payment rail.** Counsel has **not** been engaged as at 2026-11-24.
>
> **New prerequisite:** because advertising or promoting an unlicensed scheme may itself be an offence under the Lagos regime, **no public marketing spend before counsel sign-off either.** The original caveat gated code; it should have gated promotion too.

### 2.3 §3.1 — Prize-competition mechanics

**Proposed:** strike bullets 1 and 4; amend bullet 3; add a retention note.

> - ~~Every draw has a **free entry route**. V1 free route: **postal entry** […] One free entry per person per draw.~~ **Struck 2026-11-23.** Never implemented as specified — no P.O. box was leased (R-FREE-01).
> - Every paid entry path requires a **skill question** answered before payment confirmation. Wrong answer = entry rejected, no charge. Skill questions are configured per draw by the operator (multiple-choice from a small pool, rotated). **The rotation and difficulty constraints in REVIEW-001 §3.2 are a code-enforced Ticket-module contract and remain unbuilt.**
> - **Tickets are stored with an `entry_source` field** (`paid` | `free`). The draw engine treats both identically. Audit logs and the post-draw proof include the split. **The `'free'` value and the `free_entry_slips` table are retained deliberately** — historical tickets carry it and published proofs report the split. Not to be dropped. *(Corrects a long-standing drift: the PRD said `postal_free`; the schema has always said `free`.)*
> - ~~Every draw page displays the free-entry route prominently~~ → **Every draw page displays the total entries at close and the skill-question requirement.**

---

## 3. Cascading implications (§12 step 3)

John to confirm; my assessment:

| Artefact / area | Impact |
|---|---|
| `delivery-framework.md` §§49-52, 122, 131, 260, 321, 394 | Phase gates referencing free-route operationalisation and Legal-Counsel-approved free-entry copy. **Needs its own amendment — Winston + John.** |
| PRD §2, §4, §10 | "Enter for free via a documented free-entry route"; Ticket module description; Phase-0 exit item "Free-entry route operationalised: P.O. box leased…". All stale. |
| `docs/adr/ADR-004` §51, `ADR-005` §67 | Free-entry references. **Winston's amendment, not John's.** |
| Design wireframes 02, 03, 10, 15 | Specify surfaces that no longer exist. Superseding notices, not body edits — Sally. |
| Market sizing / business plan | R-REG-02: per-State licensing may reduce V1 addressable market to Lagos. **Not a PRD section, but it invalidates any forecast built on "Nigeria only".** |
| Code | Already done (2026-11-23). No follow-up. |

---

## 4. What I am NOT proposing

- **No change to the copy bans.** They stand regardless of classification.
- **No rewrite of historical artefacts.** Wireframes, checkpoints, build plans, demo plan and REVIEW-001 record what was decided at the time.
- **No removal of the `entry_source` enum value or the `free_entry_slips` table.** See §2.3.
- **No reinstatement of the free route.** That is a founder decision and counsel Q1.6 asks whether it would change the analysis. If counsel says it is load-bearing, this amendment gets reversed — roughly a week of engineering.

---

## 5. Action required

1. 📋 **John** — review as PRD owner per §12 step 2. Approve, amend, or reject.
2. **Founder** — approve as EL. Note §0: this is a spec catching up to shipped code.
3. On approval — apply to the PRD, open the follow-ups in §3, and record in `docs/AI-INTEGRATION-LOG.md` with reviewer and approver per §12 step 4.

— ⚖️ Adaeze
