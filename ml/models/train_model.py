import os
import json
import numpy as np
import pandas as pd

from dotenv import load_dotenv
from supabase import create_client

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import KFold, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# 1. SUPABASE CONNECTION
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY missing in .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Connected to Supabase")


# ============================================================
# 2. FETCH DATA
# ============================================================

required_columns = [
    "ACO_ID",
    "ACO_Name",
    "performance_year",
    "Sav_rate",

    "EarnSaveLoss",
    "ABtotExp",
    "ABtotBnchmk",
    "FinalShareRate",
    "QualScore",
    "Met_QPS",

    "N_AB",
    "ADM",
    "P_EDV_Vis",
    "P_CT_VIS",
    "P_MRI_VIS",
    "P_EM_Total",
    "P_SNF_ADM",

    "N_Hosp",
    "N_PCP",
    "N_Spec",

    "ACO_State",
    "Agree_Type",
    "Risk_Model",
    "Assign_Type",
    "Current_Track"
]


def fetch_all_rows():
    rows = []
    start = 0
    batch_size = 1000

    while True:

        response = (
            supabase
            .table("fact_aco_performance")
            .select("*")
            .range(start, start + batch_size - 1)
            .execute()
        )

        batch = response.data

        if not batch:
            break

        rows.extend(batch)

        print(f"Fetched rows: {len(rows)}")

        if len(batch) < batch_size:
            break

        start += batch_size

    return pd.DataFrame(rows)


df = fetch_all_rows()

print()
print("================================")
print("DATASET")
print("================================")

print("Total rows:", len(df))
print("Total columns:", len(df.columns))


# ============================================================
# 3. KEEP REQUIRED COLUMNS
# ============================================================

available_columns = [
    col for col in required_columns
    if col in df.columns
]

df = df[available_columns].copy()


# ============================================================
# 4. YEAR FILTER
# ============================================================

df["performance_year"] = pd.to_numeric(
    df["performance_year"],
    errors="coerce"
)

df = df[
    df["performance_year"].isin([2022, 2023, 2024])
].copy()

print()
print("================================")
print("YEAR FILTER")
print("================================")

print(
    df["performance_year"]
    .value_counts()
    .sort_index()
)


# ============================================================
# 5. SAVINGS RATE CHECK
# ============================================================

print()
print("================================")
print("SAVINGS RATE CHECK")
print("================================")

for year in [2022, 2023, 2024]:

    year_df = df[df["performance_year"] == year]

    available = year_df["Sav_rate"].notna().sum()

    total = len(year_df)

    print(
        f"{year}: {available}/{total} Sav_rate available"
    )


# ============================================================
# 6. CONVERT NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    "Sav_rate",
    "EarnSaveLoss",
    "ABtotExp",
    "ABtotBnchmk",
    "FinalShareRate",
    "QualScore",
    "Met_QPS",
    "N_AB",
    "ADM",
    "P_EDV_Vis",
    "P_CT_VIS",
    "P_MRI_VIS",
    "P_EM_Total",
    "P_SNF_ADM",
    "N_Hosp",
    "N_PCP",
    "N_Spec"
]

for col in numeric_columns:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# ============================================================
# 7. REMOVE ROWS WITHOUT TARGET
# ============================================================

df = df.dropna(
    subset=["Sav_rate"]
).copy()


# ============================================================
# 8. DUPLICATE CHECK
# ============================================================

print()
print("================================")
print("DUPLICATE CHECK")
print("================================")

duplicates = df.duplicated(
    subset=["ACO_ID", "performance_year"]
).sum()

print(
    "Duplicate ACO + performance_year rows:",
    duplicates
)

df = df.drop_duplicates(
    subset=["ACO_ID", "performance_year"],
    keep="first"
).copy()

print(
    "Rows after duplicate removal:",
    len(df)
)


# ============================================================
# 9. SORT DATA
# ============================================================

df = df.sort_values(
    ["ACO_ID", "performance_year"]
).reset_index(drop=True)


# ============================================================
# 10. CREATE LAG FEATURES
# ============================================================

print()
print("================================")
print("CREATING LAG FEATURES")
print("================================")


