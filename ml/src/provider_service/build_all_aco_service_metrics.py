from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "serving"
    / "all_aco"
    / "all_aco_provider_service.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "all_aco"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "all_aco_service_metrics.csv"
)


# ============================================================
# START
# ============================================================

print("=" * 80)
print("BHAVYA VBC")
print("=" * 80)
print("ALL-ACO SERVICE METRICS")
print("=" * 80)


# ============================================================
# CHECK INPUT
# ============================================================

print("\nChecking input file...")

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found:\n{INPUT_FILE}"
    )

print(f"OK  {INPUT_FILE}")


# ============================================================
# LOAD DATA
# ============================================================

print("\n" + "=" * 80)
print("[1/8] LOADING ALL-ACO PROVIDER-SERVICE DATA")
print("=" * 80)

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(f"Input rows       : {len(df):,}")
print(f"Input columns    : {len(df.columns):,}")
print(f"Unique ACOs      : {df['ACO_ID'].nunique():,}")
print(f"Unique providers : {df['Rndrng_NPI'].nunique():,}")
print(
    f"Years            : "
    f"{sorted(df['Year'].dropna().unique())}"
)
print(f"HCPCS codes      : {df['HCPCS_Cd'].nunique():,}")


# ============================================================
# REQUIRED COLUMNS
# ============================================================

print("\n" + "=" * 80)
print("[2/8] VALIDATING REQUIRED COLUMNS")
print("=" * 80)

required_columns = [
    "ACO_ID",
    "Rndrng_NPI",
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
    "service_mix_pct",
    "payment_mix_pct",
    "service_volume_rank",
    "service_cost_rank",
    "service_utilization_rank",
    "top_volume_service",
    "top_cost_service",
    "top_utilization_service",
    "provider_service_segment",
    "service_volume_change_pct",
    "payment_change_pct",
    "utilization_change_pct",
]

