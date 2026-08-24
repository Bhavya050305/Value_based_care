import json
import joblib
import pandas as pd

MODEL_PATH = "app/ml/segmentation/model.pkl"
FEATURES_PATH = "app/ml/segmentation/features.json"

model = joblib.load(MODEL_PATH)

with open(FEATURES_PATH, "r") as f:
    config = json.load(f)

features = config["features"]

print("Required features:")
for feature in features:
    print(feature)

print("\nModel loaded:")
print(model)