"""Draw service.

Read-only surface + state transitions per ADR-006 §Protocol stages 3-4.

Week 6 Day 1: `close_draw` — computes tickets_hash, flips state to
`sales_closed`, emits `draw.entries_snapshot` audit event.
Week 6 Day 3: `reveal_draw` — fetches entropy, decrypts server_seed,
runs `select_winners`, flips state to `revealed`, emits `draw.revealed`
+ `draw.winner_selected` audit events.

All state changes go through `state_machine.transition` — the sole
authority on legal moves. Callers pass current + action; get back the
next state string or an IllegalTransitionError.
"""

from __future__ import annotations

import hashlib
import logging
import secrets
import uuid
from datetime import UTC, datetime

import rfc8785
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log import writer as audit
from atlas.draw import crypto as seed_crypto
from atlas.draw import reveal as reveal_algo
from atlas.draw import state_machine
from atlas.draw.entropy.protocol import EntropyProvider
from atlas.draw.entropy.provider import default_provider
from atlas.draw.models import Draw, DrawWinner
from atlas.notification.winner import notify_winner
from atlas.ticket.models import Ticket

logger = logging.getLogger("atlas.draw.service")


class DrawNotFoundError(LookupError):
    """Draw id does not exist."""


class DrawNotOpenError(RuntimeError):
    """Draw exists but is not accepting new entries."""


class DrawStateError(RuntimeError):
    """Wrapper around state_machine.IllegalTransitionError for callers
    that want a draw-service-typed error surface."""


class WinnerNotFoundError(LookupError):
    """No draw_winners row for (draw_id, ticket_id)."""


class WinnerForbiddenError(PermissionError):
    """Caller is not the winning user on the requested draw_winner row."""


class WinnerAlreadyClaimedError(RuntimeError):
    """contact_status is already 'claimed' (or beyond)."""


async def create_draw(
    session: AsyncSession,
    *,
    prize_copy: str,
    ticket_price_minor: int,
    close_time: datetime,
    draw_time: datetime,
    entries_cap: int | None = None,
    actor_operator_id: uuid.UUID,
) -> Draw:
    """Mint a fresh draw in `sales_open` per week-6-build-plan §Day 5.

    V0.5 collapses draft → committed → sales_open into a single insert
    (per week-5-build-plan §0 direction: no admin-driven creation flow
    for the earlier states). The commitment is published in the same
    breath via the `draw.committed` audit event.

    W8 (ADR-006 §Stage 1): server_seed is encrypted at rest via Fernet
    keyed from ATLAS_SERVER_SEED_KEY. Decryption happens only during
    reveal (`reveal_draw`) and public proof (`routes.get_proof`).
    """
    draw_id = uuid.uuid4()
    server_seed = secrets.token_bytes(32)
    commitment = hashlib.sha256(server_seed + draw_id.bytes).hexdigest()

    draw = Draw(
        id=draw_id,
        prize_copy=prize_copy,
        ticket_price_minor=ticket_price_minor,
        currency="NGN",
        entries_cap=entries_cap,
        close_time=close_time,
        draw_time=draw_time,
        state=state_machine.DrawState.SALES_OPEN.value,
        commitment=commitment,
        server_seed_encrypted=seed_crypto.encrypt_server_seed(server_seed),
    )
    session.add(draw)
    await session.flush()

    await audit.append(
        session,
        actor_type="operator",
        actor_id=str(actor_operator_id),
        event_name="draw.committed",
        subject_type="draw",
        subject_id=str(draw_id),
        payload={
            "draw_id": str(draw_id),
            "commitment": commitment,
            "prize_copy": prize_copy,
            "ticket_price_minor": ticket_price_minor,
            "close_time": close_time.astimezone(UTC).isoformat(),
            "draw_time": draw_time.astimezone(UTC).isoformat(),
            "entries_cap": entries_cap,
        },
    )
    return draw


async def get(session: AsyncSession, *, draw_id: uuid.UUID) -> Draw:
    row = (
        await session.execute(select(Draw).where(Draw.id == draw_id))
    ).scalar_one_or_none()
    if row is None:
        raise DrawNotFoundError(str(draw_id))
    return row


async def list_active(session: AsyncSession) -> list[Draw]:
    """All draws currently in `sales_open`. V0.5 seeds exactly one."""
    rows = (
        await session.execute(
            select(Draw).where(Draw.state == "sales_open").order_by(Draw.close_time)
        )
    ).scalars().all()
    return list(rows)


async def is_sales_open(session: AsyncSession, *, draw_id: uuid.UUID) -> bool:
    """True iff the draw exists and is in `sales_open`."""
    state = (
        await session.execute(select(Draw.state).where(Draw.id == draw_id))
    ).scalar_one_or_none()
    return state == "sales_open"


