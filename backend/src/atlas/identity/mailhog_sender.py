"""Dev-only OTP delivery via Mailhog SMTP (V0.5 stub for real SMS).

Address discipline: `+234NNNNNNNNNN@sms-mock.local`. Founder inspects codes
at http://localhost:8025 (Mailhog HTTP UI).

Wire format:
    From:    otp@atlas.dev
    To:      +2348030000000@sms-mock.local
    Subject: Atlas OTP · <purpose>
    Body:    Your Atlas code is 123456. It expires in 10 minutes.

Replaced Phase 2 with a real SMS provider adapter behind the same interface.
"""

from __future__ import annotations

import logging
from email.message import EmailMessage

import aiosmtplib

from atlas.config import get_settings

logger = logging.getLogger("atlas.identity.mailhog")


async def send_otp(*, phone_e164: str, code: str, purpose: str) -> None:
    settings = get_settings()
    message = EmailMessage()
    message["From"] = "otp@atlas.dev"
    message["To"] = f"{phone_e164}@sms-mock.local"
    message["Subject"] = f"Atlas OTP · {purpose}"
    message.set_content(
        f"Your Atlas code is {code}. It expires in 10 minutes.\n\n"
        "If you didn't request this, ignore this message."
    )

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.mailhog_host,
            port=settings.mailhog_port,
        )
    except Exception:
        logger.exception(
            "mailhog OTP delivery failed (host=%s port=%s to=%s)",
            settings.mailhog_host,
            settings.mailhog_port,
            phone_e164,
        )
        raise
