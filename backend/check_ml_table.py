import asyncio

from sqlalchemy import text

from app.core.database import get_session_factory


async def main():
    session_factory = get_session_factory()

    async with session_factory() as session:

        result = await session.execute(
            text("""
                SELECT COUNT(*) AS row_count
                FROM public.aco_financial_ml_training
            """)
        )

        row_count = result.scalar_one()

        print("=" * 80)
        print("ACO FINANCIAL ML TRAINING TABLE")
        print("=" * 80)
        print("Database: vbc_dev")
        print("Schema: public")
        print("Table: aco_financial_ml_training")
        print("Row count:", row_count)


if __name__ == "__main__":
    asyncio.run(main())