lag_columns = [
    "Sav_rate",
    "EarnSaveLoss",
    "ABtotExp",
    "ABtotBnchmk",
    "FinalShareRate",
    "QualScore",
    "Met_QPS",
    "N_AB",
    "ADM",
    "P_EDV_Vis",
    "P_CT_VIS",
    "P_MRI_VIS",
    "P_EM_Total",
    "P_SNF_ADM",
    "N_Hosp",
    "N_PCP",
    "N_Spec"
]


for col in lag_columns:

    df[f"{col}_Lag1"] = (
        df.groupby("ACO_ID")[col]
        .shift(1)
    )


# ============================================================
# 11. CREATE SAFE YEAR-OVER-YEAR CHANGE FEATURES
# ============================================================

print("Creating year-over-year change features...")


change_columns = [
    "EarnSaveLoss",
    "ABtotExp",
    "ABtotBnchmk",
    "FinalShareRate",
    "QualScore",
    "Met_QPS",
    "N_AB",
    "ADM",
    "P_EDV_Vis",
    "P_CT_VIS",
    "P_MRI_VIS",
    "P_EM_Total",
    "P_SNF_ADM",
    "N_Hosp",
    "N_PCP",
    "N_Spec"
]


for col in change_columns:

    lag_col = f"{col}_Lag1"

    # Absolute change
    df[f"{col}_Change"] = (
        df[col] - df[lag_col]
    )

    # Percentage change
    denominator = df[lag_col].abs()

    df[f"{col}_PctChange"] = np.where(
        denominator > 1e-9,
        (df[col] - df[lag_col]) / denominator,
        np.nan
    )


# ============================================================
# 12. CHECK LAG DATA
# ============================================================

print()
print("================================")
print("LAG DATA CHECK")
print("================================")

for year in [2023, 2024]:

    year_df = df[
        df["performance_year"] == year
    ]

    valid_lag = year_df[
        year_df["Sav_rate_Lag1"].notna()
    ]

    print(
        f"{year}: {len(year_df)} rows, "
        f"{len(valid_lag)} have previous-year Savings Rate"
    )


# ============================================================
# 13. IMPORTANT:
#    USE ONLY INFORMATION AVAILABLE BEFORE TARGET YEAR
# ============================================================

# We will NOT use current-year variables such as:
#
# 2024 Sav_rate
# 2024 EarnSaveLoss
# 2024 ABtotExp
#
# as predictors for 2024.
#
# Instead, prediction for 2024 uses:
#
# 2023 values
# 2023 -> historical changes
# previous-year values
#
# This prevents future-information leakage.


# ============================================================
# 14. CREATE TRAINING DATA
# ============================================================

train_df = df[
    df["performance_year"] == 2023
].copy()

test_df = df[
    df["performance_year"] == 2024
].copy()


# Need previous year Savings Rate
train_df = train_df[
    train_df["Sav_rate_Lag1"].notna()
].copy()

test_df = test_df[
    test_df["Sav_rate_Lag1"].notna()
].copy()


print()
print("================================")
print("TRAIN / TEST")
print("================================")

print(
    "Training rows:",
    len(train_df)
)

print(
    "2024 prediction rows:",
    len(test_df)
)

print(
    "Training ACOs:",
    train_df["ACO_ID"].nunique()
)

print(
    "2024 prediction ACOs:",
    test_df["ACO_ID"].nunique()
)


# ============================================================
# 15. FEATURE DESIGN
# ============================================================

# IMPORTANT:
#
# For forecasting 2024:
#
# We use 2023 information + 2022 information.
#
# We DO NOT use 2024 predictors.
#
# This makes the forecasting setup more realistic.


base_numeric_features = [
    "EarnSaveLoss",
    "ABtotExp",
    "ABtotBnchmk",
    "FinalShareRate",
    "QualScore",
    "Met_QPS",
    "N_AB",
    "ADM",
    "P_EDV_Vis",
    "P_CT_VIS",
    "P_MRI_VIS",
    "P_EM_Total",
    "P_SNF_ADM",
    "N_Hosp",
    "N_PCP",
    "N_Spec"
]


