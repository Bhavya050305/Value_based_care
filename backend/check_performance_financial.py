import asyncio

from sqlalchemy import text
from app.core.database import get_session_factory


TABLE_NAME = "aco_financial_ml_training"


async def main():
    session_factory = get_session_factory()

    async with session_factory() as session:

        print("=" * 100)
        print(f"ACTUAL public.{TABLE_NAME} SCHEMA")
        print("=" * 100)

        # ---------------------------------------------------------
        # Check whether table exists
        # ---------------------------------------------------------
        result = await session.execute(
            text("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_name = :table_name
                )
            """),
            {"table_name": TABLE_NAME},
        )

        table_exists = result.scalar()

        if not table_exists:
            print(f"ERROR: public.{TABLE_NAME} does not exist.")
            return

        # ---------------------------------------------------------
        # Get columns
        # ---------------------------------------------------------
        result = await session.execute(
            text("""
                SELECT
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = :table_name
                ORDER BY ordinal_position
            """),
            {"table_name": TABLE_NAME},
        )

        rows = result.fetchall()

        for row in rows:
            print(
                f"{row.column_name:<45} "
                f"{row.data_type:<25} "
                f"nullable={row.is_nullable}"
            )

        print()
        print("COLUMN COUNT:", len(rows))

        # ---------------------------------------------------------
        # Row count
        # ---------------------------------------------------------
        result = await session.execute(
            text(f"""
                SELECT COUNT(*)
                FROM public.{TABLE_NAME}
            """)
        )

        print("ROW COUNT:", result.scalar())

        # ---------------------------------------------------------
        # Verify A1001 / 2024
        # ---------------------------------------------------------
        result = await session.execute(
            text(f"""
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
                FROM public.{TABLE_NAME}
                WHERE "ACO_ID" = :aco_id
                  AND target_year = :target_year
            """),
            {
                "aco_id": "A1001",
                "target_year": 2024,
            },
        )

        record = result.fetchone()

        print()
        print("=" * 100)
        print("A1001 / 2024 FINANCIAL RECORD")
        print("=" * 100)

        if record:
            for key, value in record._mapping.items():
                print(f"{key:<30}: {value}")
        else:
            print("No record found.")

        print()
        print("=" * 100)
        print("INSPECTION COMPLETE")
        print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())