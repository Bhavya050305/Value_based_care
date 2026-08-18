from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

PROVIDER_SERVICE_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "provider_service"
    / "provider_service_metrics.csv"
)

ACO_MAPPING_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "all_aco"
    / "aco_provider_mapping.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "serving"
    / "all_aco"
)

OUTPUT_PROVIDER_SERVICE = (
    OUTPUT_DIR
    / "all_aco_provider_service.csv"
)

OUTPUT_PROVIDER_SELECTION = (
    OUTPUT_DIR
    / "all_aco_provider_selection.csv"
)

PROVIDERS_PER_ACO_YEAR = 5


# ============================================================
# START
# ============================================================

print("=" * 80)
print("BHAVYA VBC")
print("=" * 80)
print("ALL-ACO PROVIDER + SERVICE SERVING BUILD")
print("=" * 80)


# ============================================================
# CHECK INPUT FILES
# ============================================================

print("\nChecking input files...")

if not PROVIDER_SERVICE_FILE.exists():
    raise FileNotFoundError(
        f"Provider-service file not found:\n"
        f"{PROVIDER_SERVICE_FILE}"
    )

if not ACO_MAPPING_FILE.exists():
    raise FileNotFoundError(
        f"ACO mapping file not found:\n"
        f"{ACO_MAPPING_FILE}"
    )

print(f"OK  {PROVIDER_SERVICE_FILE}")
print(f"OK  {ACO_MAPPING_FILE}")


# ============================================================
# [1/8] LOAD PROVIDER-SERVICE DATA
# ============================================================

print("\n" + "=" * 80)
print("[1/8] LOADING PROVIDER-SERVICE DATA")
print("=" * 80)

df = pd.read_csv(
    PROVIDER_SERVICE_FILE,
    low_memory=False
)

required_columns = [
    "Rndrng_NPI",
    "Year"
]

missing = [
    c for c in required_columns
    if c not in df.columns
]

if missing:
    raise ValueError(
        f"Missing required columns in provider-service data: {missing}"
    )


# ------------------------------------------------------------
# Clean identifiers
# ------------------------------------------------------------

df["Rndrng_NPI"] = (
    df["Rndrng_NPI"]
    .astype(str)
    .str.strip()
)

df["Year"] = pd.to_numeric(
    df["Year"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "Rndrng_NPI",
        "Year"
    ]
)

df["Year"] = df["Year"].astype(int)


print(
    f"Rows              : {len(df):,}"
)

print(
    f"Unique providers  : "
    f"{df['Rndrng_NPI'].nunique():,}"
)

print(
    f"Years             : "
    f"{sorted(df['Year'].unique().tolist())}"
)

if "HCPCS_Cd" in df.columns:

    print(
        f"HCPCS codes       : "
        f"{df['HCPCS_Cd'].nunique():,}"
    )

print(
    f"Features          : "
    f"{len(df.columns):,}"
)


# ============================================================
# [2/8] LOAD ALL-ACO PROVIDER MAPPING
# ============================================================

print("\n" + "=" * 80)
print("[2/8] LOADING ALL-ACO PROVIDER MAPPING")
print("=" * 80)

mapping = pd.read_csv(
    ACO_MAPPING_FILE,
    low_memory=False
)

required_mapping_columns = [
    "ACO_ID",
    "Rndrng_NPI"
]

missing_mapping = [
    c
    for c in required_mapping_columns
    if c not in mapping.columns
]

if missing_mapping:
    raise ValueError(
        "Missing required mapping columns: "
        f"{missing_mapping}"
    )


# ------------------------------------------------------------
# Clean mapping
# ------------------------------------------------------------

mapping["ACO_ID"] = (
    mapping["ACO_ID"]
    .astype(str)
    .str.strip()
)

mapping["Rndrng_NPI"] = (
    mapping["Rndrng_NPI"]
    .astype(str)
    .str.strip()
)

