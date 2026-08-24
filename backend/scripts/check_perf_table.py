import asyncio, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sqlalchemy import text
from app.core.database import get_engine

async def main():
    engine = get_engine()
    async with engine.connect() as conn:
        try:
            res = await conn.execute(text("SELECT COUNT(*) FROM public.aco_financial_performance WHERE aco_id='A3458' AND performance_year=2021"))
            print('count aco_financial_performance A3458/2021 =', res.scalar())
        except Exception as e:
            print('error querying aco_financial_performance:', e)

if __name__=='__main__':
    asyncio.run(main())
