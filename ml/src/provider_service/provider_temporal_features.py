from pathlib import Path

import numpy as np
import pandas as pd


# =========================================================
# CONFIGURATION
# =========================================================

INPUT_PATH = Path(
    "data/processed/provider_service/provider_features_stage2.csv"
)

OUTPUT_PATH = Path(
    "data/processed/provider_service/provider_features_stage3.csv"
)


# =========================================================
# LOAD STAGE 2 DATA
# =========================================================

def load_stage2_data():

    print("=" * 60)
    print("PROVIDER FEATURE ENGINEERING - STAGE 3")
    print("TEMPORAL / YEAR-OVER-YEAR FEATURES")
    print("=" * 60)

    print("\nLoading Stage 2 dataset...")

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found:\n{INPUT_PATH}"
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


# =========================================================
# REMOVE UNRELIABLE MEDICAL COMPONENT COLUMNS
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
            print(
                f"  Removing: {column}"
            )

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
    print("STAGE 3 INPUT VALIDATION")
    print("=" * 60)

    required_columns = [
        "Rndrng_NPI",
        "Year",
        "Tot_Benes",
        "Tot_Srvcs",
        "Tot_Mdcr_Pymt_Amt",
        "Tot_Mdcr_Alowd_Amt",
        "payment_per_service",
        "services_per_beneficiary",
        "beneficiary_risk_score",
        "overall_condition_burden",
        "payment_per_beneficiary",
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
            "Stage 3 input validation failed."
        )

    print(
        "Required columns: PASSED"
    )

    # -----------------------------------------------------
    # NPI conversion
    # -----------------------------------------------------

    df["Rndrng_NPI"] = pd.to_numeric(
        df["Rndrng_NPI"],
        errors="coerce"
    )

    # -----------------------------------------------------
    # Year conversion
    # -----------------------------------------------------

    df["Year"] = pd.to_numeric(
        df["Year"],
        errors="coerce"
    )

    invalid_npi = int(
        df["Rndrng_NPI"].isna().sum()
    )

    invalid_year = int(
        df["Year"].isna().sum()
    )

    print(
        "Invalid NPI values:",
        f"{invalid_npi:,}"
    )

    print(
        "Invalid Year values:",
        f"{invalid_year:,}"
    )

    if invalid_npi != 0 or invalid_year != 0:

        raise ValueError(
            "Invalid NPI or Year values detected."
        )

    # -----------------------------------------------------
    # Grain validation
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
            "NPI + Year grain is not unique."
        )

    print(
        "NPI + Year grain: PASSED"
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
            "Medical component columns are still present."
        )

    print(
        "Medical column validation: PASSED"
    )

    return df


# =========================================================
# SORT DATA
# =========================================================

def sort_data(df):

    print("\n" + "=" * 60)
    print("SORTING PROVIDER HISTORY")
    print("=" * 60)

    df = (
        df
        .sort_values(
            [
                "Rndrng_NPI",
                "Year"
            ]
        )
        .reset_index(drop=True)
    )

    print(
        "Sorted by NPI and Year: PASSED"
    )

    return df


# =========================================================
# SAFE PERCENTAGE CHANGE
# =========================================================

def percentage_change(
    current,
    previous
):

    previous = previous.replace(
        0,
        np.nan
    )

    return (
        (
            current - previous
        )
        / previous
    ) * 100


# =========================================================
# CREATE YEAR-OVER-YEAR FEATURES
# =========================================================

