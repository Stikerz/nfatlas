# Compliance Review — REVIEW-002

**Subject:** Removal (unwiring) of the free-entry route from the Ticket module, and the associated consumer regulatory copy changes.
**Drafted:** 2026-11-23
**Drafted by:** ⚖️ Adaeze (atlas-compliance-risk)
**Requested by:** S1408661 (founder), via 🏗️ Winston after implementation.
**Status:** Draft — BLOCKING. Not approved for merge. Pending founder acknowledgement and counsel engagement.
**Substrate:** PRD §1, §3.1; ADR-002, ADR-005, ADR-009, ADR-010; `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md`; `_bmad-output/planning-artifacts/research/nigerian-draw-classification-research-2026-11-23.md`; `_bmad-output/planning-artifacts/legal/counsel-engagement-brief.md`.

---

## 0. Standing caveat

I am not counsel and this is not a legal opinion. Nigerian gaming counsel has **not** been engaged. Every classification statement below is a working position derived from the 2026-11-23 desk research and from documents already in this repository.

A second caveat specific to this review: the desk research is dated the same day as the change it is assessing, is single-pass, and self-reports medium to medium-high confidence on its central findings, with the Supreme Court judgment text itself unverified. I treat it as the best evidence available, not as settled law.

---

## 1. Summary and verdicts

| Item | Verdict |
|---|---|
| The decision to remove the free-entry route | **Outside my gift — founder Tier 3 call. Dissent recorded (§2).** |
| Implementation quality of the unwiring | **Approved (§4).** |
| Retention of schema, constraint and audit chain | **Approved, and commended (§4.1).** |
| Consumer copy changes in the diff | **Approved with changes required (§5).** |
| Resulting compliance posture | **Rejected (§3).** |
| Pre-existing responsible-play claims | **ESCALATED — live consumer-facing misstatements (§6).** |

**The short version.** The code change is clean and the copy edits move in the right direction. The *posture* it produces is not one I can sign off: it leaves Atlas standing on the single mechanism I already rejected for real-user launch in REVIEW-001 §3.1. That rejection was never lifted.

Separately, and more urgently than anything in this diff, §6 records three live consumer-facing claims that the codebase does not implement.

---

## 2. The decision itself — dissent recorded

The removal of the free-entry route is a Tier 3 founder arbitration item under `AINE-AGENTS.md §5` (legal model). The founder has made it, having been advised against it twice by 🏗️ Winston and having reaffirmed. That is the founder's authority and I do not contest the process.

I record dissent on the substance, for the file:

1. **It removes the mechanism with the most traction.** The 2026-11-23 research ranked Model B (free route, no skill question) second and Model A (skill question, no free route) **last**, at medium-high confidence that A is weakest, on the basis that the now-void NLA 2005 s.57 expressly captured arrangements decided by "the exercise of skill and chance" — the federal definition reached skill rather than exempting it.
2. **It does not reduce licensing exposure.** On the research's reading of the Lagos State Lotteries and Gaming Authority Law 2021, "Gaming" requires only chance and a prize, with no payment element. All three candidate models require a State licence. This change neither helps nor hurts that position.
3. **It is, however, defensible on cost grounds.** If the free route confers no protection in Lagos, operating a postal transcription pipeline is expenditure without compliance return. I accept that reasoning. My dissent is to the *sequencing*, not the direction: this was decided before counsel was engaged, on single-pass desk research, when the route was cheap to leave in place.

**Nothing about this dissent blocks the merge.** §3, §5 and §6 do.

---

## 3. The resulting posture — rejected

This is the finding that matters.

**REVIEW-001 §3.1 already rejected the skill question for real-user launch.** My verdict there, unchanged and never lifted:

> **Verdict: Rejected for a real-user launch. Approved for V0.5 investor demo only.**
> […] The question does not filter; it is theatre.

That verdict was issued when the skill question was one of *two* mechanisms. Atlas has now removed the other one. The project is standing, solely, on the leg I had already marked as failing — and the implementation has not changed since I marked it.

