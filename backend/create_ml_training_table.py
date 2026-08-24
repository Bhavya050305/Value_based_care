"""Create aco_financial_ml_training table using raw SQL."""

import asyncio
from sqlalchemy import text
from app.core.database import get_engine


async def create_table():
    """Create the aco_financial_ml_training table."""
    engine = get_engine()
    
    statements = [
        """
        CREATE TABLE IF NOT EXISTS public.aco_financial_ml_training (
            id VARCHAR(255) NOT NULL PRIMARY KEY,
            aco_id VARCHAR(255) NOT NULL REFERENCES public.acos(aco_id),
            organization_id VARCHAR(255),
            performance_year INTEGER NOT NULL,
            
            benchmark_expenditure FLOAT,
            actual_expenditure FLOAT,
            gross_savings_loss FLOAT,
            earned_shared_savings FLOAT,
            
            quality_score FLOAT,
            expenditure_trend FLOAT,
            savings_trend FLOAT,
            risk_score FLOAT,
            anomaly_flag INTEGER DEFAULT 0,
            
            features_json JSON,
            model_version VARCHAR(100),
            training_status VARCHAR(50) DEFAULT 'pending',
            
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        )
        """,
        "CREATE INDEX IF NOT EXISTS ix_aco_financial_ml_training_aco_id ON public.aco_financial_ml_training(aco_id)",
        "CREATE INDEX IF NOT EXISTS ix_aco_financial_ml_training_organization_id ON public.aco_financial_ml_training(organization_id)",
        "CREATE INDEX IF NOT EXISTS ix_aco_financial_ml_training_performance_year ON public.aco_financial_ml_training(performance_year)",
    ]
    
    try:
        async with engine.begin() as conn:
            for statement in statements:
                await conn.execute(text(statement))
        print("✓ aco_financial_ml_training table created successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_table())