async def close_draw(session: AsyncSession, *, draw_id: uuid.UUID) -> Draw:
    """Snapshot the ticket list, compute the tickets_hash, flip state
    to `sales_closed`. Emits `draw.entries_snapshot` audit event with
    the ticket count + hash.

    Idempotent: calling close_draw on an already-closed draw returns
    the existing row (tickets_hash unchanged, no duplicate audit event).
    Calling on any other state raises DrawStateError.
    """
    draw = await get(session, draw_id=draw_id)

    if draw.state == state_machine.DrawState.SALES_CLOSED.value:
        return draw

    try:
        next_state = state_machine.transition(
            draw.state, state_machine.DrawAction.CLOSE.value
        )
    except state_machine.IllegalTransitionError as exc:
        raise DrawStateError(str(exc)) from exc

    ticket_ids = (
        await session.execute(
            select(Ticket.id)
            .where(Ticket.draw_id == draw_id)
            .order_by(Ticket.ticket_number)
        )
    ).scalars().all()
    tickets_hash = hashlib.sha256(
        rfc8785.dumps([str(t) for t in ticket_ids])
    ).hexdigest()

    draw.tickets_hash = tickets_hash
    draw.state = next_state
    draw.updated_at = datetime.now(UTC)
    await session.flush()

    await audit.append(
        session,
        actor_type="operator",
        actor_id="admin.close_draw",
        event_name="draw.entries_snapshot",
        subject_type="draw",
        subject_id=str(draw_id),
        payload={
            "draw_id": str(draw_id),
            "ticket_count": len(ticket_ids),
            "tickets_hash": tickets_hash,
        },
    )
    return draw


async def reveal_draw(
    session: AsyncSession,
    *,
    draw_id: uuid.UUID,
    entropy_provider: EntropyProvider | None = None,
    reserves: int = 5,
) -> Draw:
    """Fetch entropy, run winner selection, persist winners + proof.

    Idempotent: reveal on an already-revealed draw returns the existing
    row without re-fetching entropy or re-selecting winners. Reveal on
    any other state raises DrawStateError.

    Caller owns the transaction (route calls session.commit()).
    """
    draw = await get(session, draw_id=draw_id)

    if draw.state == state_machine.DrawState.REVEALED.value:
        return draw

    try:
        next_state = state_machine.transition(
            draw.state, state_machine.DrawAction.REVEAL.value
        )
    except state_machine.IllegalTransitionError as exc:
        raise DrawStateError(str(exc)) from exc

    if draw.tickets_hash is None:
        # Should be impossible from the state machine (sales_closed
        # implies close_draw ran and set tickets_hash) — but a defensive
        # guard catches manual DB tampering.
        raise DrawStateError(
            f"draw {draw_id} is sales_closed but has no tickets_hash"
        )

    ticket_ids = (
        await session.execute(
            select(Ticket.id)
            .where(Ticket.draw_id == draw_id)
            .order_by(Ticket.ticket_number)
        )
    ).scalars().all()

    provider = entropy_provider or default_provider()
    entropy_inputs = await provider.fetch(draw.close_time)

    server_seed_bytes = seed_crypto.decrypt_server_seed(draw.server_seed_encrypted)

    winner_ticket_ids = reveal_algo.select_winners(
        server_seed=server_seed_bytes,
        entropy=entropy_inputs.combined_bytes,
        tickets_hash=bytes.fromhex(draw.tickets_hash),
        ordered_ticket_ids=list(ticket_ids),
        reserves=reserves,
    )

    # Resolve winner user_ids from the ticket rows in one query.
    owner_rows = (
        await session.execute(
            select(Ticket.id, Ticket.user_id).where(
                Ticket.id.in_(winner_ticket_ids)
            )
        )
    ).all()
    ticket_owner_map: dict[uuid.UUID, uuid.UUID] = {
        ticket_id: user_id for ticket_id, user_id in owner_rows
    }

    now = datetime.now(UTC)
    draw.state = next_state
    draw.revealed_at = now
    draw.updated_at = now
    draw.reveal_inputs = {
        "mode": entropy_inputs.mode,
        "bitcoin_hash": entropy_inputs.bitcoin.block_hash,
        "bitcoin_height": entropy_inputs.bitcoin.block_height,
        "bitcoin_timestamp": entropy_inputs.bitcoin.block_timestamp,
        "drand_round": entropy_inputs.drand.round,
        "drand_randomness": entropy_inputs.drand.randomness,
        "drand_signature": entropy_inputs.drand.signature,
        "verified_at": entropy_inputs.verified_at.isoformat(),
    }

    winner_rows: list[DrawWinner] = []
    for position, ticket_id in enumerate(winner_ticket_ids):
        row = DrawWinner(
            draw_id=draw_id,
            position=position,
            ticket_id=ticket_id,
            user_id=ticket_owner_map[ticket_id],
            is_primary=(position == 0),
        )
        session.add(row)
        winner_rows.append(row)

    await session.flush()

    # `draw.revealed` — summary event with proof inputs.
    await audit.append(
        session,
        actor_type="operator",
        actor_id="admin.reveal_draw",
        event_name="draw.revealed",
        subject_type="draw",
        subject_id=str(draw_id),
        payload={
            "draw_id": str(draw_id),
            "commitment": draw.commitment,
            "server_seed": server_seed_bytes.hex(),
            "tickets_hash": draw.tickets_hash,
            "ticket_count": len(ticket_ids),
            "reserves": reserves,
            **draw.reveal_inputs,
        },
    )

    # One `draw.winner_selected` per winner in position order.
    for row in winner_rows:
        await audit.append(
            session,
            actor_type="operator",
            actor_id="admin.reveal_draw",
            event_name="draw.winner_selected",
            subject_type="draw_winner",
            subject_id=str(row.id),
            payload={
                "draw_id": str(draw_id),
                "position": row.position,
                "is_primary": row.is_primary,
                "ticket_id": str(row.ticket_id),
                "user_id_hash": hashlib.sha256(
                    str(row.user_id).encode("utf-8")
                ).hexdigest(),
            },
        )

    # Notification — V0.5 shortcut per §0 ask 5. Try/except each call so
    # a mailhog outage does NOT abort a reveal. The
    # notification.winner_selected audit event fires INSIDE notify_winner
    # before the delivery attempt, so the trail records "we tried" even
    # if SMTP is down.
    for row in winner_rows:
        try:
            await notify_winner(
                session,
                user_id=row.user_id,
                draw_id=draw_id,
                position=row.position,
                is_primary=row.is_primary,
                prize_copy=draw.prize_copy,
            )
        except Exception:
            logger.exception(
                "winner notification failed (draw=%s user=%s position=%s)",
                draw_id,
                row.user_id,
                row.position,
            )

    return draw