The specific defects in REVIEW-001 §3.1 and §3.2 remain unremedied, and the 2026-11-23 research §2A.4 independently reached the same conclusion:

- Four-option multiple choice, ~25% pass rate by blind guessing.
- A small pool, against my stated working target of **at least 200 questions per active month**.
- Per-user, per-draw, per-minute deterministic rotation in which each request mints a fresh attempt — functionally unlimited retries inside the minute. The research calls this "the most damaging single feature". I agree.
- My REVIEW-001 §3.2 rotation invariants (no repeat inside 30 days per user; global reuse ceiling; difficulty-variance review) were handed to the Ticket module as a code-enforceable contract. They were never built.
- `docs/compliance/skill-questions.md` — the artefact I committed to draft and which the registry lists as mine — does not exist.

**Consequence.** Atlas has no compliance mechanism I am prepared to vouch for. That is a statement about the product, not about this diff, and it is not fixed by reverting this diff.

**Note for the record:** the research also flags that under the Lagos advertising code, marketing suggesting that skill influences a game of chance may itself be a *misleading claim*. If so, the skill question is not merely ineffective in Nigeria — it carries its own small exposure. Counsel question, flagged, not decided.

---

## 4. Implementation review — approved

I reviewed the diff against the audit-integrity and trust-surface concerns I own.

### 4.1 Schema and audit-chain retention — approved and commended

The change is an unwire, not a deletion. Specifically retained:

- The `free_entry_slips` table and its `UNIQUE (draw_id, slip_reference)` index.
- The `'free'` member of the `entry_source` CHECK constraint — verified present in the running database.
- All `ticket.free_transcribed` entries in the ADR-005 hash-chained audit log.
- The mobile `FREE`/`PAID` ticket badge, which continues to render historical free tickets correctly.

This is the right call and I want it on the record as such. Narrowing the constraint or dropping the table would have invalidated existing `entry_source='free'` tickets and falsified the paid/free split published in the commit-reveal proofs for completed draws (PRD §3.1). **A published proof must never be rewritten.** The implementer identified that independently and documented the reasoning in `ticket/models.py`. No migration was written. Restoration is code-only.

### 4.2 Audit emission — approved

`_mint_ticket` now records `actor_type="system"` / `actor_id="payment.webhook"` unconditionally, which is accurate given `issue_paid` is the sole surviving caller. The ADR-002 outbox gate passes, and the `ticket.free_transcribed` allowlist entry was retained with an honest status note rather than deleted. Correct.

### 4.3 Removal of the false self-exclusion claim — approved

`ticket/__init__.py` previously asserted *"Wires self-exclusion enforcement (ADR-010) at purchase time."* No `self_exclusions` table and no enforcement code has ever existed. The claim was false and its removal is correct. See §6.1 — the same false claim is still live in consumer copy, which is far more serious than a docstring.

### 4.4 Test coverage — approved

274/274 backend tests pass, down from 282 with the eight free-entry tests removed. The E2E audit-chain assertion was correctly narrowed rather than weakened — chain linkage is still asserted across every remaining event.

---

## 5. Consumer copy — approved with changes required

### 5.1 Approved

Two legal conclusions stated in Atlas's own voice were removed:

- *"Under Nigerian and UK prize-competition norms, a free way to enter must exist."*
- *"The skill test is the legal basis for the competition status."*

Both had to go, and for the reason I set out in REVIEW-001 §2.1: **Atlas must not hold itself out as the arbiter of its own regulatory classification.** The first was additionally false as to Nigerian law on the 2026-11-23 research. Removing them is a material improvement, independent of the free-route decision.

Removing the free-route sections rather than leaving them live was also correct and necessary. Copy promising a route the system no longer offers would have been a plain consumer-protection exposure.

### 5.2 Changes required before merge

