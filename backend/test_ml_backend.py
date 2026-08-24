import asyncio

from app.services.drivers import DriversService


async def main():
    service = DriversService()

    result = await service.get_predictions(
        aco_id="A1001",
        year=2024,
    )

    print("=" * 80)
    print("REAL BACKEND → ML MODEL TEST")
    print("=" * 80)
    print("Result:")
    print(result)
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())