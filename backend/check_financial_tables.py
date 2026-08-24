import asyncio

from sqlalchemy import text
from app.core.database import get_session_factory


TABLE_NAME = "aco_financial_ml_training"


async def main():
    session_factory = get_session_factory()

    async with session_factory() as session:

        print("\n" + "=" * 100)
        print(f"TABLE: public.{TABLE_NAME}")
        print("=" * 100)

        # ---------------------------------------------------------
        # Check whether the table exists
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
                    data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = :table_name
                ORDER BY ordinal_position
            """),
            {"table_name": TABLE_NAME},
        )

        columns = result.fetchall()

        for column_name, data_type in columns:
            print(f"{column_name:50} {data_type}")

        print(f"\nCOLUMN COUNT: {len(columns)}")

        # ---------------------------------------------------------
        # Show sample rows
        # ---------------------------------------------------------
        result = await session.execute(
            text(f"""
                SELECT *
                FROM public."{TABLE_NAME}"
                LIMIT 3
            """)
        )

        rows = result.fetchall()

        print(f"\nSAMPLE ROW COUNT: {len(rows)}")

        for row in rows:
            print(row)

        # ---------------------------------------------------------
        # Validate the actual financial record
        # ---------------------------------------------------------
        print("\n" + "=" * 100)
        print("A1001 / 2024 FINANCIAL RECORD")
        print("=" * 100)

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

        financial_record = result.fetchone()

        if financial_record:
            for key, value in financial_record._mapping.items():
                print(f"{key:30}: {value}")
        else:
            print("No financial record found.")

        print("\n" + "=" * 100)
        print("INSPECTION COMPLETE")
        print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())