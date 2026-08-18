# ============================================================
# PROVIDER OUTLIER DIAGNOSIS
# Stage 4 Feature Quality / Outlier Inspection
# ============================================================

import os
import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

INPUT_PATH = (
    "data/processed/provider_service/provider_features_stage4.csv"
)

OUTPUT_DIR = (
    "data/processed/provider_service/outlier_diagnostics"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

FEATURES_TO_INSPECT = [
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


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_numeric(series):
    return pd.to_numeric(series, errors="coerce")


def percentile_value(series, percentile):
    if series.empty:
        return np.nan
    return series.quantile(percentile)


def iqr_bounds(series):
    if series.empty:
        return np.nan, np.nan

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)

    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    return lower, upper


def print_separator():
    print("=" * 60)


# ============================================================
# HEADER
# ============================================================

print("=" * 60)
print("PROVIDER OUTLIER DIAGNOSIS")
print("STAGE 4 FEATURE QUALITY / OUTLIER INSPECTION")
print("=" * 60)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading Stage 4 dataset...")

df = pd.read_csv(
    INPUT_PATH,
    low_memory=False
)

print(f"Rows loaded: {len(df):,}")
print(f"Columns loaded: {len(df.columns)}")


# ============================================================
# BASIC VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("BASIC VALIDATION")
print("=" * 60)

required_columns = [
    "Rndrng_NPI",
    "Year",
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_Mdcr_Pymt_Amt",
    "Tot_Mdcr_Alowd_Amt",
    "Tot_Sbmtd_Chrg",
    "Tot_Mdcr_Stdzd_Amt",
]

missing_required = [
    col for col in required_columns
    if col not in df.columns
]

if missing_required:
    print("Missing required columns:")
    for col in missing_required:
        print(f"- {col}")
    raise ValueError("Required columns missing.")

print("Required columns: PASSED")


duplicate_count = df.duplicated(
    subset=["Rndrng_NPI", "Year"]
).sum()

print(f"Duplicate NPI-Year rows: {duplicate_count}")

if duplicate_count == 0:
    print("NPI + Year grain: PASSED")
else:
    print("WARNING: Duplicate NPI-Year rows detected.")


# ============================================================
# FEATURE AVAILABILITY
# ============================================================

print("\n" + "=" * 60)
print("FEATURE AVAILABILITY")
print("=" * 60)

available_features = [
    feature
    for feature in FEATURES_TO_INSPECT
    if feature in df.columns
]

missing_features = [
    feature
    for feature in FEATURES_TO_INSPECT
    if feature not in df.columns
]

print(f"Requested features: {len(FEATURES_TO_INSPECT)}")
print(f"Available features: {len(available_features)}")
print(f"Missing features: {len(missing_features)}")

if missing_features:
    print("\nMissing features:")
    for feature in missing_features:
        print(f"- {feature}")


# ============================================================
# NUMERIC CONVERSION
# ============================================================

for feature in available_features:
    df[feature] = safe_numeric(df[feature])


# ============================================================
# OUTLIER STATISTICS
# ============================================================

print("\n" + "=" * 60)
print("OUTLIER STATISTICS")
print("=" * 60)

summary_rows = []

for feature in available_features:

    series = df[feature]

    valid = series.dropna()
    valid = valid[np.isfinite(valid)]

    if len(valid) == 0:
        continue

    q1 = valid.quantile(0.25)
    q3 = valid.quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    iqr_outliers = (
        (valid < lower_bound) |
        (valid > upper_bound)
    ).sum()

    summary_rows.append({
        "feature": feature,
        "count": len(valid),

        "missing": int(series.isna().sum()),

        "min": valid.min(),

        "p01": valid.quantile(0.01),
        "p05": valid.quantile(0.05),
        "p25": q1,
        "median": valid.quantile(0.50),
        "p75": q3,
        "p95": valid.quantile(0.95),
        "p99": valid.quantile(0.99),
        "p995": valid.quantile(0.995),
        "p999": valid.quantile(0.999),

        "max": valid.max(),

        "iqr_lower": lower_bound,
        "iqr_upper": upper_bound,

        "iqr_outlier_count": int(iqr_outliers),

        "iqr_outlier_pct": (
            iqr_outliers / len(valid) * 100
        ),
    })


summary_df = pd.DataFrame(summary_rows)


# ============================================================
# PRINT SUMMARY
# ============================================================

pd.set_option("display.max_rows", 200)
pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 220)
pd.set_option("display.float_format", "{:,.4f}".format)

