"""Async SQLAlchemy engine and session management.

Database models and migrations are integrated in Phase 5 after the Supabase
schema is supplied. This module defines the connection lifecycle only.
"""

from collections.abc import AsyncGenerator
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
# Provide ORM Base for modules that import it from app.core.database (historical compatibility).
from app.models.base import Base

__all__ = ["get_engine", "get_session_factory", "get_db_session", "Base"]

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _normalize_database_url(database_url: str) -> str:
    """Ensure the connection string uses an async PostgreSQL driver and removes unsupported asyncpg query params."""
    if not database_url:
        return database_url

    parsed = urlsplit(database_url)
    scheme = parsed.scheme.lower()

    if scheme in {"postgresql", "postgres"}:
        scheme = "postgresql+asyncpg"
    elif scheme == "postgresql+psycopg2":
        scheme = "postgresql+asyncpg"

    username = quote(parsed.username or "", safe="")
    password = quote(parsed.password or "", safe="")
    host = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""

    if username and password:
        auth = f"{username}:{password}"
    elif username:
        auth = username
    else:
        auth = ""

    netloc = f"{auth}@{host}{port}" if auth else host + port

    filtered_query = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower() in {"sslmode", "ssl"}:
            continue
        filtered_query.append((key, value))

    normalized = urlunsplit(
        (scheme, netloc, parsed.path, urlencode(filtered_query), parsed.fragment)
    )
    return normalized


import asyncio

_engine_loop = None

from sqlalchemy.pool import NullPool

def get_engine():
    global _engine, _engine_loop, _session_factory
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    if _engine is None or (_engine_loop is not None and current_loop != _engine_loop):
        _engine = None
        _session_factory = None
        _engine_loop = current_loop
        settings = get_settings()
        if not settings.database_url:
            raise RuntimeError(
                "DATABASE_URL is not configured. Set it before opening database connections."
            )

        normalized_url = _normalize_database_url(settings.database_url)
        connect_args = {"ssl": False} if not settings.database_ssl else {"ssl": True}
        connect_args["timeout"] = 15
        _engine = create_async_engine(
            normalized_url,
            connect_args=connect_args,
            poolclass=NullPool,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
