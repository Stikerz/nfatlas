# Compliance Review — REVIEW-001

**Subject:** V0.5 consumer wireframes 03 (free-entry disclosure), 04 (buy paid ticket), 06 (draw completes / notifications), 07 (winner claim start).
**Drafted:** 2026-07-08
**Drafted by:** ⚖️ Adaeze (atlas-compliance-risk)
**Requested by:** 🎨 Sally, per open questions logged in each wireframe.
**Status:** Draft — pending founder acknowledgement and (where flagged) counsel opinion.
**Substrate:** Nigerian prize-competition mechanics per PRD §3, ADRs 003 / 004 / 005 / 006 / 007 / 010, `_bmad-output/planning-artifacts/legal/counsel-engagement-brief.md`, `_bmad-output/planning-artifacts/research/domain-nigerian-prize-competition-licensing-research-2026-06-30.md`.

---

## 0. Standing caveat (the ceiling on this review)

The domain research file at `research/domain-nigerian-prize-competition-licensing-research-2026-06-30.md` is **aborted at step 1** — no verified web sources were retrieved, NLRA 2005 has not been read against these wireframes by anyone in this project, and Nigerian counsel has not yet been engaged (see `legal/counsel-engagement-brief.md`, still Draft). Every verdict in this review is therefore conditional on one of two things:

1. **For the V0.5 investor demo only** — the mechanic is designed to counsel-brief hypothesis (the UK-style free-route + skill-question model, PRD §3, counsel brief §2). This is defensible *design intent* and I approve on that basis for demo purposes. It is **not** a Nigerian regulatory clearance.
2. **For any real-user launch (Phase 3+)** — every "Approved" in this review below is downgraded to "Pending counsel opinion" until Q1–Q7 of the counsel-engagement brief have been answered in writing and the mechanic has been re-reviewed against that opinion.

Anyone reading this review as authority for a real-user launch is reading it wrong. I would say this in every future review too until counsel has landed.

I proceed on that footing.

---

## 1. Summary

| Wireframe | Verdict | Blocking items |
|---|---|---|
| **03** — Free-entry disclosure | **Approved with conditions** (2) | Wording change to lede (§2.1); winning-route disclosure held for counsel (§2.3). |
| **04** — Skill question + Paystack | **Approved with conditions** (3) | Skill-question difficulty is too low (§3.1); rotation policy needed (§3.2); repetition of the "not-a-lottery" phrasing is fine — bounded (§3.3). |
| **06** — Notifications | **Approved with conditions** (3) | Winner-name publication requires an explicit consent capture step that does not currently exist (§4.3); email footer legal identity gap (§4.4); "verify it yourself" URL indexability needs a small technical accommodation (§4.5). |
| **07** — Winner claim start | **Approved with conditions** (5) plus **1 rejection** | Age gate confirmed at 18 (§5.1); BVN handling approved with a specific correction (§5.2); ID-type list needs an addition and an exclusion (§5.3); name-match hard-stop confirmed (§5.4); consent language on 7.5 needs to be heavier — I've drafted replacement copy (§5.5); **rejected-claim state copy — I've drafted it (§5.6)**; the "usually 1 working day" SLA copy is **rejected** as currently written (§5.7); winner-consent capture must move onto this form (§5.8); ID-image retention policy is a Phase 0 gap (§5.9). |

Additionally, five findings Sally did not flag but I must (§6):

1. Free-entry disclosure copy assumes a **postal address exists**. It doesn't. See §6.1.
2. The **skill question is not scored against a genuine skill threshold in V0.5** — anyone who taps around eventually gets in. See §6.2.
3. **Wallet balance refunds** on self-exclusion (ADR-010 §User-facing flow) are referenced nowhere in the consumer flow. See §6.3.
4. The **audit-log integrity story** is invoked in copy but the *"See how the draw was verified"* link is not yet designed. See §6.4.
5. **NDPA (Nigeria Data Protection Act 2023) footings** are missing across the board. Cookie/consent, DPO contact, and data-subject rights are absent from the notification surfaces and the claim flow. See §6.5.

Actions back to Sally, Amelia, Tobi, founder in §7.

---

## 2. Wireframe 03 — Free-entry disclosure

### 2.1 Q4 — Lede sentence: *"Every draw at Atlas offers a free postal entry route. It exists for a simple reason: a prize competition is not a lottery. The free route is how the difference is real."*

**Verdict: Approved with a wording change.**

The framing is directionally correct. A free entry route on equal terms with the paid route is the load-bearing legal distinction between a "prize competition" and a "lottery" in jurisdictions that recognise the distinction (UK Gambling Act 2005 s.14, per counsel brief §5 comparable jurisdictions). The Atlas mechanic mirrors that distinction.

**But: the sentence *"a prize competition is not a lottery"* is a legal conclusion asserted in first-person voice by Atlas.** Counsel has not confirmed that the Nigerian regulator (NLRC) recognises the distinction, and until they have, Atlas making that assertion in consumer copy is Atlas holding itself out as the arbiter of the classification. This is a category of statement regulators dislike even when they agree with the substance.

**Change required.** Replace the second sentence with a description of the mechanic, not a legal classification:

> Every draw at Atlas offers a free postal entry route. It exists for a simple reason: **entries are earned on the same terms whether you pay or not.** The free route is how that promise is kept.

This says the operational truth ("same terms whether you pay or not") without making a legal claim about the category the product belongs to. The classification claim can and should live in the T&Cs where it is properly framed as a company position and can be updated by counsel.

Everywhere else in the wireframe set where the *"prize competition, not a lottery"* phrasing appears (wireframe 03 sheet 2.3, wireframe 04 §2.4 skill question intro), the same substitution applies. See §3.3 below for the wireframe 04 handling.

### 2.2 Q5 — *"Same odds, same pool, same shot"*

**Verdict: Approved, conditional on it being operationally true.**

The three-word rhythm is memorable and honest **iff** operations honour it. That means:

- **Same pool.** Every valid free-route entry is transcribed into the same table row-space as paid entries. No separate table, no "free-route" pool that is silently smaller. The transcription flow in the operator surface (Sally's wireframe 10, Day 9) must produce a `ticket` row indistinguishable from a paid-route `ticket` row except for the `entry_source` field. **Amelia — this is a ledger + ticket-module invariant I need in ADR-003 amendment or a new ADR before real-user launch.**
- **Same odds.** The draw engine (ADR-006) selects the winning ticket by uniform-random index over the full ticket table. No weighting by entry source. **Winston — please confirm this is what ADR-006 currently says; if not, we need an ADR amendment.**
- **Same shot.** Once entered, every ticket has an identical chance of winning. This is a consequence of the first two.

If any of these three cannot be honoured, the phrasing must change. I would rather Atlas commit to something less catchy and true than something catchier and questionable. The current wording is *fine* precisely because it is a promise the mechanic can keep.

### 2.3 Q6 — Winning-route disclosure

**Verdict: Held. Do not ship in V0.5. Re-visit for V1 with counsel.**

Sally proposed publishing *"The winning ticket in this draw came from the paid/free route"* on the disclosure element post-reveal (wireframe 03 §2.3) and echoing it in the reveal page prose ("1,247 entries were in this draw. 1,160 paid. 87 via the free route.") — wireframe 06 §3.5.

The **paid/free split as an entry count** (per wireframe 02 §2.4 draw card, wireframe 06 reveal page) is fine and I approve it. That is public draw-composition data.

The **route the specific winner came from** is a different category. It creates two risks:

1. **Adverse-selection appearance risk.** If, over multiple draws, the winner disproportionately comes from the paid route, a plaintiff or regulator could construe this as evidence the routes were not equal, even if they mathematically were (small samples produce lumpy distributions). Publishing per-draw route disclosure gives that theory data to work with. If the routes are equal, the free-route win rate will match the free-route entry share on average — but on any single draw, it might not, and that gap is what would get quoted.
2. **Winner-identification risk in small pools.** If only 87 of 1,247 entries came from the free route, and the free route wins, the pool of potentially-identifiable winners is much smaller than the pool of paid-route winners. Combined with city and first-name-plus-initial (§4.3 below), this narrows identifiability meaningfully.

**Hold this decision until counsel has opined.** The reveal page and the disclosure sheet can carry the entry-count split (as drawn) without carrying the winning-route disclosure. If counsel is comfortable with it, it comes back in V1.

Sally — remove the winning-route disclosure sentence from wireframe 03 §2.3 (post-reveal state) and wireframe 06 §3.5 (reveal page prose). Retain the entry-count split.

### 2.4 Q7 — Prominence + placement

**Verdict: Approved.**

Wireframe 02 §3 places the free-entry disclosure between the trust-hash meta rows and the "About this draw" section — above the fold on most devices, in the natural top-down scroll path, presented as a card among cards rather than a promotional banner. This treatment satisfies my prominence standard for V0.5 demo.

I do not have Nigerian regulatory guidance to cite for a stricter test (no NLRC guidance is in hand). The UK ASA / CAP Code test (which is the nearest comparable) would require the disclosure to be "clear, prominent, and equally accessible" — the current design meets this. **When counsel opines, they may raise the bar** (e.g. requirement for a specific font size, or an above-the-fold guaranteed placement across all viewport widths). Design should be prepared to adapt.

### 2.5 Q8 — Main disclosure element copy: *"Prefer not to pay? Every draw offers a free postal entry. Same odds, same pool, same shot."*

**Verdict: Approved as written.**

Direct, factual, no classification claim in this line (the classification claim lives in the sheet and is being amended per §2.1). *"Prefer not to pay?"* is a question posed to the reader — respectful, not judgemental. The three-word promise is tight. Ship this line as drawn.

---

## 3. Wireframe 04 — Buy paid ticket

### 3.1 Q6 — Skill question difficulty (*"Which of these is the capital of Nigeria? Lagos / Abuja / Kano / Ibadan"*)

**Verdict: Rejected for a real-user launch. Approved for V0.5 investor demo only.**

The question as written is not defensible as a "genuine skill test." *"Which of these is the capital of Nigeria"* is a fact taught in primary school. The plausible-wrong (*Lagos*) hedges the difficulty upward slightly, but the true answer is still guaranteed for any competent Nigerian adult, and the multiple-choice format further reduces the effort required to a single tap.

UK CAP guidance on skill questions (the closest thing to a published test I can cite — Nigerian equivalent is TBD by counsel) requires that the question must:

- **Require an application of knowledge, skill, or judgement** — not mere selection from options.
- **Be of a level of difficulty likely to prevent a significant proportion of entrants from entering** — the *"prevent"* verb matters; the question must have an *actual filtering effect*.
- **Not be so easy that the free-entry-route + skill test combination is a legal fiction.**

*"Capital of Nigeria"* fails the second criterion. Every entrant of sound mind and Nigerian education will pass. The question does not filter; it is theatre.

**For V0.5 investor demo:** approved *only* because demo scope is not real users and the mechanic is being demonstrated, not tested. If an investor asks "how do you filter?" the founder needs an answer, but the demo can proceed.

**For real-user launch (Phase 3+):** the skill-question set must be redesigned. My working target — pending counsel — is questions that:

- Require two-step reasoning (a small calculation, a comparison, or a domain fact + inference).
- Have plausibility-graded distractors (all four options must look answerable to a non-expert; the wrong ones should require actual elimination).
- Are rotated from a pool of at least 200 questions per active month, with a hard-max re-use frequency of once per 30 days per user.
- Are pre-reviewed by counsel as a set for classification-defensibility.

I will draft the V1 question-set architecture and produce `docs/compliance/skill-questions.md` per the artefact registry (AINE-AGENTS.md §4). **This is a Phase 3 blocker, not V0.5.**

### 3.2 Q7 — Skill question rotation, difficulty variance, publish requirement

**Verdict: Guidance provided; policy required as an artefact.**

I am not aware of any Nigerian regulatory requirement to publish the question pool. UK CAP practice is that operators keep the pool private — publishing it defeats the filtering purpose. Atlas should keep the pool private.

Rotation constraints (working position, pending counsel):

- **Per-user rotation:** a user must not see the same question twice within 30 days of the last time they saw it.
- **Global rotation:** a question must not appear more than a specified % of the time across all entries in any 24h window (specifically to prevent a "leaked answer" from being usable at scale).
- **Difficulty variance:** the pool must be reviewed for difficulty distribution — if 90% of questions are hard and 10% are easy, an entrant who reloads until they get an easy one has effectively bypassed the skill test.

**Ticket module contract:** rotation logic is a Ticket-module responsibility (per PRD §4 module ownership). Amelia — this rotation policy needs to be a feature of the module, not a runtime knob operators can turn off. Please treat the rotation constraints as an invariant enforceable in code + tested.

Full policy will live at `docs/compliance/skill-questions.md` when I draft it (Phase 3 pre-work).

### 3.3 Q8 — Repetition of *"prize competition, not a lottery"* across wireframes

**Verdict: Approved with a bound, subject to the §2.1 wording change.**

Repetition of a mechanic-explaining phrase across the free-entry disclosure and the skill-question intro is coherent, not over-claiming — the user encounters the mechanic twice in the same product journey and hears a consistent frame each time. This is what an auditor would expect.

**Two constraints:**

1. Once we adopt the §2.1 wording change (drop the direct legal classification claim from consumer copy, keep it in T&Cs), the repeated phrasing on the skill-question intro (wireframe 04 §2.4 — *"Atlas is a prize competition, not a lottery — the question confirms your entry."*) must also change to something like:

   > **One question before you enter. Atlas competitions are decided on the same terms whether you pay or not — the question confirms your entry.**

   This preserves the tone and the mechanic frame without making the legal-classification claim in first person.

2. The pattern is bounded to these two surfaces. If a third surface picks up the same phrasing (a marketing page, a T&C excerpt in the app), it starts to read as a defensive tell (*"they keep saying it isn't a lottery — why?"*). Two is repetition; three is protesting too much.

---

## 4. Wireframe 06 — Draw completes / notifications

### 4.1 Q6 — Prize claim requirements listed in the winner email: bank in legal name, BVN, government ID

**Verdict: Approved as a minimum. Two additions required for real-user launch (not V0.5).**

The three items listed are correct and non-negotiable. For real-user launch, add:

- **Tax status attestation.** Nigerian personal income tax treatment of prize winnings is unresolved in the counsel brief (Q6 of counsel-engagement-brief §3 covers this). Depending on counsel's answer, we may need a signed attestation from the winner acknowledging their tax responsibility. V1 must accommodate this — the claim form (wireframe 07 §7.5 review) can hold the attestation checkbox once counsel confirms wording.
- **Source-of-funds attestation for larger prizes.** Above a threshold (working position: ₦5M — same as the founder-approval-required payout threshold in AINE-AGENTS.md §6), the winner should confirm the funds used to purchase entries were their own. This is AML-adjacent. Threshold and wording pending counsel.

For V0.5 (cash prize ₦2M, no real users, demo only): current three items are sufficient.

### 4.2 Q7 — *"Claim within 5 working days"* wording

**Verdict: Approved with a specific rewording — Atlas's SLA, not user obligation.**

The current wording (winner email, wireframe 06 §5.1): *"paid to a Nigerian bank account of your choice within 5 working days of your claim being received."*

This reads as Atlas's SLA for payout after a completed claim. That is the correct commitment posture. **Confirm this is what Atlas means.** If it is (and I believe it is), the wording is fine.

If Atlas *also* wants to impose a deadline on the winner to submit the claim (e.g. must claim within 90 days or forfeit), that is a separate copy line and needs a separate policy decision — with counsel input, because forfeiture of a paid-for prize is a consumer-protection surface.

**Working position: V0.5 has no winner-side deadline** (the founder can chase manually in a demo). V1 requires a claim-window policy, drafted with counsel and reflected in T&Cs. Do not introduce a claim-window UI element until that policy exists.

### 4.3 Q8 — Winner identifier publication (*"Ifeoma A. (Yaba)"*)

**Verdict: Approved for V0.5 demo (seeded winner). Rejected for real-user launch without an explicit consent capture step that does not currently exist.**

First-name + last-initial + city is a common industry pattern (UK prize-comp operators use it) and it satisfies the *"the winner is a real specific person"* trust move Sally is going for. **But it is publication of personally-identifying information about a real person.** Under NDPA 2023 (Nigeria Data Protection Act, entered into force 2023), publication requires a lawful basis. The most defensible is explicit informed consent captured *before* publication.

The wireframe set as drawn has **no consent capture step for winner name publication.** The winner is told (in wireframe 07 §2.4 subhead) that we'll pay them; the reveal page (wireframe 06 §3.5) publishes their name and city; but nowhere between those two moments does the winner explicitly agree to that publication.

**Required for real-user launch:** wireframe 07 §7.5 (review + submit) must include a **separate opt-in checkbox** distinct from the general consent checkbox, with wording along these lines:

> ⬜ **You may publish my first name, last initial, and city on the Atlas winner announcement.** *(Optional. If you'd rather stay anonymous, we'll publish "Winner — {city}" instead.)*

If declined, the reveal page and all downstream notifications use the anonymous form. Design work on Sally to add this checkbox in a wireframe 07 amendment and to design the anonymous variant of the reveal page.

**For V0.5 investor demo:** the winner is seeded, so consent is not at issue. Approved for the demo. Flagged as a hard blocker for real-user launch.

### 4.4 Q9 — Legal footer content on emails

**Verdict: Rejected as currently drafted. Specific gaps.**

The email footer in wireframe 06 §5.1 has *"Atlas Africa Ltd — {address}"* and a "You're receiving this because you entered a draw at Atlas" line. That is not a compliant sender footprint under Nigerian requirements.

**Required additions:**

1. **Company registration number** (RC number issued by the Corporate Affairs Commission).
2. **Registered office address** (in full, not a template placeholder).
3. **Prize-competition operating licence / registration reference** — *if any is required* per counsel's opinion on Q1 of the counsel brief. If the mechanic requires no licence, this line is omitted; if it does, this line becomes mandatory. Neither the wireframe nor I know the answer today.
4. **Data controller identity** — under NDPA 2023, the sender of a marketing or service email must identify the data controller if that entity is different from Atlas Africa Ltd, and provide a contact route to the Data Protection Officer.
5. **Unsubscribe** — Sally has this flagged as V1; I concur, and I formally flag it as a ship-blocker for real-user launch, not a nice-to-have.
6. **Sending domain SPF / DKIM / DMARC alignment** — not a copy issue but a compliance-adjacent deliverability issue. Tobi's concern for real launch.

**V0.5 posture:** since no real users receive these emails, the current footer is acceptable for the Mailhog demo. **All six items above are Phase 3 blockers for real-user launch.**

### 4.5 Q10 — Public "verify it yourself" URL indexability

**Verdict: Approved with one technical accommodation.**

Public verification URLs are a positive trust surface. Search engines caching them is fine and probably desirable — a search for a draw ID should return the proof page. **However:**

- If the reveal page publishes the winner's first name, last initial, and city (per §4.3), the URL becomes searchable by the winner's name. This is a privacy exposure the winner did not explicitly agree to at time of consent.
- **Accommodation:** the public URL structure should be `atlas.ng/proof/{draw_id}` (keyed by draw, not by winner). The winner name should be **rendered client-side after page load** with a small `noindex` directive on the winner-name element, OR omitted from the public URL entirely and shown only when the visitor is authenticated as the winner. Recommend the second — the public proof page shows the *winner ticket number*, the *hashes*, and the *entropy inputs*; the *winner name* appears in the app for the winner, in the app for other logged-in users (if publication was consented), and in social share cards; but not on the public web page keyed by draw ID.

Amelia — this is a Draw-Engine / public-web contract point. When wireframe 12 (public proof page, Day 11) is drafted, I want to review it against this before it ships.

---

## 5. Wireframe 07 — Winner claim start

This is the highest-load-bearing surface in the review. Fourteen questions were raised. I take them in order.

### 5.1 Q6 — Age gate at 18

**Verdict: Approved. Copy is correct.**

18 is the standard age of majority for participation in prize-competition and gambling-adjacent activities in Nigeria. NLRA 2005 fixes 18 as the minimum for licensed activity; prize-competition posture inherits this floor whether or not the licence itself is required. The hard-stop on the DOB field with a support-contact escalation (wireframe 07 §4.3) is appropriate.

**One addition to consider (not blocking):** the age gate should also be enforced at *registration* (wireframe 01), not only at claim. Currently registration captures phone + email but not DOB, so an under-18 user can complete registration, enter draws, hold tickets, and only be blocked at the winner-claim gate — after having paid Atlas money for tickets that were, arguably, unlawfully sold to them.

**Sally / Amelia — please add DOB capture and 18+ check to registration in a wireframe 01 amendment.** Refunds of under-18 users' ticket purchases would be a complex operational problem; better to prevent than to remediate.

### 5.2 Q7 — BVN handling copy and redacted display

**Verdict: Approved with one correction.**

The BVN help copy on wireframe 07 §5.3 (*"Don't share your BVN with anyone else. We only use it to confirm your bank account."*) is well-pitched. It acknowledges the user's real-world caution about BVN sharing and gives Atlas's specific reason for asking. Ship this.

**Correction: the second half of the sentence is not the whole truth.** BVN is used for two things in Atlas:

1. To confirm the bank account matches the winner's identity (as stated).
2. To key the self-exclusion registry (ADR-010) — this is *not* stated to the user.

The current copy is technically an under-statement, not a mis-statement, but under NDPA principles of purpose limitation and transparency, a user should be told all purposes for which their personal data is processed.

**Replacement copy:**

> **Bank Verification Number (BVN)**
>
> Don't share your BVN with anyone else. Atlas uses it to confirm your bank account matches your identity, and to check our self-exclusion register.

The redacted display on wireframe 07 §7.4 (`222•••••678`) is appropriate — first-three-plus-last-three matches the pattern users expect from their own bank statements and does not expose more than a bank's SMS-confirmation would.

### 5.3 Q8 — ID types accepted (NIN slip, driver's licence, international passport, voter's card)

**Verdict: One removal, one addition.**

**Remove: Voter's card.** The Permanent Voter's Card (PVC) is not a standard KYC document in Nigerian financial-services practice. It has no photo standardisation, no counterfeit-resistance features comparable to the others, and vendor OCR performance is poor. It should not be an accepted ID.

**Add: NIN slip → NIN itself (verifiable via NIMC).** The paper NIN slip is fine, but the *primary* accepted form should be the NIN number verifiable against NIMC via the KYC vendor — the slip is a fallback for users who don't remember their NIN by heart. Copy should read:

> Any one of:
> - Your National Identification Number (NIN)
> - Driver's licence
> - International passport
> - NIN slip (if you don't have your NIN to hand)

This ordering signals the preference and matches what the vendor (ADR-007 — Smile / Dojah / Prembly all offer NIN verification via NIMC) is actually best at.

Amelia — the KYC adapter (per ADR-007) must support NIN verification as the primary path. Please confirm this fits the shortlisted vendor set.

### 5.4 Q9 — Bank account name-match hard-stop

**Verdict: Approved. Non-negotiable.**

Atlas does not pay prize proceeds to accounts not in the winner's legal name. This is required for:

- **AML posture.** Paying to a third-party account creates a laundering vector Atlas cannot audit.
- **Consumer protection.** A winner who directs payment to an "agent" account has been coerced or defrauded; Atlas's paying to that account makes Atlas the enabler.
- **Chargeback / dispute defensibility.** If Atlas paid the winner as identified, Atlas has a clean disposal record. Any other outcome is a dispute.

The mismatch branch (wireframe 07 §6.2) with the option to edit the name on Step 1 is the correct escape hatch. If a legitimate winner has changed their legal name since opening the bank account (marriage, correction), they update the bank first — Atlas does not adjudicate name reconciliation, the bank does.

### 5.5 Q10 — Consent language on 7.5 review + submit

**Verdict: Current wording is too light. Replacement drafted.**

The current consent (wireframe 07 §7.5): *"I confirm the details above are true and complete. I understand Atlas will use these details to pay my prize, as described in the Terms."*

Two gaps:

1. It bundles data-processing consent with truthfulness attestation. NDPA principles want these separated — the user should be able to see clearly *what* they are consenting to, and truthfulness of a form is not the same as consent to process personal data.
2. It defers the substance to "the Terms" — which is legally acceptable but weak for a moment as consequential as a prize claim.

**Replacement (two checkboxes, both required):**

> ⬜ **I confirm the details above are true, complete, and belong to me.**
> Providing false information may void my claim and can be reported to Nigerian authorities.
>
> ⬜ **I agree Atlas may process my personal data — including my BVN and my ID document — to verify my identity, confirm my bank account, pay my prize, and meet Atlas's regulatory obligations. Full details are in the Privacy Notice.**
> *(You can withdraw this consent later, but it will pause your claim.)*

**Plus one optional checkbox** (per §4.3 above):

> ⬜ **You may publish my first name, last initial, and city on the Atlas winner announcement.** *(Optional. If you'd rather stay anonymous, we'll publish "Winner — {city}" instead.)*

This adds one form element but makes each thing the user agrees to legible on its own. It is defensible under NDPA and it is honest.

### 5.6 Q11 — Rejected-claim state copy (Sally deferred to me — drafted)

**Verdict: Drafted below. Adopt as-is or amend by counsel.**

Sally correctly deferred this to compliance. Four rejection scenarios:

**5.6.a — KYC verification failed (identity does not match documents)**

State timeline change: second dot becomes *"Additional information needed"*, filled in state.attention (not state.danger — this is not an accusation).

> **We need to take another look.**
>
> The details you submitted didn't match cleanly against our identity checks. This can happen for a few reasons — a photo of an ID that wasn't clear, a name that appears differently on different documents, or details that don't line up with the bank account.
>
> Please **contact us at {support}** so we can help sort it out. Reference: **CL-04829-6JQ7**.

No self-diagnosis, no accusation. The winner is directed to a human contact for resolution.

**5.6.b — BVN does not match the identity on the claim**

Distinct from KYC-failed because the mismatch is specifically the BVN → bank-account link.

> **Your BVN doesn't match the account you provided.**
>
> The name on your bank account (as returned by Guaranty Trust Bank) is different from the name registered against your BVN. This usually means either the bank account isn't yours, or one of the records is out of date.
>
> **Update your bank details** if you provided the wrong account, or **contact your bank** if the name on your account needs correcting. Then come back and update this claim.
>
> Reference: **CL-04829-6JQ7**.

Two paths, no accusation, no dead-end.

**5.6.c — Suspected fraud (this state is set by the operator, not automated)**

> **Your claim is on hold pending review.**
>
> We've paused this claim while we look into some details. This can take a few working days. We'll email you as soon as we have an update.
>
> If you have information that would help, please **contact us at {support}** with your reference: **CL-04829-6JQ7**.

Minimal information disclosed. Fraud investigations are documented off the consumer surface.

**5.6.d — Self-exclusion match detected at claim time (ADR-010)**

This is the most delicate state. A user who self-excluded may not remember doing so; they may be in a difficult moment; the copy must be respectful and it must not accuse.

> **This account is on our self-exclusion register.**
>
> A member of our team will be in touch to explain what happens next and to arrange the refund of any wallet balance. If you'd like to talk to us before then, contact us at {support} or, if you'd prefer a professional, contact **{national gambling support helpline}**.
>
> Reference: **CL-04829-6JQ7**.

The support helpline reference is not optional — self-exclusion match at claim time is a duty-of-care moment. **Helpline detail: to be filled by counsel or via the risk-register when we identify the correct Nigerian resource** — there is not yet a mature GAMSTOP-equivalent in Nigeria (per ADR-010 alternatives-considered), so we may need to point at a general mental-health line as an interim.

### 5.7 Q12 — Timeline SLA copy: *"usually within 1 working day"*

**Verdict: Rejected as currently written for V1. Approved for V0.5 demo.**

*"Usually within 1 working day"* implies a repeatable operational tempo that Atlas has never operated. V0.5 has no operator SLA and no claim volume. Publishing a soft commitment we haven't measured is a specific kind of avoidable exposure — the first time the SLA slips, we've broken a written promise for no reason.

**For V0.5 demo:** approved. It's a demo. The screen shows an operational cadence that reads as reasonable.

**For real-user launch (Phase 3+):** the copy must be one of:

- A cadence we have measured across at least 30 real claims and are comfortable maintaining as a mean (with a longer SLA'd tail).
- A more conservative wording: *"Most claims are reviewed within a few working days."* This is honest, non-specific, and easier to honour.

Working position: use the conservative wording until we have real data.

### 5.8 Q13 — Winner-name publication consent (Sally flagged; concurring)

**Verdict: Concur. Add checkbox to wireframe 07 §7.5 per §5.5 above.**

Already handled in §4.3 and §5.5. Sally's instinct here was correct and I formally endorse the fix.

### 5.9 Q14 — ID image storage and retention

**Verdict: Design is directionally right. Retention policy is a Phase 0 gap and must be closed before real-user launch.**

Per ADR-007 §PII redaction, ID document images live in S3 (or equivalent object store), the application DB stores only signed URL references, and vendor responses have PII redacted before persistence. The application-code posture is correct.

**Gaps:**

1. **Retention period is not set.** ADR-007 §Audit-and-storage notes 5 years as a placeholder. Counsel opinion is required — Nigerian AML/KYC rules typically require retention of KYC records for 5–7 years post relationship end. Counsel briefs Q4 (counsel-engagement-brief §3) covers this.
2. **Deletion on user request is not designed.** NDPA 2023 grants data subjects the right to erasure. A winning claimant who has been paid may later request deletion; Atlas must have a workflow. This does *not* mean deletion is always granted — regulatory retention periods override — but Atlas needs a process to receive, evaluate, and respond to such requests. **Sally — future wireframe (V1 Settings screen) needs a "Delete my data" flow. Not V0.5.**
3. **Encryption at rest** — S3 SSE-KMS or equivalent. **Tobi's concern; noting for the risk register.**
4. **Access logs** — every read of an ID image from S3 must produce an access-log entry with the reading user's ID. Compliance-and-audit hook. Tobi + Amelia.
5. **Retention triggers** — the retention clock starts when *the relationship ends*, not when the image is uploaded. Deletion when a user account closes (via self-exclusion, per ADR-010, or via user request) must respect a delayed-delete window equal to the retention requirement.

These are Phase 3 blockers, not V0.5. V0.5 stores demo data only.

---

## 6. Findings Sally did not flag

Five items I must raise even though they were not in her question list.

### 6.1 The postal address does not exist

Wireframe 03 §3 (the "How the free route works" sheet) states:

> Post it to the address below before the draw closes.

The address is not currently procured. There is no P.O. box. Counsel-engagement-brief §2 lists it as an intended feature ("V1: postal entry to a leased P.O. box with a handwritten entry slip"), but leasing has not happened.

**For V0.5 investor demo:** approved — the sheet can render a placeholder address (e.g. *"Postal address arrives with V1 — for demo purposes, mail to {founder address}"*), or the sheet can omit the actual address and say *"Contact us for the postal address."*

**For real-user launch:** the P.O. box must be leased and manned. The transcription flow (Sally's wireframe 10, Day 9) must be a real operational capability with a named responsible person. **Adding to risk register as R-FREE-01.**

### 6.2 The V0.5 skill question does not actually filter

Wireframe 04 §2.3 describes what happens on a correct answer (auto-advance) and a wrong answer (error, chip flash, retry). It does *not* describe a rate-limit or a lockout after N wrong answers. In V0.5 as specified, a user who taps every option in sequence will get through in a maximum of 4 taps.

For the demo this is fine — the mechanic is being shown, not enforced.

**For real-user launch:** at minimum, after 3 wrong answers the entry attempt must be voided and the user required to start a fresh attempt with a fresh question — with a cooldown period between attempts. Otherwise, "the skill question filters" is not true, and §3.1 above is undermined.

**Ticket module invariant. Adding to risk register as R-SKILL-01. Not V0.5 blocking.**

### 6.3 Self-exclusion wallet refund is not surfaced

ADR-010 §User-facing flow requires that on self-exclusion, any wallet balance is refunded to the originating payment method (or escheated after 90 days). This refund process is not surfaced anywhere in the consumer flow currently designed. The self-exclusion trigger is mentioned in wireframe 05 §2.8 (greeting-chip overflow menu → Self-exclusion) but the consequence flow is not designed.

**Not V0.5 blocking** because V0.5 self-exclusion is stubbed per plan §3. **For V1**, Sally needs to design the self-exclusion confirmation flow with the wallet-refund path visible. I'll add this to my open work list for the V1 design pass.

### 6.4 Audit-log integrity story is invoked but not designed

Wireframe 06 §3.5 and wireframe 05 §3.6 reference *"See how the draw was verified"* and *"See how this draw was verified"* — public proof page at wireframe 12 (Day 11, per tone-doc §8). I have not seen that wireframe yet.

**Not currently blocking**, but **flagged for early review when Sally drafts it.** The public proof page is where the entire trust story is redeemed or falls apart. I want to review that wireframe as soon as it exists — not at Week 2 exit gate. Sally, please send it my way as soon as it's a working draft, not a finished one.

### 6.5 NDPA footings are absent across the board

The Nigeria Data Protection Act 2023 requires several things Atlas is currently not designing for on the consumer surface:

1. **Data-subject rights** — access, rectification, erasure, portability, objection. Not one of these has a UI in the current wireframe set.
2. **DPO contact** — a Data Protection Officer contact route must be discoverable. Not currently in the app.
3. **Privacy Notice** — the wireframes reference a Privacy Notice (wireframe 01 §2.4) but I have not seen a draft. Copy work owned by me per AINE-AGENTS.md §4 (`docs/compliance/copy/`). **Adding to my own work list.**
4. **Consent granularity** — currently marketing consent and service-communication consent are bundled with T&C acceptance at registration (wireframe 01 §2.4). NDPA prefers granular consent — separate opt-ins per processing purpose. This may require a wireframe 01 amendment.
5. **Cookie consent for web surfaces** — Not in V0.5 scope (no web consumer app), but the admin (Next.js) and any future marketing site will need a cookie consent banner. Tobi's concern for infra; my concern for copy.

**Not V0.5 blocking.** Real-user launch cannot proceed without at least items 1, 2, 3, and 4 addressed. Adding to Phase 3 backlog.

---

## 7. Actions

### For 🎨 Sally — before continuing the design pass

**Amendments to already-drafted wireframes (small edits):**

1. Wireframe 03 §3.4 lede — apply §2.1 wording change.
2. Wireframe 03 §2.3 — remove winning-route disclosure sentences per §2.3.
3. Wireframe 04 §2.4 — apply §3.3 wording change to skill-question intro.
4. Wireframe 06 §3.5 — remove winning-route disclosure from the reveal-page prose per §2.3 (retain entry-count split).
5. Wireframe 07 §5.3 BVN help copy — replace per §5.2.
6. Wireframe 07 §5.3 ID types — replace list per §5.3.
7. Wireframe 07 §7.4 consent — replace with two-checkbox pattern per §5.5, plus a third optional checkbox for name publication per §4.3 and §5.5.
8. Wireframe 07 §8.3 rejected-state — add the four state variants I drafted in §5.6.

**Small additions to already-drafted wireframes:**

9. Wireframe 01 amendment — add DOB capture at registration with 18+ hard-stop (§5.1).

**Flags on wireframes not yet drafted:**

10. Wireframe 10 (operator transcribe free entry, Day 9) — the transcription flow must produce `ticket` rows identical to paid-route rows except for `entry_source`; please flag this to me when drafting so I can confirm the operator UI supports it.
11. Wireframe 12 (public proof page, Day 11) — send me a working draft as soon as it exists, not a finished one. See §6.4.
12. Future Settings screen (V1) — will need a self-exclusion confirmation flow with wallet-refund path visible (§6.3), plus data-subject rights UI (§6.5.1).

### For 💻 Amelia — invariants and contract points

1. Ticket module: skill-question rotation as a code-enforced invariant, not an operator knob (§3.2).
2. Ticket module: 3-strike rate limit + cooldown on skill-question attempts (§6.2).
3. Ticket module: free-route ticket rows structurally identical to paid-route ticket rows, differing only by `entry_source` (§2.2).
4. Draw engine (ADR-006 reader): confirm uniform-random selection across the entire ticket pool without weighting by entry source; if not, raise an ADR amendment (§2.2).
5. KYC adapter (ADR-007): confirm NIN verification via NIMC is a primary path across shortlisted vendors (§5.3).
6. Claim state machine: on suspected-fraud path (§5.6.c), state must be operator-settable and consumer-visible as "on hold".
7. Public proof URL structure: `atlas.ng/proof/{draw_id}`, winner name not present on the public URL (§4.5).

### For 🏗️ Winston — ADR touch-points

1. **ADR-006 or new ADR:** invariant that draw-engine selection is uniform-random over the full pool, no weighting by entry source. Amendment or confirmation, my call.
2. **ADR-003 (ledger) or new ADR:** invariant that free-route and paid-route tickets sit in the same table with `entry_source` as a column (already implicit; make it explicit).

### For 🛡️ Tobi — infra + real-launch prep

1. Email deliverability posture — SPF / DKIM / DMARC for the production sending domain (§4.4).
2. S3 SSE-KMS or equivalent for ID document storage (§5.9.3).
3. S3 access logs enabled and retained on ID document buckets (§5.9.4).
4. Cookie consent banner infrastructure for admin (V1) and marketing site (future) (§6.5.5).

### For founder — decisions I need

1. **Concur or reject the *"prize competition is not a lottery"* wording removal from consumer copy** (§2.1, §3.3). This is a tone loss; I believe it is the right trade.
2. **Confirm winning-route disclosure hold** for V1 pending counsel (§2.3).
3. **Confirm the winner-payout SLA posture** — is *"paid within 5 working days of completed claim"* Atlas's commitment (§4.2)? If yes, we ship the current wording (as amended). If not, I need to know what Atlas actually commits to.
4. **Prize-value thresholds** for the AML additions (§4.1) — working position is ₦5M aligning with AINE-AGENTS.md §6 founder-approval threshold; confirm or set.
5. **Timeline SLA on claim review** (§5.7) — approve the more conservative wording *"Most claims are reviewed within a few working days"* for real-user launch, or push for a measured commitment once we have data.
6. **Counsel engagement** — the counsel-engagement-brief (in `_bmad-output/planning-artifacts/legal/`) has been Draft since 2026-06-30. Every item in this review flagged "pending counsel" remains unresolved until that engagement lands. **Please move the counsel brief from Draft to Sent within the next two weeks** — everything else in Phase 3 planning bottlenecks on it.

### For me — my own work list before Phase 3

1. Draft `docs/compliance/skill-questions.md` — question-pool architecture, rotation policy, difficulty tiers, review cadence.
2. Draft `docs/compliance/copy/privacy-notice.md` — NDPA-aware privacy notice draft, to be lawyered.
3. Draft `docs/compliance/copy/t-and-c.md` — first-cut T&Cs including the classification claim moved out of app copy per §2.1.
4. Update `docs/risk-register.md` — add R-FREE-01 (postal address unprocured), R-SKILL-01 (skill filter under-enforced), R-CONSENT-01 (winner-name publication consent gap), R-NDPA-01 (data-subject-rights UI absent).
5. Reserve reviewer slot on wireframe 12 (public proof page) and any wireframe touching self-exclusion, notifications, or claims post-Day-6.

---

## 8. Recording

This review will be logged in `docs/AI-INTEGRATION-LOG.md` per AINE-AGENTS.md §7. Founder acknowledgement of the "actions" list in §7 constitutes acceptance for V0.5 demo scope; each "Approved with conditions" verdict is contingent on those actions being taken before the corresponding item is regarded as compliant for its stated audience.

**Verdict summary again for the record:**

- V0.5 investor demo scope: **Approved with 11 actions to Sally + 7 to Amelia + 2 to Winston + 4 to Tobi + 6 founder decisions**, all listed in §7. None of the actions block founder from continuing the design pass — items 1–8 to Sally are small copy amendments that can be batched into a Day 7 buffer pass.
- Real-user launch scope: **Not approved.** Downgraded to "Pending counsel opinion" as per §0. Cannot approve any Nigerian real-user launch without the counsel brief landing and a re-review against that opinion.

---

⚖️ *End of REVIEW-001. Sally — I'll be watching for wireframe 12 particularly closely; for the rest, ping me when the amendments are made and I'll cross-check. Founder — the counsel brief is the single biggest thing between us and Phase 3.*
