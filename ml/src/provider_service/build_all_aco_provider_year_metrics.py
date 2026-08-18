from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

MAPPING_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "all_aco"
    / "aco_provider_mapping.csv"
)

PROVIDER_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "provider_service"
    / "provider_combined_clean.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "all_aco"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "provider_aco_year_metrics.csv"
)


# ============================================================
# START
# ============================================================

print("=" * 80)
print("BHAVYA VBC")
print("=" * 80)
print("ALL-ACO PROVIDER-YEAR METRICS")
print("=" * 80)


# ============================================================
# CHECK INPUT FILES
# ============================================================

print("\nChecking input files...")

if not MAPPING_FILE.exists():
    raise FileNotFoundError(
        f"ACO-provider mapping not found:\n{MAPPING_FILE}"
    )

print(f"OK  {MAPPING_FILE}")

if not PROVIDER_FILE.exists():
    raise FileNotFoundError(
        f"Provider dataset not found:\n{PROVIDER_FILE}"
    )

print(f"OK  {PROVIDER_FILE}")


# ============================================================
# LOAD ACO-PROVIDER MAPPING
# ============================================================

print("\n" + "=" * 80)
print("[1/7] LOADING ALL-ACO PROVIDER MAPPING")
print("=" * 80)

mapping = pd.read_csv(
    MAPPING_FILE,
    low_memory=False
)

required_mapping_columns = [
    "ACO_ID",
    "Rndrng_NPI"
]

missing_mapping_columns = [
    c
    for c in required_mapping_columns
    if c not in mapping.columns
]

if missing_mapping_columns:
    raise ValueError(
        "Missing required mapping columns: "
        f"{missing_mapping_columns}"
    )


# ------------------------------------------------------------
# Clean identifiers
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
    mapping["ACO_ID"].notna()
    & (mapping["ACO_ID"] != "")
    & mapping["Rndrng_NPI"].notna()
    & (mapping["Rndrng_NPI"] != "")
].copy()


# ------------------------------------------------------------
# Remove exact duplicate mapping rows
# ------------------------------------------------------------

mapping = mapping.drop_duplicates(
    subset=[
        "ACO_ID",
        "Rndrng_NPI"
    ]
).reset_index(drop=True)


expected_acos = (
    mapping["ACO_ID"]
    .nunique()
)

expected_providers = (
    mapping["Rndrng_NPI"]
    .nunique()
)


print(
    f"Mapping rows      : {len(mapping):,}"
)

print(
    f"Unique ACOs       : {expected_acos:,}"
)

print(
    f"Unique providers  : {expected_providers:,}"
)


# ============================================================
# VALIDATE PROVIDER → ACO MAPPING
# ============================================================

print("\n" + "=" * 80)
print("[2/7] VALIDATING PROVIDER → ACO MAPPING")
print("=" * 80)


provider_aco_counts = (
    mapping
    .groupby("Rndrng_NPI")["ACO_ID"]
    .nunique()
)

multiple_aco_providers = (
    provider_aco_counts[
        provider_aco_counts > 1
    ]
)


print(
    "Providers assigned to multiple ACOs: "
    f"{len(multiple_aco_providers):,}"
)

if len(multiple_aco_providers) != 0:

    print(
        "\nERROR: Some providers are assigned "
        "to multiple ACOs."
    )

    print(
        multiple_aco_providers.head(20)
    )

    raise ValueError(
        "Provider-to-ACO mapping is not one-to-one."
    )


duplicate_mapping_pairs = (
    mapping[
        [
            "ACO_ID",
            "Rndrng_NPI"
        ]
    ]
    .duplicated()
    .sum()
)

print(
    "Duplicate ACO-provider pairs: "
    f"{duplicate_mapping_pairs:,}"
)

if duplicate_mapping_pairs != 0:

    raise ValueError(
        "Duplicate ACO-provider mapping pairs detected."
    )


print("PASS - Provider → ACO mapping is valid.")


# ============================================================
# LOAD PROVIDER DATA
# ============================================================

print("\n" + "=" * 80)
print("[3/7] LOADING PROVIDER-YEAR DATA")
print("=" * 80)

provider = pd.read_csv(
    PROVIDER_FILE,
    low_memory=False
)


required_provider_columns = [
    "Rndrng_NPI",
    "Year"
]

missing_provider_columns = [
    c
    for c in required_provider_columns
    if c not in provider.columns
]

if missing_provider_columns:

    raise ValueError(
        "Missing required provider columns: "
        f"{missing_provider_columns}"
    )


# ------------------------------------------------------------
# Clean NPI
# ------------------------------------------------------------

provider["Rndrng_NPI"] = (
    provider["Rndrng_NPI"]
    .astype(str)
    .str.strip()
)


# ------------------------------------------------------------
# Clean Year
# ------------------------------------------------------------

provider["Year"] = pd.to_numeric(
    provider["Year"],
    errors="coerce"
)


# ------------------------------------------------------------
# Remove invalid rows
# ------------------------------------------------------------

