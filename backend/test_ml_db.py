import asyncio
from sqlalchemy import text
from app.core.database import get_session_factory

async def main():
    factory = get_session_factory()

    async with factory() as session:
        result = await session.execute(
            text("""
                SELECT *
                FROM public.aco_financial_ml_training
                LIMIT 1
            """)
        )

        row = result.mappings().first()

        print("TABLE TEST SUCCESS")
        print(row)

asyncio.run(main())