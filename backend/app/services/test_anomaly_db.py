import asyncio

from sqlalchemy import select

from app.core.database import get_session_factory
from app.models.aco_financial_ml_training import AcoFinancialMlTraining


async def main():
    session_factory = get_session_factory()

    async with session_factory() as session:
        result = await session.execute(
            select(AcoFinancialMlTraining)
            .order_by(
                ACOFinancialMLTraining.ACO_ID,
                AcoFinancialMlTraining.performance_year,
            )
        )

        rows = result.scalars().all()

        print("\n" + "=" * 80)
        print("ACO FINANCIAL ML TRAINING ROWS")
        print("=" * 80)

        if not rows:
            print("NO ROWS FOUND IN TABLE")
            return

        for row in rows:
            print(
                f"ACO={row.aco_id} | "
                f"YEAR={row.performance_year} | "
                f"BENCHMARK={row.benchmark_expenditure} | "
                f"ACTUAL={row.actual_expenditure} | "
                f"SAVINGS={row.gross_savings_loss} | "
                f"QUALITY={row.quality_score}"
            )

        print("=" * 80)
        print(f"TOTAL ROWS: {len(rows)}")


if __name__ == "__main__":
    asyncio.run(main())