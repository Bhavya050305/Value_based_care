import asyncio

from sqlalchemy import text
from app.core.database import get_session_factory


async def main():
    session_factory = get_session_factory()

    async with session_factory() as session:

        print("=" * 80)
        print("ANOMALY SOURCE DATA CHECK")
        print("=" * 80)

        queries = {
            "aco_financial_ml_training": """
                SELECT COUNT(*)
                FROM public.aco_financial_ml_training
            """,

            "performance_quality": """
                SELECT COUNT(*)
                FROM public.performance_quality
            """,

            "acos": """
                SELECT COUNT(*)
                FROM public.acos
            """,
        }

        # ---------------------------------------------------------
        # 1. Row counts
        # ---------------------------------------------------------
        for name, query in queries.items():
            result = await session.execute(text(query))
            count = result.scalar()

            print(f"{name}: {count}")

        # ---------------------------------------------------------
        # 2. Financial sample
        # ---------------------------------------------------------
        print()
        print("=" * 80)
        print("ACO FINANCIAL ML TRAINING SAMPLE")
        print("=" * 80)

        result = await session.execute(
            text("""
                SELECT
                    "ACO_ID",
                    feature_year,
                    target_year,
                    "ABtotBnchmk",
                    "ABtotExp",
                    "GenSaveLoss",
                    "EarnSaveLoss",
                    "PMPM",
                    "BenchmarkPMPM",
                    "FinancialGap",
                    "SavingsLossPct",
                    "ExpenditureVariancePct",
                    "GenSaveLossYoYPct",
                    "target_GenSaveLoss"
                FROM public.aco_financial_ml_training
                ORDER BY target_year, "ACO_ID"
                LIMIT 10
            """)
        )

        rows = result.fetchall()

        for row in rows:
            print(row)

        # ---------------------------------------------------------
        # 3. Performance quality sample
        # ---------------------------------------------------------
        print()
        print("=" * 80)
        print("PERFORMANCE QUALITY SAMPLE")
        print("=" * 80)

        result = await session.execute(
            text("""
                SELECT
                    aco_id,
                    performance_year,
                    quality_score
                FROM public.performance_quality
                ORDER BY performance_year, aco_id
                LIMIT 10
            """)
        )

        rows = result.fetchall()

        for row in rows:
            print(row)

        # ---------------------------------------------------------
        # 4. Specific financial record validation
        # ---------------------------------------------------------
        print()
        print("=" * 80)
        print("A1001 / 2024 FINANCIAL VALIDATION")
        print("=" * 80)

        result = await session.execute(
            text("""
                SELECT
                    "ACO_ID",
                    feature_year,
                    target_year,
                    "ABtotBnchmk",
                    "ABtotExp",
                    "GenSaveLoss",
                    "EarnSaveLoss",
                    "PMPM",
                    "BenchmarkPMPM",
                    "FinancialGap",
                    "SavingsLossPct",
                    "ExpenditureVariancePct",
                    "GenSaveLossYoYPct",
                    "target_GenSaveLoss"
                FROM public.aco_financial_ml_training
                WHERE "ACO_ID" = :aco_id
                  AND target_year = :target_year
                LIMIT 1
            """),
            {
                "aco_id": "A1001",
                "target_year": 2024,
            },
        )

        row = result.fetchone()

        if row:
            for key, value in row._mapping.items():
                print(f"{key:<30}: {value}")
        else:
            print("A1001 / 2024 record not found.")

        print()
        print("=" * 80)
        print("ANOMALY SOURCE DATA CHECK COMPLETE")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())