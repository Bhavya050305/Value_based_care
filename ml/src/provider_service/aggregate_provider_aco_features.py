"""
Aggregate Provider + ACO Features

Purpose:
    Convert the provider-year dataset into an ACO-year performance dataset.

Input:
    data/processed/provider_service/provider_aco_features.csv

Input grain:
    Rndrng_NPI + Year

Output:
    data/processed/provider_service/aco_provider_performance.csv

Output grain:
    ACO_ID + Year

IMPORTANT:
    ACO_ID is synthetic and is only being used for
    analytical/dashboard prototyping.
"""

from pathlib import Path

import pandas as pd
import numpy as np


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_aco_features.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "aco_provider_performance.csv"
)


# ============================================================
# 2. CONFIGURATION
# ============================================================

print("=" * 80)
print("ACO-LEVEL PROVIDER PERFORMANCE AGGREGATION")
print("=" * 80)

print("\nInput:")
print(INPUT_FILE)

print("\nOutput:")
print(OUTPUT_FILE)


# ============================================================
# 3. CHECK INPUT
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found:\n{INPUT_FILE}"
    )

print("\n✓ Input file found.")


# ============================================================
# 4. LOAD DATA
# ============================================================

print("\n" + "-" * 80)
print("LOADING PROVIDER + ACO DATA")
print("-" * 80)

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(f"Rows loaded:    {len(df):,}")
print(f"Columns loaded: {len(df.columns):,}")


# ============================================================
# 5. REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Rndrng_NPI",
    "Year",
    "ACO_ID",
]

print("\n" + "-" * 80)
print("CHECKING REQUIRED COLUMNS")
print("-" * 80)

for column in required_columns:

    if column not in df.columns:
        raise ValueError(
            f"Required column missing: {column}"
        )

    print(f"✓ {column}")


# ============================================================
# 6. STANDARDIZE KEY COLUMNS
# ============================================================

df["Rndrng_NPI"] = (
    df["Rndrng_NPI"]
    .astype("string")
    .str.strip()
)

df["ACO_ID"] = (
    df["ACO_ID"]
    .astype("string")
    .str.strip()
)


# ============================================================
# 7. BASIC VALIDATION
# ============================================================

print("\n" + "-" * 80)
print("BASIC VALIDATION")
print("-" * 80)

missing_npi = df["Rndrng_NPI"].isna().sum()
missing_year = df["Year"].isna().sum()
missing_aco = df["ACO_ID"].isna().sum()

print(f"Missing NPI:  {missing_npi:,}")
print(f"Missing Year: {missing_year:,}")
print(f"Missing ACO:  {missing_aco:,}")

if missing_npi > 0:
    raise ValueError("Missing NPI values detected.")

if missing_year > 0:
    raise ValueError("Missing Year values detected.")

if missing_aco > 0:
    raise ValueError("Missing ACO_ID values detected.")

print("✓ No missing grouping keys.")


# ============================================================
# 8. CHECK INPUT GRAIN
# ============================================================

duplicate_rows = (
    df
    .duplicated(
        subset=[
            "Rndrng_NPI",
            "Year"
        ]
    )
    .sum()
)

print(
    f"\nDuplicate NPI-Year rows: "
    f"{duplicate_rows:,}"
)

if duplicate_rows > 0:
    raise ValueError(
        "Duplicate NPI-Year rows detected."
    )

print("✓ Input grain is NPI + Year.")


# ============================================================
# 9. HELPER FUNCTIONS
# ============================================================

def find_column(possible_names):
    """
    Find the first matching column from a list of possible names.
    """

    for name in possible_names:

        if name in df.columns:
            return name

    return None


def numeric_sum(column):
    """
    Safely calculate sum.
    """

    return pd.to_numeric(
        df[column],
        errors="coerce"
    )


def safe_divide(numerator, denominator):
    """
    Safely divide two pandas Series.
    """

    return np.where(
        denominator != 0,
        numerator / denominator,
        np.nan
    )


# ============================================================
# 10. IDENTIFY IMPORTANT PROVIDER FEATURES
# ============================================================

print("\n" + "-" * 80)
print("IDENTIFYING PERFORMANCE FEATURES")
print("-" * 80)

# The pipeline may use slightly different names depending
# on earlier feature-engineering stages.

BENEFICIARY_COL = find_column([
    "Tot_Benes",
    "Total_Beneficiaries",
    "Beneficiaries",
    "Medicare_Beneficiaries",
])

