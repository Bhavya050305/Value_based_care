from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_aco_features_final.csv"
)


# ============================================================
# HELPER
# ============================================================

def section(title):
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


# ============================================================
# HEADER
# ============================================================

section("FINAL PROVIDER + ACO DATA QUALITY AUDIT")

print(f"\nInput file:\n{INPUT_FILE}")


# ============================================================
# FILE CHECK
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found:\n{INPUT_FILE}"
    )

print("\n✓ Input file found.")


# ============================================================
# LOAD
# ============================================================

section("LOADING FINAL DATASET")

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(f"Rows:    {len(df):,}")
print(f"Columns: {len(df.columns):,}")


# ============================================================
# BASIC STRUCTURE
# ============================================================

section("STRUCTURAL CHECKS")

required_keys = [
    "Rndrng_NPI",
    "Year",
    "ACO_ID",
]

for column in required_keys:

    if column in df.columns:
        print(f"✓ {column}")
    else:
        print(f"✗ MISSING: {column}")


# ============================================================
# GRAIN
# ============================================================

section("NPI + YEAR GRAIN")

duplicate_rows = df.duplicated(
    subset=["Rndrng_NPI", "Year"]
).sum()

print(f"Duplicate NPI-Year rows: {duplicate_rows:,}")

if duplicate_rows == 0:
    print("✓ NPI + Year grain is unique.")
else:
    print("✗ Duplicate NPI-Year rows detected.")


# ============================================================
# PROVIDER COVERAGE
# ============================================================

section("PROVIDER COVERAGE")

unique_npi = df["Rndrng_NPI"].nunique()

missing_npi = df["Rndrng_NPI"].isna().sum()

print(f"Unique providers: {unique_npi:,}")
print(f"Missing NPI:      {missing_npi:,}")

if missing_npi == 0:
    print("✓ No missing NPI values.")


# ============================================================
# YEAR COVERAGE
# ============================================================

section("YEAR COVERAGE")

years = sorted(
    df["Year"]
    .dropna()
    .unique()
)

print("Years:")
for year in years:
    print(f"  - {int(year)}")

print(f"\nUnique years: {len(years)}")


# ============================================================
# ACO COVERAGE
# ============================================================

section("ACO COVERAGE")

missing_aco = df["ACO_ID"].isna().sum()

aco_count = df["ACO_ID"].nunique()

print(f"Unique ACOs:   {aco_count}")
print(f"Missing ACO:   {missing_aco:,}")

print("\nACO values:")

for aco in sorted(
    df["ACO_ID"]
    .dropna()
    .unique()
):
    print(f"  - {aco}")


# ============================================================
# PERFORMANCE FEATURES
# ============================================================

section("PERFORMANCE FEATURES")

performance_columns = [
    "utilization_score",
    "cost_score",
    "provider_segment",
    "high_utilization_flag",
    "high_cost_flag",
    "low_utilization_flag",
    "low_cost_flag",
]

for column in performance_columns:

    missing = df[column].isna().sum()

    print(
        f"{column}: "
        f"{missing:,} missing"
    )


# ============================================================
# SCORE RANGES
# ============================================================

section("PERFORMANCE SCORE RANGES")

for column in [
    "utilization_score",
    "cost_score",
]:

    minimum = df[column].min()
    maximum = df[column].max()
    mean = df[column].mean()

    print(f"\n{column}")
    print(f"  Minimum: {minimum}")
    print(f"  Maximum: {maximum}")
    print(f"  Mean:    {mean}")

    if minimum < 0 or maximum > 100:
        print("  ⚠ Check score range.")
    else:
        print("  ✓ Range appears valid.")


# ============================================================
# PROVIDER SEGMENTS
# ============================================================

section("PROVIDER SEGMENTS")

print(
    df["provider_segment"]
    .value_counts(dropna=False)
)


# ============================================================
# LONGITUDINAL FEATURES
# ============================================================

section("LONGITUDINAL FEATURES")

longitudinal_columns = [
    "longitudinal_years_observed",
    "longitudinal_first_year",
    "longitudinal_last_year",
    "dominant_provider_segment",
    "segment_year_count",
    "segment_stability",
    "overall_provider_segment",
    "history_class",
]

for column in longitudinal_columns:

    missing = df[column].isna().sum()

    print(
        f"{column}: "
        f"{missing:,} missing"
    )


# ============================================================
# SEGMENT STABILITY
# ============================================================

section("SEGMENT STABILITY")

minimum = df["segment_stability"].min()
maximum = df["segment_stability"].max()

print(f"Minimum: {minimum}")
print(f"Maximum: {maximum}")

if minimum < 0 or maximum > 1:
    print("⚠ Segment stability outside expected 0-1 range.")
else:
    print("✓ Segment stability range valid.")


# ============================================================
# HISTORY CLASS
# ============================================================

section("HISTORY CLASS")

print(
    df["history_class"]
    .value_counts(dropna=False)
)


# ============================================================
# NULL CHECK
# ============================================================

section("MISSING VALUE SUMMARY")

