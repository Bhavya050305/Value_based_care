from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# BHAVYA VBC
# FINAL PROVIDER + SERVICE DATA QUALITY AUDIT
# ============================================================
#
# Purpose:
# Perform the final quality check on all dashboard-facing
# provider/service analytical datasets before database upload.
#
# This script:
#   1. Checks files exist
#   2. Loads all final datasets
#   3. Checks row counts
#   4. Checks required columns
#   5. Checks duplicate analytical grains
#   6. Checks critical missing values
#   7. Checks numeric validity
#   8. Checks relationships between datasets
#   9. Checks ACO/year coverage
#  10. Checks provider/service consistency
#  11. Produces an audit report
#
# IMPORTANT:
# This script DOES NOT modify any existing CSV.
# ============================================================


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

DATA_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "provider_service"
)

PROVIDER_FILE = (
    DATA_DIR / "provider_dashboard_analytics.csv"
)

ACO_PROVIDER_FILE = (
    DATA_DIR / "aco_provider_metrics.csv"
)

SERVICE_FILE = (
    DATA_DIR / "service_metrics.csv"
)

PROVIDER_SERVICE_FILE = (
    DATA_DIR / "provider_service_metrics.csv"
)

DRIVER_FILE = (
    DATA_DIR / "performance_drivers.csv"
)

REPORT_FILE = (
    DATA_DIR / "provider_service_final_audit_report.txt"
)


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

audit_results = []


def record(
    check,
    status,
    details=""
):
    """Store and print one audit result."""

    audit_results.append({
        "check": check,
        "status": status,
        "details": details
    })

    symbol = {
        "PASS": "PASS",
        "WARN": "WARN",
        "FAIL": "FAIL"
    }.get(status, status)

    print(
        f"[{symbol}] {check}"
    )

    if details:
        print(
            f"       {details}"
        )


def section(title):

    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def check_file(path, name):

    if path.exists():

        record(
            f"{name} exists",
            "PASS",
            str(path)
        )

        return True

    record(
        f"{name} exists",
        "FAIL",
        f"Missing: {path}"
    )

    return False


def check_columns(
    df,
    required,
    dataset_name
):

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:

        record(
            f"{dataset_name} required columns",
            "FAIL",
            f"Missing: {missing}"
        )

        return False

    record(
        f"{dataset_name} required columns",
        "PASS",
        f"{len(required)} required columns present"
    )

    return True


def check_duplicates(
    df,
    keys,
    name
):

    duplicates = df.duplicated(
        subset=keys
    ).sum()

    if duplicates == 0:

        record(
            f"{name} grain",
            "PASS",
            f"Unique at {keys}"
        )

        return True

    record(
        f"{name} grain",
        "FAIL",
        f"{duplicates:,} duplicate rows at {keys}"
    )

    return False


def check_missing(
    df,
    columns,
    name
):

    missing = (
        df[columns]
        .isna()
        .sum()
    )

    total_missing = int(
        missing.sum()
    )

    if total_missing == 0:

        record(
            f"{name} critical missing values",
            "PASS",
            "No missing values"
        )

        return True

    nonzero = (
        missing[
            missing > 0
        ]
        .to_dict()
    )

    record(
        f"{name} critical missing values",
        "WARN",
        str(nonzero)
    )

    return False


def check_numeric_finite(
    df,
    columns,
    name
):

    problems = {}

    for column in columns:

        if column not in df.columns:
            continue

        values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        non_finite = (
            ~np.isfinite(
                values.dropna()
            )
        ).sum()

        if non_finite > 0:

            problems[column] = (
                int(non_finite)
            )

    if not problems:

        record(
            f"{name} numeric validity",
            "PASS",
            "No infinite numeric values"
        )

        return True

    record(
        f"{name} numeric validity",
        "FAIL",
        str(problems)
    )

    return False


# ============================================================
# 3. LOAD DATA
# ============================================================

