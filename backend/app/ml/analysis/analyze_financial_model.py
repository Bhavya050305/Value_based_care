import os
from pathlib import Path

import joblib
import pandas as pd
import numpy as np

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ============================================================
# 1. ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env")


# ============================================================
# 2. DATABASE
# ============================================================

engine = create_engine(DATABASE_URL)


# ============================================================
# 3. LOAD TRAINED MODEL
# ============================================================

MODEL_PATH = (
    BASE_DIR
    / "app"
    / "ml"
    / "artifacts"
    / "random_forest_GenSaveLoss.joblib"
)

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model not found: {MODEL_PATH}"
    )

pipeline = joblib.load(MODEL_PATH)

if not hasattr(pipeline, "named_steps"):
    raise ValueError(
        "Loaded model is not a valid sklearn Pipeline."
    )

if "model" not in pipeline.named_steps:
    raise ValueError(
        "Pipeline does not contain a 'model' step."
    )

if "preprocessor" not in pipeline.named_steps:
    raise ValueError(
        "Pipeline does not contain a 'preprocessor' step."
    )

model = pipeline.named_steps["model"]
preprocessor = pipeline.named_steps["preprocessor"]


# ============================================================
# 4. LOAD DATA
# ============================================================

QUERY = """
SELECT *
FROM public.aco_financial_ml_training
ORDER BY "feature_year", "ACO_ID";
"""

with engine.connect() as connection:
    df = pd.read_sql(text(QUERY), connection)


if df.empty:
    raise ValueError(
        "aco_financial_ml_training returned zero rows."
    )


print("=" * 70)
print("ACO FINANCIAL ML MODEL ANALYSIS")
print("=" * 70)

print("\nDataset shape:")
print(df.shape)

print("\nAvailable columns:")
print(df.columns.tolist())


# ============================================================
# 5. TARGET DEFINITION
# ============================================================

TARGET = "target_GenSaveLoss"


if TARGET not in df.columns:
    raise ValueError(
        f"Target column '{TARGET}' not found in dataset."
    )


# ============================================================
# 6. EXPLICIT LEAKAGE / IDENTIFIER COLUMNS
# ============================================================

# These columns must NEVER be used as ML input features.
#
# target_GenSaveLoss:
#     Future value we are trying to predict.
#
# next_year_actual_gensaveloss:
#     Actual future value used for validation/ground truth.
#
# target_year:
#     Identifies the future prediction year.
#
# ACO_ID:
#     Entity identifier, not a predictive numerical feature.
#
# feature_year:
#     Time reference. We use it for temporal splitting/alignment,
#     but it should not be directly fed into the model.

DROP_COLUMNS = [
    "ACO_ID",
    "feature_year",
    "target_year",
    "target_GenSaveLoss",
    "next_year_actual_gensaveloss",
]


# ============================================================
# 7. DATA LEAKAGE AUDIT
# ============================================================

print("\n" + "=" * 70)
print("DATA LEAKAGE AUDIT")
print("=" * 70)


# ------------------------------------------------------------
# 7.1 Check target-related columns
# ------------------------------------------------------------

target_related_columns = [
    "target_GenSaveLoss",
    "next_year_actual_gensaveloss",
    "target_year",
]

print("\nTarget / future-related columns:")

for col in target_related_columns:

    if col in df.columns:
        print(f"  FOUND      : {col}")
    else:
        print(f"  NOT FOUND  : {col}")


# ------------------------------------------------------------
# 7.2 Check whether forbidden columns are candidates
# ------------------------------------------------------------

candidate_features_before_filter = [
    col
    for col in df.columns
    if col not in DROP_COLUMNS
]


found_forbidden_features = [
    col
    for col in DROP_COLUMNS
    if col in candidate_features_before_filter
]


print("\nForbidden columns inside candidate feature set:")

if found_forbidden_features:

    for col in found_forbidden_features:
        print(f"  ❌ {col}")

else:

    print(
        "  ✅ No explicitly forbidden columns "
        "are included."
    )


# ------------------------------------------------------------
# 7.3 Verify ACO_ID
# ------------------------------------------------------------

print("\nIdentifier audit:")

if "ACO_ID" in candidate_features_before_filter:

    print(
        "  ❌ ACO_ID is present in candidate features."
    )

else:

    print(
        "  ✅ ACO_ID excluded."
    )