def create_yoy_features(df):

    print("\n" + "=" * 60)
    print("CREATING YEAR-OVER-YEAR FEATURES")
    print("=" * 60)

    group = df.groupby(
        "Rndrng_NPI",
        sort=False
    )

    # -----------------------------------------------------
    # Previous-year provider values
    # -----------------------------------------------------

    print(
        "\nCreating previous-year provider values..."
    )

    df["previous_year"] = (
        group["Year"]
        .shift(1)
    )

    df["previous_year_beneficiaries"] = (
        group["Tot_Benes"]
        .shift(1)
    )

    df["previous_year_services"] = (
        group["Tot_Srvcs"]
        .shift(1)
    )

    df["previous_year_payment"] = (
        group["Tot_Mdcr_Pymt_Amt"]
        .shift(1)
    )

    df["previous_year_allowed_amount"] = (
        group["Tot_Mdcr_Alowd_Amt"]
        .shift(1)
    )

    df["previous_year_payment_per_service"] = (
        group["payment_per_service"]
        .shift(1)
    )

    df["previous_year_services_per_beneficiary"] = (
        group["services_per_beneficiary"]
        .shift(1)
    )

    df["previous_year_payment_per_beneficiary"] = (
        group["payment_per_beneficiary"]
        .shift(1)
    )

    df["previous_year_risk_score"] = (
        group["beneficiary_risk_score"]
        .shift(1)
    )

    df["previous_year_condition_burden"] = (
        group["overall_condition_burden"]
        .shift(1)
    )

    # -----------------------------------------------------
    # Check actual consecutive calendar year
    # -----------------------------------------------------

    print(
        "Checking consecutive calendar years..."
    )

    df["consecutive_year"] = (
        df["previous_year"].notna()
        &
        (
            df["Year"]
            ==
            df["previous_year"] + 1
        )
    )

    # -----------------------------------------------------
    # Remove invalid previous-year comparisons
    # -----------------------------------------------------

    comparison_columns = [

        "previous_year_beneficiaries",

        "previous_year_services",

        "previous_year_payment",

        "previous_year_allowed_amount",

        "previous_year_payment_per_service",

        "previous_year_services_per_beneficiary",

        "previous_year_payment_per_beneficiary",

        "previous_year_risk_score",

        "previous_year_condition_burden",
    ]

    for column in comparison_columns:

        df.loc[
            ~df["consecutive_year"],
            column
        ] = np.nan

    # -----------------------------------------------------
    # Beneficiary YoY
    # -----------------------------------------------------

    print(
        "Creating beneficiary YoY change..."
    )

    df["yoy_beneficiary_change_pct"] = (
        percentage_change(
            df["Tot_Benes"],
            df["previous_year_beneficiaries"]
        )
    )

    # -----------------------------------------------------
    # Service YoY
    # -----------------------------------------------------

    print(
        "Creating service YoY change..."
    )

    df["yoy_service_change_pct"] = (
        percentage_change(
            df["Tot_Srvcs"],
            df["previous_year_services"]
        )
    )

    # -----------------------------------------------------
    # Payment YoY
    # -----------------------------------------------------

    print(
        "Creating payment YoY change..."
    )

    df["yoy_payment_change_pct"] = (
        percentage_change(
            df["Tot_Mdcr_Pymt_Amt"],
            df["previous_year_payment"]
        )
    )

    # -----------------------------------------------------
    # Allowed amount YoY
    # -----------------------------------------------------

    print(
        "Creating allowed amount YoY change..."
    )

    df["yoy_allowed_amount_change_pct"] = (
        percentage_change(
            df["Tot_Mdcr_Alowd_Amt"],
            df["previous_year_allowed_amount"]
        )
    )

    # -----------------------------------------------------
    # Payment per service YoY
    # -----------------------------------------------------

    print(
        "Creating payment-per-service YoY change..."
    )

    df["yoy_payment_per_service_change_pct"] = (
        percentage_change(
            df["payment_per_service"],
            df["previous_year_payment_per_service"]
        )
    )

    # -----------------------------------------------------
    # Services per beneficiary YoY
    # -----------------------------------------------------

    print(
        "Creating services-per-beneficiary YoY change..."
    )

    df["yoy_services_per_beneficiary_change_pct"] = (
        percentage_change(
            df["services_per_beneficiary"],
            df["previous_year_services_per_beneficiary"]
        )
    )

    # -----------------------------------------------------
    # Payment per beneficiary YoY
    # -----------------------------------------------------

    print(
        "Creating payment-per-beneficiary YoY change..."
    )

    df["yoy_payment_per_beneficiary_change_pct"] = (
        percentage_change(
            df["payment_per_beneficiary"],
            df["previous_year_payment_per_beneficiary"]
        )
    )

    # -----------------------------------------------------
    # Risk score YoY
    # -----------------------------------------------------

    print(
        "Creating risk-score YoY change..."
    )

    df["yoy_risk_score_change_pct"] = (
        percentage_change(
            df["beneficiary_risk_score"],
            df["previous_year_risk_score"]
        )
    )

    # -----------------------------------------------------
    # Condition burden YoY
    # -----------------------------------------------------

    print(
        "Creating condition-burden YoY change..."
    )

    df["yoy_condition_burden_change_pct"] = (
        percentage_change(
            df["overall_condition_burden"],
            df["previous_year_condition_burden"]
        )
    )

    return df


