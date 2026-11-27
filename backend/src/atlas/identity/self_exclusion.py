"""Self-exclusion — sole writer to `self_exclusions` (ADR-010 Phase A).

Per the ADR-010 amendment of 2026-11-24. **Phase A only.** The registry is
keyed on `user_id`, not BVN: ADR-007 (KYC) is unbuilt and BVN is collected
nowhere, so there is no BVN to hash. `bvn_hash` stays NULL until Phase B
backfills it.

What Phase A guarantees, precisely — the consumer copy depends on this:

  - A user who excludes IS stopped. Account closed, every session revoked,
    no ticket obtainable by any path.
  - That user CAN still register again with a different email and phone.
    Only BVN closes that door, and BVN needs KYC.

Copy must not claim cross-account enforcement before Phase B. The sentence
that wrongly claimed it is recorded in REVIEW-002 §6.1.

`exclude()` is one transaction: write the row, close the account, revoke
every session, audit. Idempotent on `user_id` — a replay returns the
existing row and emits no second audit entry.

No reversal exists, by design. There is no `unexclude`, no `revoked_at`
column, and no admin control. V1 exclusion is permanent and the absence of
the capability is the enforcement.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log import writer as audit
from atlas.identity import session_service
from atlas.identity.models import SelfExclusion, User


class UnknownUserError(LookupError):
    """user_id does not exist."""


async def is_excluded(session: AsyncSession, *, user_id: uuid.UUID) -> bool:
    """The enforcement predicate. Cheap PK lookup.

    Called from `ticket.service.issue_paid` and `skill.service.next_question`
    per the ADR-010 amendment §Enforcement points amended. Kept free of any
    side effect so it is safe to call on every purchase.
    """
    return (
        await session.get(SelfExclusion, user_id)
    ) is not None


async def get(
    session: AsyncSession, *, user_id: uuid.UUID
) -> SelfExclusion | None:
    """Read one exclusion row, or None. For the admin read-only surface."""
    return await session.get(SelfExclusion, user_id)


async def list_all(session: AsyncSession) -> list[SelfExclusion]:
    """Every exclusion, newest first. Admin read-only; no un-exclude path."""
    rows = (
        await session.execute(
            select(SelfExclusion).order_by(SelfExclusion.excluded_at.desc())
        )
    ).scalars().all()
    return list(rows)


async def exclude(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    excluded_by: str = "user_self",
    excluded_by_id: uuid.UUID | None = None,
    reason: str | None = None,
    notes: str | None = None,
) -> tuple[SelfExclusion, int]:
    """Permanently exclude a user. Sole INSERT path for `self_exclusions`.

    Returns `(row, sessions_revoked)`. The count is returned rather than
    recomputed by the caller so the API response can state what actually
    happened — on an idempotent replay it is 0, because the sessions were
    already killed the first time.

    One transaction: registry row -> users.status='closed' -> revoke every
    session -> audit. The caller commits.

    Idempotent: if the user is already excluded, returns the existing row
    with a count of 0, without re-closing the account, re-revoking
    sessions, or emitting a second `self_exclusion.activated` event.

    NOTE (ADR-010 amendment §3): any wallet balance is deliberately NOT
    refunded here. There is no Paystack refund call and no escheatment
    policy. The balance is held on the closed account for support to
    resolve. Emitting a refund the system cannot perform is the defect the
    amendment exists to correct.
    """
    user = await session.get(User, user_id)
    if user is None:
        raise UnknownUserError(str(user_id))

    existing = await session.get(SelfExclusion, user_id)
    if existing is not None:
        return existing, 0

    row = SelfExclusion(
        user_id=user_id,
        bvn_hash=None,  # Phase B backfills; see module docstring.
        excluded_by=excluded_by,
        excluded_by_id=excluded_by_id,
        reason=reason,
        notes=notes,
    )
    session.add(row)
    await session.flush()

    # Login enforcement is already satisfied by this: session_service
    # refuses any user whose status is not 'active'. This is the first
    # writer of 'closed' — the value has been in the CHECK constraint,
    # unused, since migration 0001.
    user.status = "closed"
    await session.flush()

    revoked = await session_service.revoke_all_for_user(
        session, user_id=user_id, revoked_by="self_exclusion"
    )

    await audit.append(
        session,
        actor_type="user" if excluded_by == "user_self" else "operator",
        actor_id=str(excluded_by_id or user_id),
        event_name="self_exclusion.activated",
        subject_type="user",
        subject_id=str(user_id),
        payload={
            "user_id": str(user_id),
            "excluded_by": excluded_by,
            "excluded_by_id": str(excluded_by_id) if excluded_by_id else None,
            "sessions_revoked": revoked,
            "reason": reason,
            # Recorded so an auditor can tell Phase A rows from Phase B
            # rows without inspecting bvn_hash for NULL.
            "bvn_enforced": False,
        },
    )
    return row, revoked
