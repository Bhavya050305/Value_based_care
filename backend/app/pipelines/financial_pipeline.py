"""
Precompute ACO financial dashboard data.

SOURCE:
    public.aco_financial_ml_training

DESTINATION:
    public.aco_financial_performance
    public.financial_year_summary

IMPORTANT:
    This script performs all financial calculations ONCE.

    API requests never execute these calculations.
"""

import asyncio
from collections import defaultdict
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.database import get_session_factory
from app.models.aco_financial_ml_training import AcoFinancialMlTraining
from app.ml.models.financial_performance import (
    AcoFinancialPerformance,
    FinancialYearSummary,
)


GLOBAL_ORG_SENTINEL = "__global__"


def calculate_gross_savings_loss(
    benchmark: float | None,
    actual: float | None,
) -> float | None:
    """
    Savings/loss:

        benchmark - actual

    Positive = savings
    Negative = loss
    """

    if benchmark is None or actual is None:
        return None

    return benchmark - actual


def calculate_expenditure_variance(
    benchmark: float | None,
    actual: float | None,
) -> float | None:
    """
    Expenditure variance:

        actual - benchmark
    """

    if benchmark is None or actual is None:
        return None

    return actual - benchmark


def calculate_expenditure_variance_pct(
    benchmark: float | None,
    actual: float | None,
) -> float | None:
    """
    Expenditure variance percentage:

        ((actual - benchmark) / benchmark) * 100

    Returns None when benchmark is unavailable or zero.
    """

    if benchmark is None or actual is None:
        return None

    if benchmark == 0:
        return None

    return ((actual - benchmark) / benchmark) * 100


async def run_pipeline() -> None:
    """
    Execute complete financial precomputation.
    """

    session_factory = get_session_factory()

    async with session_factory() as session:

        await refresh_aco_financial_performance(session)

        await refresh_financial_year_summary(session)

        await session.commit()


async def refresh_aco_financial_performance(session) -> None:
    """
    Convert source ACO financial rows into dashboard-ready rows.
    """

    result = await session.execute(
        select(AcoFinancialMlTraining)
    )

    source_rows = result.scalars().all()

    if not source_rows:
        print("No source financial records found.")
        return

    values = []

    for source in source_rows:

        benchmark = source.benchmark_expenditure
        actual = source.actual_expenditure

        # ------------------------------------------------------
        # CALCULATE ONCE
        # ------------------------------------------------------

        gross_savings_loss = calculate_gross_savings_loss(
            benchmark,
            actual,
        )

        expenditure_variance = calculate_expenditure_variance(
            benchmark,
            actual,
        )

        expenditure_variance_pct = calculate_expenditure_variance_pct(
            benchmark,
            actual,
        )

        # ------------------------------------------------------
        # Validate calculations
        # ------------------------------------------------------

        if (
            gross_savings_loss is not None
            and expenditure_variance is not None
        ):
            if gross_savings_loss != -expenditure_variance:
                raise ValueError(
                    "Financial validation failed for "
                    f"{source.aco_id}/{source.performance_year}"
                )

        values.append(
            {
                "aco_id": source.aco_id,
                "performance_year": source.performance_year,

                "organization_id": source.organization_id,

                "benchmark_expenditure": benchmark,
                "actual_expenditure": actual,

                "gross_savings_loss": gross_savings_loss,
                "expenditure_variance": expenditure_variance,
                "expenditure_variance_pct": (
                    expenditure_variance_pct
                ),

                # These are source values and are NOT estimated.
                "pmpm": (
                    source.features_json.get("PMPM")
                    if source.features_json
                    and "PMPM" in source.features_json
                    else None
                ),

                "benchmark_pmpm": (
                    source.features_json.get("BenchmarkPMPM")
                    if source.features_json
                    and "BenchmarkPMPM" in source.features_json
                    else None
                ),

                "earned_shared_savings": source.earned_shared_savings,

                # These may also be stored if present in source.
                "share_rate": (
                    source.features_json.get("FinalShareRate")
                    if source.features_json
                    and "FinalShareRate" in source.features_json
                    else None
                ),

                "loss_rate": (
                    source.features_json.get("FinalLossRate")
                    if source.features_json
                    and "FinalLossRate" in source.features_json
                    else None
                ),
            }
        )

    # ----------------------------------------------------------
    # UPSERT
    # ----------------------------------------------------------

    stmt = pg_insert(
        AcoFinancialPerformance
    ).values(values)

    update_cols = {
        "organization_id": stmt.excluded.organization_id,
        "benchmark_expenditure": stmt.excluded.benchmark_expenditure,
        "actual_expenditure": stmt.excluded.actual_expenditure,
        "gross_savings_loss": stmt.excluded.gross_savings_loss,
        "expenditure_variance": stmt.excluded.expenditure_variance,
        "expenditure_variance_pct": stmt.excluded.expenditure_variance_pct,
        "pmpm": stmt.excluded.pmpm,
        "benchmark_pmpm": stmt.excluded.benchmark_pmpm,
        "earned_shared_savings": stmt.excluded.earned_shared_savings,
        "share_rate": stmt.excluded.share_rate,
        "loss_rate": stmt.excluded.loss_rate,
    }

    stmt = stmt.on_conflict_do_update(
        index_elements=[
            "aco_id",
            "performance_year",
        ],
        set_=update_cols,
    )

    await session.execute(stmt)

    print(
        f"Precomputed {len(values)} ACO financial records."
    )


