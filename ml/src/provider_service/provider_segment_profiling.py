from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_PATH = Path(
    "data/processed/provider_service/provider_performance_segments.csv"
)

OUTPUT_PATH = Path(
    "data/processed/provider_service/provider_segment_profile.csv"
)


# ============================================================
# FEATURES TO PROFILE
# ============================================================

PROFILE_FEATURES = [
    "service_intensity_per_beneficiary",
    "risk_adjusted_services",
    "risk_adjusted_payment",
    "condition_adjusted_services",
    "condition_adjusted_payment",
    "payment_per_beneficiary",
    "payment_per_service",
    "utilization_score",
    "cost_score",
]


# ============================================================
# LOAD
# ============================================================

def load_data():

    print("=" * 70)
    print("PROVIDER SEGMENT PROFILING")
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
# CREATE PROFILE
# ============================================================

def create_profile(df):

    print("\n" + "=" * 70)
    print("CREATING SEGMENT PROFILE")
    print("=" * 70)

    available_features = [
        feature
        for feature in PROFILE_FEATURES
        if feature in df.columns
    ]

    profile = (
        df.groupby("provider_segment")[
            available_features
        ]
        .agg([
            "count",
            "mean",
            "median",
            "min",
            "max"
        ])
    )

    return profile


# ============================================================
# CREATE SEGMENT COUNTS
# ============================================================

def create_counts(df):

    counts = (
        df["provider_segment"]
        .value_counts()
        .rename("provider_year_count")
        .to_frame()
    )

    counts["percentage"] = (
        counts["provider_year_count"]
        / len(df)
        * 100
    )

    return counts


# ============================================================
# PRINT PROFILE
# ============================================================

def print_profile(profile):

    print("\n" + "=" * 70)
    print("SEGMENT PROFILE")
    print("=" * 70)

    pd.set_option(
        "display.max_columns",
        None
    )

    pd.set_option(
        "display.width",
        200
    )

    print(profile.round(3).to_string())


# ============================================================
# SAVE
# ============================================================

def save_profile(profile):

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    profile.to_csv(
        OUTPUT_PATH
    )

    print(
        f"\nProfile saved to:\n{OUTPUT_PATH}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    df = load_data()

    counts = create_counts(
        df
    )

    print("\n" + "=" * 70)
    print("SEGMENT COUNTS")
    print("=" * 70)

    print(
        counts.round(2).to_string()
    )

    profile = create_profile(
        df
    )

    print_profile(
        profile
    )

    save_profile(
        profile
    )

    print("\n" + "=" * 70)
    print("SEGMENT PROFILING COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()