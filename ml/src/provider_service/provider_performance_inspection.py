"""
PROVIDER PERFORMANCE FEATURE INSPECTION - STAGE 4
=================================================

Purpose:
    Inspect Stage 4 provider performance features before creating
    composite provider performance scores.

This script DOES NOT:
    - modify the database
    - modify Stage 4 data
    - remove rows
    - create final performance scores

It only performs diagnostic inspection.
"""

import os
import numpy as np
import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

INPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "provider_service",
    "provider_features_stage4.csv"
)


# ============================================================
# DISPLAY SETTINGS
# ============================================================

pd.set_option("display.max_columns", 200)
pd.set_option("display.width", 200)
pd.set_option("display.max_rows", 200)


# ============================================================
# HELPER
# ============================================================

def section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# START
# ============================================================

print("=" * 70)
print("PROVIDER PERFORMANCE FEATURE INSPECTION - STAGE 4")
print("=" * 70)

print("\nLoading Stage 4 dataset...")

if not os.path.exists(INPUT_PATH):
    raise FileNotFoundError(
        f"\nStage 4 dataset not found:\n{INPUT_PATH}"
    )

df = pd.read_csv(
    INPUT_PATH,
    low_memory=False
)

print(f"Rows loaded: {len(df):,}")
print(f"Columns loaded: {len(df.columns):,}")


# ============================================================
# BASIC VALIDATION
# ============================================================

section("1. BASIC DATASET VALIDATION")

