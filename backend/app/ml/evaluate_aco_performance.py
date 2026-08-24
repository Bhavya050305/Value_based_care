# ================================================================
# FINAL 2023 → 2024 ACO PERFORMANCE EVALUATION
# ================================================================

from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ================================================================
# 1. PATHS
# ================================================================

# File:
# backend/app/ml/evaluate_aco_performance.py

BACKEND_DIR = Path(__file__).resolve().parents[2]

ARTIFACT_DIR = (
    BACKEND_DIR
    / "app"
    / "ml"
    / "artifacts"
)

INPUT_FILE = (
    ARTIFACT_DIR
    / "test_predictions_2023_2024.csv"
)

OUTPUT_FILE = (
    ARTIFACT_DIR
    / "aco_2023_2024_final_evaluation.csv"
)

METRICS_FILE = (
    ARTIFACT_DIR
    / "aco_2023_2024_all_metrics.csv"
)


# ================================================================
# 2. LOAD TEST PREDICTIONS
# ================================================================

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"Prediction file not found:\n{INPUT_FILE}\n\n"
        "Run train_aco_financial.py first."
    )


df = pd.read_csv(INPUT_FILE)


print("=" * 80)
print("FINAL 2023 → 2024 ACO PERFORMANCE EVALUATION")
print("=" * 80)

print(f"\nInput file : {INPUT_FILE}")
print(f"Rows       : {len(df):,}")

print("\nColumns:")
print(df.columns.tolist())


# ================================================================
# 3. REQUIRED COLUMNS
# ================================================================

required_columns = [
    "ACO_ID",
    "feature_year",
    "target_year",
    "target_GenSaveLoss",
    "predicted_GenSaveLoss",
    "absolute_error"
]

missing_columns = [
    col
    for col in required_columns
    if col not in df.columns
]

if missing_columns:

    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# ================================================================
# 4. VALIDATE DATA
# ================================================================

actual = pd.to_numeric(
    df["target_GenSaveLoss"],
    errors="coerce"
)

predicted = pd.to_numeric(
    df["predicted_GenSaveLoss"],
    errors="coerce"
)

if actual.isna().any():

    raise ValueError(
        "target_GenSaveLoss contains invalid values."
    )

if predicted.isna().any():

    raise ValueError(
        "predicted_GenSaveLoss contains invalid values."
    )


actual = actual.to_numpy(dtype=float)
predicted = predicted.to_numpy(dtype=float)


if len(actual) != len(predicted):

    raise ValueError(
        f"Length mismatch: "
        f"actual={len(actual)}, "
        f"predicted={len(predicted)}"
    )


# ================================================================
# 5. CALCULATE ERROR VALUES
# ================================================================

absolute_error = np.abs(
    actual - predicted
)

prediction_gap = (
    actual - predicted
)


# ================================================================
# METRIC 1 — MAE
# ================================================================

mae = mean_absolute_error(
    actual,
    predicted
)


# ================================================================
# METRIC 2 — RMSE
# ================================================================

rmse = np.sqrt(
    mean_squared_error(
        actual,
        predicted
    )
)


# ================================================================
# METRIC 3 — R²
# ================================================================

r2 = r2_score(
    actual,
    predicted
)


# ================================================================
# METRIC 4 — WAPE
# ================================================================

wape_denominator = np.sum(
    np.abs(actual)
)

if wape_denominator == 0:

    wape = np.nan

else:

    wape = (
        np.sum(absolute_error)
        / wape_denominator
    )


# ================================================================
# METRIC 5 — MEDIAN ABSOLUTE ERROR
# ================================================================

median_absolute_error = np.median(
    absolute_error
)


# ================================================================
# METRIC 6 — PREDICTION BIAS
# ================================================================

prediction_bias = np.mean(
    prediction_gap
)


# ================================================================
# METRIC 7 — OVER / UNDER PREDICTION
# ================================================================

underpredicted_count = np.sum(
    prediction_gap > 0
)

overpredicted_count = np.sum(
    prediction_gap < 0
)

exact_count = np.sum(
    prediction_gap == 0
)

total_count = len(actual)

underpredicted_pct = (
    underpredicted_count
    / total_count
    * 100
)

overpredicted_pct = (
    overpredicted_count
    / total_count
    * 100
)

exact_pct = (
    exact_count
    / total_count
    * 100
)


# ================================================================
# METRIC 8 — HIGH-VALUE ACO PERFORMANCE
# ================================================================

HIGH_VALUE_THRESHOLD = 50_000_000

high_value_mask = (
    actual >= HIGH_VALUE_THRESHOLD
)

high_value_actual = (
    actual[high_value_mask]
)

high_value_predicted = (
    predicted[high_value_mask]
)

