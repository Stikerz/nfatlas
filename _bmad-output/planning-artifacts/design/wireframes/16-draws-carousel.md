# Wireframe 16 — Draws Carousel (browse concurrent draws)

**Drafted:** 2026-11-27
**Drafted by:** 🎨 Sally (bmad-agent-ux-designer)
**Covers:** The Draws tab when more than one draw is `sales_open`. Implemented ahead of this wireframe in PR #20 — this document reviews what shipped and records the design intent it should have been built from.
**Surface:** Flutter consumer app, tab index 1.
**Pairs with:** `tone-doc.md` (Anchor 1, §Palette), `02-browse-active-draw.md` (the draw detail this navigates into), `tokens.md`.

---

## 0. Verdict

**Approved to merge, with two changes required (§3) and two product decisions raised (§4).**

The interaction is sound and the accessibility work is better than most carousels ship with. My reservations are about *register* — whether this surface feels like Atlas or like a storefront — and they are fixable in copy and tokens, not in architecture.

---

## 1. The thing that gave me pause

`tone-doc.md` Anchor 1 names the pattern this resembles, and rejects it:

> What Atlas does *not* take from BOTB: **the busy comparison-shopping bar of alternative prizes**, the discount countdowns, the "94% sold!" urgency copy. Atlas is not e-commerce; Atlas is more considered.

A horizontally swipeable row of alternative prizes is, structurally, that bar.

**I am approving it anyway, and the distinction matters enough to write down:** BOTB's comparison bar sits *on the draw page*, beside the prize you came to see. It exists to make you reconsider, to keep you shopping at the moment you were about to commit. That is the bit Atlas rejects — not the existence of more than one prize, but the act of waving alternatives at someone mid-decision.

This carousel lives on a **dedicated browse tab**. A user who opens "Draws" has asked to see what is available. Answering that question is service, not upsell.

**The boundary, and it is a hard one:** this pattern must never appear on the draw detail page or in the entry flow. If a future ticket proposes "related draws" under the entry CTA, or a prize-switcher on the purchase screen, that is the BOTB bar and it is out. Cite this paragraph.

---

## 2. What is right, and worth keeping

- **The peek.** `viewportFraction: 0.88` leaving the next card visible at the edge is the single thing that makes a carousel discoverable. Without it users do not swipe because nothing suggests there is anywhere to go. Correct instinct, correctly executed.
- **The dots are controls.** 44pt targets, real `onTap`, `Semantics` labels. Most carousels ship decorative dots and quietly lock out anyone who cannot drag horizontally — motor-impairment, switch control, or simply a user holding a phone one-handed on a bus. This did not do that, and a test enforces it.
- **Position is announced.** `"Draw 1 of 3"` per page. A bare `PageView` tells a screen-reader user nothing about there being more; silence reads as "this is all there is".
- **Single-draw state degrades properly.** Indicator and count hidden. Dots that cannot move are noise, and the restraint here is the right default.

---

## 3. Changes required before merge

### 3.1 "3 draws open" — wrong register, and redundant

Quantity-as-signal is the register the tone doc rejects. It is not "94% sold!", but it is the same family: a number whose job is to imply there is lots on offer. Atlas does not do inventory language.

It is also **redundant** — the dots already say "three", and the `Semantics` labels already say "of 3" for assistive tech. The visible count earns nothing.

**Change:** remove it. If a label is wanted in that slot later, it should name the *organising principle*, not the quantity — e.g. "Closing soonest first", which tells the user something the dots cannot.

### 3.2 `primary` now means two different things

`_DrawCard(primary: true)` carries a 2px navy border and a larger display face. On Home it means **"this is the featured draw"**. In the carousel it means **"this is the page you are on"**.

Same visual, two meanings, two screens. A user who learns "bordered = the big one" on Home will misread the carousel.

**Change:** the carousel should not reuse `primary`. The active page is already indicated by being centred, by the dot, and by the neighbours being cropped — it does not need a border too. Pass `primary: false` for all carousel pages and let position do the work.

### 3.3 Consequence of 3.2, stated honestly

Dropping the `primary` treatment shrinks the display face, so the card now
occupies roughly a third of the viewport and leaves a large empty region
beneath it. I regenerated the golden and looked: it reads sparse rather
than restrained.

I am not reversing §3.2 for it — one visual meaning two things across two
screens is the worse problem, and padding a card to fill space is not a
reason to keep a misleading token. But the sparseness is **real, visible
today, and resolves the moment §4.1 lands**: prize photography is exactly
what belongs in that region. Until then the Draws tab is honest but plain.

If §4.1 is deferred beyond the next sprint, revisit this with a taller
card treatment rather than restoring the border.

---

## 4. Product decisions raised, not design defects

### 4.1 There is no prize photography — and the carousel makes that worse

`tone-doc.md` Anchor 1 is unambiguous: **"prize photography dominates the fold"**. `DrawSummary` carries no image field at all. The card is prize *copy* in a serif face, a price, a countdown and a commitment hash.

On a single featured draw, text-only reads as restrained. **In a carousel it reads as a spreadsheet.** Swiping between three visually near-identical text cards gives almost no sense of moving between distinct, desirable things — which is the entire emotional job of this surface. The golden shows it plainly.

This is pre-existing and out of scope for PR #20, but it is now the **largest gap between the tone doc and what ships**. It needs a `prize_image_url` on the draw, an operator upload flow, and a hero treatment on the card. That is a Winston + John conversation, not a tweak.

### 4.2 "closed" and "TAP TO ENTER" together

Flagged by Amelia; I confirm it and it is genuinely confusing, not merely untidy. A user reading "closed" and seeing an enter affordance will conclude the app is broken — and the one who taps anyway and *succeeds* trusts us slightly less afterwards.

The cause is that the label derives from `close_time` while the affordance derives from `state`. The window between them is real: the operator closes the draw manually.

**My recommendation, for the founder to decide:** during that window show **"closing now"** rather than "closed", and keep the CTA. It is accurate — the draw is accepting entries and about to stop — and it does not promise something the backend will refuse. Saying "closed" while accepting entries is the worse of the two inconsistencies.

---

## 5. Not required, noted for later

- **Swipe does not loop.** Correct for now. Looping carousels disorient and hide the end of the set.
- **No auto-advance.** Correct, and please keep it. Auto-advancing carousels are the single most complained-about pattern in consumer apps and would read as the "urgency" the tone doc bans.
- **Order is `close_time` ascending**, so urgency drives position without any urgency *copy*. That is a genuinely elegant solve and I would like it preserved — §3.1's suggested label exists to make it legible.

---

🎨 *Design intent for a surface that shipped before it was specified. §3 before merge; §4 to the founder.*
