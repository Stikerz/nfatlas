# Project Atlas — V0.5 Design Pass, Week 2 Exit Checkpoint

**Date:** 2026-07-09 (Day 14 per `tone-doc.md §8`)
**Author:** 🎨 Sally (BMad UX Designer)
**Status:** Awaiting founder sign-off. This is the exit gate for Week 2 and for the whole 14-day design pass. Founder sign-off (or amendment) unblocks Amelia's Week 3 backend build start.
**Pairs with:** `week-1-checkpoint.md`, `tone-doc.md`, `tokens.md`, `components.md`, all wireframes 01–15, `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md`.

---

## 0. Purpose

Per `tone-doc.md §8` Day 14, the exit protocol is a founder read of the whole system followed by a handoff to Amelia. This document supports that read and stages the handoff.

Read this alongside `week-1-checkpoint.md`, which covered the consumer surface and the compliance amendments applied at Day 7. This one covers everything since — the operator surface (Days 8–10), the public proof page (Day 11), the trust-story pages (Day 12), the design-system consolidation (Day 13) — and closes the pass.

---

## 1. What shipped in Week 2

**Wireframes (8 files, wireframes 08–15):**

- **wf-08 — Admin login + admin shell primer.** Login screen + the sidebar/topbar shell every subsequent admin wireframe inherits. Operator seeded as *"Adaobi Ibe"* (Nigerian name per tone-doc §7).
- **wf-09 — Create draw.** The commit-reveal ceremony act 1 (per ADR-006). Five sub-screens ending in a type-to-confirm `PUBLISH` modal and a commitment receipt with downloadable JSON.
- **wf-10 — Transcribe free entry.** The surface that turns wireframe 03's *"same odds, same pool, same shot"* promise into a system. Structured around Adaeze's parity invariant (same table, same code path, self-exclusion check runs before ticket creation). **Working draft routed to Adaeze mid-Day-9** per REVIEW-001 §7.
- **wf-11 — Close draw.** Ceremony act 2. Publishes `tickets_hash`. Type-to-confirm `CLOSE`. Warning if free-entry queue is non-empty.
- **wf-12 — Reveal draw.** Ceremony act 3. Six sub-screens; the five-step ceremony (fetch Bitcoin → fetch drand → decrypt seed → compute winner → publish); pause between compute and publish for review; belt-and-braces self-exclusion check on the candidate winner; local replay verification before publish; type-to-confirm `REVEAL`; receipt with copy-verifier-command affordance.
- **wf-13 — Audit log (admin).** Adaeze's daily home. `ChainStateBanner` at top always shows chain integrity; broken-chain state is immovable and loud. PII-redacted-by-default payload viewer with reveal-with-reason; every reveal writes a meta-audit event. Deterministic export (JSON + CSV) with a separate gated un-redacted variant.
- **wf-14 — Public proof page.** The wow moment. Anchor-5 (Coinbase) treatment — hash typography as first-class, three-way verifier (download / CLI / reproduce). Winner name never in indexable HTML per REVIEW-001 §4.5 — client-side hydration only, opt-in via wf-07 consent checkbox, anonymous fallback everywhere else. **Working draft routed to Adaeze on Day 11** per REVIEW-001 §6.4.
- **wf-15 — Trust-story pages.** Three pages in one file: How Atlas works (the explanatory home for the classification claim relocated from consumer surfaces per REVIEW-001 §2.1), Free-entry-route detail (with the R-FREE-01 placeholder WarningNote structurally visible), Responsible play (self-exclusion + duty-of-care, with a *"Before you self-exclude"* softer-alternatives section flagged as a design stance for Adaeze).

**Design system (1 file):**

- **components.md** — the 15 primitives specified with props, variants, states, tokens consumed, accessibility contract, and per-wireframe usage index. Compositions catalogue in §18 lists ~40 one-off compositions and points at their host wireframes. §20 explicit handoff notes to Amelia (code locations, build order across Weeks 3–7, when to ping whom).

