import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# PROVIDER + SERVICE FEATURE VALIDATION
# STEP 3: JOIN KEY + JOIN COVERAGE VALIDATION
# ============================================================


# ------------------------------------------------------------
# PROJECT PATHS
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

ENV_FILE = PROJECT_ROOT / ".env"

CLEANED_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_year_clean.csv"
)


# ------------------------------------------------------------
# LOAD ENVIRONMENT
# ------------------------------------------------------------

load_dotenv(ENV_FILE)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY"
)

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL is missing from .env")

if not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError(
        "SUPABASE_SERVICE_ROLE_KEY is missing from .env"
    )


# ------------------------------------------------------------
# SUPABASE CONNECTION
# ------------------------------------------------------------

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
)


print("=" * 75)
print("PROVIDER + SERVICE FEATURE VALIDATION")
print("STEP 3: JOIN KEY + JOIN COVERAGE VALIDATION")
print("=" * 75)


# ============================================================
# PART 1 — LOAD CLEANED PROVIDER-YEAR DATA
# ============================================================

print("\n" + "=" * 75)
print("1. CLEANED PROVIDER-YEAR DATASET")
print("=" * 75)


if not CLEANED_FILE.exists():
    raise FileNotFoundError(
        f"Cleaned dataset not found:\n{CLEANED_FILE}"
    )


df_clean = pd.read_csv(
    CLEANED_FILE,
    low_memory=False
)


print(f"Rows: {len(df_clean):,}")
print(f"Columns: {len(df_clean.columns):,}")


# ------------------------------------------------------------
# STANDARDIZE KEY TYPES
# ------------------------------------------------------------

df_clean["Rndrng_NPI"] = (
    df_clean["Rndrng_NPI"]
    .astype(str)
    .str.strip()
)


df_clean["Year"] = pd.to_numeric(
    df_clean["Year"],
    errors="coerce"
)


# ------------------------------------------------------------
# CLEANED DATA KEY CHECK
# ------------------------------------------------------------

clean_key_duplicates = (
    df_clean
    .duplicated(
        ["Rndrng_NPI", "Year"]
    )
    .sum()
)


clean_unique_keys = (
    df_clean[
        ["Rndrng_NPI", "Year"]
    ]
    .drop_duplicates()
)


print(
    f"Unique NPI-Year keys: "
    f"{len(clean_unique_keys):,}"
)


print(
    f"Duplicate NPI-Year rows: "
    f"{clean_key_duplicates:,}"
)


# ============================================================
# FUNCTION — FETCH ALL SUPABASE ROWS
# ============================================================

def fetch_all_rows(
    table_name,
    page_size=1000
):
    """
    Fetch all rows from a Supabase table
    using range-based pagination.
    """

    all_rows = []

    start = 0

    while True:

        end = start + page_size - 1

        print(
            f"Fetching {table_name}: "
            f"rows {start:,} - {end:,}"
        )

        response = (
            supabase
            .table(table_name)
            .select("*")
            .range(start, end)
            .execute()
        )

        rows = response.data or []

        if not rows:
            break

        all_rows.extend(rows)

        if len(rows) < page_size:
            break

        start += page_size


    print(
        f"Total fetched from {table_name}: "
        f"{len(all_rows):,}"
    )

    return pd.DataFrame(all_rows)


# ============================================================
# PART 2 — FETCH PROVIDER SERVICE LOOKUP
# ============================================================

print("\n" + "=" * 75)
print("2. FETCH provider_service_lookup")
print("=" * 75)


df_lookup = fetch_all_rows(
    "provider_service_lookup"
)


print(
    f"\nprovider_service_lookup rows: "
    f"{len(df_lookup):,}"
)


# ============================================================
# PART 3 — FETCH PROVIDER BY NPI
# ============================================================

print("\n" + "=" * 75)
print("3. FETCH provider_by_npi")
print("=" * 75)


df_provider = fetch_all_rows(
    "provider_by_npi"
)


