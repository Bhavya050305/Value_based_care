import sys
import os
import random

sys.path.insert(0, r'c:\Users\User\Value_based_care\backend')

import asyncio
from sqlalchemy import text
from app.core.database import get_engine, get_session_factory

CONDITIONS = [
    "Diabetes Type 2 & Hypertension",
    "Congestive Heart Failure (CHF)",
    "Chronic Obstructive Pulmonary Disease (COPD)",
    "Ischemic Heart Disease",
    "Chronic Kidney Disease (CKD Stage 3)",
    "Hypertension & Hyperlipidemia",
    "Depression & Diabetes",
    "Rheumatoid Arthritis",
    "Asthma & Allergic Rhinitis",
    "Healthy / Routine Preventive"
]

FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

ATTRIBUTION_TYPES = ["Plurality Primary Care", "Evaluation & Management", "FQHC/RHC Primary Care", "Specialist Plurality"]

async def seed_member_attributions():
    engine = get_engine()
    factory = get_session_factory()

    async with factory() as session:
        print("Creating table public.member_attributions if not exists...")
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS public.member_attributions (
                id VARCHAR(100) PRIMARY KEY,
                aco_id VARCHAR(50) NOT NULL,
                member_id VARCHAR(50) NOT NULL,
                name VARCHAR(100) NOT NULL,
                age INTEGER NOT NULL,
                gender VARCHAR(10) NOT NULL,
                risk_score FLOAT NOT NULL,
                risk_category VARCHAR(20) NOT NULL,
                primary_condition VARCHAR(100) NOT NULL,
                attribution_type VARCHAR(50) NOT NULL,
                total_annual_cost FLOAT NOT NULL,
                pmpm FLOAT NOT NULL,
                performance_year INTEGER NOT NULL
            );
        """))
        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_member_attr_aco_yr ON public.member_attributions(aco_id, performance_year);
        """))
        await session.commit()

        # Fetch all ACO IDs from public.acos or aco_financial_ml_training
        res = await session.execute(text("SELECT DISTINCT aco_id FROM public.acos"))
        aco_ids = [r[0] for r in res.fetchall()]
        print(f"Found {len(aco_ids)} ACOs in database.")

        # Check existing count
        cnt_res = await session.execute(text("SELECT COUNT(*) FROM public.member_attributions"))
        existing_count = cnt_res.scalar()
        print(f"Existing rows in member_attributions: {existing_count}")

        if existing_count > 0:
            print("Table already has rows, skipping seeding or truncating to refresh...")
            await session.execute(text("TRUNCATE TABLE public.member_attributions"))
            await session.commit()

        rows = []
        random.seed(42)

        for aco_id in aco_ids:
            for year in [2022, 2023, 2024]:
                # Generate 15 members per ACO per year
                for i in range(1, 16):
                    mbr_id = f"MBR-{aco_id}-{year}-{i:03d}"
                    fn = random.choice(FIRST_NAMES)
                    ln = random.choice(LAST_NAMES)
                    gender = random.choice(["Male", "Female"])
                    age = random.randint(55, 89)
                    
                    # Risk score based on distribution
                    risk_rand = random.random()
                    if risk_rand < 0.20:
                        risk_score = round(random.uniform(2.1, 4.5), 2)
                        risk_cat = "High Risk"
                    elif risk_rand < 0.60:
                        risk_score = round(random.uniform(1.1, 2.09), 2)
                        risk_cat = "Medium Risk"
                    else:
                        risk_score = round(random.uniform(0.5, 1.09), 2)
                        risk_cat = "Low Risk"

                    cond = random.choice(CONDITIONS) if risk_cat != "Low Risk" else "Preventive / Routine Care"
                    attr_type = random.choice(ATTRIBUTION_TYPES)
                    
                    pmpm = round(800 * risk_score + random.uniform(-50, 50), 2)
                    total_annual_cost = round(pmpm * 12, 2)
                    row_id = f"{aco_id}_{year}_{mbr_id}"

                    rows.append({
                        "id": row_id,
                        "aco_id": aco_id,
                        "member_id": mbr_id,
                        "name": f"{fn} {ln}",
                        "age": age,
                        "gender": gender,
                        "risk_score": risk_score,
                        "risk_category": risk_cat,
                        "primary_condition": cond,
                        "attribution_type": attr_type,
                        "total_annual_cost": total_annual_cost,
                        "pmpm": pmpm,
                        "performance_year": year
                    })

        print(f"Prepared {len(rows)} member attribution records. Inserting...")
        
        # Batch insert
        batch_size = 1000
        for b in range(0, len(rows), batch_size):
            batch = rows[b:b+batch_size]
            stmt = text("""
                INSERT INTO public.member_attributions 
                (id, aco_id, member_id, name, age, gender, risk_score, risk_category, primary_condition, attribution_type, total_annual_cost, pmpm, performance_year)
                VALUES (:id, :aco_id, :member_id, :name, :age, :gender, :risk_score, :risk_category, :primary_condition, :attribution_type, :total_annual_cost, :pmpm, :performance_year)
            """)
            await session.execute(stmt, batch)

        await session.commit()
        
        res_final = await session.execute(text("SELECT COUNT(*) FROM public.member_attributions"))
        final_cnt = res_final.scalar()
        print(f"Successfully seeded {final_cnt} member attribution records into public.member_attributions!")

    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(seed_member_attributions())
