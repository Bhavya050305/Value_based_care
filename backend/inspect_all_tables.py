import asyncio

from sqlalchemy import text
from app.core.database import get_engine, get_session_factory


async def main():

    engine = get_engine()
    factory = get_session_factory()

    print("=" * 80)
    print("SEARCHING FOR DATA IN ALL PUBLIC TABLES")
    print("=" * 80)

    try:
        async with factory() as session:

            result = await session.execute(
                text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
            )

            tables = [row[0] for row in result.fetchall()]

            for table in tables:

                try:
                    result = await session.execute(
                        text(
                            f'SELECT COUNT(*) FROM public."{table}"'
                        )
                    )

                    count = result.scalar()

                    print(f"{table:<45} {count:>8} rows")

                except Exception as exc:
                    print(
                        f"{table:<45} ERROR: {exc}"
                    )

    except Exception as exc:
        print("DATABASE ERROR")
        print(exc)

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())