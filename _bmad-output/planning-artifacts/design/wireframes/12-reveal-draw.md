# Wireframe 12 — Reveal Draw (operator surface)

**Drafted:** 2026-07-08 (Day 9 per `tone-doc.md §8`)
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** Draft — pending founder review + ⚖️ Adaeze compliance review. Third and highest-stakes operator ceremony (after create in wf-09 and close in wf-11). **This is the admin-side of the wow moment** — the public-facing proof page (wf-14, Day 11) is where the same information lands for consumers and third parties.
**Covers:** Flagship flow step 12 from `v0.5-demo-plan.md §2` — *"Reveal draw — button (at scheduled reveal time; can be manually triggered in demo). Public entropy fetched (Bitcoin block + drand), server seed revealed, winner selected deterministically, published."*
**Surface:** Next.js admin, inside the shell (wf-08 §1).
**Pairs with:** `09-create-draw.md`, `10-transcribe-free-entry.md`, `11-close-and-reveal-draw.md`, `13-audit-log-admin.md` (Day 10 — where the reveal event lives), the future `14-public-proof-page.md` (Day 11 — where this admin action's output is consumer-verifiable), ADR-006 (protocol stages 4 and 5 — Reveal and Audit/replay).

---

## 0. The stakes on this screen

At create, Atlas committed to a set of parameters. At close, Atlas fixed the pool. Here, Atlas selects the winner using inputs anyone can verify. If any of this doesn't hold — if the entropy fetch fails, if the algorithm output can't be reproduced, if the winner ticket doesn't map to a real person — the trust story breaks *publicly*, at the most-watched moment of the draw lifecycle.

Design implications:

1. **The reveal is not a single button.** It is a *ceremony* — a sequence of steps that fetch, verify, compute, and publish. Each step is visible; each step can be paused or retried if something looks off; nothing runs invisibly. The operator is the ceremonial officiant, not a button-pusher.
2. **The operator sees exactly what will be published** before it is published, one more time. Same review discipline as create.
3. **If the entropy fetch produces mismatched values across sources** (Bitcoin block hash from explorer A doesn't match explorer B; drand signature fails verification), reveal must **halt** and surface an actionable error, not silently retry or silently pick one source. This is a hard invariant.
4. **The winner is not "announced" in the same tap as "computed."** Compute produces a candidate result; a separate publish step commits it. This prevents an accidental publish of a compute that went wrong.

**Non-goals for V0.5:**
- Automatic reveal at scheduled time. V0.5 uses manual operator-triggered reveal (per plan §2 step 12 wording).
- Multi-operator ceremony (e.g. two operator sign-off for reveal). V1 concern — potentially real for large prizes.
- Live-stream integration (video ceremony broadcast). Deferred to V2 flagship-draw treatment per delivery-framework §11.
- Multi-winner reveals (multiple simultaneous prizes). V0.5 is one prize per draw.

---

## 1. Where in the shell

Sidebar → **OPERATE → Draws → {awaiting-reveal draw}** → the draw detail page → *Reveal draw* action.

Prerequisites: draw is in the `awaiting_reveal` state (set by wf-11 close). Reveal can be manually triggered any time at or after the scheduled reveal time (V0.5 permits early-reveal for demo purposes via the wf-11 §4.1 shortcut; V1 removes that shortcut).

---

## 2. Screen 12.1 — Pre-reveal review

### 2.1 Layout

```
< inside admin shell >

  ← Back to draw

  Reveal draw

  You're about to run the reveal ceremony for the                ← body.default primary
  ₦2,000,000 in cash draw. This is the last operator step
  before the winner is public.

  space.800

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ COMMITMENTS ALREADY PUBLISHED                          │  ← summary card
  │                                                          │      surface.elevated
  │                                                          │      radius.large
  │  Commitment hash                                          │      elevation.0
  │  3f2c4b8e9a...8a91                    📋 Copy full hash  │
  │  Committed 08 Jul 2026, 13:47:52 WAT                      │
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  Tickets hash                                             │
  │  a7b3e9f1c2...4d82                    📋 Copy full hash  │
  │  Closed 12 Jul 2026, 19:58:14 WAT                         │
  │  1,247 tickets · 1,160 paid · 87 free-route              │
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  Reveal scheduled at    13 Jul 2026, 21:00 WAT            │
  │  Now                    13 Jul 2026, 21:04:12 WAT         │
  └──────────────────────────────────────────────────────────┘

  space.600

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ REVEAL CEREMONY — 5 STEPS                              │
  │                                                          │
  │  ○  1. Fetch Bitcoin block hash                           │  ← StepList — new component
  │       Source: 2 independent explorers, values must match. │      each step has a state
  │       Target: block whose timestamp ≥ sales-close time.   │      indicator (○ pending,
  │                                                          │      ⋯ running, ✓ success,
  │  ○  2. Fetch drand round                                  │      ⚠ blocked)
  │       Source: League of Entropy public endpoint,          │
  │       signature verified against group public key.        │      before Start:
  │       Target: round whose epoch ≥ sales-close time.       │      all ○
  │                                                          │
  │  ○  3. Decrypt server seed                                │
  │       Retrieved from secret manager, worker-only access.  │
  │                                                          │
  │  ○  4. Compute winner + reserves                          │
  │       prng_seed = HMAC-SHA-256(server_seed,               │  ← body.mono inline
  │         bitcoin_hash || drand_round || tickets_hash)      │      the algorithm reference
  │       Iterate to select 1 primary + 5 reserves.           │      visible even on this
  │                                                          │      surface — the trust story
  │  ○  5. Publish                                            │      is not opaque to the
  │       Winner ticket, reserves, server seed, entropy       │      operator either
  │       inputs, algorithm reference all written to draw     │
  │       record, audit log, consumer page, and /proof.       │
  │                                                          │
  │  ⓘ Steps 1-4 can be retried on failure. Step 5 is         │  ← body.small secondary
  │    one-way — once published, the reveal is final.         │
  └──────────────────────────────────────────────────────────┘

  space.1200

  [ Cancel ]                                   [  Start ceremony  ]
                                                  ↑ primary button
                                                    attention-tinted background hint
                                                    (per wf-09 §5.4 pattern)
```

### 2.2 Components used

- `AdminPageHeader`.
- `CommitmentSummaryCard` — new; the "COMMITMENTS ALREADY PUBLISHED" card. Shows the commit hash + close hash, both with copy affordances, timestamps, and entry counts. **This card makes the trust story auditable to the operator too** — they see what has been sealed before they seal the next artefact.
- `StepList` — new; the 5-step ceremony component. Each step has: leading state icon (`○` pending / `⋯` running / `✓` success / `⚠` blocked / `⌀` refused), step title, and body text describing what happens.
- `Button` (primary + secondary).
- `InlineLink`.

### 2.3 States

**Default:** as drawn. All 5 steps in `○` pending state. Start ceremony enabled.

**Cancel:** returns to draw detail page. Ceremony not started.

**Start tapped:** transitions to Screen 12.2 — the ceremony running state.

### 2.4 Copy

| Element | Copy |
|---|---|
| Back link | ← Back to draw |
| Headline | Reveal draw |
| Context | You're about to run the reveal ceremony for the {prize} draw. This is the last operator step before the winner is public. |
| Commitments eyebrow | COMMITMENTS ALREADY PUBLISHED |
| Commitment hash label | Commitment hash |
| Commitment context | Committed {commit_time} |
| Tickets hash label | Tickets hash |
| Tickets context | Closed {close_time} / {total} tickets · {paid} paid · {free} free-route |
| Scheduled label | Reveal scheduled at / {scheduled_reveal} |
| Now label | Now / {now} |
| Ceremony eyebrow | REVEAL CEREMONY — 5 STEPS |
| Step 1 title | Fetch Bitcoin block hash |
| Step 1 body | Source: 2 independent explorers, values must match. Target: block whose timestamp ≥ sales-close time. |
| Step 2 title | Fetch drand round |
| Step 2 body | Source: League of Entropy public endpoint, signature verified against group public key. Target: round whose epoch ≥ sales-close time. |
| Step 3 title | Decrypt server seed |
| Step 3 body | Retrieved from secret manager, worker-only access. |
| Step 4 title | Compute winner + reserves |
| Step 4 body | `prng_seed = HMAC-SHA-256(server_seed, bitcoin_hash \|\| drand_round \|\| tickets_hash)` — Iterate to select 1 primary + {N} reserves. |
| Step 5 title | Publish |
| Step 5 body | Winner ticket, reserves, server seed, entropy inputs, algorithm reference all written to draw record, audit log, consumer page, and /proof. |
| Steps note | Steps 1-4 can be retried on failure. Step 5 is one-way — once published, the reveal is final. |
| Cancel CTA | Cancel |
| Start CTA | Start ceremony |

---

## 3. Screen 12.2 — Ceremony running

Same layout as Screen 12.1, with the StepList animated live as each step completes. As each step transitions from `○` → `⋯` → `✓`, the body of that step gains a small **result summary** below the description.

### 3.1 Example — mid-ceremony (Steps 1-3 complete, Step 4 running)

```
  ┌──────────────────────────────────────────────────────────┐
  │  ▪ REVEAL CEREMONY — RUNNING                              │
  │                                                          │
  │  ✓  1. Fetch Bitcoin block hash                           │  ← state.success tick
  │       Block #856,142 · 13 Jul 2026, 20:18:44 WAT          │      body.small secondary
  │       Hash 8f1c...9e42     📋                             │      body.mono inline
  │                                                          │
  │  ✓  2. Fetch drand round                                  │
  │       Round #4,829,301 · 13 Jul 2026, 20:14:52 WAT        │
  │       Signature verified against group public key ✓        │
  │       Randomness 3b7d...0c88     📋                       │
  │                                                          │
  │  ✓  3. Decrypt server seed                                │
  │       Server seed retrieved.                              │
  │       Preview: 9e01...4c67  (revealed to public in Step 5)│
  │                                                          │
  │  ⋯  4. Compute winner + reserves                          │  ← state ⋯ running
  │       Computing...                                        │      soft spinner
  │                                                          │
  │  ○  5. Publish                                            │
  │       Winner ticket, reserves, ...                        │
  └──────────────────────────────────────────────────────────┘

  ⋯ Ceremony in progress — do not close this window.
```

### 3.2 State transitions

- Steps 1-4 run automatically once Start is tapped. No further operator interaction until Step 4 completes.
- Between Step 4 and Step 5, the ceremony **pauses**. The winner has been computed but not published. The operator is invited to review the candidate outcome before committing (§4).
- If any of Steps 1-4 fails, that step transitions to `⚠` blocked; a retry button appears inline; the ceremony holds. If the operator taps retry, the failed step re-runs.
- Refusal states (a step's inputs violate an invariant — e.g. Bitcoin explorer A and explorer B return different hashes for the same block) transition to `⌀` refused and require operator investigation. Retry is not offered; the operator's next action is to inspect the source data and, if necessary, cancel the ceremony (§7).

### 3.3 Step-specific error handling

| Step | Failure | Behaviour |
|---|---|---|
| 1 | One or both Bitcoin explorers unreachable | State `⚠`, retry available. Copy: *"Bitcoin explorer {X} unreachable. Check connection and retry."* |
| 1 | Two explorers return different hashes for the same block | State `⌀`, no retry. Copy: *"Bitcoin explorers returned different hashes for block #{n}. This is a critical mismatch — do not proceed. Investigate before continuing."* Link to a runbook (docs/runbooks/draw-entropy-unavailable.md). |
| 2 | drand endpoint unreachable | State `⚠`, retry. |
| 2 | drand signature verification fails | State `⌀`, no retry. Runbook link. |
| 3 | Secret manager unreachable | State `⚠`, retry. |
| 4 | Compute fails (should be impossible if all inputs present) | State `⌀`, no retry. Escalate to engineering. |

---

## 4. Screen 12.3 — Candidate winner review

Renders once Step 4 completes and before Step 5 publishes.

### 4.1 Layout

```
< inside admin shell >

  Reveal draw · Ceremony paused · Ready to publish

  space.400

  ●●●●○   Candidate outcome computed. Review, then publish.

  space.800

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ CANDIDATE WINNER                                       │  ← surface.elevated,
  │                                                          │      radius.large,
  │                                                          │      elevation.1,
  │  Ticket 04829                                             │  ← body.mono 40pt
  │                                                          │      color.text.primary
  │  ─────────────────────────────                            │
  │                                                          │
  │  Purchased by            Chinelo Okonkwo                  │
  │  Contact                 +234 803 000 0000 ·              │
  │                          chinelo@example.com              │
  │  Entry source            Paid                             │
  │  Purchased at            08 Jul 2026, 14:23 WAT           │
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  Self-exclusion register — not present.                   │  ← ADR-010 check confirming
  │  KYC status               Not yet completed               │      the operator sees this
  │  Prior claim history      None                            │      before publish
  └──────────────────────────────────────────────────────────┘

  space.400

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ RESERVES (in order)                                    │
  │                                                          │
  │  1. Ticket 07213 — Adaobi Umeh (paid)                    │  ← body.default rows
  │  2. Ticket 00042 — Ifeoma Nwosu (free-route)             │      body.small secondary
  │  3. Ticket 03917 — Chidi Adebayo (paid)                  │      for entry source
  │  4. Ticket 06104 — Kemi Balogun (paid)                   │
  │  5. Ticket 01288 — Musa Idris (free-route)               │
  │                                                          │
  │  ⓘ Reserves are drawn in this order if the primary        │  ← body.small secondary
  │    winner fails KYC or declines.                          │
  └──────────────────────────────────────────────────────────┘

  space.400

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ REPLAY VERIFICATION                                    │
  │                                                          │
  │  Inputs used:                                             │  ← definition list
  │  server_seed          9e014b7d...4c67 (32 bytes)          │      body.mono
  │  bitcoin_hash         8f1c3e9f...9e42                     │
  │  drand_round          3b7d02a4...0c88                     │
  │  tickets_hash         a7b3e9f1...4d82                     │
  │                                                          │
  │  Algorithm: HMAC-SHA-256(server_seed,                     │
  │             bitcoin_hash || drand_round || tickets_hash)  │
  │  → deterministic PRNG stream                              │
  │  → mod-N indexing over 1,247-ticket pool                  │
  │                                                          │
  │  ✓ Local verifier reran the algorithm and produced        │  ← state.success chip
  │    the same result: Ticket 04829.                         │
  │                                                          │
  │  [ Download proof package (JSON) ]                        │  ← button
  │                                                          │
  │  The proof package is what the public /proof endpoint     │  ← body.small secondary
  │  will publish. Verify it locally before publish, if you   │
  │  want extra assurance.                                    │
  └──────────────────────────────────────────────────────────┘

  space.1200

  [ Cancel ceremony ]                            [ Publish winner ]
                                                    ↑ primary
                                                      attention-tinted
```

### 4.2 Components used

- `AdminPageHeader` (with paused-state modifier — different eyebrow language).
- `CandidateWinnerCard` — new; the profile of the ticket that came out of Step 4. Shows entrant identity + contact + entry source + timestamp + **self-exclusion register check** + KYC status + prior claim history. **The self-exclusion check on this card is the belt-and-braces ADR-010 enforcement** — even though ADR-010 §2 says self-exclusion is checked at KYC, checking again at reveal ensures a race condition can't slip a self-excluded winner into publish.
- `ReservesList` — new; ordered list of the K reserves per ADR-006 §Reserve algorithm.
- `ReplayVerificationCard` — new; the algorithm inputs + verification result. This is the operator's own local check that the ceremony produced a reproducible result *before* publishing. **This card is the most important pre-publish surface** — it's where a bug would show as a mismatch and the operator would halt.
- `Button` (primary + secondary — with `Cancel ceremony` on secondary).
- `InlineLink`.

### 4.3 States

**Default (as drawn):** all cards populated, replay verification passed, Publish enabled.

**Replay verification failed:** the ReplayVerificationCard shows an error state — this is a critical bug. Publish disabled. Cancel becomes the only action. Copy: *"The local verifier could not reproduce the winning ticket. Do not publish. Cancel the ceremony and file a critical incident."*

**Winner is self-excluded (belt-and-braces check surfaces a match):** CandidateWinnerCard shows the self-excluded state. Publish disabled. Ceremony must be cancelled and re-computed after clearing the state or with an ADR-010-compliant substitution (this is a rare edge case; if it happens the runbook applies).

**Publish tapped:** opens modal 12.4.

**Cancel ceremony tapped:** confirmation modal *"Cancel this reveal? Nothing has been published. The ceremony can be re-started."* Confirm returns to Screen 12.1 with all step states cleared. **Cancelled ceremonies do write an audit-log event** (`draw.reveal_cancelled` with a reason field) — cancellation is visible on the audit trail even though nothing was published.

### 4.4 Copy

| Element | Copy |
|---|---|
| Page eyebrow | Reveal draw · Ceremony paused · Ready to publish |
| Progress label | Candidate outcome computed. Review, then publish. |
| Winner eyebrow | CANDIDATE WINNER |
| Winner ticket | Ticket {ticket_number} |
| Winner purchased by | Purchased by / {name} |
| Winner contact | Contact / {phone_e164} · {email} |
| Winner entry source | Entry source / Paid   (or Free-route) |
| Winner purchased at | Purchased at / {timestamp} |
| SE check | Self-exclusion register — not present.   (or: — present ⚠) |
| KYC status | KYC status / {status} |
| Prior claims | Prior claim history / {summary} |
| Reserves eyebrow | RESERVES (in order) |
| Reserve row | {n}. Ticket {number} — {name} ({source}) |
| Reserves note | Reserves are drawn in this order if the primary winner fails KYC or declines. |
| Verification eyebrow | REPLAY VERIFICATION |
| Verification inputs heading | Inputs used: |
| Verification algorithm | Algorithm: HMAC-SHA-256(server_seed, bitcoin_hash \|\| drand_round \|\| tickets_hash) → deterministic PRNG stream → mod-N indexing over {N}-ticket pool |
| Verification passed | ✓ Local verifier reran the algorithm and produced the same result: Ticket {ticket_number}. |
| Verification failed | ⚠ Local verifier could not reproduce the winning ticket. Do not publish. Cancel the ceremony and file a critical incident. |
| Download proof | Download proof package (JSON) |
| Proof note | The proof package is what the public /proof endpoint will publish. Verify it locally before publish, if you want extra assurance. |
| Cancel ceremony CTA | Cancel ceremony |
| Cancel ceremony confirm | Cancel this reveal? Nothing has been published. The ceremony can be re-started. |
| Publish CTA | Publish winner |

---

## 5. Modal 12.4 — Publish winner confirmation

Same type-to-confirm pattern as wf-09 §6 and wf-11 §3.

### 5.1 Copy

| Element | Copy |
|---|---|
| Eyebrow | CONFIRM PUBLISH WINNER |
| Headline | Publish this winner? |
| Body 1 | You're about to publish the reveal for: |
| Body 2 (dynamic) | Ticket {ticket_number} — {name} — {prize} |
| Body 3 | Once published, the winner is visible on the consumer surface, in the audit log, and at the public /proof endpoint. The winner will receive an in-app notification and an email within one minute. |
| Type-to-confirm | Type REVEAL to confirm: |
| Confirm CTA | Publish winner |
| Confirm loading | Publishing… |
| Cancel | Cancel |
| Fail | Publish didn't complete. Try again in a moment. Nothing has been published. |

Mechanics identical to prior confirmation modals (focus trap, backdrop = cancel, escape dismisses, idempotency-keyed POST).

**The type-to-confirm word is `REVEAL`** — completes the three-word ceremony vocabulary: `PUBLISH` (commit at create), `CLOSE` (freeze pool at close), `REVEAL` (announce winner at reveal).

---

## 6. Screen 12.5 — Reveal receipt (post-publish)

### 6.1 Layout

```
< inside admin shell >

                                                    space.1200

                        ✓                            ← 48pt gold check

                Winner published.                    ← type.display.section, centered

  Ticket 04829 — Chinelo Okonkwo — ₦2,000,000        ← body.default primary

                                                    space.1200

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ REVEAL RECEIPT                                         │  ← surface.elevated
  │                                                          │
  │  Draw ID                DRAW-2026-07-08-A                │
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  Winner ticket          04829                             │
  │  Purchased by           Chinelo Okonkwo                   │
  │  Entry source           Paid                              │
  │  Prize                  ₦2,000,000 in cash                │
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  Revealed at            13 Jul 2026, 21:06:41 WAT         │
  │  Revealed by            Adaobi Ibe (operator)             │
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  Verifiable inputs:                                       │  ← definition list, body.mono
  │  Commitment hash        3f2c...8a91                       │
  │  Tickets hash           a7b3e9f1...4d82                   │
  │  Server seed (revealed) 9e014b7d...4c67                   │
  │  Bitcoin block          #856,142                          │
  │  Bitcoin hash           8f1c3e9f...9e42                   │
  │  drand round            #4,829,301                        │
  │  drand randomness       3b7d02a4...0c88                   │
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  Published to:                                            │
  │  · Consumer draw page — atlas://draw/{draw_id}            │
  │  · Consumer notifications — {n} entrants notified         │
  │  · Winner notification — sent 21:06:44 WAT                │
  │  · Audit log — event `draw.revealed` #5012                │
  │  · Audit log — event `draw.winner_selected` #5013         │
  │  · Public /proof endpoint — atlas.ng/proof/{draw_id}      │
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  [ Download proof package (JSON) ]                        │
  │  [ Copy verifier command ]                                │  ← copies to clipboard:
  │                                                          │      python -m atlas.verify \
  │                                                          │        --proof {proof_url}
  └──────────────────────────────────────────────────────────┘

  space.800

  ┌────────────────────────┐  ┌──────────────────────────┐
  │  Go to draw page  →    │  │  View audit log  →       │
  └────────────────────────┘  └──────────────────────────┘

  space.400

  Reveal complete. The claim flow (wf-07) is now active         ← body.small secondary
  for the winner.                                                  centred
```

### 6.2 Notes

- **Copy verifier command** — a small but important operator affordance. Copies to clipboard the exact command line to run the standalone verifier script from ADR-006 §Audit/replay against the public /proof endpoint. This is what the operator hands to a regulator or auditor who wants to independently verify.
- **Notification counts** — the receipt shows how many notifications went out (winner + non-winners). If notifications fail (Mailhog error, push service down in V1), the receipt shows the failure count and a retry option.
- **Operator identity** is now permanently recorded on the audit-log event. This is the audit-trail commitment made in wf-10 §4.5 — every consequential admin action carries operator attribution.

### 6.3 States

**Success (as drawn):** everything published, notifications sent.

**Publish succeeded, notification partial failure:** receipt shows warning: *"{n}/{total} notifications sent. {failed_count} failed."* with a Retry link. Winner notification is always retried first.

---

## 7. Failure and recovery states across the ceremony

Summarising because reveal has more failure modes than any other operator surface.

| Failure | State | Recovery |
|---|---|---|
| Bitcoin explorer unreachable | Step 1 `⚠` | Retry (network transient) |
| Bitcoin explorers disagree | Step 1 `⌀` | Halt. Runbook. Investigate before retrying. |
| drand endpoint unreachable | Step 2 `⚠` | Retry |
| drand signature invalid | Step 2 `⌀` | Halt. Runbook. |
| Secret manager unreachable | Step 3 `⚠` | Retry |
| Compute exception | Step 4 `⌀` | Halt. Engineering escalation. |
| Winner is self-excluded | Screen 12.3 blocked | Cancel ceremony; runbook. |
| Replay verification failed | Screen 12.3 blocked | Cancel ceremony; critical incident. |
| Publish call failed mid-way (partial write) | Modal shows partial failure | Retry (idempotency-keyed). |
| Notification partial failure | Receipt warning | Retry from receipt. |

Runbook link: `docs/runbooks/draw-entropy-unavailable.md` (exists per initial scaffold; Tobi owns the content).

---

## 8. Design invariants for reveal

1. **Compute and publish are separate operator actions.** No single tap runs the algorithm and commits the result.
2. **Replay verification runs on the operator surface before publish.** If the local verifier can't reproduce the winner, publish is refused.
3. **Entropy-source mismatches halt with no retry.** Two Bitcoin explorers disagreeing is a critical event, not a retryable one.
4. **Self-exclusion is checked twice — at KYC-time (ADR-010) and at reveal-time.** Belt and braces.
5. **The ceremony can be cancelled at any point before publish, and cancellation is auditable.** Silent cancellation would defeat the audit trail.
6. **Publish emits the same proof package the public /proof endpoint publishes.** No divergence between what the operator sees and what the world sees.
7. **The verifier command is one-tap from the receipt.** Anyone reading the receipt can independently verify in seconds.

---

## 9. Open questions

### For founder:
1. **Ceremony pacing.** Currently Steps 1-4 run automatically once Start is tapped, then pause for review before publish. Alternative: manual step-through (operator confirms each step). Recommend current — the pause between compute and publish is the meaningful gate.
2. **Verifier command in the receipt.** The `python -m atlas.verify ...` string is engineer-flavoured. Investors won't run it; operators might. Founder — do you want this on the admin surface or is it engineering-only?
3. **Contact info visibility on §4 CandidateWinnerCard.** The operator sees the winner's phone + email pre-publish. Necessary for operational reasons (contact for KYC follow-up) but a PII-exposure surface. Confirm.

### For ⚖️ Adaeze:
4. **Self-exclusion belt-and-braces check on §4 §8.4.** Is the second check at reveal-time (in addition to ADR-010 §2 KYC-time enforcement) sufficient, or should the reveal ceremony perform additional compliance checks?
5. **The `draw.reveal_cancelled` audit event** (§4.3) — is that the right event name and is the reason field a required attestation, or free text?
6. **Verifier command in receipt copy** — should the exact command reference documentation for how a third party runs it? (Currently just the raw command; assumes reader knows.)
7. **Notification partial failure** (§6.3). If we send 1,247 notifications and 3 fail, does the audit log record a `notification_failed` event per failure, or a single summary event? Adaeze's rule of thumb on audit-event granularity.
8. **Reveal receipt PII.** The receipt shows the winner's full name on the operator surface. Is that acceptable given the audit-trail is Atlas-internal (not public)?

### For 💻 Amelia:
9. **Ceremony as a state machine** — is the flow `pre_review → step_1 → step_2 → step_3 → step_4 → paused_for_publish → publishing → published` an accurate model? Retry-able states carry a retry count; the halt states are terminal for this ceremony instance (a new instance can be started from scratch).
10. **Replay verifier on the operator surface** — the client re-runs the verifier locally (using the ADR-006 algorithm) and compares to server-computed result. This is an extra layer of defense — a compromised server can't publish a fabricated winner if the operator's client independently computes a different result. Confirm this is buildable.
11. **Proof package JSON schema.** Fields: `draw_id`, `commitment_hash`, `tickets_hash`, `server_seed` (revealed), `bitcoin_block_height`, `bitcoin_hash`, `drand_round`, `drand_randomness`, `winning_ticket_id`, `reserve_ticket_ids` (ordered), `algorithm_reference` (URL to a versioned spec), `revealed_at`, `audit_event_ids`. Confirm.
12. **Notification sender.** V0.5 Mailhog per plan §4; V1 needs a real email vendor. The retry logic on notification failure should tolerate partial success and re-fire only the failed ones (idempotent by recipient).

### For 🛡️ Tobi:
13. **Runbook — `docs/runbooks/draw-entropy-unavailable.md`.** Needs to explicitly cover the two-explorer-disagreement scenario and the drand-signature-invalid scenario. Both are hard-halt cases requiring investigation before retry.
14. **Secret manager access pattern** for server-seed decryption (§Step 3). Which service can decrypt, under what conditions, and how is the access audited.

---

## 10. Cross-references

- Flow source: `v0.5-demo-plan.md §2` (step 12).
- Upstream: `09-create-draw.md` (commit), `11-close-and-reveal-draw.md` (close), `10-transcribe-free-entry.md` (free-route pool contents).
- Downstream: `13-audit-log-admin.md` (Day 10 — the audit-log view where these events live), `14-public-proof-page.md` (Day 11 — the consumer/public version of the same proof).
- Consumer counterpart: `02-browse-active-draw.md §3.3` revealed state, `06-draw-completes-notification.md §3` reveal page.
- Runbook: `docs/runbooks/draw-entropy-unavailable.md` (Tobi).
- ADR-006 §Protocol stages 4 and 5 — this screen's exact reason to exist.
- Compliance review: `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md` (Adaeze) — audit-log invariants inform every visible field on §6 receipt.
- Tokens: `tokens.md`.

---

🎨 *End of wireframe 12. Day 9 complete.*

*Day 9 delivered wireframes 10 (transcribe free entry — parity invariant), 11 (close draw — tickets_hash publication), 12 (reveal draw — the ceremony). The three commit-reveal artefacts (commitment_hash, tickets_hash, revealed_seed) all now have their operator surfaces designed. Day 10 is the audit-log admin view where these events live. Day 11 is the public proof page — the wow moment where all three artefacts land as public evidence and where anyone can independently verify.*

*Nine days into a two-week pass. On schedule. **Adaeze — wf-10 flagged for you as a working-draft review; wf-11 and wf-12 also welcome your pass whenever.** Founder — the reveal ceremony (wf-12) is the most operator-critical thing I've drawn; would be useful to walk through it with you before Day 11 begins.*
