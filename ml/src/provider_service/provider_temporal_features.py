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

        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    print(
        "Required columns: PASSED"
    )

    # -----------------------------------------------------
    # Convert identifiers
    # -----------------------------------------------------

    df["Rndrng_NPI"] = (
        pd.to_numeric(
            df["Rndrng_NPI"],
            errors="coerce"
        )
    )

    df["Year"] = (
        pd.to_numeric(
            df["Year"],
            errors="coerce"
        )
    )

    invalid_npi = df["Rndrng_NPI"].isna().sum()
    invalid_year = df["Year"].isna().sum()

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


# =========================================================
# SORT DATA
# =========================================================

def sort_data(df):

    print("\n" + "=" * 60)
    print("SORTING PROVIDER HISTORY")
    print("=" * 60)

    df = df.sort_values(
        [
            "Rndrng_NPI",
            "Year"
        ]
    ).reset_index(
        drop=True
    )

    print(
        "Sorted by NPI and Year: PASSED"
    )

    return df


# =========================================================
# CREATE YEAR-OVER-YEAR FEATURES
# =========================================================

def create_yoy_features(df):

    print("\n" + "=" * 60)
    print("CREATING YEAR-OVER-YEAR FEATURES")
    print("=" * 60)

    # -----------------------------------------------------
    # Previous-year values
    # -----------------------------------------------------

    print(
        "\nCreating previous-year provider values..."
    )

    group = df.groupby(
        "Rndrng_NPI",
        sort=False
    )

    df["previous_year"] = group["Year"].shift(1)

    df["previous_year_beneficiaries"] = (
        group["Tot_Benes"].shift(1)
    )

    df["previous_year_services"] = (
        group["Tot_Srvcs"].shift(1)
    )

    df["previous_year_payment"] = (
        group["Tot_Mdcr_Pymt_Amt"].shift(1)
    )

    df["previous_year_allowed_amount"] = (
        group["Tot_Mdcr_Alowd_Amt"].shift(1)
    )

    df["previous_year_payment_per_service"] = (
        group["payment_per_service"].shift(1)
    )

    df["previous_year_services_per_beneficiary"] = (
        group["services_per_beneficiary"].shift(1)
    )

    df["previous_year_payment_per_beneficiary"] = (
        group["payment_per_beneficiary"].shift(1)
    )

    df["previous_year_risk_score"] = (
        group["beneficiary_risk_score"].shift(1)
    )

    df["previous_year_condition_burden"] = (
        group["overall_condition_burden"].shift(1)
    )

    # -----------------------------------------------------
    # Validate actual consecutive year
    # -----------------------------------------------------

    print(
        "Checking whether previous observation is "
        "actually the previous calendar year..."
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

    # If provider has a gap, previous observation
    # must not be treated as a true YoY comparison.

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
    # Safe percentage change
    # -----------------------------------------------------

    def percentage_change(
        current,
        previous
    ):

        previous = previous.replace(
            0,
            np.nan
        )

        return (
            (current - previous)
            / previous
        ) * 100

    # -----------------------------------------------------
    # YoY beneficiary change
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
    # YoY service change
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
    # YoY payment change
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
    # YoY allowed amount change
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
    # YoY payment per service
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
    # YoY services per beneficiary
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
    # YoY payment per beneficiary
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
    # YoY risk score change
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
    # YoY condition burden change
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
# PROVIDER OBSERVATION FEATURES
# =========================================================

def create_provider_history_features(df):

    print("\n" + "=" * 60)
    print("CREATING PROVIDER HISTORY FEATURES")
    print("=" * 60)

    group = df.groupby(
        "Rndrng_NPI"
    )

    # -----------------------------------------------------
    # First and last observed year
    # -----------------------------------------------------

    df["provider_first_year"] = (
        group["Year"]
        .transform("min")
    )

    df["provider_last_year"] = (
        group["Year"]
        .transform("max")
    )

    # -----------------------------------------------------
    # Number of observed years
    # -----------------------------------------------------

    df["provider_years_observed"] = (
        group["Year"]
        .transform("nunique")
    )

    # -----------------------------------------------------
    # Provider history length
    # -----------------------------------------------------

    df["provider_history_span_years"] = (
        df["provider_last_year"]
        -
        df["provider_first_year"]
        +
        1
    )

    # -----------------------------------------------------
    # Whether provider has complete 5-year history
    # -----------------------------------------------------

    df["complete_5_year_history"] = (
        df["provider_years_observed"] == 5
    )

    # -----------------------------------------------------
    # Whether current row is first observation
    # -----------------------------------------------------

    df["is_first_provider_year"] = (
        df["Year"]
        ==
        df["provider_first_year"]
    )

    # -----------------------------------------------------
    # Whether current row is last observation
    # -----------------------------------------------------

    df["is_last_provider_year"] = (
        df["Year"]
        ==
        df["provider_last_year"]
    )

    print(
        "Provider history features created."
    )

    return df


# =========================================================
# LONG-TERM 2020-2024 CHANGE
# =========================================================

def create_long_term_features(df):

    print("\n" + "=" * 60)
    print("CREATING LONG-TERM PROVIDER TRENDS")
    print("=" * 60)

    group = df.groupby(
        "Rndrng_NPI"
    )

    # -----------------------------------------------------
    # First observed values
    # -----------------------------------------------------

    first_payment = group[
        "Tot_Mdcr_Pymt_Amt"
    ].transform("first")

    first_services = group[
        "Tot_Srvcs"
    ].transform("first")

    first_beneficiaries = group[
        "Tot_Benes"
    ].transform("first")

    first_payment_per_service = group[
        "payment_per_service"
    ].transform("first")

    first_risk = group[
        "beneficiary_risk_score"
    ].transform("first")

    first_condition_burden = group[
        "overall_condition_burden"
    ].transform("first")

    # -----------------------------------------------------
    # Last observed values
    # -----------------------------------------------------

    last_payment = group[
        "Tot_Mdcr_Pymt_Amt"
    ].transform("last")

    last_services = group[
        "Tot_Srvcs"
    ].transform("last")

    last_beneficiaries = group[
        "Tot_Benes"
    ].transform("last")

    last_payment_per_service = group[
        "payment_per_service"
    ].transform("last")

    last_risk = group[
        "beneficiary_risk_score"
    ].transform("last")

    last_condition_burden = group[
        "overall_condition_burden"
    ].transform("last")

    # -----------------------------------------------------
    # Safe percentage change
    # -----------------------------------------------------

    def pct_change(
        current,
        previous
    ):

        previous = previous.replace(
            0,
            np.nan
        )

        return (
            (current - previous)
            / previous
        ) * 100

    # -----------------------------------------------------
    # Long-term changes
    # -----------------------------------------------------

    df["long_term_payment_change_pct"] = pct_change(
        last_payment,
        first_payment
    )

    df["long_term_service_change_pct"] = pct_change(
        last_services,
        first_services
    )

    df["long_term_beneficiary_change_pct"] = pct_change(
        last_beneficiaries,
        first_beneficiaries
    )

    df["long_term_payment_per_service_change_pct"] = (
        pct_change(
            last_payment_per_service,
            first_payment_per_service
        )
    )

    df["long_term_risk_score_change_pct"] = pct_change(
        last_risk,
        first_risk
    )

    df["long_term_condition_burden_change_pct"] = pct_change(
        last_condition_burden,
        first_condition_burden
    )

    print(
        "Long-term provider trends created."
    )

    return df


# =========================================================
# TEMPORAL VALIDATION
# =========================================================

def validate_temporal_features(df):

    print("\n" + "=" * 60)
    print("STAGE 3 TEMPORAL VALIDATION")
    print("=" * 60)

    expected_features = [
        "previous_year",
        "consecutive_year",
        "yoy_beneficiary_change_pct",
        "yoy_service_change_pct",
        "yoy_payment_change_pct",
        "yoy_allowed_amount_change_pct",
        "yoy_payment_per_service_change_pct",
        "yoy_services_per_beneficiary_change_pct",
        "yoy_payment_per_beneficiary_change_pct",
        "yoy_risk_score_change_pct",
        "yoy_condition_burden_change_pct",
        "provider_first_year",
        "provider_last_year",
        "provider_years_observed",
        "provider_history_span_years",
        "complete_5_year_history",
        "is_first_provider_year",
        "is_last_provider_year",
        "long_term_payment_change_pct",
        "long_term_service_change_pct",
        "long_term_beneficiary_change_pct",
        "long_term_payment_per_service_change_pct",
        "long_term_risk_score_change_pct",
        "long_term_condition_burden_change_pct",
    ]

    # -----------------------------------------------------
    # Check feature existence
    # -----------------------------------------------------

    missing = [
        column
        for column in expected_features
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing temporal features: {missing}"
        )

    print(
        "Expected temporal features: PASSED"
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
            "NPI + Year grain changed."
        )

    print(
        "NPI + Year grain: PASSED"
    )

    # -----------------------------------------------------
    # Consecutive-year validation
    # -----------------------------------------------------

    invalid_comparisons = (
        (~df["consecutive_year"])
        &
        (
            df[
                "yoy_payment_change_pct"
            ].notna()
        )
    ).sum()

    print(
        "Invalid YoY comparisons:",
        f"{invalid_comparisons:,}"
    )

    if invalid_comparisons != 0:

        raise ValueError(
            "Non-consecutive years were used for YoY calculations."
        )

    print(
        "Consecutive-year validation: PASSED"
    )

    # -----------------------------------------------------
    # Infinite values
    # -----------------------------------------------------

    numeric_features = [
        column
        for column in expected_features
        if column != "consecutive_year"
        and column != "complete_5_year_history"
        and column != "is_first_provider_year"
        and column != "is_last_provider_year"
    ]

    infinite_count = 0

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
    # Temporal summary
    # -----------------------------------------------------

    print("\nProvider history summary:")

    print(
        "Unique providers:",
        f"{df['Rndrng_NPI'].nunique():,}"
    )

    print(
        "Providers with complete 5-year history:",
        f"{df.loc[df['complete_5_year_history'], 'Rndrng_NPI'].nunique():,}"
    )

    print(
        "Providers with less than 5 years:",
        f"{df.loc[~df['complete_5_year_history'], 'Rndrng_NPI'].nunique():,}"
    )

    print(
        "\nYoY comparison rows:",
        f"{df['consecutive_year'].sum():,}"
    )

    print(
        "Rows without valid previous year:",
        f"{(~df['consecutive_year']).sum():,}"
    )


# =========================================================
# SAVE
# =========================================================

def save_features(df):

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\n" + "=" * 60)
    print("STAGE 3 DATASET SAVED")
    print("=" * 60)

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
        f"{len(df.columns):,}"
    )


# =========================================================
# MAIN
# =========================================================

def main():

    df = load_stage2_data()

    validate_input(
        df
    )

    df = sort_data(
        df
    )

    df = create_yoy_features(
        df
    )

    df = create_provider_history_features(
        df
    )

    df = create_long_term_features(
        df
    )

    validate_temporal_features(
        df
    )

    save_features(
        df
    )

    print("\n" + "=" * 60)
    print("STAGE 3 COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()