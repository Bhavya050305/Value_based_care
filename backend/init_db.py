"""Initialize database schema from SQLAlchemy models."""

import asyncio

from sqlalchemy import create_engine

from app.models.base import Base
from app.models.domain import (
    Organization,
    UserProfile,
    ACO,
    ACOFinancialMLTraining,
    PerformanceQuality,
    PredictionRecord,
    RecommendationRecord,
    ActionRecord,
    AuditLogRecord,
)
from app.core.config import get_settings


async def init_db():
    """Create application tables defined by SQLAlchemy models."""

    settings = get_settings()

    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    # Convert async PostgreSQL URL to synchronous URL
    sync_url = settings.database_url.replace(
        "postgresql+asyncpg://",
        "postgresql://",
    )

    engine = create_engine(
        sync_url,
        echo=True,
    )

    try:
        print("=" * 80)
        print("INITIALIZING DATABASE SCHEMA")
        print("=" * 80)

        print("\nCreating application tables...")

        Base.metadata.create_all(engine)

        print("\n✓ Database tables created successfully!")

        print("\nExisting financial source:")
        print("  public.aco_financial_ml_training")

        print("\nImportant:")
        print("  The existing aco_financial_ml_training table is")
        print("  treated as the source of precomputed financial data.")
        print("  No performance_financial table is created.")

        print("\n" + "=" * 80)
        print("DATABASE INITIALIZATION COMPLETE")
        print("=" * 80)

    finally:
        engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())