mapping = mapping[
    [
        "ACO_ID",
        "Rndrng_NPI"
    ]
].drop_duplicates()


print(
    f"Mapping rows      : "
    f"{len(mapping):,}"
)

print(
    f"Unique ACOs       : "
    f"{mapping['ACO_ID'].nunique():,}"
)

print(
    f"Unique providers  : "
    f"{mapping['Rndrng_NPI'].nunique():,}"
)


# ============================================================
# [3/8] VALIDATE ACO MAPPING
# ============================================================

print("\n" + "=" * 80)
print("[3/8] VALIDATING ACO MAPPING")
print("=" * 80)


# ------------------------------------------------------------
# Check providers assigned to multiple ACOs
# ------------------------------------------------------------

provider_aco_counts = (
    mapping
    .groupby("Rndrng_NPI")["ACO_ID"]
    .nunique()
)

multi_aco_providers = (
    provider_aco_counts[
        provider_aco_counts > 1
    ]
)

if len(multi_aco_providers) > 0:

    print(
        "Providers assigned to multiple ACOs:"
    )

    print(
        multi_aco_providers.head(20)
    )

    raise ValueError(
        "Some providers are assigned to multiple ACOs."
    )


# ------------------------------------------------------------
# Missing values
# ------------------------------------------------------------

if mapping["ACO_ID"].isna().any():

    raise ValueError(
        "Missing ACO_ID detected in mapping."
    )

if mapping["Rndrng_NPI"].isna().any():

    raise ValueError(
        "Missing provider NPI detected in mapping."
    )


print(
    "PASS - Every provider has at most one ACO."
)

print(
    f"All ACO IDs        : "
    f"{mapping['ACO_ID'].nunique():,}"
)


# ============================================================
# [4/8] APPLY ALL-ACO ASSIGNMENTS
# ============================================================

print("\n" + "=" * 80)
print("[4/8] APPLYING ALL-ACO ASSIGNMENTS")
print("=" * 80)


# IMPORTANT:
#
# The ACO_ID inside provider_service_metrics.csv belongs
# to the earlier 10-ACO processing layer.
#
# We intentionally REMOVE it.
#
# The authoritative ACO assignment is now:
#
# data/processed/all_aco/aco_provider_mapping.csv
#
# This mapping contains ALL ACOs.


if "ACO_ID" in df.columns:

    df = df.drop(
        columns=["ACO_ID"]
    )


# ------------------------------------------------------------
# Merge complete 686-ACO mapping
# ------------------------------------------------------------

df = df.merge(
    mapping,
    on="Rndrng_NPI",
    how="inner",
    validate="many_to_one"
)


print(
    f"Rows after ACO mapping: "
    f"{len(df):,}"
)

print(
    f"All ACOs represented   : "
    f"{df['ACO_ID'].nunique():,}"
)

print(
    f"Providers represented  : "
    f"{df['Rndrng_NPI'].nunique():,}"
)


# ------------------------------------------------------------
# Validate ACO coverage
# ------------------------------------------------------------

source_acos = set(
    mapping["ACO_ID"].unique()
)

mapped_acos = set(
    df["ACO_ID"].unique()
)

missing_acos = sorted(
    source_acos - mapped_acos
)

if missing_acos:

    raise ValueError(
        "Some mapped ACOs have no provider-service data.\n"
        f"Missing ACOs: {missing_acos[:20]}"
    )


print(
    "PASS - All mapped ACOs represented."
)


# ============================================================
# [5/8] BUILD PROVIDER-YEAR RANKING
# ============================================================

print("\n" + "=" * 80)
print("[5/8] BUILDING PROVIDER-YEAR RANKING")
print("=" * 80)


# ============================================================
# IMPORTANT FIX
# ============================================================
#
# DO NOT aggregate Rndrng_NPI itself.
#
# The previous version used:
#
#     "Rndrng_NPI": "size"
#
# That destroys the actual NPI identifier.
#
# Instead, Rndrng_NPI remains a GROUPBY KEY.
#
# This gives:
#
# ACO_ID + Year + Rndrng_NPI
#
# as one provider-year record.
# ============================================================


