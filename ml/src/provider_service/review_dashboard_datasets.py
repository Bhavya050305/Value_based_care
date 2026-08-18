from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

DATA_DIR = BASE_DIR / "data" / "processed" / "provider_service"


FILES = {
    "PROVIDER DASHBOARD": DATA_DIR / "provider_dashboard_analytics.csv",
    "ACO PROVIDER METRICS": DATA_DIR / "aco_provider_metrics.csv",
    "SERVICE METRICS": DATA_DIR / "service_metrics.csv",
    "PROVIDER-SERVICE METRICS": DATA_DIR / "provider_service_metrics.csv",
}


# ============================================================
# EXPECTED GRAINS
# ============================================================

EXPECTED_GRAINS = {
    "PROVIDER DASHBOARD": "Provider-Year",
    "ACO PROVIDER METRICS": "ACO-Year",
    "SERVICE METRICS": "ACO-Year-HCPCS",
    "PROVIDER-SERVICE METRICS": "Provider-Year-HCPCS",
}


# ============================================================
# REQUIRED DASHBOARD COLUMNS
# ============================================================

REQUIRED_COLUMNS = {

    "PROVIDER DASHBOARD": [
        "Rndrng_NPI",
        "Year",
        "ACO_ID",
    ],

    "ACO PROVIDER METRICS": [
        "ACO_ID",
        "Year",
    ],

    "SERVICE METRICS": [
        "ACO_ID",
        "Year",
        "HCPCS_Cd",
    ],

    "PROVIDER-SERVICE METRICS": [
        "Rndrng_NPI",
        "ACO_ID",
        "Year",
        "HCPCS_Cd",
    ],
}


# ============================================================
# HELPER FUNCTION
# ============================================================

def print_section(title):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


# ============================================================
# REVIEW FUNCTION
# ============================================================

