# Wireframe 14 — Public Proof Page (the wow moment)

**Drafted:** 2026-07-08 (Day 11 per `tone-doc.md §8`)
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** **Working draft — routed to ⚖️ Adaeze early per REVIEW-001 §6.4.** Extra design budget per tone-doc §8 (twice any other single screen). Founder review + Adaeze full compliance review pending Week 2 exit. This is the single most trust-story-load-bearing surface in the entire product.
**Covers:** Flagship flow step 14 from `v0.5-demo-plan.md §2` — *"Proof page — public URL (no login) showing: commitment hash, ticket list hash, revealed server seed, entropy inputs, algorithm reference, computed winner. Copy-paste-runnable verifier script snippet."*
**Surface:** Public web (Next.js, no login required), served at `atlas.ng/proof/{draw_id}`. Responsive; primary design target desktop 1280pt, secondary mobile 375pt.
**Pairs with:** every operator wireframe (09, 10, 11, 12, 13 — this is where those ceremonies' outputs surface publicly), `03-free-entry-disclosure.md` (the mechanic this page proves), `06-draw-completes-notification.md` (the consumer notification whose *"See how the draw was verified"* link points here), Anchor 5 (Coinbase proof pages) from `tone-doc.md §2`, ADR-005 (audit log), ADR-006 (commit-reveal protocol — this page's exact reason to exist).

---

## 0. Why this page is different from every other page in the product

Every other page in Atlas is *for* someone doing something. The consumer wants to enter, or find out, or claim. The operator wants to create, close, reveal, review. Each page's success is measured by how well it serves that intent.

**This page is different. It exists to be there.**

Success on this page is not measured by an action taken on it. Success is measured by whether, months after a draw has run, a curious user, a skeptical journalist, or a regulator can arrive at `atlas.ng/proof/{draw_id}` and, within thirty seconds, reach one of two conclusions:

- *"This draw was verified. I can see how. I could verify it myself if I wanted to."* (Trust confirmed.)
- *"Something here doesn't add up. I want to look closer."* (Legitimate scrutiny enabled, with the tools to act on it.)

Both are wins. What the page must never produce is *"I don't understand what I'm looking at, and I don't have a way to check."* That is the failure mode.

The design pattern that serves this is not persuasion. It is *invitation*. The page does not argue that the draw was fair; it presents the evidence and shows how the evidence connects. The reader draws their own conclusion. This is the Coinbase-proof-page pattern (Anchor 5, tone-doc §2) — the trust move is *"here is the mechanism, verify it if you want to,"* not *"trust us."*

Four design forces this creates:

1. **Legibility over prettiness.** Hash strings are first-class typography. Timestamps are absolute. Data density is high because the data is the product.
2. **Calm authority over celebration.** No confetti when the draw is verified. A calm gold verification mark and one plain-English sentence.
3. **The verifier is a real thing anyone can run.** The `atlas verify` command must exist, be one-tap-copy from this page, and actually work. If the copy-paste-runnable command is chrome, the whole page is chrome.
4. **Winner identity is not the point of this page.** The point is that the *process* was verifiable; the winner is a downstream consequence of that process. Per REVIEW-001 §4.5, winner name is not in indexable HTML by default.

Everything below serves those four forces.

**Non-goals for V0.5:**
- Live "verify this in your browser" — pure client-side re-run of the algorithm in JavaScript. V1+ candidate. V0.5 gives the CLI command and JSON download; browser-native verification is a real thing to build but adds meaningful surface.
- Interactive tickets browser (see every ticket_id in the pool). Compact ticket_id list is downloadable in the proof JSON; UI browser is V1+.
- Multiple prize-per-draw. V0.5 seed is single-prize.
- Historic-draws index (a list of all past proofs). V1 concern.
- Social share cards (Open Graph / Twitter Card) for `/proof/{id}` URLs. V0.5 has basic OG tags; the styled-for-share card is V1 per the note in wf-06 §3.7.
- Winner-story capture (photo, quote) that lives on this page. Belongs on a marketing/winners surface, not on the proof surface. V1+.

---

## 1. URL, indexing, and privacy discipline

Per REVIEW-001 §4.5 and Adaeze's ruling:

- URL pattern: `atlas.ng/proof/{draw_id}` — keyed by the draw, not by the winner.
- Indexable by search engines: **yes** for the process and the mechanic; **no** for winner-identifying information.
- Winner name, city, contact — **not rendered in server HTML.** The server response is winner-name-free. If publication consent was granted (per wf-07 §7.5 optional checkbox), a small client-side fetch after page load hydrates the winner-name field. This means:
  - Search engines index the proof, not the person.
  - A cached page-source view (browser view-source, archive.org) shows the proof mechanics but not the winner's name.
  - The winner name still appears in the rendered page for a normal browser session, so the human trust-story reader sees who won.
- If publication consent was declined, the winner-name element renders as *"Winner — {city}"* (anonymous fallback). Not fetched, not conditional — just the anonymous rendering.
- `noindex` meta on the winner-name element via `<span data-noindex>` and a `robots.txt` policy for the fetch endpoint.
- Ticket-owner information (contacts, BVN, KYC state) — **never on this surface.** That data lives only on the operator surface (wf-13) and only under redaction.