print(
    f"\nprovider_by_npi rows: "
    f"{len(df_provider):,}"
)


# ============================================================
# PART 4 — STANDARDIZE LOOKUP KEYS
# ============================================================

print("\n" + "=" * 75)
print("4. STANDARDIZE JOIN KEYS")
print("=" * 75)


df_lookup["Rndrng_NPI"] = (
    df_lookup["Rndrng_NPI"]
    .astype(str)
    .str.strip()
)


df_lookup["performance_year"] = pd.to_numeric(
    df_lookup["performance_year"],
    errors="coerce"
)


df_provider["Rndrng_NPI"] = (
    df_provider["Rndrng_NPI"]
    .astype(str)
    .str.strip()
)


df_provider["Year"] = pd.to_numeric(
    df_provider["Year"],
    errors="coerce"
)


print("Lookup key:")
print("  Rndrng_NPI + performance_year")


print("\nProvider key:")
print("  Rndrng_NPI + Year")


# ============================================================
# PART 5 — CHECK LOOKUP GRAIN
# ============================================================

print("\n" + "=" * 75)
print("5. provider_service_lookup GRAIN")
print("=" * 75)


lookup_duplicate_count = (
    df_lookup
    .duplicated(
        ["Rndrng_NPI", "performance_year"]
    )
    .sum()
)


lookup_unique_keys = (
    df_lookup[
        ["Rndrng_NPI", "performance_year"]
    ]
    .drop_duplicates()
)


print(
    f"Rows: {len(df_lookup):,}"
)


print(
    f"Unique NPI-Year keys: "
    f"{len(lookup_unique_keys):,}"
)


print(
    f"Duplicate NPI-Year rows: "
    f"{lookup_duplicate_count:,}"
)


# ============================================================
# PART 6 — CHECK PROVIDER_BY_NPI GRAIN
# ============================================================

print("\n" + "=" * 75)
print("6. provider_by_npi GRAIN")
print("=" * 75)


provider_duplicate_count = (
    df_provider
    .duplicated(
        ["Rndrng_NPI", "Year"]
    )
    .sum()
)


provider_unique_keys = (
    df_provider[
        ["Rndrng_NPI", "Year"]
    ]
    .drop_duplicates()
)


print(
    f"Rows: {len(df_provider):,}"
)


print(
    f"Unique NPI-Year keys: "
    f"{len(provider_unique_keys):,}"
)


print(
    f"Duplicate NPI-Year rows: "
    f"{provider_duplicate_count:,}"
)


# ============================================================
# PART 7 — BUILD STANDARDIZED KEYS
# ============================================================

print("\n" + "=" * 75)
print("7. BUILD STANDARDIZED NPI-YEAR KEYS")
print("=" * 75)


clean_keys = set(
    zip(
        clean_unique_keys["Rndrng_NPI"],
        clean_unique_keys["Year"]
    )
)


lookup_keys = set(
    zip(
        lookup_unique_keys["Rndrng_NPI"],
        lookup_unique_keys[
            "performance_year"
        ]
    )
)


provider_keys = set(
    zip(
        provider_unique_keys["Rndrng_NPI"],
        provider_unique_keys["Year"]
    )
)


print(
    f"Cleaned dataset keys: "
    f"{len(clean_keys):,}"
)


print(
    f"Lookup keys: "
    f"{len(lookup_keys):,}"
)


print(
    f"Provider-by-NPI keys: "
    f"{len(provider_keys):,}"
)


# ============================================================
# PART 8 — LOOKUP VS CLEANED DATA
# ============================================================

print("\n" + "=" * 75)
print("8. LOOKUP VS CLEANED DATA")
print("=" * 75)


lookup_clean_overlap = (
    lookup_keys
    & clean_keys
)


lookup_only = (
    lookup_keys
    - clean_keys
)


clean_only = (
    clean_keys
    - lookup_keys
)


