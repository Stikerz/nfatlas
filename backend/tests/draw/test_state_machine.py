"""atlas.draw.state_machine — pure transition unit tests.

The state machine is the sole authority on legal draw moves. If a
transition is added or removed, both the table and these tests must
change in lock-step.
"""

from __future__ import annotations

import pytest

from atlas.draw import state_machine


class TestLegalTransitions:
    @pytest.mark.parametrize(
        ("current", "action", "expected"),
        [
            ("draft", "commit", "committed"),
            ("committed", "open_sale", "sales_open"),
            ("sales_open", "close", "sales_closed"),
            ("sales_closed", "reveal", "revealed"),
        ],
    )
    def test_valid_move(self, current: str, action: str, expected: str) -> None:
        assert state_machine.transition(current, action) == expected


class TestIllegalTransitions:
    @pytest.mark.parametrize(
        ("current", "action"),
        [
            # Skipping stages.
            ("draft", "open_sale"),
            ("draft", "close"),
            ("draft", "reveal"),
            ("committed", "close"),
            ("committed", "reveal"),
            ("sales_open", "reveal"),
            ("sales_open", "open_sale"),   # already open
            ("sales_closed", "close"),     # already closed
            # Reverse moves — never legal.
            ("committed", "commit"),
            ("sales_open", "commit"),
            ("sales_closed", "open_sale"),
            # Terminal state — no outbound moves.
            ("revealed", "close"),
            ("revealed", "reveal"),
            ("revealed", "commit"),
        ],
    )
    def test_raises(self, current: str, action: str) -> None:
        with pytest.raises(state_machine.IllegalTransitionError):
            state_machine.transition(current, action)

    def test_unknown_state_raises(self) -> None:
        with pytest.raises(state_machine.IllegalTransitionError):
            state_machine.transition("not-a-state", "close")

    def test_unknown_action_raises(self) -> None:
        with pytest.raises(state_machine.IllegalTransitionError):
            state_machine.transition("sales_open", "not-an-action")


class TestIsTerminal:
    def test_revealed_is_terminal(self) -> None:
        assert state_machine.is_terminal("revealed") is True

    @pytest.mark.parametrize(
        "state", ["draft", "committed", "sales_open", "sales_closed"]
    )
    def test_others_are_not_terminal(self, state: str) -> None:
        assert state_machine.is_terminal(state) is False
