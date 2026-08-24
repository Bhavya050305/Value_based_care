import asyncio

from sqlalchemy import text

from app.core.database import get_session_factory


async def main():
    session_factory = get_session_factory()

    async with session_factory() as session:
        result = await session.execute(
            text("""
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
        )

        rows = result.fetchall()

        print("=" * 80)
        print("DATABASE TABLES")
        print("=" * 80)

        for schema, table in rows:
            print(f"{schema}.{table}")

        print("=" * 80)
        print(f"TOTAL TABLES: {len(rows)}")


if __name__ == "__main__":
    asyncio.run(main())