lag_numeric_features = [
    f"{col}_Lag1"
    for col in [
        "Sav_rate",
        "EarnSaveLoss",
        "ABtotExp",
        "ABtotBnchmk",
        "FinalShareRate",
        "QualScore",
        "Met_QPS",
        "N_AB",
        "ADM",
        "P_EDV_Vis",
        "P_CT_VIS",
        "P_MRI_VIS",
        "P_EM_Total",
        "P_SNF_ADM",
        "N_Hosp",
        "N_PCP",
        "N_Spec"
    ]
]


change_numeric_features = [
    f"{col}_Change"
    for col in change_columns
]


pct_change_features = [
    f"{col}_PctChange"
    for col in change_columns
]


numeric_features = (
    base_numeric_features
    + lag_numeric_features
    + change_numeric_features
    + pct_change_features
)


categorical_features = [
    "Agree_Type",
    "Risk_Model",
    "Assign_Type",
    "Current_Track"
]


# Remove columns that do not exist
numeric_features = [
    col for col in numeric_features
    if col in train_df.columns
]

categorical_features = [
    col for col in categorical_features
    if col in train_df.columns
]


# Remove categorical columns that contain no useful training data
valid_categorical = []

for col in categorical_features:

    if train_df[col].notna().sum() == 0:

        print(
            f"Skipping categorical feature "
            f"with no training values: {col}"
        )

    else:

        valid_categorical.append(col)

categorical_features = valid_categorical


feature_columns = (
    numeric_features
    + categorical_features
)


print()
print("================================")
print("FEATURES")
print("================================")

print(
    "Numeric features:",
    len(numeric_features)
)

print(
    "Categorical features:",
    len(categorical_features)
)

print(
    "Total features:",
    len(feature_columns)
)


# ============================================================
# 16. X AND Y
# ============================================================

X_train = train_df[
    feature_columns
].copy()

y_train = train_df[
    "Sav_rate"
].copy()

X_2024 = test_df[
    feature_columns
].copy()

y_2024 = test_df[
    "Sav_rate"
].copy()


# ============================================================
# 17. PREPROCESSING
# ============================================================

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            )
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
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)


preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            numeric_pipeline,
            numeric_features
        ),
        (
            "cat",
            categorical_pipeline,
            categorical_features
        )
    ]
)


# ============================================================
# 18. BASE MODEL
# ============================================================

base_model = GradientBoostingRegressor(
    random_state=42
)


pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            base_model
        )
    ]
)


# ============================================================
# 19. HYPERPARAMETER TUNING
# ============================================================

print()
print("================================")
print("HYPERPARAMETER TUNING")
print("================================")

print(
    "Testing multiple Gradient Boosting configurations..."
)


param_grid = {

    "model__n_estimators": [
        100,
        150,
        200,
        250,
        300
    ],

    "model__learning_rate": [
        0.01,
        0.02,
        0.03,
        0.05
    ],

    "model__max_depth": [
        2,
        3
    ],

    "model__min_samples_leaf": [
        5,
        10,
        15
    ],

    "model__subsample": [
        0.8,
        0.9,
        1.0
    ],

    "model__loss": [
        "huber",
        "squared_error"
    ]
}


# ============================================================
# 20. CROSS VALIDATION
# ============================================================

cv = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


grid_search = GridSearchCV(
    estimator=pipeline,
    param_grid=param_grid,
    scoring="r2",
    cv=cv,
    n_jobs=-1,
    verbose=1
)


grid_search.fit(
    X_train,
    y_train
)


best_model = grid_search.best_estimator_


print()
print("================================")
print("BEST MODEL")
print("================================")

print(
    "Best CV R²:",
    round(
        grid_search.best_score_,
        4
    )
)

print(
    "Best parameters:"
)

for key, value in grid_search.best_params_.items():

    print(
        f"{key}: {value}"
    )


# ============================================================
# 21. PROPER 2023 CROSS-VALIDATION PERFORMANCE
# ============================================================

print()
print("================================")
print("2023 CROSS-VALIDATION")
print("================================")

cv_predictions = np.zeros(
    len(X_train)
)


for train_index, val_index in cv.split(
    X_train
):

    X_tr = X_train.iloc[
        train_index
    ]

    X_val = X_train.iloc[
        val_index
    ]

    y_tr = y_train.iloc[
        train_index
    ]

    fold_model = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                GradientBoostingRegressor(
                    random_state=42,
                    **{
                        k.replace(
                            "model__",
                            ""
                        ): v
                        for k, v
                        in grid_search.best_params_.items()
                    }
                )
            )
        ]
    )

    fold_model.fit(
        X_tr,
        y_tr
    )

    cv_predictions[val_index] = (
        fold_model.predict(X_val)
    )


