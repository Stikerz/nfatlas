"""Winner notification — Mailhog stub for V0.5.

Called from `atlas.draw.service.reveal_draw` for the primary winner +
each reserve. Wrapped in try/except at the caller so SMTP failures
never abort a reveal.

Audit event `notification.winner_selected` is emitted BEFORE the
delivery attempt so the audit trail records "we tried" even if the
mailhog is down.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log import writer as audit
from atlas.identity import mailhog_sender
from atlas.identity.models import User


async def notify_winner(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    draw_id: uuid.UUID,
    position: int,
    is_primary: bool,
    prize_copy: str,
) -> None:
    """Emit audit event + fire-and-log mailhog delivery.

    Caller (reveal_draw) wraps in try/except — this function itself
    lets delivery exceptions propagate so tests can assert them, but
    audit-log write happens first regardless.
    """
    user = await session.get(User, user_id)
    subject_line = "You won a draw" if is_primary else "You're a reserve winner"

    await audit.append(
        session,
        actor_type="system",
        actor_id="draw.reveal",
        event_name="notification.winner_selected",
        subject_type="user",
        subject_id=str(user_id),
        payload={
            "user_id": str(user_id),
            "draw_id": str(draw_id),
            "position": position,
            "is_primary": is_primary,
            "channel": "mailhog",
        },
    )

    if user is None:
        # Impossible under the FK, but the guard means a manual data
        # cleanup targeting the referenced row cannot crash a reveal.
        return

    reserve_line = "" if is_primary else (
        f"\n\nYou are reserve #{position}. If the primary winner does "
        "not claim, we'll be in touch."
    )
    body = (
        f"Congratulations!\n\n"
        f"Draw: {prize_copy}\n"
        f"Draw ID: {draw_id}\n"
        f"Position: {position} ({'primary' if is_primary else 'reserve'})"
        f"{reserve_line}\n\n"
        f"We'll be in touch about claim next steps."
    )

    await mailhog_sender.send_notification(
        to_email=user.email, subject=subject_line, body=body
    )