required_columns = [
    "Rndrng_NPI",
    "Year",
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_Mdcr_Pymt_Amt",
    "Tot_Mdcr_Alowd_Amt",
    "payment_efficiency",
    "service_intensity_per_beneficiary",
    "risk_adjusted_services",
    "risk_adjusted_payment",
    "condition_adjusted_payment",
    "average_risk_score",
    "overall_condition_burden",
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    print("Required columns: FAILED")
    print("Missing columns:")
    for col in missing:
        print(f"- {col}")
    raise ValueError("Required Stage 4 columns are missing.")
else:
    print("Required columns: PASSED")


# ============================================================
# GRAIN VALIDATION
# ============================================================

duplicate_npi_year = df.duplicated(
    subset=["Rndrng_NPI", "Year"]
).sum()

print(f"Duplicate NPI-Year rows: {duplicate_npi_year:,}")

if duplicate_npi_year == 0:
    print("NPI + Year grain: PASSED")
else:
    print("NPI + Year grain: FAILED")


# ============================================================
# NUMERIC PERFORMANCE FEATURES
# ============================================================

performance_features = [
    "service_intensity_per_beneficiary",
    "hcpcs_intensity_per_beneficiary",
    "services_per_condition_burden",
    "services_per_risk_score",

    "payment_efficiency",
    "standardized_payment_ratio",
    "payment_to_charge_ratio",
    "allowed_to_charge_ratio",
    "payment_vs_standardized_difference",
    "payment_vs_standardized_pct",

    "risk_adjusted_services",
    "risk_adjusted_payment",
    "risk_adjusted_allowed_amount",

    "condition_adjusted_payment",
    "condition_adjusted_services",

    "payment_per_risk_adjusted_beneficiary",
    "allowed_per_risk_adjusted_beneficiary",

    "medical_payment_per_service",
    "medical_allowed_per_service",
    "medical_payment_per_beneficiary",

    "drug_payment_per_service_stage4",
    "drug_allowed_per_service_stage4",
    "drug_payment_per_beneficiary_stage4",

    "medical_payment_share",
    "drug_payment_share",
    "medical_service_share_stage4",
    "drug_service_share_stage4",

    "performance_payment_trend",
    "performance_service_trend",
    "performance_beneficiary_trend",
    "performance_payment_per_service_trend",
    "performance_risk_trend",
]


available_features = [
    col for col in performance_features
    if col in df.columns
]

missing_features = [
    col for col in performance_features
    if col not in df.columns
]

section("2. PERFORMANCE FEATURE INVENTORY")

print(f"Expected performance features: {len(performance_features)}")
print(f"Available performance features: {len(available_features)}")

if missing_features:
    print("\nMissing performance features:")
    for col in missing_features:
        print(f"- {col}")

print("\nAvailable performance features:")
for col in available_features:
    print(f"- {col}")


# ============================================================
# NULL INSPECTION
# ============================================================

section("3. NULL VALUE INSPECTION")

null_summary = df[available_features].isna().sum()

null_summary = null_summary[
    null_summary > 0
].sort_values(ascending=False)

if len(null_summary) == 0:
    print("No null values found in performance features.")
else:
    print("Performance features containing null values:")
    for col, count in null_summary.items():
        percentage = (count / len(df)) * 100

        print(
            f"- {col}: "
            f"{count:,} rows "
            f"({percentage:.2f}%)"
        )


# ============================================================
# INFINITE VALUE INSPECTION
# ============================================================

section("4. INFINITE VALUE INSPECTION")

numeric_features = df[available_features].select_dtypes(
    include=[np.number]
).columns.tolist()

infinite_summary = {}

for col in numeric_features:
    count = np.isinf(
        df[col].to_numpy(dtype=float)
    ).sum()

    if count > 0:
        infinite_summary[col] = count

if not infinite_summary:
    print("Infinite values: 0")
    print("Infinite-value validation: PASSED")
else:
    print("Infinite values found:")
    for col, count in infinite_summary.items():
        print(f"- {col}: {count:,}")


# ============================================================
# DESCRIPTIVE STATISTICS
# ============================================================

section("5. PERFORMANCE FEATURE DISTRIBUTIONS")

stats = df[numeric_features].describe(
    percentiles=[
        0.01,
        0.05,
        0.25,
        0.50,
        0.75,
        0.95,
        0.99
    ]
).T

stats["missing"] = df[numeric_features].isna().sum()

print(
    stats[
        [
            "count",
            "missing",
            "mean",
            "std",
            "min",
            "1%",
            "5%",
            "25%",
            "50%",
            "75%",
            "95%",
            "99%",
            "max",
        ]
    ].round(4).to_string()
)


# ============================================================
# EXTREME VALUE DETECTION
# ============================================================

section("6. EXTREME VALUE / OUTLIER INSPECTION")

print(
    "Using the 1st and 99th percentiles as diagnostic boundaries."
)

outlier_results = []

for col in numeric_features:

    series = df[col].dropna()

    if len(series) == 0:
        continue

    q01 = series.quantile(0.01)
    q99 = series.quantile(0.99)

    below = (series < q01).sum()
    above = (series > q99).sum()

    outlier_results.append({
        "feature": col,
        "p01": q01,
        "p99": q99,
        "below_p01": below,
        "above_p99": above,
        "extreme_total": below + above,
    })

outlier_df = pd.DataFrame(outlier_results)

outlier_df = outlier_df.sort_values(
    "extreme_total",
    ascending=False
)

print(
    outlier_df.round(4).to_string(index=False)
)


# ============================================================
# SKEWNESS INSPECTION
# ============================================================

section("7. SKEWNESS INSPECTION")

skew_results = []

for col in numeric_features:

    skew_value = df[col].skew()

    skew_results.append({
        "feature": col,
        "skewness": skew_value
    })

skew_df = pd.DataFrame(skew_results)

skew_df["absolute_skewness"] = (
    skew_df["skewness"].abs()
)

skew_df = skew_df.sort_values(
    "absolute_skewness",
    ascending=False
)

print(
    skew_df[
        ["feature", "skewness"]
    ].round(4).to_string(index=False)
)


# ============================================================
# CORRELATION INSPECTION
# ============================================================

section("8. PERFORMANCE FEATURE CORRELATION")

correlation_matrix = df[numeric_features].corr()

correlation_pairs = []

for i in range(len(correlation_matrix.columns)):

    for j in range(i + 1, len(correlation_matrix.columns)):

        col1 = correlation_matrix.columns[i]
        col2 = correlation_matrix.columns[j]

        correlation = correlation_matrix.iloc[i, j]

        if pd.notna(correlation):
            correlation_pairs.append({
                "feature_1": col1,
                "feature_2": col2,
                "correlation": correlation,
                "absolute_correlation": abs(correlation),
            })

correlation_df = pd.DataFrame(
    correlation_pairs
)

correlation_df = correlation_df.sort_values(
    "absolute_correlation",
    ascending=False
)

print("\nTop 30 strongest relationships:")

print(
    correlation_df.head(30)[
        [
            "feature_1",
            "feature_2",
            "correlation"
        ]
    ].round(4).to_string(index=False)
)


# ============================================================
# HIGH CORRELATION PAIRS
# ============================================================

section("9. HIGH-CORRELATION FEATURE PAIRS")

high_corr = correlation_df[
    correlation_df["absolute_correlation"] >= 0.90
]

if len(high_corr) == 0:
    print("No feature pairs with correlation >= 0.90.")
else:
    print(
        f"Feature pairs with |correlation| >= 0.90: "
        f"{len(high_corr)}"
    )

    print(
        high_corr[
            [
                "feature_1",
                "feature_2",
                "correlation"
            ]
        ].round(4).to_string(index=False)
    )


# ============================================================
# TEMPORAL FEATURE COVERAGE
# ============================================================

section("10. TEMPORAL PERFORMANCE FEATURE COVERAGE")

temporal_features = [
    "performance_payment_trend",
    "performance_service_trend",
    "performance_beneficiary_trend",
    "performance_payment_per_service_trend",
    "performance_risk_trend",
]

for col in temporal_features:

    if col not in df.columns:
        continue

    valid = df[col].notna().sum()
    missing_count = df[col].isna().sum()

    percentage = (
        valid / len(df)
    ) * 100

    print(
        f"{col}: "
        f"{valid:,} valid "
        f"({percentage:.2f}%), "
        f"{missing_count:,} missing"
    )


# ============================================================
# RISK / CONDITION FEATURE INSPECTION
# ============================================================

section("11. RISK AND CONDITION FEATURES")

risk_features = [
    "average_risk_score",
    "overall_condition_burden",
    "behavioral_health_burden",
    "physical_health_burden",
    "high_condition_burden_count",
    "risk_adjusted_services",
    "risk_adjusted_payment",
    "condition_adjusted_payment",
    "condition_adjusted_services",
]

available_risk_features = [
    col for col in risk_features
    if col in df.columns
]

print(
    df[available_risk_features]
    .describe()
    .round(4)
    .to_string()
)


# ============================================================
# PAYMENT EFFICIENCY RANGE CHECK
# ============================================================

section("12. RATIO / EFFICIENCY RANGE CHECK")

ratio_features = [
    "payment_efficiency",
    "standardized_payment_ratio",
    "payment_to_charge_ratio",
    "allowed_to_charge_ratio",
    "payment_vs_standardized_pct",
    "medical_payment_share",
    "drug_payment_share",
    "medical_service_share_stage4",
    "drug_service_share_stage4",
]

for col in ratio_features:

    if col not in df.columns:
        continue

    series = df[col].dropna()

    if len(series) == 0:
        print(f"{col}: no valid values")
        continue

    below_zero = (series < 0).sum()
    above_one = (series > 1).sum()

    print(
        f"\n{col}"
        f"\n  min: {series.min():.6f}"
        f"\n  max: {series.max():.6f}"
        f"\n  below 0: {below_zero:,}"
        f"\n  above 1: {above_one:,}"
    )


# ============================================================
# YEAR DISTRIBUTION
# ============================================================

section("13. YEAR DISTRIBUTION")

year_distribution = (
    df.groupby("Year")["Rndrng_NPI"]
    .nunique()
)

for year, count in year_distribution.items():
    print(f"{int(year)}: {count:,} providers")


# ============================================================
# FINAL DIAGNOSTIC SUMMARY
# ============================================================

section("14. FINAL STAGE 4 INSPECTION SUMMARY")

print(f"Total rows: {len(df):,}")
print(f"Total columns: {len(df.columns):,}")
print(
    f"Unique providers: "
    f"{df['Rndrng_NPI'].nunique():,}"
)
print(
    f"Unique NPI-Year combinations: "
    f"{df[['Rndrng_NPI', 'Year']].drop_duplicates().shape[0]:,}"
)

print(
    f"\nPerformance features inspected: "
    f"{len(available_features)}"
)

print(
    f"Numeric performance features: "
    f"{len(numeric_features)}"
)

print(
    f"High-correlation pairs (>= 0.90): "
    f"{len(high_corr)}"
)

print(
    f"Features with missing values: "
    f"{len(null_summary)}"
)

print(
    f"Features containing infinite values: "
    f"{len(infinite_summary)}"
)

print("\nNo data was modified.")
print("No rows were removed.")
print("No features were created.")
print("No scores were calculated.")

print(
    "\nThis script only inspects Stage 4 "
    "before composite provider scoring."
)

print("\n" + "=" * 70)
print("STAGE 4 PERFORMANCE INSPECTION COMPLETED")
print("=" * 70)