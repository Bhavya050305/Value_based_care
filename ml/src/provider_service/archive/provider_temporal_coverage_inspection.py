from pathlib import Path

import pandas as pd


# =========================================================
# CONFIGURATION
# =========================================================

INPUT_PATH = Path(
    "data/processed/provider_service/provider_features_stage3.csv"
)


# =========================================================
# LOAD DATA
# =========================================================

def load_data():

    print("=" * 60)
    print("PROVIDER TEMPORAL COVERAGE INSPECTION")
    print("=" * 60)

    print("\nLoading Stage 3 dataset...")

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found:\n{INPUT_PATH}"
        )

    df = pd.read_csv(
        INPUT_PATH,
        usecols=[
            "Rndrng_NPI",
            "Year"
        ],
        low_memory=False
    )

    print(
        f"Rows loaded: {len(df):,}"
    )

    print(
        f"Unique providers: "
        f"{df['Rndrng_NPI'].nunique():,}"
    )

    print(
        f"Years detected: "
        f"{sorted(df['Year'].dropna().unique())}"
    )

    return df


# =========================================================
# BASIC VALIDATION
# =========================================================

def validate_data(df):

    print("\n" + "=" * 60)
    print("BASIC VALIDATION")
    print("=" * 60)

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

    if invalid_npi != 0:
        raise ValueError(
            "Invalid NPI values detected."
        )

    if invalid_year != 0:
        raise ValueError(
            "Invalid Year values detected."
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
            "Duplicate NPI-Year rows detected."
        )

    print(
        "NPI + Year grain: PASSED"
    )


# =========================================================
# PROVIDER COUNT BY YEAR
# =========================================================

def inspect_year_coverage(df):

    print("\n" + "=" * 60)
    print("PROVIDER COVERAGE BY YEAR")
    print("=" * 60)

    yearly = (
        df.groupby("Year")["Rndrng_NPI"]
        .nunique()
        .sort_index()
    )

    print("\nUnique providers by year:")

    for year, count in yearly.items():

        print(
            f"{int(year)}: {count:,} providers"
        )

    return yearly


# =========================================================
# PROVIDER HISTORY LENGTH
# =========================================================

def inspect_history_length(df):

    print("\n" + "=" * 60)
    print("PROVIDER HISTORY LENGTH")
    print("=" * 60)

    history = (
        df.groupby("Rndrng_NPI")["Year"]
        .nunique()
    )

    distribution = (
        history
        .value_counts()
        .sort_index()
    )

    print(
        "\nNumber of providers by number of observed years:"
    )

    for years, count in distribution.items():

        print(
            f"{int(years)} year(s): "
            f"{count:,} providers"
        )

    print("\nSummary:")

    print(
        f"1 year : "
        f"{(history == 1).sum():,}"
    )

    print(
        f"2 years: "
        f"{(history == 2).sum():,}"
    )

    print(
        f"3 years: "
        f"{(history == 3).sum():,}"
    )

    print(
        f"4 years: "
        f"{(history == 4).sum():,}"
    )

    print(
        f"5 years: "
        f"{(history == 5).sum():,}"
    )

    return history


# =========================================================
# YEAR COMBINATION PATTERNS
# =========================================================

def inspect_year_combinations(df):

    print("\n" + "=" * 60)
    print("PROVIDER YEAR COMBINATION PATTERNS")
    print("=" * 60)

    provider_years = (
        df.groupby("Rndrng_NPI")["Year"]
        .apply(
            lambda x: tuple(
                sorted(
                    x.astype(int)
                    .unique()
                )
            )
        )
    )

    combination_counts = (
        provider_years
        .value_counts()
    )

    print(
        "\nMost common provider year combinations:"
    )

    for combination, count in combination_counts.head(30).items():

        year_text = "-".join(
            str(year)
            for year in combination
        )

        print(
            f"{year_text}: "
            f"{count:,} providers"
        )

    return provider_years


# =========================================================
# CONSECUTIVE YEAR COVERAGE
# =========================================================

def inspect_consecutive_coverage(df):

    print("\n" + "=" * 60)
    print("CONSECUTIVE YEAR COVERAGE")
    print("=" * 60)

    provider_years = (
        df.groupby("Rndrng_NPI")["Year"]
        .apply(
            lambda x: sorted(
                x.astype(int).unique()
            )
        )
    )

    consecutive_counts = {}

    for npi, years in provider_years.items():

        consecutive_pairs = 0

        for i in range(
            1,
            len(years)
        ):

            if years[i] == years[i - 1] + 1:

                consecutive_pairs += 1

        consecutive_counts[npi] = consecutive_pairs

    consecutive_series = pd.Series(
        consecutive_counts
    )

    print(
        "\nProviders by number of consecutive "
        "year-to-year relationships:"
    )

    distribution = (
        consecutive_series
        .value_counts()
        .sort_index()
    )

    for pairs, count in distribution.items():

        print(
            f"{int(pairs)} consecutive pair(s): "
            f"{count:,} providers"
        )

    print("\nSpecific consecutive coverage:")

    print(
        "Providers with at least "
        f"1 consecutive pair: "
        f"{(consecutive_series >= 1).sum():,}"
    )

    print(
        "Providers with at least "
        f"2 consecutive pairs: "
        f"{(consecutive_series >= 2).sum():,}"
    )

    print(
        "Providers with at least "
        f"3 consecutive pairs: "
        f"{(consecutive_series >= 3).sum():,}"
    )

    print(
        "Providers with 4 consecutive pairs "
        "(complete 2020-2024 sequence): "
        f"{(consecutive_series >= 4).sum():,}"
    )


