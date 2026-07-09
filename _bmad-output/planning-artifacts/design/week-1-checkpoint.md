# Project Atlas — V0.5 Design Pass, Week 1 Exit Checkpoint

**Date:** 2026-07-08 (Day 7 per `tone-doc.md §8`)
**Author:** 🎨 Sally (BMad UX Designer)
**Status:** Awaiting founder review — this is the exit gate for Week 1 of the two-week V0.5 design pass. Founder sign-off (or amendment) unblocks Week 2 which starts Day 8 (Monday-in-plan-time).
**Pairs with:** `tone-doc.md`, `tokens.md`, all wireframes 01–07, `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md`.

---

## 0. Purpose

Per `tone-doc.md §8` the Week 1 exit protocol is a founder review of *the consumer flow read as a system* — not as individual files. The ritual anchors and repeated phrases (*"You're in."* / *"Not this time."* / equal-terms mechanic phrasing / hash-typography motif / ticket-artefact language) are load-bearing across screens. Reading the wireframes as a set catches coherence issues that reading one at a time will miss.

This document is the short read that supports that review. It does not replace the wireframes; it summarises what shipped, what changed, what's blocking Week 2, and what's parked for founder decision.

---

## 1. What shipped this week

**Foundation:**
- `tone-doc.md` (Day 1 — founder-approved 2026-07-08 as-is)
- `tokens.md` (Day 2 — colour, typography, spacing, radius, elevation, cross-platform emission, anti-patterns)

**Wireframes (7):**
- `wf-01-register-otp-login.md` — Register → OTP → Password → Welcome (4 sub-screens)
- `wf-02-browse-active-draw.md` — Home + Draw detail (2 screens)
- `wf-03-free-entry-disclosure.md` — the disclosure element + explainer sheet
- `wf-04-buy-ticket-skill-payment.md` — Skill question → Order review → Paystack webview → Ticket issued → Payment result (5 sub-screens)
- `wf-05-my-tickets.md` — List + Detail (the Anchor 3 ticket-artefact moment; 2 screens)
- `wf-06-draw-completes-notification.md` — In-app banner + Reveal page + Notification centre + 3 email templates
- `wf-07-winner-claim-start.md` — Intro + 4 form steps + Confirmation (6 screens)

**Compliance:**
- `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md` — Adaeze's full pass on wf-03, 04, 06, 07 (Day 7)

Consumer surface is drafted end-to-end for V0.5 flagship flow steps 1–7 (register → browse → skill+payment → ticket artefact → notification → winner claim start).

---

## 2. What changed after Adaeze's review

Full audit trail in each wireframe's `Amended:` header; concise summary here.

**Wording changes:**
- The first-person legal-classification claim *"a prize competition is not a lottery"* is removed from consumer copy (wf-03 §3.4 lede, wf-04 §2.4 skill-question intro). Replaced with mechanic-descriptive language: *"entries are earned on the same terms whether you pay or not"* / *"Atlas competitions are decided on the same terms whether you pay or not"*. The classification claim moves to T&Cs where it is properly framed as a company position and can be updated by counsel. Small tone loss; correct trade.
- BVN help copy on wf-07 §5.3 now discloses the self-exclusion purpose (per NDPA transparency): *"Atlas uses it to confirm your bank account matches your identity, and to check our self-exclusion register."*

**List changes:**
- Voter's card removed from the accepted-ID list on wf-07 §5.3; NIN promoted to primary. NIN slip retained as fallback.

**Structural changes:**
- wf-01: DOB field added to Screen 1.1 with 18+ hard-stop. Downstream wf-07 §4.1 now shows DOB as read-only pre-fill.
- wf-07 §7.5 consent: single bundled checkbox replaced by two required + one optional checkbox (truthfulness attestation / data-processing consent / optional publication consent).
- wf-07 §8.3 rejected-state: four state variants drafted by Adaeze added (kyc_failed / bvn_mismatch / under_review / self_excluded — the last carries a mental-health helpline reference).

**Removals:**
- Winning-route disclosure (*"the winning ticket came from the paid/free route"*) removed from wf-03 §2.3 post-reveal state and confirmed not present in wf-06 §3.5. Held for V1 pending counsel. Entry-count paid/free split (`1,160 paid · 87 via free route`) retained on all surfaces.

