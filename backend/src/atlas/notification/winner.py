"""Winner notification — mailhog stub for V0.5.

W8 Day 3: called by the outbox worker (not reveal_draw directly).
`deliver_from_payload` reads the WINNER_SELECTED_V1 payload, emits the
`notification.winner_selected` audit event BEFORE the delivery attempt
(audit-before-delivery discipline), then calls mailhog_sender. Raising
an exception here signals the worker to retry with backoff.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log import writer as audit
from atlas.events import WinnerSelectedPayload
from atlas.identity import mailhog_sender
from atlas.identity.models import User


async def deliver_from_payload(
    session: AsyncSession, payload: dict[str, object]
) -> None:
    """Consume WINNER_SELECTED_V1 → audit event + mailhog delivery.

    Ordering: audit event first (records "we tried" even under SMTP
    outage), then mailhog delivery. Any exception from either step
    propagates to the worker for retry per ADR-002 §Processing model.
    """
    parsed = WinnerSelectedPayload.model_validate(payload)

    await audit.append(
        session,
        actor_type="system",
        actor_id="outbox.worker",
        event_name="notification.winner_selected",
        subject_type="user",
        subject_id=str(parsed.user_id),
        payload={
            "user_id": str(parsed.user_id),
            "draw_id": str(parsed.draw_id),
            "position": parsed.position,
            "is_primary": parsed.is_primary,
            "channel": "mailhog",
        },
    )

    user = await session.get(User, parsed.user_id)
    if user is None:
        # FK guarantees existence at reveal time; guard against manual
        # data cleanup between reveal and worker pickup.
        return

    subject_line = (
        "You won a draw" if parsed.is_primary else "You're a reserve winner"
    )
    reserve_line = "" if parsed.is_primary else (
        f"\n\nYou are reserve #{parsed.position}. If the primary winner does "
        "not claim, we'll be in touch."
    )
    body = (
        f"Congratulations!\n\n"
        f"Draw: {parsed.prize_copy}\n"
        f"Draw ID: {parsed.draw_id}\n"
        f"Position: {parsed.position} "
        f"({'primary' if parsed.is_primary else 'reserve'})"
        f"{reserve_line}\n\n"
        f"We'll be in touch about claim next steps."
    )

    await mailhog_sender.send_notification(
        to_email=user.email, subject=subject_line, body=body
    )