# =========================================================
# PROVIDER HISTORY FEATURES
# =========================================================

def create_provider_history_features(df):

    print("\n" + "=" * 60)
    print("CREATING PROVIDER HISTORY FEATURES")
    print("=" * 60)

    group = df.groupby(
        "Rndrng_NPI"
    )

    # -----------------------------------------------------
    # First observed year
    # -----------------------------------------------------

    print(
        "Creating provider first year..."
    )

    df["provider_first_year"] = (
        group["Year"]
        .transform("min")
    )

    # -----------------------------------------------------
    # Last observed year
    # -----------------------------------------------------

    print(
        "Creating provider last year..."
    )

    df["provider_last_year"] = (
        group["Year"]
        .transform("max")
    )

    # -----------------------------------------------------
    # Number of observed years
    # -----------------------------------------------------

    print(
        "Creating years observed..."
    )

    df["provider_years_observed"] = (
        group["Year"]
        .transform("nunique")
    )

    # -----------------------------------------------------
    # Provider history span
    # -----------------------------------------------------

    print(
        "Creating provider history span..."
    )

    df["provider_history_span"] = (
        df["provider_last_year"]
        -
        df["provider_first_year"]
    )

    # -----------------------------------------------------
    # Current year index
    # -----------------------------------------------------

    print(
        "Creating provider year index..."
    )

    df["provider_year_index"] = (
        df["Year"]
        -
        df["provider_first_year"]
        +
        1
    )

    # -----------------------------------------------------
    # Provider has prior-year history
    # -----------------------------------------------------

    print(
        "Creating prior-history flag..."
    )

    df["has_prior_year"] = (
        df["previous_year"].notna()
    ).astype(int)

    return df


# =========================================================
# ROLLING / TREND FEATURES
# =========================================================

