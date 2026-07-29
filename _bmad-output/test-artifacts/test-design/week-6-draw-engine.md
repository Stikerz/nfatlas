# Test design — Week 6 draw-engine slice

**Drafted:** 2026-08-08 (Week 6 close)
**Drafted by:** 💻 Amelia (stub — 🧪 Murat expansion Week 7)
**Applies to:** V0.5 Week 6 slice (state machine, close/reveal, entropy, winners, proof, verifier).
**Pairs with:** `week-6-build-plan.md §4 Test strategy`, `week-5-tickets-draws.md` (foundation).

Slice map + coverage matrix + gaps. Not a test plan for reviewers to sign off — the code is the ground truth; this document is the map for the next author.

---

## 1. Slice under test

- `atlas.draw.state_machine` — pure transition table.
- `atlas.draw.service.close_draw` — snapshot + hash + state flip.
- `atlas.draw.entropy` — protocol + bitcoin adapter (stub + live) + drand adapter (stub + live) + composite provider.
- `atlas.draw.reveal.select_winners` — pure HMAC stream + rejection sampling.
- `atlas.draw.service.reveal_draw` — orchestration + audit chain + notification hook.
- `atlas.draw.service.create_draw` — server_seed + commitment mint.
- Routes: `POST /draws`, `POST /draws/{id}/close`, `POST /draws/{id}/reveal`, `GET /draws/{id}/winners`, `GET /draws/{id}/proof`.
- `atlas.notification.winner.notify_winner` — Mailhog stub + audit-before-delivery.
- `backend/tools/verify_draw.py` — standalone CLI.

## 2. Coverage matrix

Rows are behaviours; columns are test files.

| Behaviour | test_state_machine | test_close_draw | test_reveal_algorithm | test_reveal_flow | test_entropy_stub | test_entropy_live | test_proof_and_notification | test_draw_lifecycle (E2E) |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| State transition table (legal + illegal) | ✔ |  |  |  |  |  |  |  |
| Terminal-state detection | ✔ |  |  |  |  |  |  |  |
| close computes deterministic tickets_hash |  | ✔ |  |  |  |  |  |  |
| close idempotent + audit event once |  | ✔ |  |  |  |  |  |  |
| close on illegal state → 409 |  | ✔ |  |  |  |  |  |  |
| purchase against closed draw → 409 (regression) |  | ✔ |  |  |  |  |  |  |
| select_winners deterministic golden vector |  |  | ✔ |  |  |  |  |  |
| select_winners returns 1+reserves distinct |  |  | ✔ |  |  |  |  |  |
| Different seed → different primary (probabilistic) |  |  | ✔ |  |  |  |  |  |
| Different entropy → different sequence |  |  | ✔ |  |  |  |  |  |
| NotEnoughTickets on small pool |  |  | ✔ |  |  |  |  |  |
| Rejection sampling boundary (0xff → reject) |  |  | ✔ |  |  |  |  |  |
| Uniform distribution smoke over 4 outcomes |  |  | ✔ |  |  |  |  |  |
| reveal flips state + writes 6 winners |  |  |  | ✔ |  |  |  | ✔ |
| reveal audit chain: 1 revealed + 6 winner_selected |  |  |  | ✔ |  |  |  |  |
| winner event uses user_id_hash not raw user_id |  |  |  | ✔ |  |  |  |  |
| reveal idempotent (no-op on already-revealed) |  |  |  | ✔ |  |  |  |  |
| reveal on sales_open → 409 |  |  |  | ✔ |  |  |  |  |
| reveal with 0 tickets → 409 not_enough_tickets |  |  |  | ✔ |  |  |  |  |
| non-admin close/reveal → 403 |  |  |  | ✔ |  |  |  |  |
| GET /winners ordered by position |  |  |  | ✔ |  |  |  |  |
| GET /winners empty pre-reveal |  |  |  | ✔ |  |  |  |  |
| Bitcoin stub determinism |  |  |  |  | ✔ |  |  |  |
| drand round derivation golden vectors |  |  |  |  | ✔ |  |  |  |
| Composite mode selection |  |  |  |  | ✔ |  |  |  |
| Bitcoin two-explorer match |  |  |  |  |  | ✔ |  |  |
| Bitcoin explorer mismatch → EntropyMismatchError |  |  |  |  |  | ✔ |  |  |
| Bitcoin 5xx → EntropyFetchError |  |  |  |  |  | ✔ |  |  |
| drand happy fetch |  |  |  |  |  | ✔ |  |  |
| drand stale-proxy detection (round mismatch) |  |  |  |  |  | ✔ |  |  |
| drand 5xx → EntropyFetchError |  |  |  |  |  | ✔ |  |  |
| Proof pre-reveal minimal shape |  |  |  |  |  |  | ✔ |  |
| Proof post-reveal full shape |  |  |  |  |  |  | ✔ | ✔ |
| Proof never leaks PII (email/phone scrape) |  |  |  |  |  |  | ✔ |  |
| Proof public — no auth required |  |  |  |  |  |  | ✔ | ✔ |
| Verifier CLI valid proof → exit 0 |  |  |  |  |  |  | ✔ | ✔ |
| Verifier CLI tampered → exit 1 + MISMATCH |  |  |  |  |  |  | ✔ |  |
| Verifier CLI pre-reveal → exit 2 |  |  |  |  |  |  | ✔ |  |
| Winner notification: 6 emails + 6 audit events |  |  |  |  |  |  | ✔ |  |
| SMTP failure caught + reveal succeeds |  |  |  |  |  |  | ✔ |  |
| Create draw generates server_seed + commitment |  |  |  |  |  |  |  | ✔ |
| Full lifecycle: create → sell → close → reveal → verify |  |  |  |  |  |  |  | ✔ |

