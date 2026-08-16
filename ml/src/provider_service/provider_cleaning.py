import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

TABLE_NAME = "provider_combined"

# IMPORTANT:
# This is a cleaned provider_combined dataset.
# We are NOT claiming NPI + Year is the final grain yet.
OUTPUT_PATH = Path(
    "data/processed/provider_service/provider_combined_clean.csv"
)


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
# FETCH ALL PROVIDER RECORDS
# =========================================================

def fetch_all_records(
    client,
    table_name,
    page_size=1000
):
    """
    Fetch the complete provider_combined table
    using deterministic pagination ordering.

    The Supabase source table is read-only.
    No records are modified.
    """

    all_rows = []
    start = 0

    print("\n" + "=" * 60)
    print("FETCHING PROVIDER_COMBINED")
    print("=" * 60)

    while True:

        end = start + page_size - 1

        response = (
            client
            .table(table_name)
            .select("*")
            .order("Rndrng_NPI")
            .order("Year")
            .order("Rndrng_Prvdr_Type")
            .order("Rndrng_Prvdr_State_Abrvtn")
            .order("Tot_HCPCS_Cds")
            .order("Tot_Benes")
            .order("Tot_Srvcs")
            .order("Tot_Mdcr_Alowd_Amt")
            .order("Tot_Mdcr_Pymt_Amt")
            .order("Tot_Mdcr_Stdzd_Amt")
            .range(start, end)
            .execute()
        )

        rows = response.data

        if not rows:
            break

        all_rows.extend(rows)

        print(
            f"Fetched: {len(all_rows):,} rows",
            end="\r"
        )

        if len(rows) < page_size:
            break

        start += page_size

    print()

    return pd.DataFrame(all_rows)


# =========================================================
# VALIDATE REQUIRED COLUMNS
# =========================================================