async def list_winners(
    session: AsyncSession, *, draw_id: uuid.UUID
) -> list[DrawWinner]:
    rows = (
        await session.execute(
            select(DrawWinner)
            .where(DrawWinner.draw_id == draw_id)
            .order_by(DrawWinner.position)
        )
    ).scalars().all()
    return list(rows)


async def claim_prize(
    session: AsyncSession,
    *,
    draw_id: uuid.UUID,
    ticket_id: uuid.UUID,
    claimant_user_id: uuid.UUID,
) -> DrawWinner:
    """Winner marks their prize as claimed. V0.5 minimum: state
    advances `pending → claimed` (skipping the operator `contacted`
    intermediate — Week 7 UX ties directly).

    Ownership: caller must be the user_id on the draw_winners row.
    """
    winner = (
        await session.execute(
            select(DrawWinner).where(
                DrawWinner.draw_id == draw_id,
                DrawWinner.ticket_id == ticket_id,
            )
        )
    ).scalar_one_or_none()

    if winner is None:
        raise WinnerNotFoundError(f"no winner for draw={draw_id} ticket={ticket_id}")
    if winner.user_id != claimant_user_id:
        raise WinnerForbiddenError(str(winner.id))
    if winner.contact_status in ("claimed", "declined", "expired"):
        raise WinnerAlreadyClaimedError(winner.contact_status)

    winner.contact_status = "claimed"
    await session.flush()

    await audit.append(
        session,
        actor_type="user",
        actor_id=str(claimant_user_id),
        event_name="draw.winner_claimed",
        subject_type="draw_winner",
        subject_id=str(winner.id),
        payload={
            "draw_id": str(draw_id),
            "ticket_id": str(ticket_id),
            "position": winner.position,
            "is_primary": winner.is_primary,
        },
    )
    return winner


async def ordered_ticket_ids(
    session: AsyncSession, *, draw_id: uuid.UUID
) -> list[uuid.UUID]:
    """Deterministic ticket ordering used for tickets_hash + reveal.

    Kept as a service function so the proof endpoint (Day 4) reads the
    same ordering that close_draw + reveal_draw consume — no risk of
    two orderings diverging.
    """
    return list(
        (
            await session.execute(
                select(Ticket.id)
                .where(Ticket.draw_id == draw_id)
                .order_by(Ticket.ticket_number)
            )
        ).scalars().all()
    )
