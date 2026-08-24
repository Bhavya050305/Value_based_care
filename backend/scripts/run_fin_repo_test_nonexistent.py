import asyncio
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import get_session_factory
from app.repositories.domain import PerformanceRepository

async def main():
    factory = get_session_factory()
    async with factory() as session:
        repo = PerformanceRepository(session)
        aco_id = 'A10001'
        target_year = 2025
        record = await repo.get_financial_by_year(aco_id=aco_id, target_year=target_year)
        print('='*80)
        print('NONEXISTENT RECORD TEST')
        print('='*80)
        if record is None:
            print(f'No record found for {aco_id} / {target_year} (expected)')
        else:
            print('Unexpectedly found:', record)

if __name__ == '__main__':
    asyncio.run(main())
