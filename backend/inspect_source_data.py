import asyncio

from sqlalchemy import text
from app.core.database import get_engine, get_session_factory


TABLE_NAME = "aco_financial_ml_training"


async def main():
    engine = None

    try:
        engine = get_engine()
        factory = get_session_factory()

        async with factory() as session:

            print("=" * 80)
            print("ACO FINANCIAL ML TRAINING INSPECTION")
            print("=" * 80)

            # ---------------------------------------------------------
            # 1. Check whether the table exists
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
                print(f"\nERROR: public.{TABLE_NAME} does not exist.")
                return

            print(f"\nTable found: public.{TABLE_NAME}")

            # ---------------------------------------------------------
            # 2. Columns
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

            columns = result.fetchall()

            print("\n" + "=" * 80)
            print(f"{TABLE_NAME} COLUMNS")
            print("-" * 80)

            for column in columns:
                print(
                    f"{column[0]:45} "
                    f"{column[1]:25} "
                    f"nullable={column[2]}"
                )

            # ---------------------------------------------------------
            # 3. Row count
            # ---------------------------------------------------------
            result = await session.execute(
                text(f"""
                    SELECT COUNT(*)
                    FROM public.{TABLE_NAME}
                """)
            )

            count = result.scalar()

            print("\n" + "=" * 80)
            print("ROW COUNT")
            print("-" * 80)
            print(f"Total rows: {count}")

            # ---------------------------------------------------------
            # 4. Sample data
            # ---------------------------------------------------------
            if count > 0:

                result = await session.execute(
                    text(f"""
                        SELECT *
                        FROM public.{TABLE_NAME}
                        LIMIT 5
                    """)
                )

                rows = result.fetchall()

                print("\n" + "=" * 80)
                print("SAMPLE DATA")
                print("-" * 80)

                for row in rows:
                    print(row)

            # ---------------------------------------------------------
            # 5. Check A1001 / 2024 financial record
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
                    LIMIT 1
                """),
                {
                    "aco_id": "A1001",
                    "target_year": 2024,
                },
            )

            financial_record = result.fetchone()

            print("\n" + "=" * 80)
            print("A1001 / 2024 FINANCIAL RECORD")
            print("-" * 80)

            if financial_record:
                print(financial_record)
            else:
                print("No record found for A1001 / 2024.")

            # ---------------------------------------------------------
            # 6. Completion
            # ---------------------------------------------------------
            print("\n" + "=" * 80)
            print("INSPECTION COMPLETE")
            print("=" * 80)

    except Exception as exc:
        print("\n" + "=" * 80)
        print("ERROR")
        print("=" * 80)
        print(f"Type: {type(exc).__name__}")
        print(f"Message: {exc}")

    finally:
        if engine is not None:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())