cv_mae = mean_absolute_error(
    y_train,
    cv_predictions
)

cv_rmse = np.sqrt(
    mean_squared_error(
        y_train,
        cv_predictions
    )
)

cv_r2 = r2_score(
    y_train,
    cv_predictions
)


print(
    f"MAE: {cv_mae:.4f}"
)

print(
    f"RMSE: {cv_rmse:.4f}"
)

print(
    f"R²: {cv_r2:.4f}"
)


# ============================================================
# 22. TRAIN FINAL MODEL ON ALL 2023 DATA
# ============================================================

print()
print("================================")
print("FINAL MODEL TRAINING")
print("================================")

best_model.fit(
    X_train,
    y_train
)

print(
    "Training completed"
)


# ============================================================
# 23. PREDICT 2024
# ============================================================

predicted_2024 = best_model.predict(
    X_2024
)


# ============================================================
# 24. 2024 METRICS
# ============================================================

mae = mean_absolute_error(
    y_2024,
    predicted_2024
)

rmse = np.sqrt(
    mean_squared_error(
        y_2024,
        predicted_2024
    )
)

r2 = r2_score(
    y_2024,
    predicted_2024
)


print()
print("================================")
print("2024 FINAL PREDICTION")
print("================================")

print(
    f"MAE: {mae:.4f}"
)

print(
    f"RMSE: {rmse:.4f}"
)

print(
    f"R²: {r2:.4f}"
)


# ============================================================
# 25. ACCURACY PERCENTAGE
# ============================================================

actual_change = (
    y_2024.values
    - test_df["Sav_rate_Lag1"].values
)

predicted_change = (
    predicted_2024
    - test_df["Sav_rate_Lag1"].values
)


threshold = 0.25


actual_trend = np.where(
    actual_change > threshold,
    "Positive",
    np.where(
        actual_change < -threshold,
        "Negative",
        "Stable"
    )
)


predicted_trend = np.where(
    predicted_change > threshold,
    "Positive",
    np.where(
        predicted_change < -threshold,
        "Negative",
        "Stable"
    )
)


accuracy_percentage = (
    np.mean(
        actual_trend == predicted_trend
    ) * 100
)


print()
print("================================")
print("ACCURACY PERCENTAGE")
print("================================")

print(
    f"Accuracy Percentage: "
    f"{accuracy_percentage:.2f}%"
)


# ============================================================
# 26. CREATE PREDICTION DATAFRAME
# ============================================================

prediction_df = pd.DataFrame({

    "ACO_ID":
        test_df["ACO_ID"].values,

    "ACO_Name":
        test_df["ACO_Name"].values,

    "Actual_2023_Sav_rate":
        test_df["Sav_rate_Lag1"].values,

    "Predicted_2024_Sav_rate":
        predicted_2024,

    "Actual_2024_Sav_rate":
        y_2024.values,

    "Predicted_Change_pp":
        predicted_change,

    "Actual_Change_pp":
        actual_change,

    "Predicted_Trend":
        predicted_trend,

    "Actual_Trend":
        actual_trend
})


# ============================================================
# 27. FORECAST QUALITY
# ============================================================

prediction_df["Absolute_Error"] = (
    prediction_df[
        "Predicted_2024_Sav_rate"
    ]
    -
    prediction_df[
        "Actual_2024_Sav_rate"
    ]
).abs()


def forecast_quality(error):

    if error <= 1:
        return "Excellent"

    elif error <= 2:
        return "Good"

    elif error <= 4:
        return "Moderate"

    else:
        return "Poor"


prediction_df[
    "Forecast_Quality"
] = prediction_df[
    "Absolute_Error"
].apply(
    forecast_quality
)


# ============================================================
# 28. SAVE PREDICTIONS
# ============================================================

prediction_file = (
    "aco_savings_rate_2024_predictions.csv"
)

prediction_df.to_csv(
    prediction_file,
    index=False
)


