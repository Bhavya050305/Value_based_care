from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "provider_service"
    / "provider_aco_features_final.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "provider_service"
    / "provider_dashboard_analytics.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("=" * 70)
    print("PROVIDER DASHBOARD ANALYTICS")
    print("=" * 70)

    print(f"Input file: {INPUT_FILE}")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found:\n{INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE,
        low_memory=False
    )

    print(f"Rows loaded: {len(df):,}")
    print(f"Columns loaded: {len(df.columns):,}")

    return df


# ============================================================
# VALIDATE INPUT
# ============================================================

def validate_input(df):

    print("\n" + "=" * 70)
    print("INPUT VALIDATION")
    print("=" * 70)

    required_columns = [
        "Rndrng_NPI",
        "Year",
        "ACO_ID",
        "provider_name_x",

        # Core utilization
        "Tot_Benes",
        "Tot_Srvcs",
        "Tot_HCPCS_Cds",

        # Core cost
        "Tot_Mdcr_Alowd_Amt",
        "Tot_Mdcr_Pymt_Amt",
        "Tot_Mdcr_Stdzd_Amt",

        # Engineered features
        "services_per_beneficiary",
        "payment_per_beneficiary",
        "payment_per_service",
        "payment_to_allowed_ratio",

        # Risk
        "beneficiary_risk_score",
        "overall_condition_burden",

        # Temporal
        "yoy_service_change_pct",
        "yoy_payment_change_pct",
        "yoy_beneficiary_change_pct",

        # Performance
        "utilization_score",
        "cost_score",
        "provider_segment",

        # Longitudinal
        "provider_years_observed",
        "provider_first_year",
        "provider_last_year",
        "dominant_provider_segment",
        "segment_stability",
        "overall_provider_segment",
        "history_class",

        # Stage 4 performance
        "payment_efficiency_ratio",
        "standardized_payment_ratio",
        "risk_adjusted_services",
        "risk_adjusted_payment",
        "risk_adjusted_payment_per_beneficiary",
        "condition_adjusted_services",
        "condition_adjusted_payment",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        print("Missing columns:")

        for column in missing:
            print(f"- {column}")

        raise ValueError(
            "Required columns are missing."
        )

    print("Required columns: PASSED")

    # --------------------------------------------------------
    # Grain
    # --------------------------------------------------------

    duplicate_count = df.duplicated(
        subset=[
            "Rndrng_NPI",
            "Year"
        ]
    ).sum()

    print(
        "Duplicate NPI-Year rows:",
        f"{duplicate_count:,}"
    )

    if duplicate_count != 0:

        raise ValueError(
            "NPI + Year grain is not unique."
        )

    print("NPI + Year grain: PASSED")

    # --------------------------------------------------------
    # ACO coverage
    # --------------------------------------------------------

    missing_aco = df["ACO_ID"].isna().sum()

    print(
        "Missing ACO_ID:",
        f"{missing_aco:,}"
    )

    if missing_aco != 0:

        raise ValueError(
            "Missing ACO_ID values detected."
        )

    print("ACO coverage: PASSED")


# ============================================================
# SAFE NUMERIC CONVERSION
# ============================================================

def convert_numeric_columns(df):

    numeric_columns = [
        "Tot_Benes",
        "Tot_Srvcs",
        "Tot_HCPCS_Cds",
        "Tot_Mdcr_Alowd_Amt",
        "Tot_Mdcr_Pymt_Amt",
        "Tot_Mdcr_Stdzd_Amt",

        "services_per_beneficiary",
        "payment_per_beneficiary",
        "payment_per_service",
        "payment_to_allowed_ratio",

        "beneficiary_risk_score",
        "overall_condition_burden",

        "yoy_service_change_pct",
        "yoy_payment_change_pct",
        "yoy_beneficiary_change_pct",

        "utilization_score",
        "cost_score",

        "provider_years_observed",
        "provider_first_year",
        "provider_last_year",
        "segment_stability",

        "payment_efficiency_ratio",
        "standardized_payment_ratio",

        "risk_adjusted_services",
        "risk_adjusted_payment",
        "risk_adjusted_payment_per_beneficiary",

        "condition_adjusted_services",
        "condition_adjusted_payment",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


# ============================================================
# CREATE DASHBOARD ANALYTICS
# ============================================================

def create_dashboard_analytics(df):

    print("\n" + "=" * 70)
    print("CREATING PROVIDER DASHBOARD ANALYTICS")
    print("=" * 70)

    output = pd.DataFrame()

    # ========================================================
    # IDENTIFIERS
    # ========================================================

    print("Creating provider identifiers...")

    output["Rndrng_NPI"] = df["Rndrng_NPI"]

    output["provider_name"] = (
        df["provider_name_x"]
    )

    output["ACO_ID"] = df["ACO_ID"]

    output["Year"] = df["Year"]

    output["provider_type"] = (
        df["Rndrng_Prvdr_Type"]
        if "Rndrng_Prvdr_Type" in df.columns
        else np.nan
    )

    output["state"] = (
        df["Rndrng_Prvdr_State_Abrvtn"]
        if "Rndrng_Prvdr_State_Abrvtn" in df.columns
        else np.nan
    )

    output["city"] = (
        df["Rndrng_Prvdr_City"]
        if "Rndrng_Prvdr_City" in df.columns
        else np.nan
    )

    # ========================================================
    # VOLUME
    # ========================================================

    print("Creating utilization analytics...")

    output["beneficiaries"] = df["Tot_Benes"]

    output["services"] = df["Tot_Srvcs"]

    output["hcpcs_codes"] = df["Tot_HCPCS_Cds"]

    output["services_per_beneficiary"] = (
        df["services_per_beneficiary"]
    )

    output["payment_per_beneficiary"] = (
        df["payment_per_beneficiary"]
    )

    output["payment_per_service"] = (
        df["payment_per_service"]
    )

    # ========================================================
    # COST
    # ========================================================

    print("Creating cost analytics...")

    output["allowed_amount"] = (
        df["Tot_Mdcr_Alowd_Amt"]
    )

    output["medicare_payment"] = (
        df["Tot_Mdcr_Pymt_Amt"]
    )

    output["standardized_payment"] = (
        df["Tot_Mdcr_Stdzd_Amt"]
    )

    output["payment_to_allowed_ratio"] = (
        df["payment_to_allowed_ratio"]
    )

    output["payment_efficiency_ratio"] = (
        df["payment_efficiency_ratio"]
    )

    output["standardized_payment_ratio"] = (
        df["standardized_payment_ratio"]
    )

    # ========================================================
    # RISK
    # ========================================================

    print("Creating risk analytics...")

    output["beneficiary_risk_score"] = (
        df["beneficiary_risk_score"]
    )

    output["overall_condition_burden"] = (
        df["overall_condition_burden"]
    )

    output["risk_adjusted_services"] = (
        df["risk_adjusted_services"]
    )

    output["risk_adjusted_payment"] = (
        df["risk_adjusted_payment"]
    )

    output["risk_adjusted_payment_per_beneficiary"] = (
        df["risk_adjusted_payment_per_beneficiary"]
    )

    output["condition_adjusted_services"] = (
        df["condition_adjusted_services"]
    )

    output["condition_adjusted_payment"] = (
        df["condition_adjusted_payment"]
    )

    # ========================================================
    # TEMPORAL / TREND
    # ========================================================

    print("Creating trend analytics...")

    output["yoy_beneficiary_change_pct"] = (
        df["yoy_beneficiary_change_pct"]
    )

    output["yoy_service_change_pct"] = (
        df["yoy_service_change_pct"]
    )

    output["yoy_payment_change_pct"] = (
        df["yoy_payment_change_pct"]
    )

    # ========================================================
    # PERFORMANCE
    # ========================================================

    print("Creating performance analytics...")

    output["utilization_score"] = (
        df["utilization_score"]
    )

    output["cost_score"] = (
        df["cost_score"]
    )

    output["provider_segment"] = (
        df["provider_segment"]
    )

    output["high_utilization_flag"] = (
        df["high_utilization_flag"]
    )

    output["high_cost_flag"] = (
        df["high_cost_flag"]
    )

    output["low_utilization_flag"] = (
        df["low_utilization_flag"]
    )

    output["low_cost_flag"] = (
        df["low_cost_flag"]
    )

    # ========================================================
    # LONGITUDINAL
    # ========================================================

    print("Creating longitudinal analytics...")

    output["years_observed"] = (
        df["provider_years_observed"]
    )

    output["first_year"] = (
        df["provider_first_year"]
    )

    output["last_year"] = (
        df["provider_last_year"]
    )

    output["dominant_provider_segment"] = (
        df["dominant_provider_segment"]
    )

    output["segment_year_count"] = (
        df["segment_year_count"]
    )

    output["segment_stability"] = (
        df["segment_stability"]
    )

    output["overall_provider_segment"] = (
        df["overall_provider_segment"]
    )

    output["history_class"] = (
        df["history_class"]
    )

    # ========================================================
    # EXECUTIVE FLAGS
    # ========================================================

    print("Creating dashboard decision flags...")

    output["needs_attention"] = (
        (
            df["high_utilization_flag"].fillna(False)
            == True
        )
        |
        (
            df["high_cost_flag"].fillna(False)
            == True
        )
    ).astype(int)

    output["high_risk_flag"] = (
        df["beneficiary_risk_score"]
        >= df["beneficiary_risk_score"].quantile(0.75)
    ).astype(int)

    output["negative_service_trend_flag"] = (
        df["yoy_service_change_pct"] < 0
    ).fillna(False).astype(int)

    output["negative_payment_trend_flag"] = (
        df["yoy_payment_change_pct"] < 0
    ).fillna(False).astype(int)

    # ========================================================
    # OVERALL DASHBOARD STATUS
    # ========================================================

    print("Creating overall dashboard status...")

    output["dashboard_status"] = np.select(
        [
            (
                (output["high_cost_flag"] == True)
                &
                (output["high_utilization_flag"] == True)
            ),

            (
                (output["high_cost_flag"] == True)
            ),

            (
                (output["high_utilization_flag"] == True)
            ),

            (
                (output["high_risk_flag"] == 1)
            )
        ],
        [
            "HIGH_COST_HIGH_UTILIZATION",
            "HIGH_COST",
            "HIGH_UTILIZATION",
            "HIGH_RISK"
        ],
        default="STABLE"
    )

    # ========================================================
    # FINAL CLEANUP
    # ========================================================

    output = output.replace(
        [np.inf, -np.inf],
        np.nan
    )

    return output


# ============================================================
# VALIDATE OUTPUT
# ============================================================

def validate_output(output):

    print("\n" + "=" * 70)
    print("VALIDATING DASHBOARD DATASET")
    print("=" * 70)

    # --------------------------------------------------------
    # Row count
    # --------------------------------------------------------

    print(
        "Output rows:",
        f"{len(output):,}"
    )

    # --------------------------------------------------------
    # Grain
    # --------------------------------------------------------

    duplicate_count = output.duplicated(
        subset=[
            "Rndrng_NPI",
            "Year"
        ]
    ).sum()

    print(
        "Duplicate NPI-Year rows:",
        f"{duplicate_count:,}"
    )

    if duplicate_count != 0:

        raise ValueError(
            "Dashboard dataset grain failed."
        )

    # --------------------------------------------------------
    # ACO
    # --------------------------------------------------------

    print(
        "Unique ACOs:",
        output["ACO_ID"].nunique()
    )

    print(
        "Missing ACO_ID:",
        output["ACO_ID"].isna().sum()
    )

    if output["ACO_ID"].isna().sum() != 0:

        raise ValueError(
            "Missing ACO_ID values."
        )

    # --------------------------------------------------------
    # Infinite values
    # --------------------------------------------------------

    numeric_columns = (
        output
        .select_dtypes(include=[np.number])
        .columns
    )

    infinite_count = 0

    for column in numeric_columns:

        infinite_count += int(
            np.isinf(
                output[column]
            ).sum()
        )

    print(
        "Infinite values:",
        infinite_count
    )

    if infinite_count != 0:

        raise ValueError(
            "Infinite values detected."
        )

    # --------------------------------------------------------
    # Required dashboard fields
    # --------------------------------------------------------

    required_output = [
        "Rndrng_NPI",
        "provider_name",
        "ACO_ID",
        "Year",
        "beneficiaries",
        "services",
        "medicare_payment",
        "utilization_score",
        "cost_score",
        "provider_segment",
        "dashboard_status"
    ]

    missing = [
        column
        for column in required_output
        if column not in output.columns
    ]

    if missing:

        raise ValueError(
            f"Missing dashboard output columns: {missing}"
        )

    print(
        "Required dashboard fields: PASSED"
    )

    # --------------------------------------------------------
    # Segment distribution
    # --------------------------------------------------------

    print("\nProvider segment distribution:")

    print(
        output["provider_segment"]
        .value_counts(dropna=False)
    )

    # --------------------------------------------------------
    # Dashboard status
    # --------------------------------------------------------

    print("\nDashboard status distribution:")

    print(
        output["dashboard_status"]
        .value_counts(dropna=False)
    )

    print(
        "\nDashboard dataset validation: PASSED"
    )


# ============================================================
# SAVE
# ============================================================

def save_output(output):

    print("\n" + "=" * 70)
    print("SAVING PROVIDER DASHBOARD ANALYTICS")
    print("=" * 70)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print(
        f"Rows: {len(output):,}"
    )

    print(
        f"Columns: {len(output.columns):,}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    df = load_data()

    validate_input(df)

    df = convert_numeric_columns(df)

    dashboard_df = create_dashboard_analytics(
        df
    )

    validate_output(
        dashboard_df
    )

    save_output(
        dashboard_df
    )

    print("\n" + "=" * 70)
    print(
        "PROVIDER DASHBOARD ANALYTICS COMPLETED SUCCESSFULLY"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()