provider = provider[
    provider["Rndrng_NPI"].notna()
    & (provider["Rndrng_NPI"] != "")
    & provider["Year"].notna()
].copy()


provider["Year"] = (
    provider["Year"]
    .astype(int)
)


print(
    f"Provider rows     : {len(provider):,}"
)

print(
    f"Unique providers  : "
    f"{provider['Rndrng_NPI'].nunique():,}"
)

print(
    f"Years             : "
    f"{sorted(provider['Year'].unique().tolist())}"
)


# ============================================================
# VALIDATE PROVIDER-YEAR GRAIN
# ============================================================

print("\n" + "=" * 80)
print("[4/7] VALIDATING PROVIDER-YEAR GRAIN")
print("=" * 80)


duplicate_provider_year = (
    provider
    .duplicated(
        [
            "Rndrng_NPI",
            "Year"
        ]
    )
    .sum()
)


print(
    "Duplicate NPI-Year rows: "
    f"{duplicate_provider_year:,}"
)


if duplicate_provider_year != 0:

    raise ValueError(
        "Provider dataset contains duplicate "
        "NPI-Year rows."
    )


print(
    "PASS - Provider dataset is unique at "
    "NPI-Year grain."
)


# ============================================================
# JOIN ACO MAPPING WITH PROVIDER-YEAR DATA
# ============================================================

print("\n" + "=" * 80)
print("[5/7] JOINING ACO MAPPING WITH PROVIDER-YEAR DATA")
print("=" * 80)


result = mapping.merge(
    provider,
    on="Rndrng_NPI",
    how="inner",
    suffixes=(
        "",
        "_provider"
    )
)


print(
    f"Joined rows      : {len(result):,}"
)

print(
    f"Joined ACOs      : "
    f"{result['ACO_ID'].nunique():,}"
)

print(
    f"Joined providers : "
    f"{result['Rndrng_NPI'].nunique():,}"
)

print(
    f"Joined years     : "
    f"{sorted(result['Year'].unique().tolist())}"
)


# ============================================================
# CHECK FOR UNMAPPED PROVIDERS
# ============================================================

mapped_provider_set = set(
    mapping["Rndrng_NPI"]
)

provider_set = set(
    provider["Rndrng_NPI"]
)

unmapped_provider_count = len(
    provider_set - mapped_provider_set
)

print(
    "\nProviders in provider dataset without "
    "an ACO mapping: "
    f"{unmapped_provider_count:,}"
)


if unmapped_provider_count != 0:

    print(
        "WARNING - Some provider records do not "
        "have an ACO mapping."
    )

else:

    print(
        "PASS - Every provider has an ACO mapping."
    )


# ============================================================
# BUILD PROVIDER NAME
# ============================================================

print("\n" + "=" * 80)
print("[6/7] BUILDING PROVIDER-YEAR DATASET")
print("=" * 80)


# ------------------------------------------------------------
# Use provider source name fields when available
# ------------------------------------------------------------

first_name_col = (
    "Rndrng_Prvdr_First_Name"
)

last_name_col = (
    "Rndrng_Prvdr_Last_Org_Name"
)


if (
    first_name_col in result.columns
    and last_name_col in result.columns
):

    result["provider_name"] = (
        result[first_name_col]
        .fillna("")
        .astype(str)
        .str.strip()
        + " "
        + result[last_name_col]
        .fillna("")
        .astype(str)
        .str.strip()
    ).str.strip()

else:

    result["provider_name"] = (
        "Provider_"
        + result["Rndrng_NPI"].astype(str)
    )


# ------------------------------------------------------------
# Remove inherited duplicate provider_name
# ------------------------------------------------------------

if "provider_name_provider" in result.columns:

    result = result.drop(
        columns=[
            "provider_name_provider"
        ]
    )


# ------------------------------------------------------------
# Remove inherited performance_year
# ------------------------------------------------------------

if "performance_year" in result.columns:

    result = result.drop(
        columns=[
            "performance_year"
        ]
    )


# ------------------------------------------------------------
# Ensure Year is integer
# ------------------------------------------------------------

result["Year"] = pd.to_numeric(
    result["Year"],
    errors="coerce"
)

result = result[
    result["Year"].notna()
].copy()

result["Year"] = (
    result["Year"]
    .astype(int)
)


# ============================================================
# SORT
# ============================================================

result = result.sort_values(
    [
        "ACO_ID",
        "Year",
        "Rndrng_NPI"
    ]
).reset_index(
    drop=True
)


# ============================================================
# FINAL GRAIN VALIDATION
# ============================================================

print("\nFinal validation...")


duplicate_final = (
    result
    .duplicated(
        [
            "ACO_ID",
            "Rndrng_NPI",
            "Year"
        ]
    )
    .sum()
)


missing_aco = (
    result["ACO_ID"]
    .isna()
    .sum()
)


missing_npi = (
    result["Rndrng_NPI"]
    .isna()
    .sum()
)


