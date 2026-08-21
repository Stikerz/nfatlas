"""Outbox dispatcher — event_name → handler registry."""

from __future__ import annotations

from atlas.events import WINNER_SELECTED_V1
from atlas.outbox import dispatcher


class TestRegistry:
    def test_winner_selected_v1_is_registered(self) -> None:
        assert WINNER_SELECTED_V1 in dispatcher.HANDLERS

    def test_registered_handler_is_async_callable(self) -> None:
        handler = dispatcher.HANDLERS[WINNER_SELECTED_V1]
        assert callable(handler)
        # Async callables have __code__.co_flags & 0x100 (CO_COROUTINE) or
        # are decorated as async. Simpler: introspect via inspect.
        import inspect

        assert inspect.iscoroutinefunction(handler)
