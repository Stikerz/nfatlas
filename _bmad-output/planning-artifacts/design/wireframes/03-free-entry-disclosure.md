# Wireframe 03 — Free-Entry Disclosure (on draw detail + explainer sheet)

**Drafted:** 2026-07-08 (Day 4 per `tone-doc.md §8`)
**Amended:** 2026-07-08 (Day 7 per `tone-doc.md §8`) — sheet lede rewritten to drop the first-person legal-classification claim (§3.4); post-reveal winning-route disclosure removed from the on-page element (§2.3). Both changes per `docs/compliance/reviews/REVIEW-001` §2.1 and §2.3 (Adaeze). Entry-count paid/free split retained on all surfaces.
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** Draft — Adaeze approved with conditions on 2026-07-08 (REVIEW-001). Founder review pending at Week 1 exit gate.
**Covers:** Flagship flow step 3 from `v0.5-demo-plan.md §2` — *"Free-entry disclosure — draw page shows the free-route mechanic prominently."*
**Surface:** Flutter consumer app — the disclosure element embedded on the draw detail page, plus its tap-through explainer sheet.
**Pairs with:** `02-browse-active-draw.md` (host page), `tokens.md`, `tone-doc.md`, `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md`, and (later) the full free-entry-route detail page produced Day 12 which this sheet links to.

---

## 0. Why this element deserves its own wireframe

The free-entry route is the load-bearing element of Atlas's prize-competition legal framing. Under Nigerian prize-competition mechanics (per `_bmad-output/planning-artifacts/research/domain-nigerian-prize-competition-licensing-research-2026-06-30.md`), the free route is not a marketing add-on — it is what makes Atlas *not a lottery*. If the disclosure is inadequate, the entire product's legal posture is at risk. If the disclosure is overweighted (loud, promotional, plastered as a banner), it undermines the premium tone the product depends on to convert.

The design goal is therefore narrow and specific:

> The free route must be **impossible to miss** on the draw detail page, without being **loud**. It must feel like the product itself, not a compliance bolt-on.

Splitting this into its own wireframe file makes the specific element reviewable in isolation — Adaeze can sign off on it, the founder can push back on tone, without either of them re-reading the whole draw-detail page.

**Non-goals:**
- The full free-entry-route explanation page (postal address, form download, deadline mechanics, transcription flow). That is a Day 12 trust-story page and is out of scope here.
- Copy for the paper entry form itself. Legal review artefact; not designed by Sally.

---

## 1. The two surfaces this covers

```
┌──────────────────────────┐         ┌──────────────────────────┐
│  Draw detail (screen 2.2)│         │  Explainer sheet (2.3)   │
│                          │         │  bottom-sheet, ~65% viewport
│  ┌────────────────────┐  │         │  ┌────────────────────┐  │
│  │ FreeEntryDisclosure│──────tap──▶│                        │  │
│  │ (inline element,   │  │         │  short summary +       │  │
│  │  ~180pt tall)      │  │         │  "See full details →"  │  │
│  └────────────────────┘  │         │  link to Day 12 page   │  │
│                          │         │                        │  │
└──────────────────────────┘         └──────────────────────────┘
```

Two levels of information:

1. **The disclosure element on the draw page** — short, always visible, factual. Present on every draw, every state.
2. **The bottom sheet** — one tap away — short summary of the mechanic in 3-4 bullets, with a link to the full Day-12 detail page for anyone who wants everything.

Progressive disclosure done properly: enough on the primary surface to satisfy the compliance intent and the tone-carrying trust story; more available on demand without cluttering.

---

## 2. The disclosure element (on screen 2.2)

### 2.1 Position on the host page

Placed between the meta rows (close time / entry count / commitment hash) and the "About this draw" section. Rationale:

- Not first — the prize is first, the trust story (numbers + hash) is second, the free route is third. This ordering says: *the mechanic is present, prominent, and part of the story — not the story itself*.
- Not last — placing it last would let scroll-averse users miss it. This is not acceptable given the legal load-bearing nature.
- Between the trust-hash region and the "About" boilerplate is the correct altitude: still above the fold on most devices for the primary interaction (Enter button is sticky, so above-fold isn't about that; it's about eyeball path when the page is read top-down).

### 2.2 Layout