**Flags without removals:**
- SLA copy *"usually within 1 working day"* on wf-07 §8.4 approved for V0.5 demo, **rejected for real-user launch** — swap to *"Most claims are reviewed within a few working days."* until Atlas has measured cadence.
- Skill-question difficulty (*"Capital of Nigeria"*) approved for V0.5 demo, **rejected for real-user launch** — Adaeze owns the Phase 3 question-pool architecture at `docs/compliance/skill-questions.md`.

---

## 3. What Week 2 covers (Day 8–14 per tone-doc §8)

- **Day 8:** Operator wireframes 8–9 — admin login + create draw.
- **Day 9:** Operator wireframes 10–12 — transcribe free entry, close draw, reveal draw. **Adaeze flagged wf-10 specifically:** the transcription flow must produce `ticket` rows structurally identical to paid-route rows except for `entry_source`. Will flag her when the wireframe is a draft.
- **Day 10:** Operator wireframe 13 — view audit log (admin-facing).
- **Day 11:** **The wow moment** — public verification page (wireframe 12). Adaeze wants to review this as a working draft, not a finished one — I will send it her way mid-draft.
- **Day 12:** Trust-story pages 15–16 — prize-competition explainer + responsible-play + free-entry-route detail page. Copy for all three drafted here. This is where the T&Cs-adjacent copy from wf-03 lede substitution surfaces properly.
- **Day 13:** Mini design system consolidation — 15 core components documented as specs (props, states, accessibility notes).
- **Day 14:** Week 2 exit gate — founder review of all wireframes + design system. Handoff to Amelia (Week 3 backend build starts).

**None of Adaeze's actions block Week 2 from starting.** The compliance-conditional items are all Phase 3 concerns (real-user launch), not V0.5 investor demo blockers.

---

## 4. What I need from founder to close Week 1

Six decisions parked by Adaeze in REVIEW-001 §7 that specifically require founder input:

1. **Concur or reject the *"prize competition is not a lottery"* wording removal from consumer copy** (REVIEW-001 §2.1, §3.3). I've applied the substitution across wf-03 and wf-04; the changes are reversible in the next commit if you'd rather push back on Adaeze here. I concur with Adaeze's reasoning: making a legal-classification claim in first person, in consumer copy, before counsel has confirmed NLRC posture, is a category regulators dislike. My tone attachment to the original sentence is real but the trade is correct.

2. **Confirm winning-route disclosure hold** for V1 pending counsel (REVIEW-001 §2.3). I applied the removal; entry-count split retained. This was one of my strongest design instincts (a trust-story move) but Adaeze's reasoning on adverse-selection appearance risk in small samples is sound. Hold accepted; revisit V1 with counsel opinion.

3. **Confirm the winner-payout SLA posture** — is *"paid within 5 working days of completed claim"* Atlas's commitment (REVIEW-001 §4.2)? If yes, current wording (as amended) ships. If not, Adaeze needs to know what Atlas actually commits to before wf-07 §8.4 finalises.

4. **Prize-value thresholds for AML additions** (REVIEW-001 §4.1) — working position is ₦5M aligning with AINE-AGENTS.md §6 founder-approval threshold. Confirm or set. This affects the tax attestation + source-of-funds attestation copy that Adaeze will land for real-user launch.

5. **Timeline SLA on claim review** (REVIEW-001 §5.7) — for V0.5 demo I've kept *"usually within 1 working day"* per tone doc; for real launch I've flagged the swap to *"Most claims are reviewed within a few working days."* Approve the conservative wording as the real-launch default, or push for a measured commitment once we have data.

6. **Move the counsel-engagement brief from Draft to Sent within the next two weeks.** Adaeze's ceiling on this review — and on every downstream compliance review — is the fact that Nigerian counsel has not yet been engaged. `_bmad-output/planning-artifacts/legal/counsel-engagement-brief.md` has been Draft since 2026-06-30. Every "Approved with conditions" in REVIEW-001 downgrades to "Pending counsel opinion" for real-user launch until that brief lands. **This is the single biggest thing between the project and Phase 3.**

---

## 5. What Week 2 will need before it can be reviewed as a system

The mid-Week-2 blockers (not Week 1 blockers, flagged for founder visibility):