aggregation = {}


# ------------------------------------------------------------
# Services
# ------------------------------------------------------------

if "Tot_Srvcs" in df.columns:

    aggregation["Tot_Srvcs"] = "sum"


# ------------------------------------------------------------
# Beneficiaries
# ------------------------------------------------------------

if "Tot_Benes" in df.columns:

    aggregation["Tot_Benes"] = "sum"


# ------------------------------------------------------------
# Payment
# ------------------------------------------------------------

if "Avg_Mdcr_Pymt_Amt" in df.columns:

    aggregation["Avg_Mdcr_Pymt_Amt"] = "mean"


# ------------------------------------------------------------
# Payment per service
# ------------------------------------------------------------

if "payment_per_service" in df.columns:

    aggregation["payment_per_service"] = "mean"


# ------------------------------------------------------------
# Cost score
# ------------------------------------------------------------

if "cost_score" in df.columns:

    aggregation["cost_score"] = "mean"


# ------------------------------------------------------------
# Utilization score
# ------------------------------------------------------------

if "utilization_score" in df.columns:

    aggregation["utilization_score"] = "mean"


# ------------------------------------------------------------
# Provider-year aggregation
# ------------------------------------------------------------

provider_year = (
    df
    .groupby(
        [
            "ACO_ID",
            "Year",
            "Rndrng_NPI"
        ],
        as_index=False
    )
    .agg(aggregation)
)


print(
    f"Provider-year rows: "
    f"{len(provider_year):,}"
)

print(
    f"ACO-year combinations: "
    f"{provider_year[['ACO_ID', 'Year']].drop_duplicates().shape[0]:,}"
)

print(
    f"Unique providers in provider-year table: "
    f"{provider_year['Rndrng_NPI'].nunique():,}"
)


# ============================================================
# BUILD RANKING SCORE
# ============================================================

print("\nBuilding provider selection ranking...")


# ------------------------------------------------------------
# Rank by service volume
# ------------------------------------------------------------

if "Tot_Srvcs" in provider_year.columns:

    provider_year["rank_services"] = (
        provider_year
        .groupby(
            [
                "ACO_ID",
                "Year"
            ]
        )["Tot_Srvcs"]
        .rank(
            ascending=False,
            method="first"
        )
    )

else:

    provider_year["rank_services"] = (
        provider_year
        .groupby(
            [
                "ACO_ID",
                "Year"
            ]
        )["Rndrng_NPI"]
        .rank(
            ascending=True,
            method="first"
        )
    )


# ------------------------------------------------------------
# Rank by beneficiaries
# ------------------------------------------------------------

if "Tot_Benes" in provider_year.columns:

    provider_year["rank_beneficiaries"] = (
        provider_year
        .groupby(
            [
                "ACO_ID",
                "Year"
            ]
        )["Tot_Benes"]
        .rank(
            ascending=False,
            method="first"
        )
    )

else:

    provider_year["rank_beneficiaries"] = (
        provider_year["rank_services"]
    )


# ------------------------------------------------------------
# Rank by payment
# ------------------------------------------------------------

if "Avg_Mdcr_Pymt_Amt" in provider_year.columns:

    provider_year["rank_payment"] = (
        provider_year
        .groupby(
            [
                "ACO_ID",
                "Year"
            ]
        )["Avg_Mdcr_Pymt_Amt"]
        .rank(
            ascending=False,
            method="first"
        )
    )

else:

    provider_year["rank_payment"] = (
        provider_year["rank_services"]
    )


# ============================================================
# SELECTION SCORE
# ============================================================
#
# Lower rank = better provider.
#
# Therefore:
#
# 50% service rank
# 30% beneficiary rank
# 20% payment rank
#
# Lower score is better.
# ============================================================

