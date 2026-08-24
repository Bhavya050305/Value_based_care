import asyncio

from sqlalchemy import text

from app.core.database import get_engine, get_session_factory


async def main():

    print("=" * 80)
    print("ACO FINANCIAL ML DATA VERIFICATION")
    print("=" * 80)

    engine = None

    try:
        engine = get_engine()
        factory = get_session_factory()

        async with factory() as session:

            # ---------------------------------------------------------
            # 1. DATABASE CONNECTION
            # ---------------------------------------------------------
            print("\n1. DATABASE CONNECTION")
            print("-" * 80)

            result = await session.execute(
                text("SELECT current_database(), current_user")
            )

            db_name, db_user = result.fetchone()

            print(f"Database : {db_name}")
            print(f"User     : {db_user}")

            # ---------------------------------------------------------
            # 2. CHECK TABLE
            # ---------------------------------------------------------
            print("\n2. CHECK TABLE")
            print("-" * 80)

            result = await session.execute(
                text("""
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = 'aco_financial_ml_training'
                    )
                """)
            )

            exists = result.scalar()

            if not exists:
                print("❌ Table does not exist.")
                return

            print("✅ public.aco_financial_ml_training exists")

            # ---------------------------------------------------------
            # 3. COUNT ROWS
            # ---------------------------------------------------------
            print("\n3. ROW COUNT")
            print("-" * 80)

            result = await session.execute(
                text("""
                    SELECT COUNT(*)
                    FROM public.aco_financial_ml_training
                """)
            )

            count = result.scalar()

            print(f"Total rows: {count}")

            if count == 0:
                print("❌ Table is empty.")
                return

            if count != 1713:
                print(
                    f"⚠️ Expected 1713 rows, but database contains {count} rows."
                )
            else:
                print("✅ Correct: 1713 rows found.")

            # ---------------------------------------------------------
            # 4. SAMPLE DATA
            # ---------------------------------------------------------
            print("\n4. SAMPLE DATA")
            print("-" * 80)

            result = await session.execute(
                text("""
                    SELECT
                        id,
                        aco_id,
                        organization_id,
                        performance_year,
                        benchmark_expenditure,
                        actual_expenditure,
                        gross_savings_loss,
                        earned_shared_savings,
                        quality_score,
                        expenditure_trend,
                        savings_trend,
                        risk_score,
                        anomaly_flag,
                        model_version,
                        training_status
                    FROM public.aco_financial_ml_training
                    ORDER BY aco_id, performance_year
                    LIMIT 10
                """)
            )

            rows = result.fetchall()

            for row in rows:
                print(row)

            # ---------------------------------------------------------
            # 5. UNIQUE ACO COUNT
            # ---------------------------------------------------------
            print("\n5. UNIQUE ACO COUNT")
            print("-" * 80)

            result = await session.execute(
                text("""
                    SELECT COUNT(DISTINCT aco_id)
                    FROM public.aco_financial_ml_training
                """)
            )

            aco_count = result.scalar()

            print(f"Unique ACOs: {aco_count}")

            # ---------------------------------------------------------
            # 6. PERFORMANCE YEAR RANGE
            # ---------------------------------------------------------
            print("\n6. PERFORMANCE YEAR RANGE")
            print("-" * 80)

            result = await session.execute(
                text("""
                    SELECT
                        MIN(performance_year),
                        MAX(performance_year)
                    FROM public.aco_financial_ml_training
                """)
            )

            min_year, max_year = result.fetchone()

            print(f"Year range: {min_year} - {max_year}")

            # ---------------------------------------------------------
            # 7. TRAINING STATUS
            # ---------------------------------------------------------
            print("\n7. TRAINING STATUS")
            print("-" * 80)

            result = await session.execute(
                text("""
                    SELECT
                        training_status,
                        COUNT(*)
                    FROM public.aco_financial_ml_training
                    GROUP BY training_status
                    ORDER BY training_status
                """)
            )

            for status, total in result.fetchall():
                print(f"{status}: {total}")

            # ---------------------------------------------------------
            # 8. MODEL VERSION
            # ---------------------------------------------------------
            print("\n8. MODEL VERSION")
            print("-" * 80)

            result = await session.execute(
                text("""
                    SELECT
                        model_version,
                        COUNT(*)
                    FROM public.aco_financial_ml_training
                    GROUP BY model_version
                    ORDER BY model_version
                """)
            )

            for model, total in result.fetchall():
                print(f"{model}: {total}")

            # ---------------------------------------------------------
            # FINAL
            # ---------------------------------------------------------
            print("\n" + "=" * 80)
            print("VERIFICATION COMPLETE")
            print("=" * 80)

    except Exception as exc:
        print("\n❌ ERROR")
        print(type(exc).__name__)
        print(exc)

    finally:
        if engine is not None:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())