---

## 2. Page anatomy (desktop, 1280pt primary target)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│                       [ Atlas wordmark ]                                  │  ← simple top bar, 72pt tall
│                                                                           │      centered wordmark
│                    ATLAS · PROOF OF DRAW                                  │      type.label.micro gold
│                                                                           │      uppercase, 8pt below
│                                                                           │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│                                                                           │  space.1600
│                                                                           │
│                                                                           │
│                  ┌─────────────────────────────────┐                      │  ← VerdictCard,
│                  │                                  │                      │      centered, 720pt wide
│                  │              ✓                   │                      │      radius.large,
│                  │                                  │                      │      surface.elevated,
│                  │      This draw is verified.      │                      │      elevation.1,
│                  │                                  │                      │      64pt padding
│                  │  ₦2,000,000 in cash · 13 Jul 2026│                      │
│                  │                                  │                      │
│                  │  ─────────────────────────       │                      │
│                  │                                  │                      │
│                  │  Anyone can independently confirm│                      │
│                  │  the winner using the inputs     │                      │
│                  │  published below. The mechanism  │                      │
│                  │  is described at each step.      │                      │
│                  │                                  │                      │
│                  └─────────────────────────────────┘                      │
│                                                                           │
│                                                                           │  space.1600
│                                                                           │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│                          THE THREE COMMITMENTS                            │  ← type.label.micro gold
│                                                                           │      centered, uppercase
│                                                                           │  space.400
│                                                                           │
│                                                                           │
│  ┌─────────────────────────┐  ┌──────────────────┐  ┌──────────────────┐│
│  │  ▪ 1  COMMITMENT         │  │  ▪ 2  CLOSE      │  │  ▪ 3  REVEAL     ││
│  │                          │  │                  │  │                  ││  ← three columns,
│  │  When the draw was       │  │  When sales      │  │  When the        ││      radius.large,
│  │  created, we sealed a    │  │  ended, we froze │  │  winner was      ││      surface.elevated,
│  │  secret in a hash. It    │  │  the pool and    │  │  chosen using    ││      elevation.0,
│  │  couldn't be known to    │  │  hashed the      │  │  public entropy  ││      hairline border,
│  │  anyone until reveal.    │  │  ticket list.    │  │  we couldn't     ││      24pt padding
│  │                          │  │                  │  │  control.        ││      body.default primary
│  │  ────────────────────    │  │  ────────────────│  │  ────────────────││      then hash block below
│  │                          │  │                  │  │                  ││
│  │  Commitment hash         │  │  Tickets hash    │  │  Server seed     ││
│  │  3f2c4b8e...8a91  📋     │  │  a7b3e9f1...4d82│  │  9e014b7d...4c67 ││  ← body.mono 14pt
│  │                          │  │  📋              │  │  📋              ││      copy affordance
│  │  Committed               │  │  Closed          │  │  Revealed        ││
│  │  08 Jul 2026,            │  │  12 Jul 2026,    │  │  13 Jul 2026,    ││
│  │  13:47:52 WAT            │  │  19:58:14 WAT    │  │  21:06:41 WAT    ││
│  │                          │  │                  │  │                  ││
│  └─────────────────────────┘  └──────────────────┘  └──────────────────┘│
│                                                                           │
│                                                                           │  space.1200
│                                                                           │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│                          THE POOL AT CLOSE                                │  ← eyebrow
│                                                                           │  space.400
│                                                                           │
│                                                                           │
│                  ┌─────────────────────────────────┐                      │  ← PoolCard, centered
│                  │                                  │                      │      radius.large
│                  │        1,247 tickets             │                      │      surface.elevated
│                  │                                  │                      │      elevation.0
│                  │  ─────────────────────────       │                      │
│                  │                                  │                      │
│                  │  1,160    Paid                   │                      │  ← two-column stat rows
│                  │     87    Free-route             │                      │      body.default
│                  │  ─────────────────────────       │                      │
│                  │  1,247    Total pool             │                      │
│                  │                                  │                      │
│                  │  All entries — paid and free —   │                      │  ← body.small secondary
│                  │  were drawn from the same pool.  │                      │      the equal-terms
│                  │                                  │                      │      promise restated here
│                  └─────────────────────────────────┘                      │
│                                                                           │
│                                                                           │  space.1200
│                                                                           │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│                       PUBLIC ENTROPY USED                                 │  ← eyebrow
│                                                                           │  space.400
│                                                                           │
│                                                                           │
│  ┌────────────────────────────────────┐  ┌────────────────────────────────┐│
│  │  ▪ BITCOIN                          │  │  ▪ DRAND                        ││
│  │                                     │  │                                 ││  ← two columns,
│  │  Block #856,142                     │  │  Round #4,829,301               ││      same treatment as
│  │  Mined 13 Jul 2026, 20:18:44 WAT   │  │  Epoch 13 Jul 2026, 20:14:52 WAT││      commitments row
│  │                                     │  │                                 ││
│  │  Block hash                         │  │  Randomness                     ││
│  │  8f1c3e9f...9e42  📋                │  │  3b7d02a4...0c88  📋            ││
│  │                                     │  │                                 ││
│  │  Verify block on:                   │  │  Signature verified against     ││
│  │  · mempool.space →                  │  │  the drand League of Entropy    ││
│  │  · blockstream.info →               │  │  group public key.              ││
│  │                                     │  │                                 ││
│  │                                     │  │  Verify round on:               ││
│  │                                     │  │  · api.drand.sh →               ││
│  └────────────────────────────────────┘  └────────────────────────────────┘│
│                                                                           │
│  Both sources are independent and public. The winner selection uses       │  ← body.default centered
│  the combined entropy of Bitcoin block hash and drand round.              │      body.default secondary
│                                                                           │
│                                                                           │  space.1200
│                                                                           │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│                        HOW THE WINNER WAS CHOSEN                          │  ← eyebrow
│                                                                           │  space.400
│                                                                           │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  Algorithm                                                         │  │  ← AlgorithmCard,
│  │                                                                    │  │      radius.large,
│  │  prng_seed = HMAC-SHA-256(                                         │  │      surface.elevated,
│  │    key   = server_seed,                                            │  │      hairline border,
│  │    msg   = bitcoin_hash || drand_round || tickets_hash             │  │      48pt padding
│  │  )                                                                 │  │      body.mono for algorithm
│  │                                                                    │  │      body.default for prose
│  │  Iterate the PRNG stream, interpret each 32-byte block as a       │  │
│  │  big-endian integer, take modulo 1,247 (the ticket count).         │  │
│  │  The first index selects the winning ticket. The next 5 distinct  │  │
│  │  indices select reserves in order.                                 │  │
│  │                                                                    │  │
│  │  Full algorithm spec: atlas.ng/spec/draw-algo/v1 →                 │  │
│  │                                                                    │  │
│  │  ─────────────────────────                                          │  │
│  │                                                                    │  │
│  │  Result                                                            │  │
│  │                                                                    │  │
│  │  Winning ticket    04829                                           │  │  ← body.mono 24pt
│  │                                                                    │  │      color.text.primary
│  │  Reserves          07213 · 00042 · 03917 · 06104 · 01288          │  │
│  │                                                                    │  │
│  │  ─────────────────────────                                          │  │
│  │                                                                    │  │
│  │  Winner  <span data-noindex data-winner-slot>                      │  │  ← client-side rendered
│  │            (Client-side, opt-in per REVIEW-001 §4.5)                │  │      only if publication
│  │          </span>                                                    │  │      consent granted.
│  │                                                                    │  │      Otherwise: "Winner — {city}"
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│                                                                           │  space.1200
│                                                                           │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│                           VERIFY IT YOURSELF                              │  ← eyebrow
│                                                                           │  space.400
│                                                                           │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  Three ways to check                                               │  │  ← VerifierCard,
│  │                                                                    │  │      radius.large,
│  │                                                                    │  │      surface.elevated,
│  │  1.  Download the proof package                                    │  │      elevation.0,
│  │                                                                    │  │      hairline border,
│  │      Every input and every hash on this page, in a single JSON     │  │      48pt padding
│  │      file. Same content the /proof API returns.                    │  │
│  │                                                                    │  │
│  │      [ Download proof.json ]                                       │  │  ← secondary button
│  │                                                                    │  │
│  │  ─────────────────────────                                          │  │
│  │                                                                    │  │
│  │  2.  Run the verifier locally                                      │  │
│  │                                                                    │  │
│  │      A standalone Python script re-runs the algorithm using the    │  │
│  │      published inputs and prints the winning ticket. Requires      │  │
│  │      Python 3.11+. Source at github.com/atlas-africa/verify.       │  │
│  │                                                                    │  │
│  │      ┌──────────────────────────────────────────────────────────┐ │  │
│  │      │  $ pip install atlas-verify                              │ │  │  ← body.mono, prominent
│  │      │  $ atlas-verify atlas.ng/proof/DRAW-2026-07-08-A         │ │  │      radius.medium,
│  │      │                                                          │ │  │      surface.inverted
│  │      │  → Winning ticket: 04829  ✓ matches published result    │ │  │      (navy background),
│  │      └──────────────────────────────────────────────────────────┘ │  │      color.text.accent (gold)
│  │                                                                    │  │      for prompt, inverted for
│  │      [ 📋 Copy command ]                                            │  │      command text.
│  │                                                                    │  │
│  │  ─────────────────────────                                          │  │
│  │                                                                    │  │
│  │  3.  Reproduce it from first principles                            │  │
│  │                                                                    │  │
│  │      Every input on this page is a public value. The algorithm is  │  │
│  │      HMAC-SHA-256 followed by modular indexing. A competent        │  │
│  │      engineer can reproduce the result in any language in an       │  │
│  │      afternoon. The full spec is at atlas.ng/spec/draw-algo/v1.   │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│                                                                           │  space.1200
│                                                                           │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│                              AUDIT TRAIL                                  │  ← eyebrow
│                                                                           │  space.400
│                                                                           │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  Every action that touched this draw was written to Atlas's        │  │
│  │  append-only audit log. The log is hash-chained — retroactive      │  │
│  │  changes are detectable.                                           │  │
│  │                                                                    │  │
│  │  Chain head at reveal   d4a7f1e6...02c8    📋                      │  │  ← body.mono
│  │                                                                    │  │
│  │  Event                          Time (WAT)          Sequence       │  │  ← audit table (5 rows)
│  │  ────────────────────────────────────────────────────────────      │  │
│  │  draw.committed                 08 Jul 13:47:52     #4988          │  │
│  │  draw.entries_snapshot          12 Jul 19:58:14     #4972          │  │
│  │  draw.revealed                  13 Jul 21:06:41     #5012          │  │
│  │  draw.winner_selected           13 Jul 21:06:44     #5013          │  │
│  │                                                                    │  │
│  │  Full audit log for regulators and auditors — request via         │  │
│  │  compliance@atlas.ng.                                              │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│                                                                           │  space.1600
│                                                                           │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│                                                                           │  space.800
│                                                                           │
│      Atlas Africa Ltd · Company RC {number}                              │  ← body.small secondary
│      Registered office {address}                                          │      centered footer
│      Data controller · dpo@atlas.ng                                       │
│                                                                           │
│      This page is the public proof for DRAW-2026-07-08-A. It exists      │
│      permanently. The URL will resolve to this content indefinitely.      │
│                                                                           │
│                                                                           │  space.1200
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Section-by-section spec

