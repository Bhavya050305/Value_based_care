"""
Provider ↔ ACO Mapping Inspection

Purpose:
    Inspect the Supabase database to identify tables that may contain
    the NPI ↔ ACO relationship.

This script DOES NOT modify any database table.

It only:
    1. Connects to Supabase using the existing .env configuration.
    2. Checks known project tables if available.
    3. Attempts to identify tables/columns relevant to:
       - NPI
       - ACO
       - provider
       - year/performance year
    4. Prints useful information for the next mapping step.

IMPORTANT:
    Do not hard-code or print the Supabase service-role key.
"""

import os
import re
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

ENV_PATH = PROJECT_ROOT / ".env"

print("=" * 80)
print("PROVIDER ↔ ACO MAPPING INSPECTION")
print("=" * 80)

print(f"\nProject root: {PROJECT_ROOT}")
print(f".env path:    {ENV_PATH}")

load_dotenv(ENV_PATH)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


# ============================================================
# 2. VALIDATE SUPABASE CREDENTIALS
# ============================================================

print("\n" + "-" * 80)
print("SUPABASE CONNECTION CHECK")
print("-" * 80)

if not SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL was not found in the .env file."
    )

if not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError(
        "SUPABASE_SERVICE_ROLE_KEY was not found in the .env file."
    )

print("SUPABASE_URL: present")
print("SUPABASE_SERVICE_ROLE_KEY: present")


# ============================================================
# 3. CREATE SUPABASE CLIENT
# ============================================================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
)

print("Supabase client created successfully.")


# ============================================================
# 4. KNOWN / LIKELY TABLE NAMES
# ============================================================

# These are candidate names only.
# We are NOT assuming any of them actually exist.

candidate_tables = [
    "provider_by_npi",
    "provider_combined",
    "aco",
    "acos",
    "aco_provider",
    "aco_providers",
    "provider_aco",
    "provider_acos",
    "aco_provider_mapping",
    "provider_aco_mapping",
    "member_attribution",
    "provider_attribution",
]


# ============================================================
# 5. HELPER FUNCTION
# ============================================================

def inspect_table(table_name):
    """
    Attempt to read a very small sample from a Supabase table.

    Returns:
        list of dictionaries if successful
        None if the table cannot be queried
    """

    try:
        response = (
            supabase
            .table(table_name)
            .select("*")
            .limit(2)
            .execute()
        )

        rows = response.data or []

        print(f"\nTABLE: {table_name}")
        print("Status: FOUND")
        print(f"Sample rows returned: {len(rows)}")

        if rows:
            columns = list(rows[0].keys())

            print("Columns:")
            for column in columns:
                print(f"    - {column}")

            print("\nFirst sample row:")
            print(rows[0])

            return rows

        print("Columns: unable to determine because table returned no rows.")

        return []

    except Exception as exc:
        message = str(exc)

        # Keep errors short and useful.
        print(f"\nTABLE: {table_name}")
        print("Status: NOT AVAILABLE / QUERY FAILED")
        print(f"Reason: {message[:300]}")

        return None


# ============================================================
# 6. INSPECT CANDIDATE TABLES
# ============================================================

print("\n" + "=" * 80)
print("CHECKING CANDIDATE TABLES")
print("=" * 80)

found_tables = {}

for table_name in candidate_tables:
    result = inspect_table(table_name)

    if result is not None:
        found_tables[table_name] = result


# ============================================================
# 7. ANALYZE COLUMNS FOR NPI / ACO / YEAR TERMS
# ============================================================

print("\n" + "=" * 80)
print("NPI / ACO / YEAR COLUMN ANALYSIS")
print("=" * 80)

npi_patterns = [
    r"(^|_)npi($|_)",
    r"rndrng",
    r"provider.*npi",
]

aco_patterns = [
    r"(^|_)aco($|_)",
    r"aco.*id",
    r"aco_id",
]

year_patterns = [
    r"(^|_)year($|_)",
    r"performance.*year",
    r"performance_year",
]


def matches_any(column_name, patterns):
    column_lower = column_name.lower()

    return any(
        re.search(pattern, column_lower)
        for pattern in patterns
    )


for table_name, rows in found_tables.items():

    if not rows:
        continue

    columns = list(rows[0].keys())

    npi_columns = [
        col for col in columns
        if matches_any(col, npi_patterns)
    ]

    aco_columns = [
        col for col in columns
        if matches_any(col, aco_patterns)
    ]

    year_columns = [
        col for col in columns
        if matches_any(col, year_patterns)
    ]

    if npi_columns or aco_columns or year_columns:

        print(f"\nTABLE: {table_name}")

        print("Possible NPI columns:")
        if npi_columns:
            for col in npi_columns:
                print(f"    - {col}")
        else:
            print("    None found")

        print("Possible ACO columns:")
        if aco_columns:
            for col in aco_columns:
                print(f"    - {col}")
        else:
            print("    None found")

        print("Possible Year columns:")
        if year_columns:
            for col in year_columns:
                print(f"    - {col}")
        else:
            print("    None found")


# ============================================================
# 8. SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("INSPECTION SUMMARY")
print("=" * 80)

print(f"\nCandidate tables checked: {len(candidate_tables)}")
print(f"Tables successfully queried: {len(found_tables)}")

if found_tables:
    print("\nSuccessfully queried tables:")

    for table_name in found_tables:
        print(f"    - {table_name}")

else:
    print(
        "\nNo candidate table could be queried."
    )

print("\nIMPORTANT:")
print("This script only inspected the database.")
print("No data was inserted, updated, deleted, or modified.")

print("\nNext step:")
print(
    "Use the output to identify the actual NPI ↔ ACO mapping table "
    "before creating the final mapping dataset."
)

print("\n" + "=" * 80)
print("INSPECTION COMPLETE")
print("=" * 80)