section(
    "1. CHECKING FINAL DATASET FILES"
)

paths = [
    (
        PROVIDER_FILE,
        "provider_dashboard_analytics"
    ),
    (
        ACO_PROVIDER_FILE,
        "aco_provider_metrics"
    ),
    (
        SERVICE_FILE,
        "service_metrics"
    ),
    (
        PROVIDER_SERVICE_FILE,
        "provider_service_metrics"
    ),
    (
        DRIVER_FILE,
        "performance_drivers"
    )
]

all_files_exist = True

for path, name in paths:

    if not check_file(
        path,
        name
    ):
        all_files_exist = False


if not all_files_exist:

    raise FileNotFoundError(
        "One or more required datasets are missing."
    )


section(
    "2. LOADING FINAL DATASETS"
)

provider = pd.read_csv(
    PROVIDER_FILE,
    low_memory=False
)

aco_provider = pd.read_csv(
    ACO_PROVIDER_FILE,
    low_memory=False
)

service = pd.read_csv(
    SERVICE_FILE,
    low_memory=False
)

provider_service = pd.read_csv(
    PROVIDER_SERVICE_FILE,
    low_memory=False
)

drivers = pd.read_csv(
    DRIVER_FILE,
    low_memory=False
)

print(
    f"Provider dashboard:       {len(provider):,} rows"
)

print(
    f"ACO provider metrics:      {len(aco_provider):,} rows"
)

print(
    f"Service metrics:            {len(service):,} rows"
)

print(
    f"Provider-service metrics: {len(provider_service):,} rows"
)

print(
    f"Performance drivers:       {len(drivers):,} rows"
)


# ============================================================
# 4. REQUIRED COLUMNS
# ============================================================

section(
    "3. REQUIRED COLUMN VALIDATION"
)


check_columns(
    provider,
    [
        "Rndrng_NPI",
        "Year",
        "ACO_ID",
        "cost_score",
        "utilization_score",
        "provider_segment",
        "high_cost_flag",
        "high_utilization_flag"
    ],
    "provider_dashboard_analytics"
)


check_columns(
    aco_provider,
    [
        "ACO_ID",
        "Year",
        "provider_count",
        "avg_payment_per_service",
        "avg_payment_per_beneficiary",
        "avg_utilization_score",
        "avg_cost_score"
    ],
    "aco_provider_metrics"
)


check_columns(
    service,
    [
        "ACO_ID",
        "Year",
        "HCPCS_Cd",
        "HCPCS_Desc",
        "service_category",
        "service_volume",
        "total_payment",
        "payment_change_pct",
        "utilization_change_pct"
    ],
    "service_metrics"
)


check_columns(
    provider_service,
    [
        "Rndrng_NPI",
        "Year",
        "ACO_ID",
        "HCPCS_Cd",
        "Tot_Srvcs",
        "payment_per_service",
        "utilization_rate"
    ],
    "provider_service_metrics"
)


check_columns(
    drivers,
    [
        "ACO_ID",
        "Year",
        "driver_type",
        "driver_name",
        "metric_name",
        "metric_value",
        "driver_score",
        "driver_rank",
        "driver_severity"
    ],
    "performance_drivers"
)


# ============================================================
# 5. GRAIN CHECKS
# ============================================================

section(
    "4. ANALYTICAL GRAIN VALIDATION"
)


check_duplicates(
    provider,
    [
        "Rndrng_NPI",
        "Year"
    ],
    "Provider dashboard"
)


check_duplicates(
    aco_provider,
    [
        "ACO_ID",
        "Year"
    ],
    "ACO provider metrics"
)


check_duplicates(
    service,
    [
        "ACO_ID",
        "Year",
        "HCPCS_Cd"
    ],
    "Service metrics"
)


check_duplicates(
    provider_service,
    [
        "Rndrng_NPI",
        "Year",
        "HCPCS_Cd"
    ],
    "Provider-service metrics"
)


