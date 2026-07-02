# Runbook: Draw entropy source unavailable at reveal time

**Severity:** SEV-2 (SEV-1 if reveal window closes without action)
**Owner:** on-call engineer (human) → EL + Compliance Lead on any postponement
**Last verified:** 2026-07-01 by 🛡️ Tobi (drafted)
**Applies to:** the commit-reveal draw protocol per ADR-006. Combined public entropy = Bitcoin block hash (at close time) + drand round (at close time).
**Related:** R-VEN-06 (🟢 low but consequential), ADR-006.

## Symptoms

- The draw engine's reveal job is unable to fetch either the required Bitcoin block hash or the required drand round at the scheduled reveal time.
- Alert fires: `DRAW_ENTROPY_UNAVAILABLE` → SEV-2 (auto-escalates to SEV-1 after 30 minutes with no resolution).
- A draw is stuck in `awaiting_reveal` state past its scheduled reveal time.

## Detection

- **Automated:** the reveal job runs at the draw's scheduled `reveal_at` time; if entropy sources fail, the job pauses and emits the alert instead of proceeding.
- **Manual:** operator observes a draw stuck past its reveal time in the admin dashboard.

## Impact

- **Users:** see the draw page still showing "awaiting reveal" — trust event if unexplained.
- **Draw:** cannot complete until entropy is available OR the reveal is postponed to a later slot with fresh entropy inputs.
- **Compliance:** any postponement is audit-logged. Postponement without transparency is a trust event; with transparency, it's a manageable operational moment.
- **Money:** no money at direct risk — reveal happens *after* sale close, so the prize pool is fixed.

## Diagnosis steps

1. **Confirm which source(s) failed.** Reveal job logs identify the source: `bitcoin` (via configured block explorer endpoints) or `drand` (via drand League of Entropy public endpoint).
2. **Check external status:**
   - Bitcoin: try 3 independent block explorers (blockstream.info, mempool.space, blockchain.info). If all 3 fail, Bitcoin network itself may be degraded (extremely rare) or Atlas's egress is blocked.
   - drand: https://drand.love/ status; check `curl -sf https://api.drand.sh/public/latest`.
3. **Determine failure mode:**
   - **Transient network issue** — retries typically succeed within minutes. Reveal job retries automatically for 15 minutes before escalating.
   - **Source-side outage** — a single source down is tolerable (per ADR-006 the requirement is *both* sources at close time; if one is temporarily unavailable at reveal time, we wait for it to recover — the *commitment* is to the entropy *at close time*, and that data may still be retrievable once the source recovers).
   - **Historical-data unavailability** — the block or round we need may have been finalised but a specific explorer's history is unavailable; try alternate explorers.
   - **Data disagreement** — two explorers return different values for the same block. This is the "hard fail" scenario — do not proceed with reveal until resolved.
4. **Check how much time is left in the reveal window.** Draws have a target reveal-time but the actual reveal can slip within a defined tolerance (default: 4 hours). Beyond tolerance → postponement.

## Mitigation steps

### For a transient / short outage (< 30 minutes)

1. Let the reveal job retry (auto). Monitor.
2. Post a brief "reveal delayed by a few minutes" notice on the draw page if the delay is user-visible (> 5 minutes past scheduled).
3. Once entropy is available, the reveal job proceeds automatically. Verify:
   ```
   platform run --env production --service backend -- \
     python -m atlas.scripts.draw_state --draw-id $DRAW_ID
   ```
   State should transition `awaiting_reveal` → `revealed`.

### For an extended outage requiring postponement

1. **Decision to postpone requires EL + Compliance Lead approval.** Do not act unilaterally.
2. **Choose new reveal time.** Recommendation: the scheduled reveal time + 24 hours, at the same hour, to preserve pattern. The new entropy inputs will be:
   - Bitcoin block hash at the *original close time* — this doesn't change; we're waiting for the source to become available, not changing the commitment.
   - drand round at the *original close time* — same.
   - Server seed — unchanged from commit; still sealed.
3. **Postpone via operator action** in the admin app: `Draws → [draw] → Postpone reveal → [new time] → [reason]`. This action:
   - Writes an audit-log entry `draw.reveal_postponed` (immutable per ADR-005).
   - Updates the draw page with new reveal time and a plain-language reason ("Our public entropy source is temporarily unavailable; the reveal has been rescheduled. The draw's commitment hash and ticket list remain unchanged.").
   - Sends a WhatsApp broadcast + email to all entrants for that draw.
4. **Do NOT change any of:**
   - The commitment hash (published at draw creation — cannot change without breaking provably-fair guarantee).
   - The `tickets_hash` (published at close — cannot change).
   - The chosen entropy source or algorithm (would break replayability).

### For data-disagreement between explorers (Diagnosis step 3, hard fail)

1. **Immediate escalation** to EL + Compliance Lead — this is a trust-critical scenario.
2. Investigate why explorers disagree — most likely a chain reorganisation window on Bitcoin (rare beyond the first few blocks). If reorg is in progress, wait for the affected block to have ≥ 6 confirmations before proceeding.
3. If disagreement persists beyond 24 hours, this is exceptional — consult ADR-006 §Consequences and consider emergency Compliance guidance on the specific draw.

## Rollback steps

If a reveal proceeded with wrong entropy inputs (should not happen — the algorithm verifies inputs before executing — but for completeness):

1. This would be a SEV-1 trust incident. Halt further draws.
2. Publish full transparency about the incident on the draw page.
3. Compliance & Risk Agent determines the corrective action per ADR-006 replay procedure — typically re-running the algorithm with correct inputs and honouring both outcomes (compensating the original announced winner if different from re-run winner, at operator discretion).
4. Post-mortem + amendment to ADR-006 to prevent recurrence.

## Post-incident actions

- Post-mortem for any postponement > 1 hour or any hard-fail scenario.
- Verify the postponement was communicated well; check user complaint intake for the 48 hours post-reveal.
- **Adaeze reviews the audit-log entries for the affected draw** to confirm no other event was affected.
- If postponements accumulate (> 2 in a quarter), trigger design review — the two-source approach may need a third source per ADR-006 §Alternatives.
- Update this runbook with any diagnostic step that was missing.
- AI Integration Log entry.

## Notes

- Bitcoin block hashes finalise irrevocably ~1 hour after the block is mined (6 confirmations); therefore the "wait for the source to recover" strategy is safe — the specific block we need does not change.
- drand publishes rounds every 30 seconds and its history is durable via multiple public relays; a total drand outage lasting hours is extremely rare.
- The 4-hour reveal tolerance is a compromise between "quick post-close reveal" (user experience) and "resilient to short-term entropy source hiccups" (operational). Do not shorten it without an ADR-006 amendment.
- **Never** substitute one entropy source for another (e.g. "drand is down, let's just use Bitcoin"). The commitment is to the *specific combined inputs*; substitution breaks the provably-fair guarantee.
- The transparency of the postponement is what makes this a manageable event rather than a trust catastrophe. Vague language in the postponement notice invites conspiracy theories; specific language ("Bitcoin explorer availability delayed reveal by X hours; commitment hash unchanged; verify at [link]") reassures.
