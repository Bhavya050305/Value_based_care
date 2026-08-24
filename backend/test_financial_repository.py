import asyncio

from app.core.database import get_session_factory
from app.repositories.domain import PerformanceRepository


async def main():

    session_factory = get_session_factory()

    async with session_factory() as session:

        repository = PerformanceRepository(session)

        print("=" * 80)
        print("FINANCIAL REPOSITORY TEST")
        print("=" * 80)

        # Test a known ACO/year
        aco_id = "A10001"
        target_year = 2025

        record = await repository.get_financial_by_year(
            aco_id=aco_id,
            target_year=target_year,
        )

        if record is None:
            print(
                f"\n❌ No financial record found for "
                f"{aco_id} / {target_year}"
            )
            return

        print("\n✓ Financial record found")

        print(f"\nACO_ID:        {record.ACO_ID}")
        print(f"Feature Year:  {record.feature_year}")
        print(f"Target Year:   {record.target_year}")

        print("\nFINANCIAL VALUES")
        print("-" * 80)

        print(f"ABtotBnchmk:        {record.ABtotBnchmk}")
        print(f"ABtotExp:           {record.ABtotExp}")
        print(f"GenSaveLoss:        {record.GenSaveLoss}")
        print(f"UpdatedBnchmk:      {record.UpdatedBnchmk}")
        print(f"HistBnchmk:         {record.HistBnchmk}")
        print(f"EarnSaveLoss:       {record.EarnSaveLoss}")

        print("\nDERIVED/PRECOMPUTED VALUES")
        print("-" * 80)

        print(f"SavingsLossPct:     {record.SavingsLossPct}")
        print(f"ExpenditureVariancePct: {record.ExpenditureVariancePct}")
        print(f"PMPM:               {record.PMPM}")
        print(f"BenchmarkPMPM:      {record.BenchmarkPMPM}")
        print(f"FinancialGap:       {record.FinancialGap}")
        print(f"GenSaveLossYoYPct:  {record.GenSaveLossYoYPct}")
        print(f"target_GenSaveLoss: {record.target_GenSaveLoss}")

        print("\n✓ Repository test completed successfully")


if __name__ == "__main__":
    asyncio.run(main())