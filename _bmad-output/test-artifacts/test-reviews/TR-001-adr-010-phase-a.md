# Test Review TR-001 — ADR-010 Phase A + free-route removal (PR #15)

**Reviewed:** 2026-11-26
**Reviewer:** 🧪 Murat (bmad-tea)
**Scope:** `backend/tests/identity/test_self_exclusion.py`, the removal of `backend/tests/ticket/test_free_entry.py`, and the `test_flagship_flow.py` amendment.
**Gate decision:** **CONCERNS** — merge-ready on the backend; two non-blocking gaps and one piece of pre-existing debt recorded below.

---

## 1. Risk classification

Self-exclusion is a **regulatory compliance** control (ADR-010; `docs/risk-register.md` R-REG-08). That is **P0** on the priorities matrix: comprehensive coverage at all levels, happy and unhappy paths, edge cases and error scenarios.

It is also the mitigation for a risk scored ⚫ — a consumer-facing claim that was false for four months. The cost of this control silently regressing is not a bug report; it is the same compliance exposure returning with a test suite asserting everything is fine.

So I held it to a higher bar than its line count suggests, and I was right to.

---

## 2. P0 gap found and closed during review

**The route-level enforcement on `POST /api/v1/tickets/purchase` had no test.**

The service-layer check in `ticket.service.issue_paid` was covered. The 403 pre-check on the route was not. I deleted that block and **all 291 tests stayed green** — an enforcement path with no signal behind it.

Risk: **P2 × I3**. Probability is moderate (a refactor or a merge drops a guard clause nobody is asserting). Impact is high — an excluded user reaches a live checkout page and a payment intent is created against a closed account.

**Closed.** Two tests added (`TestPurchaseRouteEnforcement`), plus one for the equivalent gap on `GET /draws/{id}/skill-questions/next`.

### 2.1 The first version of my own test was too weak

My initial test posted a random `draw_id` and `entitlement_id`. It did go red when I removed the enforcement — but with **404**, because it fell through to the draw lookup. A red for the wrong reason is barely better than no test: it would also fail on an unrelated routing change, and it never demonstrates the thing anyone cares about.

Rewritten to issue an **otherwise-valid purchase** — real `sales_open` draw, real unconsumed entitlement earned *before* exclusion. The mutation result is now unambiguous:

```
>       assert resp.status_code == 403, resp.text
E       assert 201 == 403
E        +  where 201 = <Response [201 Created]>.status_code
```

Without the guard, **an excluded user successfully buys a ticket.** That is the property under test, stated in the failure message. The test also asserts no `payment_intents` row is created as a side effect.

**Principle, for the record:** a test that goes red is not the same as a test that proves something. Verify what the red *says*.

---

## 3. What is genuinely good here

I am not in the habit of padding reviews, so take these as meant.

- **Enforcement is tested at the service layer, not only through HTTP.** `issue_paid` is reachable from the payment webhook without passing the route. Testing only the route would have left the webhook path unguarded and unasserted. This is "prefer the lower test level" applied correctly, for a stated reason.
- **`test_phase_a_does_not_block_reregistration` asserts a limitation, not a capability.** It encodes the Phase A boundary as an executable specification and is built to fail when Phase B lands. This is the strongest artefact in the change, and it is the mechanised copy-to-capability check Adaeze asked for in REVIEW-002 Addendum A.4 — implemented for one claim. **Generalise this pattern.**
- **`test_no_unexclude_route_exists` and `test_registry_has_no_mutation_verbs` assert the absence of capability.** Rare, and exactly right where the absence *is* the control (ADR-010: V1 exclusion is permanent).
- **Idempotency is tested properly** — not merely "the replay does not error", but that `sessions_revoked` is 0 and that **no second audit event** is emitted. Counting the side effects is the part most people skip.
- **The unhappy path asserts no state change.** `test_wrong_mfa_code_changes_nothing` checks the registry row is absent *and* status is still `active`. A failed challenge that half-applied would be the worst possible outcome; it is covered.
- **Fast and isolated.** 19 tests in 7.4s, function-scoped truncation, no hard waits, no conditional flow control, no `try/except` steering. Clean against the test-quality DoD on every axis but one (§5).

---

## 4. Coverage correctly *removed*

`test_free_entry.py` (8 tests) was deleted with the route. I checked what went with it:

| Deleted coverage | Still needed? |
|---|---|
| Admin transcribes free ticket; appears in subject's list | No — route removed |
| 403 non-admin / 401 unauthenticated on `/tickets/free` | No — route removed |
| Duplicate slip 409; unknown subject 404; closed draw 409 | No — route removed |
| `test_paid_then_free_gets_1_then_2` (mixed numbering) | **Partly.** The mixed-source case is gone with the feature; `ticket_number` monotonicity for paid tickets survives in `test_purchase_flow.py` |

No orphaned coverage. The `free_entry_slips` table and `entry_source='free'` are retained in schema, and `conftest` still truncates the table — correct, since historical rows and published proofs depend on them.

---

## 5. Open findings

### 5.1 No E2E coverage of exclusion — P1, non-blocking

`test_flagship_flow.py` does not exercise exclusion. P0 classification asks for all levels, and the one path not covered end-to-end is: exclude → attempt the full purchase journey → blocked → audit chain intact across the whole run.

The unit and integration coverage is strong enough that I will not block merge on this. It belongs in the next slice.

### 5.2 No mobile widget test for `SelfExclusionScreen` — P1, non-blocking

`mobile/test/features/` covers `identity` and `winners`. There is no `account`. The screen carries real logic: the `_confirmed` gate on the literal `EXCLUDE` string, the two-stage request-code-then-confirm flow, and button enablement derived from both. The pattern already exists in `password_screen_test.dart` — there is no framework work to do, only the test.

Compliance-critical UI with zero widget coverage is a gap I want closed before this screen changes again.

### 5.3 Test file exceeds the length guideline — minor

482 lines against a <300 DoD target. Split along the seam that already exists in the class structure: `test_self_exclusion_service.py` (service invariants) and `test_self_exclusion_api.py` (HTTP surface + admin registry).

### 5.4 Pre-existing debt, not this PR's — recorded

- **`_register_login` is reimplemented in 10 test files.** Each copy is a fixture-architecture failure waiting to drift apart; this change added the tenth. It belongs in `conftest.py` as a shared factory.
- **Phone generation is `+2348030{uuid4().int % 1_000_000:06d}`** — random data that can collide, which is precisely the bug class that produced three flaky tests in W8 (one at 47%). Function-scoped truncation holds the blast radius to within-test collisions (~3 in 10⁶ for three users), so the measured risk today is negligible. But the pattern is copied across all 10 files, and a counter-based factory costs nothing. Fix it when the fixture above is extracted.
- **Admin UI has 5 tests total** (`proof-format.test.ts`). The new self-exclusions page adds untested surface to an already-untested app.

---

## 6. Gate

**CONCERNS — approved for merge.**

The P0 gap is closed and demonstrated by mutation. §5.1 and §5.2 are real but proportionate to defer; neither leaves an enforcement path unasserted, which was the thing that mattered. §5.4 is debt this change inherited rather than created.

**293/293 backend + 5/5 admin green**, natively and through a rebuilt image. No flakes observed across repeated runs.

Conditions for the next slice, not for this merge:
1. E2E exclusion path (§5.1).
2. `SelfExclusionScreen` widget test (§5.2).
3. Extract the shared registration factory and kill the modulo-random phone (§5.4).

— 🧪 Murat
