"""FastAPI entrypoint.

Day 1 (2026-07-13): only `/healthz`. Module routers wire in Days 2-5 as they land.
"""

from __future__ import annotations

from fastapi import FastAPI

from atlas import __version__
from atlas.config import get_settings
from atlas.draw.routes import router as draw_router
from atlas.identity.routes import router as identity_router
from atlas.payment.routes import router as payment_router
from atlas.skill.routes import router as skill_router
from atlas.ticket.routes import router as ticket_router

app = FastAPI(
    title="Atlas Backend",
    version=__version__,
    docs_url="/docs" if get_settings().env != "production" else None,
    redoc_url=None,
)


@app.get("/healthz", tags=["meta"])
async def healthz() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


app.include_router(identity_router)
app.include_router(payment_router)
app.include_router(draw_router)
app.include_router(skill_router)
app.include_router(ticket_router)
