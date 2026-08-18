import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# PROVIDER-SERVICE METRICS
# ============================================================

print("=" * 70)
print("PROVIDER-SERVICE METRICS ANALYTICS")
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
    / "provider_service_metrics.csv"
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
# GRAIN VALIDATION
# ============================================================

duplicate_count = df.duplicated(
    subset=[
        "Rndrng_NPI",
        "ACO_ID",
        "Year",
        "HCPCS_Cd"
    ]
).sum()

print(
    f"Duplicate Provider-Year-HCPCS: "
    f"{duplicate_count}"
)

if duplicate_count != 0:
    raise ValueError(
        "Duplicate Provider-Year-HCPCS records detected."
    )


# ============================================================
# PROVIDER-SERVICE METRICS
#
# Grain:
# Provider + ACO + Year + HCPCS
#
# The input is already at this grain, so we mainly
# standardize the analytical columns here.
# ============================================================

print("\nCreating provider-service metrics...")


provider_service = df[
    required_columns
].copy()


# ============================================================
# PROVIDER SERVICE SHARE
# ============================================================

print("Calculating provider service mix...")


provider_total_services = (
    provider_service
    .groupby(
        ["Rndrng_NPI", "ACO_ID", "Year"]
    )["Tot_Srvcs"]
    .transform("sum")
)


provider_service["service_mix_pct"] = np.where(
    provider_total_services > 0,
    (
        provider_service["Tot_Srvcs"]
        / provider_total_services
        * 100
    ),
    0
)


# ============================================================
# PROVIDER PAYMENT SHARE
# ============================================================

provider_total_payment = (
    provider_service
    .groupby(
        ["Rndrng_NPI", "ACO_ID", "Year"]
    )["Avg_Mdcr_Pymt_Amt"]
    .transform("sum")
)


provider_service["payment_mix_pct"] = np.where(
    provider_total_payment > 0,
    (
        provider_service["Avg_Mdcr_Pymt_Amt"]
        / provider_total_payment
        * 100
    ),
    0
)


# ============================================================
# SERVICE RANK WITHIN PROVIDER
# ============================================================

print("Ranking provider services...")


provider_service["service_volume_rank"] = (
    provider_service
    .groupby(
        ["Rndrng_NPI", "Year"]
    )["Tot_Srvcs"]
    .rank(
        method="dense",
        ascending=False
    )
)


provider_service["service_cost_rank"] = (
    provider_service
    .groupby(
        ["Rndrng_NPI", "Year"]
    )["payment_per_service"]
    .rank(
        method="dense",
        ascending=False
    )
)


provider_service["service_utilization_rank"] = (
    provider_service
    .groupby(
        ["Rndrng_NPI", "Year"]
    )["utilization_rate"]
    .rank(
        method="dense",
        ascending=False
    )
)


# ============================================================
# TOP SERVICE FLAGS
# ============================================================

provider_service["top_volume_service"] = (
    provider_service["service_volume_rank"] == 1
)


provider_service["top_cost_service"] = (
    provider_service["service_cost_rank"] == 1
)


provider_service["top_utilization_service"] = (
    provider_service["service_utilization_rank"] == 1
)


# ============================================================
# COST / UTILIZATION COMBINATION
# ============================================================

def classify_provider_service(row):

    high_cost = row["cost_score"] >= 0.75
    high_utilization = row["utilization_score"] >= 0.75

    if high_cost and high_utilization:
        return "HIGH_COST_HIGH_UTILIZATION"

    elif high_cost:
        return "HIGH_COST"

    elif high_utilization:
        return "HIGH_UTILIZATION"

    else:
        return "MODERATE"


print("Creating provider-service segments...")


provider_service["provider_service_segment"] = (
    provider_service.apply(
        classify_provider_service,
        axis=1
    )
)


# ============================================================
# YEAR-OVER-YEAR SERVICE CHANGES
# ============================================================

print("Calculating year-over-year changes...")


provider_service = provider_service.sort_values(
    [
        "Rndrng_NPI",
        "HCPCS_Cd",
        "Year"
    ]
)


provider_service["service_volume_change_pct"] = (
    provider_service
    .groupby(
        ["Rndrng_NPI", "HCPCS_Cd"]
    )["Tot_Srvcs"]
    .pct_change()
    .replace(
        [np.inf, -np.inf],
        np.nan
    )
    * 100
)


provider_service["payment_change_pct"] = (
    provider_service
    .groupby(
        ["Rndrng_NPI", "HCPCS_Cd"]
    )["payment_per_service"]
    .pct_change()
    .replace(
        [np.inf, -np.inf],
        np.nan
    )
    * 100
)


provider_service["utilization_change_pct"] = (
    provider_service
    .groupby(
        ["Rndrng_NPI", "HCPCS_Cd"]
    )["utilization_rate"]
    .pct_change()
    .replace(
        [np.inf, -np.inf],
        np.nan
    )
    * 100
)


# First observed year has no previous-year comparison.
change_columns = [
    "service_volume_change_pct",
    "payment_change_pct",
    "utilization_change_pct",
]


for col in change_columns:

    provider_service[col] = (
        provider_service[col]
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .fillna(0)
    )


# ============================================================
# CLEAN NUMERIC VALUES
# ============================================================

numeric_columns = provider_service.select_dtypes(
    include=np.number
).columns


provider_service[numeric_columns] = (
    provider_service[numeric_columns]
    .replace(
        [np.inf, -np.inf],
        np.nan
    )
)


# ============================================================
# FINAL MISSING VALUE HANDLING
# ============================================================

provider_service[numeric_columns] = (
    provider_service[numeric_columns]
    .fillna(0)
)


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("PROVIDER-SERVICE METRICS VALIDATION")
print("=" * 70)


print(
    f"Rows: "
    f"{len(provider_service):,}"
)


print(
    f"Columns: "
    f"{len(provider_service.columns)}"
)


print(
    f"Unique providers: "
    f"{provider_service['Rndrng_NPI'].nunique():,}"
)


print(
    f"Unique ACOs: "
    f"{provider_service['ACO_ID'].nunique()}"
)


print(
    f"Unique HCPCS codes: "
    f"{provider_service['HCPCS_Cd'].nunique()}"
)


print(
    f"Years: "
    f"{sorted(provider_service['Year'].unique().tolist())}"
)


duplicate_final = provider_service.duplicated(
    subset=[
        "Rndrng_NPI",
        "ACO_ID",
        "Year",
        "HCPCS_Cd"
    ]
).sum()


print(
    f"Duplicate Provider-Year-HCPCS: "
    f"{duplicate_final}"
)


missing_final = (
    provider_service.isna()
    .sum()
    .sum()
)


print(
    f"Total missing values: "
    f"{missing_final:,}"
)


negative_numeric = (
    provider_service[numeric_columns] < 0
).sum().sum()


print(
    f"Total negative numeric values: "
    f"{negative_numeric:,}"
)


# ============================================================
# PROVIDER-SERVICE SEGMENT DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("PROVIDER-SERVICE SEGMENTS")
print("=" * 70)


print(
    provider_service[
        "provider_service_segment"
    ].value_counts()
)


# ============================================================
# SAVE
# ============================================================

print("\nSaving provider-service metrics...")


provider_service.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("PROVIDER-SERVICE METRICS CREATED")
print("=" * 70)


print(
    f"Output: "
    f"{OUTPUT_FILE}"
)


print(
    f"Rows: "
    f"{len(provider_service):,}"
)


print(
    f"Columns: "
    f"{len(provider_service.columns)}"
)


print("\nDONE")
print("=" * 70)