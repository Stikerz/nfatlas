# ADR-007: KYC vendor adapter abstraction

**Status:** Approved (adapter shape). Vendor selection (Smile / Dojah / Prembly / other) is a separate Phase 0 decision recorded via ADR amendment when made.
**Date:** 2026-06-29
**Approved by:** S1408661 (Engineering Lead) on 2026-07-02
**Reversibility:** Two-way door for the adapter shape; vendor swap is manageable but not trivial once production users exist.

## Context

V1 KYC integrates against a Nigerian vendor (Smile Identity, Dojah, or Prembly are shortlist per `docs/compliance/vendor-decisions.md`). Vendor pricing, latency, BVN coverage, and document-OCR quality differ enough that we want flexibility to switch without rewriting Identity-module code, and the option to use a secondary vendor as fallback if the primary has an outage.

This ADR commits the **adapter shape** that all vendors implement. Vendor selection itself is recorded as an ADR amendment after Phase 0.

## Decision

Define a `KYCProvider` protocol in `backend/api/identity/kyc/protocol.py` that all vendor adapters implement. Identity-module code calls the protocol; never a vendor SDK directly.

### Protocol surface

```python
from typing import Protocol
from dataclasses import dataclass
from enum import Enum

class KYCLevel(str, Enum):
    BASIC = "basic"        # BVN lookup, name + DoB match
    ENHANCED = "enhanced"  # BASIC + document OCR + selfie match

class KYCStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING_REVIEW = "pending_review"   # needs human reviewer
    VENDOR_ERROR = "vendor_error"        # adapter retries; not a verdict

@dataclass(frozen=True)
class KYCSubmission:
    user_id: str
    bvn: str | None
    first_name: str
    last_name: str
    date_of_birth: str        # ISO-8601
    phone_e164: str
    document_image_url: str | None
    selfie_image_url: str | None
    level: KYCLevel

@dataclass(frozen=True)
class KYCResult:
    status: KYCStatus
    vendor_reference: str          # vendor's request ID, for support / replay
    raw_response_redacted: dict     # vendor response with PII redacted, for audit
    reasons: list[str]              # vendor-supplied reason codes, normalised
    submitted_at: str               # ISO-8601
    resolved_at: str                # ISO-8601

class KYCProvider(Protocol):
    name: str   # "smile" | "dojah" | "prembly" | ...

    def submit(self, submission: KYCSubmission) -> KYCResult: ...
    def fetch(self, vendor_reference: str) -> KYCResult: ...
```

### Wiring

- One concrete adapter per vendor, in `backend/api/identity/kyc/<vendor>.py`.
- A `KYCRouter` selects the active adapter from configuration (env-driven; default + optional fallback).
- Calls flow through `KYCRouter` only. Identity-module code never imports a vendor adapter directly.
- All adapter calls go through a circuit breaker with a 30-second open period on consecutive failures.

### Audit and storage

- Every `submit` writes a `kyc_submitted` row to `audit_log` (ADR-005) and a row to `kyc_submissions` table with redacted vendor request/response.
- Every `KYCResult` writes a `kyc_approved` / `kyc_rejected` / `kyc_flagged` row to `audit_log`.
- `kyc_submissions` retains for the regulatory minimum (TBD by Phase 0 legal opinion — placeholder 5 years).

### PII redaction

Adapters return `raw_response_redacted` with these fields stripped: BVN (full), document images (replaced with hash references to S3 objects), date-of-birth (replaced with year only). Storing full PII in the application DB is avoided; S3 objects carry the originals under strict access control.

### Fallback policy

If primary vendor's circuit breaker is open, the router attempts the fallback vendor. Mismatched verdicts between primary and fallback (when both eventually return) trigger a Compliance & Risk review.

### Self-exclusion

Self-exclusion is BVN-based (`PRD.md §3.2`). The Identity module maintains a `self_exclusions` table keyed by BVN hash (peppered SHA-256, pepper in secret manager). On every KYC submission, the BVN is hashed and checked against the table; a match returns `REJECTED` with reason `self_excluded` and skips the vendor call.

## Alternatives considered

- **Single-vendor implementation with direct SDK calls.** Lost: vendor lock-in; outages have no recourse; switching costs are high. Adapter pattern is the prudent first build.
- **Generic webhook-driven async API.** Considered: vendors differ in async vs sync semantics. The adapter normalises this; the worker process polls `PENDING_REVIEW` results via `fetch` when needed.
- **Building a thin KYC ledger of our own (storing BVN + doc references encrypted with our keys, vendor only as an oracle).** Considered as a hardening step. Adopted in part: we redact PII before storing vendor responses; documents go to S3 under our keys, vendor receives signed URLs. Full custodial KYC is a V2 evaluation.

## Consequences

**Positive:**
- Vendor swap is replacing one adapter file plus a config change.
- Fallback path means single-vendor outage is a degradation, not an outage.
- Self-exclusion is enforced before any vendor call — no PII leaks to a third party for an excluded user.
- Audit-log integration makes KYC actions reviewable end-to-end.

**Negative:**
- Adapter abstraction adds a small layer; vendor-specific features (e.g. unique liveness checks) require extending the protocol, which is a coordinated change.
- Redaction logic must be re-verified per vendor; a vendor's response schema change can silently bypass redaction. Mitigated by a CI test that asserts no BVN-shaped strings remain in stored vendor responses.
- Two-vendor onboarding doubles the contract / billing surface area. Decision per Phase 0 whether V1 launches with one or two; ADR amendment to record.

**Invariants:**
- All KYC calls go through `KYCRouter`. Enforced by a grep in CI on `backend/api/identity/`.
- Vendor responses with un-redacted PII never persist to the application DB. Enforced by a CI test against fixtures.
- Self-exclusion check precedes every vendor call.
