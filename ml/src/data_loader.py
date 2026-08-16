# ============================================================
# ACO ANALYTICS - SUPABASE DATA LOADER
# ============================================================

import os
import pandas as pd

from dotenv import load_dotenv
from supabase import create_client


# ------------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ------------------------------------------------------------

load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL is missing from .env"
    )

if not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_KEY is missing from .env"
    )


# ------------------------------------------------------------
# CREATE SUPABASE CLIENT
# ------------------------------------------------------------

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


print("Supabase client created successfully!")


# ------------------------------------------------------------
# FETCH ALL ROWS
# ------------------------------------------------------------

def fetch_all_rows(
    table_name: str,
    batch_size: int = 1000
) -> pd.DataFrame:

    all_rows = []
    start = 0

    while True:

        print(
            f"Fetching rows "
            f"{start} to {start + batch_size - 1}..."
        )

        response = (
            supabase
            .table(table_name)
            .select("*")
            .range(
                start,
                start + batch_size - 1
            )
            .execute()
        )

        rows = response.data

        if not rows:
            break

        all_rows.extend(rows)

        print(
            f"Loaded {len(all_rows)} rows..."
        )

        if len(rows) < batch_size:
            break

        start += batch_size

    return pd.DataFrame(all_rows)


# ------------------------------------------------------------
# LOAD ACO PERFORMANCE DATA
# ------------------------------------------------------------

def load_aco_performance() -> pd.DataFrame:

    table_name = "fact_aco_performance"

    df = fetch_all_rows(
        table_name
    )

    if df.empty:
        raise ValueError(
            "fact_aco_performance returned no data."
        )

    print()
    print("========================================")
    print("ACO PERFORMANCE DATA LOADED")
    print("========================================")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    if "ACO_ID" in df.columns:
        print(
            "Unique ACOs:",
            df["ACO_ID"].nunique()
        )

    if "performance_year" in df.columns:
        print(
            "Years:",
            sorted(
                df["performance_year"]
                .dropna()
                .unique()
            )
        )

    return df


# ------------------------------------------------------------
# TEST CONNECTION
# ------------------------------------------------------------

if __name__ == "__main__":

    print()
    print("Testing Supabase connection...")
    print()

    df = load_aco_performance()

    print()
    print("First 5 rows:")
    print(df.head())

    print()
    print("Data loader test completed successfully.")