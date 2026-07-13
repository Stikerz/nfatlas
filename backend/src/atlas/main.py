"""FastAPI entrypoint.

Day 1 (2026-07-13): only `/healthz`. Module routers wire in Days 2-5 as they land.
"""

from __future__ import annotations

from fastapi import FastAPI

from atlas import __version__
from atlas.config import get_settings
from atlas.identity.routes import router as identity_router

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