provider_year["selection_score"] = (
    provider_year["rank_services"] * 0.50
    +
    provider_year["rank_beneficiaries"] * 0.30
    +
    provider_year["rank_payment"] * 0.20
)


# ============================================================
# [6/8] SELECT EXACTLY 5 PROVIDERS PER ACO-YEAR
# ============================================================

print("\n" + "=" * 80)
print("[6/8] SELECTING 5 PROVIDERS PER ACO-YEAR")
print("=" * 80)


# ------------------------------------------------------------
# Sort best providers first
# ------------------------------------------------------------

provider_year = provider_year.sort_values(
    [
        "ACO_ID",
        "Year",
        "selection_score",
        "Rndrng_NPI"
    ],
    ascending=[
        True,
        True,
        True,
        True
    ]
)


# ------------------------------------------------------------
# TOP 5 WITHIN EACH ACO + YEAR
# ------------------------------------------------------------

selected = (
    provider_year
    .groupby(
        [
            "ACO_ID",
            "Year"
        ],
        group_keys=False
    )
    .head(
        PROVIDERS_PER_ACO_YEAR
    )
    .copy()
)


# ------------------------------------------------------------
# Provider rank
# ------------------------------------------------------------

selected["provider_rank"] = (
    selected
    .groupby(
        [
            "ACO_ID",
            "Year"
        ]
    )
    .cumcount()
    + 1
)


# ============================================================
# VALIDATE EXACTLY 5
# ============================================================

provider_counts = (
    selected
    .groupby(
        [
            "ACO_ID",
            "Year"
        ]
    )["Rndrng_NPI"]
    .nunique()
)


print(
    "\nProvider counts across ACO-years:"
)

print(
    provider_counts
    .value_counts()
    .sort_index()
)


# ------------------------------------------------------------
# Expected number of ACO-years
# ------------------------------------------------------------

all_acos = sorted(
    mapping["ACO_ID"].unique()
)

all_years = sorted(
    df["Year"].unique()
)

expected_aco_year_count = (
    len(all_acos)
    *
    len(all_years)
)

actual_aco_year_count = (
    selected[
        [
            "ACO_ID",
            "Year"
        ]
    ]
    .drop_duplicates()
    .shape[0]
)


print(
    f"\nExpected ACO-years : "
    f"{expected_aco_year_count:,}"
)

print(
    f"Actual ACO-years   : "
    f"{actual_aco_year_count:,}"
)


# ------------------------------------------------------------
# Check every ACO-year exists
# ------------------------------------------------------------

expected_grid = (
    pd.MultiIndex
    .from_product(
        [
            all_acos,
            all_years
        ],
        names=[
            "ACO_ID",
            "Year"
        ]
    )
    .to_frame(
        index=False
    )
)

actual_grid = (
    selected[
        [
            "ACO_ID",
            "Year"
        ]
    ]
    .drop_duplicates()
)


missing_aco_years = (
    expected_grid
    .merge(
        actual_grid,
        on=[
            "ACO_ID",
            "Year"
        ],
        how="left",
        indicator=True
    )
)

missing_aco_years = (
    missing_aco_years[
        missing_aco_years["_merge"] == "left_only"
    ]
    .drop(
        columns=["_merge"]
    )
)


if len(missing_aco_years) > 0:

    print(
        "\nMissing ACO-years:"
    )

    print(
        missing_aco_years.head(20)
    )

    raise ValueError(
        "Some ACO-year combinations are missing."
    )


# ------------------------------------------------------------
# Check exactly 5 providers
# ------------------------------------------------------------

bad_counts = provider_counts[
    provider_counts != PROVIDERS_PER_ACO_YEAR
]


if len(bad_counts) > 0:

    print(
        "\nInvalid provider counts:"
    )

    print(
        bad_counts.head(20)
    )

    raise ValueError(
        "Some ACO-years do not have exactly "
        f"{PROVIDERS_PER_ACO_YEAR} providers."
    )


