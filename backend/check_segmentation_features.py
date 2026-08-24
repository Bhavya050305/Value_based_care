import asyncio

from sqlalchemy import select

from app.core.database import get_session_factory
from app.models.aco_financial_ml_training import ACOFinancialMLTraining


async def main():
    session_factory = get_session_factory()

    async with session_factory() as session:
        result = await session.execute(
            select(ACOFinancialMLTraining)
            .where(
                ACOFinancialMLTraining.ACO_ID == "A3458",
                ACOFinancialMLTraining.target_year == 2021,
            )
            .limit(1)
        )

        row = result.scalar_one_or_none()

        if row is None:
            print("No record found")
            return

        print("=" * 80)
        print("ACO:", row.ACO_ID)
        print("TARGET YEAR:", row.target_year)
        print("=" * 80)

        print("\nFEATURES_JSON:")
        print(row.features_json)

        print("\nMODEL FIELDS:")
        for field in [
            "ExpenditureVariancePct",
            "PMPM",
            "quality_score",
            "FinancialGap",
            "SavingsLossPct",
        ]:
            print(
                f"{field}: "
                f"{getattr(row, field, 'NOT_FOUND')}"
            )


if __name__ == "__main__":
    asyncio.run(main())