print("\n")
print(
    summary_df[
        [
            "feature",
            "count",
            "missing",
            "p95",
            "p99",
            "p995",
            "p999",
            "max",
            "iqr_outlier_count",
            "iqr_outlier_pct",
        ]
    ].to_string(index=False)
)


# ============================================================
# SAVE SUMMARY
# ============================================================

summary_path = os.path.join(
    OUTPUT_DIR,
    "provider_outlier_summary.csv"
)

summary_df.to_csv(
    summary_path,
    index=False
)

print("\nOutlier summary saved:")
print(summary_path)


# ============================================================
# RATIO / RANGE DIAGNOSTICS
# ============================================================

print("\n" + "=" * 60)
print("RATIO / RANGE DIAGNOSTICS")
print("=" * 60)


ratio_checks = {
    "payment_efficiency": (0, 1),
    "standardized_payment_ratio": (0, 1),
    "payment_to_charge_ratio": (0, 1),
    "allowed_to_charge_ratio": (0, 1),

    "medical_payment_share": (0, 1),
    "drug_payment_share": (0, 1),

    "medical_service_share_stage4": (0, 1),
    "drug_service_share_stage4": (0, 1),
}


ratio_rows = []

for feature, (lower, upper) in ratio_checks.items():

    if feature not in df.columns:
        continue

    series = df[feature]

    valid = series.dropna()
    valid = valid[np.isfinite(valid)]

    below = (valid < lower).sum()
    above = (valid > upper).sum()

    print(f"\n{feature}")

    print(f"  Expected range : {lower} to {upper}")
    print(f"  Below range    : {below:,}")
    print(f"  Above range    : {above:,}")

    if len(valid) > 0:
        print(f"  Minimum        : {valid.min():,.6f}")
        print(f"  Maximum        : {valid.max():,.6f}")

    ratio_rows.append({
        "feature": feature,
        "expected_lower": lower,
        "expected_upper": upper,
        "below_range_count": int(below),
        "above_range_count": int(above),
        "minimum": valid.min() if len(valid) else np.nan,
        "maximum": valid.max() if len(valid) else np.nan,
    })


ratio_df = pd.DataFrame(ratio_rows)

ratio_path = os.path.join(
    OUTPUT_DIR,
    "ratio_range_diagnostics.csv"
)

ratio_df.to_csv(
    ratio_path,
    index=False
)


# ============================================================
# ZERO DENOMINATOR DIAGNOSTICS
# ============================================================

print("\n" + "=" * 60)
print("ZERO DENOMINATOR DIAGNOSTICS")
print("=" * 60)

denominator_columns = [
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_HCPCS_Cds",
    "Tot_Sbmtd_Chrg",
    "Tot_Mdcr_Alowd_Amt",
    "Tot_Mdcr_Stdzd_Amt",

    "Drug_Tot_Benes",
    "Drug_Tot_Srvcs",
    "Drug_Tot_HCPCS_Cds",

    "Med_Tot_Benes",
    "Med_Tot_Srvcs",
    "Med_Tot_HCPCS_Cds",

    "average_risk_score",
    "overall_condition_burden",
]

zero_rows = []