### 3.1 Top bar

Fixed 72pt, `surface.base` background. Centered wordmark (Atlas, Fraunces 24pt) + gold uppercase eyebrow *"ATLAS · PROOF OF DRAW"* below. No nav — this is a landing page, not part of a site journey.

### 3.2 VerdictCard

The single most important component on the page. Composition:

- Gold check icon (48pt, `color.brand.accent`) — same visual language as consumer trust moments.
- Headline: *"This draw is verified."* — display.section (40pt Fraunces). Declarative, calm. No exclamation. Same tonal register as *"You're in."* / *"You've been paid."* — the Atlas voice.
- Prize + date subline: body.default secondary.
- Divider hairline.
- Explainer paragraph: *"Anyone can independently confirm the winner using the inputs published below. The mechanism is described at each step."* — body.default primary, centered. **This paragraph is the whole thesis of the page in two sentences.**

Card: 720pt max width, `surface.elevated`, `elevation.1`, `radius.large`, 64pt padding. Centered.

**State variants:**
- **Verified (as drawn):** `✓` gold, *"This draw is verified."*
- **Awaiting reveal (draw is closed but not yet revealed):** `⋯` in `color.state.attention`, *"This draw is awaiting reveal."* Subhead: *"Sales closed {close_time}. Winner announced {reveal_time}."*
- **In progress (draw is open, no commit to prove yet — visitor arrived at proof page during sales window):** `▪` in `color.brand.accent`, *"This draw is in progress."* Subhead points at consumer draw page.
- **Cancelled (rare):** `⌀` in `color.state.danger`, *"This draw was cancelled."* Body explains the cancellation event, refund status, and link to the audit-log entry.

