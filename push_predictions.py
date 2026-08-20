"""
STEP 4 — Uses the exported model.pkl to score every ACO.

Writes:
    aco_anomalies
    aco_risk_scores
    aco_alerts

Run AFTER:
    python export_final_model.py
"""

import json
import joblib
import pandas as pd
import numpy as np

from db import engine


# ============================================================
# LOAD EXPORTED MODEL
# ============================================================

pipeline = joblib.load("model.pkl")

with open("features.json") as f:
    FEATURE_COLS = json.load(f)["features"]


# ============================================================
# SCORE ALL ACOS
# ============================================================

def score_all_acos():

    df = pd.read_sql(
        "SELECT * FROM aco_anomaly_features",
        engine
    )

    # --------------------------------------------------------
    # Validate columns
    # --------------------------------------------------------

    missing_columns = [
        col
        for col in FEATURE_COLS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required feature columns:\n"
            + "\n".join(
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

    X = df[FEATURE_COLS].copy()

    # --------------------------------------------------------
    # IMPORTANT:
    # Do NOT manually impute or scale here.
    #
    # model.pkl already contains:
    #
    # SimpleImputer
    #       ↓
    # StandardScaler
    #       ↓
    # LOF
    #
    # Therefore we pass raw features directly.
    # --------------------------------------------------------

    df["is_anomaly"] = (
        pipeline.predict(X) == -1
    )

    # --------------------------------------------------------
    # Continuous anomaly score
    # --------------------------------------------------------

    if hasattr(pipeline, "score_samples"):

        df["anomaly_score"] = (
            -pipeline.score_samples(X)
        )

    elif hasattr(
        pipeline,
        "decision_function"
    ):

        df["anomaly_score"] = (
            -pipeline.decision_function(X)
        )

    else:

        raise ValueError(
            "The exported model does not support "
            "score_samples or decision_function."
        )

    # --------------------------------------------------------
    # Get properly transformed features
    #
    # Use the complete preprocessing pipeline rather than
    # directly calling StandardScaler.
    # --------------------------------------------------------

    imputer = pipeline.named_steps["imputer"]
    scaler = pipeline.named_steps["scaler"]

    X_imputed = imputer.transform(X)

    X_scaled = scaler.transform(
        X_imputed
    )

    X_scaled_df = pd.DataFrame(
        X_scaled,
        columns=FEATURE_COLS,
        index=df.index
    )

    # --------------------------------------------------------
    # Identify strongest anomalous metric
    # --------------------------------------------------------

    df["top_anomalous_metric"] = (
        X_scaled_df.abs().idxmax(axis=1)
    )

    return df


# ============================================================
# BUILD OUTPUT TABLES
# ============================================================

def build_output_tables(df):

    flagged = df[
        df["is_anomaly"]
    ].copy()

    # --------------------------------------------------------
    # ACO ANOMALIES
    # --------------------------------------------------------

    if len(flagged) > 0:

        # Rank anomaly scores from lowest to highest
        # and divide into severity groups.

        flagged["severity"] = pd.qcut(
            flagged["anomaly_score"],
            q=[0, 0.50, 0.85, 1.0],
            labels=[
                "MEDIUM",
                "HIGH",
                "CRITICAL"
            ],
            duplicates="drop"
        )

    else:

        flagged["severity"] = pd.Series(
            dtype="object"
        )

    aco_anomalies = flagged[
        [
            "ACO_ID",
            "performance_year",
            "anomaly_score",
            "top_anomalous_metric",
            "severity"
        ]
    ].copy()

    # --------------------------------------------------------
    # ACO RISK SCORES
    # --------------------------------------------------------

    # Rank-based risk levels are more stable than equal-width
    # bins when anomaly scores are highly concentrated.

    df["risk_percentile"] = (
        df["anomaly_score"]
        .rank(
            pct=True,
            method="average"
        )
    )

    df["risk_level"] = np.select(
        [
            df["risk_percentile"] <= 0.50,
            df["risk_percentile"] <= 0.85,
        ],
        [
            "LOW",
            "MEDIUM",
        ],
        default="HIGH"
    )

    aco_risk_scores = df[
        [
            "ACO_ID",
            "performance_year",
            "anomaly_score",
            "risk_level",
            "is_anomaly"
        ]
    ].copy()

    aco_risk_scores = (
        aco_risk_scores.rename(
            columns={
                "anomaly_score":
                    "ml_anomaly_score"
            }
        )
    )

    # --------------------------------------------------------
    # ACO ALERTS
    # --------------------------------------------------------

    alert_rows = []

    for _, row in flagged.iterrows():

        alert_rows.append(
            {
                "ACO_ID":
                    row["ACO_ID"],

                "performance_year":
                    row["performance_year"],

                "alert_type":
                    "Utilization Anomaly",

                "severity":
                    row["severity"],

                "message":
                    (
                        f"{row['top_anomalous_metric']} "
                        f"flagged as anomalous "
                        f"(score "
                        f"{row['anomaly_score']:.2f})"
                    ),
            }
        )

    aco_alerts = pd.DataFrame(
        alert_rows,
        columns=[
            "ACO_ID",
            "performance_year",
            "alert_type",
            "severity",
            "message"
        ]
    )

    return (
        aco_anomalies,
        aco_risk_scores,
        aco_alerts
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("ACO ANOMALY PREDICTION PUSH")
    print("=" * 70)

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    scored = score_all_acos()

    print(
        f"\nScored {len(scored)} ACOs."
    )

    print(
        f"Flagged "
        f"{scored['is_anomaly'].sum()} "
        f"as anomalous."
    )

    # --------------------------------------------------------
    # Build tables
    # --------------------------------------------------------

    (
        aco_anomalies,
        aco_risk_scores,
        aco_alerts
    ) = build_output_tables(scored)

    # --------------------------------------------------------
    # Save to Supabase
    # --------------------------------------------------------

    tables = [
        (
            "aco_anomalies",
            aco_anomalies
        ),
        (
            "aco_risk_scores",
            aco_risk_scores
        ),
        (
            "aco_alerts",
            aco_alerts
        ),
    ]

    for name, table in tables:

        table.to_sql(
            name,
            engine,
            if_exists="replace",
            index=False
        )

        print(
            f"Saved {name}: "
            f"{len(table)} rows"
        )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "PREDICTION PUSH COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"\nACOs scored: "
        f"{len(scored)}"
    )

    print(
        f"Anomalies: "
        f"{len(aco_anomalies)}"
    )

    print(
        f"Risk scores: "
        f"{len(aco_risk_scores)}"
    )

    print(
        f"Alerts: "
        f"{len(aco_alerts)}"
    )

    print(
        "\nYour LLM project's "
        "context_builder.py can now read "
        "real anomaly data from:"
    )

    print(
        "  aco_anomalies"
    )

    print(
        "  aco_risk_scores"
    )

    print(
        "  aco_alerts"
    )

    print(
        "\nNext step:"
    )

    print(
        "  python batch_generate.py"
    )