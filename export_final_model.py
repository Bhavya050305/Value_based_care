"""
STEP 3 — Refits the WINNING model (chosen in train_compare_models.py) as a
single, complete sklearn Pipeline (imputer + scaler + model), and exports
exactly the 3 files your backend teammate asked for:

  1. model.pkl
       Complete pipeline:
       raw_features -> imputation -> scaling -> model

  2. features.json
       Exact column names + order the model expects

  3. model_info.json
       Model information, evaluation results, target definition

Run with:
    python export_final_model.py
"""

import json
import joblib
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM

from db import engine, TARGET_YEAR


# ============================================================
# LOAD MODEL COMPARISON RESULTS
# ============================================================

with open("comparison_results.json") as f:
    comparison = json.load(f)


WINNER = comparison["winner"]
FEATURE_COLS = comparison["feature_cols"]
CONTAMINATION = comparison["contamination"]


print("=" * 70)
print("EXPORTING FINAL ACO ANOMALY MODEL")
print("=" * 70)

print(
    f"Exporting winning model: {WINNER}"
)

print(
    f"Number of features: {len(FEATURE_COLS)}"
)

print(
    f"Contamination: {CONTAMINATION}"
)


# ============================================================
# MODEL INSTANCE
# ============================================================

def get_model_instance(name):
    """
    Rebuild a fresh, unfitted instance of the winning model.

    LOF uses novelty=True here because the exported model must
    be able to score NEW ACO records later through the backend.
    """

    if name == "Isolation Forest":

        return IsolationForest(
            contamination=CONTAMINATION,
            random_state=42,
            n_estimators=200
        )

    elif name == "LOF":

        return LocalOutlierFactor(
            contamination=CONTAMINATION,
            novelty=True
        )

    elif name == "One-Class SVM":

        return OneClassSVM(
            nu=CONTAMINATION,
            kernel="rbf",
            gamma="auto"
        )

    else:

        raise ValueError(
            f"Unknown model name: {name}"
        )


# ============================================================
# BUILD AND FIT PIPELINE
# ============================================================

def build_and_fit_pipeline():

    # --------------------------------------------------------
    # Load feature table
    # --------------------------------------------------------

    df = pd.read_sql(
        "SELECT * FROM aco_anomaly_features",
        engine
    )

    print(
        f"\nTraining rows loaded: {len(df)}"
    )

    # --------------------------------------------------------
    # Check required columns
    # --------------------------------------------------------

    missing_columns = [
        col
        for col in FEATURE_COLS
        if col not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "\nMissing required feature columns:\n"
            +
            "\n".join(
                f"  - {col}"
                for col in missing_columns
            )
        )

    # --------------------------------------------------------
    # Convert features to numeric
    # --------------------------------------------------------

    for col in FEATURE_COLS:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Check missing values
    # --------------------------------------------------------

    missing_before = (
        df[FEATURE_COLS]
        .isna()
        .sum()
    )

    print(
        "\nMissing values before pipeline:"
    )

    print(
        missing_before[
            missing_before > 0
        ]
    )

    # --------------------------------------------------------
    # Check completely empty columns
    # --------------------------------------------------------

    completely_missing = [
        col
        for col in FEATURE_COLS
        if df[col].isna().all()
    ]

    if completely_missing:

        print(
            "\nCompletely missing features:"
        )

        for col in completely_missing:

            print(
                f"  {col} -> will use 0.0"
            )

        # A SimpleImputer(strategy="median") cannot calculate
        # a median for a completely empty column.
        #
        # Therefore replace completely empty columns with 0.0
        # before fitting the pipeline.

        for col in completely_missing:

            df[col] = df[col].fillna(0.0)

    # --------------------------------------------------------
    # Pipeline
    # --------------------------------------------------------

    pipeline = Pipeline(
        [
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                )
            ),

            (
                "scaler",
                StandardScaler()
            ),

            (
                "model",
                get_model_instance(WINNER)
            ),
        ]
    )

    # --------------------------------------------------------
    # Fit
    # --------------------------------------------------------

    print(
        "\nFitting final pipeline..."
    )

    pipeline.fit(
        df[FEATURE_COLS]
    )

    # --------------------------------------------------------
    # Safety validation
    # --------------------------------------------------------

    X_transformed = pipeline.named_steps[
        "scaler"
    ].transform(
        pipeline.named_steps[
            "imputer"
        ].transform(
            df[FEATURE_COLS]
        )
    )

    if not np.isfinite(
        X_transformed
    ).all():

        raise ValueError(
            "Final transformed feature matrix "
            "contains NaN or infinite values."
        )

    print(
        "Final pipeline fitted successfully."
    )

    return pipeline, len(df)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    pipeline, n_rows = (
        build_and_fit_pipeline()
    )

    # ========================================================
    # 1. SAVE MODEL
    # ========================================================

    joblib.dump(
        pipeline,
        "model.pkl"
    )

    print(
        "\nSaved model.pkl"
    )


    # ========================================================
    # 2. SAVE FEATURES
    # ========================================================

    with open(
        "features.json",
        "w"
    ) as f:

        json.dump(
            {
                "features": FEATURE_COLS
            },
            f,
            indent=2
        )

    print(
        "Saved features.json"
    )


    # ========================================================
    # 3. SAVE MODEL INFORMATION
    # ========================================================

    model_info = {

        "model_name":
            "aco_anomaly_detection",

        "version":
            "1.0",

        "model_type":
            WINNER,

        "target":
            "anomaly_score (higher = more unusual ACO behavior)",

        "trained_on_performance_year":
            TARGET_YEAR,

        "trained_on_n_rows":
            n_rows,

        "contamination_rate":
            CONTAMINATION,

        "evaluation_vs_rule_proxy":
            comparison["results"][WINNER],

        "feature_count":
            len(FEATURE_COLS),

        "features":
            FEATURE_COLS,

        "preprocessing": {
            "missing_value_strategy":
                "median",

            "completely_missing_feature_strategy":
                "zero",

            "scaling":
                "StandardScaler"
        },

        "usage_note": (
            "Pass raw feature columns in the exact order specified "
            "by features.json. The pipeline automatically performs "
            "missing-value imputation and standardization. "
            "model.predict(X) returns -1 for anomaly and 1 for normal. "
            "For LOF with novelty=True, use score_samples(X) or "
            "decision_function(X) for continuous anomaly scoring."
        ),
    }


    with open(
        "model_info.json",
        "w"
    ) as f:

        json.dump(
            model_info,
            f,
            indent=2
        )

    print(
        "Saved model_info.json"
    )


    # ========================================================
    # FINAL VALIDATION
    # ========================================================

    print(
        "\nTesting saved model..."
    )

    loaded_model = joblib.load(
        "model.pkl"
    )

    test_predictions = loaded_model.predict(
        pd.read_sql(
            "SELECT * FROM aco_anomaly_features",
            engine
        )[FEATURE_COLS]
    )

    print(
        f"Test predictions generated: "
        f"{len(test_predictions)}"
    )

    print(
        f"Anomalies detected: "
        f"{(test_predictions == -1).sum()}"
    )

    print(
        f"Normal records: "
        f"{(test_predictions == 1).sum()}"
    )


    print(
        "\n" + "=" * 70
    )

    print(
        "FINAL MODEL EXPORT COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        "\nAll 3 files are ready:"
    )

    print(
        "  model.pkl"
    )

    print(
        "  features.json"
    )

    print(
        "  model_info.json"
    )