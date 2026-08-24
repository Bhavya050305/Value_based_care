import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor
)

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# 1. LOAD ENVIRONMENT
# ============================================================

# Script:
# backend/app/ml/training/train_aco_financial.py
#
# .env:
# backend/.env

BACKEND_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = BACKEND_DIR / ".env"

load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        f"DATABASE_URL is missing from {ENV_PATH}"
    )

print("=" * 70)
print("ACO FINANCIAL ML MODEL TRAINING")
print("=" * 70)

print(f".env path       : {ENV_PATH}")
print("DATABASE_URL    : LOADED")


# ============================================================
# 2. DATABASE CONNECTION
# ============================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ============================================================
# 3. LOAD DATA
# ============================================================

QUERY = """
SELECT *
FROM public.aco_financial_ml_training
ORDER BY "feature_year", "ACO_ID";
"""

with engine.connect() as connection:

    df = pd.read_sql(
        text(QUERY),
        connection
    )


print("\n" + "=" * 70)
print("DATASET")
print("=" * 70)

print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")

print("\nFeature-year distribution:")

print(
    df["feature_year"]
    .value_counts()
    .sort_index()
)


# ============================================================
# 4. REQUIRED COLUMNS
# ============================================================

TARGET = "target_GenSaveLoss"

required_columns = [
    "ACO_ID",
    "feature_year",
    "target_year",
    TARGET
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


# ============================================================
# 5. TARGET VALIDATION
# ============================================================

target_nulls = (
    df[TARGET]
    .isna()
    .sum()
)

if target_nulls > 0:

    raise ValueError(
        f"{TARGET} contains {target_nulls} NULL values."
    )


# ============================================================
# 6. TEMPORAL VALIDATION
# ============================================================

invalid_temporal_rows = df[
    df["target_year"] !=
    df["feature_year"] + 1
]

if len(invalid_temporal_rows) > 0:

    raise ValueError(
        "Invalid temporal relationship detected.\n"
        "Every row must satisfy:\n"
        "target_year = feature_year + 1"
    )


print("\nTemporal relationship:")

print(
    "feature_year → target_year = VALID"
)

print(
    f"Valid rows: {len(df)}"
)


# ============================================================
# 7. DIRECT DATA LEAKAGE AUDIT
# ============================================================

print("\n" + "=" * 70)
print("DATA LEAKAGE AUDIT")
print("=" * 70)


FORBIDDEN_FEATURES = [
    "ACO_ID",
    "feature_year",
    "target_year",
    "target_GenSaveLoss",
    "next_year_actual_gensaveloss"
]


candidate_features = [
    col
    for col in df.columns
    if col not in FORBIDDEN_FEATURES
]


found_forbidden = [
    col
    for col in FORBIDDEN_FEATURES
    if col in candidate_features
]


if found_forbidden:

    raise ValueError(
        "LEAKAGE DETECTED. "
        f"Forbidden columns found in features: "
        f"{found_forbidden}"
    )


print("Forbidden columns checked:")

for col in FORBIDDEN_FEATURES:

    print(
        f"  {col}: "
        f"{'PRESENT IN DATA' if col in df.columns else 'NOT PRESENT'}"
    )


print(
    "\n✅ No forbidden columns are present "
    "in candidate feature set."
)


# ============================================================
# 8. TEMPORAL TRAIN / VALIDATION / TEST SPLIT
# ============================================================

#
# TRAIN
#   2020 → 2021
#   2021 → 2022
#
# VALIDATION
#   2022 → 2023
#
# TEST
#   2023 → 2024
#

train_df = df[
    df["feature_year"].isin([2020, 2021])
].copy()


validation_df = df[
    df["feature_year"] == 2022
].copy()


test_df = df[
    df["feature_year"] == 2023
].copy()


if train_df.empty:
    raise ValueError("Training dataset is empty.")


if validation_df.empty:
    raise ValueError("Validation dataset is empty.")


if test_df.empty:
    raise ValueError("Test dataset is empty.")


print("\n" + "=" * 70)
print("TIME-BASED SPLIT")
print("=" * 70)

print(
    f"TRAIN      : {len(train_df)} rows "
    f"(2020 → 2021, 2021 → 2022)"
)

print(
    f"VALIDATION : {len(validation_df)} rows "
    f"(2022 → 2023)"
)

print(
    f"TEST       : {len(test_df)} rows "
    f"(2023 → 2024)"
)


# ============================================================
# 9. FEATURE PREPARATION
# ============================================================

print("\n" + "=" * 70)
print("FEATURE PREPARATION")
print("=" * 70)

print(
    f"Initial candidate features: "
    f"{len(candidate_features)}"
)


# ============================================================
# 10. REMOVE FEATURES WITH ZERO TRAINING OBSERVATIONS
# ============================================================

all_null_training_features = []

for col in candidate_features:

    if train_df[col].notna().sum() == 0:

        all_null_training_features.append(col)


if all_null_training_features:

    print(
        "\nFeatures removed because they contain "
        "ZERO observed training values:"
    )

    for col in all_null_training_features:

        print(
            f"  - {col}"
        )


candidate_features = [
    col
    for col in candidate_features
    if col not in all_null_training_features
]


print(
    f"\nFinal candidate features: "
    f"{len(candidate_features)}"
)


# ============================================================
# 11. FINAL FEATURE LEAKAGE CHECK
# ============================================================

remaining_forbidden = [
    col
    for col in candidate_features
    if col in FORBIDDEN_FEATURES
]


if remaining_forbidden:

    raise ValueError(
        "FINAL FEATURE SET CONTAINS FORBIDDEN "
        f"COLUMNS: {remaining_forbidden}"
    )


print(
    "✅ Final feature leakage check passed."
)


# ============================================================
# 12. BUILD TRAIN / VALIDATION / TEST MATRICES
# ============================================================

X_train = train_df[
    candidate_features
].copy()

y_train = train_df[
    TARGET
].copy()


X_val = validation_df[
    candidate_features
].copy()

y_val = validation_df[
    TARGET
].copy()


X_test = test_df[
    candidate_features
].copy()

y_test = test_df[
    TARGET
].copy()


# ============================================================
# 13. HANDLE INFINITE VALUES
# ============================================================

for data in [
    X_train,
    X_val,
    X_test
]:

    numeric_cols = data.select_dtypes(
        include=["number"]
    ).columns

    data[numeric_cols] = (
        data[numeric_cols]
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
    )


# ============================================================
# 14. IDENTIFY FEATURE TYPES
# ============================================================

numeric_features = (
    X_train
    .select_dtypes(
        include=["number"]
    )
    .columns
    .tolist()
)


categorical_features = (
    X_train
    .select_dtypes(
        include=["object", "category"]
    )
    .columns
    .tolist()
)


print("\nNumeric features    :", len(numeric_features))
print("Categorical features:", len(categorical_features))


# ============================================================
# 15. DISPLAY FINAL FEATURES
# ============================================================

print("\n" + "=" * 70)
print("FINAL FEATURES USED BY MODEL")
print("=" * 70)

for i, feature in enumerate(
    candidate_features,
    start=1
):

    print(
        f"{i:02d}. {feature}"
    )


# ============================================================
# 16. PREPROCESSING
# ============================================================

numeric_pipeline = Pipeline(
    steps=[

        (
            "imputer",
            SimpleImputer(
                strategy="median"
            )
        ),

        (
            "scaler",
            StandardScaler()
        )
    ]
)


categorical_pipeline = Pipeline(
    steps=[

        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),

        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)


preprocessor = ColumnTransformer(
    transformers=[

        (
            "numeric",
            numeric_pipeline,
            numeric_features
        ),

        (
            "categorical",
            categorical_pipeline,
            categorical_features
        )
    ]
)


# ============================================================
# 17. DEFINE MODELS
# ============================================================

models = {

    "linear_regression":
        LinearRegression(),

    "random_forest":
        RandomForestRegressor(
            n_estimators=500,
            random_state=42,
            n_jobs=-1,
            max_features="sqrt"
        ),

    "gradient_boosting":
        GradientBoostingRegressor(
            n_estimators=300,
            learning_rate=0.03,
            max_depth=3,
            random_state=42,
            loss="huber"
        )
}


# ============================================================
# 18. MODEL SELECTION
# ============================================================

print("\n" + "=" * 70)
print("MODEL SELECTION")
print("=" * 70)

print(
    "Training: 2020–2021"
)

print(
    "Validation: 2022"
)

print(
    "Selection criterion: Lowest validation MAE"
)


validation_results = []

trained_validation_models = {}


for model_name, model in models.items():

    print("\n" + "-" * 70)

    print(
        f"TRAINING MODEL: {model_name}"
    )

    print("-" * 70)


    # --------------------------------------------------------
    # CREATE FRESH PREPROCESSOR
    # --------------------------------------------------------

    model_preprocessor = ColumnTransformer(
        transformers=[

            (
                "numeric",
                Pipeline(
                    steps=[

                        (
                            "imputer",
                            SimpleImputer(
                                strategy="median"
                            )
                        ),

                        (
                            "scaler",
                            StandardScaler()
                        )
                    ]
                ),
                numeric_features
            ),

            (
                "categorical",
                Pipeline(
                    steps=[

                        (
                            "imputer",
                            SimpleImputer(
                                strategy="most_frequent"
                            )
                        ),

                        (
                            "encoder",
                            OneHotEncoder(
                                handle_unknown="ignore"
                            )
                        )
                    ]
                ),
                categorical_features
            )
        ]
    )


    pipeline = Pipeline(
        steps=[

            (
                "preprocessor",
                model_preprocessor
            ),

            (
                "model",
                model
            )
        ]
    )


    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    pipeline.fit(
        X_train,
        y_train
    )


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    val_predictions = pipeline.predict(
        X_val
    )


    val_mae = mean_absolute_error(
        y_val,
        val_predictions
    )


    val_rmse = np.sqrt(
        mean_squared_error(
            y_val,
            val_predictions
        )
    )


    val_r2 = r2_score(
        y_val,
        val_predictions
    )


    print(
        f"Validation MAE  : "
        f"{val_mae:,.2f}"
    )

    print(
        f"Validation RMSE : "
        f"{val_rmse:,.2f}"
    )

    print(
        f"Validation R²   : "
        f"{val_r2:.4f}"
    )


    validation_results.append({

        "model":
            model_name,

        "validation_MAE":
            val_mae,

        "validation_RMSE":
            val_rmse,

        "validation_R2":
            val_r2
    })


    trained_validation_models[
        model_name
    ] = pipeline


# ============================================================
# 19. COMPARE MODELS
# ============================================================

validation_results_df = pd.DataFrame(
    validation_results
)


validation_results_df = (
    validation_results_df
    .sort_values(
        by="validation_MAE",
        ascending=True
    )
    .reset_index(drop=True)
)


print("\n" + "=" * 70)
print("VALIDATION MODEL COMPARISON")
print("=" * 70)

print(
    validation_results_df
    .to_string(index=False)
)


# ============================================================
# 20. SELECT BEST MODEL
# ============================================================

best_model_name = (
    validation_results_df
    .iloc[0]["model"]
)


print("\n" + "=" * 70)
print("SELECTED MODEL")
print("=" * 70)

print(
    f"Best model: {best_model_name}"
)

print(
    "Selection criterion: "
    "Lowest validation MAE"
)


# ============================================================
# 21. FINAL TRAINING DATA
# ============================================================

#
# IMPORTANT:
#
# Validation was used only for selecting
# the best model.
#
# After selection, the selected model
# is retrained using:
#
# 2020 → 2021
# 2021 → 2022
# 2022 → 2023
#
# The 2023 → 2024 test set remains
# completely untouched.
#

final_train_df = df[
    df["feature_year"].isin(
        [2020, 2021, 2022]
    )
].copy()


X_final_train = final_train_df[
    candidate_features
].copy()


y_final_train = final_train_df[
    TARGET
].copy()


print("\n" + "=" * 70)
print("FINAL MODEL TRAINING")
print("=" * 70)

print(
    f"Final training rows: "
    f"{len(final_train_df)}"
)

print(
    "Training periods: "
    "2020 → 2021, "
    "2021 → 2022, "
    "2022 → 2023"
)


# ============================================================
# 22. CREATE FINAL MODEL
# ============================================================

selected_model = models[
    best_model_name
]


final_preprocessor = ColumnTransformer(
    transformers=[

        (
            "numeric",

            Pipeline(
                steps=[

                    (
                        "imputer",
                        SimpleImputer(
                            strategy="median"
                        )
                    ),

                    (
                        "scaler",
                        StandardScaler()
                    )
                ]
            ),

            numeric_features
        ),

        (
            "categorical",

            Pipeline(
                steps=[

                    (
                        "imputer",
                        SimpleImputer(
                            strategy="most_frequent"
                        )
                    ),

                    (
                        "encoder",
                        OneHotEncoder(
                            handle_unknown="ignore"
                        )
                    )
                ]
            ),

            categorical_features
        )
    ]
)


final_pipeline = Pipeline(
    steps=[

        (
            "preprocessor",
            final_preprocessor
        ),

        (
            "model",
            selected_model
        )
    ]
)


# ============================================================
# 23. FIT FINAL MODEL
# ============================================================

final_pipeline.fit(
    X_final_train,
    y_final_train
)


print(
    "✅ Final model trained."
)


# ============================================================
# 24. FINAL TEST — 2023 → 2024
# ============================================================

print("\n" + "=" * 70)
print("FINAL TEST — 2023 → 2024")
print("=" * 70)

test_predictions = (
    final_pipeline
    .predict(X_test)
)


test_mae = mean_absolute_error(
    y_test,
    test_predictions
)


test_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        test_predictions
    )
)