missing_year = (
    result["Year"]
    .isna()
    .sum()
)


actual_acos = (
    result["ACO_ID"]
    .nunique()
)

actual_providers = (
    result["Rndrng_NPI"]
    .nunique()
)

actual_years = sorted(
    result["Year"]
    .dropna()
    .unique()
    .tolist()
)


print(
    f"Final rows                 : "
    f"{len(result):,}"
)

print(
    f"Unique ACOs                : "
    f"{actual_acos:,}"
)

print(
    f"Unique providers           : "
    f"{actual_providers:,}"
)

print(
    f"Unique years               : "
    f"{actual_years}"
)

print(
    f"Duplicate ACO-NPI-Year     : "
    f"{duplicate_final:,}"
)

print(
    f"Missing ACO_ID             : "
    f"{missing_aco:,}"
)

print(
    f"Missing NPI                : "
    f"{missing_npi:,}"
)

print(
    f"Missing Year               : "
    f"{missing_year:,}"
)


# ============================================================
# ACO-YEAR PROVIDER COVERAGE
# ============================================================

print("\n" + "-" * 80)
print("ACO-YEAR PROVIDER COVERAGE")
print("-" * 80)


aco_year_provider_counts = (
    result
    .groupby(
        [
            "ACO_ID",
            "Year"
        ]
    )["Rndrng_NPI"]
    .nunique()
)


print(
    f"ACO-year combinations: "
    f"{len(aco_year_provider_counts):,}"
)

print(
    "\nProvider counts per ACO-year:"
)

print(
    aco_year_provider_counts
    .describe()
)


# ============================================================
# COVERAGE BY ACO
# ============================================================

print("\n" + "-" * 80)
print("ACO COVERAGE")
print("-" * 80)


years_per_aco = (
    result
    .groupby("ACO_ID")["Year"]
    .nunique()
)


print(
    f"Minimum years per ACO: "
    f"{years_per_aco.min()}"
)

print(
    f"Maximum years per ACO: "
    f"{years_per_aco.max()}"
)


# ============================================================
# HARD ASSERTIONS
# ============================================================

print("\n" + "=" * 80)
print("HARD VALIDATION")
print("=" * 80)


assert duplicate_final == 0, (
    "Duplicate ACO-NPI-Year rows detected."
)


assert missing_aco == 0, (
    "Missing ACO_ID detected."
)


assert missing_npi == 0, (
    "Missing NPI detected."
)


assert missing_year == 0, (
    "Missing Year detected."
)


# ------------------------------------------------------------
# Dynamic ACO validation
# ------------------------------------------------------------

assert actual_acos == expected_acos, (
    f"ACO coverage mismatch. "
    f"Expected {expected_acos}, "
    f"found {actual_acos}."
)


# ------------------------------------------------------------
# Mapping provider validation
# ------------------------------------------------------------

assert actual_providers <= expected_providers, (
    "Result contains more providers than mapping."
)


# ------------------------------------------------------------
# ACO-year validation
# ------------------------------------------------------------

expected_aco_years = (
    expected_acos
    * len(actual_years)
)

actual_aco_years = (
    len(aco_year_provider_counts)
)


print(
    f"Expected ACO-years: "
    f"{expected_aco_years:,}"
)

print(
    f"Actual ACO-years  : "
    f"{actual_aco_years:,}"
)


if actual_aco_years != expected_aco_years:

    print(
        "WARNING - Not every ACO is represented "
        "for every provider year."
    )

else:

    print(
        "PASS - Every ACO-year combination "
        "is represented."
    )


# ============================================================
# PROVIDER DISTRIBUTION
# ============================================================

print("\n" + "-" * 80)
print("PROVIDER DISTRIBUTION BY ACO")
print("-" * 80)


providers_per_aco = (
    result
    .groupby("ACO_ID")["Rndrng_NPI"]
    .nunique()
)


print(
    providers_per_aco.describe()
)


# ============================================================
# SAVE
# ============================================================

print("\n" + "=" * 80)
print("SAVING ALL-ACO PROVIDER-YEAR METRICS")
print("=" * 80)


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


result.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    f"Output : {OUTPUT_FILE}"
)

print(
    f"Rows   : {len(result):,}"
)

print(
    f"ACOs   : {result['ACO_ID'].nunique():,}"
)

print(
    f"NPIs   : {result['Rndrng_NPI'].nunique():,}"
)

print(
    f"Years  : {sorted(result['Year'].unique().tolist())}"
)


# ============================================================
# FINAL STATUS
# ============================================================

print("\n" + "=" * 80)
print("BUILD COMPLETE")
print("=" * 80)

print(
    "PASS - All mapped ACOs preserved."
)

print(
    "PASS - Provider-year grain validated."
)

print(
    "PASS - ACO-NPI-Year grain validated."
)

print(
    "PASS - Dynamic ACO validation used."
)

print(
    "PASS - Original processed provider data untouched."
)

print("=" * 80)