# =========================================================
# YEAR-TO-YEAR PROVIDER OVERLAP
# =========================================================

def inspect_year_overlap(df):

    print("\n" + "=" * 60)
    print("YEAR-TO-YEAR PROVIDER OVERLAP")
    print("=" * 60)

    years = sorted(
        df["Year"]
        .astype(int)
        .unique()
    )

    provider_sets = {
        year: set(
            df.loc[
                df["Year"] == year,
                "Rndrng_NPI"
            ]
        )
        for year in years
    }

    for i in range(
        1,
        len(years)
    ):

        previous_year = years[i - 1]
        current_year = years[i]

        previous_providers = provider_sets[
            previous_year
        ]

        current_providers = provider_sets[
            current_year
        ]

        overlap = (
            previous_providers
            &
            current_providers
        )

        print(
            f"\n{previous_year} -> {current_year}"
        )

        print(
            f"  {previous_year} providers: "
            f"{len(previous_providers):,}"
        )

        print(
            f"  {current_year} providers: "
            f"{len(current_providers):,}"
        )

        print(
            f"  Providers present in both: "
            f"{len(overlap):,}"
        )

        if len(previous_providers) > 0:

            retention = (
                len(overlap)
                /
                len(previous_providers)
            ) * 100

            print(
                f"  Retention from {previous_year}: "
                f"{retention:.2f}%"
            )


# =========================================================
# COMPLETE 2020-2024 COVERAGE
# =========================================================

def inspect_complete_five_year_coverage(df):

    print("\n" + "=" * 60)
    print("COMPLETE 2020-2024 COVERAGE")
    print("=" * 60)

    required_years = {
        2020,
        2021,
        2022,
        2023,
        2024
    }

    provider_year_sets = (
        df.groupby("Rndrng_NPI")["Year"]
        .apply(
            lambda x: set(
                x.astype(int)
            )
        )
    )

    complete_providers = provider_year_sets[
        provider_year_sets.apply(
            lambda years:
            required_years.issubset(years)
        )
    ]

    print(
        "Providers with all five years "
        "(2020-2024):",
        f"{len(complete_providers):,}"
    )

    if len(complete_providers) == 0:

        print(
            "\nIMPORTANT:"
        )

        print(
            "No provider has observations in "
            "all five years 2020-2024."
        )

    else:

        print(
            "Complete 5-year provider coverage exists."
        )


# =========================================================
# FINAL SUMMARY
# =========================================================

def final_summary(df):

    print("\n" + "=" * 60)
    print("FINAL TEMPORAL COVERAGE SUMMARY")
    print("=" * 60)

    provider_years = (
        df.groupby("Rndrng_NPI")["Year"]
        .nunique()
    )

    print(
        f"Total rows: "
        f"{len(df):,}"
    )

    print(
        f"Unique providers: "
        f"{df['Rndrng_NPI'].nunique():,}"
    )

    print(
        f"Unique years: "
        f"{df['Year'].nunique():,}"
    )

    print(
        f"Providers with exactly 1 year: "
        f"{(provider_years == 1).sum():,}"
    )

    print(
        f"Providers with exactly 2 years: "
        f"{(provider_years == 2).sum():,}"
    )

    print(
        f"Providers with exactly 3 years: "
        f"{(provider_years == 3).sum():,}"
    )

    print(
        f"Providers with exactly 4 years: "
        f"{(provider_years == 4).sum():,}"
    )

    print(
        f"Providers with exactly 5 years: "
        f"{(provider_years == 5).sum():,}"
    )

    print("\nNo data was modified.")
    print("No rows were removed.")
    print("No features were created.")
    print("This script only inspects temporal coverage.")

    print("\n" + "=" * 60)
    print("TEMPORAL COVERAGE INSPECTION COMPLETED")
    print("=" * 60)


# =========================================================
# MAIN
# =========================================================

def main():

    df = load_data()

    validate_data(
        df
    )

    inspect_year_coverage(
        df
    )

    inspect_history_length(
        df
    )

    inspect_year_combinations(
        df
    )

    inspect_consecutive_coverage(
        df
    )

    inspect_year_overlap(
        df
    )

    inspect_complete_five_year_coverage(
        df
    )

    final_summary(
        df
    )


if __name__ == "__main__":
    main()