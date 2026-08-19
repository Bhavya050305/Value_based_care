import asyncio

from sqlalchemy import select, func

from app.core.database import get_session_factory
from app.models.aco_financial_ml_training import AcoFinancialMlTraining


async def main():
    session_factory = get_session_factory()

    async with session_factory() as session:

        # Count rows
        result = await session.execute(
            select(func.count()).select_from(AcoFinancialMlTraining)
        )

        count = result.scalar_one()

        print("\n" + "=" * 80)
        print(f"TOTAL ROWS IN aco_financial_ml_training: {count}")
        print("=" * 80)

        # Get rows
        result = await session.execute(
            select(AcoFinancialMlTraining)
            .order_by(
                ACOFinancialMLTraining.ACO_ID,
                AcoFinancialMlTraining.performance_year,
            )
        )

        rows = result.scalars().all()

        for row in rows:
            print(
                f"ACO={row.aco_id} | "
                f"YEAR={row.performance_year} | "
                f"BENCHMARK={row.benchmark_expenditure} | "
                f"ACTUAL={row.actual_expenditure} | "
                f"GROSS={row.gross_savings_loss} | "
                f"EARNED={row.earned_shared_savings} | "
                f"QUALITY={row.quality_score} | "
                f"FEATURES={row.features_json}"
            )


if __name__ == "__main__":
    asyncio.run(main())