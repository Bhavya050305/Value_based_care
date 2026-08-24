"""Initialize database schema from SQLAlchemy models."""

from sqlalchemy import create_engine

from app.models.base import Base

# Import ALL models so SQLAlchemy registers them
# in Base.metadata.
from app.models.aco_financial_ml_training import (
    ACOFinancialMLTraining,
)

from app.models.domain import (
    Organization,
    UserProfile,
    ACO,
    PerformanceFinancial,
    PerformanceQuality,
    PredictionRecord,
    RecommendationRecord,
    ActionRecord,
    AuditLogRecord,
    SimulationRecord,
    OutcomeRecord,
    ReportRecord,
    UserPreferenceRecord,
)

from app.core.config import get_settings


def init_db() -> None:
    """Create all application tables."""

    settings = get_settings()

    if not settings.database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured."
        )

    sync_url = settings.database_url.replace(
        "postgresql+asyncpg://",
        "postgresql://",
    )

    engine = create_engine(
        sync_url,
        echo=True,
    )

    try:
        print("=" * 70)
        print("CREATING DATABASE TABLES")
        print("=" * 70)

        Base.metadata.create_all(engine)

        print()
        print("Registered tables:")

        for table_name in Base.metadata.tables:
            print(f"  ✓ {table_name}")

        print()
        print("✓ Database tables created successfully!")

    finally:
        engine.dispose()


if __name__ == "__main__":
    init_db()