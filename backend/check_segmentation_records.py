import asyncio

from sqlalchemy import select

from app.core.database import get_session_factory
from app.models.aco_financial_ml_training import ACOFinancialMLTraining


async def main():
    session_factory = get_session_factory()

    async with session_factory() as session:
        result = await session.execute(
            select(
                ACOFinancialMLTraining.ACO_ID,
                ACOFinancialMLTraining.feature_year,
                ACOFinancialMLTraining.target_year,
            )
            .order_by(
                ACOFinancialMLTraining.ACO_ID,
                ACOFinancialMLTraining.feature_year,
            )
            .limit(20)
        )

        rows = result.all()

        print("=" * 80)
        print("AVAILABLE ACO FINANCIAL ML RECORDS")
        print("=" * 80)

        if not rows:
            print("NO RECORDS FOUND")
            return

        for row in rows:
            print(
                f"ACO_ID={row.ACO_ID}, "
                f"feature_year={row.feature_year}, "
                f"target_year={row.target_year}"
            )


if __name__ == "__main__":
    asyncio.run(main())