missing_columns = [
    c for c in required_columns
    if c not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

print(
    f"PASS - All {len(required_columns)} required "
    "columns are present."
)


# ============================================================
# CLEAN KEYS
# ============================================================

print("\n" + "=" * 80)
print("[3/8] CLEANING KEY FIELDS")
print("=" * 80)

df["ACO_ID"] = (
    df["ACO_ID"]
    .astype(str)
    .str.strip()
)

df["Rndrng_NPI"] = (
    df["Rndrng_NPI"]
    .astype(str)
    .str.strip()
)

df["HCPCS_Cd"] = (
    df["HCPCS_Cd"]
    .astype(str)
    .str.strip()
)

df["Year"] = pd.to_numeric(
    df["Year"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "ACO_ID",
        "Rndrng_NPI",
        "Year",
        "HCPCS_Cd"
    ]
)

print(f"ACOs  : {df['ACO_ID'].nunique():,}")
print(
    f"Years : "
    f"{sorted(df['Year'].unique())}"
)
print(
    f"HCPCS : {df['HCPCS_Cd'].nunique():,}"
)


# ============================================================
# PROVIDER-SERVICE GRAIN
# ============================================================

print("\n" + "=" * 80)
print("[4/8] VALIDATING PROVIDER-SERVICE GRAIN")
print("=" * 80)

duplicate_count = (
    df
    .duplicated(
        subset=[
            "ACO_ID",
            "Rndrng_NPI",
            "Year",
            "HCPCS_Cd"
        ]
    )
    .sum()
)

print(
    f"Duplicate ACO-NPI-Year-HCPCS rows: "
    f"{duplicate_count:,}"
)

if duplicate_count != 0:
    raise ValueError(
        "Duplicate ACO-NPI-Year-HCPCS rows detected."
    )

print(
    "PASS - Provider-service grain is unique."
)


# ============================================================
# ACO-YEAR COVERAGE
# ============================================================

print("\n" + "=" * 80)
print("[5/8] VALIDATING ALL-ACO COVERAGE")
print("=" * 80)

aco_count = df["ACO_ID"].nunique()

years = sorted(
    df["Year"].unique()
)

year_count = len(years)

expected_aco_years = (
    aco_count * year_count
)

actual_aco_years = (
    df
    .groupby(
        ["ACO_ID", "Year"]
    )
    .ngroups
)

print(
    f"ACOs              : {aco_count:,}"
)

print(
    f"Years             : {year_count:,}"
)

print(
    f"Expected ACO-years: {expected_aco_years:,}"
)

print(
    f"Actual ACO-years  : {actual_aco_years:,}"
)

if actual_aco_years != expected_aco_years:
    raise ValueError(
        "Not every ACO-year combination is represented."
    )

print(
    "PASS - Every ACO-year is represented."
)


# ============================================================
# PROVIDER STRUCTURE
# ============================================================

print("\n" + "=" * 80)
print("[6/8] VALIDATING PROVIDER-SERVICE STRUCTURE")
print("=" * 80)


# ------------------------------------------------------------
# Providers per ACO-year
# ------------------------------------------------------------

providers_per_aco_year = (
    df
    .groupby(
        ["ACO_ID", "Year"]
    )["Rndrng_NPI"]
    .nunique()
)

print("\nProviders per ACO-year:")

print(
    providers_per_aco_year
    .value_counts()
    .sort_index()
)


invalid_provider_counts = (
    providers_per_aco_year[
        providers_per_aco_year != 5
    ]
)

if len(invalid_provider_counts) > 0:

    print("\nInvalid ACO-years:")

    print(
        invalid_provider_counts
        .head(20)
        .to_string()
    )

    raise ValueError(
        "Some ACO-years do not have exactly "
        "5 selected providers."
    )

print(
    "\nPASS - Every ACO-year has exactly "
    "5 providers."
)


# ------------------------------------------------------------
# SERVICES PER PROVIDER-YEAR
# ------------------------------------------------------------

services_per_provider_year = (
    df
    .groupby(
        [
            "ACO_ID",
            "Rndrng_NPI",
            "Year"
        ]
    )["HCPCS_Cd"]
    .nunique()
)

print("\nServices per provider-year:")

print(
    services_per_provider_year
    .value_counts()
    .sort_index()
)


service_counts = (
    services_per_provider_year
    .unique()
)

if len(service_counts) != 1:

    raise ValueError(
        "Service count is inconsistent across "
        "provider-year combinations."
    )

services_per_provider = int(
    service_counts[0]
)

print(
    f"\nServices per provider-year: "
    f"{services_per_provider}"
)


# ------------------------------------------------------------
# ROWS PER ACO-YEAR
# ------------------------------------------------------------

rows_per_aco_year = (
    df
    .groupby(
        ["ACO_ID", "Year"]
    )
    .size()
)

expected_rows_per_aco_year = (
    5 * services_per_provider
)

print("\nRows per ACO-year:")

print(
    rows_per_aco_year
    .describe()
)

print(
    f"\nSelected providers per ACO-year: 5"
)

print(
    f"Services per provider-year: "
    f"{services_per_provider}"
)

print(
    f"Expected rows per ACO-year: "
    f"{expected_rows_per_aco_year}"
)


invalid_rows = (
    rows_per_aco_year[
        rows_per_aco_year != expected_rows_per_aco_year
    ]
)

if len(invalid_rows) > 0:

    print("\nInvalid ACO-years:")

    print(
        invalid_rows
        .head(20)
        .to_string()
    )

    raise ValueError(
        "Provider-service structure is inconsistent."
    )

print(
    "\nPASS - Provider-service structure is valid."
)


# ============================================================
# BUILD SERVICE METRICS
# ============================================================

print("\n" + "=" * 80)
print("[7/8] BUILDING ALL-ACO SERVICE METRICS")
print("=" * 80)


# ------------------------------------------------------------
# Service-level aggregation
# ------------------------------------------------------------

service_metrics = (
    df
    .groupby(
        [
            "ACO_ID",
            "Year",
            "HCPCS_Cd"
        ],
        as_index=False
    )
    .agg(
        HCPCS_Desc=(
            "HCPCS_Desc",
            "first"
        ),
        providers=(
            "Rndrng_NPI",
            "nunique"
        ),
        beneficiaries=(
            "Tot_Benes",
            "sum"
        ),
        services=(
            "Tot_Srvcs",
            "sum"
        ),
        avg_submitted_charge=(
            "Avg_Sbmtd_Chrg",
            "mean"
        ),
        avg_medicare_allowed=(
            "Avg_Mdcr_Alowd_Amt",
            "mean"
        ),
        avg_medicare_payment=(
            "Avg_Mdcr_Pymt_Amt",
            "mean"
        ),
        avg_standardized_payment=(
            "Avg_Mdcr_Stdzd_Amt",
            "mean"
        ),
    )
)


# ------------------------------------------------------------
# Derived service metrics
# ------------------------------------------------------------

service_metrics[
    "payment_per_service"
] = (
    service_metrics[
        "avg_medicare_payment"
    ]
    /
    service_metrics[
        "services"
    ].replace(0, pd.NA)
)

service_metrics[
    "payment_per_beneficiary"
] = (
    service_metrics[
        "avg_medicare_payment"
    ]
    /
    service_metrics[
        "beneficiaries"
    ].replace(0, pd.NA)
)


# ------------------------------------------------------------
# Service volume share
# ------------------------------------------------------------

total_services = (
    service_metrics
    .groupby(
        ["ACO_ID", "Year"]
    )["services"]
    .transform("sum")
)

service_metrics[
    "service_volume_pct"
] = (
    service_metrics["services"]
    /
    total_services.replace(0, pd.NA)
    * 100
)


# ------------------------------------------------------------
# Service payment share
# ------------------------------------------------------------

payment_total = (
    service_metrics
    .groupby(
        ["ACO_ID", "Year"]
    )["avg_medicare_payment"]
    .transform("sum")
)

service_metrics[
    "payment_mix_pct"
] = (
    service_metrics[
        "avg_medicare_payment"
    ]
    /
    payment_total.replace(0, pd.NA)
    * 100
)


# ------------------------------------------------------------
# Rankings
# ------------------------------------------------------------

service_metrics[
    "service_volume_rank"
] = (
    service_metrics
    .groupby(
        ["ACO_ID", "Year"]
    )["services"]
    .rank(
        ascending=False,
        method="dense"
    )
)

service_metrics[
    "service_payment_rank"
] = (
    service_metrics
    .groupby(
        ["ACO_ID", "Year"]
    )["avg_medicare_payment"]
    .rank(
        ascending=False,
        method="dense"
    )
)


# ------------------------------------------------------------
# Top service flags
# ------------------------------------------------------------

service_metrics[
    "top_volume_service"
] = (
    service_metrics[
        "service_volume_rank"
    ] == 1
)

service_metrics[
    "top_payment_service"
] = (
    service_metrics[
        "service_payment_rank"
    ] == 1
)


# ------------------------------------------------------------
# Sort
# ------------------------------------------------------------

service_metrics = (
    service_metrics
    .sort_values(
        [
            "ACO_ID",
            "Year",
            "service_volume_rank",
            "HCPCS_Cd"
        ]
    )
    .reset_index(drop=True)
)


# ============================================================
# FINAL VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("[8/8] FINAL VALIDATION")
print("=" * 80)

print(
    f"Output rows       : "
    f"{len(service_metrics):,}"
)

print(
    f"Output ACOs       : "
    f"{service_metrics['ACO_ID'].nunique():,}"
)

print(
    f"Output years      : "
    f"{sorted(service_metrics['Year'].unique())}"
)

print(
    f"Output HCPCS      : "
    f"{service_metrics['HCPCS_Cd'].nunique():,}"
)


# ------------------------------------------------------------
# ACO coverage
# ------------------------------------------------------------

if (
    service_metrics["ACO_ID"].nunique()
    != aco_count
):

    raise ValueError(
        "Not all ACOs survived service aggregation."
    )


# ------------------------------------------------------------
# ACO-year coverage
# ------------------------------------------------------------

final_aco_years = (
    service_metrics
    .groupby(
        ["ACO_ID", "Year"]
    )
    .ngroups
)

if final_aco_years != expected_aco_years:

    raise ValueError(
        "Not all ACO-year combinations survived."
    )


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

service_metrics.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 80)
print("OUTPUT")
print("=" * 80)

print(
    f"File : {OUTPUT_FILE}"
)

print(
    f"Rows : {len(service_metrics):,}"
)

print(
    f"ACOs : "
    f"{service_metrics['ACO_ID'].nunique():,}"
)

print(
    f"Years: "
    f"{len(service_metrics['Year'].unique())}"
)

print(
    f"HCPCS: "
    f"{service_metrics['HCPCS_Cd'].nunique():,}"
)

print("\n" + "=" * 80)
print("BUILD COMPLETE")
print("=" * 80)

print(
    "PASS - All ACOs preserved."
)

print(
    "PASS - All years preserved."
)

print(
    "PASS - Exactly 5 providers per ACO-year."
)

print(
    f"PASS - {services_per_provider} services "
    "per provider-year."
)

print(
    f"PASS - {expected_rows_per_aco_year} "
    "service rows per ACO-year."
)

print(
    "PASS - Original serving data untouched."
)

print("=" * 80)