check_duplicates(
    drivers,
    [
        "ACO_ID",
        "Year",
        "driver_type",
        "driver_rank"
    ],
    "Performance drivers"
)


# ============================================================
# 6. CRITICAL MISSING VALUES
# ============================================================

section(
    "5. CRITICAL MISSING VALUE CHECK"
)


check_missing(
    provider,
    [
        "Rndrng_NPI",
        "Year",
        "ACO_ID",
        "cost_score",
        "utilization_score"
    ],
    "Provider dashboard"
)


check_missing(
    aco_provider,
    [
        "ACO_ID",
        "Year",
        "provider_count"
    ],
    "ACO provider metrics"
)


check_missing(
    service,
    [
        "ACO_ID",
        "Year",
        "HCPCS_Cd",
        "service_category",
        "service_volume",
        "total_payment"
    ],
    "Service metrics"
)


check_missing(
    provider_service,
    [
        "Rndrng_NPI",
        "Year",
        "ACO_ID",
        "HCPCS_Cd"
    ],
    "Provider-service metrics"
)


check_missing(
    drivers,
    [
        "ACO_ID",
        "Year",
        "driver_type",
        "driver_name"
    ],
    "Performance drivers"
)


# ============================================================
# 7. NUMERIC VALIDATION
# ============================================================

section(
    "6. NUMERIC VALIDATION"
)


check_numeric_finite(
    provider,
    [
        "cost_score",
        "utilization_score",
        "payment_per_service",
        "payment_per_beneficiary"
    ],
    "Provider dashboard"
)


check_numeric_finite(
    aco_provider,
    [
        "provider_count",
        "avg_payment_per_service",
        "avg_payment_per_beneficiary",
        "avg_cost_score",
        "avg_utilization_score"
    ],
    "ACO provider metrics"
)


check_numeric_finite(
    service,
    [
        "service_volume",
        "total_payment",
        "avg_payment",
        "avg_utilization_rate",
        "payment_change_pct",
        "utilization_change_pct"
    ],
    "Service metrics"
)


check_numeric_finite(
    provider_service,
    [
        "Tot_Srvcs",
        "payment_per_service",
        "utilization_rate",
        "service_mix_pct",
        "payment_mix_pct"
    ],
    "Provider-service metrics"
)


check_numeric_finite(
    drivers,
    [
        "metric_value",
        "change_pct",
        "contribution_pct",
        "driver_score"
    ],
    "Performance drivers"
)


# ============================================================
# 8. NON-NEGATIVE CORE METRICS
# ============================================================

section(
    "7. NON-NEGATIVE CORE METRIC CHECK"
)


non_negative_checks = [
    (
        provider,
        "payment_per_service",
        "Provider payment per service"
    ),
    (
        provider,
        "payment_per_beneficiary",
        "Provider payment per beneficiary"
    ),
    (
        provider,
        "cost_score",
        "Provider cost score"
    ),
    (
        provider,
        "utilization_score",
        "Provider utilization score"
    ),
    (
        service,
        "service_volume",
        "Service volume"
    ),
    (
        service,
        "total_payment",
        "Service total payment"
    ),
    (
        provider_service,
        "Tot_Srvcs",
        "Provider-service volume"
    ),
    (
        provider_service,
        "payment_per_service",
        "Provider-service payment per service"
    ),
    (
        drivers,
        "driver_score",
        "Performance driver score"
    )
]


for df, column, name in non_negative_checks:

    if column not in df.columns:
        continue

    values = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    negative_count = (
        values < 0
    ).sum()

    if negative_count == 0:

        record(
            name,
            "PASS",
            "No negative values"
        )

    else:

        record(
            name,
            "FAIL",
            f"{negative_count:,} negative values"
        )


# ============================================================
# 9. ACO / YEAR COVERAGE
# ============================================================

section(
    "8. ACO AND YEAR COVERAGE"
)


