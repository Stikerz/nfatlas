# Project Atlas — Tone & Design Direction

**Drafted:** 2026-07-02
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** **Approved by founder 2026-07-08** — as-is, no amendments. Sally cleared to advance to design tokens (Day 1 evening / Day 2) and consumer wireframe 1 (Day 3).
**Applies to:** V0.5 investor demo (Phase 2, weeks 1–2 design pass). Extends into V1 unless deliberately reset.
**Pairs with:** `_bmad-output/planning-artifacts/v0.5-demo-plan.md`

---

## 0. Who this is for

Before any pixel: the person at the other end.

She is 32. She lives in Yaba, works in Ikeja, and the commute costs her three hours a day and half of her patience. She has a Guaranty Trust account and a Kuda account and knows the difference between them. She has, at some point in the past year, sent money to a "giveaway" account on WhatsApp and felt stupid about it for two weeks. She is not credulous. She is not desperate. She is *cautiously optimistic under pressure* — which is what most Nigerian professionals in their thirties are, most days.

When she opens Atlas the first time, she is not asking *"how do I win?"* She is asking *"how do I know this is real?"*

**Every design decision in this document serves that question.**

If a design choice makes her feel *this is polished, this is real, this is not going to embarrass me if I tell my sister I entered* — it is right. If it makes her feel *this is a game show, this is desperate, this is asking for too much of my trust* — it is wrong. Whenever a tradeoff arises during the build, that's the test.

---

## 1. Positioning

**One sentence:**

Atlas is where aspiration meets integrity — the premium prize competition that treats trust as a first-class deliverable.

**Three positioning axes:**

- **Aspiration.** The prize is the hero. The interface makes room for it. Photography is rich, generous, warm. Prize amounts are set in a typeface that carries weight. When Atlas shows you what you could win, it does not shout — it *presents*.
- **Integrity.** The trust story is not a bolt-on. Every screen that involves money, entry, or draw outcome earns its trust through *visible mechanism* — receipts, timestamps, commit hashes, verification badges, proof pages. The trust story has as much design love as the aspiration story.
- **Restraint.** Atlas does not celebrate itself. Atlas celebrates the winner. The brand does not feature heavily on the winner's moment — the winner's face does, the winner's story does. This is a service, not a personality.

**What that produces in practice:**

- Draw pages look more like Watches of Switzerland product pages than like a lottery website.
- Winner claim pages feel closer to a Bentley delivery experience than a Publishers Clearing House cheque handover.
- Audit / proof pages feel closer to Coinbase's blockchain confirmation UI than to a compliance disclaimer footer.
- Loading states, error states, empty states are as considered as the happy path. (Most prize platforms fail here. That failure is our differentiator.)

---

## 2. Visual anchors (5 references)

Real products Atlas should sit adjacent to. Each anchor names the *specific thing* Atlas learns from it — not "everything about it."

### Anchor 1 — BOTB (Best of the Best) — `botb.com`
*The prize-first hero treatment on draw pages.*

BOTB's core competence is making the car the emotional centre of the page. Full-bleed photography, restrained supporting UI, entry mechanic tucked into the corner because it doesn't need to shout. Atlas draw pages inherit this structural discipline: **prize photography dominates the fold; entry mechanic is a confident secondary presence, never a scream.**

What Atlas does *not* take from BOTB: the busy comparison-shopping bar of alternative prizes, the discount countdowns, the "94% sold!" urgency copy. Atlas is not e-commerce; Atlas is more considered.

### Anchor 2 — Watches of Switzerland — `watches-of-switzerland.co.uk`
*Luxury e-commerce proportion and typographic elegance.*

The whitespace-to-content ratio, the way serif headlines earn their gravity, the way product photography is treated as *documentary* not marketing. Atlas headline typography (prize names, prize amounts) inherits this seriousness. Prize photography style guide follows this documentary-not-advertising principle.

### Anchor 3 — Range Rover Configurator — `landrover.co.uk`
*The "this could be yours" personalisation moment.*

When a user has bought a ticket and is looking at "My Tickets," there should be a moment of *ownership* that mirrors the feeling of specifying a car you haven't bought yet. Not a receipt. An artefact. **Ticket cards on Atlas are objects the user feels affection for, not database rows.**

### Anchor 4 — Kuda Bank (mobile app) — reference: App Store screenshots
*Institutional Nigerian fintech clarity — trust in the Nigerian consumer context.*

Kuda solved a version of Atlas's problem: how do you look premium *and* trustworthy in a Nigerian consumer market where trust is scarce, without becoming another cold-white-Silicon-Valley-fintech clone that feels alien? Atlas takes from Kuda: **information density that respects the user's intelligence, transaction receipts that feel official, and the visual convention that "your money" screens are always calm and clear.**

