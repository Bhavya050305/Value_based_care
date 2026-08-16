import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv


# ============================================================
# PROVIDER_COMBINED EXACT DUPLICATE TEST
# ============================================================

print("=" * 75)
print("PROVIDER_COMBINED EXACT DUPLICATE TEST")
print("=" * 75)


# ============================================================
# 1. ENVIRONMENT
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError(
        "Supabase environment variables are missing."
    )


# ============================================================
# 2. CONNECTION
# ============================================================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
)

TABLE_NAME = "provider_combined"

print("\nConnected to Supabase.")


# ============================================================
# 3. FETCH ALL ROWS IN SMALL BATCHES
# ============================================================
#
# IMPORTANT:
# We are now fetching all 68 columns, but only 150,000 rows.
# This is acceptable for this one-time duplicate investigation.
#
# 150,000 x 68 is substantially larger than the earlier
# key-only test, but still manageable for a normal laptop.
#
# We will NOT permanently keep this as our production pipeline.
# ============================================================

print("\nFetching provider_combined in batches...")

all_data = []

batch_size = 1000
start = 0

while True:

    print(
        f"Fetching rows "
        f"{start:,} - {start + batch_size - 1:,}"
    )

    response = (
        supabase
        .table(TABLE_NAME)
        .select("*")
        .range(
            start,
            start + batch_size - 1
        )
        .execute()
    )

    batch = response.data

    if not batch:
        break

    all_data.extend(batch)

    if len(batch) < batch_size:
        break

    start += batch_size


df = pd.DataFrame(all_data)


# ============================================================
# 4. BASIC CHECK
# ============================================================

print("\n" + "=" * 75)
print("DATASET LOADED")
print("=" * 75)

print(f"Rows retrieved    : {len(df):,}")
print(f"Columns retrieved : {len(df.columns):,}")


# ============================================================
# 5. EXACT DUPLICATE ROWS
# ============================================================

print("\n" + "=" * 75)
print("1. EXACT DUPLICATE ROW ANALYSIS")
print("=" * 75)

exact_duplicate_mask = df.duplicated(
    keep=False
)

exact_duplicate_rows = (
    exact_duplicate_mask.sum()
)

unique_rows = (
    df.drop_duplicates()
    .shape[0]
)

duplicate_row_count = (
    len(df) - unique_rows
)

print(
    f"Total rows              : {len(df):,}"
)

print(
    f"Unique complete rows    : {unique_rows:,}"
)

print(
    f"Duplicate extra rows    : {duplicate_row_count:,}"
)

print(
    f"Rows belonging to "
    f"duplicate groups       : "
    f"{exact_duplicate_rows:,}"
)


# ============================================================
# 6. NPI-YEAR DUPLICATES
# ============================================================

print("\n" + "=" * 75)
print("2. NPI-YEAR DUPLICATE ANALYSIS")
print("=" * 75)

npi_year_counts = (
    df
    .groupby(
        ["Rndrng_NPI", "Year"]
    )
    .size()
    .reset_index(name="row_count")
)

duplicate_npi_years = (
    npi_year_counts[
        npi_year_counts["row_count"] > 1
    ]
)

print(
    f"Unique NPI-Year keys    : "
    f"{len(npi_year_counts):,}"
)

print(
    f"Duplicate NPI-Year keys : "
    f"{len(duplicate_npi_years):,}"
)


# ============================================================
# 7. COMPARE EXACT DUPLICATES WITH NPI-YEAR DUPLICATES
# ============================================================

print("\n" + "=" * 75)
print("3. DUPLICATE TYPE COMPARISON")
print("=" * 75)

if duplicate_row_count == 0:

    print(
        "There are NO exact duplicate rows."
    )

else:

    print(
        f"There are {duplicate_row_count:,} "
        f"exact duplicate extra rows."
    )


if len(duplicate_npi_years) > 0:

    print(
        f"There are {len(duplicate_npi_years):,} "
        f"NPI-Year groups containing multiple rows."
    )


# ============================================================
# 8. SAMPLE NPI-YEAR GROUP WITH MULTIPLE ROWS
# ============================================================

print("\n" + "=" * 75)
print("4. SAMPLE NPI-YEAR DUPLICATE GROUP")
print("=" * 75)

if duplicate_npi_years.empty:

    print(
        "No duplicate NPI-Year groups found."
    )

else:

    sample_group = (
        duplicate_npi_years
        .sort_values(
            "row_count",
            ascending=False
        )
        .iloc[0]
    )

    sample_npi = sample_group["Rndrng_NPI"]
    sample_year = sample_group["Year"]

    print(
        f"NPI  : {sample_npi}"
    )

    print(
        f"Year : {sample_year}"
    )

    print(
        f"Rows : {sample_group['row_count']}"
    )

    sample_df = df[
        (df["Rndrng_NPI"] == sample_npi) &
        (df["Year"] == sample_year)
    ].copy()

    print("\nComplete rows:")

    print(
        sample_df
        .to_string(index=False)
    )


# ============================================================
# 9. CHECK WHETHER SAMPLE ROWS ARE IDENTICAL
# ============================================================

print("\n" + "=" * 75)
print("5. SAMPLE GROUP COMPARISON")
print("=" * 75)

if not duplicate_npi_years.empty:

    duplicate_columns = []

    for column in sample_df.columns:

        if sample_df[column].nunique(
            dropna=False
        ) > 1:

            duplicate_columns.append(
                column
            )

    if duplicate_columns:

        print(
            "The sample NPI-Year group "
            "contains DIFFERENT values in:"
        )

        for column in duplicate_columns:
            print(
                f"\n--- {column} ---"
            )

            print(
                sample_df[column]
                .value_counts(dropna=False)
                .to_string()
            )

    else:

        print(
            "The sample NPI-Year group "
            "contains EXACTLY IDENTICAL rows."
        )


# ============================================================
# 10. FINAL DECISION
# ============================================================

print("\n" + "=" * 75)
print("FINAL INTERPRETATION")
print("=" * 75)

if duplicate_row_count > 0:

    print(
        "\nEXACT DUPLICATES EXIST."
    )

    print(
        "We need to determine whether they are "
        "ingestion duplicates before doing anything else."
    )

else:

    print(
        "\nNO EXACT DUPLICATES FOUND."
    )

    print(
        "Therefore repeated NPI-Year rows represent "
        "a real additional dimension or source structure."
    )


print(
    "\nDO NOT AGGREGATE YET."
)

print(
    "DO NOT JOIN YET."
)

print(
    "\nEXACT DUPLICATE TEST COMPLETED."
)