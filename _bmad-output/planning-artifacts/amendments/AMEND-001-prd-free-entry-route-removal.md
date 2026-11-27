# Amendment Proposal AMEND-001 — PRD §1 and §3.1

**Artefact:** `_bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md`
**Sections:** §1 (The product decision), §1 Nigerian legal caveat, §3.1 (Prize-competition mechanics)
**Proposed:** 2026-11-24
**Proposed by:** ⚖️ Adaeze (atlas-compliance-risk)
**Owner agent (must review per `delivery-framework.md §12` step 2):** 📋 **John** (bmad-agent-pm)
**Approver:** S1408661 (Founder / Engineering Lead)
**Status:** **APPLIED 2026-11-27.** Founder approved as EL; the PRD now reflects this amendment.

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

---

# Owner review — 📋 John (PRD owner), 2026-11-26

Per `delivery-framework.md §12` step 2.

## Verdict: APPROVED WITH REQUIRED ADDITIONS — not yet applicable

The §1 and §3.1 wording in §2 of this proposal is right and I would land it as drafted. But **the proposal is incomplete.** It amends two sections of a document that is wrong in five places, and applying it as-is would leave the PRD internally inconsistent — §1 saying one mechanic, §2 still promising users a free entry route, §3.2 still promising a protection that does not exist.

An amendment that half-corrects a specification is worse than one that has not been written, because it looks done. §6 below supplies the missing sections. With those, I approve.

I also have a product question that sits outside the amendment process entirely — §7.

## 1. What the proposal gets right

- Striking through rather than deleting. The PRD should record that a free entry route was specified and why it went, not pretend it never existed. Future readers need the decision, not a clean document.
- §1's new sentence that the legal caveat **governs** the product decision rather than footnoting it. That inversion is correct and overdue.
- Recording the §12 breach in §0 instead of quietly retro-fitting. Noted, accepted, and I expect the next one to go spec-first.
- Correcting `entry_source` from `postal_free` to `free`. That drift has been live since W5 and nobody caught it because nobody reads a spec against a schema.

## 2. Required addition — §3.2 is untouched and is now false

This is the significant omission.

PRD §3.2 currently reads:

> Self-exclusion: a user can self-exclude permanently from settings. **Re-registration with the same BVN is blocked.**

ADR-010's Context section cites **§3.2 as the requirement it exists to satisfy**. Its 2026-11-24 amendment then split delivery into two phases and blocked Phase B on ADR-007. So §3.2's first sentence is now true (Phase A shipped, including the settings entry point); **its second sentence is not deliverable and has no date.**

AMEND-001 does not mention §3.2. It amends the section describing a feature that was *removed* while leaving untouched the section describing a protection that was *never built* — the defect that produced REVIEW-002 §6 in the first place.

## 3. Required addition — §2 still sells the free route to users

§2 "What V1 is" lists, as a thing V1 does for a user:

> - Enter for free via a documented free-entry route (see §3).

That is a user-facing scope commitment, not a mechanic detail. It belongs in this amendment, and the proposal's cascade table lists §2 without proposing wording for it.

The same bullet list also has an operator line: *"Configure and schedule a draw (prize, ticket price, **max entries**, close date, draw date, skill question)."* `entries_cap` was found unenforced, and the founder decided against caps. Another stale commitment.

## 4. Required addition — §10 contains an exit criterion that can never be met

Phase 0 exit criteria include:

> - Free-entry route operationalised: P.O. box leased, entry slip designed, transcription workflow documented.

Phase 0 cannot close against a criterion for a feature that no longer exists. This is a delivery blocker sitting inside a checklist where nobody will look until someone tries to declare Phase 0 done.

## 5. Disagreement — market scope is a PRD question

The proposal's cascade table lists market sizing and says *"not a PRD section, but it invalidates any forecast built on 'Nigeria only'."*

I do not accept that framing. **"Nigeria only" is a PRD scope statement** — §2 says it, §3 is written against it, and §7's V2 expansion plan depends on it. R-REG-02 now says per-State licensing may reduce V1's addressable market to Lagos. If that is right, V1's scope line is wrong, and scope lines are mine.