def validate_required_columns(df):

    required_columns = [
        "Rndrng_NPI",
        "Year"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


# =========================================================
# CLEAN PROVIDER DATA
# =========================================================

def clean_provider_data(df):

    validate_required_columns(df)

    print("\n" + "=" * 60)
    print("BEFORE CLEANING")
    print("=" * 60)

    print(
        "Total rows:",
        f"{len(df):,}"
    )

    print(
        "Total columns:",
        f"{len(df.columns):,}"
    )

    # -----------------------------------------------------
    # Year validation
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("YEAR VALIDATION")
    print("=" * 60)

    df["Year"] = pd.to_numeric(
        df["Year"],
        errors="coerce"
    )

    null_year_count = int(
        df["Year"].isna().sum()
    )

    print(
        "Null/invalid Year values:",
        null_year_count
    )

    if null_year_count > 0:

        raise ValueError(
            "Null or invalid Year values detected. "
            "Cleaning stopped."
        )

    # Convert to integer after validation
    df["Year"] = df["Year"].astype(int)

    detected_years = sorted(
        df["Year"].unique()
    )

    print(
        "Years detected:",
        detected_years
    )

    # -----------------------------------------------------
    # NPI validation
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("NPI VALIDATION")
    print("=" * 60)

    df["Rndrng_NPI"] = (
        df["Rndrng_NPI"]
        .astype(str)
        .str.strip()
    )

    invalid_npi_mask = df[
        "Rndrng_NPI"
    ].isin(
        ["", "nan", "None"]
    )

    invalid_npi_count = int(
        invalid_npi_mask.sum()
    )

    print(
        "Null/invalid NPI values:",
        invalid_npi_count
    )

    if invalid_npi_count > 0:

        raise ValueError(
            "Null or invalid NPI values detected. "
            "Cleaning stopped."
        )

    # -----------------------------------------------------
    # EXACT DUPLICATE DETECTION
    # -----------------------------------------------------
    #
    # IMPORTANT:
    # We compare ALL columns.
    #
    # We do NOT use:
    #     subset=["NPI", "Year"]
    #
    # We do NOT use a manually selected subset of columns.
    #
    # Only fully identical records are considered
    # exact duplicates.
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("EXACT DUPLICATE VALIDATION")
    print("=" * 60)

    exact_duplicate_mask = df.duplicated(
        keep=False
    )

    exact_duplicate_rows = int(
        exact_duplicate_mask.sum()
    )

    exact_duplicate_extra_rows = int(
        df.duplicated(
            keep="first"
        ).sum()
    )

    print(
        "Rows belonging to exact duplicate groups:",
        f"{exact_duplicate_rows:,}"
    )

    print(
        "Exact duplicate rows that can be removed:",
        f"{exact_duplicate_extra_rows:,}"
    )

    # -----------------------------------------------------
    # REMOVE ONLY FULLY IDENTICAL ROWS
    # -----------------------------------------------------

    clean_df = df.drop_duplicates(
        keep="first"
    ).copy()

    print("\n" + "=" * 60)
    print("AFTER EXACT DUPLICATE REMOVAL")
    print("=" * 60)

    print(
        "Rows before cleaning:",
        f"{len(df):,}"
    )

    print(
        "Rows after exact duplicate removal:",
        f"{len(clean_df):,}"
    )

    print(
        "Rows removed:",
        f"{len(df) - len(clean_df):,}"
    )

    # -----------------------------------------------------
    # NPI + YEAR GRAIN INSPECTION
    # -----------------------------------------------------
    #
    # IMPORTANT:
    # We are NOT assuming NPI + Year is the final grain.
    #
    # If duplicates exist, we report them.
    # We do NOT remove them.
    # We do NOT aggregate them.
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("NPI + YEAR GRAIN INSPECTION")
    print("=" * 60)

    npi_year_duplicate_mask = clean_df.duplicated(
        subset=[
            "Rndrng_NPI",
            "Year"
        ],
        keep=False
    )

    duplicate_npi_year_rows = int(
        npi_year_duplicate_mask.sum()
    )

    unique_npi_year_count = (
        clean_df[
            [
                "Rndrng_NPI",
                "Year"
            ]
        ]
        .drop_duplicates()
        .shape[0]
    )

    npi_year_group_count = (
        clean_df
        .groupby(
            [
                "Rndrng_NPI",
                "Year"
            ]
        )
        .size()
    )

    duplicate_npi_year_groups = (
        npi_year_group_count[
            npi_year_group_count > 1
        ]
    )

    print(
        "Unique NPI-Year combinations:",
        f"{unique_npi_year_count:,}"
    )

    print(
        "Duplicate NPI-Year groups:",
        f"{len(duplicate_npi_year_groups):,}"
    )

    print(
        "Rows participating in duplicate NPI-Year groups:",
        f"{duplicate_npi_year_rows:,}"
    )

    if len(duplicate_npi_year_groups) > 0:

        print(
            "\nNPI + Year is NOT currently unique."
        )

        print(
            "This is recorded for investigation."
        )

        print(
            "No aggregation or additional row removal "
            "will be performed."
        )

    else:

        print(
            "\nNPI + Year is unique."
        )

    # -----------------------------------------------------
    # YEAR DISTRIBUTION
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("CLEANED YEAR DISTRIBUTION")
    print("=" * 60)

    year_distribution = (
        clean_df["Year"]
        .value_counts()
        .sort_index()
    )

    for year, count in year_distribution.items():

        print(
            f"{int(year)}: {count:,} rows"
        )

    # -----------------------------------------------------
    # PROVIDER STATISTICS
    # -----------------------------------------------------

    unique_npi_count = (
        clean_df["Rndrng_NPI"]
        .nunique()
    )

    print("\n" + "=" * 60)
    print("PROVIDER STATISTICS")
    print("=" * 60)

    print(
        "Unique NPIs:",
        f"{unique_npi_count:,}"
    )

    # -----------------------------------------------------
    # FINAL VALIDATION
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL VALIDATION")
    print("=" * 60)

    print(
        "Exact duplicate validation: PASSED"
    )

    if len(duplicate_npi_year_groups) == 0:

        print(
            "NPI + Year uniqueness: PASSED"
        )

    else:

        print(
            "NPI + Year uniqueness: "
            "NOT UNIQUE — recorded for investigation"
        )

    print(
        "No NPI-Year aggregation performed."
    )

    return clean_df


# =========================================================
# SAVE CLEAN DATASET
# =========================================================

def save_clean_dataset(df):

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\n" + "=" * 60)
    print("PROCESSED DATASET SAVED")
    print("=" * 60)

    print(
        "Output path:",
        OUTPUT_PATH
    )

    print(
        "Output rows:",
        f"{len(df):,}"
    )

    print(
        "Output columns:",
        f"{len(df.columns):,}"
    )


# =========================================================
# MAIN PIPELINE
# =========================================================

def main():

    print("=" * 60)
    print("PROVIDER + SERVICE ANALYTICS")
    print("PROVIDER CLEANING PIPELINE")
    print("=" * 60)

    print("\nCreating Supabase client...")

    client = create_supabase_client()

    print(
        "Supabase client created successfully."
    )

    print(
        f"\nFetching table: {TABLE_NAME}"
    )

    df = fetch_all_records(
        client,
        TABLE_NAME
    )

    if df.empty:

        raise ValueError(
            "provider_combined returned zero rows."
        )

    print(
        f"\nTotal records fetched: {len(df):,}"
    )

    clean_df = clean_provider_data(
        df
    )

    save_clean_dataset(
        clean_df
    )

    print("\n" + "=" * 60)
    print("PROVIDER CLEANING COMPLETED SUCCESSFULLY")
    print("=" * 60)


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()