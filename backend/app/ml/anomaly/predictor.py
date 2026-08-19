import pandas as pd

from app.ml.anomaly.loader import model, FEATURES


def predict_anomaly(feature_values: dict) -> dict:
    """
    Run the trained anomaly detection model.

    feature_values must contain all features specified
    in features.json.
    """

    missing_features = [
        feature
        for feature in FEATURES
        if feature not in feature_values
    ]

    if missing_features:
        raise ValueError(
            f"Missing anomaly model features: {missing_features}"
        )

    # IMPORTANT:
    # Exact feature order from features.json
    X = pd.DataFrame(
        [[feature_values[feature] for feature in FEATURES]],
        columns=FEATURES,
    )

    prediction = model.predict(X)[0]

    decision_score = model.decision_function(X)[0]

    score_sample = model.score_samples(X)[0]

    return {
        "prediction": int(prediction),
        "is_anomaly": bool(prediction == -1),
        "decision_score": float(decision_score),
        "score_sample": float(score_sample),
    }