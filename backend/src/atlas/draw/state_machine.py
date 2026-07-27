"""Draw state machine (ADR-006 §Protocol stages).

Pure functions. `transition(current, action)` returns the target state
or raises `IllegalTransitionError`. No I/O, no shared mutable state —
the DB row is updated by the caller (draw.service) after the
transition function OK's the move.

State graph:

    draft ── commit ──▶ committed ── open_sale ──▶ sales_open
                                                      │
                                                      close
                                                      ▼
                                                  sales_closed ── reveal ──▶ revealed

V0.5 seeds draws directly into `sales_open` (see infrastructure/
scripts/seed_v0_5.py); the `draft → committed → sales_open` prefix
exists in the state enum for V1 admin-driven draw creation, but only
the `sales_open → sales_closed → revealed` moves are exercised in the
demo path.
"""

from __future__ import annotations

from enum import StrEnum


class DrawState(StrEnum):
    DRAFT = "draft"
    COMMITTED = "committed"
    SALES_OPEN = "sales_open"
    SALES_CLOSED = "sales_closed"
    REVEALED = "revealed"


class DrawAction(StrEnum):
    COMMIT = "commit"
    OPEN_SALE = "open_sale"
    CLOSE = "close"
    REVEAL = "reveal"


# Table-driven: (current_state, action) → next_state.
# Any pair not in this table is illegal.
_TRANSITIONS: dict[tuple[DrawState, DrawAction], DrawState] = {
    (DrawState.DRAFT, DrawAction.COMMIT): DrawState.COMMITTED,
    (DrawState.COMMITTED, DrawAction.OPEN_SALE): DrawState.SALES_OPEN,
    (DrawState.SALES_OPEN, DrawAction.CLOSE): DrawState.SALES_CLOSED,
    (DrawState.SALES_CLOSED, DrawAction.REVEAL): DrawState.REVEALED,
}


class IllegalTransitionError(RuntimeError):
    """The requested action is not legal from the current state."""

    def __init__(self, current: str, action: str) -> None:
        super().__init__(
            f"illegal transition: cannot {action} from state {current!r}"
        )
        self.current = current
        self.action = action


def transition(current: str, action: str) -> str:
    """Return the target state string. Raises IllegalTransitionError
    if the move is not on the state graph.

    Accepts plain strings (as read from the DB) rather than enum values
    to keep the call sites terse; the enums exist for callers that want
    them but are not enforced.
    """
    try:
        current_state = DrawState(current)
        action_enum = DrawAction(action)
    except ValueError as exc:
        raise IllegalTransitionError(current=current, action=action) from exc

    next_state = _TRANSITIONS.get((current_state, action_enum))
    if next_state is None:
        raise IllegalTransitionError(current=current, action=action)
    return next_state.value


def is_terminal(state: str) -> bool:
    """True iff the state is a terminal state — no further transitions.

    V0.5 has one terminal: `revealed`. `sales_closed` is intermediate
    (reveal follows). `draft` has an outbound edge (commit). All others
    have outbound edges.
    """
    return state == DrawState.REVEALED.value
