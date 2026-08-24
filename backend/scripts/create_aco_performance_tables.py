"""Build canonical public.aco_performance_2022, 2023, 2024 tables and views in Supabase PostgreSQL directly from canonical aco_year_analytics."""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load backend/.env
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.database import get_engine, get_session_factory
from sqlalchemy import text

async def main():
    engine = get_engine()
    factory = get_session_factory()

    async with factory() as session:
        print("=" * 80)
        print("BUILDING DEDICATED TABLES: aco_performance_2022, aco_performance_2023, aco_performance_2024")
        print("=" * 80)

        # 1. Drop existing aco_performance tables and old views if present
        for yr in [2022, 2023, 2024]:
            await session.execute(text(f"DROP VIEW IF EXISTS public.aco_{yr} CASCADE;"))
            await session.execute(text(f"DROP TABLE IF EXISTS public.aco_performance_{yr} CASCADE;"))
        await session.commit()

        # 2. Create aco_performance_2022, 2023, 2024 from public.aco_year_analytics
        for yr in [2022, 2023, 2024]:
            print(f"\nCreating table public.aco_performance_{yr}...")
            create_sql = f"""
                CREATE TABLE public.aco_performance_{yr} AS
                SELECT 
                    aco_id AS "ACO_ID",
                    aco_name AS "ACO_Name",
                    'US' AS "ACO_State",
                    'BASIC' AS "Agree_Type",
                    'ONE-SIDED' AS "Risk_Model",
                    attributed_members AS "N_AB",
                    benchmark_expenditure AS "ABtotBnchmk",
                    actual_expenditure AS "ABtotExp",
                    gross_savings_loss AS "GenSaveLoss",
                    earned_shared_savings AS "EarnSaveLoss",
                    savings_rate AS "SavingsLossPct",
                    savings_rate AS "ExpenditureVariancePct",
                    actual_pmpm AS "PMPM",
                    benchmark_pmpm AS "BenchmarkPMPM",
                    quality_score AS "QualScore",
                    NULL::DOUBLE PRECISION AS "FinalShareRate",
                    NULL::DOUBLE PRECISION AS "FinalLossRate",
                    NULL::DOUBLE PRECISION AS "ADM",
                    NULL::DOUBLE PRECISION AS "P_EDV_Vis",
                    risk_level AS risk_level,
                    performance_year AS performance_year,
                    NOW() AS created_at,
                    NOW() AS updated_at
                FROM public.aco_year_analytics
                WHERE performance_year = {yr};
            """
            await session.execute(text(create_sql))
            await session.commit()
            print(f"Table public.aco_performance_{yr} created successfully.")

        # 3. Create year views
        print("\nCreating views public.aco_2022, public.aco_2023, public.aco_2024...")
        for yr in [2022, 2023, 2024]:
            view_sql = f"""
                CREATE VIEW public.aco_{yr} AS
                SELECT * FROM public.aco_performance_{yr};
            """
            await session.execute(text(view_sql))
            await session.commit()

        # 4. Strict Year Isolation Checks
        print("\n" + "=" * 80)
        print("STRICT YEAR ISOLATION VERIFICATION")
        print("=" * 80)
        for yr in [2022, 2023, 2024]:
            check_sql = f"""
                SELECT COUNT(*) AS invalid_rows
                FROM public.aco_performance_{yr}
                WHERE performance_year <> {yr};
            """
            res = await session.execute(text(check_sql))
            invalid_cnt = res.scalar()
            print(f"aco_performance_{yr} invalid rows (expected 0): {invalid_cnt}")

        # 5. Mandatory Aggregate SQL Query
        print("\n" + "=" * 80)
        print("FINAL MANDATORY 3-YEAR SQL AGGREGATION VERIFICATION")
        print("=" * 80)
        
        agg_sql = """
            SELECT
                2022 AS year,
                COUNT(*) AS total_rows,
                COUNT(DISTINCT "ACO_ID") AS total_acos,
                SUM("N_AB") AS total_beneficiaries,
                SUM("ABtotBnchmk") AS total_benchmark_expenditure,
                SUM("ABtotExp") AS total_actual_expenditure,
                SUM("GenSaveLoss") AS total_gross_savings,
                SUM("EarnSaveLoss") AS total_earned_shared_savings,
                AVG("QualScore") AS avg_quality_score
            FROM public.aco_performance_2022

            UNION ALL

            SELECT
                2023 AS year,
                COUNT(*) AS total_rows,
                COUNT(DISTINCT "ACO_ID") AS total_acos,
                SUM("N_AB") AS total_beneficiaries,
                SUM("ABtotBnchmk") AS total_benchmark_expenditure,
                SUM("ABtotExp") AS total_actual_expenditure,
                SUM("GenSaveLoss") AS total_gross_savings,
                SUM("EarnSaveLoss") AS total_earned_shared_savings,
                AVG("QualScore") AS avg_quality_score
            FROM public.aco_performance_2023

            UNION ALL

            SELECT
                2024 AS year,
                COUNT(*) AS total_rows,
                COUNT(DISTINCT "ACO_ID") AS total_acos,
                SUM("N_AB") AS total_beneficiaries,
                SUM("ABtotBnchmk") AS total_benchmark_expenditure,
                SUM("ABtotExp") AS total_actual_expenditure,
                SUM("GenSaveLoss") AS total_gross_savings,
                SUM("EarnSaveLoss") AS total_earned_shared_savings,
                AVG("QualScore") AS avg_quality_score
            FROM public.aco_performance_2024

            ORDER BY year;
        """
        
        agg_res = await session.execute(text(agg_sql))
        rows = agg_res.fetchall()
        
        print(f"{'Year':<6} {'Rows':<6} {'ACOs':<6} {'Beneficiaries':<15} {'Benchmark':<18} {'Actual':<18} {'Gross Savings':<18} {'Earned Savings':<18} {'Avg Quality':<12}")
        print("-" * 120)
        for r in rows:
            print(f"{r[0]:<6} {r[1]:<6} {r[2]:<6} {int(r[3]):<15,} ${float(r[4]):<17,.2f} ${float(r[5]):<17,.2f} ${float(r[6]):<17,.2f} ${float(r[7]):<17,.2f} {float(r[8]):<12.4f}")

    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(main())
