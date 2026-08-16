import os

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY"
)

TABLE_NAME = "provider_combined"

PAGE_SIZE = 1000


# =========================================================
# SUPABASE CONNECTION
# =========================================================

def create_supabase_client():

    if not SUPABASE_URL:
        raise ValueError(
            "SUPABASE_URL is missing from .env"
        )

    if not SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError(
            "SUPABASE_SERVICE_ROLE_KEY is missing from .env"
        )

    return create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY
    )


# =========================================================
# DATABASE ROW COUNT
# =========================================================

def get_database_row_count(client):

    response = (
        client
        .table(TABLE_NAME)
        .select(
            "Rndrng_NPI",
            count="exact"
        )
        .limit(1)
        .execute()
    )

    return response.count


# =========================================================
# FETCH ONE PAGE
# =========================================================

def fetch_page(
    client,
    start,
    end
):

    response = (
        client
        .table(TABLE_NAME)
        .select(
            "Rndrng_NPI,Year"
        )
        .order("Rndrng_NPI")
        .order("Year")
        .range(start, end)
        .execute()
    )

    return response.data


# =========================================================
# PAGINATION TEST
# =========================================================

def test_full_npi_year_extraction(client):

    print("\n" + "=" * 60)
    print("FULL 150,000 ROW NPI-YEAR VALIDATION")
    print("=" * 60)

    all_rows = []

    start = 0

    while True:

        end = start + PAGE_SIZE - 1

        print(
            f"Fetching rows {start:,} - {end:,}...",
            end="\r"
        )

        response = (
            client
            .table(TABLE_NAME)
            .select(
                "Rndrng_NPI,Year"
            )
            .order("Rndrng_NPI")
            .order("Year")
            .range(start, end)
            .execute()
        )

        rows = response.data

        if not rows:
            break

        all_rows.extend(rows)

        if len(rows) < PAGE_SIZE:
            break

        start += PAGE_SIZE

    print()

    df = pd.DataFrame(all_rows)

    print("\n" + "=" * 60)
    print("FULL EXTRACTION RESULTS")
    print("=" * 60)

    print(
        "Rows extracted:",
        f"{len(df):,}"
    )

    print(
        "Expected database rows:",
        f"{150000:,}"
    )

    # -----------------------------------------------------
    # Row count validation
    # -----------------------------------------------------

    if len(df) == 150000:

        print(
            "Row count validation: PASSED"
        )

    else:

        print(
            "Row count validation: FAILED"
        )

    # -----------------------------------------------------
    # Unique NPI count
    # -----------------------------------------------------

    unique_npi_count = (
        df["Rndrng_NPI"]
        .nunique()
    )

    print(
        "Unique NPIs:",
        f"{unique_npi_count:,}"
    )

    # -----------------------------------------------------
    # Unique NPI-Year
    # -----------------------------------------------------

    unique_npi_year_count = (
        df[
            [
                "Rndrng_NPI",
                "Year"
            ]
        ]
        .drop_duplicates()
        .shape[0]
    )

    print(
        "Unique NPI-Year combinations:",
        f"{unique_npi_year_count:,}"
    )

    # -----------------------------------------------------
    # Duplicate NPI-Year groups
    # -----------------------------------------------------

    group_counts = (
        df
        .groupby(
            [
                "Rndrng_NPI",
                "Year"
            ]
        )
        .size()
    )

    duplicate_groups = (
        group_counts[
            group_counts > 1
        ]
    )

    print(
        "Duplicate NPI-Year groups:",
        f"{len(duplicate_groups):,}"
    )

    # -----------------------------------------------------
    # Rows participating in duplicate groups
    # -----------------------------------------------------

    duplicate_rows = int(
        df.duplicated(
            subset=[
                "Rndrng_NPI",
                "Year"
            ],
            keep=False
        ).sum()
    )

    print(
        "Rows participating in duplicate NPI-Year groups:",
        f"{duplicate_rows:,}"
    )

    # -----------------------------------------------------
    # Maximum rows per NPI-Year
    # -----------------------------------------------------

    if len(duplicate_groups) > 0:

        print(
            "Maximum rows for one NPI-Year:",
            int(duplicate_groups.max())
        )

    else:

        print(
            "Maximum rows for one NPI-Year: 1"
        )

    # -----------------------------------------------------
    # Year distribution
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("YEAR DISTRIBUTION")
    print("=" * 60)

    year_distribution = (
        df["Year"]
        .value_counts()
        .sort_index()
    )

    for year, count in year_distribution.items():

        print(
            f"{year}: {count:,} rows"
        )

    # -----------------------------------------------------
    # Final interpretation
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL NPI-YEAR GRAIN RESULT")
    print("=" * 60)

    if len(duplicate_groups) == 0:

        print(
            "RESULT: NPI + Year IS UNIQUE "
            "across the full 150,000 rows."
        )

    else:

        print(
            "RESULT: NPI + Year IS NOT UNIQUE "
            "across the full 150,000 rows."
        )

        print(
            "DO NOT aggregate or join yet."
        )

    return df

    # -----------------------------------------------------
    # Check whether page boundaries overlap
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("PAGE OVERLAP TEST")
    print("=" * 60)

    overlap_found = False

    for i in range(len(pages) - 1):

        current_page = pages[i]
        next_page = pages[i + 1]

        current_keys = set(
            zip(
                current_page["Rndrng_NPI"],
                current_page["Year"]
            )
        )

        next_keys = set(
            zip(
                next_page["Rndrng_NPI"],
                next_page["Year"]
            )
        )

        overlap = (
            current_keys
            .intersection(next_keys)
        )

        if overlap:

            overlap_found = True

            print(
                f"Overlap between page {i + 1} "
                f"and page {i + 2}: "
                f"{len(overlap):,} NPI-Year keys"
            )

    if not overlap_found:

        print(
            "No NPI-Year overlap detected "
            "between tested pages."
        )

    return combined_df