# ------------------------------------------------------------
# Expected provider-year rows
# ------------------------------------------------------------

expected_provider_year_rows = (
    len(all_acos)
    *
    len(all_years)
    *
    PROVIDERS_PER_ACO_YEAR
)

actual_provider_year_rows = len(
    selected
)


print(
    f"\nExpected provider-year rows: "
    f"{expected_provider_year_rows:,}"
)

print(
    f"Actual provider-year rows  : "
    f"{actual_provider_year_rows:,}"
)


if actual_provider_year_rows != expected_provider_year_rows:

    raise ValueError(
        "Provider-year selection row count is incorrect."
    )


print(
    "\nPASS - Every ACO-year has exactly "
    f"{PROVIDERS_PER_ACO_YEAR} providers."
)


# ============================================================
# CREATE PROVIDER SELECTION DATASET
# ============================================================

selection_columns = [
    "ACO_ID",
    "Year",
    "Rndrng_NPI",
    "provider_rank",
    "selection_score"
]


for column in [
    "Tot_Srvcs",
    "Tot_Benes",
    "Avg_Mdcr_Pymt_Amt",
    "cost_score",
    "utilization_score"
]:

    if column in selected.columns:

        selection_columns.append(
            column
        )


provider_selection = (
    selected[
        selection_columns
    ]
    .copy()
)


# ============================================================
# [7/8] BUILD PROVIDER-SERVICE DATASET
# ============================================================

print("\n" + "=" * 80)
print("[7/8] BUILDING ALL-ACO PROVIDER-SERVICE DATASET")
print("=" * 80)


selection_keys = (
    selected[
        [
            "ACO_ID",
            "Year",
            "Rndrng_NPI"
        ]
    ]
    .drop_duplicates()
)


# ------------------------------------------------------------
# Keep only selected 5 providers for each ACO-year
# ------------------------------------------------------------

all_aco_provider_service = (
    df
    .merge(
        selection_keys,
        on=[
            "ACO_ID",
            "Year",
            "Rndrng_NPI"
        ],
        how="inner",
        validate="many_to_one"
    )
)


print(
    f"Provider-service rows: "
    f"{len(all_aco_provider_service):,}"
)

print(
    f"ACOs: "
    f"{all_aco_provider_service['ACO_ID'].nunique():,}"
)

print(
    f"Providers: "
    f"{all_aco_provider_service['Rndrng_NPI'].nunique():,}"
)

print(
    f"Years: "
    f"{sorted(all_aco_provider_service['Year'].unique().tolist())}"
)


# ------------------------------------------------------------
# Add provider rank
# ------------------------------------------------------------

all_aco_provider_service = (
    all_aco_provider_service
    .merge(
        selected[
            [
                "ACO_ID",
                "Year",
                "Rndrng_NPI",
                "provider_rank"
            ]
        ],
        on=[
            "ACO_ID",
            "Year",
            "Rndrng_NPI"
        ],
        how="left",
        validate="many_to_one"
    )
)


# ============================================================
# [8/8] FINAL VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("[8/8] FINAL ALL-ACO VALIDATION")
print("=" * 80)


source_acos = (
    mapping["ACO_ID"]
    .nunique()
)

selected_acos = (
    selected["ACO_ID"]
    .nunique()
)

service_acos = (
    all_aco_provider_service["ACO_ID"]
    .nunique()
)


source_years = sorted(
    df["Year"].unique()
)

service_years = sorted(
    all_aco_provider_service["Year"].unique()
)


# ============================================================
# DATASET SUMMARY
# ============================================================

print("\nDATASET SUMMARY")
print("-" * 80)

print(
    f"ACO provider mapping       : "
    f"{len(mapping):,} rows"
)

print(
    f"Provider-year selection    : "
    f"{len(selected):,} rows"
)

