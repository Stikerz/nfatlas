# Amendment Proposal AMEND-004 — commit the prize image, not just the prize copy

**Artefacts:** `docs/adr/ADR-005-hash-chained-audit-log.md` (primary), `docs/adr/ADR-006-commit-reveal-protocol-and-public-entropy.md` (no change — see §2)
**Proposed:** 2026-11-27
**Proposed by:** 🏗️ Winston
**Approver:** S1408661 (Engineering Lead)
**Status:** PROPOSED. No code, no ADR edited.
**Depends on:** the founder's decision that Atlas hosts prize imagery (taken 2026-11-27).

---

## 0. A correction this proposal rests on

I told the founder the prize description was "committed before entries open", in a way that implied the commit-reveal commitment covers it. **It does not.**

```python
commitment = hashlib.sha256(server_seed + draw_id.bytes).hexdigest()
```

The commitment covers the **server seed and nothing else** — that is its whole job under ADR-006, and it is correct as designed. `prize_copy` is made tamper-evident by a different mechanism entirely: it sits in the `draw.committed` audit event, and ADR-005's hash chain is what prevents it being altered afterwards.

The conclusion is unchanged. The design is much cheaper, and it belongs in a different ADR.

---

## 1. The problem

The prize photograph will be the single most persuasive element on the draw card — more persuasive than the price or the copy. It is part of the offer.

**Nothing makes it tamper-evident.** An operator can publish a draw showing a 2026 Corolla, sell entries for a week, and replace the image file before the reveal. The audit chain records `prize_copy`; it records nothing about the image. The published proof says nothing about it either. A disgruntled entrant has no way to show what they were actually shown.

This is not an exotic attack. It is the obvious one for a prize platform, and it is the kind of thing a State regulator asks about during licensing.

The gap exists today only because there is no imagery. The moment the founder's hosting decision is implemented, it becomes live.

---

## 2. Why this is NOT an ADR-006 amendment

My first instinct was to fold the image hash into the commitment. That instinct was wrong, and I want the reasoning recorded so nobody re-proposes it:

- **The commitment covers the server seed because that is the secret.** Commit-reveal exists to prove the operator could not have known the winner in advance. Mixing unrelated material into it muddies a protocol whose legibility is the point.
- **It would change what every existing proof asserts.** The verifier CLI reproduces winner selection from published inputs; altering the commitment's preimage forces a versioned proof format and a verifier that understands both.
- **The image may not exist at draw creation.** The commitment is computed at creation. Requiring imagery before a draw can exist couples two unrelated things.
- **ADR-005 already solves this exact problem.** `prize_copy` is protected by the chain, not the commitment. The image hash wants identical treatment.

**ADR-006 needs no amendment. The protocol is correct as it stands.**

---

## 3. Proposed change — ADR-005 §Event catalogue

Add to the `draw.committed` payload:

```
prize_image_sha256   — SHA-256 of the image bytes as served, or null
prize_image_url      — the canonical URL the bytes are served from
```

Computed **on upload**, over the bytes Atlas stores, before any derivative is generated. The hash covers the original; derivatives are deterministic from it.

**Invariant:** the image a draw was sold with is the image whose hash sits in that draw's `draw.committed` row. Replacing it after publication requires a new `draw.image_replaced` event carrying both hashes and an operator id — visible, attributable, and never silent.

### 3.1 Surfaced on the public proof

The proof page already presents hashes as first-class typography (tone-doc Anchor 3, the Coinbase treatment). The prize-image hash belongs there, alongside the commitment and `tickets_hash`, with the same copy-to-clipboard affordance.

Anyone can then fetch the image and verify the digest themselves — the same shape of claim the verifier CLI already makes about the winner.

### 3.2 Null is legitimate and must stay legitimate

Draws without imagery exist today and will keep existing. `prize_image_sha256: null` is a valid payload, not a defect, and the proof page must render that case without implying something is missing.

---

## 4. What this buys, in order of weight

1. **A verifiable answer to "that is not the car you advertised."** Today Atlas has none.
2. **Consistency of posture.** A platform whose entire positioning is "verify everything yourself" should not have its most persuasive element be the one unverifiable thing on the page.
3. **A regulator-facing answer** on misleading-advertising exposure (counsel Q5), which Adaeze already flags as live.
4. **It is nearly free.** One hash at upload, two fields in a payload that is already chained, one row on a page already built to display hashes. No protocol change, no verifier change, no migration of existing proofs.

---

## 5. What it does not buy

- It does not prove the photograph depicts the actual prize. It proves the image was not swapped after publication. Stock photography of *a* Corolla rather than *the* Corolla is a disclosure question for Adaeze, not a cryptographic one.
- It does not prevent an operator changing the image — only from doing so invisibly.

---

## 6. Dependency and sequencing

Strictly downstream of imagery existing at all. Per `prize-photography-scope.md` §3 that is behind the platform choice, which is behind Phase 0, which is behind the licence.

**But it must be designed in now, not retrofitted.** Hashing on upload is trivial when the upload endpoint is being written and awkward afterwards — and a backfill cannot hash images for draws that have already closed. The cost of deciding this late is permanently unverifiable history.

---

## 7. Action

1. **Founder** — approve in principle, so the upload work in `prize-photography-scope.md` §4 row C is built with hashing from the first commit.
2. ⚖️ **Adaeze** — §5's first bullet is yours: what must the draw page say about whether the photograph is the actual prize?
3. 🏗️ **Winston** — on approval, amend ADR-005 §Event catalogue and add the invariant to its retention rules. ADR-006 untouched.

— 🏗️ Winston