Atlas does *not* take Kuda's colour palette, energy, or brand voice — those are Kuda-specific. We take the *posture*.

### Anchor 5 — Coinbase transaction proof pages — reference: any confirmed transaction
*Making a technical proof feel authoritative without being visually cold.*

The audit-log verification page is Atlas's wow moment. Coinbase solved a version of this: how do you show a user a blockchain hash and make them feel *"okay, this is real, this is verifiable, I don't fully understand it but I trust the mechanism"?* Atlas takes: **the treatment of hash strings as first-class typography, the copy-to-clipboard affordance done well, the verification-badge motif, the calm presentation of complex information.**

Atlas does *not* take Coinbase's aggressive orange, crypto-culture styling, or "trade now" energy. We take the *proof page discipline.*

---

## 3. Colour direction (starting palette — final on Week 1 sign-off)

Every colour has a job. Nothing here is decorative.

| Role | Colour | Hex (starting) | Why |
|---|---|---|---|
| **Primary** | Deep midnight navy | `#0F1E38` | Institutional gravity, premium restraint. Foundational. All headers, primary buttons, brand marks. |
| **Accent** | Champagne gold | `#C9A96A` | Aspirational warmth. Winner moments, prize amounts, verification badges. Used sparingly — never a background, never a large area. |
| **Surface** | Warm off-white | `#FAF7F2` | Base for content. Not stark white — off-white reads as premium; stark white reads as clinical or budget. |
| **Elevated surface** | Slightly darker warm off-white | `#F2EDE4` | Cards, ticket surfaces, modals. Creates gentle hierarchy without heavy shadows. |
| **Text (primary)** | Near-black charcoal | `#1A1A1A` | Not full `#000000` — softer, more premium. Body copy, headlines against light surfaces. |
| **Text (secondary)** | Warm mid-grey | `#5F5A54` | Timestamps, secondary metadata, supporting labels. |
| **Text (inverted)** | Warm off-white | `#FAF7F2` | Text on midnight-navy surfaces. Matches surface for consistency. |
| **Success** | Deep emerald | `#1E5F4C` | Verified proof, confirmed transactions, won prizes. Never bright green — bright green is casino. |
| **Attention** | Muted amber | `#B87728` | Timers approaching close, KYC pending, awaiting action. |
| **Danger** | Muted terracotta | `#A94A38` | Rejected payments, self-exclusion active, audit-log breaks. Never fire-engine red — fire-engine red is panic UI. |
| **Divider / hairline** | Warm light grey | `#E5DFD6` | Subtle. Almost invisible. Divides without shouting. |

**What this palette explicitly rejects:**

- ❌ Any bright red or bright yellow — reads as budget-airline promotional / desperation.
- ❌ Neon greens or electric blues — reads as crypto / gambling-adjacent.
- ❌ Soft pastels — undermines gravity.
- ❌ Corporate teal or insurance blue — safe but forgettable.
- ❌ Full black backgrounds — reads as luxury e-commerce cliché; Atlas is warmer than that.

**Accessibility note:** every text-on-surface pair in this palette exceeds WCAG 2.2 AA contrast (4.5:1 for body, 3:1 for large text). Champagne gold is *not* used for text on light surfaces (would fail contrast); only for accents, icons, and text on midnight-navy surfaces where it hits 7.2:1.

---

## 4. Typography direction

**Two typefaces. That's it.** Every additional typeface is a fingerprint of "we couldn't decide."

### Display face — serif, for gravity

**Recommendation: Fraunces** (Google Fonts — free, open-source, ships with the app).

Used for: prize amounts, prize names, section headlines on public pages, the winner's name on the winner reveal.

**Why Fraunces:** it's a modern serif with real personality — softly rounded terminals, warm optical sizing, wide range of weights. It carries seriousness without being stiff. Alternative if you want a paid option: GT Sectra or Canela. But Fraunces is 90% of what those give you, at zero licence cost.

**Size scale (display):**
- Prize amount / hero moments: 64px / 4rem
- Section headline: 40px / 2.5rem
- Draw name: 32px / 2rem
- Card heading: 24px / 1.5rem

### Body face — modern grotesque sans, for legibility

**Recommendation: Inter** (Google Fonts — free, open-source, ships with the app).

Used for: everything that isn't a display moment. Body copy, buttons, form inputs, table content, metadata, admin UI.

**Why Inter:** designed specifically for UI legibility at small sizes; large character set (matters for Nigerian names, some of which use diacritics); huge weight range; industry standard so users' eyes are pre-adapted. Alternatives: IBM Plex Sans (also excellent), Söhne (paid).