```
┌───────────────────────────────────────┐
│  ▪  Free entry route                  │  ← 16pt gold square bullet
│                                       │      + label.micro uppercase gold
│                                       │  space.300
│                                       │
│  Prefer not to pay?                   │  ← body.default, primary
│  Every draw offers a free postal      │
│  entry. Same odds, same pool,         │
│  same shot.                           │
│                                       │
│                                       │  space.400
│                                       │
│  How the free route works  →          │  ← inline link, navy underline,
│                                       │      body.default weight 500
└───────────────────────────────────────┘
  Container: radius.large, surface.elevated,
  1pt divider.hairline border, elevation.0,
  16pt internal padding on all sides.
```

**Why this treatment, specifically:**

- **Not a banner.** A yellow strip across the page reads promotional / "hurry" — the exact tone we've committed against. This is a card among cards.
- **Not a modal on landing.** A modal on the draw page reads as an interruption. Our user is here to look at the prize, not to first accept a compliance disclaimer.
- **Not below-the-fold.** Placed above "About this draw" to guarantee it lands in the primary scroll path.
- **Small gold square bullet** — not an exclamation mark, not a warning triangle. The gold marks it as *belonging to the trust story* (same palette family as the champagne accent, same posture as the section eyebrow above). It says *"this is a considered part of the product,"* not *"this is a warning."*
- **Copy directly from tone-doc.md §5** — no rewrite. *"Prefer not to pay? Every draw offers a free postal entry. Same odds, same pool, same shot."* This is the sentence I want carved on the product.
- **Ends in a link, not a button.** The tap-through is an inline navy link. Buttons are for commitments (Enter, Create account); links are for reading further. This element asks the user to *know*, not to *commit*.

### 2.3 States on the host page

**Draw open (default).** As drawn.

**Approaching close (< 4h remain):** no change in this element. The disclosure doesn't participate in urgency — the free route is available *equally* right up to close time (per prize-comp mechanics — Adaeze to confirm).

**Draw closed (post 8pm Saturday):** copy switches to:
> ▪ Free entry route
>
> Sales closed. The free route accepted 87 entries this draw.
>
> How the free route works →

The link still works; the sheet still explains the mechanic — helpful for people who arrive after close and want to understand what they missed.

**Draw revealed (post 9pm Sunday):** copy:
> ▪ Free entry route
>
> The winning ticket has been drawn. Every entry — paid or free — had the same chance.
>
> See the proof →

**Amendment 2026-07-08 per REVIEW-001 §2.3.** The original draft proposed a per-draw *"winning ticket came from the paid/free route"* disclosure. Adaeze held this decision for V1 pending counsel — adverse-selection appearance risk on small samples and winner-identifiability risk in small free-route pools were the reasons. The entry-count split (`1,160 paid · 87 via free route`) is retained on the draw card (wf-02 §2.4) and on the reveal page (wf-06 §3.5, post-amendment); only the *"which route won this specific draw"* line is removed.

### 2.4 Copy (default state)

| Element | Copy |
|---|---|
| Label | Free entry route |
| Body | Prefer not to pay? Every draw offers a free postal entry. Same odds, same pool, same shot. |
| Link | How the free route works → |
| Body (closed) | Sales closed. The free route accepted {n} entries this draw. |
| Body (revealed) | The winning ticket has been drawn. Every entry — paid or free — had the same chance. |
| Link (revealed) | See the proof → |

### 2.5 Accessibility (host-page element)

- **Semantics:** the block is a `section` with `aria-labelledby` pointing at "Free entry route" (rendered as an `h3`). Body copy is a normal paragraph; link is a normal link with `→` reading as the word *"opens details"* (arrow character hidden from AT via `aria-hidden`, replaced by accessible label).
- **Screen-reader read:** *"Free entry route. Prefer not to pay? Every draw offers a free postal entry. Same odds, same pool, same shot. How the free route works, opens details."*
- **Contrast:** gold label is 12pt uppercase, tracking +0.05em (`type.label.micro`), passes AA large text. Body copy `text.primary` on `surface.elevated` = 15.3:1 (AAA). Link `brand.primary` on `surface.elevated` = 14:1 (AAA).
- **Touch target of the link:** the link + its arrow occupy a 44pt tall row (padding above/below the link inside the container makes the whole link row tappable).
- **Reduce motion:** N/A (no motion here).

---

## 3. Sheet 2.3 — "How the free route works"

### 3.1 Layout (bottom sheet, ~65% viewport height)

