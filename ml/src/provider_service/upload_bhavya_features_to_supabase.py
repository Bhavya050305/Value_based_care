from pathlib import Path
import os
import math
import time

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CSV_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "bhavya_provider_aco_features_final.csv"
)


# ============================================================
# ENVIRONMENT
# ============================================================

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


if not SUPABASE_URL:
    raise RuntimeError(
        "SUPABASE_URL not found in .env"
    )

if not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_SERVICE_ROLE_KEY not found in .env"
    )


# ============================================================
# SUPABASE TABLE
# ============================================================

TABLE_NAME = "bhavya_provider_aco_features_final"

# 500 rows per request.
# Because the table contains 195 columns, this is a reasonable
# batch size for Supabase/PostgREST.
BATCH_SIZE = 500

# Maximum retry attempts for a failed batch.
MAX_RETRIES = 5


# ============================================================
# BIGINT COLUMNS
# ============================================================

BIGINT_COLUMNS = {
    "rndrng_npi",
    "year",

    "tot_hcpcs_cds",
    "tot_benes",

    "drug_tot_hcpcs_cds",
    "drug_tot_benes",

    "med_tot_hcpcs_cds",
    "med_tot_benes",

    "bene_age_lt_65_cnt",
    "bene_age_65_74_cnt",
    "bene_age_75_84_cnt",
    "bene_age_gt_84_cnt",

    "bene_feml_cnt",
    "bene_male_cnt",
    "bene_dual_cnt",
    "bene_ndual_cnt",

    "previous_year",

    "provider_years_observed",
    "provider_history_span_years",
    "segment_year_count",

    "longitudinal_years_observed",
    "longitudinal_first_year",
    "longitudinal_last_year",
}


# ============================================================
# BOOLEAN COLUMNS
# ============================================================

BOOLEAN_COLUMNS = {
    "drug_data_suppressed",
    "consecutive_year",
    "complete_5_year_history",
    "is_first_provider_year",
    "is_last_provider_year",
    "high_utilization_flag",
    "high_cost_flag",
    "low_utilization_flag",
    "low_cost_flag",
}


# ============================================================
# LOAD CSV
# ============================================================

print("=" * 80)
print("BHAVYA PROVIDER + ACO → SUPABASE UPLOAD")
print("=" * 80)

print("\nCSV:")
print(CSV_FILE)

if not CSV_FILE.exists():

    raise FileNotFoundError(
        f"\nCSV file not found:\n{CSV_FILE}"
    )


print("\nLoading CSV...")

df = pd.read_csv(
    CSV_FILE,
    low_memory=False
)

print(
    f"[OK] Rows:    {len(df):,}"
)

print(
    f"[OK] Columns: {len(df.columns):,}"
)


# ============================================================
# NORMALIZE COLUMN NAMES
# ============================================================

print("\nNormalizing column names...")

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
)

print(
    "[OK] Column names normalized to lowercase."
)


# ============================================================
# FIX PANDAS DUPLICATE COLUMN SUFFIXES
# ============================================================
#
# Example:
#
# medical_payment_per_service
# medical_payment_per_service.1
#
# becomes:
#
# medical_payment_per_service
# medical_payment_per_service_1
#
# ============================================================

duplicate_suffix_columns = [
    column
    for column in df.columns
    if column.endswith(".1")
]


if duplicate_suffix_columns:

    print(
        "\nPandas duplicate-suffix columns detected:"
    )

    for column in duplicate_suffix_columns:

        print(
            f"  {column} → "
            f"{column[:-2]}_1"
        )


    df.columns = [
        column[:-2] + "_1"
        if column.endswith(".1")
        else column
        for column in df.columns
    ]


    print(
        "[OK] Pandas duplicate suffixes "
        "converted from '.1' to '_1'."
    )

else:

    print(
        "[OK] No Pandas '.1' duplicate suffix columns found."
    )


