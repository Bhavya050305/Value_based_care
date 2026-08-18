import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# SERVICE METRICS
# ============================================================

print("=" * 70)
print("SERVICE METRICS ANALYTICS")
print("=" * 70)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "provider_service"
    / "synthetic_service_data.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "provider_service"
    / "service_metrics.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading synthetic service dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Rows loaded: {len(df):,}")
print(f"Columns loaded: {len(df.columns)}")


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Rndrng_NPI",
    "ACO_ID",
    "Year",
    "HCPCS_Cd",
    "HCPCS_Desc",
    "Place_Of_Srvc",
    "service_category",
    "Tot_Benes",
    "Tot_Srvcs",
    "Avg_Sbmtd_Chrg",
    "Avg_Mdcr_Alowd_Amt",
    "Avg_Mdcr_Pymt_Amt",
    "Avg_Mdcr_Stdzd_Amt",
    "payment_per_service",
    "payment_per_beneficiary",
    "utilization_rate",
    "cost_score",
    "utilization_score",
]


missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    print("\nERROR: Missing columns:")
    print(missing_columns)
    raise SystemExit(1)

print("Required column check: PASSED")


# ============================================================
# BASIC VALIDATION
# ============================================================

duplicate_count = df.duplicated(
    subset=["Rndrng_NPI", "ACO_ID", "Year", "HCPCS_Cd"]
).sum()

print(f"Duplicate Provider-Year-HCPCS: {duplicate_count}")

if duplicate_count != 0:
    raise ValueError(
        "Duplicate Provider-Year-HCPCS records detected."
    )


# ============================================================
# CREATE SERVICE-LEVEL AGGREGATION
#
# Grain:
# ACO + Year + HCPCS + Service Category
# ============================================================

print("\nCreating service-level metrics...")


group_columns = [
    "ACO_ID",
    "Year",
    "HCPCS_Cd",
    "HCPCS_Desc",
    "Place_Of_Srvc",
    "service_category",
]


service_metrics = (
    df.groupby(group_columns, dropna=False)
    .agg(
        provider_count=("Rndrng_NPI", "nunique"),

        beneficiary_count=("Tot_Benes", "sum"),

        service_volume=("Tot_Srvcs", "sum"),

        total_submitted_charge=(
            "Avg_Sbmtd_Chrg",
            "mean"
        ),

        avg_allowed_amount=(
            "Avg_Mdcr_Alowd_Amt",
            "mean"
        ),

        total_payment=(
            "Avg_Mdcr_Pymt_Amt",
            "sum"
        ),

        avg_payment=(
            "Avg_Mdcr_Pymt_Amt",
            "mean"
        ),

        avg_standardized_payment=(
            "Avg_Mdcr_Stdzd_Amt",
            "mean"
        ),

        avg_payment_per_service=(
            "payment_per_service",
            "mean"
        ),

        avg_payment_per_beneficiary=(
            "payment_per_beneficiary",
            "mean"
        ),

        avg_utilization_rate=(
            "utilization_rate",
            "mean"
        ),

        avg_cost_score=(
            "cost_score",
            "mean"
        ),

        avg_utilization_score=(
            "utilization_score",
            "mean"
        ),
    )
    .reset_index()
)


# ============================================================
# DERIVED METRICS
# ============================================================

print("Creating derived metrics...")


# Service volume per provider
service_metrics["services_per_provider"] = (
    service_metrics["service_volume"]
    / service_metrics["provider_count"].replace(0, np.nan)
)


# Beneficiaries per provider
service_metrics["beneficiaries_per_provider"] = (
    service_metrics["beneficiary_count"]
    / service_metrics["provider_count"].replace(0, np.nan)
)


# Payment per service
service_metrics["calculated_payment_per_service"] = (
    service_metrics["total_payment"]
    / service_metrics["service_volume"].replace(0, np.nan)
)


# ============================================================
# YEAR-OVER-YEAR CHANGES
# ============================================================

print("Calculating year-over-year changes...")


service_metrics = service_metrics.sort_values(
    [
        "HCPCS_Cd",
        "ACO_ID",
        "Year"
    ]
)