**(a) Residual classification claims.** `how-it-works` still opens *"Atlas runs **prize competitions**"*, the page title reads *"Provably fair prize competitions"*, and the metadata description repeats it. This is the same category of statement as the sentence I required removed in REVIEW-001 §2.1 — weaker in degree, identical in kind, and now sitting on research suggesting the classification is unavailable in Nigeria. I am not requiring immediate rewording of the brand term, but it must go to counsel in the same package as everything else, and it must not be expanded in the meantime.

**(b) `REVIEW-001 §2.5` copy is now void.** I approved *"Prefer not to pay? Every draw offers a free postal entry. Same odds, same pool, same shot."* That approval is withdrawn as moot. If it appears in any surface not covered by this diff — wireframes, marketing drafts, App Store listing, investor material — it must be pulled. The diff covers the web surfaces; **nobody has swept the non-code surfaces.**

**(c) `REVIEW-001 §2.2` condition fails.** *"Same odds, same pool, same shot"* was approved **conditional on it being operationally true**. With no free route, there is no second pool to be equal to. Any surviving instance is now unmoored and must be pulled with (b).

---

## 6. Findings outside the diff — ESCALATED

These are pre-existing and not caused by this change. I surface them because they are live, consumer-facing, and in my remit, and because reviewing this page without reporting them would be negligent.

`admin/src/app/(public)/responsible-play/page.tsx` makes three claims to the public:

### 6.1 "Self-exclusion is permanent" — FALSE

> *"**Self-exclusion is permanent.** If you choose to self-exclude, we retain that decision indefinitely — a fresh account with the same phone or bank details cannot bypass it."*

There is no `self_exclusions` table in any migration and no enforcement code anywhere in `backend/src/atlas`. ADR-010 is **Approved**, signed by the founder on 2026-07-02, and names self-exclusion the V1's primary responsible-gaming control. It does not exist.

### 6.2 "Self-exclude now — In-app: Settings → Account → Self-exclude" — FALSE

The page gives step-by-step instructions for a flow that is not built. `mobile/lib/features/home/home_screen.dart:246` states plainly: *"Self-exclusion + profile settings land in V1."* The page also promises an email fallback actioned "within one working day" against a registry that does not exist to record it in.

### 6.3 "Age is verified at registration and at every purchase" — PARTIALLY FALSE

Registration is genuinely gated: `identity/service.py` enforces `MIN_AGE_YEARS = 18`, backed by a database CHECK constraint. Good. **There is no age check in the purchase path** — `ticket/routes.py::purchase` validates draw state and entitlement only. The words "and at every purchase" are not true.

### 6.4 Assessment

A platform taking money for prize draws, publishing a responsible-play page that describes a permanent self-exclusion regime, and operating no such regime, is in my judgement the single largest compliance exposure in this repository — larger than the classification question, because it is a concrete, demonstrable, documented misstatement to consumers rather than an unresolved question of law.

It is also made materially worse by two recent decisions: unlimited per-user entries with no spend ceiling, and the removal of the free route (which that very page cited as a harm-reduction control, and which this diff correctly removed from it, leaving the page thinner still).

**Required:** either build ADR-010, or amend the page to describe what Atlas actually does today. I am indifferent as to which. I am not indifferent as to whether. Until one happens, the page should not be publicly reachable.

---

## 7. Conditions for merge

**Blocking:**

1. §5.2(a) — residual classification claims added to the counsel package; no expansion meanwhile.
2. §5.2(b)/(c) — sweep every non-code surface for withdrawn free-route copy. Owner: 🎨 Sally with me.
3. §6 — responsible-play page either corrected or taken offline. This blocks independently of everything else in this review and should not wait on counsel.

**Not blocking this merge, but blocking real-user launch:**

4. REVIEW-001 §3.1 / §3.2 remediation, or an explicit founder decision to launch without it, recorded.
5. `docs/compliance/skill-questions.md` — mine to draft, now Phase 3 critical path.
6. PRD §1 and §3.1 amendment through `delivery-framework.md §12`. The PRD still describes two load-bearing mechanisms; one is gone.
7. ADR-001 / ADR-004 / ADR-005 free-route references — amendment through 🏗️ Winston. Correctly left untouched in this diff.
8. Counsel brief Q1/Q5/Q7 rewritten off the void NLA 2005 framing **before transmission**.

