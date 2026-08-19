import asyncio

from sqlalchemy import text

from app.core.database import get_engine, get_session_factory


async def main():
    engine = get_engine()
    factory = get_session_factory()

    try:
        async with factory() as session:

            result = await session.execute(
                text("""
                    SELECT
                        column_name,
                        data_type,
                        is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = 'aco_financial_ml_training'
                    ORDER BY ordinal_position
                """)
            )

            rows = result.fetchall()

            print("=" * 80)
            print("aco_financial_ml_training COLUMNS")
            print("=" * 80)

            for column_name, data_type, nullable in rows:
                print(
                    f"{column_name:<45} "
                    f"{data_type:<20} "
                    f"nullable={nullable}"
                )

            print("=" * 80)

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())