## 3. Coverage gaps (Murat to expand)

- **Live-mode entropy against real endpoints:** stub mode is CI-tested; live mode only sees mocked HTTP. A weekly smoke test hitting real mempool.space + blockstream.info + drand would surface upstream API changes early. Should be a separate job (marked `@pytest.mark.live_entropy`, off by default).
- **Reveal-time BLS verification of the drand signature:** Week 6 persists `drand_signature` but skips client-side verify per §risk 3. Add when the BLS library dependency is accepted.
- **Concurrency:** two concurrent reveal requests race the same draw. State-machine guard + SQLAlchemy's session isolation should serialize but there is no explicit test.
- **Reveal-abort recovery:** live-mode `EntropyMismatchError` retry-after-30-min is documented in the runbook but not simulated. A pytest fixture that force-fails the first fetch then succeeds on retry would prove the recovery path.
- **Large pools:** V0.5 tests use pools of 6-10 tickets. `select_winners` should be exercised against a 10,000-ticket pool to catch any O(n²) or memory issue in the rejection loop. Not shipping-blocking for V0.5.
- **Proof-endpoint pagination:** `ordered_ticket_ids` returns the full list — fine for V0.5 (< 100 tickets), needs pagination when V1 draws hit ~100k. Test would verify the pagination doesn't break `select_winners` reproducibility.
- **Verifier CLI: --proof-url with self-signed TLS:** production will serve /proof over TLS; the CLI's `urlopen` uses system trust roots. Should test against a local self-signed cert to confirm no accidental verification-skip.
- **`draw.committed` audit event content:** covered indirectly by E2E but a dedicated test that asserts the payload shape (`commitment`, `prize_copy`, `close_time`, `draw_time`, `entries_cap`, actor_id) would catch a shape regression.

## 4. Handoff to Week 7

Week 7 = polish + admin UI + public proof page.

- **Admin Next.js pages** for close + reveal + audit-log viewer: backend endpoints are stable; UI is Sally + Amelia W7.
- **Public proof page** at `/proof/{draw_id}` (Next.js server-rendered) reads `GET /proof` and renders the trust surface in a browser. Should include a big "Copy verifier command" button that produces the exact `python verify_draw.py --proof-url ...` line for the user's own terminal.
- **Prize-claim UX**: `draw_winners.contact_status` advances from `pending` → `contacted` → `claimed` on the mobile app; Week 6 leaves the state machine bones in place, W7 wires the UX.
- **Demo-mode config**: auto-advance close_time so a demo can compress "3 days sale + 1 hour buffer + reveal" into 5 minutes without breaking the ADR-006 semantics.

## 5. Notes for the next author

- The verifier CLI must stay stdlib-only (no atlas package install required). Any change that adds a dependency requires the CI to install atlas + deps before running the verifier subprocess test — currently it just prepends `backend/src` to sys.path.
- `select_winners` is the load-bearing "provably fair" property. Any change to that function is a trust-story change and needs Adaeze on the PR.
- The `_stub_notification_sender` fixture in `test_proof_and_notification.py` is the cleanest way to test reveal flows without a real Mailhog — reuse in Week 7.