service_metrics["service_volume_change_pct"] = (
    service_metrics
    .groupby(["ACO_ID", "HCPCS_Cd"])["service_volume"]
    .pct_change()
    .replace([np.inf, -np.inf], np.nan)
    * 100
)


service_metrics["payment_change_pct"] = (
    service_metrics
    .groupby(["ACO_ID", "HCPCS_Cd"])["total_payment"]
    .pct_change()
    .replace([np.inf, -np.inf], np.nan)
    * 100
)


service_metrics["utilization_change_pct"] = (
    service_metrics
    .groupby(["ACO_ID", "HCPCS_Cd"])["avg_utilization_rate"]
    .pct_change()
    .replace([np.inf, -np.inf], np.nan)
    * 100
)
# First year has no previous year for comparison.
# Use 0 for dashboard-friendly output.
change_columns = [
    "service_volume_change_pct",
    "payment_change_pct",
    "utilization_change_pct",
]

for col in change_columns:
    service_metrics[col] = (
        service_metrics[col]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )


# ============================================================
# HIGH-COST / HIGH-UTILIZATION FLAGS
# ============================================================

print("Creating service performance flags...")


cost_threshold = service_metrics["avg_cost_score"].quantile(0.75)

utilization_threshold = (
    service_metrics["avg_utilization_score"]
    .quantile(0.75)
)


service_metrics["high_cost_service"] = (
    service_metrics["avg_cost_score"]
    >= cost_threshold
)


service_metrics["high_utilization_service"] = (
    service_metrics["avg_utilization_score"]
    >= utilization_threshold
)


# ============================================================
# SERVICE PERFORMANCE SEGMENT
# ============================================================

def classify_service(row):

    high_cost = row["high_cost_service"]
    high_util = row["high_utilization_service"]

    if high_cost and high_util:
        return "HIGH_COST_HIGH_UTILIZATION"

    elif high_cost and not high_util:
        return "HIGH_COST"

    elif not high_cost and high_util:
        return "HIGH_UTILIZATION"

    else:
        return "MODERATE"


service_metrics["service_performance_segment"] = (
    service_metrics.apply(
        classify_service,
        axis=1
    )
)


# ============================================================
# CLEAN NUMERIC VALUES
# ============================================================

numeric_columns = service_metrics.select_dtypes(
    include=np.number
).columns


service_metrics[numeric_columns] = (
    service_metrics[numeric_columns]
    .replace([np.inf, -np.inf], np.nan)
)


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("SERVICE METRICS VALIDATION")
print("=" * 70)


print(
    f"Rows: {len(service_metrics):,}"
)

print(
    f"Columns: {len(service_metrics.columns)}"
)

print(
    f"Unique ACOs: "
    f"{service_metrics['ACO_ID'].nunique()}"
)

print(
    f"Unique HCPCS codes: "
    f"{service_metrics['HCPCS_Cd'].nunique()}"
)

print(
    f"Years: "
    f"{sorted(service_metrics['Year'].unique().tolist())}"
)


duplicate_metrics = service_metrics.duplicated(
    subset=[
        "ACO_ID",
        "Year",
        "HCPCS_Cd"
    ]
).sum()


print(
    f"Duplicate ACO-Year-HCPCS: "
    f"{duplicate_metrics}"
)


missing_total = service_metrics.isna().sum().sum()

print(
    f"Total missing values: "
    f"{missing_total:,}"
)


# ============================================================
# SERVICE SEGMENT DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("SERVICE PERFORMANCE SEGMENTS")
print("=" * 70)

print(
    service_metrics[
        "service_performance_segment"
    ].value_counts()
)


# ============================================================
# SAVE
# ============================================================

print("\nSaving service metrics...")

service_metrics.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("SERVICE METRICS CREATED")
print("=" * 70)

print(
    f"Output: {OUTPUT_FILE}"
)

print(
    f"Rows: {len(service_metrics):,}"
)

print(
    f"Columns: {len(service_metrics.columns)}"
)

print("\nDONE")
print("=" * 70)