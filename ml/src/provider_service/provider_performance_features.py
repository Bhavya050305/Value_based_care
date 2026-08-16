from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_PATH = Path(
    "data/processed/provider_service/provider_features_stage3.csv"
)

OUTPUT_PATH = Path(
    "data/processed/provider_service/provider_features_stage4.csv"
)


# ============================================================
# HELPER FUNCTION
# ============================================================

def safe_divide(numerator, denominator):
    """
    Safely divide two pandas Series.

    Rules:
    - Convert numerator and denominator to numeric.
    - Treat zero denominators as invalid.
    - Return NaN for invalid divisions.
    - Never allow infinity values.
    """

    numerator = pd.to_numeric(
        numerator,
        errors="coerce"
    )

    denominator = pd.to_numeric(
        denominator,
        errors="coerce"
    )

    denominator = denominator.replace(
        0,
        np.nan
    )

    result = numerator.div(
        denominator
    )

    result = result.replace(
        [np.inf, -np.inf],
        np.nan
    )

    return result


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("=" * 60)
    print("PROVIDER FEATURE ENGINEERING - STAGE 4")
    print("PROVIDER PERFORMANCE / EFFICIENCY FEATURES")
    print("=" * 60)

    print("\nLoading Stage 3 dataset...")

    if not INPUT_PATH.exists():

        raise FileNotFoundError(
            f"Stage 3 dataset not found:\n{INPUT_PATH}"
        )

    df = pd.read_csv(
        INPUT_PATH,
        low_memory=False
    )

    print(
        f"Rows loaded: {len(df):,}"
    )

    print(
        f"Columns loaded: {len(df.columns):,}"
    )

    return df


# ============================================================
# INPUT VALIDATION
# ============================================================