print(
    f"Matching keys: "
    f"{len(lookup_clean_overlap):,}"
)


print(
    f"Lookup-only keys: "
    f"{len(lookup_only):,}"
)


print(
    f"Cleaned-only keys: "
    f"{len(clean_only):,}"
)


if len(clean_keys) > 0:

    coverage = (
        len(lookup_clean_overlap)
        / len(clean_keys)
        * 100
    )

    print(
        f"\nLookup coverage of cleaned dataset: "
        f"{coverage:.2f}%"
    )


# ============================================================
# PART 9 — PROVIDER TABLE VS CLEANED DATA
# ============================================================

print("\n" + "=" * 75)
print("9. PROVIDER_BY_NPI VS CLEANED DATA")
print("=" * 75)


provider_clean_overlap = (
    provider_keys
    & clean_keys
)


provider_only = (
    provider_keys
    - clean_keys
)


print(
    f"Matching keys: "
    f"{len(provider_clean_overlap):,}"
)


print(
    f"Provider-table-only keys: "
    f"{len(provider_only):,}"
)


if len(clean_keys) > 0:

    provider_coverage = (
        len(provider_clean_overlap)
        / len(clean_keys)
        * 100
    )

    print(
        f"\nProvider table coverage: "
        f"{provider_coverage:.2f}%"
    )


# ============================================================
# PART 10 — LOOKUP VS PROVIDER TABLE
# ============================================================

print("\n" + "=" * 75)
print("10. LOOKUP VS PROVIDER_BY_NPI")
print("=" * 75)


lookup_provider_overlap = (
    lookup_keys
    & provider_keys
)


lookup_provider_only = (
    lookup_keys
    - provider_keys
)


provider_lookup_only = (
    provider_keys
    - lookup_keys
)


print(
    f"Matching keys: "
    f"{len(lookup_provider_overlap):,}"
)


print(
    f"Lookup-only keys: "
    f"{len(lookup_provider_only):,}"
)


print(
    f"Provider-only keys: "
    f"{len(provider_lookup_only):,}"
)


if len(provider_keys) > 0:

    service_coverage = (
        len(lookup_provider_overlap)
        / len(provider_keys)
        * 100
    )

    print(
        f"\nService lookup coverage of "
        f"provider table: "
        f"{service_coverage:.2f}%"
    )


# ============================================================
# PART 11 — YEAR DISTRIBUTION
# ============================================================

print("\n" + "=" * 75)
print("11. YEAR DISTRIBUTION")
print("=" * 75)


print("\nCleaned dataset:")

print(
    df_clean["Year"]
    .value_counts()
    .sort_index()
    .to_string()
)


print("\nProvider-by-NPI:")

print(
    df_provider["Year"]
    .value_counts()
    .sort_index()
    .to_string()
)


print("\nService lookup:")

print(
    df_lookup["performance_year"]
    .value_counts()
    .sort_index()
    .to_string()
)


# ============================================================
# PART 12 — FINAL DECISION INFORMATION
# ============================================================

print("\n" + "=" * 75)
print("12. JOIN VALIDATION SUMMARY")
print("=" * 75)


print(
    "\nCandidate join:"
)


print(
    "provider_year_clean.Rndrng_NPI"
    "  ↔  provider_service_lookup.Rndrng_NPI"
)


print(
    "provider_year_clean.Year"
    "  ↔  provider_service_lookup.performance_year"
)


print(
    "\nprovider_by_npi candidate join:"
)


print(
    "provider_year_clean.Rndrng_NPI"
    "  ↔  provider_by_npi.Rndrng_NPI"
)


print(
    "provider_year_clean.Year"
    "  ↔  provider_by_npi.Year"
)


print(
    "\nNO JOIN HAS BEEN PERFORMED."
)


print(
    "This step only validates keys, "
    "grain and coverage."
)


print("\n" + "=" * 75)
print("STEP 3 JOIN VALIDATION COMPLETE")
print("=" * 75)