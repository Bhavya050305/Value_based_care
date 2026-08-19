from pathlib import Path
import json
import joblib


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "model.pkl"
FEATURES_PATH = BASE_DIR / "features.json"
MODEL_INFO_PATH = BASE_DIR / "model_info.json"


# Load model once when backend starts/imports this module
model = joblib.load(MODEL_PATH)


with open(FEATURES_PATH, "r", encoding="utf-8") as f:
    feature_config = json.load(f)


with open(MODEL_INFO_PATH, "r", encoding="utf-8") as f:
    model_info = json.load(f)


FEATURES = feature_config["features"]