### 3.3 The three commitments (row)

Three columns, each with:
- Numbered gold eyebrow (`▪ 1 COMMITMENT` / `▪ 2 CLOSE` / `▪ 3 REVEAL`).
- Plain-English paragraph explaining what this step means for a non-technical reader.
- The hash (truncated, mono, copy affordance).
- The timestamp.

Cards use `surface.elevated`, hairline border, `elevation.0`, 24pt padding. `radius.large`.

**Copy commentary:**
- Each paragraph is one sentence. Two if it earns it. The reader is skimming; the reader gets the mechanic.
- Each paragraph explains the *significance* (why this step matters for trust), not the *mechanics* (algorithm names, formats). Mechanics land in section §3.6 for readers who want them.

### 3.4 Pool at close

Centered `PoolCard`. Big total number in `display.card` (24pt Fraunces). Paid/free breakdown as two-column definition-list rows. Footer sentence: *"All entries — paid and free — were drawn from the same pool."* — restates the equal-terms promise from wf-03 §3.4 on the public proof itself.

This is a deliberate cross-surface echo. The consumer sees the paid/free split on the draw card. The disclosure sheet promises equal treatment. The proof page proves it — with the actual counts frozen at close, published permanently.

### 3.5 Public entropy used (two columns)

Two side-by-side cards — Bitcoin and drand — each with:
- Source identifier (block number / round number).
- Timestamp.
- The hash / randomness value.
- Verification pointers ("Verify block on: mempool.space, blockstream.info").
- Signature verification note for drand.

**External-verification pointers are load-bearing.** The whole point of using public entropy sources is that they are *independently checkable*. A reader who wants to confirm that `#856,142`'s hash really is `8f1c3e9f...9e42` can click through to a third-party Bitcoin explorer and see for themselves. If those links were absent, the entropy might as well be a private random number — the trust would derive from Atlas asserting the values.

Below the two columns: one sentence explaining why both are used together (independence).

### 3.6 How the winner was chosen — the algorithm card

Wide single card. Composition:

- **Algorithm header + mono block** showing the exact HMAC-SHA-256 expression and the iteration logic. Rendered in `body.mono` at 14pt with generous line-height. This is the moment the page trusts the reader with the actual algorithm. Anchor 5 treatment applied — hash typography as first-class.
- **One prose paragraph** explaining the iteration in plain English (32-byte blocks, big-endian int, mod N).
- **Link to full spec** at `atlas.ng/spec/draw-algo/v1` — versioned URL. This URL points at a technical spec document (owned by Winston + Amelia; not designed here) that a competent engineer would use to reproduce the algorithm.
- **Result section** below the algorithm: winning ticket (mono 24pt), reserves (mono, comma-separated ticket IDs).
- **Winner name field** — client-side-hydrated `<span data-noindex data-winner-slot>` — either the consented winner name+city or the anonymous *"Winner — {city}"* fallback. **Empty in server HTML per §1.**

### 3.7 Verify it yourself

The VerifierCard. Three ways to check, in order of increasing rigour:

1. **Download proof.json** — the fastest path. Every input and hash on the page, in a single JSON, matching the `/proof` API response byte-for-byte. Downloadable as a file.
2. **Run the verifier locally** — the `atlas-verify` CLI. Two-line command block, monospaced, rendered in `surface.inverted` (navy background) with gold prompt and inverted text — visually distinct from any other card on the page, reads as a *terminal moment* even for readers who've never opened one. **Copy-command affordance is the load-bearing interaction** — one tap, whole command in clipboard. Copy-tested against every major OS clipboard.
3. **Reproduce from first principles** — the "power user" path. Not a button; a paragraph acknowledging that a competent engineer can reproduce the result in any language, with a pointer to the spec.

**Design intent:** the three paths are ordered from *"easy and enough for a curious reader"* to *"maximally rigorous and enough for a suspicious auditor."* The page respects both audiences without patronising the first or under-serving the second.

### 3.8 Audit trail

A compact 5-row table showing the key audit events for this draw with their sequence numbers. Plus the chain head at reveal (with copy affordance). Plus a line pointing at `compliance@atlas.ng` for regulators/auditors who need the full log.

Deliberately not a full audit-log dump — this page is not the operator surface (wf-13). The five key events are the ones a public reader needs to see: commit, snapshot, reveal, winner-selected. If they want more, they email compliance.

### 3.9 Footer

Small footer with:
- Legal identity (Atlas Africa Ltd, RC number, registered office) — **required for real launch** per REVIEW-001 §4.4.
- Data controller / DPO contact — NDPA 2023 requirement per REVIEW-001 §6.5.
- A permanence commitment: *"This page is the public proof for DRAW-{id}. It exists permanently. The URL will resolve to this content indefinitely."* This is a promise Atlas keeps by design (the /proof endpoint is not deprecated, ever) and a promise the reader can rely on for regulatory record-keeping.

---

## 4. Responsive / mobile

Mobile viewport 375pt:
- Top bar stays; wordmark same size, eyebrow wraps if needed.
- VerdictCard: same content, adjusted padding (32pt not 64pt), full width minus 16pt margins.
- **Three commitments row stacks vertically** — three cards top to bottom.
- Pool card unchanged, narrower.
- Public entropy: **two Bitcoin + drand cards stack vertically.**
- Algorithm card: mono block scrolls horizontally if the line is longer than the viewport. Wrapping the algorithm expression is *not* acceptable — the mathematical intent is line-oriented; horizontal scroll is the correct compromise.
- Verifier terminal block: same horizontal-scroll treatment. Copy-command affordance stays prominent.
- Audit table: horizontal-scroll wrapping.
- Footer copy wraps as expected.

Mobile-tested viewport target: iPhone 13 (390pt) and small Android (360pt). Landscape not specifically designed; existing responsive behaviour holds.

---

## 5. States

**Verified (post-reveal — the primary state):** as drawn.

**Awaiting reveal (post-close, pre-reveal):** VerdictCard shows the `⋯` variant. Sections §3.3 (three commitments) show *Commitment* and *Close* filled; *Reveal* shows a placeholder card: *"Reveal fires at {reveal_time}. This section will complete then."* Sections §3.5, §3.6, and the audit-trail rows for reveal-events are absent. Verifier section shows *"Verifier command will be available after reveal."*

**In progress (open, pre-close):** VerdictCard shows the `▪` variant + points at the consumer draw page. Only section §3.3 first commitment (COMMITMENT) is filled; the others are placeholders. Verifier section absent.

**Cancelled:** VerdictCard shows `⌀` in danger. Prose block explains the cancellation with a link to the audit-log entry. No entropy or algorithm section. Refund status noted.

