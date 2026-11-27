# Compliance Review — REVIEW-004

**Subject:** Login response for a self-excluded account (PR #17).
**Drafted:** 2026-11-27
**Drafted by:** ⚖️ Adaeze (atlas-compliance-risk)
**Status:** Draft — pending founder acknowledgement.

---

## 1. Verdict: **Approved.**

Small change, correct on both the compliance and the security side, and it fixes a defect I should have caught myself when I reviewed Phase A in REVIEW-002 Addendum B.

## 2. What was wrong

ADR-010 §Enforcement points states that after self-exclusion, *"future logins return a polite 'this account has been closed' message."* The shipped behaviour returned `invalid_credentials` — the same response as a typo.

That is a responsible-gaming defect, not a cosmetic one. A person who has deliberately closed their account and later returns — often at exactly the moment of weakest resolve — was told their password was wrong. The predictable responses are to try again, attempt a reset, or contact support: three more touchpoints with a platform they asked to be shut out of. The control worked; the communication actively undermined it.

I approved Phase A without checking this. REVIEW-002 Addendum B §B.2 lists what I verified, and the login *refusal* is there — but I checked that login was refused, not what the refused user was told. Enforcement and disclosure are different questions and I only asked one of them.

## 3. Why the fix is sound

The naive fix — change the message where the status was checked — would have been a disclosure defect. Status was checked **before** the password, so any distinct response would have let an unauthenticated party enumerate closed accounts by email alone. Self-exclusion status is sensitive: it indicates a user's relationship with gambling harm, and under NDPA 2023 (counsel Q4) it is plausibly special-category data.

The implemented fix verifies the password first and raises `AccountClosed` (403) only for a caller who has already proved they hold the credentials — someone who, by definition, can already access the account. A wrong password on a closed account still returns `invalid_credentials`, and a test asserts that non-disclosure rather than leaving it to inspection.

Checking the password for every caller is also the more timing-uniform path, which marginally reduces a side-channel I had not considered.

## 4. Copy

> *"This account has been closed and cannot be reopened."*

Approved as written. Factual, final, no invitation to retry, no support deflection, and consistent with the in-app closure screen and the responsible-play page. It does not say "contact support" — correct, because support cannot reverse it and implying otherwise would restart the conversation the user ended.

## 5. Note on how this was found

This was found by **running the application**, not by the test suite — 268 passing tests asserted that login was refused, and none asserted what the user was told.

That is the fourth defect this month in the same family: a documented behaviour that the system did not actually exhibit. The previous three were consumer copy claiming controls that did not exist. This one inverts it — the control existed and the ADR described it correctly, but the implementation quietly diverged.

Addendum A.4 established that no claim ships without code and a test behind it. **I am extending it:** where an ADR specifies what a user is *told*, the assertion must cover the message, not merely the outcome. Murat — this is the same generalisation of `test_phase_a_does_not_block_reregistration` we discussed, applied to disclosure rather than capability.

— ⚖️ Adaeze
