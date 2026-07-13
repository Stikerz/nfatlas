"""Idempotency support types (ADR-004).

No FastAPI BaseHTTPMiddleware is used — the enforcement lives in a per-endpoint
dependency (`atlas.idempotency.dependency.idempotency_guard`) so read endpoints
skip the check entirely per ADR-004 §Scope. This module defines the shared
exception classes used by dependency + route handlers.
"""

from __future__ import annotations

from fastapi import HTTPException, status


class MissingIdempotencyKey(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "idempotency_key_required",
                "message": "This endpoint requires an Idempotency-Key header.",
            },
        )


class IdempotencyConflict(HTTPException):
    """Same key reused with a different request body (ADR-004 §Processing step 2)."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "idempotency_key_conflict",
                "message": "Idempotency-Key was previously used with a different request body.",
            },
        )


class IdempotencyInFlight(HTTPException):
    """Same key in flight, retry-after 1 (ADR-004 §Processing step 3)."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "idempotency_key_in_flight",
                "message": "A request with this Idempotency-Key is still processing.",
            },
            headers={"Retry-After": "1"},
        )
