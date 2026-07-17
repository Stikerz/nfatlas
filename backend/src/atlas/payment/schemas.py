"""Payment request/response Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PaymentMethodStr = Literal["card", "bank_transfer", "ussd", "mobile_money"]


class CreateIntentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount_minor: int = Field(gt=0, description="Amount in kobo (NGN minor units).")
    method: PaymentMethodStr = "card"
    description: str = Field(default="", max_length=200)


class CreateIntentResponse(BaseModel):
    payment_intent_id: uuid.UUID
    vendor_reference: str
    checkout_url: str | None
    amount_minor: int
    currency: str
    status: str
    expires_at: datetime | None