def review_dataset(name, path):

    print_section(name)

    print(f"File: {path}")
    print(f"Expected grain: {EXPECTED_GRAINS[name]}")

    # --------------------------------------------------------
    # File existence
    # --------------------------------------------------------

    if not path.exists():
        print("STATUS: FILE NOT FOUND")
        return

    print("STATUS: FILE FOUND")

    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    df = pd.read_csv(path, low_memory=False)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    # --------------------------------------------------------
    # Column list
    # --------------------------------------------------------

    print()
    print("COLUMNS:")

    for column in df.columns:
        print(f"  - {column}")

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    print()
    print("REQUIRED COLUMN CHECK:")

    required = REQUIRED_COLUMNS[name]

    for column in required:

        if column in df.columns:
            print(f"  FOUND: {column}")
        else:
            print(f"  MISSING: {column}")

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    print()
    print("MISSING VALUES:")

    missing = df.isna().sum()

    missing = missing[missing > 0].sort_values(ascending=False)

    if len(missing) == 0:
        print("  No missing values.")
    else:
        for column, count in missing.items():
            print(f"  {column}: {count:,}")

    # --------------------------------------------------------
    # Duplicate full rows
    # --------------------------------------------------------

    duplicate_rows = df.duplicated().sum()

    print()
    print(f"Duplicate full rows: {duplicate_rows:,}")

    # --------------------------------------------------------
    # Year information
    # --------------------------------------------------------

    if "Year" in df.columns:

        years = sorted(df["Year"].dropna().unique().tolist())

        print()
        print(f"Years: {years}")

    # --------------------------------------------------------
    # ACO information
    # --------------------------------------------------------

    if "ACO_ID" in df.columns:

        unique_acos = df["ACO_ID"].nunique(dropna=True)

        print(f"Unique ACOs: {unique_acos:,}")

    # --------------------------------------------------------
    # Provider information
    # --------------------------------------------------------

    if "Rndrng_NPI" in df.columns:

        unique_providers = df["Rndrng_NPI"].nunique(dropna=True)

        print(f"Unique providers: {unique_providers:,}")

    # --------------------------------------------------------
    # HCPCS information
    # --------------------------------------------------------

    if "HCPCS_Cd" in df.columns:

        unique_hcpcs = df["HCPCS_Cd"].nunique(dropna=True)

        print(f"Unique HCPCS codes: {unique_hcpcs:,}")

    # --------------------------------------------------------
    # Provider-Year duplicate check
    # --------------------------------------------------------

    if all(
        column in df.columns
        for column in ["Rndrng_NPI", "Year"]
    ):

        duplicates = df.duplicated(
            subset=["Rndrng_NPI", "Year"]
        ).sum()

        print(
            f"Duplicate Provider-Year keys: "
            f"{duplicates:,}"
        )

    # --------------------------------------------------------
    # ACO-Year duplicate check
    # --------------------------------------------------------

    if all(
        column in df.columns
        for column in ["ACO_ID", "Year"]
    ):

        duplicates = df.duplicated(
            subset=["ACO_ID", "Year"]
        ).sum()

        print(
            f"Duplicate ACO-Year keys: "
            f"{duplicates:,}"
        )

    # --------------------------------------------------------
    # Provider-Year-HCPCS duplicate check
    # --------------------------------------------------------

    if all(
        column in df.columns
        for column in [
            "Rndrng_NPI",
            "Year",
            "HCPCS_Cd"
        ]
    ):

        duplicates = df.duplicated(
            subset=[
                "Rndrng_NPI",
                "Year",
                "HCPCS_Cd"
            ]
        ).sum()

        print(
            f"Duplicate Provider-Year-HCPCS keys: "
            f"{duplicates:,}"
        )

    # --------------------------------------------------------
    # ACO-Year-HCPCS duplicate check
    # --------------------------------------------------------

    if all(
        column in df.columns
        for column in [
            "ACO_ID",
            "Year",
            "HCPCS_Cd"
        ]
    ):

        duplicates = df.duplicated(
            subset=[
                "ACO_ID",
                "Year",
                "HCPCS_Cd"
            ]
        ).sum()

        print(
            f"Duplicate ACO-Year-HCPCS keys: "
            f"{duplicates:,}"
        )

    # --------------------------------------------------------
    # Negative numeric values
    # --------------------------------------------------------

    print()
    print("NEGATIVE NUMERIC VALUES:")

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    negative_found = False

    for column in numeric_columns:

        count = (df[column] < 0).sum()

        if count > 0:

            negative_found = True

            print(
                f"  {column}: "
                f"{count:,}"
            )

    if not negative_found:
        print("  No negative numeric values.")

    # --------------------------------------------------------
    # Summary statistics for important columns
    # --------------------------------------------------------

    important_columns = [
        "Tot_Benes",
        "Tot_Srvcs",
        "payment_per_service",
        "payment_per_beneficiary",
        "utilization_rate",
        "cost_score",
        "utilization_score",
        "payment_change_pct",
        "service_volume_change_pct",
        "utilization_change_pct",
    ]

    available_important = [
        column
        for column in important_columns
        if column in df.columns
    ]

    if available_important:

        print()
        print("IMPORTANT METRIC SUMMARY:")

        print(
            df[available_important]
            .describe()
            .round(4)
            .to_string()
        )

    # --------------------------------------------------------
    # Data types
    # --------------------------------------------------------

    print()
    print("DATA TYPES:")

    print(df.dtypes.to_string())

    # --------------------------------------------------------
    # Memory usage
    # --------------------------------------------------------

    memory_mb = (
        df.memory_usage(deep=True).sum()
        / (1024 ** 2)
    )

    print()
    print(
        f"Approximate memory usage: "
        f"{memory_mb:.2f} MB"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print_section(
        "BHAVYA VBC - DASHBOARD DATASET REVIEW"
    )

    print(
        "This script ONLY reviews existing datasets."
    )

    print(
        "It does NOT modify or recreate any dataset."
    )

    for name, path in FILES.items():

        review_dataset(
            name,
            path
        )

    print_section("REVIEW COMPLETE")

    print(
        "Next step: inspect the results and identify "
        "any dashboard coverage gaps before creating "
        "performance_drivers.csv."
    )


if __name__ == "__main__":
    main()