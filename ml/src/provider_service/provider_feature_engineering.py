from pathlib import Path

import numpy as np
import pandas as pd


# =========================================================
# CONFIGURATION
# =========================================================

INPUT_PATH = Path(
    "data/processed/provider_service/provider_combined_clean.csv"
)

OUTPUT_PATH = Path(
    "data/processed/provider_service/provider_features_stage1.csv"
)


# =========================================================
# LOAD CLEAN DATA
# =========================================================

def load_clean_data():

    print("=" * 60)
    print("PROVIDER FEATURE ENGINEERING - STAGE 1")
    print("=" * 60)

    print("\nLoading cleaned provider dataset...")

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
# VALIDATE INPUT
# =========================================================

def validate_input(df):

    print("\n" + "=" * 60)
    print("INPUT VALIDATION")
    print("=" * 60)

    required_columns = [

        # Identity / grain
        "Rndrng_NPI",
        "Year",

        # Overall utilization
        "Tot_HCPCS_Cds",
        "Tot_Benes",
        "Tot_Srvcs",

        # Overall Medicare cost
        "Tot_Sbmtd_Chrg",
        "Tot_Mdcr_Alowd_Amt",
        "Tot_Mdcr_Pymt_Amt",
        "Tot_Mdcr_Stdzd_Amt",

        # Drug component
        "Drug_Tot_HCPCS_Cds",
        "Drug_Tot_Benes",
        "Drug_Tot_Srvcs",
        "Drug_Sbmtd_Chrg",
        "Drug_Mdcr_Alowd_Amt",
        "Drug_Mdcr_Pymt_Amt",
        "Drug_Mdcr_Stdzd_Amt",

        # Beneficiary demographics / risk
        "Bene_Avg_Age",
        "Bene_Feml_Cnt",
        "Bene_Male_Cnt",
        "Bene_Dual_Cnt",
        "Bene_Ndual_Cnt",
        "Bene_Avg_Risk_Scre",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        print("Missing columns:")

        for column in missing_columns:
            print(f"- {column}")

        raise ValueError(
            "Input validation failed."
        )

    # -----------------------------------------------------
    # Confirm medical columns are NOT present
    # -----------------------------------------------------

    medical_columns = [
        column
        for column in df.columns
        if column.startswith("Med_")
    ]

    print(
        "\nMedical columns present:",
        len(medical_columns)
    )

    if medical_columns:

        print(
            "Unexpected medical columns:"
        )

        for column in medical_columns:
            print(f"- {column}")

        raise ValueError(
            "Medical component columns should have been removed."
        )

    print(
        "Medical component exclusion: PASSED"
    )

    print(
        "\nRequired columns: PASSED"
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
# NUMERIC CONVERSION
# =========================================================

def convert_numeric_columns(df):

    print("\n" + "=" * 60)
    print("NUMERIC COLUMN VALIDATION")
    print("=" * 60)

    identifier_columns = [
        "Rndrng_NPI",
        "Year",
        "Rndrng_Prvdr_Last_Org_Name",
        "Rndrng_Prvdr_First_Name",
        "Rndrng_Prvdr_City",
        "Rndrng_Prvdr_State_Abrvtn",
        "Rndrng_Prvdr_Zip5",
        "Rndrng_Prvdr_RUCA_Desc",
        "Rndrng_Prvdr_Type",
        "provider_name",
        "performance_year",
    ]

    numeric_columns = [
        column
        for column in df.columns
        if column not in identifier_columns
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    print(
        f"Numeric columns processed: "
        f"{len(numeric_columns):,}"
    )

    return df


# =========================================================
# SAFE DIVISION
# =========================================================

def safe_divide(
    numerator,
    denominator
):

    denominator = denominator.replace(
        0,
        np.nan
    )

    return numerator / denominator


# =========================================================
# CREATE STAGE 1 FEATURES
# =========================================================

def create_stage1_features(df):

    print("\n" + "=" * 60)
    print("CREATING STAGE 1 PROVIDER FEATURES")
    print("=" * 60)

    original_columns = set(
        df.columns
    )

    # =====================================================
    # A. UTILIZATION FEATURES
    # =====================================================

    print("\nCreating utilization features...")

    df["services_per_beneficiary"] = safe_divide(
        df["Tot_Srvcs"],
        df["Tot_Benes"]
    )

    df["hcpcs_codes_per_beneficiary"] = safe_divide(
        df["Tot_HCPCS_Cds"],
        df["Tot_Benes"]
    )

    df["services_per_hcpcs"] = safe_divide(
        df["Tot_Srvcs"],
        df["Tot_HCPCS_Cds"]
    )

    # =====================================================
    # B. CHARGE FEATURES
    # =====================================================

    print("Creating charge features...")

    df["submitted_charge_per_service"] = safe_divide(
        df["Tot_Sbmtd_Chrg"],
        df["Tot_Srvcs"]
    )

    df["submitted_charge_per_beneficiary"] = safe_divide(
        df["Tot_Sbmtd_Chrg"],
        df["Tot_Benes"]
    )

    # =====================================================
    # C. MEDICARE ALLOWED AMOUNT
    # =====================================================

    print("Creating allowed amount features...")

    df["allowed_amount_per_service"] = safe_divide(
        df["Tot_Mdcr_Alowd_Amt"],
        df["Tot_Srvcs"]
    )

    df["allowed_amount_per_beneficiary"] = safe_divide(
        df["Tot_Mdcr_Alowd_Amt"],
        df["Tot_Benes"]
    )

    # =====================================================
    # D. MEDICARE PAYMENT
    # =====================================================

    print("Creating Medicare payment features...")

    df["payment_per_service"] = safe_divide(
        df["Tot_Mdcr_Pymt_Amt"],
        df["Tot_Srvcs"]
    )

    df["payment_per_beneficiary"] = safe_divide(
        df["Tot_Mdcr_Pymt_Amt"],
        df["Tot_Benes"]
    )

    # =====================================================
    # E. STANDARDIZED PAYMENT
    # =====================================================

    print("Creating standardized payment features...")

    df["standardized_amount_per_service"] = safe_divide(
        df["Tot_Mdcr_Stdzd_Amt"],
        df["Tot_Srvcs"]
    )

    df["standardized_amount_per_beneficiary"] = safe_divide(
        df["Tot_Mdcr_Stdzd_Amt"],
        df["Tot_Benes"]
    )

    # =====================================================
    # F. PAYMENT / ALLOWED RATIO
    # =====================================================

    print("Creating payment ratios...")

    df["payment_to_allowed_ratio"] = safe_divide(
        df["Tot_Mdcr_Pymt_Amt"],
        df["Tot_Mdcr_Alowd_Amt"]
    )

    # =====================================================
    # G. DRUG UTILIZATION
    # =====================================================

    print("Creating drug utilization features...")

    df["drug_service_share"] = safe_divide(
        df["Drug_Tot_Srvcs"],
        df["Tot_Srvcs"]
    )

    df["drug_beneficiary_share"] = safe_divide(
        df["Drug_Tot_Benes"],
        df["Tot_Benes"]
    )

    df["drug_hcpcs_share"] = safe_divide(
        df["Drug_Tot_HCPCS_Cds"],
        df["Tot_HCPCS_Cds"]
    )

    df["drug_services_per_beneficiary"] = safe_divide(
        df["Drug_Tot_Srvcs"],
        df["Drug_Tot_Benes"]
    )

    # =====================================================
    # H. DRUG COST
    # =====================================================

    print("Creating drug cost features...")

    df["drug_payment_per_service"] = safe_divide(
        df["Drug_Mdcr_Pymt_Amt"],
        df["Drug_Tot_Srvcs"]
    )

    df["drug_payment_per_beneficiary"] = safe_divide(
        df["Drug_Mdcr_Pymt_Amt"],
        df["Drug_Tot_Benes"]
    )

    df["drug_allowed_per_service"] = safe_divide(
        df["Drug_Mdcr_Alowd_Amt"],
        df["Drug_Tot_Srvcs"]
    )

    # =====================================================
    # I. BENEFICIARY MIX
    # =====================================================

    print("Creating beneficiary mix features...")

    df["female_share"] = safe_divide(
        df["Bene_Feml_Cnt"],
        df["Tot_Benes"]
    )

    df["male_share"] = safe_divide(
        df["Bene_Male_Cnt"],
        df["Tot_Benes"]
    )

    df["dual_share"] = safe_divide(
        df["Bene_Dual_Cnt"],
        df["Tot_Benes"]
    )

    df["nondual_share"] = safe_divide(
        df["Bene_Ndual_Cnt"],
        df["Tot_Benes"]
    )

    # =====================================================
    # J. BENEFICIARY DEMOGRAPHICS
    # =====================================================

    print("Creating beneficiary demographic features...")

    df["average_beneficiary_age"] = (
        df["Bene_Avg_Age"]
    )

    df["beneficiary_risk_score"] = (
        df["Bene_Avg_Risk_Scre"]
    )

    # =====================================================
    # FEATURE SUMMARY
    # =====================================================

    new_columns = [
        column
        for column in df.columns
        if column not in original_columns
    ]

    print("\n" + "=" * 60)
    print("STAGE 1 FEATURE SUMMARY")
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
# FEATURE VALIDATION
# =========================================================

def validate_features(df):

    print("\n" + "=" * 60)
    print("FEATURE VALIDATION")
    print("=" * 60)

    feature_columns = [

        "services_per_beneficiary",
        "hcpcs_codes_per_beneficiary",
        "services_per_hcpcs",

        "submitted_charge_per_service",
        "submitted_charge_per_beneficiary",

        "allowed_amount_per_service",
        "allowed_amount_per_beneficiary",

        "payment_per_service",
        "payment_per_beneficiary",

        "standardized_amount_per_service",
        "standardized_amount_per_beneficiary",

        "payment_to_allowed_ratio",

        "drug_service_share",
        "drug_beneficiary_share",
        "drug_hcpcs_share",
        "drug_services_per_beneficiary",

        "drug_payment_per_service",
        "drug_payment_per_beneficiary",
        "drug_allowed_per_service",

        "female_share",
        "male_share",
        "dual_share",
        "nondual_share",

        "average_beneficiary_age",
        "beneficiary_risk_score",
    ]

    missing_features = [
        column
        for column in feature_columns
        if column not in df.columns
    ]

    if missing_features:

        raise ValueError(
            f"Missing engineered features: "
            f"{missing_features}"
        )

    print(
        "All expected features exist: PASSED"
    )

    print(
        "\nNull counts in engineered features:"
    )

    null_summary = (
        df[feature_columns]
        .isna()
        .sum()
    )

    for column, count in null_summary.items():

        if count > 0:

            print(
                f"- {column}: {count:,}"
            )

    # -----------------------------------------------------
    # Infinite values
    # -----------------------------------------------------

    infinite_count = 0

    for column in feature_columns:

        infinite_count += int(
            np.isinf(
                df[column].fillna(0)
            ).sum()
        )

    print(
        "\nInfinite values:",
        infinite_count
    )

    if infinite_count != 0:

        raise ValueError(
            "Infinite values detected."
        )

    print(
        "Infinite value validation: PASSED"
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
        "\nMedical columns in Stage 1:",
        medical_columns
    )

    if medical_columns:

        raise ValueError(
            "Medical columns unexpectedly present in Stage 1 output."
        )

    print(
        "Medical column exclusion: PASSED"
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
    print("FEATURE DATASET SAVED")
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

    df = load_clean_data()

    validate_input(
        df
    )

    df = convert_numeric_columns(
        df
    )

    df = create_stage1_features(
        df
    )

    validate_features(
        df
    )

    save_features(
        df
    )

    print("\n" + "=" * 60)
    print("STAGE 1 FEATURE ENGINEERING COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()