# ============================================================
# REMOVE DATABASE-GENERATED ID
# ============================================================

if "id" in df.columns:

    print(
        "\nRemoving CSV id column..."
    )

    df = df.drop(
        columns=["id"]
    )


# ============================================================
# CONVERT BIGINT COLUMNS
# ============================================================

print(
    "\n" + "=" * 80
)

print(
    "CONVERTING BIGINT COLUMNS"
)

print(
    "=" * 80
)


for column in BIGINT_COLUMNS:

    if column not in df.columns:

        print(
            f"[WARNING] BIGINT column not found in CSV: "
            f"{column}"
        )

        continue


    print(
        f"  {column}"
    )


    numeric = pd.to_numeric(
        df[column],
        errors="coerce"
    )


    # --------------------------------------------------------
    # Check for genuine decimal values
    # --------------------------------------------------------

    non_integer_mask = (
        numeric.notna()
        &
        ((numeric % 1) != 0)
    )


    non_integer_count = int(
        non_integer_mask.sum()
    )


    if non_integer_count > 0:

        examples = (
            numeric[
                non_integer_mask
            ]
            .drop_duplicates()
            .head(10)
            .tolist()
        )


        raise ValueError(
            f"\nBIGINT column '{column}' contains "
            f"{non_integer_count} genuine decimal values.\n"
            f"Examples: {examples}\n\n"
            f"Do NOT round these values."
        )


    # --------------------------------------------------------
    # Nullable integer
    # --------------------------------------------------------

    df[column] = numeric.astype(
        "Int64"
    )


# ============================================================
# VALIDATE DECIMAL SERVICE COUNT COLUMNS
# ============================================================

SERVICE_DECIMAL_COLUMNS = {
    "tot_srvcs",
    "drug_tot_srvcs",
    "med_tot_srvcs",
}


print(
    "\n" + "=" * 80
)

print(
    "VALIDATING DECIMAL SERVICE COUNT COLUMNS"
)

print(
    "=" * 80
)


for column in SERVICE_DECIMAL_COLUMNS:

    if column not in df.columns:

        print(
            f"[WARNING] Service column not found: "
            f"{column}"
        )

        continue


    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


    decimal_count = int(
        (
            df[column].notna()
            &
            ((df[column] % 1) != 0)
        ).sum()
    )


    print(
        f"  {column}: "
        f"{decimal_count:,} genuine decimal values"
    )


    print(
        "  [OK] Stored as DOUBLE PRECISION"
    )


# ============================================================
# NORMALIZE BOOLEAN COLUMNS
# ============================================================

print(
    "\n" + "=" * 80
)

print(
    "NORMALIZING BOOLEAN COLUMNS"
)

print(
    "=" * 80
)


def convert_boolean(value):

    if pd.isna(value):

        return None


    if isinstance(
        value,
        bool
    ):

        return value


    value_string = (
        str(value)
        .strip()
        .lower()
    )


    if value_string in {
        "true",
        "1",
        "yes",
        "y",
        "t"
    }:

        return True


    if value_string in {
        "false",
        "0",
        "no",
        "n",
        "f"
    }:

        return False


    return None


for column in BOOLEAN_COLUMNS:

    if column not in df.columns:

        continue


    df[column] = df[column].apply(
        convert_boolean
    )


    print(
        f"  {column}"
    )


# ============================================================
# CLEAN NULL VALUES
# ============================================================

print(
    "\n" + "=" * 80
)

print(
    "CLEANING NULL VALUES"
)

print(
    "=" * 80
)


df = df.astype(
    object
)


df = df.where(
    pd.notna(df),
    None
)


print(
    "[OK] NaN / NA values converted "
    "to PostgreSQL NULL."
)


# ============================================================
# CONVERT VALUES TO PYTHON TYPES
# ============================================================

print(
    "\n" + "=" * 80
)

