from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "all_aco"
    / "all_aco_service_metrics.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "all_aco"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "aco_service_analysis.csv"
)


# ============================================================
# START
# ============================================================

print("=" * 80)
print("BHAVYA VBC")
print("=" * 80)
print("ALL-ACO ACO-LEVEL SERVICE ANALYSIS")
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
# LOAD
# ============================================================

print("\n" + "=" * 80)
print("[1/8] LOADING ALL-ACO SERVICE METRICS")
print("=" * 80)

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(f"Input rows       : {len(df):,}")
print(f"Input columns    : {len(df.columns):,}")


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "ACO_ID",
    "Year",
    "HCPCS_Cd",
    "HCPCS_Desc",
    "providers",
    "beneficiaries",
    "services",
    "avg_submitted_charge",
    "avg_medicare_allowed",
    "avg_medicare_payment",
    "avg_standardized_payment",
    "payment_per_service",
    "payment_per_beneficiary",
    "service_volume_pct",
    "payment_mix_pct",
    "service_volume_rank",
    "service_payment_rank",
    "top_volume_service",
    "top_payment_service",
]


print("\n" + "=" * 80)
print("[2/8] VALIDATING REQUIRED COLUMNS")
print("=" * 80)

missing_columns = [
    col
    for col in required_columns
    if col not in df.columns
]

if missing_columns:

    print("Missing columns:")

    for col in missing_columns:
        print(f"  - {col}")

    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

print(
    f"PASS - All {len(required_columns)} required columns are present."
)


# ============================================================
# CLEAN KEY FIELDS
# ============================================================

print("\n" + "=" * 80)
print("[3/8] CLEANING KEY FIELDS")
print("=" * 80)


df["ACO_ID"] = (
    df["ACO_ID"]
    .astype(str)
    .str.strip()
)

df["Year"] = pd.to_numeric(
    df["Year"],
    errors="coerce"
)

df["HCPCS_Cd"] = (
    df["HCPCS_Cd"]
    .astype(str)
    .str.strip()
)

df["HCPCS_Desc"] = (
    df["HCPCS_Desc"]
    .fillna("")
    .astype(str)
    .str.strip()
)


numeric_columns = [
    "providers",
    "beneficiaries",
    "services",
    "avg_submitted_charge",
    "avg_medicare_allowed",
    "avg_medicare_payment",
    "avg_standardized_payment",
    "payment_per_service",
    "payment_per_beneficiary",
    "service_volume_pct",
    "payment_mix_pct",
    "service_volume_rank",
    "service_payment_rank",
]

for col in numeric_columns:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


df = df[
    df["ACO_ID"].notna()
    & df["Year"].notna()
    & df["HCPCS_Cd"].notna()
].copy()


df["Year"] = df["Year"].astype(int)


print(
    f"ACOs  : {df['ACO_ID'].nunique():,}"
)

print(
    f"Years : {sorted(df['Year'].unique().tolist())}"
)

print(
    f"HCPCS : {df['HCPCS_Cd'].nunique():,}"
)


# ============================================================
# VALIDATE SERVICE GRAIN
# ============================================================

print("\n" + "=" * 80)
print("[4/8] VALIDATING SERVICE GRAIN")
print("=" * 80)


duplicate_service_rows = (
    df
    .duplicated(
        [
            "ACO_ID",
            "Year",
            "HCPCS_Cd"
        ]
    )
    .sum()
)


print(
    f"Duplicate ACO-Year-HCPCS rows: "
    f"{duplicate_service_rows:,}"
)


if duplicate_service_rows != 0:

    raise ValueError(
        "Duplicate ACO-Year-HCPCS rows detected."
    )


print(
    "PASS - ACO-Year-HCPCS grain is unique."
)


# ============================================================
# VALIDATE ACO-YEAR COVERAGE
# ============================================================

print("\n" + "=" * 80)
print("[5/8] VALIDATING ALL-ACO COVERAGE")
print("=" * 80)


aco_count = df["ACO_ID"].nunique()

year_count = df["Year"].nunique()

expected_aco_years = (
    aco_count *
    year_count
)


actual_aco_years = (
    df[
        [
            "ACO_ID",
            "Year"
        ]
    ]
    .drop_duplicates()
    .shape[0]
)


print(
    f"ACOs               : {aco_count:,}"
)

print(
    f"Years              : {year_count:,}"
)

print(
    f"Expected ACO-years : {expected_aco_years:,}"
)

print(
    f"Actual ACO-years   : {actual_aco_years:,}"
)


if actual_aco_years != expected_aco_years:

    raise ValueError(
        "Not every ACO-year combination is represented."
    )


print(
    "PASS - Every ACO-year is represented."
)


# ============================================================
# SERVICE COVERAGE
# ============================================================