test_r2 = r2_score(
    y_test,
    test_predictions
)


print(
    f"Test MAE  : "
    f"{test_mae:,.2f}"
)

print(
    f"Test RMSE : "
    f"{test_rmse:,.2f}"
)

print(
    f"Test R²   : "
    f"{test_r2:.4f}"
)


# ============================================================
# 25. ARTIFACT DIRECTORY
# ============================================================

ARTIFACT_DIR = (
    BACKEND_DIR
    / "app"
    / "ml"
    / "artifacts"
)

ARTIFACT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 26. SAVE FINAL MODEL
# ============================================================

model_path = (
    ARTIFACT_DIR
    / "best_GenSaveLoss_model.joblib"
)


joblib.dump(
    final_pipeline,
    model_path
)


print("\nFinal production model saved:")
print(model_path)


# ============================================================
# 27. SAVE VALIDATION RESULTS
# ============================================================

validation_results_path = (
    ARTIFACT_DIR
    / "model_validation_results.csv"
)


validation_results_df.to_csv(
    validation_results_path,
    index=False
)


print(
    "\nValidation results saved:"
)

print(
    validation_results_path
)


# ============================================================
# 28. SAVE FINAL TEST PREDICTIONS
# ============================================================

test_output = test_df[
    [
        "ACO_ID",
        "feature_year",
        "target_year",
        TARGET
    ]
].copy()