**Size scale (body):**
- Body copy: 16px / 1rem, 1.6 line-height
- Small metadata / timestamps: 14px / 0.875rem
- Micro labels (admin, uppercase): 12px / 0.75rem, +0.05em letter-spacing
- Button labels: 15px / 0.9375rem, medium weight

**Weight discipline:**
- Fraunces used in weights 400 (regular), 600 (semibold), 700 (bold) only.
- Inter used in weights 400 (regular), 500 (medium), 600 (semibold), 700 (bold) only.
- No thin/light weights (illegible on lower-end Android devices which are >50% of the Nigerian market).

---

## 5. Copy voice

The written product is as much of the design as the visual product. Copy is Atlas talking. Atlas talks like this:

**Declarative. Confident. Unfussy. Never cheerful-marketing. Never sales-y.**

The prize speaks for itself. Atlas does not oversell.

### Sample copy across key moments

**Draw page headline (property prize, later phase):**
> A three-bedroom in Ikoyi. Or ₦180,000,000 in cash — your call.

**Draw page headline (vehicle prize, V1):**
> A 2024 Lexus RX 350. Yours to keep, or ₦45m if you'd rather.

**Skill question intro (before the question):**
> One question before you enter. Atlas is a prize competition, not a lottery — the question confirms your entry.

**After successful entry:**
> Ticket 04829 is yours. Draw closes 8pm Saturday. We'll be in touch.

**Free entry route disclosure (on every draw page):**
> Prefer not to pay? Every draw offers a free postal entry. Same odds, same pool, same shot. Details on how →

**Winner notification (in-app):**
> Congratulations. You've won the 2024 Lexus RX 350. Here's what happens next.

**Audit / proof page intro:**
> This is how we prove it. Every input the draw used is published below. Anyone with the proof can re-run the algorithm and reach the same winner.

**Empty state — no draws currently active:**
> Nothing running right now. The next draw opens Friday morning.

**Error state — payment failed:**
> Something went wrong with the payment. Nothing was charged. Try again, or use a different card.

**Self-exclusion confirmation:**
> Your account will be permanently closed. Any balance is refunded to your original payment method. This cannot be reversed. Type EXCLUDE to confirm.

### Copy rules

