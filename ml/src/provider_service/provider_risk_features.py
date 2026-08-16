from pathlib import Path

import numpy as np
import pandas as pd


# =========================================================
# CONFIGURATION
# =========================================================

INPUT_PATH = Path(
    "data/processed/provider_service/provider_features_stage1.csv"
)

OUTPUT_PATH = Path(
    "data/processed/provider_service/provider_features_stage2.csv"
)


# =========================================================
# LOAD STAGE 1 DATA
# =========================================================

def load_stage1_data():

    print("=" * 60)
    print("PROVIDER FEATURE ENGINEERING - STAGE 2")
    print("BENEFICIARY + CLINICAL RISK FEATURES")
    print("=" * 60)

    print("\nLoading Stage 1 dataset...")

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
    print("STAGE 2 INPUT VALIDATION")
    print("=" * 60)

    required_columns = [
        "Rndrng_NPI",
        "Year",
        "Bene_Avg_Risk_Scre"
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing required columns: {missing}"
        )

    print(
        "Required columns: PASSED"
    )

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


# =========================================================
# IDENTIFY CONDITION COLUMNS
# =========================================================

def identify_condition_columns(df):

    behavioral_columns = [
        column
        for column in df.columns
        if column.startswith("Bene_CC_BH_")
    ]

    physical_columns = [
        column
        for column in df.columns
        if column.startswith("Bene_CC_PH_")
    ]

    print("\n" + "=" * 60)
    print("CONDITION COLUMN IDENTIFICATION")
    print("=" * 60)

    print(
        "Behavioral-health columns:",
        len(behavioral_columns)
    )

    for column in behavioral_columns:
        print(f"- {column}")

    print(
        "\nPhysical-health columns:",
        len(physical_columns)
    )

    for column in physical_columns:
        print(f"- {column}")

    if not behavioral_columns:
        raise ValueError(
            "No behavioral-health condition columns found."
        )

    if not physical_columns:
        raise ValueError(
            "No physical-health condition columns found."
        )

    return behavioral_columns, physical_columns


# =========================================================
# NUMERIC CONVERSION
# =========================================================

def convert_condition_columns(
    df,
    behavioral_columns,
    physical_columns
):

    print("\n" + "=" * 60)
    print("CONVERTING CONDITION FEATURES")
    print("=" * 60)

    condition_columns = (
        behavioral_columns
        + physical_columns
        + ["Bene_Avg_Risk_Scre"]
    )

    for column in condition_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    print(
        "Condition columns converted:",
        len(condition_columns)
    )

    return df


# =========================================================
# CREATE RISK FEATURES
# =========================================================

def create_risk_features(
    df,
    behavioral_columns,
    physical_columns
):

    print("\n" + "=" * 60)
    print("CREATING RISK FEATURES")
    print("=" * 60)

    original_columns = set(
        df.columns
    )

    # -----------------------------------------------------
    # Behavioral health burden
    # -----------------------------------------------------

    print(
        "Creating behavioral-health burden..."
    )

    df["behavioral_health_burden"] = (
        df[behavioral_columns]
        .mean(
            axis=1,
            skipna=True
        )
    )

    # -----------------------------------------------------
    # Physical health burden
    # -----------------------------------------------------

    print(
        "Creating physical-health burden..."
    )

    df["physical_health_burden"] = (
        df[physical_columns]
        .mean(
            axis=1,
            skipna=True
        )
    )

    # -----------------------------------------------------
    # Overall condition burden
    # -----------------------------------------------------

    print(
        "Creating overall condition burden..."
    )

    all_condition_columns = (
        behavioral_columns
        + physical_columns
    )

    df["overall_condition_burden"] = (
        df[all_condition_columns]
        .mean(
            axis=1,
            skipna=True
        )
    )

    # -----------------------------------------------------
    # Condition counts
    # -----------------------------------------------------

    print(
        "Creating condition counts..."
    )

    df["behavioral_health_condition_count"] = (
        df[behavioral_columns]
        .notna()
        .sum(axis=1)
    )

    df["physical_health_condition_count"] = (
        df[physical_columns]
        .notna()
        .sum(axis=1)
    )

    # -----------------------------------------------------
    # High condition burden count
    # -----------------------------------------------------
    #
    # Threshold is 50%.
    #
    # This is an analytical flag, not a clinical diagnosis.
    # -----------------------------------------------------

    print(
        "Creating high-condition-burden count..."
    )

    high_burden_threshold = 50

    df["high_condition_burden_count"] = (
        df[all_condition_columns]
        .ge(high_burden_threshold)
        .sum(axis=1)
    )

    # -----------------------------------------------------
    # Preserve existing risk score
    # -----------------------------------------------------

    df["average_risk_score"] = (
        df["Bene_Avg_Risk_Scre"]
    )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    new_columns = [
        column
        for column in df.columns
        if column not in original_columns
    ]

    print("\n" + "=" * 60)
    print("STAGE 2 FEATURE SUMMARY")
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
# VALIDATE FEATURES
# =========================================================

def validate_features(df):

    print("\n" + "=" * 60)
    print("STAGE 2 FEATURE VALIDATION")
    print("=" * 60)

    expected_features = [
        "behavioral_health_burden",
        "physical_health_burden",
        "overall_condition_burden",
        "behavioral_health_condition_count",
        "physical_health_condition_count",
        "high_condition_burden_count",
        "average_risk_score"
    ]

    missing = [
        column
        for column in expected_features
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing Stage 2 features: {missing}"
        )

    print(
        "All expected Stage 2 features exist: PASSED"
    )

    # -----------------------------------------------------
    # Infinite values
    # -----------------------------------------------------

    infinite_count = 0

    for column in expected_features:

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
    # Risk feature summary
    # -----------------------------------------------------

    print("\nRisk feature summary:")

    print(
        df[
            expected_features
        ].describe()
        .round(3)
        .to_string()
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
    print("STAGE 2 DATASET SAVED")
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

    df = load_stage1_data()

    validate_input(
        df
    )

    (
        behavioral_columns,
        physical_columns
    ) = identify_condition_columns(
        df
    )

    df = convert_condition_columns(
        df,
        behavioral_columns,
        physical_columns
    )

    df = create_risk_features(
        df,
        behavioral_columns,
        physical_columns
    )

    validate_features(
        df
    )

    save_features(
        df
    )

    print("\n" + "=" * 60)
    print("STAGE 2 COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()