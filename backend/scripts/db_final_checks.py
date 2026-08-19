import asyncio, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sqlalchemy import text
from app.core.database import get_engine

async def main():
    engine = get_engine()
    async with engine.connect() as conn:
        res = await conn.execute(text('SELECT current_database(), current_schema(), current_user;'))
        print('CURRENT DB/SCH/USER:', res.fetchone())

        res = await conn.execute(text("SELECT COUNT(*) FROM public.aco_financial_ml_training;"))
        print('TOTAL ROWS in public.aco_financial_ml_training =', res.scalar())

        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'aco_financial_ml_training' ORDER BY ordinal_position;"))
        cols = [r[0] for r in res.fetchall()]
        print('\nCOLUMNS (first 20):')
        for c in cols[:20]:
            print(' -', c)
        print('... total columns =', len(cols))

        sel = text('''SELECT "ACO_ID", feature_year, target_year, "ABtotBnchmk", "ABtotExp", "GenSaveLoss" FROM public.aco_financial_ml_training WHERE "ACO_ID" = 'A3458' AND target_year = 2021 LIMIT 1;''')
        res = await conn.execute(sel)
        print('\nSELECT A3458/2021 result:')
        print(res.fetchone())

if __name__ == '__main__':
    asyncio.run(main())