---

## 8. Position

I approve the engineering. I cannot approve the posture, and I record that the posture now rests entirely on a mechanism this office rejected in REVIEW-001 §3.1 and has not re-approved.

The founder may proceed over this review — that is what Tier 3 means, and §2 is dissent, not obstruction. §6 is different. It is not a matter of classification judgement or legal uncertainty; it is a page telling consumers that a protection exists when it does not, and it should be fixed this week whatever else is decided.

— ⚖️ Adaeze

---

# Addendum A — §5.2(b) surface sweep

**Added:** 2026-11-24 by ⚖️ Adaeze. Discharges §7 blocking item 2.

## A.1 Scope

Swept `_bmad-output/`, `docs/`, `README.md`, `admin/`, `mobile/` for free-route copy and for the phrases I approved in REVIEW-001 §2.2 and §2.5 and have now withdrawn. **No App Store listing, marketing draft, or investor deck exists in this repository** — if any exists outside it, it is unswept and remains the founder's to check.

## A.2 A finding that reframes the decision — R-FREE-01

The free-entry route was **never operable.** Per my own REVIEW-001 §6.1 and the carry-forward in `design/wireframes/07-winner-claim-start.md`:

> **R-FREE-01** — postal address for free entry does not exist as a leased P.O. box. Placeholder acceptable for demo; real address required for real-user launch.

No P.O. box was ever leased. For the whole of V0.5 the public surface advertised a free postal entry route with no address to post to.

Two consequences I must state plainly:

1. **This materially softens my §2 dissent.** I objected to removing the mechanism the research ranked as having the most traction. That mechanism was a claim, not a capability. Removing an inoperable route is more honest than retaining it, and the founder's decision looks better in that light than it did when I wrote §2. The dissent stands as to sequencing; it no longer stands as to substance.
2. **It is the same defect as §6.** Self-exclusion described but not built; free route described but not addressable; age verification "at every purchase" not enforced. Three instances, one pattern: consumer-facing copy running ahead of implementation. That pattern is the risk, not any single claim.

**R-FREE-01 and R-SKILL-01 are recorded only inside a Day-9 wireframe, not in `docs/risk-register.md`.** The risk register is mine. That is my own omission and I am recording it as such; both belong in the register, where they would have been visible to the founder before this week.

## A.3 Disposition of swept surfaces

**Live surfaces — corrected (no further action).**

| Surface | Action |
|---|---|
| `admin/.../how-it-works/page.tsx` | Free-route sections and two legal conclusions removed (§5.1) |
| `admin/.../responsible-play/page.tsx` | Corrected against reality (§6) |
| `docs/runbooks/payment-outage.md` | On-call was told a free route remained available during a Paystack outage. It never existed. Corrected 2026-11-24 |
| `docs/VISUAL-WALKTHROUGH.md` | Screenshot-set caveat added; stale narration corrected |
| `README.md` §Legal model | Under-review notice added |
| `mobile/lib/.../home_screen.dart` | `FREE`/`PAID` badge **correctly retained** — renders historical tickets truthfully |
| `mobile/lib/design/tokens/radii.dart` | Comment only, no user-visible copy. Leave |

**Versioned artefacts — require the `delivery-framework.md §12` amendment process. NOT to be edited in place.**

| Artefact | What is now wrong |
|---|---|
| `PRD.md` §1, §2, §3.1, §4, §10 | Describes two load-bearing mechanisms; one is gone. §3.1's `entry_source` enum, the postal-route spec, and the per-draw disclosure requirement are all stale |
| `delivery-framework.md` §§49-52, 122, 131, 260, 321, 394 | Phase gates and exit criteria that reference free-route operationalisation and Legal Counsel approval of free-entry copy |
| `counsel-engagement-brief.md` §2, §3 Q1/Q5/Q7 | Rewrite before transmission — §7 item 8 |
| `docs/adr/ADR-004` §51, `ADR-005` §67 | Free-entry references. Amendment through 🏗️ Winston per CLAUDE.md |