- **Adaeze on wf-12 (public proof page, Day 11):** she wants a working-draft review, not a finished-draft review. I will route her the wireframe as soon as it has structure, not when it has polish. If she flags something structural, I'd rather rework at Day 11 than Day 14.
- **Adaeze on wf-10 (transcribe free entry, Day 9):** the transcription-flow-produces-identical-tickets invariant needs the operator UI to make this obviously easy to do right and obviously hard to do wrong. Adaeze reviewer slot reserved.
- **Amelia's confirmation on 5 contract points** parked in REVIEW-001 §7 (ticket-module rotation invariant, 3-strike rate limit, entry-source parity, uniform-random selection, NIN vendor coverage). These aren't design-blocking but if Amelia surfaces "backend can't do that" on any of them, the affected wireframes need revisiting.

---

## 6. What Adaeze parked with other agents (non-blocking for design)

Recording here so nothing gets forgotten between now and Phase 3:

- **💻 Amelia** — 7 contract points across Ticket, Draw Engine, KYC adapter, claim state machine, and public URL structure.
- **🏗️ Winston** — 2 potential ADR amendments (ADR-006 uniform-random confirmation, ADR-003 entry-source column explicitness).
- **🛡️ Tobi** — 4 infra items for real-launch (SPF/DKIM/DMARC, S3 SSE-KMS, S3 access logs, cookie consent).
- **⚖️ Adaeze herself** — draft `docs/compliance/skill-questions.md`, draft `docs/compliance/copy/privacy-notice.md`, draft `docs/compliance/copy/t-and-c.md`, update `docs/risk-register.md` with R-FREE-01, R-SKILL-01, R-CONSENT-01, R-NDPA-01.

Adaeze will pull these forward when the counsel opinion lands and Phase 3 planning begins.

---

## 7. A short retrospective from six days in

What worked:
- **Ritual anchors landed.** *"You're in."* recurring across registration success and ticket-issued, *"Not this time."* across ticket detail + banner + reveal page + email, and the *"same terms whether you pay or not"* substitute for the classification claim reads (I think) as *voice* rather than as *repetition*. Reading the wireframes as a set, the product has a mouth.
- **Anchor references paid off.** The five references in tone-doc.md §2 (BOTB / Watches of Switzerland / Range Rover / Kuda / Coinbase) did specific work in specific places — BOTB in the draw-detail full-bleed treatment, Range Rover in the ticket-artefact, Coinbase in the hash typography and proof-summary card. Naming the reference and naming the specific thing to take from it (not "everything about it") was better guidance to my future self than more time in exploration.
- **Adaeze early was the right call.** Reviewing wf-03/04/06/07 as a compliance-set (rather than one-at-a-time as they landed) surfaced coherence issues (the repeated legal claim, the missing consent capture cascade from wf-06 back into wf-07) that would have cost me more to fix if she'd reviewed piecemeal.

What I'd do differently:
- **Should have flagged the postal address earlier.** Adaeze caught in REVIEW-001 §6.1 that wf-03 references a P.O. box that doesn't exist. I wrote the sheet on Day 4 assuming procurement was in progress; I should have asked. Placeholder is fine for demo, but this is an operational blocker for launch and it would have been useful to flag on Day 4, not Day 7.
- **Should have designed the anonymous winner variant of the reveal page immediately, not deferred to V1.** Adaeze correctly noted (REVIEW-001 §4.3) that winner-name publication requires consent and there's no capture step; I added the checkbox to wf-07 in this amendment pass, but the *anonymous rendering* of wf-06 non-winner banner / reveal / email is still a V1 task. If a founder wants to demo the anonymous case, we can't. Not a Week 2 blocker; noting for retro.

What's genuinely uncertain going into Week 2:
- **The public proof page (wf-12) is the wow moment.** I have not yet drafted it. It's the single most important trust-story surface, and I have Anchor 5 (Coinbase) as reference but no product-in-hand to compare against — proof pages are rare. Expecting to spend more of Day 11 in exploration than in polish, which is why I want Adaeze reviewing a working draft rather than a finished one.

---

## 8. Cross-references

- All wireframes: `_bmad-output/planning-artifacts/design/wireframes/01..07`.
- Tokens + tone: `_bmad-output/planning-artifacts/design/tokens.md`, `tone-doc.md`.
- Compliance review: `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md`.
- Overall V0.5 plan: `_bmad-output/planning-artifacts/v0.5-demo-plan.md`.
- Delivery framework (Phase 3+ context): `_bmad-output/planning-artifacts/delivery-framework.md`.
- Agent operating model: `docs/AINE-AGENTS.md`.

---

🎨 *End of Week-1 checkpoint. Founder — read as a system, push back where instinct says push back, sign off where it holds. Six decisions parked in §4 are the direct asks. Week 2 begins Day 8 on your ack.*
