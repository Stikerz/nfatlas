"""Event-name constants + pydantic payload schemas for outbox events.

Every outbox-eligible event is declared here. `atlas.outbox.writer.emit`
validates the payload against `EVENT_SCHEMAS[event_name]` before insert
so a producer + consumer contract violation fails at the producer, not
in the worker.

Versioning: event names carry a `.vN` suffix (ADR-002 §Forward-compat
invariants). Breaking payload changes require a new version + new
constant + new schema class + new consumer registration.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict

# Named for the producing domain, not the consumer: a second consumer (a public
# surface update alongside the email) must not require renaming the event.
# See docs/events.md §Naming and emission rules.
WINNER_SELECTED_V1 = "draw.winner_selected.v1"


class WinnerSelectedPayload(BaseModel):
    """Payload for `draw.winner_selected.v1`.

    Contains no PII beyond `user_id` (a UUID). The worker re-hydrates
    the winner's email at delivery time via the identity module — see
    Day 3 winner-notification producer migration.
    """

    model_config = ConfigDict(extra="forbid")

    draw_id: uuid.UUID
    winner_id: uuid.UUID
    ticket_id: uuid.UUID
    user_id: uuid.UUID
    position: int
    is_primary: bool
    prize_copy: str


EVENT_SCHEMAS: dict[str, type[BaseModel]] = {
    WINNER_SELECTED_V1: WinnerSelectedPayload,
}