test_output[
    "predicted_GenSaveLoss"
] = test_predictions


test_output[
    "absolute_error"
] = (
    test_output[TARGET]
    -
    test_output[
        "predicted_GenSaveLoss"
    ]
).abs()


test_output[
    "absolute_percentage_error"
] = np.where(

    test_output[TARGET].abs() > 0,

    (
        test_output[
            "absolute_error"
        ]
        /
        test_output[TARGET].abs()
    ) * 100,

    np.nan
)


prediction_path = (
    ARTIFACT_DIR
    / "test_predictions_2023_2024.csv"
)


test_output.to_csv(
    prediction_path,
    index=False
)


print(
    "\nTest predictions saved:"
)

print(
    prediction_path
)


# ============================================================
# 29. SAVE FEATURE LIST
# ============================================================

feature_output = pd.DataFrame({

    "feature_name":
        candidate_features,

    "feature_type": [

        (
            "numeric"
            if feature in numeric_features
            else "categorical"
        )

        for feature in candidate_features
    ]
})


feature_path = (
    ARTIFACT_DIR
    / "model_features.csv"
)


feature_output.to_csv(
    feature_path,
    index=False
)


print(
    "\nFeature list saved:"
)

print(
    feature_path
)


# ============================================================
# 30. SAVE FINAL TEST METRICS
# ============================================================