- **Never** use: "lottery", "raffle", "luck", "chances of a lifetime", "unbelievable", "amazing", "you could be next!", "hurry", "limited time".
- **Never** use exclamation marks. (One exception permitted: the winner's own name in celebration UI — and only once, on one screen. Everywhere else, no exclamations.)
- **Prefer** short sentences. If a sentence exceeds 20 words, break it.
- **Prefer** the second person ("you") for user-facing copy. Reserve "we" for Atlas-as-operator moments (payouts, verifications, contact).
- **Numbers are premium.** Prize amounts always use the currency symbol and thousands separators. `₦180,000,000` not `180 million naira`.
- **Timestamps are absolute, not relative.** "8pm Saturday" not "in 2 days." (Nigerian users check across time zones with diaspora relatives; relative times are confusing.)

---

## 6. What Atlas is NOT (visually)

Naming the negative space is as important as naming the positive.

Atlas is **not**:

- ❌ **Neon crypto-gambling adjacent.** No dark backgrounds with electric-green accents. No animated dollar signs. Atlas is not a betting app.
- ❌ **Budget-airline promotional.** No red-and-yellow "WIN BIG" typography. No banner ads for the free entry route (the free entry route is a design commitment, not a promotion).
- ❌ **Scandinavian minimalist / cold Silicon Valley.** No stark whites, no rigid grids of monochrome. Atlas has warmth.
- ❌ **Soft-pastel friendly-fintech / chatbot brand.** Atlas is not a friend or a companion. Atlas is a professional service provider.
- ❌ **Corporate-blue-and-white insurance / dated Nigerian bank app circa 2018.** Safe but forgettable is worse than opinionated and wrong.
- ❌ **Lottery-industrial "big spinning wheel" / game-show aesthetic.** The draw reveal is a *moment*, but it's a documentary moment, not a Wheel of Fortune moment.
- ❌ **Overly celebratory / confetti-and-balloons everywhere.** Celebration is earned and rare (winner moments only). Everywhere else, calm.
- ❌ **Chat-with-us bubble in the bottom-right corner.** Support exists but reaches you through named channels (WhatsApp, email). The chat bubble is fintech shorthand for "we're just like everyone else."

---

## 7. Nigerian cultural context — push back if wrong

I'm going to state a hypothesis you should stress-test.

Aspiration in the Nigerian consumer context has its own visual grammar. Wealth is often expressed **visibly and celebratedly**, not silent-luxury-minimalist. Contrast a UK Range Rover ad (understated, quiet, "if you know you know") with a Nigerian premium hospitality brand like Radisson Blu Ikeja or Wheatbaker (confident, visible, unashamed of the fact that this is *nice*).

This has three implications for Atlas that I want you to react to:

1. **Champagne gold should not be apologetic.** In a Western-luxury template you might use gold as a hairline accent, barely visible. In the Nigerian premium context, gold can carry more real estate — a full-width divider, a solid-fill verification badge, gold typography for the prize amount — without tipping into gaudy. My intent is to use it more generously than a Western minimalist template would.
2. **Prize photography should be rich and warm, not muted.** The "Aesop or Le Labo" fashion for desaturated, cool product photography reads as *cold* to a Nigerian premium audience. Prize photography for Atlas should be warm, well-lit, ideally shot in Nigerian light (this matters — even the light temperature reads differently). If the winner is standing next to the prize on the reveal page, that photograph should feel *proud*, not *ironic*.
3. **The winner's story is a bigger deal than in a Western equivalent.** The winner is not embarrassed to be seen winning. Atlas should design the winner-celebration UI to be *properly* celebratory — a full-screen moment, the winner's name in Fraunces at 96px, a documentary photograph — because this is the moment that becomes screenshot fodder for WhatsApp shares, which is *Atlas's most important marketing channel by far*.

If this cultural read is wrong, tell me. If it's right, tell me and I'll design against it more confidently in the wireframes.

---

## 8. Two-week design pass — schedule

Hard 2-week cap per `v0.5-demo-plan.md §5`. If overshoot risk emerges by end of week 1, I hand off "good enough" wireframes with a "V1 design refresh" ticket rather than delay Amelia.

### Week 1 — foundations + consumer flows

| Day | Deliverable |
|---|---|
| **Day 1 (today)** | This tone doc (delivered). Design tokens draft: colour, typography scale, spacing scale (4px base), border-radius scale, elevation levels. |
| **Day 2** | Founder review of tone doc + tokens. **Founder sign-off gate.** Any rejections force a re-do before Day 3 starts. |
| **Day 3** | Consumer wireframe 1: Register → OTP → login. |
| **Day 4** | Consumer wireframes 2–3: Browse active draw + free-entry disclosure on the draw page. |
| **Day 5** | Consumer wireframes 4–5: Buy paid ticket → skill question → payment → ticket appears. Ticket-card design gets extra attention (this is the Anchor 3 "object of affection" moment). |
| **Day 6** | Consumer wireframes 6–7: Draw completes → notification → winner claim flow start. |
| **Day 7** | Buffer + copy-block refinement for consumer flows. End-of-week-1 checkpoint with founder. |

### Week 2 — operator flows + trust story + wow moment + system consolidation

| Day | Deliverable |
|---|---|
| **Day 8** | Operator wireframes 8–9: admin login + create draw. |
| **Day 9** | Operator wireframes 10–12: transcribe free entry, close draw, reveal draw. |
| **Day 10** | Operator wireframe 13: view audit log (admin-facing). |
| **Day 11** | **The wow moment** — public verification page (step 14). This gets *twice* the design time of any other single screen. |
| **Day 12** | Trust-story pages 15–16: prize-competition explainer + responsible-play + free-entry-route detail page. Copy for all three drafted here. |
| **Day 13** | Mini design system consolidation — all 15 components documented as specs (props, states, accessibility notes). |
| **Day 14** | **Exit gate.** Founder review of all wireframes + design system. Hand off to Amelia. Any post-review rework happens in Week 3 in parallel with Amelia's Day-3 backend work. |

### Deliverables format

All wireframes ship as markdown files under `_bmad-output/planning-artifacts/design/wireframes/`, one file per screen. Each file contains:
- ASCII/markdown layout description (Sally has no Figma tool; wireframes are text-first specs that Amelia builds directly against).
- Component composition (which of the 15 design-system components appear on the screen).
- States (empty, loading, error, success).
- Copy for the screen (final, ready to paste into implementation).
- Accessibility notes (focus order, ARIA roles, alt text).
- Interaction notes (what happens on tap, on submit, on error).

Design system components ship as `_bmad-output/planning-artifacts/design/components/<component-name>.md`.

---

## 9. Cross-references

- V0.5 plan: `_bmad-output/planning-artifacts/v0.5-demo-plan.md`
- PRD: `_bmad-output/planning-artifacts/prds/prd-nf-atlas-2026-06-29/PRD.md`
- Copy compliance (Adaeze's future review): `docs/compliance/copy/` (pending)
- Delivery framework: `_bmad-output/planning-artifacts/delivery-framework.md`

---

🎨 *End of tone doc. Sally awaits founder review before advancing to design tokens (Day 1 evening / Day 2). Push back on anything that doesn't ring true — colour palette, typography choice, cultural context, copy voice. This is Day 1; changing course now is free. Changing course after wireframes are in flight is expensive.*
