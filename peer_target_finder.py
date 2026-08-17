import json
from pathlib import Path

import joblib


MODEL_PATH = (
    Path("ml")
    / "models"
    / "peer_target_finder"
    / "model.pkl"
)


if __name__ == "__main__":

    print("Loading Peer Target Finder model...")

    model = joblib.load(MODEL_PATH)

    # ---------------------------------------------------------
    # CHANGE THESE TWO VALUES WHEN TESTING ANOTHER ACO
    # ---------------------------------------------------------

    target_aco_id = "A2057"
    target_year = 2024

    # ---------------------------------------------------------
    # RUN MODEL
    # ---------------------------------------------------------

    result = model.predict(
        target_aco_id,
        target_year,
        top_k=3
    )

    print()
    print(
        json.dumps(
            result,
            indent=2,
            default=str
        )
    )