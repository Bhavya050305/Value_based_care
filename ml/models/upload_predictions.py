import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL is missing from .env")

if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY is missing from .env")


# ============================================================
# 2. CONNECT TO SUPABASE
# ============================================================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

print("Connected to Supabase successfully.")


# ============================================================
# 3. FILE AND TABLE
# ============================================================

CSV_FILE = "aco_savings_rate_2024_predictions.csv"
TABLE_NAME = "aco_trend_predictions"


# ============================================================
# 4. READ CSV
# ============================================================

if not os.path.exists(CSV_FILE):
    raise FileNotFoundError(
        f"CSV file not found: {CSV_FILE}"
    )

df = pd.read_csv(CSV_FILE)

print("CSV loaded successfully.")
print(f"Number of rows: {len(df)}")
print(f"Number of columns: {len(df.columns)}")


# ============================================================
# 5. CHECK CSV COLUMNS
# ============================================================

expected_columns = [
    "ACO_ID",
    "ACO_Name",
    "Actual_2023_Sav_rate",
    "Predicted_2024_Sav_rate",
    "Actual_2024_Sav_rate",
    "Predicted_Change_pp",
    "Actual_Change_pp",
    "Predicted_Trend",
    "Actual_Trend",
    "Absolute_Error",
    "Forecast_Quality"
]

missing_columns = [
    column
    for column in expected_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns in CSV: {missing_columns}"
    )

print("CSV columns verified successfully.")


# ============================================================
# 6. RENAME CSV COLUMNS TO SUPABASE COLUMN NAMES
# ============================================================

df = df.rename(columns={
    "ACO_ID": "aco_id",
    "ACO_Name": "aco_name",
    "Actual_2023_Sav_rate": "actual_2023_sav_rate",
    "Predicted_2024_Sav_rate": "predicted_2024_sav_rate",
    "Actual_2024_Sav_rate": "actual_2024_sav_rate",
    "Predicted_Change_pp": "predicted_change_pp",
    "Actual_Change_pp": "actual_change_pp",
    "Predicted_Trend": "predicted_trend",
    "Actual_Trend": "actual_trend",
    "Absolute_Error": "absolute_error",
    "Forecast_Quality": "forecast_quality"
})


# ============================================================
# 7. SELECT SUPABASE COLUMNS
# ============================================================

supabase_columns = [
    "aco_id",
    "aco_name",
    "actual_2023_sav_rate",
    "predicted_2024_sav_rate",
    "actual_2024_sav_rate",
    "predicted_change_pp",
    "actual_change_pp",
    "predicted_trend",
    "actual_trend",
    "absolute_error",
    "forecast_quality"
]

df = df[supabase_columns]


# ============================================================
# 8. HANDLE EMPTY VALUES
# ============================================================

df = df.where(pd.notnull(df), None)


# ============================================================
# 9. CONVERT TO DICTIONARY
# ============================================================

records = df.to_dict(orient="records")

print(f"Prepared {len(records)} records for upload.")


# ============================================================
# 10. UPLOAD IN BATCHES
# ============================================================

BATCH_SIZE = 100

total_uploaded = 0

for start in range(0, len(records), BATCH_SIZE):

    batch = records[start:start + BATCH_SIZE]

    batch_number = (start // BATCH_SIZE) + 1

    print(
        f"Uploading batch {batch_number}: "
        f"{len(batch)} records..."
    )

    try:

        response = (
            supabase
            .table(TABLE_NAME)
            .upsert(
                batch,
                on_conflict="aco_id"
            )
            .execute()
        )

        uploaded_count = len(response.data)

        total_uploaded += uploaded_count

        print(
            f"Batch {batch_number} uploaded successfully: "
            f"{uploaded_count} records."
        )

    except Exception as e:

        print(
            f"ERROR while uploading batch {batch_number}:"
        )

        print(e)

        raise


# ============================================================
# 11. FINAL RESULT
# ============================================================

print()
print("=" * 60)
print("UPLOAD COMPLETED")
print("=" * 60)

print(f"Total CSV rows : {len(df)}")
print(f"Total uploaded : {total_uploaded}")
print(f"Supabase table : {TABLE_NAME}")

print("=" * 60)