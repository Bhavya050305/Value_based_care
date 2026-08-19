import asyncio, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sqlalchemy import text
from app.core.database import get_engine
from app.models.aco_financial_ml_training import ACOFinancialMLTraining

async def main():
    engine = get_engine()
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='aco_financial_ml_training' ORDER BY ordinal_position"))
        db_cols = [r[0] for r in res.fetchall()]

    model_cols = [c.name for c in ACOFinancialMLTraining.__table__.columns]

    print('DB columns count:', len(db_cols))
    print('Model columns count:', len(model_cols))

    missing_in_db = [c for c in model_cols if c not in db_cols]
    extra_in_db = [c for c in db_cols if c not in model_cols]

    print('\nColumns in model but not in DB (should be none):')
    for c in missing_in_db:
        print(' -', c)

    print('\nColumns in DB but not in model (informational):')
    for c in extra_in_db:
        print(' -', c)

    if not missing_in_db:
        print('\nModel exactly matches DB columns (or DB has extras).')
    else:
        print('\nModel/DB mismatch detected.')

if __name__ == '__main__':
    asyncio.run(main())
