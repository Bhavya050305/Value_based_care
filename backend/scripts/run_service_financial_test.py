import asyncio, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.performance import PerformanceService

async def main():
    service = PerformanceService()
    try:
        data = await service.get_financial(aco_id='A3458', year=2021)
        print('SERVICE returned:')
        print(data.model_dump())
    except Exception as e:
        print('SERVICE error:', type(e).__name__, e)

if __name__=='__main__':
    asyncio.run(main())
