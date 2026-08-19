"""Connectivity checks for readiness probes."""

from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import get_engine
from app.schemas.common import DataAvailability, DataStatus


async def check_database() -> DataAvailability:
    settings = get_settings()
    if not settings.database_url:
        return DataAvailability(
            available=False,
            data_status=DataStatus.NO_DATA_AVAILABLE,
            reason="DATABASE_URL is not configured.",
            required_source="environment:DATABASE_URL",
        )

    try:
        engine = get_engine()
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return DataAvailability(
            available=True,
            data_status=DataStatus.AVAILABLE,
            source="postgresql",
        )
    except Exception as exc:
        return DataAvailability(
            available=False,
            data_status=DataStatus.INSUFFICIENT_DATA,
            reason=str(exc),
            source="postgresql",
        )


async def check_redis() -> DataAvailability:
    settings = get_settings()
    if not settings.redis_url:
        return DataAvailability(
            available=False,
            data_status=DataStatus.NO_DATA_AVAILABLE,
            reason="REDIS_URL is not configured.",
            required_source="environment:REDIS_URL",
        )

    try:
        from redis.asyncio import from_url

        client = from_url(settings.redis_url)
        try:
            await client.ping()
        finally:
            await client.aclose()

        return DataAvailability(
            available=True,
            data_status=DataStatus.AVAILABLE,
            source="redis",
        )
    except Exception as exc:
        return DataAvailability(
            available=False,
            data_status=DataStatus.INSUFFICIENT_DATA,
            reason=str(exc),
            source="redis",
        )
