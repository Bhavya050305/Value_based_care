import json
from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "model.pkl"
FEATURES_PATH = BASE_DIR / "features.json"
MODEL_INFO_PATH = BASE_DIR / "model_info.json"


class SegmentationPredictor:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)

        with open(FEATURES_PATH, "r") as f:
            self.feature_config = json.load(f)

        with open(MODEL_INFO_PATH, "r") as f:
            self.model_info = json.load(f)

        self.features = self.feature_config["features"]

        # IMPORTANT:
        # This mapping should be confirmed against the training artifact/code.
        self.cluster_mapping = {
            0: "High Performing",
            1: "Moderate",
            2: "Needs Attention",
        }

    def predict(self, feature_data: dict) -> dict:
        missing_features = [
            feature
            for feature in self.features
            if feature not in feature_data
        ]

        if missing_features:
            raise ValueError(
                f"Missing required features: {missing_features}"
            )

        # Keep the exact feature order from features.json
        input_data = {
            feature: feature_data[feature]
            for feature in self.features
        }

        dataframe = pd.DataFrame([input_data])

        # model.pkl already contains:
        # StandardScaler -> KMeans
        cluster = int(self.model.predict(dataframe)[0])

        segment = self.cluster_mapping.get(
            cluster,
            f"Unknown Cluster {cluster}"
        )

        return {
            "cluster": cluster,
            "segment": segment,
        }