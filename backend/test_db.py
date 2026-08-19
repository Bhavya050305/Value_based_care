import asyncio

from sqlalchemy import text

from app.core.database import get_engine, get_session_factory


async def main():
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)

    engine = None

    try:
        engine = get_engine()
        factory = get_session_factory()

        async with factory() as session:
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()

            print("✅ DATABASE CONNECTION SUCCESS")
            print(f"Result: {value}")

    except Exception as exc:
        print("❌ DATABASE CONNECTION FAILED")
        print(f"Error: {type(exc).__name__}")
        print(f"Details: {exc}")

    finally:
        if engine:
            await engine.dispose()

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())