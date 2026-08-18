from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# BHAVYA VBC
# ALL-ACO PROVIDER + SERVICE SERVING LAYER
# ============================================================
#
# PURPOSE
# ------------------------------------------------------------
# Build dashboard-ready serving datasets for ALL real ACOs.
#
# IMPORTANT:
# - NO ML
# - Does NOT modify processed source datasets
# - Preserves all 686 ACOs
# - Preserves all 5 years
# - Exactly 5 providers per ACO-year
# - Uses the all-ACO provider-service serving source
# - Uses all-ACO service metrics
# - Uses all-ACO ACO/provider metrics
# - Uses filtered all-ACO performance drivers
#
# OUTPUTS
# ------------------------------------------------------------
# data/serving/provider_service/
#
#   provider_selection.csv
#   provider_dashboard.csv
#   provider_service_dashboard.csv
#   aco_provider_dashboard.csv
#   aco_service_dashboard.csv
#   performance_drivers.csv
#
# ============================================================


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

PROCESSED_PROVIDER_SERVICE = (
    BASE_DIR
    / "data"
    / "processed"
    / "provider_service"
)

PROCESSED_ALL_ACO = (
    BASE_DIR
    / "data"
    / "processed"
    / "all_aco"
)

SERVING_DIR = (
    BASE_DIR
    / "data"
    / "serving"
    / "provider_service"
)


# ============================================================
# 2. INPUT FILES
# ============================================================

PROVIDER_SERVICE_FILE = (
    BASE_DIR
    / "data"
    / "serving"
    / "all_aco"
    / "all_aco_provider_service.csv"
)

SERVICE_METRICS_FILE = (
    PROCESSED_ALL_ACO
    / "all_aco_service_metrics.csv"
)

PROVIDER_SELECTION_FILE = (
    BASE_DIR
    / "data"
    / "serving"
    / "all_aco"
    / "all_aco_provider_selection.csv"
)

ACO_PROVIDER_METRICS_FILE = (
    PROCESSED_ALL_ACO
    / "aco_provider_metrics.csv"
)

PERFORMANCE_DRIVER_FILE = (
    PROCESSED_ALL_ACO
    / "performance_drivers.csv"
)


# ============================================================
# 3. OUTPUT FILES
# ============================================================

OUTPUT_PROVIDER_SELECTION = (
    SERVING_DIR / "provider_selection.csv"
)

OUTPUT_PROVIDER_DASHBOARD = (
    SERVING_DIR / "provider_dashboard.csv"
)

OUTPUT_PROVIDER_SERVICE = (
    SERVING_DIR / "provider_service_dashboard.csv"
)

OUTPUT_ACO_PROVIDER = (
    SERVING_DIR / "aco_provider_dashboard.csv"
)

OUTPUT_ACO_SERVICE = (
    SERVING_DIR / "aco_service_dashboard.csv"
)

OUTPUT_DRIVERS = (
    SERVING_DIR / "performance_drivers.csv"
)


# ============================================================
# 4. CONFIGURATION
# ============================================================

EXPECTED_PROVIDERS_PER_ACO_YEAR = 5

EXPECTED_YEARS = {2020, 2021, 2022, 2023, 2024}

pd.set_option("display.max_columns", 100)


# ============================================================
# 5. HELPERS
# ============================================================

def section(title):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def check_file(path, label):
    if not path.exists():
        raise FileNotFoundError(
            f"\n{label} not found:\n{path}"
        )

    print(f"OK  {path}")


def clean_columns(df):
    df.columns = [
        str(c).strip()
        for c in df.columns
    ]
    return df


def normalize_ids(df):

    if "ACO_ID" in df.columns:
        df["ACO_ID"] = (
            df["ACO_ID"]
            .astype(str)
            .str.strip()
        )

    if "Rndrng_NPI" in df.columns:
        df["Rndrng_NPI"] = (
            df["Rndrng_NPI"]
            .astype(str)
            .str.strip()
        )

    if "Year" in df.columns:
        df["Year"] = pd.to_numeric(
            df["Year"],
            errors="coerce"
        )

        df["Year"] = df["Year"].astype("Int64")

    return df