# ------------------------------------------------------------
# 7.4 Verify year columns
# ------------------------------------------------------------

print("\nTemporal-column audit:")

for col in [
    "feature_year",
    "target_year",
]:

    if col in candidate_features_before_filter:

        print(
            f"  ❌ {col} is present in candidate features."
        )

    else:

        print(
            f"  ✅ {col} excluded."
        )


# ------------------------------------------------------------
# 7.5 Verify target columns
# ------------------------------------------------------------

print("\nTarget leakage audit:")

for col in [
    "target_GenSaveLoss",
    "next_year_actual_gensaveloss",
]:

    if col in candidate_features_before_filter:

        print(
            f"  ❌ {col} is present in candidate features."
        )

    else:

        print(
            f"  ✅ {col} excluded."
        )


# ============================================================
# 8. BUILD CURRENT-YEAR CANDIDATE FEATURES
# ============================================================

candidate_features = [
    col
    for col in df.columns
    if col not in DROP_COLUMNS
]


# ============================================================
# 9. REMOVE FEATURES WITH ZERO TRAINING OBSERVATIONS
# ============================================================

train_df = df[
    df["feature_year"].isin([2020, 2021])
].copy()


if train_df.empty:

    raise ValueError(
        "No training rows found for feature_year 2020/2021."
    )


feature_columns = [
    col
    for col in candidate_features
    if train_df[col].notna().any()
]


# ============================================================
# 10. FINAL FEATURE AUDIT
# ============================================================

print("\n" + "=" * 70)
print("FINAL FEATURE AUDIT")
print("=" * 70)

print(f"\nCandidate features : {len(candidate_features)}")
print(f"Final features     : {len(feature_columns)}")


remaining_forbidden = [
    col
    for col in feature_columns
    if col in DROP_COLUMNS
]


if remaining_forbidden:

    print(
        "\n❌ LEAKAGE DETECTED:"
    )

    for col in remaining_forbidden:
        print(f"   {col}")

    raise ValueError(
        "Forbidden target/future/identifier columns "
        "remain in feature_columns. "
        "Stop before using this feature set."
    )

else:

    print(
        "\n✅ No direct target/future/identifier "
        "columns remain in feature_columns."
    )


# ============================================================
# 11. CRITICAL FINANCIAL FEATURE AUDIT
# ============================================================

critical_features = [
    "GenSaveLoss",
    "EarnSaveLoss",
    "FinancialGap",
    "SavingsLossPct",
    "GenSaveLossYoYPct",
]


print("\nCritical financial features:")

for col in critical_features:

    if col in feature_columns:

        print(f"  ✓ {col}")

    else:

        print(f"  - {col}")


# ============================================================
# 12. IMPORTANT WARNING ABOUT GenSaveLoss
# ============================================================

if "GenSaveLoss" in feature_columns:

    print("\n" + "=" * 70)
    print("IMPORTANT: GenSaveLoss TEMPORAL CHECK")
    print("=" * 70)

    print(
        """
GenSaveLoss is being used as an input feature.

This is valid ONLY if GenSaveLoss represents
the ACO's value from feature_year.

Expected relationship:

    feature_year GenSaveLoss
              ↓
            MODEL
              ↓
    target_year GenSaveLoss

Example:

    2020 GenSaveLoss → predict 2021 GenSaveLoss

If GenSaveLoss contains the target-year/future value,
that would constitute target leakage.

This cannot be determined from the column name alone;
its SQL/table construction must be verified.
"""
    )


# ============================================================
# 13. GET ACTUAL FEATURES USED BY THE LOADED MODEL
# ============================================================

print("\n" + "=" * 70)
print("LOADED MODEL FEATURE AUDIT")
print("=" * 70)


try:

    transformed_feature_names = (
        preprocessor.get_feature_names_out()
    )

except Exception as exc:

    raise ValueError(
        "Unable to obtain transformed feature names "
        "from the model preprocessor."
    ) from exc


print(
    f"\nTransformed model features: "
    f"{len(transformed_feature_names)}"
)


# ============================================================
# 14. MAP TRANSFORMED FEATURES TO ORIGINAL FEATURES
# ============================================================