datasets = {
    "provider_dashboard": provider,
    "aco_provider_metrics": aco_provider,
    "service_metrics": service,
    "provider_service_metrics": provider_service,
    "performance_drivers": drivers
}


coverage = {}

for name, df in datasets.items():

    acos = set(
        df["ACO_ID"]
        .dropna()
        .astype(str)
    )

    years = set(
        pd.to_numeric(
            df["Year"],
            errors="coerce"
        )
        .dropna()
        .astype(int)
    )

    coverage[name] = {
        "acos": acos,
        "years": years
    }

    print(
        f"{name}:"
    )

    print(
        f"  ACOs: {len(acos)}"
    )

    print(
        f"  Years: {sorted(years)}"
    )


base_name = (
    "service_metrics"
)

base_acos = coverage[
    base_name
]["acos"]

base_years = coverage[
    base_name
]["years"]


for name, values in coverage.items():

    missing_acos = (
        base_acos
        - values["acos"]
    )

    missing_years = (
        base_years
        - values["years"]
    )

    if not missing_acos and not missing_years:

        record(
            f"{name} coverage",
            "PASS",
            "Contains all ACOs and years from service metrics"
        )

    else:

        record(
            f"{name} coverage",
            "WARN",
            f"Missing ACOs={missing_acos}, "
            f"Missing years={missing_years}"
        )


# ============================================================
# 10. PROVIDER → ACO CONSISTENCY
# ============================================================

section(
    "9. PROVIDER TO ACO CONSISTENCY"
)


provider_pairs = (
    provider[
        [
            "Rndrng_NPI",
            "Year",
            "ACO_ID"
        ]
    ]
    .drop_duplicates()
)

provider_service_pairs = (
    provider_service[
        [
            "Rndrng_NPI",
            "Year",
            "ACO_ID"
        ]
    ]
    .drop_duplicates()
)


merged = provider_service_pairs.merge(
    provider_pairs,
    on=[
        "Rndrng_NPI",
        "Year"
    ],
    how="left",
    suffixes=(
        "_service",
        "_provider"
    )
)


missing_provider_mapping = (
    merged["ACO_ID_provider"]
    .isna()
    .sum()
)

if missing_provider_mapping == 0:

    record(
        "Provider-service provider→ACO mapping",
        "PASS",
        "All provider-service records have provider dashboard ACO mappings"
    )

else:

    record(
        "Provider-service provider→ACO mapping",
        "WARN",
        f"{missing_provider_mapping:,} records have no provider mapping"
    )


# Check mismatches

mismatch_mask = (
    merged["ACO_ID_service"].notna()
    &
    merged["ACO_ID_provider"].notna()
    &
    (
        merged["ACO_ID_service"]
        !=
        merged["ACO_ID_provider"]
    )
)

mismatch_count = (
    mismatch_mask.sum()
)

if mismatch_count == 0:

    record(
        "Provider-service ACO consistency",
        "PASS",
        "No provider→ACO mismatches detected"
    )

else:

    record(
        "Provider-service ACO consistency",
        "FAIL",
        f"{mismatch_count:,} mismatches detected"
    )


# ============================================================
# 11. SERVICE → PROVIDER-SERVICE CONSISTENCY
# ============================================================

section(
    "10. SERVICE COVERAGE CONSISTENCY"
)


service_keys = (
    service[
        [
            "ACO_ID",
            "Year",
            "HCPCS_Cd"
        ]
    ]
    .drop_duplicates()
)

provider_service_keys = (
    provider_service[
        [
            "ACO_ID",
            "Year",
            "HCPCS_Cd"
        ]
    ]
    .drop_duplicates()
)


service_check = service_keys.merge(
    provider_service_keys,
    on=[
        "ACO_ID",
        "Year",
        "HCPCS_Cd"
    ],
    how="left",
    indicator=True
)


missing_service_relationships = (
    (
        service_check["_merge"]
        == "left_only"
    )
    .sum()
)


if missing_service_relationships == 0:

    record(
        "Service → provider-service coverage",
        "PASS",
        "Every service metric key has provider-service evidence"
    )