def require_columns(df, columns, name):

    missing = [
        c for c in columns
        if c not in df.columns
    ]

    if missing:
        raise ValueError(
            f"{name} is missing columns:\n{missing}"
        )


def numeric(df, columns):

    for c in columns:

        if c in df.columns:

            df[c] = pd.to_numeric(
                df[c],
                errors="coerce"
            )

    return df


def save(df, path):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        path,
        index=False
    )

    print(
        f"Saved: {path.relative_to(BASE_DIR)}"
    )

    print(
        f"Rows : {len(df):,}"
    )


# ============================================================
# 6. START
# ============================================================

print("=" * 80)
print("BHAVYA VBC")
print("=" * 80)
print("ALL-ACO PROVIDER + SERVICE SERVING LAYER")
print("=" * 80)

section("CHECKING INPUT FILES")

for path, label in [
    (PROVIDER_SERVICE_FILE, "All-ACO provider-service"),
    (SERVICE_METRICS_FILE, "All-ACO service metrics"),
    (PROVIDER_SELECTION_FILE, "All-ACO provider selection"),
    (ACO_PROVIDER_METRICS_FILE, "All-ACO provider metrics"),
    (PERFORMANCE_DRIVER_FILE, "All-ACO performance drivers"),
]:

    check_file(path, label)


# ============================================================
# 7. LOAD DATA
# ============================================================

section("LOADING ALL-ACO DATASETS")

provider_service = pd.read_csv(
    PROVIDER_SERVICE_FILE,
    low_memory=False
)

service_metrics = pd.read_csv(
    SERVICE_METRICS_FILE,
    low_memory=False
)

provider_selection = pd.read_csv(
    PROVIDER_SELECTION_FILE,
    low_memory=False
)

aco_provider = pd.read_csv(
    ACO_PROVIDER_METRICS_FILE,
    low_memory=False
)

drivers = pd.read_csv(
    PERFORMANCE_DRIVER_FILE,
    low_memory=False
)


# ============================================================
# 8. CLEAN
# ============================================================

provider_service = normalize_ids(
    clean_columns(provider_service)
)

service_metrics = normalize_ids(
    clean_columns(service_metrics)
)

provider_selection = normalize_ids(
    clean_columns(provider_selection)
)

aco_provider = normalize_ids(
    clean_columns(aco_provider)
)

drivers = normalize_ids(
    clean_columns(drivers)
)


print(
    f"Provider-service rows : {len(provider_service):,}"
)

print(
    f"Service metric rows   : {len(service_metrics):,}"
)

print(
    f"Provider selection    : {len(provider_selection):,}"
)

print(
    f"ACO provider metrics  : {len(aco_provider):,}"
)

print(
    f"Performance drivers   : {len(drivers):,}"
)


# ============================================================
# 9. REQUIRED COLUMN VALIDATION
# ============================================================

section("VALIDATING INPUT DATASETS")

require_columns(
    provider_service,
    [
        "ACO_ID",
        "Rndrng_NPI",
        "Year",
        "HCPCS_Cd"
    ],
    "provider_service"
)

require_columns(
    service_metrics,
    [
        "ACO_ID",
        "Year",
        "HCPCS_Cd"
    ],
    "service_metrics"
)

require_columns(
    provider_selection,
    [
        "ACO_ID",
        "Rndrng_NPI",
        "Year"
    ],
    "provider_selection"
)

require_columns(
    aco_provider,
    [
        "ACO_ID",
        "Year"
    ],
    "aco_provider"
)

require_columns(
    drivers,
    [
        "ACO_ID",
        "Year",
        "driver_type",
        "driver_name",
        "metric_name"
    ],
    "performance_drivers"
)

print("PASS - Required columns")


# ============================================================
# 10. COVERAGE VALIDATION
# ============================================================

section("VALIDATING ALL-ACO COVERAGE")

provider_acos = set(
    provider_service["ACO_ID"]
    .dropna()
    .astype(str)
    .unique()
)

service_acos = set(
    service_metrics["ACO_ID"]
    .dropna()
    .astype(str)
    .unique()
)

selection_acos = set(
    provider_selection["ACO_ID"]
    .dropna()
    .astype(str)
    .unique()
)