def original_feature_name(name):

    if name.startswith("numeric__"):

        return name.replace(
            "numeric__",
            "",
            1
        )


    if name.startswith("categorical__"):

        name = name.replace(
            "categorical__",
            "",
            1
        )

        # Find original categorical column
        for col in feature_columns:

            prefix = f"{col}_"

            if name.startswith(prefix):

                return col

        return name


    return name


model_feature_mapping = pd.DataFrame({
    "transformed_feature": transformed_feature_names
})


model_feature_mapping["feature"] = (
    model_feature_mapping[
        "transformed_feature"
    ]
    .apply(original_feature_name)
)


# ============================================================
# 15. AUDIT ACTUAL MODEL FEATURES FOR LEAKAGE
# ============================================================

actual_model_features = set(
    model_feature_mapping["feature"]
)


actual_leakage_features = [
    col
    for col in DROP_COLUMNS
    if col in actual_model_features
]


print("\nActual features represented in loaded model:")

print(
    model_feature_mapping[
        "feature"
    ]
    .drop_duplicates()
    .to_string(index=False)
)


print("\nActual model leakage audit:")

if actual_leakage_features:

    print(
        "\n❌ POTENTIAL DIRECT LEAKAGE FOUND "
        "IN LOADED MODEL:"
    )

    for col in actual_leakage_features:

        print(
            f"   ❌ {col}"
        )

    print(
        "\nIMPORTANT:"
    )

    print(
        "The existing .joblib model should NOT be "
        "used for final evaluation until it is retrained "
        "without these features."
    )

else:

    print(
        "  ✅ No explicitly forbidden columns "
        "were found in the loaded model."
    )


# ============================================================
# 16. GET RANDOM FOREST IMPORTANCE
# ============================================================

importances = model.feature_importances_


if len(transformed_feature_names) != len(importances):

    raise ValueError(
        f"Feature-name count "
        f"({len(transformed_feature_names)}) "
        f"does not match importance count "
        f"({len(importances)})."
    )


importance_df = pd.DataFrame({

    "transformed_feature":
        transformed_feature_names,

    "importance":
        importances,
})


# ============================================================
# 17. MAP TRANSFORMED FEATURES TO ORIGINAL FEATURES
# ============================================================

importance_df["feature"] = (
    importance_df[
        "transformed_feature"
    ]
    .apply(original_feature_name)
)


# ============================================================
# 18. AGGREGATE IMPORTANCE
# ============================================================

feature_importance = (
    importance_df
    .groupby(
        "feature",
        as_index=False
    )["importance"]
    .sum()
    .sort_values(
        "importance",
        ascending=False
    )
)


feature_importance["importance_pct"] = (
    feature_importance["importance"] * 100
)


feature_importance["rank"] = range(
    1,
    len(feature_importance) + 1
)


# ============================================================
# 19. PRINT RESULTS
# ============================================================

print("\n" + "=" * 70)
print("RANDOM FOREST FEATURE IMPORTANCE")
print("=" * 70)

print(
    feature_importance[
        [
            "rank",
            "feature",
            "importance",
            "importance_pct",
        ]
    ]
    .to_string(index=False)
)


# ============================================================
# 20. SAVE RESULTS
# ============================================================

ARTIFACT_DIR = (
    BASE_DIR
    / "app"
    / "ml"
    / "artifacts"
)

ARTIFACT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


output_path = (
    ARTIFACT_DIR
    / "random_forest_feature_importance.csv"
)


feature_importance[
    [
        "rank",
        "feature",
        "importance",
        "importance_pct",
    ]
].to_csv(
    output_path,
    index=False
)


# ============================================================
# 21. TOP 15 FEATURES
# ============================================================

print("\n" + "=" * 70)
print("TOP 15 FEATURES")
print("=" * 70)

print(
    feature_importance
    .head(15)
    .to_string(index=False)
)


# ============================================================
# 22. FINAL STATUS
# ============================================================

print("\n" + "=" * 70)
print("LEAKAGE AUDIT STATUS")
print("=" * 70)


if actual_leakage_features:

    print(
        "❌ FAILED"
    )

    print(
        "The currently loaded model contains "
        "one or more explicitly forbidden columns."
    )

    print(
        "Do NOT use this model for final evaluation."
    )

else:

    print(
        "✅ DIRECT LEAKAGE CHECK PASSED"
    )

    print(
        "No explicitly forbidden target/future/ID "
        "columns were detected in the loaded model."
    )


print("\nFeature importance saved to:")
print(output_path)