```
┌─────────────────────────────────────────┐
│                                         │
│         ═════                           │  ← drag handle
│                                         │
│  ▪ Free entry route                     │  ← gold label.micro
│                                         │
│  How it works                           │  ← type.display.card (24pt Fraunces)
│                                         │
│                                         │  space.600
│                                         │
│  Every draw at Atlas offers a free      │  ← body.default
│  postal entry route. It exists for      │
│  a simple reason: entries are earned    │
│  on the same terms whether you pay      │
│  or not. The free route is how that     │
│  promise is kept.                       │
│                                         │
│                                         │  space.600
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  1.  Download the entry form       │ │  ← 3 numbered steps in
│  │      or write your details on any  │ │      a numbered list.
│  │      sheet of paper.               │ │      Each step: bold number,
│  │                                    │ │      body.default text.
│  │  2.  Answer the same skill         │ │
│  │      question that paying entrants │ │
│  │      answer.                       │ │
│  │                                    │ │
│  │  3.  Post it to the address below  │ │
│  │      before the draw closes.       │ │
│  │      We transcribe every valid     │ │
│  │      entry into the same pool.     │ │
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.600
│                                         │
│  ─────────────────────────────          │  ← hairline
│                                         │
│  Same odds. Same pool. Same shot.       │  ← body.default, primary,
│                                         │      centered
│                                         │
│                                         │  space.800
│                                         │
│  See full details, form download,       │  ← inline link, navy
│  and postal address  →                  │      opens Day 12 page
│                                         │
│                                         │  space.600
│                                         │
│  ┌───────────────────────────────────┐ │
│  │            Close                   │ │  ← button, secondary variant
│  └───────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

### 3.2 Components

- `BottomSheet` — Flutter `showModalBottomSheet` with drag handle, `radius.large` top corners, `surface.base` background.
- `SectionLabel` — gold eyebrow.
- `SectionHeadline` — 24pt Fraunces.
- `NumberedList` — new component; each item is `[bold number] [body.default text]`.
- `InlineLink`.
- `Button` — secondary variant.

### 3.3 States

**Default (as drawn).** Only state; sheet is informational.

**Draw closed:** sheet content unchanged — the mechanic explanation is evergreen and useful post-close.

**Loading:** N/A — content is static bundled copy, no fetch.

### 3.4 Copy (final)

| Element | Copy |
|---|---|
| Eyebrow | Free entry route |
| Headline | How it works |
| Lede | Every draw at Atlas offers a free postal entry route. It exists for a simple reason: entries are earned on the same terms whether you pay or not. The free route is how that promise is kept. |
| Step 1 | Download the entry form or write your details on any sheet of paper. |
| Step 2 | Answer the same skill question that paying entrants answer. |
| Step 3 | Post it to the address below before the draw closes. We transcribe every valid entry into the same pool. |
| Reassurance | Same odds. Same pool. Same shot. |
| Deep link | See full details, form download, and postal address → |
| Close CTA | Close |

**Copy commentary:**

- The lede states *"entries are earned on the same terms whether you pay or not"* — a description of the mechanic rather than a legal classification claim. **Amended 2026-07-08 per REVIEW-001 §2.1.** The original draft made a first-person *"prize competition is not a lottery"* legal claim; Adaeze required its removal from consumer copy (the classification claim moves to T&Cs where it belongs) because until Nigerian counsel confirms the NLRC recognises the distinction, Atlas holding itself out as the arbiter of the classification is a category of statement regulators dislike even when they agree with the substance. The revised sentence carries the same operational promise (equal-terms entry) without the legal-classification assertion. Small tone loss; correct trade.
- *"We transcribe every valid entry into the same pool"* is a specific commitment. It means operations have to actually do this every draw. Ownership: 🛡️ Tobi (operator flow, wireframe 06 Day 9). If this promise is written on the consumer surface, the operator flow has to honour it — this is an intentional design-forcing-function.
- *"Same odds. Same pool. Same shot."* — deliberately a rhythmic, memorable line. Compare the "you can't win if you don't play" trope of lottery marketing. Ours is the inverse: a promise of *fairness*, not of *hope*.
- No mention of specific postal address or entry deadline inside the sheet. Those live on the Day 12 full-detail page — because they change per draw and shouldn't be embedded in a static sheet. The sheet establishes the mechanic; the page carries the operational detail.

### 3.5 Accessibility

- **Sheet semantics:** `role="dialog"` `aria-modal="true"` `aria-labelledby="how-it-works-heading"`.
- **Focus trap:** when open, focus is trapped inside the sheet; the drag handle, close button, and inline link are all reachable via tab order (which is: Close X → Numbered list items (as list) → Deep link → Close button).
- **Announcement on open:** *"How the free route works. Every draw at Atlas..."* announced by AT immediately.
- **Dismiss:** close button, tap outside sheet, back gesture, and swipe-down all dismiss. All routes return focus to the disclosure link on the host page.
- **Reduce motion:** sheet appears via fade + minimal upward slide (60pt of translate), not the full sheet-slide-up animation.

### 3.6 Interaction

- **Deep link tap:** navigates *out of* the sheet into the full Day-12 free-entry-route detail page. This means the sheet dismisses first, then navigation happens. This preserves the mental model: sheets are for glances, pages are for reading.
- **Close button:** dismisses sheet. Focus returns to the disclosure link.
- **Swipe-down:** dismisses sheet. Focus returns to the disclosure link.
- **Backgrounding the app while sheet is open:** on resume, sheet is still there — state preserved.

---

## 4. What this element is NOT (design guardrails)

Encoded here because the free-entry element is the single most-likely piece of the product to drift toward "compliance banner ugly" as more voices review it. Preserving these:

- ❌ **Not a banner strip.** A yellow horizontal strip screams "compliance". Ours is a card.
- ❌ **Not a warning triangle icon.** Ours is a gold square bullet.
- ❌ **Not "Free entries available!"** with exclamation. Copy is *"Prefer not to pay?"* — a question posed to the reader.
- ❌ **Not a full-screen interstitial on landing.** Interstitials cost the trust story more than they gain in disclosure.
- ❌ **Not a small footer link only.** A tiny link at page bottom is not "prominent" per plan §2 step 3.
- ❌ **Not in a "Terms & FAQ" accordion.** Accordion = hidden. This element is always open.
- ❌ **Not translated into "Enter for free!"** on any surface. The mechanic is *"same odds, same pool, same shot"*, not "get in without paying". Wording matters — the second frames it as a workaround for the paid route, which subtly implies the paid route is the "real" route. Both routes are the real route.

---

## 5. Open questions for founder + Adaeze review

### For founder:

1. **Winning-route disclosure on the disclosure element (post-reveal state, §2.3).** Publishing *"The winning ticket came from the paid/free route"* is a strong trust-story move. Any objection?
2. **Numbered steps in the sheet vs plain prose.** Numbered steps are clearer; plain prose is calmer. I've gone with numbered. Pushback welcome if this feels too "how-to" for the tone.
3. **Sheet CTA copy — currently just "Close".** Alternative: "Back to the draw". Either is fine. "Close" is more sheet-native.

### For Adaeze (compliance, hard gate) — RESOLVED 2026-07-08 by REVIEW-001

4. **Lede sentence** — resolved §2.1: rewritten to remove first-person legal-classification claim; applied above.
5. **"Same odds, same pool, same shot"** — approved §2.2 as literally true, conditional on operational invariants (Amelia + Winston own the invariants in ticket module + ADR-006).
6. **Winning-route disclosure** — held for V1 pending counsel §2.3; per-draw route disclosure removed from post-reveal state. Entry-count split retained.
7. **Prominence + placement** — approved §2.4. Placement between hash-row and About holds. Counsel may raise the bar later.
8. **Main disclosure element copy** — approved as written §2.5.

Additionally, Adaeze flagged in REVIEW-001 §6.1 that the postal address referenced in this wireframe **does not currently exist as a leased P.O. box**. For V0.5 demo this sheet renders a placeholder; for real-user launch the P.O. box must be leased and the transcription capability must be a real operational function with a named responsible person. Tracked as R-FREE-01.

---

## 6. Cross-references

- Host wireframe: `02-browse-active-draw.md` §3 (draw detail page).
- Full free-entry-route page (Day 12, not yet drafted): will live at `wireframes/15-free-entry-route-page.md`.
- Operator flow (Day 9, not yet drafted): `wireframes/10-transcribe-free-entry.md` — the operator side of the "we transcribe every valid entry" promise.
- Compliance ownership: ⚖️ Adaeze per `docs/AINE-AGENTS.md`.
- Research source: `_bmad-output/planning-artifacts/research/domain-nigerian-prize-competition-licensing-research-2026-06-30.md`.
- Tokens: `tokens.md`.
- Tone: `tone-doc.md` §5 (copy voice) — the free-entry sentence appears there as an approved sample.

---

🎨 *End of wireframe 03. This is the single most compliance-load-bearing piece of consumer UI in V0.5. It ships when Adaeze signs off on the copy, not before. Day 5 (skill question + payment + ticket appears) next.*