SERVICE_COL = find_column([
    "Tot_Srvcs",
    "Total_Services",
    "Services",
])

PAYMENT_COL = find_column([
    "Tot_Mdcr_Pymt_Amt",
    "Total_Medicare_Payment",
    "Medicare_Payment",
    "Total_Payment",
])

ALLOWED_COL = find_column([
    "Tot_Mdcr_Alowd_Amt",
    "Total_Medicare_Allowed",
    "Medicare_Allowed",
    "Total_Allowed",
])

CHARGE_COL = find_column([
    "Tot_Mdcr_Stdzd_Amt",
    "Total_Standardized_Payment",
    "Standardized_Payment",
])


print(f"Beneficiary column: {BENEFICIARY_COL}")
print(f"Service column:     {SERVICE_COL}")
print(f"Payment column:     {PAYMENT_COL}")
print(f"Allowed column:     {ALLOWED_COL}")
print(f"Standardized col:   {CHARGE_COL}")


# ============================================================
# 11. IDENTIFY SCORE / SEGMENT FEATURES
# ============================================================

score_candidates = [
    "utilization_score",
    "Utilization_Score",
    "cost_score",
    "Cost_Score",
    "risk_score",
    "Risk_Score",
    "performance_score",
    "Performance_Score",
]

score_columns = [
    column
    for column in score_candidates
    if column in df.columns
]

print("\nScore columns found:")

if score_columns:

    for column in score_columns:
        print(f"    ✓ {column}")

else:

    print("    None found")


# ============================================================
# 12. IDENTIFY SEGMENT COLUMN
# ============================================================

segment_candidates = [
    "performance_segment",
    "Performance_Segment",
    "provider_segment",
    "Provider_Segment",
    "segment",
    "Segment",
]

SEGMENT_COL = find_column(segment_candidates)

print("\nSegment column:")
print(SEGMENT_COL)


# ============================================================
# 13. START ACO-YEAR GROUPING
# ============================================================

print("\n" + "-" * 80)
print("CREATING ACO-YEAR GROUPS")
print("-" * 80)

grouped = (
    df
    .groupby(
        [
            "ACO_ID",
            "Year"
        ],
        dropna=False
    )
)


# ============================================================
# 14. BASIC ACO-YEAR METRICS
# ============================================================

aco_df = (
    grouped
    .agg(
        Provider_Year_Count=(
            "Rndrng_NPI",
            "count"
        ),
        Unique_Provider_Count=(
            "Rndrng_NPI",
            "nunique"
        )
    )
    .reset_index()
)

print(
    f"ACO-Year groups created: "
    f"{len(aco_df):,}"
)


# ============================================================
# 15. ADD BENEFICIARY METRICS
# ============================================================

if BENEFICIARY_COL:

    df["_beneficiaries_numeric"] = pd.to_numeric(
        df[BENEFICIARY_COL],
        errors="coerce"
    )

    beneficiary_stats = (
        df
        .groupby(
            [
                "ACO_ID",
                "Year"
            ]
        )["_beneficiaries_numeric"]
        .agg(
            Total_Beneficiaries="sum",
            Average_Beneficiaries_Per_Provider="mean",
            Median_Beneficiaries_Per_Provider="median",
        )
        .reset_index()
    )

    aco_df = aco_df.merge(
        beneficiary_stats,
        on=[
            "ACO_ID",
            "Year"
        ],
        how="left"
    )


# ============================================================
# 16. ADD SERVICE METRICS
# ============================================================

if SERVICE_COL:

    df["_services_numeric"] = pd.to_numeric(
        df[SERVICE_COL],
        errors="coerce"
    )

    service_stats = (
        df
        .groupby(
            [
                "ACO_ID",
                "Year"
            ]
        )["_services_numeric"]
        .agg(
            Total_Services="sum",
            Average_Services_Per_Provider="mean",
            Median_Services_Per_Provider="median",
        )
        .reset_index()
    )

    aco_df = aco_df.merge(
        service_stats,
        on=[
            "ACO_ID",
            "Year"
        ],
        how="left"
    )


# ============================================================
# 17. ADD PAYMENT METRICS
# ============================================================