aco_provider_acos = set(
    aco_provider["ACO_ID"]
    .dropna()
    .astype(str)
    .unique()
)

driver_acos = set(
    drivers["ACO_ID"]
    .dropna()
    .astype(str)
    .unique()
)


print(
    f"Provider-service ACOs : {len(provider_acos)}"
)

print(
    f"Service metric ACOs   : {len(service_acos)}"
)

print(
    f"Selection ACOs        : {len(selection_acos)}"
)

print(
    f"ACO provider ACOs     : {len(aco_provider_acos)}"
)

print(
    f"Driver ACOs           : {len(driver_acos)}"
)


if len(provider_acos) != 686:
    raise ValueError(
        f"Expected 686 ACOs in provider-service, "
        f"found {len(provider_acos)}"
    )

if len(service_acos) != 686:
    raise ValueError(
        f"Expected 686 ACOs in service metrics, "
        f"found {len(service_acos)}"
    )

print("PASS - 686 ACOs confirmed")


# ============================================================
# 11. PROVIDER SELECTION
# ============================================================

section("BUILDING PROVIDER SELECTION")

selection = provider_selection.copy()

selection = selection.sort_values(
    [
        "ACO_ID",
        "Year",
        "provider_rank"
        if "provider_rank" in selection.columns
        else "Rndrng_NPI"
    ]
)

selection = (
    selection
    .groupby(
        ["ACO_ID", "Year"],
        group_keys=False
    )
    .head(EXPECTED_PROVIDERS_PER_ACO_YEAR)
    .copy()
)

selection = selection.drop_duplicates(
    [
        "ACO_ID",
        "Rndrng_NPI",
        "Year"
    ]
)


# Validate provider count

provider_counts = (
    selection
    .groupby(
        ["ACO_ID", "Year"]
    )["Rndrng_NPI"]
    .nunique()
)

bad_counts = provider_counts[
    provider_counts != EXPECTED_PROVIDERS_PER_ACO_YEAR
]

print(
    f"Provider-year rows : {len(selection):,}"
)

print(
    f"ACO-year groups    : {len(provider_counts):,}"
)

print(
    "Provider distribution:"
)

print(
    provider_counts.value_counts()
)

if len(bad_counts) > 0:
    raise ValueError(
        "Some ACO-years do not have exactly 5 providers."
    )

print(
    "PASS - Exactly 5 providers per ACO-year"
)


# ============================================================
# 12. PROVIDER DASHBOARD
# ============================================================

section("BUILDING PROVIDER DASHBOARD")

provider_dashboard = provider_service.copy()


# Aggregate provider-year metrics

