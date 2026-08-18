from pathlib import Path

import numpy as np
import pandas as pd


# =========================================================
# CONFIGURATION
# =========================================================

INPUT_PATH = Path(
    "data/processed/provider_service/provider_features_stage3.csv"
)

OUTPUT_PATH = Path(
    "data/processed/provider_service/provider_features_stage4.csv"
)


# =========================================================
# LOAD STAGE 3 DATA
# =========================================================

def load_stage3_data():

    print("=" * 60)
    print("PROVIDER FEATURE ENGINEERING - STAGE 4")
    print("PROVIDER PERFORMANCE / EFFICIENCY FEATURES")
    print("=" * 60)

    print("\nLoading Stage 3 dataset...")

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found:\n{INPUT_PATH}"
        )

    df = pd.read_csv(
        INPUT_PATH,
        low_memory=False
    )

    print(f"Rows loaded: {len(df):,}")
    print(f"Columns loaded: {len(df.columns):,}")

    return df


# =========================================================
# REMOVE MEDICAL COMPONENT COLUMNS
# =========================================================

def exclude_medical_columns(df):

    print("\n" + "=" * 60)
    print("EXCLUDING UNRELIABLE MEDICAL COMPONENT COLUMNS")
    print("=" * 60)

    medical_columns = [
        column
        for column in df.columns
        if column.startswith("Med_")
    ]

    print(
        "Medical columns found:",
        len(medical_columns)
    )

    if medical_columns:

        for column in medical_columns:
            print(f"  Removing: {column}")

        df = df.drop(
            columns=medical_columns
        )

    else:

        print(
            "No medical component columns found."
        )

    print(
        "Columns after exclusion:",
        len(df.columns)
    )

    return df


# =========================================================
# INPUT VALIDATION
# =========================================================

def validate_input(df):

    print("\n" + "=" * 60)
    print("STAGE 4 INPUT VALIDATION")
    print("=" * 60)

    required_columns = [
        "Rndrng_NPI",
        "Year",

        # Provider utilization
        "Tot_HCPCS_Cds",
        "Tot_Benes",
        "Tot_Srvcs",

        # Provider financial metrics
        "Tot_Sbmtd_Chrg",
        "Tot_Mdcr_Alowd_Amt",
        "Tot_Mdcr_Pymt_Amt",
        "Tot_Mdcr_Stdzd_Amt",

        # Existing Stage 1 efficiency features
        "services_per_beneficiary",
        "payment_per_service",
        "payment_per_beneficiary",
        "allowed_amount_per_service",
        "allowed_amount_per_beneficiary",
        "payment_to_allowed_ratio",

        # Risk / clinical features
        "average_risk_score",
        "overall_condition_burden",

        # Stage 3 temporal features
        "yoy_service_change_pct",
        "yoy_payment_change_pct",
        "yoy_payment_per_service_change_pct",
        "yoy_risk_score_change_pct",
        "provider_years_observed"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        print("Missing required columns:")

        for column in missing_columns:
            print(f"- {column}")

        raise ValueError(
            "Stage 4 input validation failed."
        )

    print(
        "Required columns: PASSED"
    )

    # -----------------------------------------------------
    # Medical column validation
    # -----------------------------------------------------

    medical_columns = [
        column
        for column in df.columns
        if column.startswith("Med_")
    ]

    print(
        "Medical columns:",
        medical_columns
    )

    if medical_columns:

        raise ValueError(
            "Stage 4 contains forbidden medical component columns."
        )

    print(
        "Medical column validation: PASSED"
    )

    # -----------------------------------------------------
    # NPI + Year validation
    # -----------------------------------------------------

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
            "NPI + Year grain has been violated."
        )

    print(
        "NPI + Year grain: PASSED"
    )

    # -----------------------------------------------------
    # Year validation
    # -----------------------------------------------------

    years = sorted(
        pd.to_numeric(
            df["Year"],
            errors="coerce"
        )
        .dropna()
        .unique()
        .tolist()
    )

    print(
        "Years detected:",
        years
    )

    if not years:
        raise ValueError(
            "No valid years detected."
        )


# =========================================================
# NUMERIC CONVERSION
# =========================================================

