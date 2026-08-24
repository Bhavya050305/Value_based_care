import asyncio
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import get_session_factory
from app.repositories.domain import PerformanceRepository

async def main():
    factory = get_session_factory()
    async with factory() as session:
        repo = PerformanceRepository(session)
        aco_id = 'A3458'
        target_year = 2021
        record = await repo.get_financial_by_year(aco_id=aco_id, target_year=target_year)
        print('='*80)
        print('FINANCIAL REPOSITORY RUN')
        print('='*80)
        if record is None:
            print(f'No record found for {aco_id} / {target_year}')
            return
        print('Record found:')
        print(f'ACO_ID: {record.ACO_ID}')
        print(f'feature_year: {record.feature_year}')
        print(f'target_year: {record.target_year}')
        print(f'ABtotBnchmk: {record.ABtotBnchmk}')
        print(f'ABtotExp: {record.ABtotExp}')
        print(f'GenSaveLoss: {record.GenSaveLoss}')

if __name__ == '__main__':
    asyncio.run(main())