I am not proposing wording yet, because it turns on counsel Q7.2 (which State's law governs an online operator serving users nationwide). But it is a **tracked, open PRD amendment**, not a business-plan footnote. Recording it as AMEND-002-pending.

## 6. Proposed additional changes — required before this is applied

### 6.1 §2, consumer bullet list

> - ~~Enter for free via a documented free-entry route (see §3).~~ **Struck 2026-11-23** — the free entry route was removed. It was never operable (R-FREE-01).

### 6.2 §2, operator bullet list

> - Configure and schedule a draw (prize, ticket price, ~~max entries,~~ close date, draw date, skill question). **`entries_cap` struck 2026-11-23** — the field existed but was never enforced, and the founder decided V1 operates with no per-draw entry cap.

### 6.3 §3.2 Identity — self-exclusion

> - **Self-exclusion (Phase A, shipped 2026-11-24):** a user can permanently close their account from settings. Closure is enforced at login, at ticket purchase and at skill-question issue, and every session is revoked. **There is no reversal.**
> - **Self-exclusion (Phase B, NOT DELIVERED):** blocking re-registration by the same person requires BVN matching and is **blocked on ADR-007 (KYC), which is unbuilt.** Until Phase B ships, a closed account does not prevent the same person opening a new one with a different email and phone. **Consumer copy must not claim otherwise** — see REVIEW-002 §6.1 for the withdrawn wording.

*Rationale: the old single line conflated a shipped capability with an unbuilt one. Splitting them is what stops the copy defect recurring, because the spec now states the boundary that the test `test_phase_a_does_not_block_reregistration` enforces.*

### 6.4 §10 Phase 0 exit criteria

> - ~~Free-entry route operationalised: P.O. box leased, entry slip designed, transcription workflow documented.~~ **Struck 2026-11-23.** Never completed — no P.O. box was ever leased (R-FREE-01) — and no longer applicable.
> - **Added:** Nigerian gaming counsel engaged and Q7/Q1 answered. **This replaces the free-route criterion as the Phase 0 legal gate** and is the harder of the two.

## 7. The question this amendment cannot answer

PRD §1 is titled "The product decision". Its stated rationale was that two mechanics let UK operators sit outside gambling regulation, and Atlas would use both.

One has been removed. The other, on the 2026-11-23 research, is legally inert in Nigeria — there is no skill carve-out to qualify for. The free route, had it been built, would have been inert too: the governing definition needs only chance and a prize.

So the product decision in §1 now rests on **nothing that survives contact with the governing law.** This amendment faithfully records what changed. It does not ask whether the decision still holds — and that is the question in front of the founder, not a documentation task:

1. **Licensed operator.** If a Lagos licence is obtainable at ~₦250–400m in year one (unverified, counsel Q7.3), that is a funding round before a single entry is sold. It is a viable business. It is not the business in this PRD, and the unit economics in §5 do not survive it.
2. **Proportionate permit**, if one exists (counsel Q7.4). The research calls this the highest-leverage unknown in the engagement, and I agree — it is the difference between a startup and a licensed gaming operator.
3. **Different launch market.** Ghana, Kenya, SA. **No regulatory research exists for any of them.** Nigeria was also assumed benign for five months.

**My recommendation:** do not apply AMEND-001 or build further product against this PRD until counsel answers Q7 and Q1. Amending §1 to describe one surviving mechanic is accurate bookkeeping, but the PRD's entire premise is pending a verdict that has not been requested yet, from a firm that has not been engaged.

The smallest thing that validates the assumption here is not a feature. It is an email to a Lagos gaming firm.

## 8. Decision

**Approved subject to §6 being incorporated.** With §6.1–§6.4 added, I approve AMEND-001 as PRD owner and it passes to the founder as EL approver per §12 step 2.

**Not yet applied.** The PRD remains unchanged on disk.

Opened as follow-ups:
- **AMEND-002-pending** — V1 market scope, gated on counsel Q7.2 (§5).
- **§7 product decision review** — founder-level, gated on counsel Q1/Q7. Not an amendment.

— 📋 John


---

## Applied — 2026-11-27

Founder approved as EL. AMEND-001 is applied to `PRD.md` per `delivery-framework.md §12` step 3.

**Beyond the sections this amendment named**, the application swept the whole PRD for text describing the removed features and corrected: §2 "mobile-first prize competition platform"; §2 success criterion 2 (NLRC scrutiny); §3.3 skill-question resume window; §3.3 ticket-issue preconditions; §4 Ticket module scope; §4 module-ownership reviewer note; §10 Phase 0 counsel criterion; §10 beta-phase flows; §11 open questions 1, 4 and 5. Leaving those would have produced exactly the half-corrected specification John warned about in his owner review §1.

One correction to this amendment's own text, found during application: the §3.2 wording proposed in AMEND-001 §6.3 said closure is enforced "at login, at ticket purchase and at skill-question issue". The skill-question enforcement point no longer exists — the module was unwired by AMEND-003, so that check is unreachable. The applied text names only login and ticket purchase.

Still outstanding, and NOT part of this application:
- **`delivery-framework.md`** §§49-52, 122, 131, 260, 321, 394 still reference free-route operationalisation and Legal-Counsel-approved free-entry copy. Needs its own amendment (Winston + John).
- **ADR-004 §51, ADR-005 §67** free-entry references — Winston's amendment, not John's.
- **AMEND-002** (V1 market scope: "Nigeria only" vs per-State licensing) remains open, gated on counsel Q7.2.
