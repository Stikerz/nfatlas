"""Per-endpoint idempotency dependency (ADR-004 §Processing).

Usage in a route:

    @router.post("/api/v1/users", status_code=201)
    async def register(
        body: RegisterRequest,
        idempotency: IdempotencyGuard = Depends(idempotency_guard(endpoint="POST /api/v1/users")),
        session: AsyncSession = Depends(get_session),
    ) -> RegisterResponse:
        if idempotency.cached_response is not None:
            return idempotency.cached_response
        response = await identity_service.register(session, body)
        await idempotency.record(session, status_code=201, response_body=response.model_dump(mode="json"))
        return response

The guard runs steps 1-3 of ADR-004 §Processing before the route body executes;
the route calls `.record()` to complete step 4.

In-flight detection uses a 30s window per ADR-004 §Processing step 3.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import rfc8785
from fastapi import Depends, Header, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.db import get_session
from atlas.idempotency.middleware import (
    IdempotencyConflict,
    IdempotencyInFlight,
    MissingIdempotencyKey,
)
from atlas.idempotency.models import IdempotencyRecord

IN_FLIGHT_WINDOW = timedelta(seconds=30)


def canonical_request_hash(body: Any) -> str:
    """SHA-256 of the JCS-canonicalized request body. Deterministic across clients."""
    return hashlib.sha256(rfc8785.dumps(body)).hexdigest()


@dataclass
class IdempotencyGuard:
    key: str
    endpoint: str
    request_hash: str
    cached_response: dict[str, Any] | None = None
    cached_status: int | None = None
    _record: IdempotencyRecord | None = field(default=None, repr=False)

    async def record(
        self,
        session: AsyncSession,
        *,
        status_code: int,
        response_body: dict[str, Any],
    ) -> None:
        """Persist the response so future retries return it verbatim (step 4)."""
        if self._record is None:
            raise RuntimeError(
                "IdempotencyGuard.record() called without a pending record — "
                "this guard was constructed from a cached response."
            )
        self._record.response_code = status_code
        self._record.response_body = response_body
        self._record.completed_at = datetime.now(timezone.utc)
        await session.flush()


def idempotency_guard(*, endpoint: str) -> Callable[..., Any]:
    """Factory returning a FastAPI dependency scoped to a specific endpoint label."""

    async def _dependency(
        request: Request,
        session: AsyncSession = Depends(get_session),
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> IdempotencyGuard:
        if not idempotency_key:
            raise MissingIdempotencyKey()

        # Parse body once and stash on request.state so the route handler can
        # re-use the same parsed representation without a second read.
        body_bytes = await request.body()
        body_json: Any = None
        if body_bytes:
            import json

            try:
                body_json = json.loads(body_bytes)
            except json.JSONDecodeError:
                body_json = {"__raw__": body_bytes.decode("utf-8", errors="replace")}

        request_hash = canonical_request_hash(body_json)

        existing = (
            await session.execute(
                select(IdempotencyRecord).where(IdempotencyRecord.key == idempotency_key)
            )
        ).scalar_one_or_none()

        if existing is not None:
            if existing.completed_at is not None:
                if existing.request_hash != request_hash:
                    raise IdempotencyConflict()
                return IdempotencyGuard(
                    key=idempotency_key,
                    endpoint=endpoint,
                    request_hash=request_hash,
                    cached_response=existing.response_body or {},
                    cached_status=existing.response_code,
                )
            # in-flight
            if datetime.now(timezone.utc) - existing.created_at < IN_FLIGHT_WINDOW:
                raise IdempotencyInFlight()
            # Aged-out in-flight row — treat as stale and overwrite.
            existing.request_hash = request_hash
            existing.created_at = datetime.now(timezone.utc)
            await session.flush()
            return IdempotencyGuard(
                key=idempotency_key,
                endpoint=endpoint,
                request_hash=request_hash,
                _record=existing,
            )

        record = IdempotencyRecord(
            key=idempotency_key,
            user_id=None,
            endpoint=endpoint,
            request_hash=request_hash,
        )
        session.add(record)
        await session.flush()
        return IdempotencyGuard(
            key=idempotency_key,
            endpoint=endpoint,
            request_hash=request_hash,
            _record=record,
        )

    return _dependency
