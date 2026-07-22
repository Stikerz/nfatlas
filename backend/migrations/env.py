"""Alembic environment — async SQLAlchemy per SQLAlchemy 2.x recipe.

Reads the DB URL from `atlas.config.get_settings()` — one env-var reader per
ADR-012. No metadata autogenerate wired at Day 1: Day 2 will introduce the
first `models.py` in `atlas.identity` and register its metadata here.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from atlas.config import get_settings
from atlas.db import Base

# Import model modules so their tables register on Base.metadata before
# Alembic autogenerate reflects.
from atlas.audit_log import models as _audit_log_models  # noqa: F401
from atlas.identity import models as _identity_models  # noqa: F401
from atlas.idempotency import models as _idempotency_models  # noqa: F401
from atlas.admin import models as _admin_models  # noqa: F401
from atlas.wallet import models as _wallet_models  # noqa: F401
from atlas.payment import models as _payment_models  # noqa: F401
from atlas.draw import models as _draw_models  # noqa: F401
from atlas.skill import models as _skill_models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

config.set_main_option(
    "sqlalchemy.url",
    get_settings().database_url.get_secret_value(),
)


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