important_columns = [
    "Rndrng_NPI",
    "Year",
    "ACO_ID",
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_Mdcr_Pymt_Amt",
    "Tot_Mdcr_Alowd_Amt",
    "Tot_Mdcr_Stdzd_Amt",
    "Bene_Avg_Risk_Scre",
    "service_intensity_per_beneficiary",
    "payment_per_beneficiary",
    "payment_per_service",
    "risk_adjusted_services",
    "risk_adjusted_payment",
    "risk_adjusted_allowed_amount",
    "condition_adjusted_services",
    "condition_adjusted_payment",
    "utilization_score",
    "cost_score",
    "provider_segment",
]

for column in important_columns:

    missing = df[column].isna().sum()

    percentage = (
        missing / len(df) * 100
    )

    print(
        f"{column:45s}"
        f"{missing:10,} "
        f"({percentage:.2f}%)"
    )


# ============================================================
# INFINITE VALUES
# ============================================================

section("INFINITE VALUE CHECK")

numeric_columns = df.select_dtypes(
    include=np.number
).columns

infinite_count = np.isinf(
    df[numeric_columns]
).sum().sum()

print(
    f"Infinite numeric values: "
    f"{infinite_count:,}"
)

if infinite_count == 0:
    print("✓ No infinite numeric values.")


# ============================================================
# NEGATIVE VALUES
# ============================================================

section("NEGATIVE VALUE CHECK")

non_negative_columns = [
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_HCPCS_Cds",
    "Tot_Mdcr_Pymt_Amt",
    "Tot_Mdcr_Alowd_Amt",
    "Tot_Mdcr_Stdzd_Amt",
    "service_intensity_per_beneficiary",
    "payment_per_beneficiary",
    "payment_per_service",
    "risk_adjusted_services",
    "risk_adjusted_payment",
    "risk_adjusted_allowed_amount",
]

for column in non_negative_columns:

    negative_count = (
        df[column] < 0
    ).sum()

    if negative_count == 0:
        print(f"✓ {column}")
    else:
        print(
            f"⚠ {column}: "
            f"{negative_count:,} negative"
        )


# ============================================================
# MEDICAL / DRUG
# ============================================================

section("MEDICAL / DRUG FEATURES")

medical_drug_columns = [
    "drug_data_suppressed",
    "medical_payment_share",
    "drug_payment_share",
    "medical_service_share_stage4",
    "drug_service_share_stage4",
]

for column in medical_drug_columns:

    missing = df[column].isna().sum()

    print(
        f"{column}: "
        f"{missing:,} missing"
    )


# ============================================================
# ACO DISTRIBUTION
# ============================================================

section("ACO DISTRIBUTION")

aco_summary = (
    df.groupby("ACO_ID")
    .agg(
        Provider_Year_Rows=("Rndrng_NPI", "size"),
        Unique_Providers=("Rndrng_NPI", "nunique"),
        Avg_Utilization=("utilization_score", "mean"),
        Avg_Cost=("cost_score", "mean"),
    )
    .reset_index()
)

print(
    aco_summary.to_string(
        index=False
    )
)


# ============================================================
# PROVIDER HISTORY CONSISTENCY
# ============================================================

section("PROVIDER HISTORY CONSISTENCY")

history_check = (
    df.groupby("Rndrng_NPI")
    .agg(
        actual_years=("Year", "nunique"),
        reported_years=(
            "longitudinal_years_observed",
            "first"
        ),
        first_actual_year=("Year", "min"),
        first_reported_year=(
            "longitudinal_first_year",
            "first"
        ),
        last_actual_year=("Year", "max"),
        last_reported_year=(
            "longitudinal_last_year",
            "first"
        ),
    )
)

year_mismatch = (
    history_check[
        history_check["actual_years"]
        != history_check["reported_years"]
    ]
)

first_year_mismatch = (
    history_check[
        history_check["first_actual_year"]
        != history_check["first_reported_year"]
    ]
)

last_year_mismatch = (
    history_check[
        history_check["last_actual_year"]
        != history_check["last_reported_year"]
    ]
)

print(
    f"Providers with year-count mismatch: "
    f"{len(year_mismatch):,}"
)

print(
    f"Providers with first-year mismatch: "
    f"{len(first_year_mismatch):,}"
)

print(
    f"Providers with last-year mismatch: "
    f"{len(last_year_mismatch):,}"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

section("FINAL AUDIT SUMMARY")

print(
    f"Rows:                    {len(df):,}"
)

print(
    f"Columns:                 {len(df.columns):,}"
)

print(
    f"Unique providers:        {df['Rndrng_NPI'].nunique():,}"
)

print(
    f"Unique years:            {df['Year'].nunique():,}"
)

print(
    f"Unique ACOs:             {df['ACO_ID'].nunique():,}"
)

print(
    f"Duplicate NPI-Year:      {duplicate_rows:,}"
)

print(
    f"Missing NPI:             {missing_npi:,}"
)

print(
    f"Missing ACO:             {missing_aco:,}"
)

print(
    f"Infinite values:         {infinite_count:,}"
)

print(
    f"History count mismatch:  {len(year_mismatch):,}"
)

print(
    f"First-year mismatch:     {len(first_year_mismatch):,}"
)

print(
    f"Last-year mismatch:      {len(last_year_mismatch):,}"
)

print("\nOutput dataset is ready for final review.")

print("\n" + "=" * 90)