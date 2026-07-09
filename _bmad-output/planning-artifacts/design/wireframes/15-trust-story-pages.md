# Wireframe 15 — Trust-Story Pages (How Atlas works · Free-entry-route detail · Responsible play)

**Drafted:** 2026-07-08 (Day 12 per `tone-doc.md §8`)
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** Draft — **hard-blocking review by ⚖️ Adaeze required before ship** (this is where the compliance-load-bearing copy that REVIEW-001 §2.1 relocated from consumer product surfaces properly lives) + founder review at end of Week 2. The three pages together carry the legal-classification claim, the free-route mechanic detail, the self-exclusion commitment, and the responsible-play stance — all in one Day-12 batch since they share voice, visual language, and cross-reference each other heavily.
**Covers:** Flagship flow steps 15 and 16 from `v0.5-demo-plan.md §2` — *"How it works — one page explaining prize competition (not lottery), free entry route, skill question, provably fair draw"* + *"Responsible play — self-exclusion mentioned, permanent commitment stated."* Plus the free-entry-route detail page which wireframe 03 §3.6 links to via *"See full details, form download, and postal address"*.
**Surface:** Flutter consumer app primary (in-app trust-story pages accessible from wf-02 §2.4 home links). Public web mirror at `atlas.ng/how-it-works`, `atlas.ng/free-entry`, `atlas.ng/responsible-play` — same content, adapted layout, must be discoverable without app install (regulatory requirement per counsel-brief expectations).
**Pairs with:** `03-free-entry-disclosure.md` (the disclosure sheet whose "See full details" link points to Part B here), `02-browse-active-draw.md §2.4` (home surface trust-story link row), `07-winner-claim-start.md` (winner claim; responsible-play page links to self-exclusion), `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md` (the review this wireframe answers structurally), ADR-010 (self-exclusion — Part C surfaces the flow), `docs/compliance/copy/` (future — Adaeze's authoritative copy home; this wireframe is design context around copy she owns).

---

## 0. What these three pages carry that no other pages do

Every product surface in Atlas is honest and mechanic-descriptive by design — the tone doc bans marketing language, exclamation marks, and legal-classification claims from consumer flow copy (REVIEW-001 §2.1). That discipline creates a specific gap: **where does the reader who wants to understand the mechanic, verify the legal framing, learn about the free route in operational detail, or exercise their responsible-play rights actually go?**

These three pages are the answer. They are Atlas's *explanatory* surface — where the depth lives so the product surfaces can be lean. Design implications:

1. **These pages hold the classification claim** *"a prize competition, not a lottery"* that REVIEW-001 §2.1 removed from consumer flow copy. Not as marketing; as fact. Presented once, on the page dedicated to the mechanic.
2. **These pages hold the operational detail** — postal address, entry-form download, exact steps to enter free-route — that the disclosure sheet couldn't hold without becoming a wall of text.
3. **These pages hold the responsible-play commitment** — self-exclusion is permanent, wallet balance is refunded, no cool-off reversal in V1. This is a duty-of-care surface as much as an informational one.
4. **These pages are what Atlas gives to counsel, regulators, and journalists** as a first read. If someone wants to understand what Atlas is doing without engaging with a live draw, these three pages are what they read.

**Design forces that follow:**

- **Copy weight, not chrome.** These pages are dense with text. They earn density by being *the* reference, not by being *pretty*. Layout supports reading, not scrolling-past.
- **Voice consistent with the product surfaces** — declarative, calm, no exclamations, no *"hurry"*, no *"amazing"*. But *permission to be longer-form* here that the product surfaces don't have.
- **Cross-referenceable.** These pages link to each other, to the proof page (wf-14), and to the T&Cs / Privacy Notice (Adaeze's `docs/compliance/copy/` deliverables — not designed here). A confused reader always has a next place to go.

**Non-goals for V0.5:**
- Live chat or contact widget. Support routes via named channels (WhatsApp in V1, mailto in V0.5).
- Multi-language. English-only V0.5; Igbo / Yoruba / Hausa translations are a V1+ consideration, especially for responsible-play copy.
- Interactive help / search on these pages. V1+ FAQ layer if needed.
- Marketing lift (testimonials, winner stories, hero photography). Atlas has a separate marketing site for those; the trust-story pages are informational, not persuasive.
- T&Cs and Privacy Notice content — those are Adaeze's copy artefacts (per `docs/compliance/copy/`), lawyered before publish. This wireframe designs the *presentation container* if needed but not the content.

---

## 1. Shared design vocabulary for the three pages

All three pages share the following pattern:

```
< in-app (Flutter) OR public web (Next.js) — same content, adapted layout >

┌───────────────────────────────────────────────────────────┐
│                                                           │
│  ← Back                                                   │  ← top bar; in-app returns
│                                                           │      to prior screen; web has
│                                                           │      nav breadcrumbs
│                                                           │
│                                                           │  space.800
│                                                           │
│  ▪ ATLAS · {PAGE EYEBROW}                                 │  ← gold uppercase label.micro
│                                                           │
│                                                           │  space.300
│                                                           │
│  {Page headline}                                          │  ← type.display.section
│                                                           │      (40pt Fraunces)
│                                                           │      color.text.primary
│                                                           │
│                                                           │  space.400
│                                                           │
│  {Lede paragraph — one or two sentences framing the       │  ← type.body.default
│   page. The reader who reads only the lede should walk    │      color.text.primary
│   away with the correct high-level understanding.}        │
│                                                           │
│                                                           │  space.1200
│                                                           │
│  { — section blocks, described per page — }               │
│                                                           │
│                                                           │  space.1200
│                                                           │
│  ─────────────────────────────                            │
│                                                           │
│  ▪ RELATED                                                │  ← gold eyebrow, small
│                                                           │
│  · {Cross-link 1} →                                       │  ← body.default navy links
│  · {Cross-link 2} →                                       │      always three
│  · {Cross-link 3} →                                       │
│                                                           │
│                                                           │  space.1200
│                                                           │
│  Something not clear? Contact us at hello@atlas.ng.       │  ← body.small secondary
│                                                           │      centered
│                                                           │
│                                                           │  bottom safe area / footer
└───────────────────────────────────────────────────────────┘
```

### 1.1 Shared components

- `TrustPageHeader` — new; back-link + gold page eyebrow + display headline + lede paragraph. Used identically across all three pages.
- `RelatedLinksRow` — new; three cross-links at page bottom, always three, always to *other* trust-story or evidence pages. The consistency is the point — every trust-story page tells the reader where else to go.
- `ContactLine` — new; a one-line "Something not clear? Contact us at {mailto}" footer inside the content area. V0.5 mailto: only; V1 gets WhatsApp Business channel.
- `TrustSectionCard` — new; a bordered card for a numbered or eyebrow-titled section within the page body. Same visual language as the disclosure sheet's numbered-steps card (wf-03 §3.1). `radius.large`, `surface.elevated`, hairline border, `elevation.0`, 24pt padding.
- `TrustCallout` — new; a full-width, gold-bulleted quote-style block for the *"one line that must land"* on each page. `surface.elevated` with a solid `brand.accent` (gold) 4pt left border, 32pt padding, `type.display.card` (24pt Fraunces) for the callout copy. Used sparingly (one per page).

### 1.2 Voice + rules that apply to all three pages

- Same copy discipline as tone-doc §5. No exclamations, no *"hurry"*, no marketing.
- Permission for longer sentences than product surfaces — the reader has arrived to read, not to skim past a CTA.
- Every claim that could be checked links to where to check it (proof page, audit-log request address, external Bitcoin/drand pointers).
- Every commitment made is a real commitment operationally honoured elsewhere (postal address in Part B is a real address; self-exclusion in Part C is enforced per ADR-010).
- **Every page cites the sources it depends on** at the bottom (link to relevant ADRs / spec URLs) — same discipline as `_bmad/`-style documentation. Trust-story pages are documentation for the outside world; they should behave like documentation.

---

## 2. Part A — How Atlas works (main explainer)

The primary trust-story page. Linked from wf-02 §2.4 home ("How Atlas works →"). Also public at `atlas.ng/how-it-works`.

### 2.1 Layout (per §1 shared structure; page-specific sections below)

**Eyebrow:** `ATLAS · HOW IT WORKS`
**Headline:** *How Atlas works.*
**Lede:** *Atlas runs prize competitions. Every draw has a free entry route on the same terms as the paid one, a skill question, and a provably fair result. Here is what that means, in plain terms.*

Content sections (below the lede, above the RELATED row):

```
──────────

Section 1 — What Atlas is (and what it isn't)

Atlas is a prize competition operator. Every draw offers a chance to
win a specific prize — cash, a car, a home — in exchange for an entry
that is either paid or free.

  ┌─────────────────────────────────────────────┐
  │  ▪                                          │  ← TrustCallout, gold left border
  │                                             │      display.card
  │  Atlas is a prize competition, not a        │
  │  lottery. Two things make the difference:   │
  │  a free entry route on the same terms       │
  │  as the paid route, and a skill question    │
  │  that every entrant must answer.            │
  │                                             │
  └─────────────────────────────────────────────┘

These two things are not marketing. They are the mechanic Atlas runs on,
and they are the reason Atlas describes itself as a prize competition
rather than a lottery.

──────────

Section 2 — The free entry route

Every draw at Atlas offers a way to enter without paying. It is a real
route, not a legal technicality. The free route is a postal entry:
you fill in a form (or write your details on any sheet of paper),
answer the same skill question that paying entrants answer, and post
the slip to Atlas before the draw closes. We transcribe every valid
slip into the same pool as paid entries.

  ┌─────────────────────────────────────────────┐
  │  ▪ THE RULE                                 │  ← TrustSectionCard
  │                                             │
  │  Free-route tickets and paid tickets sit    │
  │  in the same pool. The draw engine picks    │
  │  a winner from the pool without knowing     │
  │  which route any ticket came from.          │
  │                                             │
  │  Same odds. Same pool. Same shot.            │  ← italic in body.emphasis
  │                                             │
  └─────────────────────────────────────────────┘

The full free-entry route detail — the postal address, a downloadable
entry form, and step-by-step instructions — is on its own page:
See the free entry route in detail →

──────────

Section 3 — The skill question

Every paid entry (and every free-route slip) requires the entrant to
answer a substantive question. Wrong answer means the entry is void
— no ticket issued, no charge taken.

  ┌─────────────────────────────────────────────┐
  │  ▪ WHY                                      │  ← TrustSectionCard
  │                                             │
  │  The skill question is the second half of   │
  │  what makes this a prize competition rather │
  │  than a lottery. Chance alone is not what   │
  │  gets you in.                               │
  │                                             │
  └─────────────────────────────────────────────┘

The question pool is rotated. No entrant sees the same question in a
short window. The pool is not published — publishing it would defeat
the filtering purpose.

──────────

Section 4 — Provably fair draws

When a draw is created, Atlas seals a secret in a cryptographic
commitment — a hash published to the world before sales open. When
the draw closes, the ticket pool is hashed and published. When it's
time to draw, Atlas uses public entropy — the hash of a specific
Bitcoin block plus a specific drand round — that Atlas cannot control.
The secret is then revealed, the algorithm is run, and the winner is
computed deterministically.

Anyone with the published inputs can rerun the algorithm and reach
the same winner. Every draw has a public proof page with the inputs
and a copy-paste-runnable verifier command.

  ┌─────────────────────────────────────────────┐
  │  ▪                                          │  ← TrustCallout
  │                                             │      display.card
  │  Atlas cannot know the winner before sales  │
  │  close, and cannot bias the result after.   │
  │  The mechanism is verifiable by anyone      │
  │  with the published proof.                  │
  │                                             │
  └─────────────────────────────────────────────┘

See how a specific draw was proved: any draw's proof page shows the
commitment hash, tickets hash, revealed seed, entropy sources, and
verifier command. Example: atlas.ng/proof/{example_draw_id} →

──────────

Section 5 — What Atlas does with your money

Paying entrants pay Atlas for their entry. That money goes to Atlas
Africa Ltd as revenue. Atlas uses the revenue to run the draws, pay
the prizes to winners, and operate the business (staff, technology,
compliance, customer support). Atlas is a for-profit company;
that is not hidden.

The double-entry ledger Atlas uses to track every transaction is
audited, and the reconciliation between Atlas's records and Paystack's
settlement reports runs nightly. Financial records for a draw are
included in the audit trail available to regulators on request via
compliance@atlas.ng.

──────────

Section 6 — What Atlas doesn't do

For clarity — because unclear is worse than uncomfortable:

- Atlas does not know or influence the winner before reveal.
- Atlas does not weight the pool by route (paid vs free).
- Atlas does not sell entrant data to third parties.
- Atlas does not run credit checks or share BVN with third parties
  beyond the KYC vendor for identity verification.
- Atlas does not permit re-registration after self-exclusion (see
  Responsible play →).
```

Then the standard `RELATED` and `ContactLine`.

### 2.2 RELATED cross-links (Part A)

- See the free entry route in detail →
- Responsible play →
- Our terms and privacy notice →

### 2.3 States

**Default (as drawn).** No state variants; this page is static content.

**404 / not found:** the container framework's standard 404. Not specific to this page.

### 2.4 Copy

Copy is above in the layout section. Every string is intended as final draft; Adaeze's review may amend before ship. Notable strings:

- Lede: *Atlas runs prize competitions. Every draw has a free entry route on the same terms as the paid one, a skill question, and a provably fair result. Here is what that means, in plain terms.*
- Section-1 TrustCallout: *Atlas is a prize competition, not a lottery. Two things make the difference: a free entry route on the same terms as the paid route, and a skill question that every entrant must answer.*
- Section-2 TrustSectionCard: *Free-route tickets and paid tickets sit in the same pool. The draw engine picks a winner from the pool without knowing which route any ticket came from. Same odds. Same pool. Same shot.*
- Section-3 TrustSectionCard: *The skill question is the second half of what makes this a prize competition rather than a lottery. Chance alone is not what gets you in.*
- Section-4 TrustCallout: *Atlas cannot know the winner before sales close, and cannot bias the result after. The mechanism is verifiable by anyone with the published proof.*

**Copy commentary:**

- The Section-1 callout is the load-bearing legal-classification claim. Per REVIEW-001 §2.1, this claim was moved from the consumer product surfaces to here — where it lives as a company position on the explanatory page and can be updated by counsel if the phrasing needs to shift. Adaeze will want this sentence particularly.
- Section 5 (*"What Atlas does with your money"*) is unusual on a trust-story page and I want it here specifically. Prize-competition products are frequently viewed with skepticism about where the money goes. Naming that Atlas is for-profit, describing the operational use of revenue, and pointing at the auditable financial trail is a specific trust move — the alternative (silence) is worse.
- Section 6 (*"What Atlas doesn't do"*) is a negative-space section — naming what Atlas explicitly *doesn't* do closes ambiguity that a positive-only description leaves open. Bulleted, blunt, honest.

### 2.5 Accessibility

- Standard landmark structure (`<main>`, `<h1>` for headline, `<h2>` for section headers, `<h3>` inside TrustSectionCard eyebrows).
- All hashes and technical terms rendered in `<code>` where appropriate (algorithm reference, Bitcoin block hash).
- External links to proof example URLs have `aria-label="{destination} — external link"`.
- Callout blocks: `role="region"` + `aria-label="{callout content excerpt}"`.
- Reading order matches visual order.
- Contrast: all tokens as spec.

### 2.6 Interaction

- **In-app back:** returns to prior screen (usually home per wf-02 §2.4).
- **"See the free entry route in detail" link:** navigates to Part B.
- **Proof example link:** navigates to wf-14 for a specific example draw (V0.5 uses the seed draw; V1 picks the most recent revealed draw dynamically).
- **RELATED links:** navigate to Part B, Part C, and T&Cs / Privacy Notice.

---

## 3. Part B — Free-entry-route detail

The page the wireframe 03 §3.6 sheet's *"See full details, form download, and postal address"* link points to. Also public at `atlas.ng/free-entry`.

### 3.1 Layout (per §1 shared structure)

**Eyebrow:** `ATLAS · FREE ENTRY ROUTE`
**Headline:** *The free entry route.*
**Lede:** *Every draw at Atlas offers a way to enter without paying. It's a postal entry: you send a slip to Atlas before the draw closes, we transcribe it into the same pool as paid entries, and it has the same chance of winning. This page has everything you need.*

Content sections:

```
──────────

Section 1 — What you'll need

  ┌─────────────────────────────────────────────┐
  │  ▪ TO ENTER A DRAW FOR FREE                 │  ← TrustSectionCard
  │                                             │      numbered list of items
  │  1. A sheet of paper or the printable       │
  │     entry form (below).                     │
  │                                             │
  │  2. A pen.                                  │
  │                                             │
  │  3. A postage stamp and an envelope.        │
  │                                             │
  │  4. The postal address of the current       │
  │     draw (below — changes per draw).        │
  │                                             │
  └─────────────────────────────────────────────┘

──────────

Section 2 — The steps

1.  Write on your slip:
    - Your full name (as it appears on your Atlas account, or the
      name you'll register with).
    - Your Atlas account email or phone number, so we can match
      your entry to you.
    - The draw you're entering (draw ID or prize description).
    - Your answer to the skill question (below).

2.  Answer the skill question for this draw:

    ┌──────────────────────────────────────────┐
    │  Which of these is the capital of        │  ← question card
    │  Nigeria?                                │      radius.large
    │                                          │      surface.elevated
    │  A · Lagos                               │      hairline border
    │  B · Abuja                               │      body.default
    │  C · Kano                                │
    │  D · Ibadan                              │
    │                                          │
    │  Write the letter of your answer on      │  ← body.small secondary
    │  your slip. Wrong answers void the slip. │
    └──────────────────────────────────────────┘

3.  Post the slip to the address for this draw. The address changes
    per draw — check the address below matches the draw you're
    entering.

──────────

Section 3 — The postal address (current draw)

  ┌─────────────────────────────────────────────┐
  │  ▪ CURRENT ACTIVE DRAW                      │  ← surface.elevated
  │                                             │      radius.large,
  │                                             │      elevation.1
  │  ₦2,000,000 in cash draw                    │  ← body.emphasis
  │  Draw ID  DRAW-2026-07-08-A                 │  ← body.mono 14pt
  │  Closes   12 Jul 2026, 20:00 WAT            │  ← body.default
  │                                             │
  │  ─────────────────────────                  │
  │                                             │
  │  Post your slip to:                         │
  │                                             │
  │  ATLAS DRAW ENTRIES                         │  ← body.emphasis primary
  │  P.O. BOX {number}                          │      formatted as postal address
  │  {area}                                     │      block, monospace-friendly
  │  LAGOS                                      │
  │  NIGERIA                                    │
  │                                             │
  │  ─────────────────────────                  │
  │                                             │
  │  Your slip must be postmarked by            │  ← body.default primary
  │  12 Jul 2026 (the sales-close date).        │
  │  Slips postmarked later are not eligible    │
  │  for this draw; they can enter the next.    │
  │                                             │
  │  [ Copy postal address ]                    │  ← inline button
  └─────────────────────────────────────────────┘

  ⓘ V0.5 note: the P.O. box in the address above is a placeholder.  ← WarningNote
    The real address is procured before real-user launch, per         color.state.attention
    docs/compliance/reviews/REVIEW-001 §6.1 (R-FREE-01).               visible only in V0.5

──────────

Section 4 — The printable entry form

You can download a pre-formatted entry form if you'd rather not
write on plain paper. The form has all the fields laid out and
comes as a PDF.

  [ Download the free-entry form (PDF) ]  ← primary button, secondary variant

The form contains the same fields you'd write out by hand. Using it
is optional.

──────────

Section 5 — What happens after you post

1.  Your slip arrives at the P.O. box within a few days of posting.
2.  An Atlas operator reads the slip, matches it to your Atlas
    account (or opens one if you haven't registered), and transcribes
    it as a ticket in the same pool as paid entries.
3.  You'll receive an email confirming the transcription with your
    ticket number. If the skill answer on your slip is wrong, the
    email tells you the slip was voided.
4.  When the draw closes and the reveal runs, you find out if you
    won on the same channel as paying entrants — email + in-app
    notification.

──────────

Section 6 — Rules and limits

- One slip is one entry. Multiple slips in one envelope are
  transcribed as multiple entries.
- Slips postmarked after the draw's close date are not eligible for
  that draw. They can be transcribed against the next open draw
  (Atlas holds them for up to 30 days).
- Wrong skill answer voids the slip. You'll be told; no charge, no
  reissue.
- If we can't match your slip to an Atlas account and you haven't
  registered, we hold the slip in a review queue and try to contact
  you via the details on the slip.
- Slips are not returned. Void slips are kept as records for audit.

──────────

Section 7 — Costs

Postage is your only cost. Atlas does not charge for a free-route
entry. If we ever needed to change that, we'd change the name of
the mechanic — a free-route entry with a charge would not be a
free route.
```

Then the standard `RELATED` and `ContactLine`.

### 3.2 RELATED cross-links (Part B)

- How Atlas works →
- The current active draw →   (or, if no active draw: *"No active draw right now. We'll list one here when the next one opens."*)
- Responsible play →

### 3.3 States

**Default (as drawn), with an active draw:** Section 3 renders with the active draw's postal address, ID, and close date.

**No active draw:** Section 3 replaced by: *"No draw is currently open. When the next draw opens, this page will show the postal address for it. In the meantime, you can register on Atlas so we can email you when it opens."* with a register link.

**Post-launch, real P.O. box:** the V0.5 WarningNote (§Section 3) is removed. This is a **hard removal at real-user launch** — the note existing after go-live would signal to a regulator that Atlas launched with unresolved free-route infrastructure.

**Print/PDF form download** — the *[ Download the free-entry form (PDF) ]* button triggers a PDF download.

### 3.4 Copy

All above. Notable strings:

- Lede: *Every draw at Atlas offers a way to enter without paying. It's a postal entry: you send a slip to Atlas before the draw closes, we transcribe it into the same pool as paid entries, and it has the same chance of winning. This page has everything you need.*
- Section 6 rule on postage: *One slip is one entry. Multiple slips in one envelope are transcribed as multiple entries.* — a specific promise that closes an operational ambiguity.
- Section 7: *Postage is your only cost. Atlas does not charge for a free-route entry. If we ever needed to change that, we'd change the name of the mechanic — a free-route entry with a charge would not be a free route.*

**Copy commentary:**

- Section 7 (*"Costs"*) exists because *"free entry route"* is a phrase that invites the reader to ask *"but there's a catch, right?"* — the section names the only cost (postage, which Atlas can't waive) and pre-commits Atlas to a change-if-we-change-terms policy. Reads as respect for the reader's skepticism.
- The current-active-draw block (§Section 3) is dynamic — the address, draw ID, and close date update per draw. This is deliberate: printing a permanent address on a static page invites confusion if we ever change P.O. boxes; keying the address to the current draw is honest.
- The **V0.5 WarningNote** on Section 3 is a structural embodiment of R-FREE-01. It makes the placeholder-address risk visible on the surface itself; anyone reading this page in a V0.5 build knows they're looking at a placeholder. **This note must be removed as part of the real-launch checklist** — its persistence into real launch would itself be a compliance incident.

### 3.5 Accessibility

- Postal address block: `role="region" aria-label="Postal address for the current active draw"`. Address is rendered as a `<pre>` for correct visual formatting; the whole address is also inside a `<address>` HTML element for semantics.
- Copy address button: `aria-label="Copy the postal address to clipboard"`. On tap: toast *"Postal address copied."*
- Question card: `role="region" aria-label="Skill question for the current draw"`.
- Form download button: `aria-label="Download the printable free entry form as PDF"`.
- Reading order matches visual order.
- The PDF form must itself be accessible — tagged PDF with correct field ordering, form fields have labels. Amelia/Tobi joint concern; not designed here.

### 3.6 Interaction

- **Copy postal address:** copies the full address block to clipboard.
- **Download form (PDF):** triggers browser download.
- **RELATED links:** navigate to their targets.

---

## 4. Part C — Responsible play

The self-exclusion + duty-of-care surface. Linked from wf-02 §2.4 home ("Responsible play →") and from wf-01 §2.4 registration (via the T&C sheet, once Adaeze lands the T&C copy). Also public at `atlas.ng/responsible-play`.

### 4.1 Layout (per §1 shared structure)

**Eyebrow:** `ATLAS · RESPONSIBLE PLAY`
**Headline:** *Responsible play.*
**Lede:** *Prize competitions are entertainment. If Atlas ever stops being that for you, here is what to do — and here is what Atlas commits to whether or not you ask.*

Content sections:

```
──────────

Section 1 — The commitment

  ┌─────────────────────────────────────────────┐
  │  ▪                                          │  ← TrustCallout, gold left border
  │                                             │      display.card
  │  You can permanently close your Atlas       │
  │  account at any time. Once closed, you      │
  │  cannot re-register.                        │
  │                                             │
  └─────────────────────────────────────────────┘

This is called self-exclusion. It is a hard, permanent boundary.
Atlas offers no reversal — no cool-off window, no re-open flow.
This is a deliberate choice, made because the responsible-gaming
research suggests that reversible self-exclusion is often worse
than no self-exclusion at all.

──────────

Section 2 — How self-exclusion works at Atlas

  ┌─────────────────────────────────────────────┐
  │  ▪ THE MECHANIC                             │  ← TrustSectionCard
  │                                             │
  │  1. You tap "Close my account" in Settings, │
  │     type EXCLUDE to confirm, and complete   │
  │     a second-factor challenge.              │
  │                                             │
  │  2. Your Atlas account closes immediately.  │
  │     Active sessions end. Any pending        │
  │     tickets are refunded. Your wallet       │
  │     balance is refunded to the payment      │
  │     method you originally used.             │
  │                                             │
  │  3. Your identity — specifically, your BVN  │
  │     — is added to our self-exclusion        │
  │     register. Any future attempt to         │
  │     register a new account using the same   │
  │     BVN will not be able to enter draws.    │
  │                                             │
  │  4. If we ever contact you again (support   │
  │     follow-up, refund reconciliation), we   │
  │     do so respectfully and only about       │
  │     resolving the closure.                  │
  │                                             │
  └─────────────────────────────────────────────┘

──────────

Section 3 — Before you self-exclude

If you're deciding whether Atlas is still entertainment for you,
there are a few softer steps you can take first:

- **Reduce your entry frequency.** Atlas will not stop you entering
  a draw; you can stop yourself. If you're entering every draw
  without deciding to, that's information worth noticing.

- **Set a monthly limit for yourself.** V1 will add a spending cap
  feature to help. Until then, an entry log is on your account:
  see your last-3-months entries under Settings → My activity.

- **Talk to someone.** Talking helps. If you'd rather talk to a
  professional than to friends or family, contact {national helpline}.

Any of these is a legitimate alternative to self-exclusion. Self-
exclusion is the hardest option, and it is right for some people;
it is not the first thing to try if you're not sure.

──────────

Section 4 — How to self-exclude

To close your account permanently, tap Settings → Account → Close
my account. You'll be asked to:

1. Type EXCLUDE to confirm you intend to close.
2. Complete a second-factor challenge (a code sent to your phone).
3. Confirm one last time that you understand the closure is
   permanent.

The closure completes immediately once you confirm.

  ┌─────────────────────────────────────────────┐
  │  [ Go to Settings → Close my account ]      │  ← button, secondary variant
  │                                             │      opens the settings screen
  │                                             │      (only visible when signed in;
  │                                             │      on public web version, this
  │                                             │      is replaced by "Sign in to
  │                                             │      close your account")
  └─────────────────────────────────────────────┘

──────────

Section 5 — If someone you know is affected

If someone you know is showing signs that a prize-competition
product isn't entertainment for them anymore, the same softer
options above apply — and the same support resources.

If they've asked you for help and can't or won't self-exclude
themselves, contact us at compliance@atlas.ng. We take third-party
concern seriously and will consider a case-by-case restriction
subject to verification.

──────────

Section 6 — What Atlas does independent of any request

  ┌─────────────────────────────────────────────┐
  │  ▪ ATLAS'S SIDE                             │  ← TrustSectionCard
  │                                             │
  │  Atlas does not:                            │
  │                                             │
  │  · Send promotional messages ("draw closing │
  │    soon", "new draw open") to anyone who    │
  │    hasn't opted in.                         │
  │                                             │
  │  · Offer bonuses, free entries, or credit   │
  │    to entrants (Kobo-neutral incentives     │
  │    are a competition-adjacent design that   │
  │    Atlas has chosen not to build).          │
  │                                             │
  │  · Use urgency copy ("hurry", "last chance")│
  │    anywhere in the product.                 │
  │                                             │
  │  · Auto-enter anyone into anything without  │
  │    explicit action.                         │
  │                                             │
  │  · Withhold refunds or dispute a self-      │
  │    exclusion request.                       │
  │                                             │
  └─────────────────────────────────────────────┘

──────────

Section 7 — Age

Atlas is for adults. You must be 18 or over to hold an Atlas account
or enter any Atlas draw. Under-18 registration attempts are blocked
at sign-up; under-18 discovered later (e.g. at winner-claim time)
result in the account being closed and any funds returned.
```

Then the standard `RELATED` and `ContactLine`.

### 4.2 RELATED cross-links (Part C)

- How Atlas works →
- The free entry route →
- Our terms and privacy notice →

### 4.3 States

**Signed in:** Section 4 shows the `[ Go to Settings → Close my account ]` button that deep-links into the app's Settings screen.

**Not signed in (public web view):** button replaced with *"Sign in to close your account →"*.

**Already self-excluded (edge case):** if the reader is signed in and their account is somehow surfacing this page (rare — self-exclusion closes the account), the page shows: *"Your account is closed as of {date}. See our restoration policy below or contact us at compliance@atlas.ng."* — with contact routes.

### 4.4 Copy

All above. Notable strings and reasoning:

- **Section 1 TrustCallout:** *You can permanently close your Atlas account at any time. Once closed, you cannot re-register.* — the single most important sentence on the page, callout-weight. Legal and operational commitment in one.
- **Section 3 (*"Before you self-exclude"*)** — this section is the responsible-play stance made real. It could easily be omitted (a lot of gambling-industry pages jump straight to *"here's how to exclude"* without discussing softer alternatives). Including it is a duty-of-care move: not every reader who lands on this page needs the most drastic option; some need to see that Atlas takes the softer paths seriously too. **Adaeze — this section is a design stance; if you'd prefer to point out only self-exclusion (regulatory-minimum posture), that's your call.**
- **Section 5 (*"If someone you know is affected"*)** — the "concerned third party" surface. Names a real support route (compliance@atlas.ng) with a real commitment (case-by-case restriction subject to verification). Adaeze to define the operational process; the design surfaces the promise.
- **Section 6 (*"What Atlas does independent of any request"*)** — a negative-space section like §2.6 of Part A. Names five things Atlas *doesn't* do that other prize/gambling products often do. Bulleted, blunt.
- **Section 7 (*"Age"*)** — brief, per REVIEW-001 §5.1. The 18+ gate is enforced at wf-01 registration; this section documents the commitment on a page where readers might look.

### 4.5 Accessibility

- **Callouts and section cards:** `role="region"` with appropriate labels.
- **Bulleted lists in sections:** proper `<ul>` semantics.
- **Support contact addresses:** `<a href="mailto:...">` with `aria-label` describing the destination.
- **The "Close my account" button** is prominent and reachable via keyboard; on activation deep-links into the app or prompts sign-in on web.
- **Reading order matches visual order.**
- **National helpline placeholder** — must be a real number before real launch. If placeholder shows in V0.5 demo, is fine; the section text explicitly says *"contact {national helpline}"* — Adaeze to fill.

### 4.6 Interaction

- **Close-my-account button:** in-app opens Settings → Close my account (deep link). On public web with an unauthenticated visitor, opens the sign-in page with a return-URL pointing at Settings.
- **RELATED links:** navigate to their targets.
- **Support contact links:** open mail client (V0.5) or WhatsApp Business channel (V1).

---

## 5. Design invariants across all three pages

Recording so nothing drifts as the pages get re-read, translated (V1+), or expanded:

1. **The shared visual language (§1.1) is used identically across all three pages.** Same header, same callout treatment, same section-card treatment, same RELATED row, same ContactLine.
2. **The classification claim (*"prize competition, not a lottery"*) lives on Part A §Section 1 TrustCallout — and nowhere else on the product surfaces.** Per REVIEW-001 §2.1.
3. **Every operational commitment made in copy is a real commitment enforced elsewhere** — postal address is a real address (post-launch); self-exclusion is real per ADR-010; skill question is real per wf-04 §2.
4. **The V0.5 placeholder-address WarningNote on Part B §Section 3 must be removed at real-user launch.** Its persistence into launch is itself a compliance incident.
5. **Every page has exactly one primary TrustCallout** (gold-left-bordered display.card block). Two or more start to feel like an ad campaign; the callout is a single moment of emphasis per page.
6. **Every page ends with the same RelatedLinksRow structure (three links) and the same ContactLine.** Consistency across pages tells the reader they're in a coherent explanatory surface.
7. **These pages are what Atlas gives to counsel, regulators, and journalists as a first read.** Copy should always survive being read as such.
8. **No page has a marketing CTA** ("Enter now", "Try Atlas") in its body. The RELATED row is the only navigation forward, and it navigates to *other explanatory pages* — not to product surfaces. (One exception: Part B *"The current active draw"* RELATED link, which is directly useful to a free-route-curious reader.)

---

## 6. Open questions

### For ⚖️ Adaeze — hard-blocking review since these pages are your compliance-copy home:

1. **Part A §Section 1 TrustCallout** (the *"prize competition, not a lottery"* claim). This is where REVIEW-001 §2.1 relocated the classification claim. Confirm the wording, and confirm this is the right (and only) surface for it.
2. **Part A §Section 5 (*"What Atlas does with your money"*).** Naming the for-profit posture is a trust move; confirm the wording is legally-safe (no accidental misrepresentation of financial structure).
3. **Part B §Section 3 WarningNote** — V0.5 placeholder address disclosure. Wording appropriate? Should it be more emphatic?
4. **Part B §Section 6** — rules and limits. Are these the correct operational rules (30-day carry, one-slip-one-entry, wrong-answer voids, non-return of slips)?
5. **Part C §Section 3 (*"Before you self-exclude"*).** Is this the right stance? A regulatory-minimum posture would jump to *"here's how to exclude"*; this page offers softer alternatives first. Design choice with a compliance flavour — your call.
6. **Part C §Section 5 (*"If someone you know is affected"*).** Confirm compliance@atlas.ng is the right route and that "case-by-case restriction subject to verification" is a commitment Atlas can operationally honour.
7. **Part C §Section 6 (*"What Atlas does independent of any request"*).** The five items listed are commitments Atlas makes on its own. Missing anything?
8. **National helpline placeholder in Part C §3 and §5.** What is the right Nigerian resource, or is the correct answer a general mental-health line pending a mature GAMSTOP-equivalent? Same question you flagged for wf-07 §5.6.d (rejected-claim self-exclusion state).
9. **Cross-references to T&Cs and Privacy Notice.** RELATED rows on Parts A and C point at *"Our terms and privacy notice →"* — those are your copy artefacts. When they land, is a single combined page appropriate or should they be separate targets?
10. **Translation.** Multi-language is V1+; do Igbo / Yoruba / Hausa versions of Part C (responsible play) carry a higher-priority for V1 due to duty-of-care reach? Your call.

### For founder:

11. **Voice + length.** These pages are longer than any other consumer surface. Is that the right trade? (I believe yes; the reader has arrived to read.)
12. **Contact address: hello@atlas.ng vs compliance@atlas.ng vs support@atlas.ng.** Copy currently uses `hello@` for general contact and `compliance@` for regulator/duty-of-care contact. Confirm the mailbox scheme.
13. **Voice on Part C.** Duty-of-care copy is delicate; the current voice is respectful, calm, non-patronising. If it lands as too-cold-clinical, we can warm the phrasing without softening the commitments. Watch reaction on read-through.
14. **Public web mirror.** All three pages have both an in-app version (Flutter) and a public web version (Next.js). Same content, adapted layout. Confirm the public web mirror is in V0.5 scope, or is it V1 (V0.5 = in-app only)?

### For 💻 Amelia:

15. **Deep-link scheme** for `[ Go to Settings → Close my account ]` on Part C. In-app deep link works; public web version needs to route to sign-in-then-settings.
16. **PDF form download on Part B.** Static asset served from S3 or generated on the fly per draw? V0.5 recommendation: static PDF (single canonical form; slips are transcribed manually and don't require per-draw form fields).
17. **Current-active-draw block on Part B §Section 3.** Rendered from live data; if no active draw, alternate copy. Confirm the fetch pattern (server-render vs client-hydrate).

### For 🛡️ Tobi:

18. **Public web version delivery.** These pages are indexable content — SEO matters (a regulator or journalist Googling "Atlas free entry route" should find Part B). Same Next.js infra as the proof page (wf-14). Cache aggressively; revalidate when draw parameters change.
19. **PDF form asset hosting.** S3 bucket with signed URLs? Direct public URL? Not sensitive data — recommend direct.

---

## 7. Cross-references

- Flow source: `v0.5-demo-plan.md §2` (steps 15, 16) + wf-03 §3 (which links to Part B).
- Consumer surface entry points: `02-browse-active-draw.md §2.4` (home surface link row).
- Adjacent trust-story surface: `14-public-proof-page.md` — every reference on these pages to *"proof"* or *"verify"* links there.
- ADR-006 §Draw mechanic (referenced in Part A §Section 4).
- ADR-010 §Self-exclusion (Part C §Section 2 is the consumer-facing expression of ADR-010).
- Compliance review: `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md` — this wireframe answers §2.1 (classification-claim relocation), §6.1 (R-FREE-01 postal address), §5.1 (age gate documentation), §5.6.d (self-exclusion / helpline reference).
- Future copy artefacts (owned by Adaeze): `docs/compliance/copy/t-and-c.md`, `docs/compliance/copy/privacy-notice.md`.
- Tone: `tone-doc.md §5` (copy voice), `tone-doc.md §6` (what Atlas is NOT — Part C §Section 6 negative-space mirrors this).
- Tokens: `tokens.md` — shared components use existing tokens; TrustCallout adds one bounded exception (4pt solid gold left border) which fits within the existing radius/elevation/spacing system.

---

🎨 *End of wireframe 15. Day 12 complete.*

*Three trust-story pages drafted. This is Atlas's explanatory surface — where the legal classification claim, the free-route operational detail, and the responsible-play commitment live in coherent, cross-referenceable form. Adaeze's authoritative copy artefacts (T&Cs, Privacy Notice at docs/compliance/copy/) will slot into the RELATED links across all three pages when she lands them.*

*Day 13 tomorrow — design system consolidation. All 15 components documented as specs (props, states, accessibility notes). Then Day 14 exit gate + Amelia handoff.*