final_test_metrics = pd.DataFrame([{

    "best_model":
        best_model_name,

    "validation_period":
        "2022_to_2023",

    "test_period":
        "2023_to_2024",

    "training_periods":
        "2020_to_2023",

    "training_rows":
        len(final_train_df),

    "validation_rows":
        len(validation_df),

    "test_rows":
        len(test_df),

    "MAE":
        test_mae,

    "RMSE":
        test_rmse,

    "R2":
        test_r2
}])


test_metrics_path = (
    ARTIFACT_DIR
    / "final_test_metrics.csv"
)


final_test_metrics.to_csv(
    test_metrics_path,
    index=False
)


print(
    "\nFinal test metrics saved:"
)

print(
    test_metrics_path
)


# ============================================================
# 31. SAVE MODEL METADATA
# ============================================================

metadata = {

    "target":
        TARGET,

    "selected_model":
        best_model_name,

    "validation_period":
        "2022_to_2023",

    "test_period":
        "2023_to_2024",

    "final_training_periods":
        [
            "2020_to_2021",
            "2021_to_2022",
            "2022_to_2023"
        ],

    "number_of_features":
        len(candidate_features),

    "training_rows":
        len(final_train_df),

    "validation_rows":
        len(validation_df),

    "test_rows":
        len(test_df),

    "test_MAE":
        float(test_mae),

    "test_RMSE":
        float(test_rmse),

    "test_R2":
        float(test_r2),

    "leakage_check":
        "PASSED",

    "temporal_validation":
        "PASSED"
}


metadata_path = (
    ARTIFACT_DIR
    / "model_metadata.joblib"
)


joblib.dump(
    metadata,
    metadata_path
)


print(
    "\nModel metadata saved:"
)

print(
    metadata_path
)


# ============================================================
# 32. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("TRAINING COMPLETED SUCCESSFULLY")
print("=" * 70)

print(
    f"Dataset rows        : "
    f"{len(df)}"
)

print(
    f"Final features      : "
    f"{len(candidate_features)}"
)

print(
    f"Model selection     : "
    f"2020–2021 → 2022"
)

print(
    f"Final training      : "
    f"2020–2022"
)

print(
    f"Final test          : "
    f"2023 → 2024"
)

print(
    f"Best model          : "
    f"{best_model_name}"
)

print(
    f"Test MAE            : "
    f"{test_mae:,.2f}"
)

print(
    f"Test RMSE           : "
    f"{test_rmse:,.2f}"
)

print(
    f"Test R²             : "
    f"{test_r2:.4f}"
)

print(
    "\nLeakage status      : PASSED"
)

print(
    "Temporal validation : PASSED"
)

print("=" * 70)