if PAYMENT_COL:

    df["_payment_numeric"] = pd.to_numeric(
        df[PAYMENT_COL],
        errors="coerce"
    )

    payment_stats = (
        df
        .groupby(
            [
                "ACO_ID",
                "Year"
            ]
        )["_payment_numeric"]
        .agg(
            Total_Medicare_Payment="sum",
            Average_Payment_Per_Provider="mean",
            Median_Payment_Per_Provider="median",
        )
        .reset_index()
    )

    aco_df = aco_df.merge(
        payment_stats,
        on=[
            "ACO_ID",
            "Year"
        ],
        how="left"
    )


# ============================================================
# 18. ADD ALLOWED AMOUNT
# ============================================================

if ALLOWED_COL:

    df["_allowed_numeric"] = pd.to_numeric(
        df[ALLOWED_COL],
        errors="coerce"
    )

    allowed_stats = (
        df
        .groupby(
            [
                "ACO_ID",
                "Year"
            ]
        )["_allowed_numeric"]
        .sum()
        .reset_index(
            name="Total_Allowed_Amount"
        )
    )

    aco_df = aco_df.merge(
        allowed_stats,
        on=[
            "ACO_ID",
            "Year"
        ],
        how="left"
    )


# ============================================================
# 19. ADD STANDARDIZED PAYMENT
# ============================================================

if CHARGE_COL:

    df["_standardized_numeric"] = pd.to_numeric(
        df[CHARGE_COL],
        errors="coerce"
    )

    standardized_stats = (
        df
        .groupby(
            [
                "ACO_ID",
                "Year"
            ]
        )["_standardized_numeric"]
        .sum()
        .reset_index(
            name="Total_Standardized_Amount"
        )
    )

    aco_df = aco_df.merge(
        standardized_stats,
        on=[
            "ACO_ID",
            "Year"
        ],
        how="left"
    )


# ============================================================
# 20. DERIVED COST / UTILIZATION METRICS
# ============================================================

print("\n" + "-" * 80)
print("CALCULATING DERIVED ACO METRICS")
print("-" * 80)


# Payment per beneficiary
if (
    "Total_Medicare_Payment" in aco_df.columns
    and "Total_Beneficiaries" in aco_df.columns
):

    aco_df["Payment_Per_Beneficiary"] = safe_divide(
        aco_df["Total_Medicare_Payment"],
        aco_df["Total_Beneficiaries"]
    )


# Payment per service
if (
    "Total_Medicare_Payment" in aco_df.columns
    and "Total_Services" in aco_df.columns
):

    aco_df["Payment_Per_Service"] = safe_divide(
        aco_df["Total_Medicare_Payment"],
        aco_df["Total_Services"]
    )


# Services per beneficiary
if (
    "Total_Services" in aco_df.columns
    and "Total_Beneficiaries" in aco_df.columns
):

    aco_df["Services_Per_Beneficiary"] = safe_divide(
        aco_df["Total_Services"],
        aco_df["Total_Beneficiaries"]
    )


# ============================================================
# 21. AGGREGATE SCORE FEATURES
# ============================================================

print("\n" + "-" * 80)
print("AGGREGATING PERFORMANCE SCORES")
print("-" * 80)

for column in score_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    score_summary = (
        df
        .groupby(
            [
                "ACO_ID",
                "Year"
            ]
        )[column]
        .agg(
            [
                "mean",
                "median",
                "min",
                "max"
            ]
        )
        .reset_index()
    )

    score_summary = score_summary.rename(
        columns={
            "mean": f"Avg_{column}",
            "median": f"Median_{column}",
            "min": f"Min_{column}",
            "max": f"Max_{column}",
        }
    )

    aco_df = aco_df.merge(
        score_summary,
        on=[
            "ACO_ID",
            "Year"
        ],
        how="left"
    )

    print(f"✓ Aggregated {column}")


# ============================================================
# 22. SEGMENT DISTRIBUTION
# ============================================================

print("\n" + "-" * 80)
print("CALCULATING PROVIDER SEGMENT DISTRIBUTION")
print("-" * 80)

if SEGMENT_COL:

    segment_counts = pd.crosstab(
        [
            df["ACO_ID"],
            df["Year"]
        ],
        df[SEGMENT_COL]
    )

    segment_counts = (
        segment_counts
        .reset_index()
    )

    # Find all segment categories.
    segment_categories = [
        column
        for column in segment_counts.columns
        if column not in [
            "ACO_ID",
            "Year"
        ]
    ]

    # Convert counts to percentages.
    for category in segment_categories:

        percentage_column = (
            f"Segment_Pct_{str(category)}"
        )

        segment_counts[
            percentage_column
        ] = (
            segment_counts[category]
            / segment_counts[
                segment_categories
            ].sum(axis=1)
            * 100
        )

    # Keep only percentage columns.
    percentage_columns = [
        "ACO_ID",
        "Year"
    ] + [
        f"Segment_Pct_{str(category)}"
        for category in segment_categories
    ]

    segment_percentages = segment_counts[
        percentage_columns
    ]

    aco_df = aco_df.merge(
        segment_percentages,
        on=[
            "ACO_ID",
            "Year"
        ],
        how="left"
    )

    print(
        f"✓ Segment percentages created for "
        f"{len(segment_categories)} categories."
    )

