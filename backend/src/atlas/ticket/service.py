"""Ticket service — sole INSERT path for `tickets` (grep-enforced Day 5).

`_mint_ticket` allocates a monotonically-increasing `ticket_number`
per draw. Concurrency contract: a `SELECT ... FROM draws WHERE id = :d
FOR UPDATE` serializes ticket allocation within a draw. Any concurrent
minter waits until the first one commits, then reads the next number.
V0.5 is single-user so no real contention; the lock is correctness for
V1 multi-user demos.

`issue_paid` consumes a skill-question entitlement in the same
transaction as the mint. The entitlement was created by
atlas.skill.service.verify_answer on a correct answer; consumption
marks `consumed_at` on the attempt row so the entitlement is
single-use even under retry.

`issue_free` (Day 4) transcribes a free-entry slip and mints a ticket
with `entry_source='free'`; same `_mint_ticket` underneath.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log import writer as audit
from atlas.skill.models import SkillQuestionAttempt
from atlas.ticket.models import Ticket


class EntitlementNotFoundError(LookupError):
    """attempt_id (entitlement) unknown."""


class EntitlementForbiddenError(PermissionError):
    """Entitlement belongs to another user."""


class EntitlementInvalidError(RuntimeError):
    """Entitlement is not-correct / expired / already-consumed / for a
    different draw. One error class — the audit-log payload disambiguates."""


async def _next_ticket_number(
    session: AsyncSession, *, draw_id: uuid.UUID
) -> int:
    """Serialized allocation of the next ticket_number for a draw.

    Locks the draw row with SELECT FOR UPDATE so a concurrent minter
    waits its turn. Then computes MAX(ticket_number)+1 across the
    committed + in-flight state visible to this transaction.
    """
    # Row-lock the draw. The result is discarded — we only need the lock
    # side-effect. Postgres releases the lock at COMMIT / ROLLBACK.
    await session.execute(
        text("SELECT 1 FROM draws WHERE id = :d FOR UPDATE"),
        {"d": str(draw_id)},
    )
    current_max = (
        await session.execute(
            select(func.coalesce(func.max(Ticket.ticket_number), 0)).where(
                Ticket.draw_id == draw_id
            )
        )
    ).scalar_one()
    return int(current_max) + 1


async def _mint_ticket(
    session: AsyncSession,
    *,
    draw_id: uuid.UUID,
    user_id: uuid.UUID,
    entry_source: str,
    external_ref: str | None,
    idempotency_key: str,
) -> Ticket:
    """Sole INSERT path. Callers: issue_paid, issue_free.

    Idempotency: `tickets.idempotency_key` UNIQUE. A replay with the
    same key returns the existing row without allocating a new number.
    """
    existing = (
        await session.execute(
            select(Ticket).where(Ticket.idempotency_key == idempotency_key)
        )
    ).scalar_one_or_none()
    if existing is not None:
        return existing

    number = await _next_ticket_number(session, draw_id=draw_id)
    ticket = Ticket(
        draw_id=draw_id,
        user_id=user_id,
        ticket_number=number,
        entry_source=entry_source,
        external_ref=external_ref,
        idempotency_key=idempotency_key,
    )
    session.add(ticket)
    await session.flush()

    await audit.append(
        session,
        actor_type="system" if entry_source == "paid" else "operator",
        actor_id="payment.webhook" if entry_source == "paid" else "admin.free_entry",
        event_name="ticket.issued",
        subject_type="ticket",
        subject_id=str(ticket.id),
        payload={
            "user_id": str(user_id),
            "draw_id": str(draw_id),
            "ticket_number": number,
            "entry_source": entry_source,
            "external_ref": external_ref,
        },
    )
    return ticket


async def issue_paid(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    draw_id: uuid.UUID,
    payment_intent_id: uuid.UUID,
    entitlement_id: uuid.UUID,
) -> Ticket:
    """Called from the webhook charge.success handler with
    metadata.purpose == 'ticket'. Consumes the entitlement, then mints
    the ticket. Idempotent by payment_intent_id — replay is a no-op."""
    await _validate_and_consume_entitlement(
        session,
        entitlement_id=entitlement_id,
        expected_user_id=user_id,
        expected_draw_id=draw_id,
    )

    ticket = await _mint_ticket(
        session,
        draw_id=draw_id,
        user_id=user_id,
        entry_source="paid",
        external_ref=str(payment_intent_id),
        # Bind idempotency to the payment_intent_id so a retried webhook
        # delivers the same ticket, and a re-purchase creates a new one.
        idempotency_key=f"ticket:paid:{payment_intent_id}",
    )

    await audit.append(
        session,
        actor_type="system",
        actor_id="payment.webhook",
        event_name="ticket.paid_purchase_completed",
        subject_type="payment_intent",
        subject_id=str(payment_intent_id),
        payload={
            "user_id": str(user_id),
            "draw_id": str(draw_id),
            "ticket_id": str(ticket.id),
            "ticket_number": ticket.ticket_number,
            "entitlement_id": str(entitlement_id),
        },
    )
    return ticket


async def check_entitlement(
    session: AsyncSession,
    *,
    entitlement_id: uuid.UUID,
    expected_user_id: uuid.UUID,
    expected_draw_id: uuid.UUID,
) -> SkillQuestionAttempt:
    """Read-only validation. Raises the typed errors above without any
    state change. Called from POST /tickets/purchase so the user gets
    fast feedback on a bad entitlement instead of a silent checkout
    failure."""
    attempt = await session.get(SkillQuestionAttempt, entitlement_id)
    if attempt is None:
        raise EntitlementNotFoundError(str(entitlement_id))
    if attempt.user_id != expected_user_id:
        raise EntitlementForbiddenError(str(entitlement_id))
    if attempt.draw_id != expected_draw_id:
        raise EntitlementInvalidError("draw_mismatch")
    if attempt.is_correct is not True:
        raise EntitlementInvalidError("not_correct")
    if attempt.consumed_at is not None:
        raise EntitlementInvalidError("already_consumed")
    if (
        attempt.entitlement_expires_at is None
        or attempt.entitlement_expires_at <= datetime.now(UTC)
    ):
        raise EntitlementInvalidError("expired")
    return attempt


async def _validate_and_consume_entitlement(
    session: AsyncSession,
    *,
    entitlement_id: uuid.UUID,
    expected_user_id: uuid.UUID,
    expected_draw_id: uuid.UUID,
) -> SkillQuestionAttempt:
    """Called by the webhook path: re-validates + marks consumed_at.

    The purchase-time check_entitlement is not a substitute — a slow
    Paystack round-trip could see the entitlement expire between check
    and consume, so the webhook path validates again against the
    committed state at consumption time.
    """
    attempt = await check_entitlement(
        session,
        entitlement_id=entitlement_id,
        expected_user_id=expected_user_id,
        expected_draw_id=expected_draw_id,
    )
    attempt.consumed_at = datetime.now(UTC)
    await session.flush()
    return attempt


async def list_for_user(
    session: AsyncSession, *, user_id: uuid.UUID
) -> list[Ticket]:
    """User's tickets across all draws, newest first."""
    rows = (
        await session.execute(
            select(Ticket)
            .where(Ticket.user_id == user_id)
            .order_by(Ticket.issued_at.desc())
        )
    ).scalars().all()
    return list(rows)