high_value_count = len(
    high_value_actual
)


if high_value_count > 0:

    high_value_mae = mean_absolute_error(
        high_value_actual,
        high_value_predicted
    )

    high_value_rmse = np.sqrt(
        mean_squared_error(
            high_value_actual,
            high_value_predicted
        )
    )

    if (
        high_value_count >= 2
        and len(
            np.unique(high_value_actual)
        ) > 1
    ):

        high_value_r2 = r2_score(
            high_value_actual,
            high_value_predicted
        )

    else:

        high_value_r2 = np.nan


    high_value_wape_denominator = np.sum(
        np.abs(high_value_actual)
    )


    if high_value_wape_denominator != 0:

        high_value_wape = (
            np.sum(
                np.abs(
                    high_value_actual
                    - high_value_predicted
                )
            )
            / high_value_wape_denominator
        )

    else:

        high_value_wape = np.nan

else:

    high_value_mae = np.nan
    high_value_rmse = np.nan
    high_value_r2 = np.nan
    high_value_wape = np.nan


# ================================================================
# 6. PRINT ALL METRICS
# ================================================================

print("\n" + "=" * 80)
print("8 CORE EVALUATION METRICS")
print("=" * 80)

print(
    f"\n1. MAE"
    f"\n   ${mae:,.2f}"
)

print(
    f"\n2. RMSE"
    f"\n   ${rmse:,.2f}"
)

print(
    f"\n3. R²"
    f"\n   {r2:.4f}"
)

print(
    f"\n4. WAPE"
    f"\n   {wape * 100:.2f}%"
)

print(
    f"\n5. Median Absolute Error"
    f"\n   ${median_absolute_error:,.2f}"
)

print(
    f"\n6. Prediction Bias"
    f"\n   ${prediction_bias:,.2f}"
)

print(
    "\n7. Prediction Direction"
)

print(
    f"   Underpredicted : "
    f"{underpredicted_count:,} "
    f"({underpredicted_pct:.2f}%)"
)

print(
    f"   Overpredicted  : "
    f"{overpredicted_count:,} "
    f"({overpredicted_pct:.2f}%)"
)

print(
    f"   Exact          : "
    f"{exact_count:,} "
    f"({exact_pct:.2f}%)"
)

print(
    "\n8. High-Value ACO Performance"
)

print(
    f"   Threshold : "
    f"${HIGH_VALUE_THRESHOLD:,.0f}"
)

print(
    f"   ACO count : "
    f"{high_value_count:,}"
)

if high_value_count > 0:

    print(
        f"   MAE       : "
        f"${high_value_mae:,.2f}"
    )

    print(
        f"   RMSE      : "
        f"${high_value_rmse:,.2f}"
    )

    print(
        f"   R²        : "
        f"{high_value_r2:.4f}"
    )

    print(
        f"   WAPE      : "
        f"{high_value_wape * 100:.2f}%"
    )


# ================================================================
# 7. BUILD FINAL ACO PERFORMANCE TABLE
# ================================================================

final_evaluation = df[
    [
        "ACO_ID",
        "feature_year",
        "target_year",
        "target_GenSaveLoss",
        "predicted_GenSaveLoss"
    ]
].copy()


final_evaluation[
    "absolute_error"
] = np.abs(
    final_evaluation[
        "target_GenSaveLoss"
    ]
    -
    final_evaluation[
        "predicted_GenSaveLoss"
    ]
)


final_evaluation[
    "prediction_gap"
] = (
    final_evaluation[
        "target_GenSaveLoss"
    ]
    -
    final_evaluation[
        "predicted_GenSaveLoss"
    ]
)


# ================================================================
# 8. ABSOLUTE PERCENTAGE ERROR
# ================================================================

final_evaluation[
    "absolute_percentage_error"
] = np.where(

    final_evaluation[
        "target_GenSaveLoss"
    ].abs() > 0,

    (
        final_evaluation[
            "absolute_error"
        ]
        /
        final_evaluation[
            "target_GenSaveLoss"
        ].abs()
    ) * 100,

    np.nan
)


# ================================================================
# 9. PERFORMANCE STATUS
# ================================================================

def classify_performance(row):

    actual_value = (
        row["target_GenSaveLoss"]
    )

    gap = row["prediction_gap"]

    if actual_value < 0:

        return "Financial Loss"

    if actual_value == 0:

        return "Zero Actual"

    relative_gap = (
        abs(gap)
        /
        abs(actual_value)
    )

    if relative_gap <= 0.10:

        return "Expected Performance"

    elif gap > 0:

        return "Positive Deviation"

    else:

        return "Negative Deviation"


final_evaluation[
    "performance_status"
] = final_evaluation.apply(
    classify_performance,
    axis=1
)