async def refresh_financial_year_summary(session) -> None:
    """
    Calculate portfolio totals from the precomputed ACO table.

    These totals are calculated during preprocessing,
    NOT during API requests.
    """

    result = await session.execute(
        select(AcoFinancialPerformance)
    )

    rows = result.scalars().all()

    if not rows:
        print("No precomputed financial records found.")
        return

    by_year: dict[int, list[AcoFinancialPerformance]] = (
        defaultdict(list)
    )

    for row in rows:
        by_year[row.performance_year].append(row)

    values = []

    for year, group in by_year.items():

        valid_benchmark = [
            r.benchmark_expenditure
            for r in group
            if r.benchmark_expenditure is not None
        ]

        valid_actual = [
            r.actual_expenditure
            for r in group
            if r.actual_expenditure is not None
        ]

        valid_savings = [
            r.gross_savings_loss
            for r in group
            if r.gross_savings_loss is not None
        ]

        valid_earned = [
            r.earned_shared_savings
            for r in group
            if r.earned_shared_savings is not None
        ]

        total_benchmark = (
            sum(valid_benchmark)
            if valid_benchmark
            else None
        )

        total_actual = (
            sum(valid_actual)
            if valid_actual
            else None
        )

        total_savings = (
            sum(valid_savings)
            if valid_savings
            else None
        )

        total_earned = (
            sum(valid_earned)
            if valid_earned
            else None
        )

        values.append(
            {
                "performance_year": year,
                "organization_id": GLOBAL_ORG_SENTINEL,

                "aco_count": len(group),

                "total_benchmark_expenditure": total_benchmark,

                "total_actual_expenditure": total_actual,

                "total_gross_savings_loss": total_savings,

                "total_earned_shared_savings": total_earned,

                "avg_share_rate": None,

                "avg_loss_rate": None,

                "pct_acos_earning_savings": (
                    sum(
                        1
                        for r in group
                        if (
                            r.gross_savings_loss is not None
                            and r.gross_savings_loss > 0
                        )
                    )
                    / len(group)
                    * 100
                    if group
                    else None
                ),
            }
        )

    stmt = pg_insert(
        FinancialYearSummary
    ).values(values)

    update_cols = {
        "aco_count": stmt.excluded.aco_count,
        "total_benchmark_expenditure": (
            stmt.excluded.total_benchmark_expenditure
        ),
        "total_actual_expenditure": (
            stmt.excluded.total_actual_expenditure
        ),
        "total_gross_savings_loss": (
            stmt.excluded.total_gross_savings_loss
        ),
        "total_earned_shared_savings": (
            stmt.excluded.total_earned_shared_savings
        ),
        "avg_share_rate": stmt.excluded.avg_share_rate,
        "avg_loss_rate": stmt.excluded.avg_loss_rate,
        "pct_acos_earning_savings": (
            stmt.excluded.pct_acos_earning_savings
        ),
    }

    stmt = stmt.on_conflict_do_update(
        index_elements=[
            "performance_year",
            "organization_id",
        ],
        set_=update_cols,
    )

    await session.execute(stmt)

    print(
        f"Precomputed {len(values)} yearly financial summaries."
    )


if __name__ == "__main__":
    asyncio.run(run_pipeline())