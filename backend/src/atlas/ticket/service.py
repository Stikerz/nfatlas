"""Ticket service — sole INSERT path for `tickets` (grep-enforced Day 5).

`_mint_ticket` allocates a monotonically-increasing `ticket_number`
per draw. Concurrency contract: a `SELECT ... FROM draws WHERE id = :d
FOR UPDATE` serializes ticket allocation within a draw. Any concurrent
minter waits until the first one commits, then reads the next number.
V0.5 is single-user so no real contention; the lock is correctness for
V1 multi-user demos.

`issue_paid` mints against a confirmed payment. The skill-question
entitlement it used to consume was removed on 2026-11-26 (AMEND-003):
the skill question bought Atlas nothing under the governing State law,
so the purchase is gated only on an open draw and a buyer who is not
self-excluded. The `skill_question_attempts` table is retained for the
ADR-005 audit chain — see the `atlas.skill` package docstring.

The free-entry route (`issue_free`, W5 Day 4) was unwired on
2026-11-23 — see the `atlas.ticket.models` docstring for why the
`free_entry_slips` table and the `entry_source='free'` enum value are
deliberately retained.
"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log import writer as audit
from atlas.identity import self_exclusion
from atlas.ticket.models import Ticket


class SelfExcludedError(RuntimeError):
    """The buyer is self-excluded (ADR-010). No ticket may be issued."""


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
    """Sole INSERT path. Sole caller: issue_paid.

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

    # `issue_paid` is the only live caller since the free route was
    # unwired, so the actor is always the webhook. Restoring `issue_free`
    # restores the operator branch alongside it.
    await audit.append(
        session,
        actor_type="system",
        actor_id="payment.webhook",
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
) -> Ticket:
    """Called from the webhook charge.success handler with
    metadata.purpose == 'ticket'. Mints the ticket. Idempotent by
    payment_intent_id — replay is a no-op.

    ADR-010 amendment §Enforcement points: the exclusion check lives here,
    not only on the purchase route. The webhook reaches this function
    without passing through the route, and a user who excluded between
    checkout and capture must not receive a ticket. This is now the ONLY
    eligibility check on the mint path — the skill entitlement that used
    to sit beside it was removed on 2026-11-26 (AMEND-003).
    """
    if await self_exclusion.is_excluded(session, user_id=user_id):
        raise SelfExcludedError(str(user_id))

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
        },
    )
    return ticket


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
