#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.48",
#   "httpx>=0.28",
# ]
# ///
"""Atlas demo screen-recording script — W8 Day 4.

Walks the flagship flow end-to-end in headless Chromium and records the
visible surfaces to WebM. The backend heavy lifting (register + skill +
purchase + webhook × 6) happens over HTTPS from this process; the
browser only observes the surfaces a founder or investor would watch:
admin login → close → reveal → public /proof/[drawId] with copy-verify.

Output: {repo}/_bmad-output/demo/atlas-hero-flow.webm

Prereqs
-------
- Full local stack up:  `make dev` then `make demo-reset`
- Playwright installed (see below).

Install (dedicated venv — keeps demo tooling out of backend deps):

    python3 -m venv infrastructure/scripts/.venv-record
    infrastructure/scripts/.venv-record/bin/pip install \\
        playwright>=1.48 httpx>=0.28
    infrastructure/scripts/.venv-record/bin/playwright install chromium

Or, if you have `uv` (uses the PEP-723 block at the top of this file):

    uv run infrastructure/scripts/record_demo.py

Fallback: if Chromium download stalls under a corporate proxy,
follow docs/runbooks/demo-recording-obs-fallback.md instead.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import os
import random
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

import httpx
from playwright.async_api import async_playwright


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "_bmad-output" / "demo"
OUTPUT_NAME = "atlas-hero-flow.webm"

# Six known-correct skill-question answers (mirrors demo_rehearsal.sh:127).
CORRECT_OPTION_TEXTS = {
    "Abuja", "Green", "60", "144", "Mars", "0",
    "7", "Mandarin Chinese", "Pound Sterling", "9",
}

# 1 primary + 5 reserves = 6 tickets in the pool.
POOL_SIZE = 6


@dataclass(frozen=True)
class Config:
    api_base: str
    admin_base: str
    admin_email: str
    admin_password: str
    webhook_secret: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            api_base=os.environ.get("ATLAS_API_BASE", "http://localhost:8000"),
            admin_base=os.environ.get("ATLAS_ADMIN_BASE", "http://localhost:3000"),
            admin_email=os.environ.get(
                "ATLAS_SUPERADMIN_EMAIL", "adaobi.ibe@atlas.dev"
            ),
            admin_password=os.environ.get(
                "ATLAS_SUPERADMIN_PASSWORD",
                "dev_bootstrap_password_change_me_00",
            ),
            webhook_secret=os.environ.get(
                "ATLAS_PAYSTACK_WEBHOOK_SECRET",
                "local_dev_paystack_webhook_secret_do_not_use_in_prod",
            ),
        )


def sign_paystack(body: str, secret: str) -> str:
    return hmac.new(
        secret.encode(), body.encode(), hashlib.sha512
    ).hexdigest()


def random_email() -> str:
    return f"kemi-{uuid.uuid4().hex[:8]}@example.com"


def random_phone() -> str:
    return f"+2348030{random.randint(0, 999_999):06d}"


async def _register_consumer(
    client: httpx.AsyncClient, cfg: Config
) -> tuple[str, str]:
    """Register + verify + set password + login. Returns (email, jwt)."""
    email = random_email()
    phone = random_phone()
    password = "correct horse battery staple"

    reg = await client.post(
        "/api/v1/users",
        json={
            "email": email,
            "phone_e164": phone,
            "date_of_birth": "1993-03-12",
            "terms_accepted": True,
        },
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    reg.raise_for_status()
    user_id = reg.json()["user_id"]

    await client.post(
        "/api/v1/otps",
        json={"user_id": user_id, "purpose": "registration"},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )

    # Poll mailhog for the OTP addressed to this phone.
    code: str | None = None
    for _ in range(20):
        await asyncio.sleep(0.25)
        mh = await client.get(
            "http://localhost:8025/api/v2/messages",
            headers={"Host": "localhost:8025"},
        )
        for item in mh.json().get("items", []):
            to = item.get("To") or []
            if to and to[0].get("Mailbox") == phone:
                body = item["Content"]["Body"]
                digits = "".join(c for c in body if c.isdigit())
                if len(digits) >= 6:
                    code = digits[:6]
                    break
        if code:
            break
    if not code:
        raise RuntimeError(f"no OTP for {phone} in mailhog")

    await client.post(
        "/api/v1/otps/verify",
        json={
            "user_id": user_id,
            "purpose": "registration",
            "code": code,
        },
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    await client.post(
        f"/api/v1/users/{user_id}/password",
        json={"password": password},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    login = await client.post(
        "/api/v1/sessions",
        json={"email": email, "password": password},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    login.raise_for_status()
    return email, login.json()["access_token"]


async def _buy_ticket(
    client: httpx.AsyncClient,
    cfg: Config,
    draw_id: str,
    token: str,
    email: str,
) -> None:
    q = await client.get(
        f"/api/v1/draws/{draw_id}/skill-questions/next",
        headers={"Authorization": f"Bearer {token}"},
    )
    q.raise_for_status()
    qbody = q.json()
    attempt_id = qbody["attempt_id"]
    correct_id = next(
        (
            o["id"]
            for o in qbody["options"]
            if o["text"] in CORRECT_OPTION_TEXTS
        ),
        None,
    )
    if not correct_id:
        raise RuntimeError(f"no known-correct option: {qbody}")

    await client.post(
        f"/api/v1/skill-questions/attempts/{attempt_id}/answer",
        json={"option_id": correct_id},
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": str(uuid.uuid4()),
        },
    )
    purchase = await client.post(
        "/api/v1/tickets/purchase",
        json={"draw_id": draw_id, "entitlement_id": attempt_id},
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": str(uuid.uuid4()),
        },
    )
    purchase.raise_for_status()
    pbody = purchase.json()
    vendor_ref = pbody["vendor_reference"]
    amount = pbody["amount_minor"]

    webhook_body = json.dumps(
        {
            "event": "charge.success",
            "data": {
                "reference": vendor_ref,
                "amount": amount,
                "currency": "NGN",
                "status": "success",
                "channel": "card",
                "fees": 10_000,
                "customer": {"email": email},
            },
        },
        separators=(",", ":"),
    )
    sig = sign_paystack(webhook_body, cfg.webhook_secret)
    await client.post(
        "/api/v1/payments/webhooks/paystack",
        content=webhook_body,
        headers={
            "x-paystack-signature": sig,
            "Content-Type": "application/json",
        },
    )


async def bootstrap_pool(cfg: Config) -> str:
    """Register POOL_SIZE consumers and have each buy a ticket. Returns draw_id."""
    async with httpx.AsyncClient(base_url=cfg.api_base, timeout=30) as client:
        draws = await client.get("/api/v1/draws")
        draws.raise_for_status()
        items = draws.json().get("items", [])
        if not items:
            raise RuntimeError(
                "no active draw — run `make demo-reset` before recording"
            )
        draw_id = items[0]["id"]

        for i in range(1, POOL_SIZE + 1):
            email, token = await _register_consumer(client, cfg)
            await _buy_ticket(client, cfg, draw_id, token, email)
            print(f"  consumer {i}: {email}")
        return draw_id


async def record_visible_surfaces(cfg: Config, draw_id: str) -> Path:
    """Drive the admin UI + public /proof page, recording to WebM."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            record_video_dir=str(OUTPUT_DIR),
            record_video_size={"width": 1440, "height": 900},
        )
        page = await context.new_page()

        # 1. Admin login
        await page.goto(f"{cfg.admin_base}/login")
        await page.get_by_label("Email").fill(cfg.admin_email)
        await page.get_by_label("Password").fill(cfg.admin_password)
        await page.get_by_role("button", name="Sign in").click()
        await page.wait_for_url(f"{cfg.admin_base}/admin", timeout=15_000)

        # 2. Draws list → detail
        await page.goto(f"{cfg.admin_base}/admin/draws/{draw_id}")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1_500)  # let the reader see the state badge

        # 3. Close draw (two-step confirm)
        await page.get_by_role("button", name="Close draw").click()
        await page.get_by_role("button", name="Yes, close draw").click()
        await page.wait_for_load_state("networkidle")
        # State transitions to sales_closed; the reveal button renders.
        await page.get_by_role("button", name="Reveal winner").wait_for(
            timeout=15_000
        )
        await page.wait_for_timeout(1_500)

        # 4. Reveal winner (two-step confirm)
        await page.get_by_role("button", name="Reveal winner").click()
        await page.get_by_role("button", name="Yes, reveal winner").click()
        # Winners table appears once state → revealed.
        await page.get_by_role("link", name="View public proof →").wait_for(
            timeout=15_000
        )
        await page.wait_for_timeout(2_000)

        # 5. Follow "View public proof →" to /proof/[drawId]
        await page.goto(f"{cfg.admin_base}/proof/{draw_id}")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2_000)

        # 6. Copy-verify — scroll to the CopyCommand island + click.
        copy_button = page.get_by_role("button", name="Copy verify command")
        await copy_button.scroll_into_view_if_needed()
        await page.wait_for_timeout(1_000)
        await copy_button.click()
        await page.wait_for_timeout(2_000)  # let "Copied" state read

        # 7. Close — flush the video file.
        video = page.video
        await context.close()
        await browser.close()
        if video is None:
            raise RuntimeError("Playwright did not record a video")
        raw_path = Path(await video.path())

    final_path = OUTPUT_DIR / OUTPUT_NAME
    if final_path.exists():
        final_path.unlink()
    raw_path.rename(final_path)
    return final_path


async def main() -> int:
    cfg = Config.from_env()
    print(f"→ API      {cfg.api_base}")
    print(f"→ Admin UI {cfg.admin_base}")
    print("→ Bootstrapping pool via API…")
    draw_id = await bootstrap_pool(cfg)
    print(f"→ Draw     {draw_id}")
    print("→ Recording visible surfaces via headless Chromium…")
    path = await record_visible_surfaces(cfg, draw_id)
    print(f"✓ Video    {path.relative_to(REPO_ROOT)}")
    print(f"  size     {path.stat().st_size / 1024:.1f} KiB")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))