def create_trend_features(df):

    print("\n" + "=" * 60)
    print("CREATING PROVIDER TREND FEATURES")
    print("=" * 60)

    group = df.groupby(
        "Rndrng_NPI",
        sort=False
    )

    # -----------------------------------------------------
    # Previous 2-year values
    # -----------------------------------------------------

    print(
        "Creating two-year historical values..."
    )

    df["two_years_ago_beneficiaries"] = (
        group["Tot_Benes"]
        .shift(2)
    )

    df["two_years_ago_services"] = (
        group["Tot_Srvcs"]
        .shift(2)
    )

    df["two_years_ago_payment"] = (
        group["Tot_Mdcr_Pymt_Amt"]
        .shift(2)
    )

    # -----------------------------------------------------
    # Validate two-year consecutive history
    # -----------------------------------------------------

    previous_year_2 = (
        group["Year"]
        .shift(2)
    )

    valid_two_year_history = (
        previous_year_2.notna()
        &
        (
            df["Year"]
            ==
            previous_year_2 + 2
        )
    )

    for column in [
        "two_years_ago_beneficiaries",
        "two_years_ago_services",
        "two_years_ago_payment",
    ]:

        df.loc[
            ~valid_two_year_history,
            column
        ] = np.nan

    # -----------------------------------------------------
    # Two-year beneficiary growth
    # -----------------------------------------------------

    print(
        "Creating two-year beneficiary growth..."
    )

    df["two_year_beneficiary_change_pct"] = (
        percentage_change(
            df["Tot_Benes"],
            df["two_years_ago_beneficiaries"]
        )
    )

    # -----------------------------------------------------
    # Two-year service growth
    # -----------------------------------------------------

    print(
        "Creating two-year service growth..."
    )

    df["two_year_service_change_pct"] = (
        percentage_change(
            df["Tot_Srvcs"],
            df["two_years_ago_services"]
        )
    )

    # -----------------------------------------------------
    # Two-year payment growth
    # -----------------------------------------------------

    print(
        "Creating two-year payment growth..."
    )

    df["two_year_payment_change_pct"] = (
        percentage_change(
            df["Tot_Mdcr_Pymt_Amt"],
            df["two_years_ago_payment"]
        )
    )

    # -----------------------------------------------------
    # Provider cumulative observations
    # -----------------------------------------------------

    print(
        "Creating cumulative provider observations..."
    )

    df["provider_observation_number"] = (
        group.cumcount() + 1
    )

    # -----------------------------------------------------
    # Cumulative average services
    # -----------------------------------------------------

    print(
        "Creating historical average services..."
    )

    df["historical_avg_services"] = (
        group["Tot_Srvcs"]
        .transform(
            lambda x:
            x.expanding()
            .mean()
        )
    )

    # -----------------------------------------------------
    # Cumulative average payment
    # -----------------------------------------------------

    print(
        "Creating historical average payment..."
    )

    df["historical_avg_payment"] = (
        group["Tot_Mdcr_Pymt_Amt"]
        .transform(
            lambda x:
            x.expanding()
            .mean()
        )
    )

    # -----------------------------------------------------
    # Current services vs historical average
    # -----------------------------------------------------

    print(
        "Creating service trend ratio..."
    )

    df["services_vs_historical_avg_pct"] = (
        percentage_change(
            df["Tot_Srvcs"],
            df["historical_avg_services"]
        )
    )

    # -----------------------------------------------------
    # Current payment vs historical average
    # -----------------------------------------------------

    print(
        "Creating payment trend ratio..."
    )

    df["payment_vs_historical_avg_pct"] = (
        percentage_change(
            df["Tot_Mdcr_Pymt_Amt"],
            df["historical_avg_payment"]
        )
    )

    return df


# =========================================================
# FEATURE VALIDATION
# =========================================================