for column in denominator_columns:

    if column not in df.columns:
        continue

    series = safe_numeric(df[column])

    zero_count = (series == 0).sum()
    negative_count = (series < 0).sum()
    null_count = series.isna().sum()

    print(f"\n{column}")
    print(f"  Zero values     : {zero_count:,}")
    print(f"  Negative values: {negative_count:,}")
    print(f"  Null values    : {null_count:,}")

    zero_rows.append({
        "column": column,
        "zero_count": int(zero_count),
        "negative_count": int(negative_count),
        "null_count": int(null_count),
    })


zero_df = pd.DataFrame(zero_rows)

zero_path = os.path.join(
    OUTPUT_DIR,
    "denominator_diagnostics.csv"
)

zero_df.to_csv(
    zero_path,
    index=False
)


# ============================================================
# TOP EXTREME RECORDS
# ============================================================

print("\n" + "=" * 60)
print("TOP EXTREME PROVIDER-YEAR RECORDS")
print("=" * 60)


identifier_columns = [
    "Rndrng_NPI",
    "Year",
    "Rndrng_Prvdr_Last_Org_Name",
    "Rndrng_Prvdr_First_Name",
    "Rndrng_Prvdr_Type",
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_Mdcr_Pymt_Amt",
]


identifier_columns = [
    col for col in identifier_columns
    if col in df.columns
]


for feature in [
    "service_intensity_per_beneficiary",
    "services_per_risk_score",
    "risk_adjusted_services",
    "risk_adjusted_payment",
    "condition_adjusted_payment",
]:

    if feature not in df.columns:
        continue

    print("\n" + "-" * 60)
    print(f"TOP 10: {feature}")
    print("-" * 60)

    top = (
        df[
            identifier_columns + [feature]
        ]
        .sort_values(
            by=feature,
            ascending=False,
            na_position="last"
        )
        .head(10)
    )

    print(top.to_string(index=False))

    output_path = os.path.join(
        OUTPUT_DIR,
        f"top_extreme_{feature}.csv"
    )

    top.to_csv(
        output_path,
        index=False
    )


# ============================================================
# YEAR-WISE EXTREME ANALYSIS
# ============================================================

print("\n" + "=" * 60)
print("YEAR-WISE OUTLIER ANALYSIS")
print("=" * 60)

year_rows = []

for feature in available_features:

    if "Year" not in df.columns:
        break

    for year, group in df.groupby("Year"):

        series = group[feature].dropna()

        series = series[
            np.isfinite(series)
        ]

        if len(series) == 0:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        upper = q3 + 1.5 * iqr

        outliers = (series > upper).sum()

        year_rows.append({
            "feature": feature,
            "year": year,
            "count": len(series),
            "p95": series.quantile(0.95),
            "p99": series.quantile(0.99),
            "max": series.max(),
            "iqr_upper": upper,
            "iqr_outlier_count": int(outliers),
            "iqr_outlier_pct": (
                outliers / len(series) * 100
            ),
        })


year_df = pd.DataFrame(year_rows)

year_path = os.path.join(
    OUTPUT_DIR,
    "yearwise_outlier_diagnostics.csv"
)

year_df.to_csv(
    year_path,
    index=False
)


# ============================================================
# FINAL STATUS
# ============================================================

print("\n" + "=" * 60)
print("OUTLIER DIAGNOSIS COMPLETED")
print("=" * 60)

print("\nIMPORTANT:")
print("This script DOES NOT remove rows.")
print("This script DOES NOT cap values.")
print("This script DOES NOT winsorize values.")
print("This script DOES NOT modify Stage 4.")
print()
print("It only diagnoses:")
print("- Statistical outliers")
print("- Extreme distributions")
print("- Suspicious ratio ranges")
print("- Zero/invalid denominators")
print("- Year-specific extremes")
print("- Extreme provider-year observations")
print()
print("Next step: review the diagnostic output before")
print("deciding whether any feature definitions need correction")
print("or whether genuine outliers should simply be FLAGGED.")

print("\nDiagnostic files saved under:")
print(OUTPUT_DIR)

print("=" * 60)