import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv


# ============================================================
# PROVIDER_COMBINED - FULL NPI-YEAR GRAIN TEST
# ============================================================

print("=" * 75)
print("PROVIDER_COMBINED FULL NPI-YEAR GRAIN TEST")
print("=" * 75)


# ============================================================
# 1. LOAD ENVIRONMENT
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError(
        "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is missing."
    )


# ============================================================
# 2. CONNECT TO SUPABASE
# ============================================================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
)

TABLE_NAME = "provider_combined"

print("\nConnected to Supabase.")


# ============================================================
# 3. FETCH ONLY NPI + YEAR
# ============================================================

print("\nFetching ONLY NPI + Year columns...")

all_keys = []

batch_size = 1000
start = 0

while True:

    print(
        f"Fetching keys {start:,} "
        f"to {start + batch_size - 1:,}..."
    )

    response = (
        supabase
        .table(TABLE_NAME)
        .select("Rndrng_NPI, Year")
        .range(
            start,
            start + batch_size - 1
        )
        .execute()
    )

    batch = response.data

    if not batch:
        break

    all_keys.extend(batch)

    if len(batch) < batch_size:
        break

    start += batch_size


df = pd.DataFrame(all_keys)

print("\n" + "=" * 75)
print("DATA RETRIEVAL RESULT")
print("=" * 75)

print(
    f"Total NPI-Year rows retrieved: "
    f"{len(df):,}"
)


# ============================================================
# 4. BASIC KEY VALIDATION
# ============================================================

print("\n" + "=" * 75)
print("1. NPI ANALYSIS")
print("=" * 75)

print(
    f"Unique NPIs: "
    f"{df['Rndrng_NPI'].nunique():,}"
)


print("\n" + "=" * 75)
print("2. YEAR ANALYSIS")
print("=" * 75)

print(
    f"Unique Years: "
    f"{df['Year'].nunique():,}"
)

print("\nYear distribution:")

print(
    df["Year"]
    .value_counts(dropna=False)
    .sort_index()
    .to_string()
)


# ============================================================
# 5. NPI + YEAR GRAIN
# ============================================================

print("\n" + "=" * 75)
print("3. FULL NPI + YEAR GRAIN")
print("=" * 75)

npi_year_counts = (
    df
    .groupby(
        ["Rndrng_NPI", "Year"]
    )
    .size()
    .reset_index(name="row_count")
)

print(
    f"Unique NPI-Year keys: "
    f"{len(npi_year_counts):,}"
)

duplicate_keys = npi_year_counts[
    npi_year_counts["row_count"] > 1
]

print(
    f"Duplicate NPI-Year keys: "
    f"{len(duplicate_keys):,}"
)

print(
    f"Maximum rows per NPI-Year: "
    f"{npi_year_counts['row_count'].max():,}"
)


# ============================================================
# 6. DUPLICATE DISTRIBUTION
# ============================================================

print("\n" + "=" * 75)
print("4. NPI-YEAR ROW COUNT DISTRIBUTION")
print("=" * 75)

print(
    npi_year_counts["row_count"]
    .value_counts()
    .sort_index()
    .head(30)
    .to_string()
)


# ============================================================
# 7. SAMPLE DUPLICATE NPI-YEAR KEYS
# ============================================================

print("\n" + "=" * 75)
print("5. SAMPLE DUPLICATE NPI-YEAR KEYS")
print("=" * 75)

if duplicate_keys.empty:

    print("NO DUPLICATE NPI-YEAR KEYS FOUND.")

else:

    print(
        duplicate_keys
        .sort_values(
            "row_count",
            ascending=False
        )
        .head(20)
        .to_string(index=False)
    )


# ============================================================
# 8. CHECK 2020-2024 COVERAGE
# ============================================================

print("\n" + "=" * 75)
print("6. FIVE-YEAR COVERAGE")
print("=" * 75)

expected_years = [2020, 2021, 2022, 2023, 2024]

for year in expected_years:

    count = (
        df["Year"]
        .astype(str)
        .eq(str(year))
        .sum()
    )

    print(
        f"{year}: {count:,} rows"
    )


# ============================================================
# 9. FINAL DECISION
# ============================================================

print("\n" + "=" * 75)
print("7. GRAIN DECISION")
print("=" * 75)

if (
    len(duplicate_keys) == 0
    and len(df) == len(npi_year_counts)
):

    print(
        "RESULT: provider_combined IS UNIQUE "
        "AT NPI + YEAR GRAIN."
    )

else:

    print(
        "RESULT: provider_combined IS NOT UNIQUE "
        "AT NPI + YEAR GRAIN."
    )


print("\n" + "=" * 75)
print("FULL NPI-YEAR GRAIN TEST COMPLETED")
print("=" * 75)