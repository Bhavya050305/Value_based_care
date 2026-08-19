import asyncio

from app.services.drivers import DriversService


async def main():
    service = DriversService()

    result = await service.get_predictions(
        aco_id="A3458",
        year=2024,
    )

    print("=" * 70)
    print("REAL SERVICE TEST")
    print("=" * 70)
    print(result.model_dump())


if __name__ == "__main__":
    asyncio.run(main())