print(
    f"Provider-service serving   : "
    f"{len(all_aco_provider_service):,} rows"
)


# ============================================================
# ACO COVERAGE
# ============================================================

print("\nACO COVERAGE")
print("-" * 80)

print(
    f"Source mapping ACOs        : "
    f"{source_acos:,}"
)

print(
    f"Selected ACOs              : "
    f"{selected_acos:,}"
)

print(
    f"Service ACOs               : "
    f"{service_acos:,}"
)


# ============================================================
# YEAR COVERAGE
# ============================================================

print("\nYEAR COVERAGE")
print("-" * 80)

print(
    f"Source years               : "
    f"{source_years}"
)

print(
    f"Serving years              : "
    f"{service_years}"
)


# ============================================================
# PROVIDER-YEAR SUMMARY
# ============================================================

print("\nPROVIDER-YEAR SELECTION")
print("-" * 80)

print(
    f"Expected ACOs              : "
    f"{source_acos:,}"
)

print(
    f"Expected years             : "
    f"{len(source_years):,}"
)

print(
    f"Providers per ACO-year     : "
    f"{PROVIDERS_PER_ACO_YEAR}"
)

print(
    f"Expected provider-years    : "
    f"{expected_provider_year_rows:,}"
)

print(
    f"Actual provider-years      : "
    f"{actual_provider_year_rows:,}"
)


# ============================================================
# FINAL HARD CHECKS
# ============================================================

if source_acos != selected_acos:

    raise ValueError(
        "Not all ACOs are represented "
        "in provider selection."
    )


if source_acos != service_acos:

    raise ValueError(
        "Not all ACOs are represented "
        "in provider-service data."
    )


if source_years != service_years:

    raise ValueError(
        "Year coverage changed unexpectedly."
    )


if actual_provider_year_rows != (
    source_acos
    *
    len(source_years)
    *
    PROVIDERS_PER_ACO_YEAR
):

    raise ValueError(
        "Final provider-year selection "
        "row count is incorrect."
    )


if all_aco_provider_service[
    "ACO_ID"
].isna().any():

    raise ValueError(
        "Missing ACO IDs in final service dataset."
    )


if all_aco_provider_service[
    "Rndrng_NPI"
].isna().any():

    raise ValueError(
        "Missing provider NPIs "
        "in final service dataset."
    )


# ============================================================
# FINAL PROVIDER COUNT VALIDATION
# ============================================================

final_provider_counts = (
    selected
    .groupby(
        [
            "ACO_ID",
            "Year"
        ]
    )["Rndrng_NPI"]
    .nunique()
)


if not (
    final_provider_counts
    == PROVIDERS_PER_ACO_YEAR
).all():

    raise ValueError(
        "Final validation failed: "
        "not every ACO-year has exactly 5 providers."
    )


print(
    "\nPASS - All ACO-year combinations "
    "have exactly 5 providers."
)


# ============================================================
# SAVE OUTPUTS
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


provider_selection.to_csv(
    OUTPUT_PROVIDER_SELECTION,
    index=False
)


all_aco_provider_service.to_csv(
    OUTPUT_PROVIDER_SERVICE,
    index=False
)


# ============================================================
# OUTPUT FILE SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("OUTPUT FILES")
print("=" * 80)

print(
    f"OK  {OUTPUT_PROVIDER_SELECTION}"
)

print(
    f"OK  {OUTPUT_PROVIDER_SERVICE}"
)


# ============================================================
# FINAL STATUS
# ============================================================

print("\n" + "=" * 80)
print("BUILD COMPLETE")
print("=" * 80)

print(
    "PASS - ALL ACOs preserved."
)

print(
    "PASS - ALL years preserved."
)

print(
    "PASS - Exactly 5 providers selected "
    "per ACO-year."
)

print(
    "PASS - Provider-service data restricted "
    "to selected providers."
)

print(
    "PASS - Original processed data untouched."
)

print("=" * 80)