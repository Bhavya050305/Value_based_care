from pathlib import Path
import sys

import numpy as np
import pandas as pd


# ============================================================
# VBC COMMANDIQ
# PROVIDER + SERVICE INPUT INSPECTION
#
# Purpose:
#   Inspect the two CURRENT provider/service datasets before
#   building the next Provider + Service Analytics layer.
#
# IMPORTANT:
#   - Does NOT modify any data
#   - Does NOT create features
#   - Does NOT introduce ML
#   - Does NOT fabricate missing medical/service values
# ============================================================


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

PROVIDER_DASHBOARD_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_dashboard_analytics.csv"
)

SERVICE_METRICS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "all_aco"
    / "provider_service_metrics.csv"
)


# ============================================================
# HELPER
# ============================================================

def print_section(title: str) -> None:
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


# ============================================================
# DATASET INSPECTION
# ============================================================

def inspect_dataset(
    df: pd.DataFrame,
    name: str,
    grain_columns: list[str],
    important_columns: list[str],
) -> None:

    print_section(f"DATASET: {name}")

    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------

    print(f"Rows       : {len(df):,}")
    print(f"Columns    : {len(df.columns):,}")

    # --------------------------------------------------------
    # Columns
    # --------------------------------------------------------

    print("\nCOLUMN NAMES")

    for index, column in enumerate(df.columns, start=1):
        print(f"{index:03d}. {column}")

    # --------------------------------------------------------
    # Data types
    # --------------------------------------------------------

    print("\nDATA TYPES")

    print(df.dtypes.to_string())

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    print("\nMISSING VALUES")

    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    if missing.empty:
        print("No missing values.")
    else:
        print(missing.to_string())

    # --------------------------------------------------------
    # Infinite values
    # --------------------------------------------------------

    print("\nINFINITE VALUES")

    numeric_df = df.select_dtypes(include=[np.number])

    if numeric_df.empty:
        print("No numeric columns.")
    else:
        infinite_count = np.isinf(numeric_df).sum().sum()
        print(f"Total infinite values: {infinite_count:,}")

    # --------------------------------------------------------
    # Important columns
    # --------------------------------------------------------

    print("\nIMPORTANT COLUMN CHECK")

    for column in important_columns:

        if column in df.columns:
            non_null = df[column].notna().sum()
            unique = df[column].nunique(dropna=True)

            print(
                f"[FOUND]   {column:<45} "
                f"non-null={non_null:,} "
                f"unique={unique:,}"
            )

        else:
            print(
                f"[MISSING] {column:<45}"
            )

    # --------------------------------------------------------
    # Grain validation
    # --------------------------------------------------------

    print("\nGRAIN VALIDATION")

    available_grain = [
        column
        for column in grain_columns
        if column in df.columns
    ]

    missing_grain = [
        column
        for column in grain_columns
        if column not in df.columns
    ]

    if missing_grain:
        print(
            "Missing grain columns:"
        )

        for column in missing_grain:
            print(f"  - {column}")

    if available_grain:

        duplicate_count = df.duplicated(
            subset=available_grain
        ).sum()

        print(
            f"Grain columns: {available_grain}"
        )

        print(
            f"Duplicate rows at available grain: "
            f"{duplicate_count:,}"
        )

    # --------------------------------------------------------
    # Sample
    # --------------------------------------------------------

    print("\nFIRST 5 ROWS")

    print(
        df.head(5).to_string()
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print_section(
        "VBC COMMANDIQ — PROVIDER + SERVICE INPUT INSPECTION"
    )

    print(
        "Purpose: inspect current provider/service datasets "
        "before creating performance drivers."
    )

    print(
        f"\nProject root:\n{PROJECT_ROOT}"
    )

    # ========================================================
    # FILE EXISTENCE
    # ========================================================

    print_section("FILE EXISTENCE VALIDATION")

    print(
        f"\nProvider dashboard:\n"
        f"{PROVIDER_DASHBOARD_PATH}"
    )

    print(
        f"\nProvider service metrics:\n"
        f"{SERVICE_METRICS_PATH}"
    )

    if not PROVIDER_DASHBOARD_PATH.exists():

        print(
            "\nERROR: provider_dashboard_analytics.csv "
            "was not found."
        )

        sys.exit(1)

    if not SERVICE_METRICS_PATH.exists():

        print(
            "\nERROR: provider_service_metrics.csv "
            "was not found."
        )

        sys.exit(1)

    print("\nProvider dashboard file : FOUND")
    print("Service metrics file    : FOUND")

    # ========================================================
    # LOAD DATASETS
    # ========================================================

    print_section("LOADING DATASETS")

    try:

        provider_df = pd.read_csv(
            PROVIDER_DASHBOARD_PATH,
            low_memory=False,
        )

        service_df = pd.read_csv(
            SERVICE_METRICS_PATH,
            low_memory=False,
        )

    except Exception as error:

        print(
            f"\nERROR while loading CSV files:\n{error}"
        )

        sys.exit(1)

    print(
        f"Provider dashboard loaded: "
        f"{len(provider_df):,} rows × "
        f"{len(provider_df.columns):,} columns"
    )

    print(
        f"Service metrics loaded: "
        f"{len(service_df):,} rows × "
        f"{len(service_df.columns):,} columns"
    )

    # ========================================================
    # PROVIDER DASHBOARD
    # ========================================================

    inspect_dataset(

        df=provider_df,

        name="provider_dashboard_analytics.csv",

        grain_columns=[
            "Rndrng_NPI",
            "Year",
        ],

        important_columns=[
            "Rndrng_NPI",
            "ACO_ID",
            "Year",
            "provider_name",

            "services_per_beneficiary",
            "hcpcs_codes_per_beneficiary",

            "payment_per_service",
            "payment_per_beneficiary",

            "allowed_amount_per_service",
            "allowed_amount_per_beneficiary",

            "standardized_amount_per_service",
            "standardized_amount_per_beneficiary",

            "provider_segment",

            "high_utilization_flag",
            "high_cost_flag",

            "yoy_service_change_pct",
            "yoy_payment_change_pct",

            "yoy_services_per_beneficiary_change_pct",
            "yoy_payment_per_beneficiary_change_pct",

            "dashboard_status",
        ],
    )

    # ========================================================
    # SERVICE METRICS
    # ========================================================

    inspect_dataset(

        df=service_df,

        name="provider_service_metrics.csv",

        grain_columns=[
            "ACO_ID",
            "Rndrng_NPI",
            "Year",
        ],

        important_columns=[
            "ACO_ID",
            "Rndrng_NPI",
            "Year",
            "provider_name",

            "HCPCS_Cd",

            "Tot_Srvcs",
            "Tot_Benes",

            "Tot_Pymt_Amt",
            "Tot_Mdcr_Alowd_Amt",
            "Tot_Mdcr_Pymt_Amt",

            "service_share",
            "payment_share",
        ],
    )

    # ========================================================
    # PROVIDER IDENTIFIER COMPARISON
    # ========================================================

    print_section(
        "CROSS-DATASET PROVIDER IDENTIFIER VALIDATION"
    )

    if "Rndrng_NPI" in provider_df.columns:

        provider_npis = set(
            provider_df["Rndrng_NPI"]
            .dropna()
            .astype(str)
        )

    else:

        provider_npis = set()

    if "Rndrng_NPI" in service_df.columns:

        service_npis = set(
            service_df["Rndrng_NPI"]
            .dropna()
            .astype(str)
        )

    else:

        service_npis = set()

    common_npis = (
        provider_npis.intersection(service_npis)
    )

    dashboard_only = (
        provider_npis - service_npis
    )

    service_only = (
        service_npis - provider_npis
    )

    print(
        f"Provider dashboard NPIs : "
        f"{len(provider_npis):,}"
    )

    print(
        f"Service metrics NPIs    : "
        f"{len(service_npis):,}"
    )

    print(
        f"Common NPIs             : "
        f"{len(common_npis):,}"
    )

    print(
        f"Dashboard-only NPIs     : "
        f"{len(dashboard_only):,}"
    )

    print(
        f"Service-only NPIs       : "
        f"{len(service_only):,}"
    )

    # ========================================================
    # YEAR VALIDATION
    # ========================================================

    print_section("YEAR VALIDATION")

    if "Year" in provider_df.columns:

        provider_years = sorted(
            provider_df["Year"]
            .dropna()
            .unique()
            .tolist()
        )

        print(
            f"Provider dashboard years: "
            f"{provider_years}"
        )

    else:

        print(
            "Provider dashboard does not contain Year."
        )

    if "Year" in service_df.columns:

        service_years = sorted(
            service_df["Year"]
            .dropna()
            .unique()
            .tolist()
        )

        print(
            f"Service metrics years: "
            f"{service_years}"
        )

    else:

        print(
            "Service metrics does not contain Year."
        )

    # ========================================================
    # ACO VALIDATION
    # ========================================================

    print_section("ACO VALIDATION")

    if "ACO_ID" in provider_df.columns:

        provider_acos = (
            provider_df["ACO_ID"]
            .nunique(dropna=True)
        )

        print(
            f"Provider dashboard ACOs: "
            f"{provider_acos:,}"
        )

        print(
            f"Provider dashboard missing ACO_ID: "
            f"{provider_df['ACO_ID'].isna().sum():,}"
        )

    else:

        print(
            "Provider dashboard does not contain ACO_ID."
        )

    if "ACO_ID" in service_df.columns:

        service_acos = (
            service_df["ACO_ID"]
            .nunique(dropna=True)
        )

        print(
            f"Service metrics ACOs: "
            f"{service_acos:,}"
        )

        print(
            f"Service metrics missing ACO_ID: "
            f"{service_df['ACO_ID'].isna().sum():,}"
        )

    else:

        print(
            "Service metrics does not contain ACO_ID."
        )

    # ========================================================
    # PROVIDER DASHBOARD GRAIN
    # ========================================================

    print_section(
        "PROVIDER DASHBOARD GRAIN"
    )

    if {
        "Rndrng_NPI",
        "Year",
    }.issubset(provider_df.columns):

        duplicate_count = provider_df.duplicated(
            subset=[
                "Rndrng_NPI",
                "Year",
            ]
        ).sum()

        unique_grain = (
            provider_df[
                [
                    "Rndrng_NPI",
                    "Year",
                ]
            ]
            .drop_duplicates()
        )

        print(
            f"Unique NPI-Year combinations: "
            f"{len(unique_grain):,}"
        )

        print(
            f"Duplicate NPI-Year rows: "
            f"{duplicate_count:,}"
        )

    else:

        print(
            "Cannot validate NPI-Year grain "
            "because required columns are missing."
        )

    # ========================================================
    # SERVICE METRICS GRAIN
    # ========================================================

    print_section(
        "SERVICE METRICS GRAIN"
    )

    if {
        "ACO_ID",
        "Rndrng_NPI",
        "Year",
    }.issubset(service_df.columns):

        duplicate_count = service_df.duplicated(
            subset=[
                "ACO_ID",
                "Rndrng_NPI",
                "Year",
            ]
        ).sum()

        unique_grain = (
            service_df[
                [
                    "ACO_ID",
                    "Rndrng_NPI",
                    "Year",
                ]
            ]
            .drop_duplicates()
        )

        print(
            f"Unique ACO-NPI-Year combinations: "
            f"{len(unique_grain):,}"
        )

        print(
            f"Duplicate ACO-NPI-Year rows: "
            f"{duplicate_count:,}"
        )

    else:

        print(
            "Cannot validate ACO-NPI-Year grain "
            "because required columns are missing."
        )

    # ========================================================
    # DETAILED PROVIDER-YEAR COVERAGE
    # ========================================================

    print_section(
        "PROVIDER-YEAR COVERAGE"
    )

    if {
        "Rndrng_NPI",
        "Year",
    }.issubset(provider_df.columns):

        provider_year_counts = (
            provider_df
            .groupby("Year")["Rndrng_NPI"]
            .nunique()
            .sort_index()
        )

        print(
            provider_year_counts.to_string()
        )

    # ========================================================
    # ACO PROVIDER-YEAR COVERAGE
    # ========================================================

    print_section(
        "ACO PROVIDER-YEAR COVERAGE"
    )

    if {
        "ACO_ID",
        "Rndrng_NPI",
        "Year",
    }.issubset(service_df.columns):

        service_coverage = (
            service_df
            .groupby("Year")["Rndrng_NPI"]
            .nunique()
            .sort_index()
        )

        print(
            service_coverage.to_string()
        )

        print(
            "\nProviders per ACO:"
        )

        providers_per_aco = (
            service_df
            .groupby("ACO_ID")["Rndrng_NPI"]
            .nunique()
        )

        print(
            providers_per_aco.describe().to_string()
        )

    # ========================================================
    # JOIN COVERAGE
    # ========================================================

    print_section(
        "PROVIDER-SERVICE JOIN COVERAGE"
    )

    if {
        "Rndrng_NPI",
        "Year",
    }.issubset(provider_df.columns) and {
        "ACO_ID",
        "Rndrng_NPI",
        "Year",
    }.issubset(service_df.columns):

        provider_keys = (
            provider_df[
                [
                    "Rndrng_NPI",
                    "Year",
                ]
            ]
            .drop_duplicates()
        )

        service_keys = (
            service_df[
                [
                    "ACO_ID",
                    "Rndrng_NPI",
                    "Year",
                ]
            ]
            .drop_duplicates()
        )

        coverage_check = service_keys.merge(
            provider_keys,
            on=[
                "Rndrng_NPI",
                "Year",
            ],
            how="left",
            indicator=True,
        )

        matched = (
            coverage_check["_merge"] == "both"
        ).sum()

        unmatched = (
            coverage_check["_merge"] == "left_only"
        ).sum()

        total = len(coverage_check)

        print(
            f"Service ACO-NPI-Year keys : "
            f"{total:,}"
        )

        print(
            f"Matching provider-year    : "
            f"{matched:,}"
        )

        print(
            f"Unmatched provider-year   : "
            f"{unmatched:,}"
        )

        if total > 0:

            match_rate = (
                matched / total * 100
            )

            print(
                f"Join coverage             : "
                f"{match_rate:.2f}%"
            )

    else:

        print(
            "Cannot perform join coverage test "
            "because required keys are missing."
        )

    # ========================================================
    # COLUMN DISCOVERY FOR SERVICE DRIVER ANALYSIS
    # ========================================================

    print_section(
        "SERVICE DRIVER COLUMN DISCOVERY"
    )

    service_keywords = [
        "HCPCS",
        "Srv",
        "Serv",
        "Bene",
        "Pymt",
        "Payment",
        "Allowed",
        "Standard",
        "Share",
        "Growth",
        "Drug",
        "Cost",
        "Util",
    ]

    discovered_columns = []

    for column in service_df.columns:

        column_lower = column.lower()

        if any(
            keyword.lower() in column_lower
            for keyword in service_keywords
        ):

            discovered_columns.append(column)

    if discovered_columns:

        print(
            "Potential service-driver columns:"
        )

        for column in discovered_columns:
            print(
                f"  - {column}"
            )

    else:

        print(
            "No service-driver columns matched "
            "the discovery keywords."
        )

    # ========================================================
    # COLUMN DISCOVERY FOR PROVIDER DRIVER ANALYSIS
    # ========================================================

    print_section(
        "PROVIDER DRIVER COLUMN DISCOVERY"
    )

    provider_keywords = [
        "service",
        "util",
        "payment",
        "allowed",
        "standard",
        "cost",
        "risk",
        "growth",
        "segment",
        "status",
        "efficiency",
    ]

    discovered_provider_columns = []

    for column in provider_df.columns:

        column_lower = column.lower()

        if any(
            keyword.lower() in column_lower
            for keyword in provider_keywords
        ):

            discovered_provider_columns.append(
                column
            )

    if discovered_provider_columns:

        print(
            "Potential provider-driver columns:"
        )

        for column in discovered_provider_columns:
            print(
                f"  - {column}"
            )

    else:

        print(
            "No provider-driver columns matched "
            "the discovery keywords."
        )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print_section(
        "INSPECTION COMPLETE"
    )

    print(
        "No files were modified."
    )

    print(
        "No features were created."
    )

    print(
        "No ML was used."
    )

    print(
        "\nNext step:"
    )

    print(
        "Paste the COMPLETE terminal output into ChatGPT."
    )

    print(
        "\nThe next script will be designed from the "
        "ACTUAL columns and grain discovered here."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()