**Historical records — DO NOT REWRITE.** Design wireframes 01-15, `design/tone-doc.md`, `design/tokens.md`, week-1/week-2 checkpoints, `week-5`/`week-7` build plans, `v0.5-demo-plan.md`, `v0.5-close.md`, `test-artifacts/test-design/week-5-tickets-draws.md`, and REVIEW-001 itself are records of what was decided and built at the time. Editing them to match today's product would falsify the audit trail — the same objection I raise to rewriting a published proof (§4.1). They are superseded, not wrong.

**The practical consequence for 🎨 Sally:** wireframes 02, 03, 10 and 15 specify surfaces that no longer exist (`FreeEntryDisclosure`, the Part B free-entry-route detail page with its PDF form download, the operator transcription screen). They need superseding notices at the top pointing here, not edits to their bodies. That is a design-register task, not a copy pull.

## A.4 Revised position

§5.2(b) and (c) are **discharged** for every surface inside this repository. No withdrawn copy remains on a live surface.

My §7 ordering changes on the strength of A.2. The responsible-play page (§6) was already first and stays first. But R-FREE-01 shows the project's real exposure is not any individual claim — it is that consumer copy has repeatedly shipped ahead of implementation with no gate catching it. I am adding a standing requirement, and it is mine to enforce:

**No consumer-facing claim about a control, protection, or entry route ships unless the implementing code exists and a test asserts it.** Three breaches found this week, all pre-existing, none caught by CI. 🧪 Murat — this is a testability question as much as a compliance one, and I would like your view on whether a copy-to-capability assertion can be mechanised the way the ADR-002 outbox gate was.

— ⚖️ Adaeze

---

# Addendum B — ADR-010 Phase A review

**Added:** 2026-11-24 by ⚖️ Adaeze. Discharges §7 blocking item 3 (responsible-play page) and reviews the implementation behind it.

## B.1 Verdict

| Item | Verdict |
|---|---|
| ADR-010 amendment (two-phase, spec written before code) | **Approved.** |
| Phase A implementation | **Approved.** |
| Enforcement coverage | **Approved — and it closed a defect I had not found.** |
| Wallet balance held rather than refunded | **Approved for Phase A, conditionally (B.3).** |
| Responsible-play copy | **Approved.** §7 item 3 **discharged** — the page no longer states anything untrue. |
| Admin registry surface | **Approved.** |
| **Overall** | **Approved for merge**, subject to B.3 and 🧪 Murat's sign-off. |

This is the first change this week I can approve without a standing objection attached.

## B.2 What I checked, and what satisfied me

**The copy now matches the code, claim by claim.** I checked each surviving assertion against an enforcement point:

| Page claim | Enforced by | Verified |
|---|---|---|
| "You can close your account permanently" | `self_exclusion.exclude()` → registry row + `status='closed'` | ✅ test asserts row, status, revoked sessions |
| "You are signed out everywhere" | `revoke_all_for_user` in the same transaction | ✅ `test_revoked_session_cannot_be_reused` |
| "No further entry is possible, on any route" | `issue_paid` + `next_question` + route pre-check | ✅ service-layer tests on both |
| "We cannot reopen it" | No un-exclude route, no `revoked_at` column, no admin control | ✅ three tests assert absence |
| "There is not yet a switch for this in the app" | Was true when written; **now superseded by A5** — see B.4 | ⚠️ |
| "Does not stop someone opening a new one" | Phase A is account-level | ✅ `test_phase_a_does_not_block_reregistration` |

**The enforcement defect.** The base ADR named KYC, registration and login and omitted **purchase**. I did not catch that in REVIEW-001 or in REVIEW-002 §6, and it is the gap that would actually have mattered: a user who closed their account while holding a live session could have bought a ticket. It is now checked in `ticket.service.issue_paid` — the service layer, not only the route, which is correct because the payment webhook reaches that function without passing through HTTP. Credit where due; that was found by reading the code rather than the ADR.

