"""ORM models for precomputed ACO financial performance data."""

from sqlalchemy import Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class AcoFinancialPerformance(Base, TimestampMixin):
    """
    One precomputed financial-performance row per ACO per performance year.

    This table is populated by the financial preprocessing pipeline.

    IMPORTANT:
    API requests only READ from this table.
    No financial calculations or ML inference occur during GET requests.
    """

    __tablename__ = "aco_financial_performance"

    __table_args__ = (
        UniqueConstraint(
            "aco_id",
            "performance_year",
            name="uq_aco_financial_performance_aco_year",
        ),
        {"extend_existing": True},
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    aco_id: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )

    performance_year: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=False,
    )

    organization_id: Mapped[str | None] = mapped_column(
        String(255),
        index=True,
        nullable=True,
    )

    # ---------------------------------------------------------
    # Core financial metrics
    # ---------------------------------------------------------

    benchmark_expenditure: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    actual_expenditure: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    gross_savings_loss: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    expenditure_variance: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    expenditure_variance_pct: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    # ---------------------------------------------------------
    # Per-member financial metrics
    # ---------------------------------------------------------

    pmpm: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    benchmark_pmpm: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    # ---------------------------------------------------------
    # Existing financial information
    # ---------------------------------------------------------

    earned_shared_savings: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    share_rate: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    loss_rate: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    # Source lineage
    source_target_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )


class FinancialYearSummary(Base, TimestampMixin):
    """
    Precomputed portfolio-level financial totals for each year.
    """

    __tablename__ = "financial_year_summary"

    __table_args__ = (
        UniqueConstraint(
            "performance_year",
            "organization_id",
            name="uq_financial_year_summary_year_org",
        ),
        {"extend_existing": True},
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    performance_year: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=False,
    )

    organization_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    aco_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_benchmark_expenditure: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    total_actual_expenditure: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    total_gross_savings_loss: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    total_earned_shared_savings: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    avg_share_rate: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    avg_loss_rate: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    pct_acos_earning_savings: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )