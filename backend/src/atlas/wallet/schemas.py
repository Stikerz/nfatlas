"""Wallet request/response Pydantic schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class WalletBalance(BaseModel):
    """Shape returned by GET /api/v1/users/me/wallet — the balance chip."""

    balance_minor: int
    currency: str
    updated_at: datetime