**The test I value most** is `test_phase_a_does_not_block_reregistration`. It asserts a *limitation* rather than a capability, with a comment saying it must fail loudly if Phase B lands. That is the mechanised copy-to-capability check I asked Murat for in Addendum A.4, implemented for one claim. It is the pattern I want generalised.

**Audit.** `self_exclusion.activated` carries `bvn_enforced: false`, so an auditor can separate Phase A from Phase B rows without inspecting the registry for NULLs. The event is allowlisted in the ADR-002 gate as deferred. Correct on both counts.

**Admin surface.** Read-only with no mutation verbs, and `test_registry_has_no_mutation_verbs` asserts it — so adding an un-exclude control becomes a failing test rather than something I have to catch in review. The Phase A limitation is stated on the page itself, where the operator reads it, not only in the ADR.

## B.3 Condition on the held balance

ADR-010 requires a closed account's balance be refunded to the originating payment method. Phase A holds it instead, because no Paystack refund call exists and `docs/compliance/escheatment-policy.md` — my artefact — was never drafted.

**Holding is acceptable for Phase A, on two conditions:**

1. **The user must be told.** Nothing in the current copy mentions what happens to a balance. In V0.5 the wallet is winnings-only and non-zero balances at closure are rare, but "rare" is not "never", and a user who closes an account with money in it must not have to guess. One sentence on the closure screen and the responsible-play page: the balance is retained and support will arrange payment. **I will draft it.**
2. **The escheatment policy is mine and is overdue.** It gates Phase B. I am recording it as outstanding against me, not against engineering.

This condition does not block the merge. It blocks calling Phase A finished.

## B.4 One copy line already stale

The responsible-play page says *"There is not yet a switch for this in the app."* That was true when written this morning. **A5 then shipped** — there is now a "Close my account" control on the account panel and a dedicated screen.

The line must be corrected to point users at the in-app route, with support as the fallback. Minor, and the error is in the safe direction — understating a capability rather than overstating one, which is the opposite of every other defect found this week. But it is still a page saying something untrue, and the standing requirement in Addendum A.4 does not have a size threshold. **I will fix it with the B.3 wording in one pass.**

## B.5 On the mobile screen specifically

I reviewed `self_exclusion_screen.dart` as regulatory copy, which it is.

It states the limitation in a panel headed *"What this does not do"* **above** the confirmation field rather than below it, carries no retention offer or softer alternative, and points at independent support resources as more useful than the button itself. That last line is the one I would have asked for and did not have to.

The one thing I will keep watching: the entry point is an underlined text button at the bottom of the account panel. Findable without being promoted is the right call for V1. If a future design review proposes burying it further, that comes to me.

## B.6 Outstanding after this change

Unchanged from Addendum A.4 except where noted:

- **Mine, overdue:** `docs/compliance/skill-questions.md`; `docs/compliance/escheatment-policy.md`; B.3 and B.4 copy.
- **R-REG-09 stands.** The skill question remains the sole classification mechanism and remains rejected for real-user launch. Nothing in this change touches it.
- **No per-user entry cap, no spend ceiling.** Winston flagged it in §7 of his plan and he is right: a responsible-play posture resting on exclusion alone is thin. Founder decision.
- **Phase B is blocked on ADR-007**, and the stronger copy stays withdrawn until it ships.

— ⚖️ Adaeze


---

## Addendum B postscript (2026-11-24, same session)

B.3 and B.4 are **closed**. Applied in one pass:

- The responsible-play page now points users at *Account → Close my account* in the app, with email as the equal alternative rather than the fallback-for-the-determined.
- Both the web page **and** the mobile closure screen now state that a balance is held and paid out by support, not forfeited. I put it on the mobile screen deliberately: the decision is taken there, so the disclosure belongs there, not only on a page the user may never open.

Still outstanding against me: `docs/compliance/skill-questions.md` and `docs/compliance/escheatment-policy.md`.

— ⚖️ Adaeze