# =========================================================
# COMPARE TWO EXTRACTIONS
# =========================================================

def compare_extractions(client):

    print("\n" + "=" * 60)
    print("REPEATED EXTRACTION CONSISTENCY TEST")
    print("=" * 60)

    first_rows = fetch_page(
        client,
        0,
        PAGE_SIZE - 1
    )

    second_rows = fetch_page(
        client,
        0,
        PAGE_SIZE - 1
    )

    first_df = pd.DataFrame(first_rows)
    second_df = pd.DataFrame(second_rows)

    first_keys = list(
        zip(
            first_df["Rndrng_NPI"],
            first_df["Year"]
        )
    )

    second_keys = list(
        zip(
            second_df["Rndrng_NPI"],
            second_df["Year"]
        )
    )

    print(
        "First extraction rows:",
        len(first_df)
    )

    print(
        "Second extraction rows:",
        len(second_df)
    )

    print(
        "First 1,000 rows identical:",
        first_keys == second_keys
    )

    if first_keys != second_keys:

        print(
            "\nWARNING:"
        )

        print(
            "The same database page returned "
            "different records between requests."
        )

        print(
            "Pagination is NOT deterministic."
        )

    else:

        print(
            "\nThe first page is deterministic "
            "for this test."
        )


# =========================================================
# MAIN
# =========================================================

def main():

    print("=" * 60)
    print("PROVIDER_COMBINED EXTRACTION VALIDATION")
    print("=" * 60)

    client = create_supabase_client()

    print(
        "\nConnected to Supabase."
    )

    # -----------------------------------------------------
    # Database count
    # -----------------------------------------------------

    database_count = get_database_row_count(
        client
    )

    print("\n" + "=" * 60)
    print("DATABASE ROW COUNT")
    print("=" * 60)

    print(
        "Database reports:",
        f"{database_count:,} rows"
    )

    # -----------------------------------------------------
    # Pagination test
    # -----------------------------------------------------

    test_full_npi_year_extraction(
    client
)
    # -----------------------------------------------------
    # Repeated extraction test
    # -----------------------------------------------------

    compare_extractions(
        client
    )

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("EXTRACTION VALIDATION COMPLETED")
    print("=" * 60)

    print(
        "\nIMPORTANT:"
    )

    print(
        "This script does NOT modify the database."
    )

    print(
        "This script does NOT remove duplicates."
    )

    print(
        "This script only tests extraction consistency."
    )


if __name__ == "__main__":
    main()