**Ceremony vocabulary landed:** `PUBLISH` / `CLOSE` / `REVEAL` for the three operator acts + `EXPORT` for un-redacted audit-log exports. Matches the consumer-side `EXCLUDE` for self-exclusion per ADR-010 — same discipline of typed-confirmation for irreversible actions across the whole product.

---

## 2. What changed since Week 1 checkpoint

Nothing was retracted. Amendments to Week-1 wireframes at Day 7 (per REVIEW-001) hold as documented in `week-1-checkpoint.md §2`. Week 2 is additive.

Two small additions to already-drafted Week-1 wireframes made in Week 2, both captured in each wireframe's `Amended:` header:

- **wf-07 §4.1** — DOB field became read-only pre-fill from registration (cascade from the wf-01 amendment). Already noted in `week-1-checkpoint.md §2`.
- No other Week-1 wireframes touched in Week 2.

**Adaeze's REVIEW-001 has not been re-run** against Week 2's wireframes (08–15) as of this checkpoint. Her early-look flags landed on wf-10 (routed Day 9) and wf-14 (routed Day 11); she has not yet responded to either. Neither is blocking Amelia's Week 3 start — the questions Adaeze will raise are mostly copy-and-policy amendments that can be applied in parallel with backend build.

---

## 3. Composite state — the whole design pass

**Total artefacts:**
- 15 wireframes (wf-01 through wf-15)
- 1 tone doc
- 1 tokens doc
- 1 components spec
- 2 exit checkpoints (Week 1, this one)
- 1 compliance review (REVIEW-001)

**Surfaces covered:**
- Consumer mobile (Flutter): 7 flagship-flow steps end-to-end (register → browse → skill+payment → ticket artefact → notification → winner claim start).
- Operator admin (Next.js): 5 flagship-flow steps (login → create draw → transcribe free entry → close draw → reveal draw → audit log).
- Public web (Next.js, no login): public proof page + three trust-story pages.
- Email (Mailhog in V0.5): 3 templates (winner / non-winner / ticket-confirmed).

**Surfaces deliberately not in this pass:**
- Admin draw-detail page — implicit context in wf-11 / wf-12 / wf-13 but not fully specified. A follow-on wireframe when the state-machine work firms up.
- Admin ticket-detail page — inspect-a-ticket surface. Similar deferral.
- Admin claim-review page — operator side of the winner claim (wf-07 is consumer). Deferred to a follow-on wireframe as noted in wf-07's status.
- Admin user-detail page — search + inspect a user account. Similar deferral.
- Consumer settings screen (incl. self-exclusion confirmation flow) — flagged in Adaeze's §6.3 as a V1 pre-launch task.
- Consumer notification-preferences screen — V1.
- V1 dark mode, real MFA, real push notifications, etc — plan §3 non-goals.

These deferrals are documented; nothing is silently missing.

---

## 4. What I need from founder to close Week 2

