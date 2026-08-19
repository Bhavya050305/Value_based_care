import asyncio
import json

from sqlalchemy import text

from app.core.database import get_session_factory


async def main():
    factory = get_session_factory()

    async with factory() as session:

        print("=" * 80)
        print("ACO FINANCIAL ML FEATURE INSPECTION")
        print("=" * 80)

        result = await session.execute(
            text("""
                SELECT
                    id,
                    aco_id,
                    organization_id,
                    performance_year,
                    model_version,
                    training_status,
                    features_json
                FROM public.aco_financial_ml_training
                LIMIT 5
            """)
        )

        rows = result.mappings().all()

        print(f"\nRows found: {len(rows)}")

        for index, row in enumerate(rows, start=1):

            print("\n" + "=" * 80)
            print(f"ROW {index}")
            print("=" * 80)

            print("id:", row["id"])
            print("aco_id:", row["aco_id"])
            print("organization_id:", row["organization_id"])
            print("performance_year:", row["performance_year"])
            print("model_version:", row["model_version"])
            print("training_status:", row["training_status"])

            features = row["features_json"]

            print("\nfeatures_json type:", type(features).__name__)

            if features is None:
                print("features_json: NULL")
                continue

            if isinstance(features, str):
                try:
                    features = json.loads(features)
                except Exception:
                    print("features_json is not valid JSON")
                    print(features)
                    continue

            if isinstance(features, dict):

                print("Feature count:", len(features))

                print("\nFeatures:")
                for key, value in features.items():
                    print(f"  {key}: {value}")

            else:
                print("Unexpected features_json value:")
                print(features)

        print("\n" + "=" * 80)
        print("INSPECTION COMPLETE")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())