else:

    record(
        "Service → provider-service coverage",
        "WARN",
        f"{missing_service_relationships:,} service keys have no provider-service evidence"
    )


# ============================================================
# 12. DRIVER CONSISTENCY
# ============================================================

section(
    "11. PERFORMANCE DRIVER CONSISTENCY"
)


driver_acos = set(
    drivers["ACO_ID"]
    .dropna()
    .astype(str)
)

driver_years = set(
    pd.to_numeric(
        drivers["Year"],
        errors="coerce"
    )
    .dropna()
    .astype(int)
)


if driver_acos.issubset(
    base_acos
):

    record(
        "Driver ACO consistency",
        "PASS",
        "All driver ACOs exist in service metrics"
    )

else:

    record(
        "Driver ACO consistency",
        "FAIL",
        "Driver dataset contains unknown ACOs"
    )


if driver_years.issubset(
    base_years
):

    record(
        "Driver year consistency",
        "PASS",
        "All driver years exist in service metrics"
    )

else:

    record(
        "Driver year consistency",
        "FAIL",
        "Driver dataset contains unknown years"
    )


# Check driver scores

negative_driver_scores = (
    pd.to_numeric(
        drivers["driver_score"],
        errors="coerce"
    )
    < 0
).sum()


if negative_driver_scores == 0:

    record(
        "Driver score validity",
        "PASS",
        "No negative driver scores"
    )

else:

    record(
        "Driver score validity",
        "FAIL",
        f"{negative_driver_scores:,} negative driver scores"
    )


# ============================================================
# 13. DRIVER TYPE COVERAGE
# ============================================================

section(
    "12. DRIVER TYPE COVERAGE"
)


expected_driver_types = {
    "SERVICE_COST",
    "SERVICE_UTILIZATION",
    "SERVICE_COST_GROWTH",
    "SERVICE_UTILIZATION_GROWTH",
    "PROVIDER_COST",
    "PROVIDER_UTILIZATION",
    "HIGH_COST_PROVIDER_CONCENTRATION",
    "HIGH_UTILIZATION_PROVIDER_CONCENTRATION",
    "HIGH_COST_HIGH_UTILIZATION_CONCENTRATION"
}


actual_driver_types = set(
    drivers[
        "driver_type"
    ]
    .dropna()
)


missing_driver_types = (
    expected_driver_types
    -
    actual_driver_types
)


if not missing_driver_types:

    record(
        "Driver type coverage",
        "PASS",
        "All expected driver types are present"
    )

else:

    record(
        "Driver type coverage",
        "WARN",
        f"Missing: {missing_driver_types}"
    )


print()
print(
    "Driver types found:"
)

for driver_type in sorted(
    actual_driver_types
):

    count = (
        drivers[
            "driver_type"
        ]
        == driver_type
    ).sum()

    print(
        f"  {driver_type}: {count:,}"
    )


# ============================================================
# 14. YEAR RANGE CHECK
# ============================================================

section(
    "13. YEAR RANGE VALIDATION"
)


for name, df in datasets.items():

    years = (
        pd.to_numeric(
            df["Year"],
            errors="coerce"
        )
        .dropna()
    )

    if years.empty:

        record(
            f"{name} year range",
            "FAIL",
            "No valid years"
        )

        continue

    minimum = int(
        years.min()
    )

    maximum = int(
        years.max()
    )

    if minimum >= 2020 and maximum <= 2024:

        record(
            f"{name} year range",
            "PASS",
            f"{minimum}–{maximum}"
        )

    else:

        record(
            f"{name} year range",
            "WARN",
            f"{minimum}–{maximum}"
        )


# ============================================================
# 15. PROVIDER COUNT REASONABLENESS
# ============================================================

section(
    "14. PROVIDER COUNT REASONABLENESS"
)


provider_counts = (
    aco_provider[
        "provider_count"
    ]
)

