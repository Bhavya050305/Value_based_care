import asyncio

from sqlalchemy import text

from app.core.database import get_session_factory


async def main():
    session_factory = get_session_factory()

    async with session_factory() as session:
        result = await session.execute(
            text(
                """
                SELECT
                    table_name,
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name IN (
                      'acos',
                      'aco_financial_ml_training',
                      'performance_quality'
                  )
                ORDER BY table_name, ordinal_position
                """
            )
        )

        print("=" * 80)
        print("ANOMALY SOURCE TABLE COLUMNS")
        print("=" * 80)

        rows = result.fetchall()

        if not rows:
            print("No matching tables found.")
            return

        current_table = None

        for row in rows:
            if row.table_name != current_table:
                if current_table is not None:
                    print()

                print(f"\n[{row.table_name}]")
                print("-" * 80)
                current_table = row.table_name

            print(
                f"{row.column_name:45} "
                f"{row.data_type}"
            )

        print("\n" + "=" * 80)
        print("DATABASE TABLE CHECK COMPLETED")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())