else:

    print(
        "No provider segment column found."
    )


# ============================================================
# 23. SORT DATA
# ============================================================

aco_df = (
    aco_df
    .sort_values(
        [
            "ACO_ID",
            "Year"
        ]
    )
    .reset_index(drop=True)
)


# ============================================================
# 24. ROUND DERIVED NUMBERS
# ============================================================

numeric_columns = (
    aco_df
    .select_dtypes(
        include=["float64", "float32"]
    )
    .columns
)

aco_df[numeric_columns] = (
    aco_df[numeric_columns]
    .round(4)
)


# ============================================================
# 25. VALIDATE ACO-YEAR GRAIN
# ============================================================

print("\n" + "-" * 80)
print("VALIDATING ACO-YEAR DATASET")
print("-" * 80)

duplicate_aco_year = (
    aco_df
    .duplicated(
        subset=[
            "ACO_ID",
            "Year"
        ]
    )
    .sum()
)

print(
    f"Duplicate ACO-Year rows: "
    f"{duplicate_aco_year:,}"
)

if duplicate_aco_year > 0:
    raise ValueError(
        "Duplicate ACO-Year rows detected."
    )

print("✓ One row per ACO-Year.")


# ============================================================
# 26. VALIDATE ACO COUNT
# ============================================================

unique_acos = aco_df["ACO_ID"].nunique()
unique_years = aco_df["Year"].nunique()

print(
    f"Unique ACOs:  {unique_acos:,}"
)

print(
    f"Unique years: {unique_years:,}"
)

expected_groups = (
    unique_acos
    * unique_years
)

print(
    f"Expected maximum ACO-Year groups: "
    f"{expected_groups:,}"
)

print(
    f"Actual ACO-Year groups: "
    f"{len(aco_df):,}"
)


# ============================================================
# 27. CHECK MISSING VALUES
# ============================================================

missing_values = (
    aco_df
    .isna()
    .sum()
)

missing_values = (
    missing_values[
        missing_values > 0
    ]
    .sort_values(
        ascending=False
    )
)

print("\nColumns containing missing values:")

if len(missing_values) == 0:

    print("    None")

else:

    print(
        missing_values
        .head(20)
        .to_string()
    )


# ============================================================
# 28. SHOW OUTPUT PREVIEW
# ============================================================

print("\n" + "-" * 80)
print("ACO PERFORMANCE PREVIEW")
print("-" * 80)

print(
    aco_df
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 29. SAVE DATASET
# ============================================================

print("\n" + "-" * 80)
print("SAVING ACO PERFORMANCE DATASET")
print("-" * 80)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

aco_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("✓ Output saved successfully.")

print("\nOutput:")
print(OUTPUT_FILE)


# ============================================================
# 30. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("ACO AGGREGATION COMPLETE")
print("=" * 80)

print(
    f"\nProvider-Year input rows: "
    f"{len(df):,}"
)

print(
    f"ACO-Year output rows:      "
    f"{len(aco_df):,}"
)

print(
    f"Unique ACOs:               "
    f"{unique_acos:,}"
)

print(
    f"Unique years:              "
    f"{unique_years:,}"
)

print(
    f"Output columns:            "
    f"{len(aco_df.columns):,}"
)

print(
    f"Duplicate ACO-Year rows:   "
    f"{duplicate_aco_year:,}"
)

print("\nValidation:")
print("✓ Provider-Year data successfully aggregated")
print("✓ One row per ACO-Year")
print("✓ Provider counts calculated")
print("✓ Financial metrics calculated where available")
print("✓ Utilization metrics calculated where available")
print("✓ Performance scores aggregated where available")
print("✓ Segment distribution calculated where available")

print("\nIMPORTANT:")
print(
    "ACO_ID is SYNTHETIC and is intended only for "
    "analytical/dashboard prototyping."
)

print("\nOutput file:")
print(OUTPUT_FILE)

print("=" * 80)