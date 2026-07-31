"""Admin audit-log read endpoint (Week 7).

Superadmin-only. Filterable by event_name + subject_type + time range,
paginated newest-first via a `before_seq` anchor.

Only reads — writes stay locked to `atlas.audit_log.writer.append`
per ADR-005.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.admin import service as admin_service
from atlas.audit_log import reader
from atlas.db import get_session
from atlas.identity.auth import current_session
from atlas.identity.models import Session as SessionRow

router = APIRouter(prefix="/api/v1", tags=["audit_log"])

_MAX_LIMIT = 500


class AuditLogEntry(BaseModel):
    seq: int
    occurred_at: str
    actor_type: str
    actor_id: str | None
    event_name: str
    subject_type: str
    subject_id: str
    payload: dict[str, Any]
    prev_hash: str
    row_hash: str


class AuditLogPage(BaseModel):
    items: list[AuditLogEntry]
    next_before_seq: int | None
    chain_verified: bool
    chain_verify_reason: str | None


@router.get("/audit-log", response_model=AuditLogPage)
async def list_audit_log(
    event_name: str | None = Query(default=None),
    subject_type: str | None = Query(default=None),
    since: datetime | None = Query(default=None),
    until: datetime | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=_MAX_LIMIT),
    before_seq: int | None = Query(default=None, ge=1),
    db: AsyncSession = Depends(get_session),
    session: SessionRow = Depends(current_session),
) -> AuditLogPage:
    if not await admin_service.is_superadmin(db, user_id=session.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "operator_role_required",
                "message": "Audit-log access is an operator action.",
            },
        )

    rows = await reader.query(
        db,
        event_name=event_name,
        subject_type=subject_type,
        since=since,
        until=until,
        limit=limit,
        before_seq=before_seq,
    )
    verified, reason = reader.verify_chain_page(rows)

    return AuditLogPage(
        items=[AuditLogEntry(**reader.to_dict(r)) for r in rows],
        next_before_seq=rows[-1].seq if rows else None,
        chain_verified=verified,
        chain_verify_reason=reason,
    )