def validate_features(df):

    print("\n" + "=" * 60)
    print("STAGE 3 FEATURE VALIDATION")
    print("=" * 60)

    expected_features = [

        # Previous-year features
        "previous_year",
        "previous_year_beneficiaries",
        "previous_year_services",
        "previous_year_payment",
        "previous_year_allowed_amount",
        "previous_year_payment_per_service",
        "previous_year_services_per_beneficiary",
        "previous_year_payment_per_beneficiary",
        "previous_year_risk_score",
        "previous_year_condition_burden",

        # Calendar validation
        "consecutive_year",

        # YoY features
        "yoy_beneficiary_change_pct",
        "yoy_service_change_pct",
        "yoy_payment_change_pct",
        "yoy_allowed_amount_change_pct",
        "yoy_payment_per_service_change_pct",
        "yoy_services_per_beneficiary_change_pct",
        "yoy_payment_per_beneficiary_change_pct",
        "yoy_risk_score_change_pct",
        "yoy_condition_burden_change_pct",

        # Provider history
        "provider_first_year",
        "provider_last_year",
        "provider_years_observed",
        "provider_history_span",
        "provider_year_index",
        "has_prior_year",

        # Two-year history
        "two_years_ago_beneficiaries",
        "two_years_ago_services",
        "two_years_ago_payment",
        "two_year_beneficiary_change_pct",
        "two_year_service_change_pct",
        "two_year_payment_change_pct",

        # Historical trend
        "provider_observation_number",
        "historical_avg_services",
        "historical_avg_payment",
        "services_vs_historical_avg_pct",
        "payment_vs_historical_avg_pct",
    ]

    missing = [
        column
        for column in expected_features
        if column not in df.columns
    ]

    if missing:

        print(
            "Missing Stage 3 features:"
        )

        for column in missing:
            print(
                f"- {column}"
            )

        raise ValueError(
            "Stage 3 feature validation failed."
        )

    print(
        "All expected temporal features exist: PASSED"
    )

    # -----------------------------------------------------
    # Infinite values
    # -----------------------------------------------------

    infinite_count = 0

    numeric_features = [
        column
        for column in expected_features
        if column != "consecutive_year"
        and column != "has_prior_year"
    ]

    for column in numeric_features:

        values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        infinite_count += int(
            np.isinf(values)
            .sum()
        )

    print(
        "Infinite values:",
        f"{infinite_count:,}"
    )

    if infinite_count != 0:

        raise ValueError(
            "Infinite values detected in Stage 3."
        )

    print(
        "Infinite-value validation: PASSED"
    )

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
            "Medical columns detected in Stage 3."
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
        "Duplicate NPI-Year:",
        f"{duplicate_count:,}"
    )

    if duplicate_count != 0:

        raise ValueError(
            "NPI + Year uniqueness failed."
        )

    print(
        "NPI + Year uniqueness: PASSED"
    )

    # -----------------------------------------------------
    # Year coverage
    # -----------------------------------------------------

    years = sorted(
        df["Year"]
        .dropna()
        .unique()
        .tolist()
    )

    print(
        "Years:",
        years
    )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("TEMPORAL FEATURE SUMMARY")
    print("=" * 60)

    print(
        "Temporal features created:",
        len(expected_features)
    )

    for feature in expected_features:
        print(
            f"- {feature}"
        )


# =========================================================
# SAVE DATASET
# =========================================================

def save_dataset(df):

    print("\n" + "=" * 60)
    print("SAVING STAGE 3 DATASET")
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
        "Output path:",
        OUTPUT_PATH
    )

    print(
        "Rows:",
        f"{len(df):,}"
    )

    print(
        "Columns:",
        len(df.columns)
    )

    medical_columns = [
        column
        for column in df.columns
        if column.startswith("Med_")
    ]

    print(
        "Medical columns:",
        medical_columns
    )


# =========================================================
# MAIN PIPELINE
# =========================================================

def main():

    # -----------------------------------------------------
    # 1. Load Stage 2
    # -----------------------------------------------------

    df = load_stage2_data()

    # -----------------------------------------------------
    # 2. Remove medical components defensively
    # -----------------------------------------------------

    df = exclude_medical_columns(
        df
    )

    # -----------------------------------------------------
    # 3. Validate
    # -----------------------------------------------------

    df = validate_input(
        df
    )

    # -----------------------------------------------------
    # 4. Sort provider history
    # -----------------------------------------------------

    df = sort_data(
        df
    )

    # -----------------------------------------------------
    # 5. Create YoY features
    # -----------------------------------------------------

    df = create_yoy_features(
        df
    )

    # -----------------------------------------------------
    # 6. Create provider history features
    # -----------------------------------------------------

    df = create_provider_history_features(
        df
    )

    # -----------------------------------------------------
    # 7. Create trend features
    # -----------------------------------------------------

    df = create_trend_features(
        df
    )

    # -----------------------------------------------------
    # 8. Validate final Stage 3
    # -----------------------------------------------------

    validate_features(
        df
    )

    # -----------------------------------------------------
    # 9. Save
    # -----------------------------------------------------

    save_dataset(
        df
    )

    print("\n" + "=" * 60)
    print("STAGE 3 COMPLETED SUCCESSFULLY")
    print("=" * 60)


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()