if (
    provider_counts > 0
).all():

    record(
        "ACO provider counts",
        "PASS",
        "All ACO-year provider counts are positive"
    )

else:

    bad = (
        provider_counts <= 0
    ).sum()

    record(
        "ACO provider counts",
        "FAIL",
        f"{bad} ACO-year records have non-positive provider counts"
    )


# ============================================================
# 16. SUMMARY STATISTICS
# ============================================================

section(
    "15. FINAL DATASET SUMMARY"
)


print(
    f"Provider dashboard rows:       {len(provider):,}"
)

print(
    f"ACO provider rows:              {len(aco_provider):,}"
)

print(
    f"Service metric rows:            {len(service):,}"
)

print(
    f"Provider-service rows:         {len(provider_service):,}"
)

print(
    f"Performance driver rows:        {len(drivers):,}"
)

print()

print(
    f"Unique providers: "
    f"{provider['Rndrng_NPI'].nunique():,}"
)

print(
    f"Unique ACOs: "
    f"{service['ACO_ID'].nunique():,}"
)

print(
    f"Unique service codes: "
    f"{service['HCPCS_Cd'].nunique():,}"
)

print(
    f"Unique service categories: "
    f"{service['service_category'].nunique():,}"
)


# ============================================================
# 17. FINAL RESULT
# ============================================================

section(
    "16. FINAL AUDIT RESULT"
)


results_df = pd.DataFrame(
    audit_results
)

fail_count = (
    results_df[
        "status"
    ]
    == "FAIL"
).sum()

warn_count = (
    results_df[
        "status"
    ]
    == "WARN"
).sum()

pass_count = (
    results_df[
        "status"
    ]
    == "PASS"
).sum()


print(
    f"PASS: {pass_count}"
)

print(
    f"WARN: {warn_count}"
)

print(
    f"FAIL: {fail_count}"
)


if fail_count == 0:

    if warn_count == 0:

        final_status = (
            "FINAL AUDIT: PASSED"
        )

    else:

        final_status = (
            "FINAL AUDIT: PASSED WITH WARNINGS"
        )

else:

    final_status = (
        "FINAL AUDIT: FAILED"
    )


print()
print(
    final_status
)


# ============================================================
# 18. SAVE AUDIT REPORT
# ============================================================

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "BHAVYA VBC\n"
    )

    file.write(
        "FINAL PROVIDER + SERVICE DATA QUALITY AUDIT\n"
    )

    file.write(
        "=" * 80
        + "\n\n"
    )

    file.write(
        f"Final status: {final_status}\n\n"
    )

    file.write(
        f"PASS: {pass_count}\n"
    )

    file.write(
        f"WARN: {warn_count}\n"
    )

    file.write(
        f"FAIL: {fail_count}\n\n"
    )

    file.write(
        "Audit checks\n"
    )

    file.write(
        "-" * 80
        + "\n"
    )

    for result in audit_results:

        file.write(
            f"[{result['status']}] "
            f"{result['check']}\n"
        )

        if result["details"]:

            file.write(
                f"    {result['details']}\n"
            )

    file.write(
        "\nDataset summary\n"
    )

    file.write(
        "-" * 80
        + "\n"
    )

    file.write(
        f"Provider dashboard rows: "
        f"{len(provider):,}\n"
    )

    file.write(
        f"ACO provider rows: "
        f"{len(aco_provider):,}\n"
    )

    file.write(
        f"Service metric rows: "
        f"{len(service):,}\n"
    )

    file.write(
        f"Provider-service rows: "
        f"{len(provider_service):,}\n"
    )

    file.write(
        f"Performance driver rows: "
        f"{len(drivers):,}\n"
    )


print()
print(
    f"Audit report saved to:\n"
    f"{REPORT_FILE}"
)

print()
print(
    "=" * 80
)

print(
    "FINAL DATA QUALITY AUDIT COMPLETE"
)

print(
    "=" * 80
)