numeric_columns = [
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


provider_dashboard = numeric(
    provider_dashboard,
    numeric_columns
)


aggregation = {}

for c in numeric_columns:

    if c in [
        "Tot_Benes",
        "Tot_Srvcs"
    ]:
        aggregation[c] = "sum"

    else:
        aggregation[c] = "mean"


provider_dashboard = (
    provider_dashboard
    .groupby(
        [
            "ACO_ID",
            "Rndrng_NPI",
            "Year"
        ],
        as_index=False
    )
    .agg(aggregation)
)


# Add provider rank

provider_rank_source = selection[
    [
        "ACO_ID",
        "Rndrng_NPI",
        "Year"
    ]
    + [
        c for c in [
            "provider_rank",
            "selection_score"
        ]
        if c in selection.columns
    ]
].copy()


provider_dashboard = provider_dashboard.merge(
    provider_rank_source,
    on=[
        "ACO_ID",
        "Rndrng_NPI",
        "Year"
    ],
    how="left"
)


# Provider segment

def provider_segment(row):

    cost = row.get(
        "cost_score",
        np.nan
    )

    util = row.get(
        "utilization_score",
        np.nan
    )

    if pd.isna(cost) or pd.isna(util):
        return "MODERATE"

    if cost >= 0.75 and util >= 0.75:
        return "HIGH_COST_HIGH_UTILIZATION"

    if cost >= 0.75:
        return "HIGH_COST"

    if util >= 0.75:
        return "HIGH_UTILIZATION"

    return "MODERATE"


provider_dashboard[
    "provider_segment"
] = provider_dashboard.apply(
    provider_segment,
    axis=1
)


print(
    f"Provider dashboard rows: "
    f"{len(provider_dashboard):,}"
)


# ============================================================
# 13. PROVIDER-SERVICE DASHBOARD
# ============================================================

section("BUILDING PROVIDER-SERVICE DASHBOARD")

provider_service_dashboard = provider_service.copy()

# Keep only dashboard-relevant columns

preferred_provider_service_columns = [
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
    "provider_rank"
]


provider_service_dashboard = provider_service_dashboard[
    [
        c
        for c in preferred_provider_service_columns
        if c in provider_service_dashboard.columns
    ]
].copy()


print(
    f"Provider-service dashboard rows: "
    f"{len(provider_service_dashboard):,}"
)


# ============================================================
# 14. ACO PROVIDER DASHBOARD
# ============================================================

section("BUILDING ACO PROVIDER DASHBOARD")

aco_provider_dashboard = aco_provider.copy()

print(
    f"ACO provider rows: "
    f"{len(aco_provider_dashboard):,}"
)


# ============================================================
# 15. ACO SERVICE DASHBOARD
# ============================================================

section("BUILDING ACO SERVICE DASHBOARD")

aco_service_dashboard = service_metrics.copy()

preferred_service_columns = [
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
    "top_payment_service"
]


aco_service_dashboard = aco_service_dashboard[
    [
        c
        for c in preferred_service_columns
        if c in aco_service_dashboard.columns
    ]
].copy()


print(
    f"ACO service dashboard rows: "
    f"{len(aco_service_dashboard):,}"
)


# ============================================================
# 16. PERFORMANCE DRIVERS
# ============================================================

section("BUILDING PERFORMANCE DRIVER SERVING DATA")

performance_drivers = drivers.copy()

# Ensure drivers belong to the real all-ACO universe

performance_drivers = performance_drivers[
    performance_drivers["ACO_ID"].isin(
        provider_acos
    )
].copy()


# Keep dashboard columns

driver_columns = [
    "ACO_ID",
    "Year",
    "driver_type",
    "driver_name",
    "metric_name",
    "metric_value",
    "change_pct",
    "driver_score",
    "driver_rank",
    "driver_severity"
]


performance_drivers = performance_drivers[
    [
        c
        for c in driver_columns
        if c in performance_drivers.columns
    ]
].copy()


performance_drivers = (
    performance_drivers
    .sort_values(
        [
            "ACO_ID",
            "Year",
            "driver_type",
            "driver_rank"
        ]
    )
)


print(
    f"Performance driver rows: "
    f"{len(performance_drivers):,}"
)


# ============================================================
# 17. FINAL VALIDATION
# ============================================================

section("FINAL SERVING-LAYER VALIDATION")


def validate_dataset(
    df,
    name,
    grain_columns
):

    print()
    print(f"=== {name} ===")

    print(
        f"Rows       : {len(df):,}"
    )

    print(
        f"Columns    : {len(df.columns)}"
    )

    if "ACO_ID" in df.columns:

        print(
            f"ACOs       : "
            f"{df['ACO_ID'].nunique()}"
        )

    if "Year" in df.columns:

        print(
            f"Years      : "
            f"{sorted(df['Year'].dropna().unique().tolist())}"
        )

    duplicates = df.duplicated(
        grain_columns
    ).sum()

    print(
        f"Duplicates : {duplicates}"
    )

    if duplicates != 0:

        raise ValueError(
            f"{name} contains duplicate grain rows."
        )


validate_dataset(
    selection,
    "provider_selection",
    [
        "ACO_ID",
        "Rndrng_NPI",
        "Year"
    ]
)

validate_dataset(
    provider_dashboard,
    "provider_dashboard",
    [
        "ACO_ID",
        "Rndrng_NPI",
        "Year"
    ]
)

validate_dataset(
    provider_service_dashboard,
    "provider_service_dashboard",
    [
        "ACO_ID",
        "Rndrng_NPI",
        "Year",
        "HCPCS_Cd"
    ]
)

validate_dataset(
    aco_provider_dashboard,
    "aco_provider_dashboard",
    [
        "ACO_ID",
        "Year"
    ]
)

validate_dataset(
    aco_service_dashboard,
    "aco_service_dashboard",
    [
        "ACO_ID",
        "Year",
        "HCPCS_Cd"
    ]
)

validate_dataset(
    performance_drivers,
    "performance_drivers",
    [
        "ACO_ID",
        "Year",
        "driver_type",
        "driver_rank"
    ]
)


# ============================================================
# 18. COVERAGE CHECK
# ============================================================

section("FINAL ACO/YEAR COVERAGE")

expected_aco_years = (
    provider_acos
    and len(provider_acos) * len(EXPECTED_YEARS)
)

actual_provider_selection = (
    selection[
        ["ACO_ID", "Year"]
    ]
    .drop_duplicates()
    .shape[0]
)

actual_provider_dashboard = (
    provider_dashboard[
        ["ACO_ID", "Year"]
    ]
    .drop_duplicates()
    .shape[0]
)

actual_service_dashboard = (
    aco_service_dashboard[
        ["ACO_ID", "Year"]
    ]
    .drop_duplicates()
    .shape[0]
)

actual_aco_provider = (
    aco_provider_dashboard[
        ["ACO_ID", "Year"]
    ]
    .drop_duplicates()
    .shape[0]
)


print(
    f"Expected ACO-years : "
    f"{expected_aco_years:,}"
)

print(
    f"Provider selection : "
    f"{actual_provider_selection:,}"
)

print(
    f"Provider dashboard : "
    f"{actual_provider_dashboard:,}"
)

print(
    f"ACO service        : "
    f"{actual_service_dashboard:,}"
)

print(
    f"ACO provider       : "
    f"{actual_aco_provider:,}"
)


if actual_provider_selection != expected_aco_years:
    raise ValueError(
        "Provider selection does not contain all ACO-years."
    )

if actual_provider_dashboard != expected_aco_years:
    raise ValueError(
        "Provider dashboard does not contain all ACO-years."
    )

if actual_service_dashboard != expected_aco_years:
    raise ValueError(
        "ACO service dashboard does not contain all ACO-years."
    )

if actual_aco_provider != expected_aco_years:
    raise ValueError(
        "ACO provider dashboard does not contain all ACO-years."
    )


print(
    "PASS - All 686 ACOs × 5 years represented"
)


# ============================================================
# 19. SAVE
# ============================================================

section("SAVING SERVING DATASETS")

SERVING_DIR.mkdir(
    parents=True,
    exist_ok=True
)

save(
    selection,
    OUTPUT_PROVIDER_SELECTION
)

save(
    provider_dashboard,
    OUTPUT_PROVIDER_DASHBOARD
)

save(
    provider_service_dashboard,
    OUTPUT_PROVIDER_SERVICE
)

save(
    aco_provider_dashboard,
    OUTPUT_ACO_PROVIDER
)

save(
    aco_service_dashboard,
    OUTPUT_ACO_SERVICE
)

save(
    performance_drivers,
    OUTPUT_DRIVERS
)


# ============================================================
# 20. FINAL SUMMARY
# ============================================================

section("SERVING LAYER BUILD COMPLETE")

print(
    "PASS - All 686 ACOs preserved."
)

print(
    "PASS - All 5 years preserved."
)

print(
    "PASS - Exactly 5 providers per ACO-year."
)

print(
    "PASS - Provider-service grain preserved."
)

print(
    "PASS - ACO-service grain preserved."
)

print(
    "PASS - ACO-provider grain preserved."
)

print(
    "PASS - Performance drivers restricted to real ACOs."
)

print(
    "PASS - Processed source datasets were not modified."
)

print()
print("OUTPUT FILES")
print("-" * 80)

for path in [
    OUTPUT_PROVIDER_SELECTION,
    OUTPUT_PROVIDER_DASHBOARD,
    OUTPUT_PROVIDER_SERVICE,
    OUTPUT_ACO_PROVIDER,
    OUTPUT_ACO_SERVICE,
    OUTPUT_DRIVERS
]:

    print(
        f"OK  {path.relative_to(BASE_DIR)}"
    )

print()
print("=" * 80)
print("DONE")
print("=" * 80)