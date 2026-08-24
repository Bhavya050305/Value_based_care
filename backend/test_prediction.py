import asyncio

from sqlalchemy import text

from app.core.database import get_session_factory
from app.ml.inference.predictor import predictor


async def main():

    factory = get_session_factory()

    async with factory() as session:

        result = await session.execute(
            text("""
                SELECT *
                FROM public.aco_financial_ml_training
                WHERE "ACO_ID" = 'A3458'
                  AND "feature_year" = 2023
                  AND "target_year" = 2024
                LIMIT 1
            """)
        )

        row = result.mappings().first()

        if not row:
            print("NO DATA FOUND")
            return

        data = dict(row)

        print("=" * 70)
        print("REAL ML INFERENCE TEST")
        print("=" * 70)

        print("ACO_ID:", data["ACO_ID"])
        print("Feature year:", data["feature_year"])
        print("Target year:", data["target_year"])

        # Remove database identifiers and target
        # The predictor expects only the 61 model features.
        prediction_input = {
            feature: data.get(feature)
            for feature in predictor.feature_names
        }

        print("\nFeature count:", len(prediction_input))

        prediction = predictor.predict(prediction_input)

        print("\nPREDICTED GenSaveLoss:")
        print(prediction)

        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())