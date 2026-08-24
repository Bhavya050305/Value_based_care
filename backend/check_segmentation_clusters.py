import json
import joblib

MODEL_PATH = "app/ml/segmentation/model.pkl"
FEATURES_PATH = "app/ml/segmentation/features.json"

model = joblib.load(MODEL_PATH)

with open(FEATURES_PATH, "r") as f:
    config = json.load(f)

features = config["features"]

kmeans = model.named_steps["kmeans"]

print("=" * 80)
print("SEGMENTATION MODEL")
print("=" * 80)

print("Number of clusters:", kmeans.n_clusters)

print("\nFeatures:")
for i, feature in enumerate(features):
    print(f"{i + 1:2}. {feature}")

print("\n" + "=" * 80)
print("CLUSTER CENTERS")
print("=" * 80)

for cluster_id, center in enumerate(kmeans.cluster_centers_):
    print(f"\nCluster {cluster_id}")

    for feature, value in zip(features, center):
        print(f"  {feature}: {value:.6f}")