from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_PATH = Path(
    "data/processed/provider_service/provider_features_stage4.csv"
)

OUTPUT_PATH = Path(
    "data/processed/provider_service/provider_performance_segments.csv"
)


# ============================================================
# CONFIGURATION: SEGMENTATION FEATURES
# ============================================================

SEGMENT_FEATURES = [
    "service_intensity_per_beneficiary",
    "risk_adjusted_services",
    "risk_adjusted_payment",
    "condition_adjusted_services",
    "condition_adjusted_payment",
    "payment_per_beneficiary",
    "payment_per_service",
]


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("=" * 70)
    print("PROVIDER PERFORMANCE SEGMENTATION")
    print("=" * 70)

    print("\nLoading Stage 4 dataset...")

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Stage 4 dataset not found:\n{INPUT_PATH}"
        )

    df = pd.read_csv(
        INPUT_PATH,
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
    print("SEGMENTATION INPUT VALIDATION")
    print("=" * 70)

    required_columns = [
        "Rndrng_NPI",
        "Year",
        *SEGMENT_FEATURES
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        print("\nMissing required columns:")

        for column in missing:
            print(f"- {column}")

        raise ValueError(
            "Segmentation input validation failed."
        )

    print("Required columns: PASSED")

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
            "NPI + Year grain failed."
        )

    print("NPI + Year grain: PASSED")


# ============================================================
# PREPARE SEGMENTATION FEATURES
# ============================================================

def prepare_features(df):

    print("\n" + "=" * 70)
    print("PREPARING SEGMENTATION FEATURES")
    print("=" * 70)

    work = df[
        [
            "Rndrng_NPI",
            "Year",
            *SEGMENT_FEATURES
        ]
    ].copy()

    for feature in SEGMENT_FEATURES:

        work[feature] = pd.to_numeric(
            work[feature],
            errors="coerce"
        )

    print("\nFeature availability:")

    for feature in SEGMENT_FEATURES:

        valid_count = work[feature].notna().sum()

        print(
            f"{feature}: "
            f"{valid_count:,} valid / "
            f"{len(work):,} total"
        )

    return work


# ============================================================
# WINSOR-FREE ROBUST PERCENTILE SCORING
# ============================================================

def create_percentile_scores(work):

    print("\n" + "=" * 70)
    print("CREATING ROBUST PERCENTILE SCORES")
    print("=" * 70)

    result = work.copy()

    for feature in SEGMENT_FEATURES:

        score_column = f"{feature}_percentile"

        result[score_column] = (
            result[feature]
            .rank(
                pct=True,
                method="average"
            )
        )

    return result


# ============================================================
# CREATE COMPOSITE PERFORMANCE DIMENSIONS
# ============================================================

def create_performance_dimensions(df):

    print("\n" + "=" * 70)
    print("CREATING PERFORMANCE DIMENSIONS")
    print("=" * 70)

    result = df.copy()

    # --------------------------------------------------------
    # UTILIZATION DIMENSION
    # --------------------------------------------------------

    utilization_features = [
        "service_intensity_per_beneficiary_percentile",
        "risk_adjusted_services_percentile",
        "condition_adjusted_services_percentile",
    ]

    result["utilization_score"] = (
        result[utilization_features]
        .mean(axis=1)
    )

    # --------------------------------------------------------
    # COST DIMENSION
    # --------------------------------------------------------

    cost_features = [
        "risk_adjusted_payment_percentile",
        "condition_adjusted_payment_percentile",
        "payment_per_beneficiary_percentile",
        "payment_per_service_percentile",
    ]

    result["cost_score"] = (
        result[cost_features]
        .mean(axis=1)
    )

    return result


# ============================================================
# ASSIGN PROVIDER SEGMENTS
# ============================================================

def assign_segments(df):

    print("\n" + "=" * 70)
    print("ASSIGNING PROVIDER PERFORMANCE SEGMENTS")
    print("=" * 70)

    result = df.copy()

    utilization = result["utilization_score"]
    cost = result["cost_score"]

    result["provider_segment"] = "INSUFFICIENT_DATA"

    valid_mask = (
        utilization.notna()
        &
        cost.notna()
    )

    # --------------------------------------------------------
    # HIGH UTILIZATION + HIGH COST
    # --------------------------------------------------------

    result.loc[
        valid_mask
        &
        (utilization >= 0.75)
        &
        (cost >= 0.75),
        "provider_segment"
    ] = "HIGH_COST_HIGH_UTILIZATION"

    # --------------------------------------------------------
    # HIGH UTILIZATION
    # --------------------------------------------------------

    result.loc[
        valid_mask
        &
        (utilization >= 0.75)
        &
        (cost < 0.75),
        "provider_segment"
    ] = "HIGH_UTILIZATION"

    # --------------------------------------------------------
    # HIGH COST
    # --------------------------------------------------------

    result.loc[
        valid_mask
        &
        (utilization < 0.75)
        &
        (cost >= 0.75),
        "provider_segment"
    ] = "HIGH_COST"

    # --------------------------------------------------------
    # LOW UTILIZATION + LOW COST
    # --------------------------------------------------------

    result.loc[
        valid_mask
        &
        (utilization < 0.25)
        &
        (cost < 0.25),
        "provider_segment"
    ] = "LOW_COST_LOW_UTILIZATION"

    # --------------------------------------------------------
    # BALANCED / MODERATE
    # --------------------------------------------------------

    result.loc[
        valid_mask
        &
        (result["provider_segment"] == "INSUFFICIENT_DATA"),
        "provider_segment"
    ] = "MODERATE_BALANCED"

    print("\nSegment distribution:")

    print(
        result[
            "provider_segment"
        ]
        .value_counts(dropna=False)
        .to_string()
    )

    return result


# ============================================================
# CREATE INTERPRETATION FLAGS
# ============================================================

def create_flags(df):

    print("\n" + "=" * 70)
    print("CREATING PROVIDER PERFORMANCE FLAGS")
    print("=" * 70)

    result = df.copy()

    result["high_utilization_flag"] = (
        result["utilization_score"] >= 0.75
    )

    result["high_cost_flag"] = (
        result["cost_score"] >= 0.75
    )

    result["low_utilization_flag"] = (
        result["utilization_score"] < 0.25
    )

    result["low_cost_flag"] = (
        result["cost_score"] < 0.25
    )

    return result


# ============================================================
# VALIDATE OUTPUT
# ============================================================

def validate_output(df):

    print("\n" + "=" * 70)
    print("SEGMENTATION OUTPUT VALIDATION")
    print("=" * 70)

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
            "Segmentation changed the analytical grain."
        )

    print("NPI + Year grain: PASSED")

    print(
        f"\nRows: {len(df):,}"
    )

    print(
        f"Columns: {len(df.columns):,}"
    )

    print("\nFinal segment distribution:")

    print(
        df["provider_segment"]
        .value_counts(dropna=False)
        .to_string()
    )


# ============================================================
# SAVE
# ============================================================

def save_output(df):

    print("\n" + "=" * 70)
    print("SAVING PROVIDER SEGMENTATION DATASET")
    print("=" * 70)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        f"Output saved to:\n{OUTPUT_PATH}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    df = load_data()

    validate_input(
        df
    )

    work = prepare_features(
        df
    )

    work = create_percentile_scores(
        work
    )

    work = create_performance_dimensions(
        work
    )

    work = assign_segments(
        work
    )

    work = create_flags(
        work
    )

    validate_output(
        work
    )

    save_output(
        work
    )

    print("\n" + "=" * 70)
    print("PROVIDER SEGMENTATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()