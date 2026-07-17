"""Deterministic Paystack fixture responses used in stub mode.

Shapes mirror Paystack's public API docs (docs.paystack.com):
  - POST /transaction/initialize          -> `initialize_response`
  - GET  /transaction/verify/:reference   -> `verify_success_response` / `_failed`
  - webhook `charge.success` / `charge.failed`

Fees are Paystack's Nigerian card schedule: ₦100 flat below ₦2,500;
1.5% + ₦100 above ₦2,500; capped at ₦2,000. See §0.2 of the Week 4
build plan — we trust the vendor field in real mode, but the stub
computes it locally so tests can exercise the split.

Every fixture uses `http://mock-paystack.local/checkout/{ref}` so
consumers of a stubbed `checkout_url` see immediately that it is not a
live sandbox URL.
"""

from __future__ import annotations

from typing import Any

CHECKOUT_HOST = "http://mock-paystack.local/checkout"


def compute_fee_kobo(amount_minor: int) -> int:
    """Paystack NG-card schedule (kobo). Approximate; real numbers come from vendor."""
    flat_only_threshold = 2_500_00  # ₦2,500 in kobo
    if amount_minor <= flat_only_threshold:
        return 100_00  # ₦100
    fee = (amount_minor * 15) // 1000 + 100_00  # 1.5% + ₦100
    cap = 2_000_00  # ₦2,000
    return min(fee, cap)


def initialize_response(*, reference: str, amount_minor: int, email: str) -> dict[str, Any]:
    """Shape mirrors POST /transaction/initialize's `data` block."""
    return {
        "status": True,
        "message": "Authorization URL created",
        "data": {
            "authorization_url": f"{CHECKOUT_HOST}/{reference}",
            "access_code": f"stub_access_{reference}",
            "reference": reference,
            "amount": amount_minor,
            "currency": "NGN",
            "customer": {"email": email},
        },
    }


def verify_success_response(*, reference: str, amount_minor: int, email: str) -> dict[str, Any]:
    """Shape mirrors GET /transaction/verify/:reference on a successful charge."""
    fee = compute_fee_kobo(amount_minor)
    return {
        "status": True,
        "message": "Verification successful",
        "data": {
            "id": abs(hash(reference)) % (2**31),
            "status": "success",
            "reference": reference,
            "amount": amount_minor,
            "currency": "NGN",
            "channel": "card",
            "fees": fee,
            "customer": {"email": email},
            "paid_at": "2026-07-22T09:30:00.000Z",
        },
    }


def verify_failed_response(*, reference: str, amount_minor: int, email: str) -> dict[str, Any]:
    return {
        "status": True,
        "message": "Verification successful",
        "data": {
            "id": abs(hash(reference)) % (2**31),
            "status": "failed",
            "reference": reference,
            "amount": amount_minor,
            "currency": "NGN",
            "channel": "card",
            "fees": 0,
            "customer": {"email": email},
            "gateway_response": "Declined",
            "paid_at": None,
        },
    }


def charge_success_event(*, reference: str, amount_minor: int, email: str) -> dict[str, Any]:
    """Shape mirrors a webhook `charge.success` event body."""
    fee = compute_fee_kobo(amount_minor)
    return {
        "event": "charge.success",
        "data": {
            "id": abs(hash(reference)) % (2**31),
            "reference": reference,
            "amount": amount_minor,
            "currency": "NGN",
            "status": "success",
            "channel": "card",
            "fees": fee,
            "customer": {"email": email},
            "paid_at": "2026-07-22T09:30:00.000Z",
        },
    }


def charge_failed_event(*, reference: str, amount_minor: int, email: str) -> dict[str, Any]:
    return {
        "event": "charge.failed",
        "data": {
            "id": abs(hash(reference)) % (2**31),
            "reference": reference,
            "amount": amount_minor,
            "currency": "NGN",
            "status": "failed",
            "channel": "card",
            "fees": 0,
            "customer": {"email": email},
            "gateway_response": "Declined",
            "paid_at": None,
        },
    }
