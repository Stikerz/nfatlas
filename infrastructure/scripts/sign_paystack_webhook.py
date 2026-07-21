"""Compute a valid x-paystack-signature for a webhook body.

Feeds Day 4's local webhook testing: hand-craft a body, sign it with
the local ATLAS_PAYSTACK_WEBHOOK_SECRET, POST it to
`/api/v1/payments/webhooks/paystack`, watch the deposit land.

Usage (from repo root, with the backend env loaded):

    python infrastructure/scripts/sign_paystack_webhook.py \\
        < path/to/event.json

    # Or pipe:
    echo '{"event":"charge.success","data":{...}}' \\
        | python infrastructure/scripts/sign_paystack_webhook.py

Prints the raw signature to stdout. Full curl command example:

    BODY='{"event":"charge.success","data":{"reference":"atlas-abc","amount":50000,"status":"success","currency":"NGN","fees":10000,"customer":{"email":"a@b.c"}}}'
    SIG=$(printf '%s' "$BODY" \\
        | python infrastructure/scripts/sign_paystack_webhook.py)
    curl -X POST http://localhost:8000/api/v1/payments/webhooks/paystack \\
        -H "x-paystack-signature: $SIG" \\
        -H "Content-Type: application/json" \\
        -d "$BODY"

Requires ATLAS_PAYSTACK_WEBHOOK_SECRET in the environment or `.env`.
"""

from __future__ import annotations

import hashlib
import hmac
import sys
from pathlib import Path


def _load_secret() -> str:
    """Read ATLAS_PAYSTACK_WEBHOOK_SECRET via the app config so the
    ADR-012 env-var discipline holds even for this helper."""
    # Prefer sys.path relative to the repo layout so the script works
    # without the package installed (fresh clone / no venv activated).
    repo_root = Path(__file__).resolve().parents[2]
    backend_src = repo_root / "backend" / "src"
    sys.path.insert(0, str(backend_src))

    from atlas.config import get_settings

    return get_settings().paystack_webhook_secret.get_secret_value()


def sign(body: bytes, secret: str) -> str:
    return hmac.new(
        key=secret.encode("utf-8"),
        msg=body,
        digestmod=hashlib.sha512,
    ).hexdigest()


def main() -> int:
    body = sys.stdin.buffer.read()
    if not body:
        print(
            "usage: pipe JSON body on stdin, e.g. "
            "`echo '{...}' | python sign_paystack_webhook.py`",
            file=sys.stderr,
        )
        return 2

    signature = sign(body, _load_secret())
    sys.stdout.write(signature + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