print("\n" + "=" * 80)
print("[6/8] VALIDATING SERVICE COVERAGE")
print("=" * 80)


services_per_aco_year = (
    df
    .groupby(
        [
            "ACO_ID",
            "Year"
        ]
    )[
        "HCPCS_Cd"
    ]
    .nunique()
)


print("\nServices per ACO-year:")

print(
    services_per_aco_year.value_counts()
    .sort_index()
)


print("\nService coverage summary:")

print(
    services_per_aco_year.describe()
)


minimum_services = (
    services_per_aco_year.min()
)

maximum_services = (
    services_per_aco_year.max()
)


print(
    f"\nMinimum services per ACO-year: "
    f"{minimum_services}"
)

print(
    f"Maximum services per ACO-year: "
    f"{maximum_services}"
)


# IMPORTANT:
#
# We DO NOT require exactly 5 services.
#
# The current service universe contains 15 HCPCS codes,
# but not every ACO-year necessarily has all 15 represented.
#
# Therefore variable service coverage is valid.
#
# We only require:
#
# 1. Every ACO-year exists.
# 2. Every ACO-year has at least one service.
# 3. No duplicate ACO-Year-HCPCS rows.


if minimum_services < 1:

    raise ValueError(
        "At least one service is required for every ACO-year."
    )


print(
    "\nPASS - Variable service coverage is valid."
)

print(
    "PASS - No artificial 5-service requirement applied."
)


# ============================================================
# BUILD ACO SERVICE ANALYSIS
# ============================================================

print("\n" + "=" * 80)
print("[7/8] BUILDING ACO-LEVEL SERVICE ANALYSIS")
print("=" * 80)


# ------------------------------------------------------------
# Provider count
# ------------------------------------------------------------

# The input service metrics are already aggregated at
# ACO-Year-HCPCS level and contain provider counts.

# Keep the service-level structure while creating
# clean ACO-level analytical fields.


analysis = df.copy()


# ------------------------------------------------------------
# Service ranking within ACO-year
# ------------------------------------------------------------

analysis["service_volume_rank"] = (
    analysis
    .groupby(
        [
            "ACO_ID",
            "Year"
        ]
    )["services"]
    .rank(
        method="dense",
        ascending=False
    )
)


analysis["service_payment_rank"] = (
    analysis
    .groupby(
        [
            "ACO_ID",
            "Year"
        ]
    )["avg_medicare_payment"]
    .rank(
        method="dense",
        ascending=False
    )
)


# ------------------------------------------------------------
# Top service flags
# ------------------------------------------------------------

analysis["top_volume_service"] = (
    analysis["service_volume_rank"] == 1
)


analysis["top_payment_service"] = (
    analysis["service_payment_rank"] == 1
)


# ------------------------------------------------------------
# ACO total services
# ------------------------------------------------------------

aco_year_total_services = (
    analysis
    .groupby(
        [
            "ACO_ID",
            "Year"
        ]
    )["services"]
    .transform("sum")
)


analysis["aco_total_services"] = (
    aco_year_total_services
)


# ------------------------------------------------------------
# ACO total beneficiaries
# ------------------------------------------------------------

aco_year_total_beneficiaries = (
    analysis
    .groupby(
        [
            "ACO_ID",
            "Year"
        ]
    )["beneficiaries"]
    .transform("sum")
)


analysis["aco_total_beneficiaries"] = (
    aco_year_total_beneficiaries
)


# ------------------------------------------------------------
# Service share validation
# ------------------------------------------------------------

analysis["calculated_service_volume_pct"] = np.where(
    analysis["aco_total_services"] > 0,
    (
        analysis["services"]
        /
        analysis["aco_total_services"]
        *
        100
    ),
    0
)


# ------------------------------------------------------------
# ACO service payment
# ------------------------------------------------------------

analysis["service_total_payment"] = (
    analysis["services"]
    *
    analysis["avg_medicare_payment"]
)


analysis["service_total_standardized_payment"] = (
    analysis["services"]
    *
    analysis["avg_standardized_payment"]
)


# ------------------------------------------------------------
# ACO payment total
# ------------------------------------------------------------

aco_total_payment = (
    analysis
    .groupby(
        [
            "ACO_ID",
            "Year"
        ]
    )["service_total_payment"]
    .transform("sum")
)


analysis["aco_total_payment"] = (
    aco_total_payment
)


# ------------------------------------------------------------
# Payment contribution
# ------------------------------------------------------------

analysis["calculated_payment_mix_pct"] = np.where(
    analysis["aco_total_payment"] > 0,
    (
        analysis["service_total_payment"]
        /
        analysis["aco_total_payment"]
        *
        100
    ),
    0
)


# ------------------------------------------------------------
# Service intensity
# ------------------------------------------------------------