print()
print(
    "Prediction file saved:"
)

print(
    prediction_file
)


# ============================================================
# 29. SAVE MODEL METRICS
# ============================================================

metrics_df = pd.DataFrame({

    "Metric": [
        "CV MAE",
        "CV RMSE",
        "CV R2",
        "2024 MAE",
        "2024 RMSE",
        "2024 R2",
        "Accuracy Percentage"
    ],

    "Value": [
        cv_mae,
        cv_rmse,
        cv_r2,
        mae,
        rmse,
        r2,
        accuracy_percentage
    ]
})


metrics_file = "model_metrics.csv"

metrics_df.to_csv(
    metrics_file,
    index=False
)


# ============================================================
# 30. SAVE MODEL INFORMATION
# ============================================================

model_info = {

    "model":
        "Gradient Boosting Regressor",

    "training_period":
        "2022 -> 2023",

    "prediction_period":
        "2023 -> 2024",

    "training_rows":
        int(len(X_train)),

    "prediction_rows":
        int(len(X_2024)),

    "numeric_features":
        int(len(numeric_features)),

    "categorical_features":
        int(len(categorical_features)),

    "total_features":
        int(len(feature_columns)),

    "cv_r2":
        float(cv_r2),

    "cv_mae":
        float(cv_mae),

    "cv_rmse":
        float(cv_rmse),

    "2024_r2":
        float(r2),

    "2024_mae":
        float(mae),

    "2024_rmse":
        float(rmse),

    "accuracy_percentage":
        float(accuracy_percentage),

    "best_parameters":
        {
            key: value
            for key, value
            in grid_search.best_params_.items()
        },

    "target":
        "Sav_rate",

    "trend_threshold":
        threshold
}


with open(
    "model_info.json",
    "w"
) as f:

    json.dump(
        model_info,
        f,
        indent=4,
        default=str
    )


# ============================================================
# 31. FINAL RESULTS
# ============================================================

print()
print("================================")
print("FINAL MODEL RESULTS")
print("================================")

print(
    f"CV MAE: {cv_mae:.4f}"
)

print(
    f"CV RMSE: {cv_rmse:.4f}"
)

print(
    f"CV R²: {cv_r2:.4f}"
)

print(
    f"2024 MAE: {mae:.4f}"
)

print(
    f"2024 RMSE: {rmse:.4f}"
)

print(
    f"2024 R²: {r2:.4f}"
)

print(
    f"Accuracy Percentage: "
    f"{accuracy_percentage:.2f}%"
)


# ============================================================
# 32. TREND DISTRIBUTION
# ============================================================

print()
print("================================")
print("PREDICTED TREND DISTRIBUTION")
print("================================")

print(
    prediction_df[
        "Predicted_Trend"
    ].value_counts()
)


# ============================================================
# 33. TOP EXPECTED IMPROVEMENTS
# ============================================================

print()
print("================================")
print("TOP EXPECTED IMPROVEMENTS")
print("================================")

print(
    prediction_df[
        [
            "ACO_ID",
            "ACO_Name",
            "Actual_2023_Sav_rate",
            "Predicted_2024_Sav_rate",
            "Predicted_Change_pp"
        ]
    ]
    .sort_values(
        "Predicted_Change_pp",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 34. TOP EXPECTED DECLINES
# ============================================================

print()
print("================================")
print("TOP EXPECTED DECLINES")
print("================================")

print(
    prediction_df[
        [
            "ACO_ID",
            "ACO_Name",
            "Actual_2023_Sav_rate",
            "Predicted_2024_Sav_rate",
            "Predicted_Change_pp"
        ]
    ]
    .sort_values(
        "Predicted_Change_pp",
        ascending=True
    )
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 35. SAMPLE PREDICTIONS
# ============================================================

print()
print("================================")
print("SAMPLE PREDICTIONS")
print("================================")

print(
    prediction_df[
        [
            "ACO_ID",
            "ACO_Name",
            "Actual_2023_Sav_rate",
            "Predicted_2024_Sav_rate",
            "Actual_2024_Sav_rate",
            "Predicted_Trend",
            "Actual_Trend"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 36. COMPLETED
# ============================================================

print()
print("================================")
print("PROCESS COMPLETED")
print("================================")