def convert_numeric_columns(df):

    print("\n" + "=" * 60)
    print("NUMERIC COLUMN CONVERSION")
    print("=" * 60)

    numeric_columns = [
        "Tot_HCPCS_Cds",
        "Tot_Benes",
        "Tot_Srvcs",
        "Tot_Sbmtd_Chrg",
        "Tot_Mdcr_Alowd_Amt",
        "Tot_Mdcr_Pymt_Amt",
        "Tot_Mdcr_Stdzd_Amt",

        "services_per_beneficiary",
        "payment_per_service",
        "payment_per_beneficiary",
        "allowed_amount_per_service",
        "allowed_amount_per_beneficiary",
        "payment_to_allowed_ratio",

        "average_risk_score",
        "overall_condition_burden",

        "yoy_service_change_pct",
        "yoy_payment_change_pct",
        "yoy_payment_per_service_change_pct",
        "yoy_risk_score_change_pct",

        "provider_years_observed"
    ]

    numeric_columns = [
        column
        for column in numeric_columns
        if column in df.columns
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    print(
        "Numeric columns converted:",
        len(numeric_columns)
    )

    return df


# =========================================================
# SAFE DIVISION
# =========================================================

def safe_divide(numerator, denominator):

    denominator = denominator.replace(
        0,
        np.nan
    )

    result = numerator / denominator

    result = result.replace(
        [np.inf, -np.inf],
        np.nan
    )

    return result


# =========================================================
# CREATE PERFORMANCE FEATURES
# =========================================================

def create_performance_features(df):

    print("\n" + "=" * 60)
    print("CREATING STAGE 4 PERFORMANCE FEATURES")
    print("=" * 60)

    original_columns = set(
        df.columns
    )

    # =====================================================
    # A. COST EFFICIENCY
    # =====================================================

    print(
        "\nCreating cost-efficiency features..."
    )

    df["payment_efficiency_ratio"] = safe_divide(
        df["Tot_Mdcr_Pymt_Amt"],
        df["Tot_Mdcr_Alowd_Amt"]
    )

    df["standardized_payment_ratio"] = safe_divide(
        df["Tot_Mdcr_Stdzd_Amt"],
        df["Tot_Mdcr_Alowd_Amt"]
    )

    df["payment_to_charge_ratio"] = safe_divide(
        df["Tot_Mdcr_Pymt_Amt"],
        df["Tot_Sbmtd_Chrg"]
    )

    df["allowed_to_charge_ratio"] = safe_divide(
        df["Tot_Mdcr_Alowd_Amt"],
        df["Tot_Sbmtd_Chrg"]
    )

    # =====================================================
    # B. UTILIZATION EFFICIENCY
    # =====================================================

    print(
        "Creating utilization-efficiency features..."
    )

    df["services_per_hcpcs"] = safe_divide(
        df["Tot_Srvcs"],
        df["Tot_HCPCS_Cds"]
    )

    df["beneficiaries_per_hcpcs"] = safe_divide(
        df["Tot_Benes"],
        df["Tot_HCPCS_Cds"]
    )

    df["services_per_provider_beneficiary"] = safe_divide(
        df["Tot_Srvcs"],
        df["Tot_Benes"]
    )

    # =====================================================
    # C. FINANCIAL INTENSITY
    # =====================================================

    print(
        "Creating financial-intensity features..."
    )

    df["payment_per_hcpcs"] = safe_divide(
        df["Tot_Mdcr_Pymt_Amt"],
        df["Tot_HCPCS_Cds"]
    )

    df["allowed_amount_per_hcpcs"] = safe_divide(
        df["Tot_Mdcr_Alowd_Amt"],
        df["Tot_HCPCS_Cds"]
    )

    df["charge_per_hcpcs"] = safe_divide(
        df["Tot_Sbmtd_Chrg"],
        df["Tot_HCPCS_Cds"]
    )

    # =====================================================
    # D. RISK-ADJUSTED UTILIZATION
    # =====================================================

    print(
        "Creating risk-adjusted utilization features..."
    )

    df["risk_adjusted_services"] = safe_divide(
        df["Tot_Srvcs"],
        df["average_risk_score"]
    )

    df["risk_adjusted_payment"] = safe_divide(
        df["Tot_Mdcr_Pymt_Amt"],
        df["average_risk_score"]
    )

    df["risk_adjusted_payment_per_beneficiary"] = safe_divide(
        df["payment_per_beneficiary"],
        df["average_risk_score"]
    )

    # =====================================================
    # E. CONDITION-BURDEN ADJUSTMENT
    # =====================================================

    print(
        "Creating condition-burden adjusted features..."
    )

    df["condition_adjusted_services"] = safe_divide(
        df["Tot_Srvcs"],
        df["overall_condition_burden"]
    )

    df["condition_adjusted_payment"] = safe_divide(
        df["Tot_Mdcr_Pymt_Amt"],
        df["overall_condition_burden"]
    )

    # =====================================================
    # F. PERFORMANCE TREND FEATURES
    # =====================================================

    print(
        "Creating performance-trend features..."
    )

    df["positive_service_growth_flag"] = (
        df["yoy_service_change_pct"] > 0
    ).astype(int)

    df["positive_payment_growth_flag"] = (
        df["yoy_payment_change_pct"] > 0
    ).astype(int)

    df["payment_efficiency_improvement_flag"] = (
        df["yoy_payment_per_service_change_pct"] < 0
    ).astype(int)

    df["risk_increase_flag"] = (
        df["yoy_risk_score_change_pct"] > 0
    ).astype(int)

    # =====================================================
    # G. PERFORMANCE STABILITY
    # =====================================================

    print(
        "Creating performance-stability features..."
    )

    df["service_growth_magnitude"] = (
        df["yoy_service_change_pct"]
        .abs()
    )

    df["payment_growth_magnitude"] = (
        df["yoy_payment_change_pct"]
        .abs()
    )

    df["payment_per_service_change_magnitude"] = (
        df["yoy_payment_per_service_change_pct"]
        .abs()
    )

    # =====================================================
    # H. COMPOSITE PERFORMANCE SIGNAL
    # =====================================================

    print(
        "Creating composite performance signal..."
    )

    efficiency_component = (
        df["payment_efficiency_ratio"]
        .clip(
            lower=0,
            upper=1
        )
    )

    utilization_component = (
        df["services_per_beneficiary"]
        .rank(
            pct=True
        )
    )

    stability_component = (
        1
        -
        (
            df["payment_per_service_change_magnitude"]
            .clip(
                lower=0,
                upper=100
            )
            / 100
        )
    )

    risk_component = (
        1
        -
        (
            df["average_risk_score"]
            .rank(
                pct=True
            )
        )
    )

    df["performance_signal"] = (
        0.35 * efficiency_component
        +
        0.25 * utilization_component
        +
        0.25 * stability_component
        +
        0.15 * risk_component
    )

    # =====================================================
    # I. PERFORMANCE TIER
    # =====================================================

    print(
        "Creating performance tier..."
    )

    df["performance_tier"] = pd.cut(
        df["performance_signal"],
        bins=[
            -np.inf,
            0.25,
            0.50,
            0.75,
            np.inf
        ],
        labels=[
            "Needs Improvement",
            "Developing",
            "Strong",
            "High Performer"
        ]
    )

    # =====================================================
    # NEW FEATURE SUMMARY
    # =====================================================

    new_columns = [
        column
        for column in df.columns
        if column not in original_columns
    ]

    print("\n" + "=" * 60)
    print("STAGE 4 FEATURE SUMMARY")
    print("=" * 60)

    print(
        "New features created:",
        len(new_columns)
    )

    for column in new_columns:
        print(
            f"- {column}"
        )

    return df


# =========================================================
# VALIDATE OUTPUT
# =========================================================

def validate_output(df):

    print("\n" + "=" * 60)
    print("STAGE 4 OUTPUT VALIDATION")
    print("=" * 60)

    # -----------------------------------------------------
    # Medical columns
    # -----------------------------------------------------

    medical_columns = [
        column
        for column in df.columns
        if column.startswith("Med_")
    ]

    print(
        "Medical columns:",
        medical_columns
    )

    if medical_columns:

        raise ValueError(
            "Medical columns detected in Stage 4 output."
        )

    print(
        "Medical column exclusion: PASSED"
    )

    # -----------------------------------------------------
    # Grain
    # -----------------------------------------------------

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
            "Duplicate NPI-Year rows detected."
        )

    print(
        "NPI + Year grain: PASSED"
    )

    # -----------------------------------------------------
    # Infinite values
    # -----------------------------------------------------

    numeric_df = df.select_dtypes(
        include=[np.number]
    )

    infinite_count = int(
        np.isinf(
            numeric_df
        ).sum()
        .sum()
    )

    print(
        "Infinite values:",
        infinite_count
    )

    if infinite_count != 0:

        raise ValueError(
            "Infinite values detected."
        )

    print(
        "Infinite-value validation: PASSED"
    )

    # -----------------------------------------------------
    # Performance features
    # -----------------------------------------------------

    expected_features = [
        "payment_efficiency_ratio",
        "standardized_payment_ratio",
        "payment_to_charge_ratio",
        "allowed_to_charge_ratio",
        "services_per_hcpcs",
        "beneficiaries_per_hcpcs",
        "payment_per_hcpcs",
        "allowed_amount_per_hcpcs",
        "charge_per_hcpcs",
        "risk_adjusted_services",
        "risk_adjusted_payment",
        "risk_adjusted_payment_per_beneficiary",
        "condition_adjusted_services",
        "condition_adjusted_payment",
        "positive_service_growth_flag",
        "positive_payment_growth_flag",
        "payment_efficiency_improvement_flag",
        "risk_increase_flag",
        "service_growth_magnitude",
        "payment_growth_magnitude",
        "payment_per_service_change_magnitude",
        "performance_signal",
        "performance_tier"
    ]

    missing_features = [
        column
        for column in expected_features
        if column not in df.columns
    ]

    if missing_features:

        raise ValueError(
            f"Missing Stage 4 features: {missing_features}"
        )

    print(
        "Expected performance features: PASSED"
    )


# =========================================================
# SAVE OUTPUT
# =========================================================

def save_output(df):

    print("\n" + "=" * 60)
    print("SAVING STAGE 4 DATASET")
    print("=" * 60)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        f"Output path: {OUTPUT_PATH}"
    )

    print(
        f"Rows: {len(df):,}"
    )

    print(
        f"Columns: {len(df.columns):,}"
    )

    print(
        "Medical columns:",
        [
            column
            for column in df.columns
            if column.startswith("Med_")
        ]
    )


# =========================================================
# MAIN
# =========================================================

def main():

    df = load_stage3_data()

    df = exclude_medical_columns(
        df
    )

    validate_input(
        df
    )

    df = convert_numeric_columns(
        df
    )

    df = create_performance_features(
        df
    )

    validate_output(
        df
    )

    save_output(
        df
    )

    print("\n" + "=" * 60)
    print("STAGE 4 COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()