print(
    "CONVERTING VALUES TO SUPABASE-COMPATIBLE TYPES"
)

print(
    "=" * 80
)


def clean_value(value):

    if value is None:

        return None


    # --------------------------------------------------------
    # Handle pandas NA
    # --------------------------------------------------------

    try:

        if pd.isna(value):

            return None

    except Exception:

        pass


    # --------------------------------------------------------
    # Convert numpy / pandas scalar types
    # --------------------------------------------------------

    if hasattr(
        value,
        "item"
    ):

        try:

            value = value.item()

        except Exception:

            pass


    # --------------------------------------------------------
    # Prevent NaN / Infinity
    # --------------------------------------------------------

    if isinstance(
        value,
        float
    ):

        if math.isnan(value):

            return None


        if math.isinf(value):

            return None


    return value


# ============================================================
# BUILD UPLOAD RECORDS
# ============================================================

print(
    "\nBuilding upload records..."
)


records = []


for row in df.itertuples(
    index=False,
    name=None
):

    record = {
        column: clean_value(value)
        for column, value in zip(
            df.columns,
            row
        )
    }


    records.append(
        record
    )


print(
    f"[OK] Prepared "
    f"{len(records):,} records."
)


# ============================================================
# CONNECT TO SUPABASE
# ============================================================

print(
    "\n" + "=" * 80
)

print(
    "CONNECTING TO SUPABASE"
)

print(
    "=" * 80
)

print(
    f"URL: {SUPABASE_URL}"
)


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


print(
    "[OK] Supabase client created."
)


# ============================================================
# VERIFY TABLE IS EMPTY
# ============================================================
#
# IMPORTANT:
#
# We already deleted the previous 15,000 rows.
#
# This script intentionally requires the table to be empty.
#
# ============================================================

print(
    "\nChecking existing rows..."
)


try:

    count_response = (
        supabase
        .table(TABLE_NAME)
        .select(
            "id",
            count="exact"
        )
        .limit(1)
        .execute()
    )


    existing_count = (
        count_response.count
        if count_response.count is not None
        else 0
    )


except Exception as error:

    print(
        "\n[ERROR] Could not check "
        "existing Supabase rows."
    )

    print(
        error
    )

    raise


print(
    f"[INFO] Existing Supabase rows: "
    f"{existing_count:,}"
)


# ============================================================
# SAFETY CHECK
# ============================================================

if existing_count != 0:

    raise RuntimeError(
        "\nSupabase table is NOT empty.\n\n"
        f"Existing rows: {existing_count:,}\n"
        f"CSV rows:      {len(records):,}\n\n"
        "This script is configured for a "
        "fresh upload.\n"
        "Clear the table first, then run again."
    )


print(
    "[OK] Supabase table is empty."
)


# ============================================================
# FRESH UPLOAD
# ============================================================

print(
    "\n" + "=" * 80
)

print(
    "STARTING FRESH UPLOAD TO SUPABASE"
)

print(
    "=" * 80
)


total_rows = len(records)


total_batches = (
    (
        total_rows
        + BATCH_SIZE
        - 1
    )
    // BATCH_SIZE
)


uploaded_rows = 0


print(
    f"\nTotal CSV rows: "
    f"{total_rows:,}"
)

print(
    f"Batch size: "
    f"{BATCH_SIZE:,}"
)

print(
    f"Total batches: "
    f"{total_batches:,}"
)


# ============================================================
# BATCH UPLOAD LOOP
# ============================================================

