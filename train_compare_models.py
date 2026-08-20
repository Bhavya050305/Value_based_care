"""
STEP 2 — Train and compare anomaly detection models.

Historical data:
    2021 + 2022 + 2023

Purpose:
    Learn the normal/anomalous behavior patterns of ACOs using
    historical feature data.

Models:
    1. Isolation Forest
    2. Local Outlier Factor
    3. One-Class SVM

Because there is no true anomaly label, a rule-based proxy is
used only as a weak reference for model comparison.

The winning model is selected using F1 score against the
rule-based proxy.

Run:
    python train_compare_models.py
"""

import json
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.metrics import precision_score, recall_score, f1_score

from db import engine, CONTAMINATION


# ============================================================
# CONFIGURATION
# ============================================================

FEATURE_COLS = [
    "ed_utilization_change_yoy",
    "admission_change_yoy",
    "em_utilization_change_yoy",
    "advanced_imaging_change_yoy",
    "readmission_proxy_rate_yoy_change",
    "savings_yoy_change_pct",
    "expenditure_variance_pct",
    "quality_change_yoy",
    "provider_utilization_variation",
    "provider_cost_variation",
]

TRAINING_YEARS = [2021, 2022, 2023]

os.makedirs("plots", exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

def load_and_prepare():

    print("=" * 70)
    print("LOADING ANOMALY FEATURES")
    print("=" * 70)

    query = """
        SELECT *
        FROM aco_anomaly_features
        WHERE performance_year IN (2021, 2022, 2023)
        ORDER BY performance_year, "ACO_ID"
    """

    df = pd.read_sql(query, engine)

    print(f"Rows: {len(df)}")

    print(
        f"Training years: "
        f"{sorted(df['performance_year'].unique().tolist())}"
    )

    print("\nRows by year:")

    print(
        df.groupby("performance_year")
        .size()
        .to_string()
    )

    # --------------------------------------------------------
    # Check columns
    # --------------------------------------------------------

    missing_columns = [
        col
        for col in FEATURE_COLS
        if col not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "\nMissing required feature columns:\n"
            + "\n".join(
                f"  - {col}"
                for col in missing_columns
            )
        )

    # --------------------------------------------------------
    # Numeric conversion
    # --------------------------------------------------------

    for col in FEATURE_COLS:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Missing values before imputation
    # --------------------------------------------------------

    missing_before = (
        df[FEATURE_COLS]
        .isnull()
        .sum()
    )

    print("\nMissing values before impute:")

    display_missing = (
        missing_before[
            missing_before > 0
        ]
    )

    if len(display_missing) > 0:
        print(display_missing)
    else:
        print("None")

    # --------------------------------------------------------
    # Median imputation
    # --------------------------------------------------------

    print("\nImputation:")

    imputation_values = {}

    for col in FEATURE_COLS:

        missing_count = df[col].isna().sum()

        if missing_count == 0:
            continue

        median_value = df[col].median()

        if pd.isna(median_value):

            median_value = 0.0

            print(
                f"  {col}: {missing_count} missing "
                f"-> filled with 0.0"
            )

        else:

            print(
                f"  {col}: {missing_count} missing "
                f"-> median = {median_value:.6f}"
            )

        imputation_values[col] = float(
            median_value
        )

        df[col] = df[col].fillna(
            median_value
        )

    # --------------------------------------------------------
    # Final missing check
    # --------------------------------------------------------

    remaining_missing = (
        df[FEATURE_COLS]
        .isnull()
        .sum()
        .sum()
    )

    if remaining_missing > 0:

        raise ValueError(
            "Missing values remain after imputation."
        )

    print("\nMissing values after impute:")
    print(remaining_missing)

    # --------------------------------------------------------
    # Scaling
    # --------------------------------------------------------

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(
        df[FEATURE_COLS]
    )

    if not np.isfinite(X_scaled).all():

        raise ValueError(
            "Scaled feature matrix contains "
            "NaN or infinite values."
        )

    print(
        f"\nScaled feature matrix: "
        f"{X_scaled.shape}"
    )

    return (
        df,
        X_scaled,
        scaler,
        imputation_values
    )


# ============================================================
# RULE-BASED PROXY
# ============================================================

def build_rule_proxy(df):

    print("\n" + "=" * 70)
    print("RULE-BASED PROXY")
    print("=" * 70)

    expenditure_threshold = (
        df["expenditure_variance_pct"]
        .quantile(0.90)
    )

    quality_threshold = (
        df["quality_change_yoy"]
        .quantile(0.10)
    )

    ed_threshold = (
        df["ed_utilization_change_yoy"]
        .quantile(0.90)
    )

    print(
        f"Expenditure variance 90th percentile: "
        f"{expenditure_threshold:.6f}"
    )

    print(
        f"Quality change 10th percentile: "
        f"{quality_threshold:.6f}"
    )

    print(
        f"ED utilization change 90th percentile: "
        f"{ed_threshold:.6f}"
    )

    rule_flag = (
        (
            df["expenditure_variance_pct"]
            > expenditure_threshold
        )
        |
        (
            df["quality_change_yoy"]
            < quality_threshold
        )
        |
        (
            df["ed_utilization_change_yoy"]
            > ed_threshold
        )
    )

    return rule_flag.values


# ============================================================
# TRAIN MODELS
# ============================================================

def train_all_models(X_scaled):

    models = {}

    # --------------------------------------------------------
    # Isolation Forest
    # --------------------------------------------------------

    isolation_forest = IsolationForest(
        contamination=CONTAMINATION,
        random_state=42,
        n_estimators=200
    )

    iso_pred = isolation_forest.fit_predict(
        X_scaled
    )

    iso_score = -isolation_forest.score_samples(
        X_scaled
    )

    models["Isolation Forest"] = {
        "pred": iso_pred,
        "score": iso_score,
        "fitted": isolation_forest
    }

    # --------------------------------------------------------
    # LOF
    # --------------------------------------------------------

    lof = LocalOutlierFactor(
        contamination=CONTAMINATION,
        novelty=False
    )

    lof_pred = lof.fit_predict(
        X_scaled
    )

    lof_score = (
        -lof.negative_outlier_factor_
    )

    models["LOF"] = {
        "pred": lof_pred,
        "score": lof_score,
        "fitted": lof
    }

    # --------------------------------------------------------
    # One-Class SVM
    # --------------------------------------------------------

    ocsvm = OneClassSVM(
        nu=CONTAMINATION,
        kernel="rbf",
        gamma="auto"
    )

    ocsvm_pred = ocsvm.fit_predict(
        X_scaled
    )

    ocsvm_score = (
        -ocsvm.decision_function(
            X_scaled
        )
    )

    models["One-Class SVM"] = {
        "pred": ocsvm_pred,
        "score": ocsvm_score,
        "fitted": ocsvm
    }

    return models


# ============================================================
# EVALUATE
# ============================================================

def evaluate(models, rule_flag):

    results = {}

    for name, model in models.items():

        pred_anomaly = (
            model["pred"] == -1
        )

        precision = precision_score(
            rule_flag,
            pred_anomaly,
            zero_division=0
        )

        recall = recall_score(
            rule_flag,
            pred_anomaly,
            zero_division=0
        )

        f1 = f1_score(
            rule_flag,
            pred_anomaly,
            zero_division=0
        )

        new_catches = (
            pred_anomaly
            &
            (~rule_flag)
        )

        results[name] = {
            "precision": round(
                float(precision),
                3
            ),
            "recall": round(
                float(recall),
                3
            ),
            "f1": round(
                float(f1),
                3
            ),
            "n_flagged": int(
                pred_anomaly.sum()
            ),
            "n_new_catches": int(
                new_catches.sum()
            )
        }

    return results


# ============================================================
# PLOTS
# ============================================================

def make_plots(
    models,
    results
):

    # --------------------------------------------------------
    # Plot 02
    # --------------------------------------------------------

    counts = {
        name: int(
            (model["pred"] == -1).sum()
        )
        for name, model in models.items()
    }

    plt.figure(
        figsize=(7, 4)
    )

    plt.bar(
        counts.keys(),
        counts.values()
    )

    plt.title(
        "Anomalies Flagged per Model"
    )

    plt.ylabel(
        "Number of ACOs"
    )

    plt.tight_layout()

    plt.savefig(
        "plots/02_model_anomaly_counts.png",
        dpi=150
    )

    plt.close()

    # --------------------------------------------------------
    # Plot 03
    # --------------------------------------------------------

    score_df = pd.DataFrame(
        {
            name: model["score"]
            for name, model in models.items()
        }
    )

    plt.figure(
        figsize=(5, 4)
    )

    sns.heatmap(
        score_df.corr(),
        annot=True,
        vmin=0,
        vmax=1
    )

    plt.title(
        "Score Correlation Between Models"
    )

    plt.tight_layout()

    plt.savefig(
        "plots/03_model_correlation.png",
        dpi=150
    )

    plt.close()

    # --------------------------------------------------------
    # Plot 04
    # --------------------------------------------------------

    metrics_df = (
        pd.DataFrame(results)
        .T[
            [
                "precision",
                "recall",
                "f1"
            ]
        ]
    )

    metrics_df.plot(
        kind="bar",
        figsize=(8, 5)
    )

    plt.title(
        "Model Comparison: Agreement with Rule-Based Proxy"
    )

    plt.ylabel(
        "Score"
    )

    plt.xticks(
        rotation=0
    )

    plt.ylim(
        0,
        1
    )

    plt.tight_layout()

    plt.savefig(
        "plots/04_model_comparison_f1.png",
        dpi=150
    )

    plt.close()

    print("\nSaved:")

    print(
        "  plots/02_model_anomaly_counts.png"
    )

    print(
        "  plots/03_model_correlation.png"
    )

    print(
        "  plots/04_model_comparison_f1.png"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("ACO ANOMALY MODEL TRAINING")
    print("=" * 70)

    print(
        "\nTraining years:",
        TRAINING_YEARS
    )

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    (
        df,
        X_scaled,
        scaler,
        imputation_values
    ) = load_and_prepare()

    # --------------------------------------------------------
    # Rule proxy
    # --------------------------------------------------------

    rule_flag = build_rule_proxy(
        df
    )

    print(
        f"\nRule-based proxy flagged "
        f"{rule_flag.sum()} / {len(df)} "
        f"ACOs as anomalous."
    )

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("TRAINING MODELS")
    print("=" * 70)

    models = train_all_models(
        X_scaled
    )

    print(
        "All 3 models trained successfully."
    )

    # --------------------------------------------------------
    # Evaluate
    # --------------------------------------------------------

    results = evaluate(
        models,
        rule_flag
    )

    print(
        "\n--- MODEL COMPARISON ---"
    )

    for name, result in results.items():

        print(
            f"{name}: "
            f"precision={result['precision']}, "
            f"recall={result['recall']}, "
            f"F1={result['f1']}, "
            f"flagged={result['n_flagged']}, "
            f"new_catches_vs_rules={result['n_new_catches']}"
        )

    # --------------------------------------------------------
    # Plots
    # --------------------------------------------------------

    make_plots(
        models,
        results
    )

    # --------------------------------------------------------
    # Winner
    # --------------------------------------------------------

    winner = max(
        results,
        key=lambda name:
        results[name]["f1"]
    )

    print(
        f"\n>>> WINNER: {winner} "
        f"(F1={results[winner]['f1']}) <<<"
    )

    # --------------------------------------------------------
    # Top anomalies
    # --------------------------------------------------------

    df["winner_score"] = (
        models[winner]["score"]
    )

    top10 = (
        df
        .nlargest(
            10,
            "winner_score"
        )
    )

    plt.figure(
        figsize=(10, 5)
    )

    sns.barplot(
        data=top10,
        y="ACO_ID",
        x="winner_score"
    )

    plt.title(
        f"Top 10 Anomalous ACOs — {winner}"
    )

    plt.xlabel(
        "Anomaly Score"
    )

    plt.tight_layout()

    plt.savefig(
        "plots/05_top10_anomalies.png",
        dpi=150
    )

    plt.close()

    print(
        "Saved plots/05_top10_anomalies.png"
    )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    with open(
        "comparison_results.json",
        "w"
    ) as f:

        json.dump(
            {
                "results": results,
                "winner": winner,
                "feature_cols": FEATURE_COLS,
                "training_years": TRAINING_YEARS,
                "contamination": CONTAMINATION,
                "n_training_rows": len(df),
                "imputation_values": imputation_values
            },
            f,
            indent=2
        )

    print(
        "\nSaved comparison_results.json "
        "— read by export_final_model.py next."
    )

    print("\n" + "=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)