Six decisions carried forward from Week 1 (§4 there — biggest one is #6 counsel brief). New ones from Week 2:

7. **Ceremony vocabulary — 4 typed-confirm words** (`PUBLISH` / `CLOSE` / `REVEAL` / `EXPORT`). The consistency is deliberate; the count is a small friction tax. Recommend keep. If it feels over-templated, `EXPORT` is the one I'd drop first.
8. **Publish-button attention-tint** on wf-09 §5.3, wf-11 §2.1, wf-12 §2.1. A subtle 12% attention-colour hint on the primary button for irreversible actions. Recommend keep — a small pre-modal visual cue reinforces "this is different."
9. **Human-readable draw IDs** (`DRAW-2026-07-08-A` vs opaque UUIDs). Recommend human-readable for operator surfaces + audit log + public /proof URLs.
10. **Type-to-confirm friction on `PUBLISH` / `CLOSE` / `REVEAL`.** ~2s of typing per irreversible action. Recommend keep; alternative is hold-to-confirm gesture if it feels excessive after the demo.
11. **Verifier command visibility** on the admin reveal receipt (wf-12 §6). The `python -m atlas.verify …` string is engineer-flavoured; keep on admin surface or engineering-only?
12. **Ceremony pacing** (wf-12 §2). Steps 1–4 auto-run, pause between compute and publish. Alternative is manual step-through per step. Recommend current — the compute/publish pause is the meaningful gate.
13. **Operator-visible contact info for the candidate winner pre-publish** (wf-12 §4). Necessary operationally (KYC follow-up context) but a PII-exposure surface. Confirm.
14. **Public web mirror of trust-story pages** (wf-15 Part A, B, C also served at `atlas.ng/how-it-works`, `/free-entry`, `/responsible-play`). Is this in V0.5 scope or V1? Recommend V0.5 for `/free-entry` and `/responsible-play` (regulatory discoverability requirement), V1 for `/how-it-works`.

---

## 5. What Amelia will need before Week 3 begins

The explicit handoff. Amelia — reading order:

**Read first (context — 30 min):**
1. `v0.5-demo-plan.md` — the target you're building toward. Read the whole thing.
2. `week-2-checkpoint.md` (this doc) — the map of what exists.
3. `tone-doc.md` — the voice the product speaks in. Especially §5 (copy voice).

**Read as you build (per module):**
4. `tokens.md` — the design tokens. Land these in code first (Week 3 Day 1) before anything else.
5. `components.md` — the 15 primitives + the compositions catalog + your handoff notes in §20. Build the primitives per §20.2 build order.
6. `wireframes/{01..15}.md` — read the ones matching the module you're building. Don't try to read all 15 up front; they're specs, not narrative.

**Read when compliance-adjacent code lands:**
7. `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md` — the invariants Adaeze committed. Especially the invariants for the ticket module (parity §2.2), the audit log (§4 + §6.5), and the claim flow (§5).
8. `docs/adr/ADR-{003,004,005,006,007,010}.md` — the ADRs your build must honour. Winston already approved these.

**When you hit a design question the wireframe doesn't answer:**
- Ping Sally in the shared channel. Don't work around it in code — that produces silent divergence per components.md §1 principle 7.

**When you hit a compliance/policy question the ADRs don't answer:**
- Ping Adaeze. Especially anything about redaction, consent, self-exclusion, or audit-log content.

**When you hit an architecture/schema question:**
- Ping Winston. Especially anything about module boundaries, event shapes, or ADR amendments.

**When you hit an infra/deploy/security question:**
- Ping Tobi. Especially anything about secrets, S3 access, CI, or the runbooks.

### 5.1 Contract points I owe Amelia

Documented across the wireframes; pulling into one list here:

- **Ticket module invariants** (per REVIEW-001 §7 + wf-10):
  - Free-route + paid-route tickets in the same table, differ only by `entry_source`.
  - Skill-question rotation as a code-enforced invariant (per-user ≥ 30 days, global cap, difficulty variance) — Adaeze owns the rotation policy at `docs/compliance/skill-questions.md`.
  - 3-strike rate limit + cooldown on skill-question attempts (R-SKILL-01).
- **Draw engine invariants** (per REVIEW-001 §2.2 + wf-12 + ADR-006):
  - Uniform-random selection over the full pool; no weighting by entry source. Winston confirms via ADR-006 amendment if not already explicit.
- **KYC adapter invariants** (per REVIEW-001 §5.3 + ADR-007):
  - NIN verification via NIMC is a primary path across shortlisted vendors.
- **Claim state machine** (per REVIEW-001 §7 + wf-07 amendment):
  - 6 states: `created → in_review → approved | rejected → payment_pending → paid | payment_failed → complete`.
  - `payment_failed` needs a distinct consumer-facing state.
  - Rejection has 4 sub-states (kyc_failed / bvn_mismatch / under_review / self_excluded) with distinct consumer-surface copy (wf-07 §8.3 post-amendment).
- **Audit log** (per REVIEW-001 §7 + wf-13):
  - Client-side JCS canonicalizer for chain-check-on-panel-open (defense in depth).
  - Meta-audit events for PII reveals (`payload.pii_revealed`) and exports (`data.exported`).
- **Public proof surface** (per wf-14):
  - `atlas.ng/proof/{draw_id}` — SSR, aggressively cached (proof immutable after reveal).
  - `winner-display` hydration endpoint — no-cache, robots-disallowed.
  - `proof.json` download is byte-identical to the `/api/v1/draws/{id}/proof` response.
  - `atlas-verify` published as a real PyPI package (Winston + Amelia joint).
- **Idempotency (ADR-004)** on every consequential POST — `POST /entries`, `POST /admin/tickets`, `POST /admin/draws`, `POST /claims`, and all state transitions.
- **Ledger discipline (ADR-003)** — kobo-integer money, no floats, no mutable `balance` column.

### 5.2 What Amelia can start on Day 1 of Week 3

Per `v0.5-demo-plan.md §5` Week 3:
- Repo scaffold (Docker Compose, Dockerfiles, FastAPI shell, Flutter + Next.js shells, migrations baseline, seed script skeleton, Mailhog wired). Tobi supports.
- Identity module (register/OTP/login) end-to-end.

For identity module, Amelia's UI dependencies per components.md §20.2:
- **Primitives needed:** Button, Input (text/password/date/phone/otp variants), Banner, Modal, Toast, bottom Nav.
- **Wireframes:** wf-01 (register/OTP/password/welcome), wf-08 (admin login).

These primitives are the ones I'd sequence first — they unlock Weeks 4+ implicitly. Everything else builds on them.

---

## 6. What Adaeze still owes (non-blocking for Week 3)

Recording so nothing gets forgotten between now and Phase 3:

- REVIEW-002 covering wireframes 08–15 (specifically the compliance-adjacent surfaces: wf-10 parity invariant, wf-13 chain-state + PII redaction + retention, wf-14 public proof + winner-name treatment, wf-15 trust-story copy).
- `docs/compliance/skill-questions.md` — the Phase 3 question-pool architecture (rotation, difficulty tiers, review cadence).
- `docs/compliance/copy/privacy-notice.md` — NDPA-aware draft, to be lawyered.
- `docs/compliance/copy/t-and-c.md` — first-cut T&Cs including the classification claim relocated from app copy per REVIEW-001 §2.1.
- `docs/risk-register.md` updates — R-FREE-01, R-SKILL-01, R-CONSENT-01, R-NDPA-01.
- Nigerian responsible-play helpline identifier (open in wf-07 §5.6.d and wf-15 Part C §3/§5).

Adaeze indicated in REVIEW-001 §7 that these are her Phase-3 pre-work; they get pulled forward when the counsel opinion lands.

---

## 7. What's not blocking Week 3 but will block real launch

Compiling for founder visibility so nothing lands on Amelia mid-build unexpectedly:

**Compliance / policy (mostly Adaeze + counsel):**
- Counsel-engagement brief moves from Draft to Sent (still #6 in Week-1 checkpoint §4, still the biggest downstream bottleneck).
- Nigerian licensing research completed (`research/domain-nigerian-prize-competition-licensing-research-2026-06-30.md` still aborted at step 1).
- Skill-question pool architecture (Adaeze — Phase 3).
- Privacy Notice + T&Cs drafted + lawyered.
- NDPA data-subject-rights UI (V1 pre-launch).
- Cookie consent (V1 for admin + marketing site).

**Operational infrastructure (mostly Tobi + Adaeze):**
- Postal address P.O. box procured + transcription operations set up (R-FREE-01).
- Real MFA on admin login (wf-08 §7).
- Session-timeout UX (wf-08 §7).
- SPF / DKIM / DMARC on production email domain (REVIEW-001 §4.4).
- S3 SSE-KMS + access logs for ID documents (REVIEW-001 §5.9).
- Real KYC vendor selection (ADR-007 amendment).
- Real WhatsApp Business channel wired (V1).

**Product surfaces I deferred to V1 pre-launch (my own work):**
- Anonymous variant of the reveal page + non-winner banner (per REVIEW-001 §4.3 winner-name consent cascade).
- Consumer settings screen with self-exclusion confirmation flow surfacing wallet refund (per ADR-010 + REVIEW-001 §6.3).
- Full free-entry-route page P.O. box removal of the V0.5 WarningNote (wf-15 Part B §3 — must remove at real launch, its persistence would itself be a compliance incident).
- Admin draw-detail / ticket-detail / claim-review / user-detail follow-on wireframes.
- V1 uploader on wf-09 (currently URL-only).
- V1 push notifications displacing on-launch fetch (wf-06 §7).

None of the above blocks Week 3. All of it blocks real launch.

---

## 8. Retrospective from 14 days

What worked:

- **Ritual anchors held.** *"You're in."* / *"Not this time."* / *"Claim received."* / *"You've been paid."* / *"This draw is verified."* — declarative sentences about what just happened, without game-show voice, without exclamations, without marketing tropes. When I read the wireframes as a system, the product has a mouth.
- **The three-word ceremony vocabulary** (`PUBLISH` / `CLOSE` / `REVEAL`) plus the consumer-side `EXCLUDE` created coherence I wasn't planning for. Reads as *"whenever Atlas does something irreversible, it asks you to name the action"* — a discipline that generalises.
- **The Anchor 5 (Coinbase) reference for the proof page** did specific work I couldn't have designed without it — hash typography as first-class, terminal-block visual for the verifier command, calm authority over celebration. Naming the anchor and naming the specific thing to take from it (not "everything about it") is a pattern I'll keep using.
- **Adaeze reviewing wf-03/04/06/07 as a set** at Day 7 (not piecemeal) surfaced coherence issues (the repeated legal-classification claim, the missing consent-capture cascade from wf-06 back into wf-07, the missing NDPA footings across the board) that would have cost more to fix if she'd seen them one at a time.
- **Adaeze's REVIEW-001 shifted the classification claim from consumer surfaces to trust-story pages** in a way that improved the product — the consumer surfaces are cleaner, the explanatory surface (wf-15) carries the claim honestly, and counsel gets a stable target to review.
- **The design invariants sections** in each wireframe (wf-05 §4 ticket artefact, wf-09 §8 create draw, wf-10 §4 free-entry parity, wf-14 §8 proof page) proved useful — they name what future changes must not break, so an amendment is a conscious choice rather than a drift.

What I'd do differently:

- **Should have flagged the postal address earlier** — Adaeze caught in REVIEW-001 §6.1 that wf-03 references a P.O. box that doesn't exist. Same lesson from Week 1 retro; didn't apply it fast enough in Week 2 (the postal address is now surfaced structurally via the WarningNote on wf-15, but I could have raised it Day 4).
- **The wf-14 audit-trail excerpt should have shown actor** or *deliberately* omitted it with a note about why. I made the decision to omit but didn't document the reasoning at time of design — Adaeze may push back.
- **The anonymous reveal-page variant** got flagged twice (Week 1 checkpoint + wf-06 amendment) but was never drawn. It's a small drawing job; I should have just done it inline with the wf-06 amendment. Deferring it to V1 is defensible but not ideal.
- **The compositions catalog in components.md §18 grew to ~40 items.** That's a lot. Either my design was under-decomposed (some compositions should be primitives) or the tone-doc's target of "15 core components" was optimistic. I'd revisit the primitive/composition threshold in a V1 design system pass.
- **Should have spent 30 minutes drawing the admin draw-detail page in wf-11 §1** rather than leaving it "implicit context". The three admin surfaces that reference it (wf-11, wf-12, wf-13) each assume it exists but nobody has designed its shape. Amelia will build something reasonable, but a working wireframe would have been cheap.

What's genuinely uncertain going into Week 3:

- **Whether the atlas-verify CLI package (wf-14 §3.7 path 2, wf-12 §6.2 copy verifier command) actually ships in V0.5.** I've written the wireframes as if it does; Amelia + Winston need to confirm the effort is in scope. If it doesn't ship for V0.5, wf-14's "Three ways to check" section changes — down to two — and that's a tone loss on the wow moment.
- **Whether Adaeze's REVIEW-002 will surface Week-2-specific amendments** that cascade into wireframes I thought were settled. wf-13 (audit log) and wf-14 (proof page) are the most likely surfaces to attract compliance nuance.
- **Whether the demo can be walked end-to-end in ≤ 5 minutes** per `v0.5-demo-plan.md §1`. My wireframe count (15) means the demo has to be selective; the founder-rehearsal process will surface which screens make the cut for the 5-minute walkthrough and which sit in the "and here's how X works" post-hoc discussion.

---

## 9. Cross-references

- Design pass artefacts: `_bmad-output/planning-artifacts/design/{tokens.md, tone-doc.md, components.md, week-1-checkpoint.md, this file, wireframes/01..15.md}`.
- Compliance review: `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md`.
- V0.5 plan: `_bmad-output/planning-artifacts/v0.5-demo-plan.md`.
- Delivery framework: `_bmad-output/planning-artifacts/delivery-framework.md`.
- Agent operating model: `docs/AINE-AGENTS.md`.
- ADRs: `docs/adr/ADR-{001..012}.md`.
- Runbooks: `docs/runbooks/` (Tobi).
- Counsel brief (still Draft): `_bmad-output/planning-artifacts/legal/counsel-engagement-brief.md`.

---

## 10. Recommended founder read-through order (for the exit-gate read)

If you're reading the whole pass before signing off — I'd read in this order:

1. **`tone-doc.md`** — voice + Nigerian cultural context. 20 min.
2. **`v0.5-demo-plan.md §1-2, §6`** — audience, flagship flow, success gates. 10 min. (You've read this before but re-orienting.)
3. **`week-1-checkpoint.md §4 + §7`** — the six founder decisions parked at Week 1, plus my retro. 5 min.
4. **This document §4 + §8** — the additional decisions parked at Week 2 + this pass's retro. 5 min.
5. **Wireframes 01, 02, 04, 05, 06, 07 — consumer flow end-to-end.** ~60 min. Read the layouts and the copy tables; skim the state and accessibility sections unless something reads off.
6. **Wireframes 03 + 15 — trust story.** 30 min. Read the copy carefully; this is where the compliance-load-bearing language lives.
7. **Wireframes 09 + 11 + 12 — operator ceremony.** 30 min. Focus on the type-to-confirm gates and the receipts.
8. **Wireframe 14 — public proof page.** 20 min. Read as if you were a journalist arriving at the URL cold.
9. **`components.md §1 + §2 + §18 + §19 + §20`** — the principles, the 15 primitives at glance, the compositions catalog, deliberate exclusions, Amelia handoff notes. 15 min.
10. **`docs/compliance/reviews/REVIEW-001` §0 + §7** — the standing caveat + the actions Adaeze parked with each agent (including you). 10 min.

Total: ~3 hours. If you want to short-circuit: just steps 1, 5, 8, and 10. That's ~90 min and covers the tone, the consumer story, the wow moment, and the compliance ceiling.

---

🎨 *End of Week 2 checkpoint.*

*14 days of design. 15 wireframes. 1 tone doc. 1 tokens doc. 1 components spec. 1 compliance review. 2 exit checkpoints.*

*Founder — this is where the design pass closes. Sign off, amend, or push back on anything in §4. On sign-off, Amelia begins Week 3 with the reading order in §5.*

*Amelia — the primitives in components.md §20.2 for Week 3 identity are Button, Input (all variants), Banner, Modal, Toast, Nav (bottom). Wireframes 01 and 08 are your source of truth for the identity flows. Ping me on any spec ambiguity before working around it in code.*

*Adaeze — REVIEW-002 on Week 2 wireframes (08–15) is the outstanding compliance ask; not blocking Week 3 but worth landing before wf-14 goes public.*