**Not found (visitor arrives at a `/proof/{id}` URL that doesn't exist):** page 404 with a small explanation: *"No draw with this identifier exists. If you were looking for a specific draw's proof, check the URL or contact us at hello@atlas.ng."*

**Loading (initial render — server-side):** should be near-instant; if the API is slow, the page shows a skeleton of the VerdictCard + section headings without content.

---

## 6. Copy inventory

| Section | Element | Copy |
|---|---|---|
| Top bar | Wordmark eyebrow | ATLAS · PROOF OF DRAW |
| Verdict (verified) | Icon | ✓ |
| Verdict (verified) | Headline | This draw is verified. |
| Verdict (verified) | Subhead | {prize} · {reveal_date} |
| Verdict (verified) | Body | Anyone can independently confirm the winner using the inputs published below. The mechanism is described at each step. |
| Verdict (awaiting reveal) | Headline | This draw is awaiting reveal. |
| Verdict (awaiting reveal) | Body | Sales closed {close_time}. Winner announced {reveal_time}. |
| Verdict (in progress) | Headline | This draw is in progress. |
| Verdict (in progress) | Body | Sales are open until {close_time}. The proof completes after the winner is revealed. See the current draw. |
| Verdict (cancelled) | Headline | This draw was cancelled. |
| Three commitments | Row eyebrow | THE THREE COMMITMENTS |
| Commit 1 | Header | ▪ 1  COMMITMENT |
| Commit 1 | Body | When the draw was created, we sealed a secret in a hash. It couldn't be known to anyone until reveal. |
| Commit 1 | Hash label | Commitment hash |
| Commit 1 | Timestamp label | Committed |
| Commit 2 | Header | ▪ 2  CLOSE |
| Commit 2 | Body | When sales ended, we froze the pool and hashed the ticket list. |
| Commit 2 | Hash label | Tickets hash |
| Commit 2 | Timestamp label | Closed |
| Commit 3 | Header | ▪ 3  REVEAL |
| Commit 3 | Body | When the winner was chosen using public entropy we couldn't control. |
| Commit 3 | Hash label | Server seed |
| Commit 3 | Timestamp label | Revealed |
| Pool | Eyebrow | THE POOL AT CLOSE |
| Pool | Total | {total} tickets |
| Pool | Row — paid | {paid} · Paid |
| Pool | Row — free | {free} · Free-route |
| Pool | Row — total | {total} · Total pool |
| Pool | Promise | All entries — paid and free — were drawn from the same pool. |
| Entropy | Eyebrow | PUBLIC ENTROPY USED |
| Entropy bitcoin | Header | ▪ BITCOIN |
| Entropy bitcoin | Block | Block #{block_height} |
| Entropy bitcoin | Time | Mined {mined_at} |
| Entropy bitcoin | Hash label | Block hash |
| Entropy bitcoin | Verify | Verify block on: mempool.space · blockstream.info |
| Entropy drand | Header | ▪ DRAND |
| Entropy drand | Round | Round #{round} |
| Entropy drand | Time | Epoch {epoch_time} |
| Entropy drand | Randomness label | Randomness |
| Entropy drand | Verify | Verify round on: api.drand.sh |
| Entropy drand | Signature note | Signature verified against the drand League of Entropy group public key. |
| Entropy | Combined note | Both sources are independent and public. The winner selection uses the combined entropy of Bitcoin block hash and drand round. |
| Algorithm | Eyebrow | HOW THE WINNER WAS CHOSEN |
| Algorithm | Header | Algorithm |
| Algorithm | Prose | Iterate the PRNG stream, interpret each 32-byte block as a big-endian integer, take modulo {ticket_count} (the ticket count). The first index selects the winning ticket. The next {reserves_count} distinct indices select reserves in order. |
| Algorithm | Spec link | Full algorithm spec: atlas.ng/spec/draw-algo/v1 |
| Algorithm | Result header | Result |
| Algorithm | Winning ticket label | Winning ticket |
| Algorithm | Reserves label | Reserves |
| Algorithm | Winner label (consented) | Winner |
| Algorithm | Winner value (anonymous) | Winner — {city} |
| Verifier | Eyebrow | VERIFY IT YOURSELF |
| Verifier | Header | Three ways to check |
| Verifier | Path 1 title | 1. Download the proof package |
| Verifier | Path 1 body | Every input and every hash on this page, in a single JSON file. Same content the /proof API returns. |
| Verifier | Path 1 CTA | Download proof.json |
| Verifier | Path 2 title | 2. Run the verifier locally |
| Verifier | Path 2 body | A standalone Python script re-runs the algorithm using the published inputs and prints the winning ticket. Requires Python 3.11+. Source at github.com/atlas-africa/verify. |
| Verifier | Path 2 command | $ pip install atlas-verify\n$ atlas-verify atlas.ng/proof/{draw_id}\n\n→ Winning ticket: {ticket} ✓ matches published result |
| Verifier | Path 2 copy | 📋 Copy command |
| Verifier | Copy toast | Command copied to clipboard. |
| Verifier | Path 3 title | 3. Reproduce it from first principles |
| Verifier | Path 3 body | Every input on this page is a public value. The algorithm is HMAC-SHA-256 followed by modular indexing. A competent engineer can reproduce the result in any language in an afternoon. The full spec is at atlas.ng/spec/draw-algo/v1. |
| Audit | Eyebrow | AUDIT TRAIL |
| Audit | Intro | Every action that touched this draw was written to Atlas's append-only audit log. The log is hash-chained — retroactive changes are detectable. |
| Audit | Chain head label | Chain head at reveal |
| Audit | Table headers | Event / Time (WAT) / Sequence |
| Audit | Compliance-contact line | Full audit log for regulators and auditors — request via compliance@atlas.ng. |
| Footer | Legal | Atlas Africa Ltd · Company RC {rc_number} |
| Footer | Address | Registered office {address} |
| Footer | DPO | Data controller · dpo@atlas.ng |
| Footer | Permanence | This page is the public proof for {draw_id}. It exists permanently. The URL will resolve to this content indefinitely. |
| 404 | Headline | We don't have a proof for that draw. |
| 404 | Body | No draw with this identifier exists. If you were looking for a specific draw's proof, check the URL or contact us at hello@atlas.ng. |

**Copy commentary:**
- *"This draw is verified."* is deliberate. Alternatives considered and rejected: *"Verified draw."* (too label-like), *"Fair draw ✓"* (asserts a value judgement — fair according to whom?), *"Draw completed successfully."* (marketing-flavoured). *"This draw is verified"* is a statement about verifiability, not about outcome. That is what the page can promise.
- The three-commitment paragraphs (COMMITMENT / CLOSE / REVEAL) each start with *"When…"* — deliberate parallelism. The pattern reads as a timeline even before the reader has parsed the mechanic.
- *"When the winner was chosen using public entropy we couldn't control"* — the sentence in the REVEAL commit paragraph does more work than any other single sentence on the page. It says: (a) winner was chosen, (b) the choice used public entropy, (c) Atlas could not manipulate that entropy. Three trust claims in twelve words. **Adaeze — this sentence is the load-bearing legal-adjacent claim on the page; please flag any concern.**
- *"Three ways to check"* — the count is a commitment. Doing exactly three (not four, not two) reads as considered. The three are ordered by rigour (easy → thorough).

---

## 7. Accessibility

- **Landmark structure:** proper `<main>` + `<header>` + `<footer>`; each major section wrapped in `<section aria-labelledby="{id}">` with the eyebrow as the `<h2>`.
- **Heading hierarchy:** page title `<h1>` from VerdictCard headline; section eyebrows `<h2>`; card sub-headings `<h3>`.
- **Focus order:** top-bar wordmark → VerdictCard (composite readable summary) → each section top-to-bottom → each copy-affordance individually focusable → footer.
- **Hash typography:** each hash is inside a `<code>` with `aria-label="Truncated hash: {first_8} truncated {last_4}"` and a `Copy full hash` button beside. Screen reader users hear the truncation cue explicitly and can trigger the copy.
- **External-verification links:** each external link (`mempool.space`, `blockstream.info`, `api.drand.sh`, `github.com/atlas-africa/verify`) has `rel="noopener noreferrer"` and `aria-label="{destination} — external site"`.
- **Verifier terminal block:** rendered inside `<pre><code>`, `role="region"` with a label. Copy-command button has `aria-label="Copy verifier command to clipboard"`.
- **Client-side winner-name hydration:** the `<span data-winner-slot>` initially contains the anonymous fallback text; after client-side fetch, if consent granted, it updates. `aria-live="polite"` announces the change.
- **Colour independence:** Verdict state (✓ / ⋯ / ▪ / ⌀) is never colour-only; the icon shape carries meaning.
- **Reduce motion:** no animations on this page beyond a brief fade for the winner-name hydration. Reduce-motion mode disables the fade.
- **Contrast:** all tokens as spec. The `surface.inverted` (navy) terminal block with gold prompt and inverted text hits AAA on desktop and AA on mobile after adjustment.
- **Print stylesheet:** yes — regulators and auditors will print this page. Print CSS collapses sections into a legible black-on-white document, keeps hash typography monospaced, retains verifier command text, includes footer. No copy affordances in print (they don't work on paper).

---

## 8. Design invariants for the proof page

Recording explicitly because this page is the highest-trust surface:

1. **Winner name never in indexable HTML.** Client-side hydration only, `noindex`, `robots.txt` on the hydration endpoint.
2. **Hash values always in body.mono typography, always with copy affordance.** No exceptions.
3. **Timestamps always absolute (WAT).** Never relative.
4. **External-verification links are load-bearing.** Removing a Bitcoin explorer or the drand endpoint pointer breaks the whole "verify it yourself" claim.
5. **The verifier command works.** The `atlas-verify` package exists, is versioned, is a real Python package on PyPI, and produces the winning ticket when run against the published proof. If this command is chrome, the page is a lie.
6. **The URL is permanent.** `/proof/{draw_id}` resolves forever. Deprecating a proof URL is worse than losing a customer.
7. **The proof.json download is byte-identical to the /proof API response.** Any drift breaks reproducibility.
8. **No marketing on this page.** No "Try Atlas today", no "See the current draw" CTA in the body (a link is fine in the *"in progress"* verdict variant only). This page is evidence, not funnel.

---

## 9. Open questions

### For ⚖️ Adaeze — this is the surface where your review-001 §6.4 early-look applies:

1. **VerdictCard headline "This draw is verified"** (§3.2). Is this the right claim to make on Atlas's behalf, or does it stray into the legal-classification territory you flagged in REVIEW-001 §2.1? My read: this is a statement about verifiability (a fact about the page's contents), not about legal classification (a claim about the mechanic). Confirm.
2. **The REVEAL-commit paragraph** (§6): *"When the winner was chosen using public entropy we couldn't control."* Legally and factually load-bearing. Any changes?
3. **Winner-name client-side hydration** (§1, §3.6, §8.1). Is this treatment sufficient to satisfy your REVIEW-001 §4.5 concern? Alternative options laid out — if this isn't enough, name what would be.
4. **Anonymous winner fallback** (*"Winner — {city}"*) — same treatment across surfaces. Confirm the copy.
5. **Audit trail excerpt on this public page** (§3.8, §6). Five events shown. Is this the right subset? Should any of these be omitted from public view (e.g. actor identity)? Currently the public table doesn't show actor at all — actor is Atlas-internal-only on this surface.
6. **Compliance contact line** (§6, footer). *"Full audit log for regulators and auditors — request via compliance@atlas.ng."* — is compliance@atlas.ng the right address, or should there be a more formal regulator-request channel?
7. **NDPA footings on this public page** — legal identity, DPO contact are present in the footer (§3.9). Anything else missing?
8. **Permanence commitment** ("This page … exists permanently"). Legally binding? A promise Atlas can keep by design, but should we soften?
9. **The proof.json downloadable** — should it carry a cryptographic signature so a downloader can prove authenticity without Atlas's site being available? (Deferred as non-goal, but flagging as future work.)

### For founder:

10. **"This draw is verified" as the primary headline** — the page's whole voice depends on this line. Any different-worded alternative?
11. **Print stylesheet** (§7). Adds a small amount of work but produces regulator-friendly output. Recommend keep.
12. **404 page copy** — currently *"We don't have a proof for that draw."* Confirm.
13. **Company registration details in footer** — real values required for real launch. For V0.5 demo, placeholder or real values?

### For 💻 Amelia:

14. **`/api/v1/draws/{id}/proof` endpoint** — returns the exact JSON that (a) the page renders from and (b) `Download proof.json` downloads. Byte-identical to what the on-page rendering computes from. Confirm this contract.
15. **`atlas-verify` package.** V0.5 target: real package on PyPI, single-command install, reads proof URL, re-runs algorithm, prints winning ticket. Amelia owns build; Winston to sign off on the algorithm spec at `atlas.ng/spec/draw-algo/v1`.
16. **Winner-name hydration endpoint.** `GET /api/v1/draws/{id}/winner-display` — returns `{ mode: "consented"|"anonymous", name?: string, city: string }`. `noindex` on the endpoint, no caching, robots-disallowed.
17. **Server-rendered HTML content.** Next.js SSR (or SSG-with-revalidate) — the page must be crawlable and fast. Confirm framework fit.

### For 🏗️ Winston:

18. **Algorithm-spec URL `atlas.ng/spec/draw-algo/v1`** — versioned technical spec document. Content owner: Winston. Format: an HTML doc that describes the algorithm, references RFCs, includes worked example. Not designed here (it's a technical spec, not a UX artefact).
19. **Draw-algo versioning.** If we ever change the algorithm, we mint `/v2` and older draws still point at `/v1`. Confirm.

### For 🛡️ Tobi:

20. **Public site delivery.** The proof surface is on the Next.js monolith per plan §4; delivered via the same infra. **Cache aggressively** (proof content is immutable after reveal) but respect the `winner-display` endpoint's no-cache. CDN configuration falls to you when real launch approaches.
21. **URL permanence.** The /proof/{id} URLs are commitments to the public. Infra needs to preserve them across deploys, domain changes, migrations. Add to the runbook set.

---

## 10. Cross-references

- Flow source: `v0.5-demo-plan.md §2` (step 14).
- Upstream: `09-create-draw.md §7` (commit receipt — same commitment hash), `11-close-and-reveal-draw.md §4` (close receipt — same tickets hash), `12-reveal-draw.md §6` (reveal receipt — same server seed + entropy + winner).
- Consumer counterpart: `06-draw-completes-notification.md §3.6` (Verified link that lands here), `03-free-entry-disclosure.md §2.3` post-reveal state.
- Admin counterpart: `13-audit-log-admin.md` (full audit log — this page shows the excerpt).
- Anchor 5 from `tone-doc.md §2` — Coinbase proof pages, the direct design reference.
- ADR-005 (audit log — hash-chain visible in §3.8), ADR-006 (commit-reveal — this page's exact reason to exist), ADR-007 §PII redaction (winner-name treatment).
- Compliance review: `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md` §4.5, §6.4.
- Tokens: `tokens.md` (hash typography = body.mono, verdict card treatment, all colours).
- Tone: `tone-doc.md` (Anchor 5, copy voice, no-exclamations, absolute-timestamps).

---

🎨 *End of wireframe 14 — working draft.*

*Day 11 complete. This is the wow moment. It's the surface Atlas will be judged on most: consumers will glance, journalists will scrutinise, regulators will archive, and — if we do the job right — competitors will study and imitate. If any of the copy, the sequencing of the three commitments, the verify-it-yourself pattern, the winner-name treatment, or the audit-trail excerpt doesn't land for you, this is the moment to push back — before Day 12 (trust-story pages) reuses the visual language and Day 13 consolidates the design system.*

*Adaeze — flagged for early review per REVIEW-001 §6.4. Not polished; ready for compliance pass on winner-name treatment, the "verified" claim, the audit-trail excerpt scope, and the NDPA footings.*

*Founder — three days from Week 2 exit. Recommend a full end-to-end read (all 14 wireframes + tone-doc + tokens + REVIEW-001 + week-1 checkpoint) before Day 14 sign-off. Day 12 (trust-story explainer pages) tomorrow.*
