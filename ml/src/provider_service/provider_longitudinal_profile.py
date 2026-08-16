from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_PATH = Path(
    "data/processed/provider_service/provider_performance_segments.csv"
)

OUTPUT_PATH = Path(
    "data/processed/provider_service/provider_longitudinal_profile.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("=" * 70)
    print("PROVIDER LONGITUDINAL PROFILE")
    print("=" * 70)

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


# ============================================================
# CREATE PROVIDER-LEVEL PROFILE
# ============================================================

def create_provider_profile(df):

    print("\n" + "=" * 70)
    print("CREATING PROVIDER-LEVEL PROFILE")
    print("=" * 70)

    numeric_features = [
        "utilization_score",
        "cost_score",
        "service_intensity_per_beneficiary",
        "risk_adjusted_services",
        "risk_adjusted_payment",
        "condition_adjusted_services",
        "condition_adjusted_payment",
        "payment_per_beneficiary",
        "payment_per_service",
    ]

    available_features = [
        column
        for column in numeric_features
        if column in df.columns
    ]

    grouped = df.groupby(
        "Rndrng_NPI"
    )

    provider_profile = grouped[
        available_features
    ].agg(
        [
            "count",
            "mean",
            "median",
            "std"
        ]
    )

    provider_profile.columns = [
        f"{feature}_{stat}"
        for feature, stat in provider_profile.columns
    ]

    provider_profile = (
        provider_profile
        .reset_index()
    )

    return provider_profile


# ============================================================
# ADD YEAR INFORMATION
# ============================================================

def add_year_information(df, profile):

    year_information = (
        df.groupby(
            "Rndrng_NPI"
        )["Year"]
        .agg(
            years_observed="nunique",
            first_year="min",
            last_year="max"
        )
        .reset_index()
    )

    profile = profile.merge(
        year_information,
        on="Rndrng_NPI",
        how="left"
    )

    return profile


# ============================================================
# ADD DOMINANT PROVIDER SEGMENT
# ============================================================

def add_dominant_segment(df, profile):

    segment_counts = (
        df.groupby(
            [
                "Rndrng_NPI",
                "provider_segment"
            ]
        )
        .size()
        .reset_index(
            name="segment_year_count"
        )
    )

    segment_counts = segment_counts.sort_values(
        [
            "Rndrng_NPI",
            "segment_year_count"
        ],
        ascending=[
            True,
            False
        ]
    )

    dominant_segment = (
        segment_counts
        .drop_duplicates(
            subset=["Rndrng_NPI"]
        )
        [
            [
                "Rndrng_NPI",
                "provider_segment",
                "segment_year_count"
            ]
        ]
        .rename(
            columns={
                "provider_segment":
                    "dominant_provider_segment"
            }
        )
    )

    profile = profile.merge(
        dominant_segment,
        on="Rndrng_NPI",
        how="left"
    )

    return profile


# ============================================================
# CALCULATE SEGMENT STABILITY
# ============================================================

def add_segment_stability(df, profile):

    segment_counts = (
        df.groupby(
            [
                "Rndrng_NPI",
                "provider_segment"
            ]
        )
        .size()
        .reset_index(
            name="segment_count"
        )
    )

    total_counts = (
        df.groupby(
            "Rndrng_NPI"
        )
        .size()
        .rename(
            "total_years"
        )
        .reset_index()
    )

    segment_counts = segment_counts.merge(
        total_counts,
        on="Rndrng_NPI",
        how="left"
    )

    segment_counts["segment_share"] = (
        segment_counts["segment_count"]
        /
        segment_counts["total_years"]
    )

    stability = (
        segment_counts
        .groupby(
            "Rndrng_NPI"
        )["segment_share"]
        .max()
        .rename(
            "segment_stability"
        )
        .reset_index()
    )

    profile = profile.merge(
        stability,
        on="Rndrng_NPI",
        how="left"
    )

    return profile


# ============================================================
# CLASSIFY OVERALL PROVIDER SEGMENT
# ============================================================

def classify_provider(row):

    utilization = row[
        "utilization_score_mean"
    ]

    cost = row[
        "cost_score_mean"
    ]

    if pd.isna(utilization) or pd.isna(cost):
        return "INSUFFICIENT_DATA"

    if (
        utilization >= 0.75
        and
        cost >= 0.75
    ):
        return "HIGH_COST_HIGH_UTILIZATION"

    if utilization >= 0.75:
        return "HIGH_UTILIZATION"

    if cost >= 0.75:
        return "HIGH_COST"

    if (
        utilization < 0.25
        and
        cost < 0.25
    ):
        return "LOW_COST_LOW_UTILIZATION"

    return "MODERATE_BALANCED"


def add_overall_segment(profile):

    profile[
        "overall_provider_segment"
    ] = profile.apply(
        classify_provider,
        axis=1
    )

    return profile


# ============================================================
# CREATE OBSERVATION HISTORY CLASS
# ============================================================

def add_history_class(profile):

    print("\n" + "=" * 70)
    print("CREATING OBSERVATION HISTORY CLASS")
    print("=" * 70)

    def classify_history(years):

        if years == 1:
            return "SINGLE_YEAR"

        if years == 2:
            return "LIMITED_HISTORY"

        if years == 3:
            return "MODERATE_HISTORY"

        return "LONGITUDINAL_HISTORY"

    profile[
        "history_class"
    ] = profile[
        "years_observed"
    ].apply(
        classify_history
    )

    return profile


# ============================================================
# VALIDATION
# ============================================================

def validate(profile):

    print("\n" + "=" * 70)
    print("LONGITUDINAL PROFILE VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # UNIQUE PROVIDERS
    # --------------------------------------------------------

    unique_providers = (
        profile[
            "Rndrng_NPI"
        ].nunique()
    )

    print(
        f"Unique providers: "
        f"{unique_providers:,}"
    )

    # --------------------------------------------------------
    # OVERALL PROVIDER SEGMENTS
    # --------------------------------------------------------

    print(
        "\nOverall provider segment distribution:"
    )

    print(
        profile[
            "overall_provider_segment"
        ]
        .value_counts(
            dropna=False
        )
        .to_string()
    )

    # --------------------------------------------------------
    # YEARS OBSERVED
    # --------------------------------------------------------

    print(
        "\nYears observed distribution:"
    )

    print(
        profile[
            "years_observed"
        ]
        .value_counts()
        .sort_index()
        .to_string()
    )

    # --------------------------------------------------------
    # HISTORY CLASS
    # --------------------------------------------------------

    print(
        "\nHistory class distribution:"
    )

    print(
        profile[
            "history_class"
        ]
        .value_counts(
            dropna=False
        )
        .to_string()
    )

    # --------------------------------------------------------
    # SEGMENT STABILITY
    # --------------------------------------------------------

    print(
        "\nSegment stability summary:"
    )

    print(
        profile[
            "segment_stability"
        ]
        .describe()
        .round(3)
        .to_string()
    )

    # --------------------------------------------------------
    # DUPLICATE PROVIDERS
    # --------------------------------------------------------

    duplicate_npi_count = (
        profile[
            "Rndrng_NPI"
        ]
        .duplicated()
        .sum()
    )

    print(
        "\nDuplicate provider rows:"
        f" {duplicate_npi_count}"
    )

    if duplicate_npi_count == 0:

        print(
            "Provider-level grain: PASSED"
        )

    else:

        print(
            "Provider-level grain: FAILED"
        )


# ============================================================
# SAVE OUTPUT
# ============================================================

def save(profile):

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    profile.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        "\nOutput saved to:"
        f"\n{OUTPUT_PATH}"
    )

    print(
        f"Rows saved: {len(profile):,}"
    )

    print(
        f"Columns saved: {len(profile.columns):,}"
    )


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    # --------------------------------------------------------
    # 1. LOAD
    # --------------------------------------------------------

    df = load_data()

    # --------------------------------------------------------
    # 2. PROVIDER-LEVEL AGGREGATION
    # --------------------------------------------------------

    profile = create_provider_profile(
        df
    )

    # --------------------------------------------------------
    # 3. YEAR INFORMATION
    # --------------------------------------------------------

    profile = add_year_information(
        df,
        profile
    )

    # --------------------------------------------------------
    # 4. DOMINANT SEGMENT
    # --------------------------------------------------------

    profile = add_dominant_segment(
        df,
        profile
    )

    # --------------------------------------------------------
    # 5. SEGMENT STABILITY
    # --------------------------------------------------------

    profile = add_segment_stability(
        df,
        profile
    )

    # --------------------------------------------------------
    # 6. OVERALL PROVIDER SEGMENT
    # --------------------------------------------------------

    profile = add_overall_segment(
        profile
    )

    # --------------------------------------------------------
    # 7. HISTORY CLASS
    # --------------------------------------------------------

    profile = add_history_class(
        profile
    )

    # --------------------------------------------------------
    # 8. VALIDATE
    # --------------------------------------------------------

    validate(
        profile
    )

    # --------------------------------------------------------
    # 9. SAVE
    # --------------------------------------------------------

    save(
        profile
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "LONGITUDINAL PROVIDER PROFILE COMPLETED"
    )

    print(
        "=" * 70
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()