def validate_input(df):

    print("\n" + "=" * 60)
    print("STAGE 4 INPUT VALIDATION")
    print("=" * 60)

    required_columns = [

        # Provider identity
        "Rndrng_NPI",
        "Year",

        # Overall utilization / financial
        "Tot_HCPCS_Cds",
        "Tot_Benes",
        "Tot_Srvcs",
        "Tot_Sbmtd_Chrg",
        "Tot_Mdcr_Alowd_Amt",
        "Tot_Mdcr_Pymt_Amt",
        "Tot_Mdcr_Stdzd_Amt",

        # Medical
        "Med_Tot_Benes",
        "Med_Tot_Srvcs",
        "Med_Mdcr_Alowd_Amt",
        "Med_Mdcr_Pymt_Amt",

        # Drug
        "Drug_Tot_Benes",
        "Drug_Tot_Srvcs",
        "Drug_Mdcr_Alowd_Amt",
        "Drug_Mdcr_Pymt_Amt",

        # Risk / condition
        "Bene_Avg_Risk_Scre",
        "overall_condition_burden",
        "physical_health_burden",
        "behavioral_health_burden",
        "high_condition_burden_count",

        # Stage 1 foundational features
        "services_per_beneficiary",
        "payment_per_service",
        "payment_per_beneficiary",
        "allowed_amount_per_service",
        "standardized_amount_per_service",
        "payment_to_allowed_ratio"
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        print("Missing required columns:")

        for column in missing:

            print(
                f"- {column}"
            )

        raise ValueError(
            "Stage 4 input validation failed."
        )

    print(
        "Required columns: PASSED"
    )

    # --------------------------------------------------------
    # NPI + YEAR GRAIN
    # --------------------------------------------------------

    duplicate_count = df.duplicated(
        subset=[
            "Rndrng_NPI",
            "Year"
        ]
    ).sum()

    print(
        f"Duplicate NPI-Year rows: "
        f"{duplicate_count:,}"
    )

    if duplicate_count != 0:

        raise ValueError(
            "Duplicate NPI-Year rows detected."
        )

    print(
        "NPI + Year grain: PASSED"
    )


# ============================================================
# PERFORMANCE FEATURES
# ============================================================

def create_performance_features(df):

    print("\n" + "=" * 60)
    print("CREATING PROVIDER PERFORMANCE FEATURES")
    print("=" * 60)

    new_features = {}

    # ========================================================
    # 1. SERVICE INTENSITY
    # ========================================================

    print(
        "\nCreating service intensity features..."
    )

    new_features[
        "service_intensity_per_beneficiary"
    ] = safe_divide(
        df["Tot_Srvcs"],
        df["Tot_Benes"]
    )

    new_features[
        "hcpcs_intensity_per_beneficiary"
    ] = safe_divide(
        df["Tot_HCPCS_Cds"],
        df["Tot_Benes"]
    )

    new_features[
        "services_per_condition_burden"
    ] = safe_divide(
        df["Tot_Srvcs"],
        df["overall_condition_burden"]
    )

    new_features[
        "services_per_risk_score"
    ] = safe_divide(
        df["Tot_Srvcs"],
        df["Bene_Avg_Risk_Scre"]
    )

    # ========================================================
    # 2. PAYMENT EFFICIENCY
    # ========================================================

    print(
        "Creating payment efficiency features..."
    )

    new_features[
        "payment_efficiency"
    ] = safe_divide(
        df["Tot_Mdcr_Pymt_Amt"],
        df["Tot_Mdcr_Alowd_Amt"]
    )

    new_features[
        "standardized_payment_ratio"
    ] = safe_divide(
        df["Tot_Mdcr_Stdzd_Amt"],
        df["Tot_Mdcr_Pymt_Amt"]
    )

    new_features[
        "payment_to_charge_ratio"
    ] = safe_divide(
        df["Tot_Mdcr_Pymt_Amt"],
        df["Tot_Sbmtd_Chrg"]
    )

    new_features[
        "allowed_to_charge_ratio"
    ] = safe_divide(
        df["Tot_Mdcr_Alowd_Amt"],
        df["Tot_Sbmtd_Chrg"]
    )

    # ========================================================
    # 3. STANDARDIZED PAYMENT DIFFERENCE
    # ========================================================

    print(
        "Creating standardized payment features..."
    )

    new_features[
        "payment_vs_standardized_difference"
    ] = (
        pd.to_numeric(
            df["Tot_Mdcr_Pymt_Amt"],
            errors="coerce"
        )
        -
        pd.to_numeric(
            df["Tot_Mdcr_Stdzd_Amt"],
            errors="coerce"
        )
    )

    new_features[
        "payment_vs_standardized_pct"
    ] = safe_divide(
        (
            pd.to_numeric(
                df["Tot_Mdcr_Pymt_Amt"],
                errors="coerce"
            )
            -
            pd.to_numeric(
                df["Tot_Mdcr_Stdzd_Amt"],
                errors="coerce"
            )
        ),
        df["Tot_Mdcr_Stdzd_Amt"]
    )

    # ========================================================
    # 4. RISK-ADJUSTED UTILIZATION
    # ========================================================

    print(
        "Creating risk-adjusted utilization features..."
    )

    risk_adjusted_beneficiary_base = (
        pd.to_numeric(
            df["Tot_Benes"],
            errors="coerce"
        )
        *
        pd.to_numeric(
            df["Bene_Avg_Risk_Scre"],
            errors="coerce"
        )
    )

    new_features[
        "risk_adjusted_services"
    ] = safe_divide(
        df["Tot_Srvcs"],
        risk_adjusted_beneficiary_base
    )

    new_features[
        "risk_adjusted_payment"
    ] = safe_divide(
        df["Tot_Mdcr_Pymt_Amt"],
        risk_adjusted_beneficiary_base
    )

    new_features[
        "risk_adjusted_allowed_amount"
    ] = safe_divide(
        df["Tot_Mdcr_Alowd_Amt"],
        risk_adjusted_beneficiary_base
    )

    # ========================================================
    # 5. CONDITION-BURDEN ADJUSTED FEATURES
    # ========================================================

    print(
        "Creating condition-burden adjusted features..."
    )

    condition_adjusted_beneficiary_base = (
        pd.to_numeric(
            df["Tot_Benes"],
            errors="coerce"
        )
        *
        (
            1
            +
            pd.to_numeric(
                df["overall_condition_burden"],
                errors="coerce"
            )
            /
            100
        )
    )

    new_features[
        "condition_adjusted_payment"
    ] = safe_divide(
        df["Tot_Mdcr_Pymt_Amt"],
        condition_adjusted_beneficiary_base
    )

    new_features[
        "condition_adjusted_services"
    ] = safe_divide(
        df["Tot_Srvcs"],
        condition_adjusted_beneficiary_base
    )

    # ========================================================
    # 6. BENEFICIARY COST FEATURES
    # ========================================================

    print(
        "Creating beneficiary cost features..."
    )

    new_features[
        "payment_per_risk_adjusted_beneficiary"
    ] = safe_divide(
        df["Tot_Mdcr_Pymt_Amt"],
        risk_adjusted_beneficiary_base
    )

    new_features[
        "allowed_per_risk_adjusted_beneficiary"
    ] = safe_divide(
        df["Tot_Mdcr_Alowd_Amt"],
        risk_adjusted_beneficiary_base
    )

    # ========================================================
    # 7. MEDICAL PERFORMANCE
    # ========================================================

    print(
        "Creating medical performance features..."
    )

    new_features[
        "medical_payment_per_service"
    ] = safe_divide(
        df["Med_Mdcr_Pymt_Amt"],
        df["Med_Tot_Srvcs"]
    )

    new_features[
        "medical_allowed_per_service"
    ] = safe_divide(
        df["Med_Mdcr_Alowd_Amt"],
        df["Med_Tot_Srvcs"]
    )

    new_features[
        "medical_payment_per_beneficiary"
    ] = safe_divide(
        df["Med_Mdcr_Pymt_Amt"],
        df["Med_Tot_Benes"]
    )

    # ========================================================
    # 8. DRUG PERFORMANCE
    # ========================================================

    print(
        "Creating drug performance features..."
    )

    new_features[
        "drug_payment_per_service_stage4"
    ] = safe_divide(
        df["Drug_Mdcr_Pymt_Amt"],
        df["Drug_Tot_Srvcs"]
    )

    new_features[
        "drug_allowed_per_service_stage4"
    ] = safe_divide(
        df["Drug_Mdcr_Alowd_Amt"],
        df["Drug_Tot_Srvcs"]
    )

    new_features[
        "drug_payment_per_beneficiary_stage4"
    ] = safe_divide(
        df["Drug_Mdcr_Pymt_Amt"],
        df["Drug_Tot_Benes"]
    )

    # ========================================================
    # 9. MEDICAL VS DRUG MIX
    # ========================================================

    print(
        "Creating service mix performance features..."
    )

    new_features[
        "medical_payment_share"
    ] = safe_divide(
        df["Med_Mdcr_Pymt_Amt"],
        df["Tot_Mdcr_Pymt_Amt"]
    )

    new_features[
        "drug_payment_share"
    ] = safe_divide(
        df["Drug_Mdcr_Pymt_Amt"],
        df["Tot_Mdcr_Pymt_Amt"]
    )

    new_features[
        "medical_service_share_stage4"
    ] = safe_divide(
        df["Med_Tot_Srvcs"],
        df["Tot_Srvcs"]
    )

    new_features[
        "drug_service_share_stage4"
    ] = safe_divide(
        df["Drug_Tot_Srvcs"],
        df["Tot_Srvcs"]
    )

    # ========================================================
    # SUPPRESSION-AWARE COMPONENT SHARE HANDLING
    # ========================================================

    print(
        "Applying suppression-aware component share handling..."
    )

    if "drug_data_suppressed" in df.columns:

        suppressed_mask = (
            df["drug_data_suppressed"]
            .fillna(False)
            .astype(bool)
        )

        suppressed_count = int(
            suppressed_mask.sum()
        )

        print(
            f"Suppressed rows detected: "
            f"{suppressed_count:,}"
        )

        # IMPORTANT:
        # new_features is a dictionary.
        # Therefore we cannot use:
        #
        # new_features.loc[...]
        #
        # Instead, each dictionary value is a pandas Series
        # and must be modified individually.

        new_features[
            "medical_payment_share"
        ] = new_features[
            "medical_payment_share"
        ].mask(
            suppressed_mask,
            np.nan
        )

        new_features[
            "drug_payment_share"
        ] = new_features[
            "drug_payment_share"
        ].mask(
            suppressed_mask,
            np.nan
        )

        new_features[
            "medical_service_share_stage4"
        ] = new_features[
            "medical_service_share_stage4"
        ].mask(
            suppressed_mask,
            np.nan
        )

        new_features[
            "drug_service_share_stage4"
        ] = new_features[
            "drug_service_share_stage4"
        ].mask(
            suppressed_mask,
            np.nan
        )

        print(
            "Suppressed component shares marked unavailable: PASSED"
        )

    else:

        print(
            "drug_data_suppressed column not present."
        )

    # ========================================================
    # 10. TEMPORAL PERFORMANCE INDICATORS
    # ========================================================

    print(
        "Creating temporal performance indicators..."
    )

    if "yoy_payment_change_pct" in df.columns:

        new_features[
            "performance_payment_trend"
        ] = df[
            "yoy_payment_change_pct"
        ]

    if "yoy_service_change_pct" in df.columns:

        new_features[
            "performance_service_trend"
        ] = df[
            "yoy_service_change_pct"
        ]

    if "yoy_beneficiary_change_pct" in df.columns:

        new_features[
            "performance_beneficiary_trend"
        ] = df[
            "yoy_beneficiary_change_pct"
        ]

    if "yoy_payment_per_service_change_pct" in df.columns:

        new_features[
            "performance_payment_per_service_trend"
        ] = df[
            "yoy_payment_per_service_change_pct"
        ]

    if "yoy_risk_score_change_pct" in df.columns:

        new_features[
            "performance_risk_trend"
        ] = df[
            "yoy_risk_score_change_pct"
        ]

    # ========================================================
    # ADD ALL FEATURES AT ONCE
    # ========================================================

    feature_df = pd.DataFrame(
        new_features,
        index=df.index
    )

    df = pd.concat(
        [
            df,
            feature_df
        ],
        axis=1
    )

    print(
        f"\nNew performance features created: "
        f"{len(new_features)}"
    )

    for feature in new_features:

        print(
            f"- {feature}"
        )

    return df, list(
        new_features.keys()
    )


# ============================================================
# FEATURE VALIDATION
# ============================================================

def validate_features(
    df,
    new_features
):

    print("\n" + "=" * 60)
    print("STAGE 4 FEATURE VALIDATION")
    print("=" * 60)

    # --------------------------------------------------------
    # FEATURE EXISTENCE
    # --------------------------------------------------------

    missing = [
        feature
        for feature in new_features
        if feature not in df.columns
    ]

    if missing:

        print("Missing features:")

        for feature in missing:

            print(
                f"- {feature}"
            )

        raise ValueError(
            "Stage 4 feature creation failed."
        )

    print(
        "All expected performance features exist: PASSED"
    )

    # --------------------------------------------------------
    # ROW COUNT
    # --------------------------------------------------------

    if len(df) != 150000:

        raise ValueError(
            f"Unexpected row count: "
            f"{len(df):,}"
        )

    print(
        "Row count preservation: PASSED "
        f"({len(df):,})"
    )

    # --------------------------------------------------------
    # NPI-YEAR GRAIN
    # --------------------------------------------------------

    duplicate_count = df.duplicated(
        subset=[
            "Rndrng_NPI",
            "Year"
        ]
    ).sum()

    print(
        f"Duplicate NPI-Year rows: "
        f"{duplicate_count:,}"
    )

    if duplicate_count != 0:

        raise ValueError(
            "NPI-Year uniqueness failed."
        )

    print(
        "NPI + Year grain: PASSED"
    )

    # --------------------------------------------------------
    # INFINITE VALUES
    # --------------------------------------------------------

    numeric_new_features = df[
        new_features
    ].select_dtypes(
        include=np.number
    )

    infinite_count = np.isinf(
        numeric_new_features.to_numpy()
    ).sum()

    print(
        f"Infinite values: "
        f"{infinite_count:,}"
    )

    if infinite_count != 0:

        raise ValueError(
            "Infinite values detected."
        )

    print(
        "Infinite-value validation: PASSED"
    )

    # --------------------------------------------------------
    # NULL SUMMARY
    # --------------------------------------------------------

    print(
        "\nNull counts in performance features:"
    )

    null_counts = (
        df[new_features]
        .isna()
        .sum()
    )

    null_features = null_counts[
        null_counts > 0
    ]

    if len(null_features) == 0:

        print(
            "No null values detected."
        )

    else:

        for feature, count in null_features.items():

            print(
                f"- {feature}: {count:,}"
            )

    # --------------------------------------------------------
    # SUMMARY STATISTICS
    # --------------------------------------------------------

    print(
        "\nPerformance feature summary:"
    )

    summary_features = [

        "service_intensity_per_beneficiary",

        "payment_efficiency",

        "standardized_payment_ratio",

        "payment_to_charge_ratio",

        "allowed_to_charge_ratio",

        "payment_vs_standardized_pct",

        "risk_adjusted_services",

        "risk_adjusted_payment",

        "condition_adjusted_payment"
    ]

    available_summary_features = [
        feature
        for feature in summary_features
        if feature in df.columns
    ]

    if available_summary_features:

        print(
            df[
                available_summary_features
            ]
            .describe()
            .round(4)
            .to_string()
        )


# ============================================================
# SAVE DATASET
# ============================================================

def save_dataset(df):

    print("\n" + "=" * 60)
    print("STAGE 4 DATASET SAVING")
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


# ============================================================
# MAIN
# ============================================================

def main():

    df = load_data()

    validate_input(
        df
    )

    df, new_features = create_performance_features(
        df
    )

    validate_features(
        df,
        new_features
    )

    save_dataset(
        df
    )

    print("\n" + "=" * 60)
    print("STAGE 4 COMPLETED SUCCESSFULLY")
    print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()