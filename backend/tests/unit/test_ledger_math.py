"""Unit tests for the ledger draft-balancing math.

Tests the application-side pre-check that runs before INSERT. The DB
trigger is the source of truth at COMMIT; this pre-check gives callers
a typed error message before the round-trip.
"""

from __future__ import annotations

import uuid

import pytest

from atlas.wallet.ledger import (
    LedgerEntryDraft,
    UnbalancedTransactionError,
    _net_minor,
)

_ACCT_A = uuid.uuid4()
_ACCT_B = uuid.uuid4()


def _draft(direction: str, amount: int, account: uuid.UUID = _ACCT_A) -> LedgerEntryDraft:
    return LedgerEntryDraft(
        account_id=account,
        direction=direction,  # type: ignore[arg-type]
        amount_minor=amount,
        description="test entry",
    )


class TestNetMinor:
    def test_single_credit_returns_positive(self) -> None:
        assert _net_minor([_draft("C", 100)]) == 100

    def test_single_debit_returns_negative(self) -> None:
        assert _net_minor([_draft("D", 100)]) == -100

    def test_balanced_pair_returns_zero(self) -> None:
        entries = [_draft("D", 500, _ACCT_A), _draft("C", 500, _ACCT_B)]
        assert _net_minor(entries) == 0

    def test_multi_side_transaction_balances(self) -> None:
        # e.g. deposit 500 with fee split: user +500, clearing -500, operator_revenue -25, clearing +25
        entries = [
            _draft("D", 500, _ACCT_A),
            _draft("C", 500, _ACCT_B),
            _draft("D", 25, _ACCT_A),
            _draft("C", 25, _ACCT_B),
        ]
        assert _net_minor(entries) == 0

    def test_unbalanced_returns_delta(self) -> None:
        entries = [_draft("D", 500, _ACCT_A), _draft("C", 499, _ACCT_B)]
        assert _net_minor(entries) == -1


class TestDraftValidation:
    def test_zero_amount_rejected(self) -> None:
        with pytest.raises(ValueError, match="amount_minor must be > 0"):
            _draft("D", 0)

    def test_negative_amount_rejected(self) -> None:
        with pytest.raises(ValueError, match="amount_minor must be > 0"):
            _draft("D", -1)

    def test_invalid_direction_rejected(self) -> None:
        with pytest.raises(ValueError, match="direction must be 'D' or 'C'"):
            LedgerEntryDraft(
                account_id=_ACCT_A,
                direction="X",  # type: ignore[arg-type]
                amount_minor=100,
                description="bad direction",
            )


class TestUnbalancedTransactionError:
    """The exception type is part of the public API surface used by wallet.service."""

    def test_is_a_value_error(self) -> None:
        assert issubclass(UnbalancedTransactionError, ValueError)
