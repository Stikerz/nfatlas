# Runbook: Reveal abort (entropy failure / mismatch)

**Severity:** SEV-1 if a real-money draw is in the reveal window; SEV-2 otherwise
**Owner:** on-call engineer → EL immediately if a draw is in flight
**Last verified:** 2026-08-07 by 💻 Amelia (W6 Day 4 draft — awaiting Tobi review)
**Applies to:** V1 real-money draws. V0.5 demo runs in `stub` entropy mode where this scenario is impossible; the runbook exists so live-mode failures are handled without improvisation.
**Related:** ADR-006 §Protocol stage 4, `payment-outage.md`, `paystack-webhook-outage.md`.

## Symptoms

Reveal endpoint (`POST /api/v1/draws/{id}/reveal`) returns 500 or the transaction rolls back with one of:

- `EntropyFetchError: mempool.space fetch failed` — Bitcoin explorer #1 5xx/timeout.
- `EntropyFetchError: blockstream: ...` — Bitcoin explorer #2 5xx/timeout or walk exhausted.
- `EntropyMismatchError: bitcoin explorers disagree at close_time=...` — both explorers responded but returned different block hashes for the same timestamp.
- `EntropyFetchError: drand fetch failed for round N` — drand endpoint 5xx/timeout.
- `EntropyFetchError: drand returned round N but we asked for M` — proxy stale.

None of these mutate DB state — the reveal transaction rolls back cleanly. The draw stays in `sales_closed`; no `draw.revealed` audit event fires.

## Detection

- **Alert:** `REVEAL_ABORT` — the `POST /reveal` endpoint returned 5xx or `EntropyMismatchError` in the last 15 minutes.
- **User signal:** the operator UI (Week 7) surfaces the abort inline; the demo reveal button shows "Reveal failed — see logs".
- **External signal:** the two Bitcoin explorers' status pages, drand's `#status` channel.

## Impact

- **Users:** if a real-money draw is affected, winners are not yet published. Perceived integrity is at risk if this takes > 15 minutes to resolve. The user-visible message must be honest ("Reveal delayed — external randomness source unavailable, retrying").
- **Ledger:** no side effects. `close_draw` was already committed (tickets_hash is stable); the reveal transaction rolls back.
- **Trust:** the two-explorer cross-check IS the trust primitive — a mismatch means one explorer served a reorg-orphaned block, which is exactly what the protocol is designed to catch. **Retry is safe** once the reorg settles (typically < 30 min).

## Diagnosis

1. **Which failure mode?** Read the exception message in the backend logs. Categorise:
   - Bitcoin single-source failure: `mempool.space` OR `blockstream.info` 5xx.
   - Bitcoin mismatch: `EntropyMismatchError`.
   - drand failure: `drand fetch failed`.
   - drand stale proxy: `drand returned round N but we asked for M`.
2. **Check the external status pages:**
   - https://status.mempool.space/
   - Blockstream status is announced on their support channels.
   - https://status.drand.love/ (League of Entropy).
3. **Check network egress** from the atlas-backend container. If both Bitcoin explorers 5xx simultaneously and drand is also failing, the issue is likely our side.
4. **Bitcoin mismatch specifically:** query both explorers manually with the failing `close_time` unix timestamp. If they still disagree after 15 minutes, a reorg-orphan is the most likely cause; wait another 30 minutes for the chain to settle.

## Mitigation

### For a transient external failure (Bitcoin OR drand 5xx)

1. **Retry the reveal after 5 minutes.** The endpoint is idempotent; a fresh call re-fetches entropy and either succeeds or re-aborts.
2. If two retries fail, wait 30 minutes and retry. Most public API outages resolve within 30 minutes.
3. **Do NOT switch entropy sources on the fly** — that changes the reveal-time input set and would invalidate the trust story (verifier CLI reproduces against whatever sources were published).

### For a Bitcoin explorer mismatch

4. **Wait for the reorg to settle.** Bitcoin block finality is probabilistic; 3-6 confirmations (~30-60 min) is typically enough for two explorers to converge.
5. Retry the reveal. If they now agree, reveal proceeds normally.
6. If they still disagree after 2 hours, escalate to EL. This is unprecedented outside a hostile network event; the operator should decide whether to postpone the draw's reveal_time (see `draw-entropy-unavailable.md` §Rollback for the postponement mechanic).

### For a drand outage

7. drand's League of Entropy is highly reliable (multiple geo-distributed nodes; single-node outage is transparent). A prolonged drand outage is extremely rare. If confirmed, wait for recovery; do not substitute an alternative randomness source.

### Never do

- **Never manually pick a Bitcoin block or drand round.** The two-source cross-check + deterministic round derivation IS the trust primitive; any manual selection destroys the "provably fair" claim for that draw.
- **Never disable the two-explorer check** to "get the reveal through". A single-source reveal is not covered by ADR-006 and would need a public disclosure.
- **Never re-run `close_draw`** to "refresh" the tickets_hash. Tickets have not changed; the hash is stable; re-close would emit a duplicate `draw.entries_snapshot` and confuse the audit trail.

## Rollback steps

Nothing to roll back — the reveal transaction rolled back on the exception. The draw stays in `sales_closed`; retry is the only forward path.

If a draw close was postponed as part of a wider outage response, un-postponing is not appropriate; the postponed time is now the announced time.

## Post-incident actions

- Post-mortem if the abort delayed a real-money reveal by > 15 minutes OR involved a manual escalation.
- AI Integration Log entry with the exception message + resolution time.
- Update `docs/risk-register.md` R-VEN-01 if the outage involved a Bitcoin explorer that has now had > 2 incidents in the trailing 30 days — consider adding a third explorer as a tiebreaker (V2).
- Notify Adaeze if a draw's reveal was delayed > 1 hour past its announced time — regulatory-disclosure implications for user comms.
- Verify the incident-comms template held up under real use.

## Notes

- V0.5 demo runs in `ATLAS_DRAW_ENTROPY_MODE=stub`. This runbook does not apply to demo runs; the stub always succeeds.
- The `EntropyFetchError` / `EntropyMismatchError` types are typed exceptions from `atlas.draw.entropy.protocol` — grep the logs for them, not "500".
- The reveal endpoint is public-facing per ADR-006 (only the trigger is admin-gated; the proof endpoint is open). A leaked reveal-abort log doesn't disclose sensitive material.
- Week 7 will surface the abort inline in the admin UI. Until then, the operator watches the terminal running `curl` for the exception.