for start in range(
    0,
    total_rows,
    BATCH_SIZE
):

    end = min(
        start + BATCH_SIZE,
        total_rows
    )


    batch = records[
        start:end
    ]


    batch_number = (
        start // BATCH_SIZE
    ) + 1


    print(
        f"\nBatch "
        f"{batch_number:,}/"
        f"{total_batches:,}"
        f" → rows "
        f"{start + 1:,}-"
        f"{end:,}"
    )


    # ========================================================
    # RETRY FAILED BATCH
    # ========================================================

    batch_uploaded = False


    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            response = (
                supabase
                .table(TABLE_NAME)
                .insert(batch)
                .execute()
            )


            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            uploaded_rows += len(
                batch
            )


            batch_uploaded = True


            print(
                f"[OK] Uploaded "
                f"{len(batch):,} rows "
                f"| Attempt "
                f"{attempt}/{MAX_RETRIES}"
            )


            print(
                f"[PROGRESS] "
                f"{uploaded_rows:,}/"
                f"{total_rows:,} rows "
                f"accounted for"
            )


            break


        except Exception as error:

            print(
                f"\n[WARNING] Batch "
                f"{batch_number:,} "
                f"attempt "
                f"{attempt}/{MAX_RETRIES} "
                f"failed."
            )


            print(
                f"Error: {error}"
            )


            # ------------------------------------------------
            # Retry
            # ------------------------------------------------

            if attempt < MAX_RETRIES:

                wait_seconds = (
                    2 ** attempt
                )


                print(
                    f"Retrying in "
                    f"{wait_seconds} "
                    f"seconds..."
                )


                time.sleep(
                    wait_seconds
                )


            else:

                print(
                    "\n[ERROR] Maximum "
                    "retries reached."
                )


                print(
                    f"Failed batch: "
                    f"{batch_number:,}/"
                    f"{total_batches:,}"
                )


                print(
                    f"Rows attempted: "
                    f"{start + 1:,}-"
                    f"{end:,}"
                )


                raise


    # ========================================================
    # VERIFY BATCH SUCCESS
    # ========================================================

    if not batch_uploaded:

        raise RuntimeError(
            f"Batch {batch_number} "
            f"was not uploaded."
        )


# ============================================================
# UPLOAD FINISHED
# ============================================================

print(
    "\n" + "=" * 80
)

print(
    "UPLOAD COMPLETED"
)

print(
    "=" * 80
)


print(
    f"CSV rows:       "
    f"{total_rows:,}"
)


print(
    f"Rows uploaded:  "
    f"{uploaded_rows:,}"
)


# ============================================================
# FINAL SUPABASE COUNT
# ============================================================

print(
    "\n" + "=" * 80
)

print(
    "VERIFYING SUPABASE"
)

print(
    "=" * 80
)


try:

    final_response = (
        supabase
        .table(TABLE_NAME)
        .select(
            "id",
            count="exact"
        )
        .limit(1)
        .execute()
    )


    database_count = (
        final_response.count
        if final_response.count is not None
        else 0
    )


except Exception as error:

    print(
        "\n[ERROR] Final row-count "
        "verification failed."
    )


    print(
        error
    )


    raise


print(
    f"\nCSV rows:       "
    f"{total_rows:,}"
)


print(
    f"Uploaded rows:  "
    f"{uploaded_rows:,}"
)


print(
    f"Supabase rows:  "
    f"{database_count:,}"
)


# ============================================================
# FINAL RESULT
# ============================================================

print(
    "\n" + "=" * 80
)

print(
    "FINAL RESULT"
)

print(
    "=" * 80
)


if database_count == total_rows:

    print(
        "\n[SUCCESS] Provider + ACO "
        "dataset uploaded successfully."
    )


    print(
        f"\nTotal rows: "
        f"{database_count:,}"
    )


    print(
        f"Total columns: "
        f"{len(df.columns):,}"
    )


    print(
        f"\nSupabase table: "
        f"{TABLE_NAME}"
    )


else:

    print(
        "\n[WARNING] Row count mismatch."
    )


    print(
        f"Expected: "
        f"{total_rows:,}"
    )


    print(
        f"Found:    "
        f"{database_count:,}"
    )


print(
    "\n" + "=" * 80
)

print(
    "SCRIPT FINISHED"
)

print(
    "=" * 80
)