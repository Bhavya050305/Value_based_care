import asyncio

from sqlalchemy import text

from app.core.database import get_session_factory


async def main():
    session_factory = get_session_factory()

    async with session_factory() as session:

        print("=" * 80)
        print("ANOMALY DATABASE CHECK")
        print("=" * 80)

        result = await session.execute(
            text("""
                SELECT
                    aco_id,
                    performance_year,
                    benchmark_expenditure,
                    actual_expenditure,
                    gross_savings_loss,
                    earned_shared_savings,
                    quality_score,
                    features_json
                FROM aco_financial_ml_training
                ORDER BY performance_year DESC
                LIMIT 10
            """)
        )

        rows = result.fetchall()

        print("ROWS:", len(rows))

        for row in rows:
            print(row)


if __name__ == "__main__":
    asyncio.run(main())