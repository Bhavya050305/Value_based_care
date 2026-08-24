import asyncio
import os, sys
# Ensure the repository root is on sys.path so `import app` works when running from scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from app.core.database import get_engine


async def main():
    engine = get_engine()
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT current_database(), current_schema(), current_user;"))
        print("CURRENT DB/SCH/USER:", res.fetchone())

        q = text("""
        SELECT table_schema, table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'aco_financial_ml_training'
        ORDER BY table_schema, ordinal_position;
        """)
        res = await conn.execute(q)
        rows = res.fetchall()
        print("\nCOLUMNS for aco_financial_ml_training:")
        for r in rows:
            print(r)

        # Try selecting the verified row
        sel = text('''
        SELECT
            "ACO_ID",
            feature_year,
            target_year,
            "ABtotBnchmk",
            "ABtotExp",
            "GenSaveLoss"
        FROM public.aco_financial_ml_training
        WHERE "ACO_ID" = 'A3458' AND target_year = 2021
        LIMIT 1;
        ''')
        try:
            res = await conn.execute(sel)
            row = res.fetchone()
            print('\nSELECT result for A3458/2021:')
            print(row)
        except Exception as e:
            print('\nSELECT error:')
            print(e)


async def find_db_with_precomputed_table():
    engine = get_engine()
    url = engine.url
    # list databases accessible via current server
    async with engine.connect() as conn:
        rows = await conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
        dbs = [r[0] for r in rows.fetchall()]
    print('\nDatabases visible from this server:')
    for db in dbs:
        print(' -', db)

    # try connecting to each database and check for required table/column
    candidates = []
    for db in dbs:
        try:
            new_url = url._replace(database=db)
            from sqlalchemy.ext.asyncio import create_async_engine
            test_engine = create_async_engine(str(new_url))
            async with test_engine.connect() as conn:
                q = text("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'aco_financial_ml_training';")
                res = await conn.execute(q)
                cols = [r[0] for r in res.fetchall()]
                if cols:
                    candidates.append((db, cols))
            await test_engine.dispose()
        except Exception as e:
            # ignore connection failures
            pass

    print('\nDatabases that contain public.aco_financial_ml_training:')
    for db, cols in candidates:
        has_aco_id = 'ACO_ID' in cols or 'aco_id' in cols
        print(f" - {db}: columns count={len(cols)}; has_ACO_ID={has_aco_id}")


if __name__ == '__main__':
    asyncio.run(main())
    asyncio.run(find_db_with_precomputed_table())
