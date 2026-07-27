# Test design — Week 5 tickets + draws slice

**Drafted:** 2026-08-01 (Week 5 close)
**Drafted by:** 💻 Amelia (stub — awaiting 🧪 Murat expansion Week 6)
**Applies to:** V0.5 Week 5 slice (draw skeleton + skill-question surface + ticket module).
**Pairs with:** `week-5-build-plan.md §4 Test strategy`, `docs/qa/strategy.md` (once Murat authors it).

Skeleton so the Week 6 test-design pass has somewhere to grow. Not a test plan for reviewers to sign off — the code is the ground truth; this document is a map.

---

## 1. Slice under test

- `atlas.draw`: read-only surface (`GET /draws`, `GET /draws/{id}`); state stays `sales_open` in V0.5. Close + reveal ship Week 6.
- `atlas.skill`: `next_question` rotation, `verify_answer` grading, 5-minute entitlement.
- `atlas.ticket`: `_mint_ticket` monotonic-per-draw allocator, `issue_paid`, `issue_free`.
- `atlas.wallet.service.record_ticket_sale`: direct-to-Paystack revenue posting (distinct from `record_deposit`).
- `atlas.payment.service`: `purpose` dispatch (`deposit` vs `ticket`) in `_apply_succeeded`.

## 2. Coverage matrix

Rows are behaviours; columns are test files that exercise them.

| Behaviour | draw/test_draw_routes | skill/test_skill_service | skill/test_skill_routes | ticket/test_purchase_flow | ticket/test_free_entry | wallet/test_wallet_routes | e2e/test_flagship_flow |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `GET /draws` filters to sales_open | ✔ |  |  |  |  |  | ✔ |
| `GET /draws/{id}` returns commitment | ✔ |  |  |  |  |  | ✔ |
| 404 unknown draw | ✔ |  |  |  |  |  |  |
| `is_sales_open` state discrimination | ✔ |  |  |  |  |  |  |
| Rotation deterministic per (user, draw, minute) |  | ✔ |  |  |  |  |  |
| Rotation varies per user |  | ✔ |  |  |  |  |  |
| Wrong answer → no entitlement |  | ✔ | ✔ |  |  |  |  |
| Correct answer → entitlement |  | ✔ | ✔ | ✔ (setup) | ✔ (parity) |  | ✔ |
| Cross-user entitlement rejection |  | ✔ | ✔ | ✔ |  |  |  |
| Expired attempt → 410 |  | ✔ |  |  |  |  |  |
| Already-answered → 409 |  | ✔ | ✔ |  |  |  |  |
| `is_correct` never leaked on the wire |  |  | ✔ |  |  |  |  |
| Idempotency-Key replay on `/answer` |  |  | ✔ |  |  |  |  |
| Purchase → checkout URL (no ticket yet) |  |  |  | ✔ |  |  | ✔ |
| Webhook mints paid ticket + posts revenue |  |  |  | ✔ |  |  | ✔ |
| user_wallet stays 0 across paid path |  |  |  | ✔ |  | ✔ | ✔ |
| Webhook replay is a no-op |  |  |  | ✔ |  |  |  |
| Entitlement marked consumed after mint |  |  |  | ✔ |  |  |  |
| Ticket-number monotonic across three purchases |  |  |  | ✔ |  |  |  |
| Draw-closed-mid-purchase → 409 |  |  |  | ✔ |  |  |  |
| GET /tickets/me isolated per user |  |  |  | ✔ |  |  | ✔ |
| Admin transcribes free ticket |  |  |  |  | ✔ |  | ✔ |
| Non-admin → 403 |  |  |  |  | ✔ |  |  |
| Duplicate slip → 409 |  |  |  |  | ✔ |  |  |
| Unknown subject user → 404 |  |  |  |  | ✔ |  |  |
| Closed draw for free entry → 409 |  |  |  |  | ✔ |  |  |
| Free ticket audit uses slip_reference_hash (no raw) |  |  |  |  | ✔ |  |  |
| Paid #1 + free #2 (parity by construction) |  |  |  |  | ✔ |  |  |
| Wallet chip: new user → 0 |  |  |  |  |  | ✔ | ✔ |
| Wallet chip: after deposit reflects balance |  |  |  |  |  | ✔ |  |
| Full audit chain (register → free ticket) |  |  |  | ✔ (subset) |  |  | ✔ |

## 3. Coverage gaps (Murat to expand)

- **Concurrency on `_mint_ticket`:** V0.5 is single-user demo; the row-lock allocator was written for V1 but has no adversarial concurrency test. A pytest fixture that opens two async sessions and races two `issue_paid` calls into the same draw would prove the SELECT FOR UPDATE serialization holds.
- **Free-entry parity beyond ticket_number:** currently proved by construction (shared `_mint_ticket`); no test asserts the odds are equal. Week 6's reveal path is where this becomes visible — a test that mints N paid + N free tickets, runs the reveal, and checks the winner-source distribution is not skewed.
- **Entitlement expiry mid-purchase:** the pre-check catches expired entitlements at `/purchase`, but a Paystack round-trip that spans the 5-minute TTL is not tested. Simulate by patching `datetime.now` between pre-check and webhook dispatch.
- **`payment.ticket_metadata_missing` audit event:** the failure branch in `_apply_ticket_success` when `metadata.draw_id` or `metadata.entitlement_id` is missing has no test. Would require constructing a ticket-purpose intent by hand (bypassing `create_intent`) and feeding a webhook.
- **Rotation golden vectors:** the rotation tests assert determinism but the specific offset values are not pinned. A change to `_rotation_offset` (e.g. hash function swap) would go unnoticed by the assertions. Golden-vector tests (given known user_id/draw_id/bucket → assert exact offset) would catch this.
- **`GET /tickets/me` pagination:** V0.5 returns all tickets unpaged. Add pagination + tests when the mobile UI needs it (Week 6-7 polish).
- **Purchase → webhook race:** two rapid `/purchase` calls for the same entitlement land two payment intents (different `Idempotency-Key`s); webhook consumption is single-use so the second webhook's `_validate_and_consume_entitlement` raises `EntitlementInvalidError('already_consumed')`. Add explicit test.

## 4. Real-Postgres vs mocks

Per `AINE-AGENTS.md §8.6` we run integration tests against real Postgres and mock only at the Paystack HTTP boundary (Paystack API is mocked; Paystack webhook signatures are computed for real using the configured secret).

Fixtures live in `backend/tests/conftest.py`; per-test truncation covers the Week 5 additions (`tickets`, `free_entry_slips`, `skill_question_attempts` already added Days 1-3).

## 5. Handoff to Week 6

Draw close + reveal will need:
- Fixture: a draw with N tickets already minted, ready to close.
- Fixture: canonical `entropy` + `bitcoin_hash` + `drand_round` inputs matching the tickets_hash math.
- Golden vector: given fixed inputs → the same winner ticket every time. This is the load-bearing property for the "provably fair" trust claim.

Murat should own the golden-vector shape and the verifier CLI's contract.