analysis["services_per_provider"] = np.where(
    analysis["providers"] > 0,
    analysis["services"]
    /
    analysis["providers"],
    0
)


# ------------------------------------------------------------
# Cost per service
# ------------------------------------------------------------

analysis["cost_per_service"] = (
    analysis["avg_medicare_payment"]
)


# ------------------------------------------------------------
# Standardized payment difference
# ------------------------------------------------------------

analysis["standardized_payment_difference"] = (
    analysis["avg_medicare_payment"]
    -
    analysis["avg_standardized_payment"]
)


# ------------------------------------------------------------
# Year-over-year service change
# ------------------------------------------------------------

analysis = analysis.sort_values(
    [
        "ACO_ID",
        "HCPCS_Cd",
        "Year"
    ]
).reset_index(drop=True)


analysis["service_volume_change_pct"] = (
    analysis
    .groupby(
        [
            "ACO_ID",
            "HCPCS_Cd"
        ]
    )["services"]
    .pct_change()
    * 100
)


analysis["payment_change_pct"] = (
    analysis
    .groupby(
        [
            "ACO_ID",
            "HCPCS_Cd"
        ]
    )["avg_medicare_payment"]
    .pct_change()
    * 100
)


# ------------------------------------------------------------
# Restore deterministic order
# ------------------------------------------------------------

analysis = analysis.sort_values(
    [
        "ACO_ID",
        "Year",
        "service_volume_rank",
        "HCPCS_Cd"
    ]
).reset_index(drop=True)


# ============================================================
# FINAL COLUMN ORDER
# ============================================================

final_columns = [
    "ACO_ID",
    "Year",
    "HCPCS_Cd",
    "HCPCS_Desc",

    "providers",
    "beneficiaries",
    "services",

    "avg_submitted_charge",
    "avg_medicare_allowed",
    "avg_medicare_payment",
    "avg_standardized_payment",

    "payment_per_service",
    "payment_per_beneficiary",

    "service_volume_pct",
    "payment_mix_pct",

    "service_volume_rank",
    "service_payment_rank",

    "top_volume_service",
    "top_payment_service",

    "aco_total_services",
    "aco_total_beneficiaries",
    "aco_total_payment",

    "calculated_service_volume_pct",
    "calculated_payment_mix_pct",

    "services_per_provider",
    "cost_per_service",
    "standardized_payment_difference",

    "service_volume_change_pct",
    "payment_change_pct",
]


analysis = analysis[
    final_columns
].copy()


# ============================================================
# FINAL VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("[8/8] FINAL VALIDATION")
print("=" * 80)


final_duplicate_count = (
    analysis
    .duplicated(
        [
            "ACO_ID",
            "Year",
            "HCPCS_Cd"
        ]
    )
    .sum()
)


final_aco_count = (
    analysis["ACO_ID"].nunique()
)


final_year_count = (
    analysis["Year"].nunique()
)


final_service_count = (
    analysis["HCPCS_Cd"].nunique()
)


final_aco_year_count = (
    analysis[
        [
            "ACO_ID",
            "Year"
        ]
    ]
    .drop_duplicates()
    .shape[0]
)


print(
    f"Output rows       : {len(analysis):,}"
)

print(
    f"Output ACOs       : {final_aco_count:,}"
)

print(
    f"Output years      : "
    f"{sorted(analysis['Year'].unique().tolist())}"
)

print(
    f"Output HCPCS      : {final_service_count:,}"
)

print(
    f"Output ACO-years  : {final_aco_year_count:,}"
)

print(
    f"Duplicate rows    : {final_duplicate_count:,}"
)


# ------------------------------------------------------------
# Hard validation
# ------------------------------------------------------------

if final_duplicate_count != 0:

    raise ValueError(
        "Duplicate ACO-Year-HCPCS rows detected in final dataset."
    )


if final_aco_count != aco_count:

    raise ValueError(
        "Not all ACOs are preserved."
    )


if final_aco_year_count != expected_aco_years:

    raise ValueError(
        "Not all ACO-year combinations are preserved."
    )


if final_service_count == 0:

    raise ValueError(
        "No services remain in final dataset."
    )


# ============================================================
# SAVE
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


analysis.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("OUTPUT")
print("=" * 80)

print(
    f"File : {OUTPUT_FILE}"
)

print(
    f"Rows : {len(analysis):,}"
)

print(
    f"ACOs : {final_aco_count:,}"
)

print(
    f"Years: {final_year_count}"
)

print(
    f"HCPCS: {final_service_count:,}"
)

print(
    f"ACO-years: {final_aco_year_count:,}"
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
    "PASS - ACO-Year-HCPCS grain preserved."
)

print(
    "PASS - Variable service coverage supported."
)

print(
    "PASS - No artificial 5-service requirement."
)

print(
    "PASS - Original serving data untouched."
)

print("=" * 80)