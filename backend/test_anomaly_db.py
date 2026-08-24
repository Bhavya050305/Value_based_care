import asyncio

from sqlalchemy import select

from app.core.database import get_session_factory
from app.models.aco_financial_ml_training import AcoFinancialMlTraining


async def main():

    session_factory = get_session_factory()

    async with session_factory() as session:

        stmt = (
            select(AcoFinancialMlTraining)
            .where(
                ACOFinancialMLTraining.ACO_ID == "A1501",
                AcoFinancialMlTraining.performance_year == 2024,
            )
            .order_by(AcoFinancialMlTraining.created_at.desc())
            .limit(1)
        )

        result = await session.execute(stmt)

        row = result.scalar_one_or_none()

        if row is None:
            print("NO ROW FOUND")
            return

        print("ACO:", row.aco_id)
        print("YEAR:", row.performance_year)
        print("FEATURES_JSON:")
        print(row.features_json)


asyncio.run(main())