# ================================================================
# 10. PRIORITY
# ================================================================

def classify_priority(row):

    actual_value = (
        row["target_GenSaveLoss"]
    )

    gap = row["prediction_gap"]

    abs_gap = abs(gap)

    if actual_value < 0:

        return "Critical"

    if abs_gap >= 50_000_000:

        return "Critical"

    if abs_gap >= 20_000_000:

        return "High"

    if abs_gap >= 10_000_000:

        return "Medium"

    return "Low"


final_evaluation[
    "priority"
] = final_evaluation.apply(
    classify_priority,
    axis=1
)


# ================================================================
# 11. HIGH-VALUE FLAG
# ================================================================

final_evaluation[
    "high_value_ACO"
] = (
    final_evaluation[
        "target_GenSaveLoss"
    ]
    >= HIGH_VALUE_THRESHOLD
)


# ================================================================
# 12. SORT
# ================================================================

priority_order = {

    "Critical": 1,

    "High": 2,

    "Medium": 3,

    "Low": 4
}


final_evaluation[
    "priority_rank"
] = (
    final_evaluation[
        "priority"
    ]
    .map(priority_order)
)


final_evaluation = (
    final_evaluation
    .sort_values(
        by=[
            "priority_rank",
            "absolute_error"
        ],
        ascending=[
            True,
            False
        ]
    )
    .drop(
        columns=["priority_rank"]
    )
    .reset_index(drop=True)
)


# ================================================================
# 13. SAVE FINAL ACO TABLE
# ================================================================

final_evaluation.to_csv(
    OUTPUT_FILE,
    index=False
)


# ================================================================
# 14. SAVE METRICS TABLE
# ================================================================

metrics_output = pd.DataFrame([{

    "test_period":
        "2023_to_2024",

    "ACO_count":
        total_count,

    "MAE":
        mae,

    "RMSE":
        rmse,

    "R2":
        r2,

    "WAPE":
        wape,

    "WAPE_percent":
        wape * 100,

    "Median_Absolute_Error":
        median_absolute_error,

    "Prediction_Bias":
        prediction_bias,

    "Underpredicted_count":
        underpredicted_count,

    "Underpredicted_percent":
        underpredicted_pct,

    "Overpredicted_count":
        overpredicted_count,

    "Overpredicted_percent":
        overpredicted_pct,

    "Exact_count":
        exact_count,

    "Exact_percent":
        exact_pct,

    "High_Value_Threshold":
        HIGH_VALUE_THRESHOLD,

    "High_Value_ACO_Count":
        high_value_count,

    "High_Value_MAE":
        high_value_mae,

    "High_Value_RMSE":
        high_value_rmse,

    "High_Value_R2":
        high_value_r2,

    "High_Value_WAPE":
        high_value_wape,

    "High_Value_WAPE_percent":
        high_value_wape * 100
}])


metrics_output.to_csv(
    METRICS_FILE,
    index=False
)


# ================================================================
# 15. PERFORMANCE SUMMARY
# ================================================================

status_summary = (
    final_evaluation[
        "performance_status"
    ]
    .value_counts()
    .rename_axis(
        "performance_status"
    )
    .reset_index(
        name="ACO_count"
    )
)


status_summary[
    "percentage"
] = (
    status_summary["ACO_count"]
    /
    total_count
    * 100
)


print("\n" + "=" * 80)
print("PERFORMANCE STATUS SUMMARY")
print("=" * 80)

print(
    status_summary.to_string(
        index=False
    )
)


# ================================================================
# 16. PRIORITY SUMMARY
# ================================================================

priority_summary = (
    final_evaluation[
        "priority"
    ]
    .value_counts()
    .rename_axis(
        "priority"
    )
    .reset_index(
        name="ACO_count"
    )
)


priority_summary[
    "percentage"
] = (
    priority_summary["ACO_count"]
    /
    total_count
    * 100
)


print("\n" + "=" * 80)
print("PRIORITY SUMMARY")
print("=" * 80)

print(
    priority_summary.to_string(
        index=False
    )
)


# ================================================================
# 17. DISPLAY FINAL TABLE
# ================================================================

print("\n" + "=" * 100)
print("FINAL ACO PERFORMANCE TABLE")
print("=" * 100)

print(
    final_evaluation.to_string(
        index=False,
        max_rows=200
    )
)


# ================================================================
# 18. FINAL OUTPUT
# ================================================================

print("\n" + "=" * 80)
print("EVALUATION COMPLETED")
print("=" * 80)

print(
    f"\nFinal ACO table:"
    f"\n{OUTPUT_FILE}"
)

print(
    f"\nAll metrics:"
    f"\n{METRICS_FILE}"
)

print("\n" + "=" * 80)