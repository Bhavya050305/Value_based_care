from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

BASE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_aco_features.csv"
)

PERFORMANCE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_performance_segments.csv"
)

LONGITUDINAL_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_longitudinal_profile.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_aco_features_final.csv"
)


# ============================================================
# HELPER
# ============================================================

def print_section(title):
    print("\n" + "-" * 90)
    print(title)
    print("-" * 90)


# ============================================================
# HEADER
# ============================================================

print("=" * 90)
print("BUILD FINAL PROVIDER + ACO FEATURE DATASET")
print("=" * 90)

print("\nProject root:")
print(PROJECT_ROOT)

print("\nBase dataset:")
print(BASE_FILE)

print("\nPerformance dataset:")
print(PERFORMANCE_FILE)

print("\nLongitudinal dataset:")
print(LONGITUDINAL_FILE)

print("\nOutput dataset:")
print(OUTPUT_FILE)


# ============================================================
# CHECK FILES
# ============================================================

print_section("CHECKING INPUT FILES")

for file_path in [
    BASE_FILE,
    PERFORMANCE_FILE,
    LONGITUDINAL_FILE,
]:
    if not file_path.exists():
        raise FileNotFoundError(
            f"\nRequired file not found:\n{file_path}"
        )

    print(f"✓ Found: {file_path.name}")


# ============================================================
# LOAD BASE DATA
# ============================================================

print_section("LOADING BASE PROVIDER + ACO DATASET")

base = pd.read_csv(
    BASE_FILE,
    low_memory=False
)

print(f"Rows loaded: {len(base):,}")
print(f"Columns loaded: {len(base.columns):,}")


# ============================================================
# LOAD PERFORMANCE DATA
# ============================================================

print_section("LOADING PROVIDER PERFORMANCE DATASET")

performance = pd.read_csv(
    PERFORMANCE_FILE,
    low_memory=False
)

print(f"Rows loaded: {len(performance):,}")
print(f"Columns loaded: {len(performance.columns):,}")


# ============================================================
# LOAD LONGITUDINAL DATA
# ============================================================

print_section("LOADING PROVIDER LONGITUDINAL DATASET")

longitudinal = pd.read_csv(
    LONGITUDINAL_FILE,
    low_memory=False
)

print(f"Rows loaded: {len(longitudinal):,}")
print(f"Columns loaded: {len(longitudinal.columns):,}")


# ============================================================
# REQUIRED KEY CHECK
# ============================================================

print_section("CHECKING REQUIRED KEY COLUMNS")

base_required = [
    "Rndrng_NPI",
    "Year",
    "ACO_ID",
]

performance_required = [
    "Rndrng_NPI",
    "Year",
    "utilization_score",
    "cost_score",
    "provider_segment",
]

longitudinal_required = [
    "Rndrng_NPI",
    "years_observed",
    "first_year",
    "last_year",
    "dominant_provider_segment",
    "segment_year_count",
    "segment_stability",
    "overall_provider_segment",
    "history_class",
]


def check_columns(df, required, name):

    missing = [
        col for col in required
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"\n{name} is missing required columns:\n"
            + "\n".join(missing)
        )

    print(f"✓ {name} contains all required columns.")


check_columns(
    base,
    base_required,
    "Base dataset"
)

check_columns(
    performance,
    performance_required,
    "Performance dataset"
)

check_columns(
    longitudinal,
    longitudinal_required,
    "Longitudinal dataset"
)


# ============================================================
# STANDARDIZE NPI
# ============================================================

print_section("STANDARDIZING NPI VALUES")


def standardize_npi(df):

    df["Rndrng_NPI"] = (
        pd.to_numeric(
            df["Rndrng_NPI"],
            errors="coerce"
        )
        .astype("Int64")
    )

    return df


base = standardize_npi(base)
performance = standardize_npi(performance)
longitudinal = standardize_npi(longitudinal)

print("✓ NPI values standardized.")


# ============================================================
# STANDARDIZE YEAR
# ============================================================

print_section("STANDARDIZING YEAR VALUES")

base["Year"] = pd.to_numeric(
    base["Year"],
    errors="coerce"
).astype("Int64")

performance["Year"] = pd.to_numeric(
    performance["Year"],
    errors="coerce"
).astype("Int64")

print("✓ Year values standardized.")


# ============================================================
# CHECK BASE GRAIN
# ============================================================

print_section("VALIDATING BASE DATASET GRAIN")

base_duplicates = base.duplicated(
    subset=["Rndrng_NPI", "Year"]
).sum()

print(
    f"Duplicate NPI-Year rows: {base_duplicates:,}"
)

if base_duplicates != 0:
    raise ValueError(
        "Base dataset does not have unique NPI-Year grain."
    )

print("✓ Base dataset has unique NPI-Year grain.")


# ============================================================
# CHECK PERFORMANCE GRAIN
# ============================================================

print_section("VALIDATING PERFORMANCE DATASET GRAIN")

performance_duplicates = performance.duplicated(
    subset=["Rndrng_NPI", "Year"]
).sum()

print(
    f"Duplicate NPI-Year rows: {performance_duplicates:,}"
)

if performance_duplicates != 0:
    raise ValueError(
        "Performance dataset contains duplicate NPI-Year rows."
    )

print("✓ Performance dataset has unique NPI-Year grain.")


# ============================================================
# CHECK LONGITUDINAL GRAIN
# ============================================================

print_section("VALIDATING LONGITUDINAL DATASET GRAIN")

longitudinal_duplicates = longitudinal.duplicated(
    subset=["Rndrng_NPI"]
).sum()

print(
    f"Duplicate NPI rows: {longitudinal_duplicates:,}"
)

if longitudinal_duplicates != 0:
    raise ValueError(
        "Longitudinal dataset contains duplicate NPIs."
    )

print("✓ Longitudinal dataset has one row per NPI.")


# ============================================================
# CHECK NPI COVERAGE
# ============================================================

print_section("CHECKING PERFORMANCE COVERAGE")

base_npis = set(
    base["Rndrng_NPI"].dropna().unique()
)

performance_npis = set(
    performance["Rndrng_NPI"].dropna().unique()
)

missing_performance_npis = (
    base_npis - performance_npis
)

extra_performance_npis = (
    performance_npis - base_npis
)

print(
    f"Base unique NPIs:              {len(base_npis):,}"
)

print(
    f"Performance unique NPIs:       {len(performance_npis):,}"
)

print(
    f"Base NPIs without performance: {len(missing_performance_npis):,}"
)

print(
    f"Extra performance NPIs:        {len(extra_performance_npis):,}"
)


# ============================================================
# CHECK PERFORMANCE NPI-YEAR COVERAGE
# ============================================================

base_keys = set(
    zip(
        base["Rndrng_NPI"],
        base["Year"]
    )
)

performance_keys = set(
    zip(
        performance["Rndrng_NPI"],
        performance["Year"]
    )
)

missing_performance_keys = (
    base_keys - performance_keys
)

print(
    f"\nBase NPI-Year combinations: "
    f"{len(base_keys):,}"
)

print(
    f"Performance NPI-Year combinations: "
    f"{len(performance_keys):,}"
)

print(
    f"Base NPI-Year without performance: "
    f"{len(missing_performance_keys):,}"
)


# ============================================================
# CHECK LONGITUDINAL COVERAGE
# ============================================================

print_section("CHECKING LONGITUDINAL COVERAGE")

longitudinal_npis = set(
    longitudinal["Rndrng_NPI"].dropna().unique()
)

missing_longitudinal_npis = (
    base_npis - longitudinal_npis
)

extra_longitudinal_npis = (
    longitudinal_npis - base_npis
)

print(
    f"Longitudinal unique NPIs:       "
    f"{len(longitudinal_npis):,}"
)

print(
    f"Base NPIs without longitudinal: "
    f"{len(missing_longitudinal_npis):,}"
)

print(
    f"Extra longitudinal NPIs:        "
    f"{len(extra_longitudinal_npis):,}"
)


# ============================================================
# SELECT PERFORMANCE COLUMNS
# ============================================================

print_section("SELECTING PERFORMANCE FEATURES")

performance_columns = [
    "Rndrng_NPI",
    "Year",

    "service_intensity_per_beneficiary_percentile",
    "risk_adjusted_services_percentile",
    "risk_adjusted_payment_percentile",
    "condition_adjusted_services_percentile",
    "condition_adjusted_payment_percentile",
    "payment_per_beneficiary_percentile",
    "payment_per_service_percentile",

    "utilization_score",
    "cost_score",
    "provider_segment",

    "high_utilization_flag",
    "high_cost_flag",
    "low_utilization_flag",
    "low_cost_flag",
]

performance_selected = performance[
    performance_columns
].copy()

print(
    f"Performance features selected: "
    f"{len(performance_selected.columns) - 2}"
)


# ============================================================
# SELECT LONGITUDINAL COLUMNS
# ============================================================

print_section("SELECTING LONGITUDINAL FEATURES")

longitudinal_columns = [
    "Rndrng_NPI",

    "years_observed",
    "first_year",
    "last_year",

    "dominant_provider_segment",
    "segment_year_count",
    "segment_stability",
    "overall_provider_segment",
    "history_class",
]

longitudinal_selected = longitudinal[
    longitudinal_columns
].copy()

print(
    f"Longitudinal features selected: "
    f"{len(longitudinal_selected.columns) - 1}"
)


# ============================================================
# RENAME DUPLICATE-LIKE LONGITUDINAL FIELDS
# ============================================================

print_section("STANDARDIZING LONGITUDINAL FEATURE NAMES")

longitudinal_selected = longitudinal_selected.rename(
    columns={
        "years_observed":
            "longitudinal_years_observed",

        "first_year":
            "longitudinal_first_year",

        "last_year":
            "longitudinal_last_year",
    }
)

print("✓ Longitudinal names standardized.")


# ============================================================
# CHECK COLUMN COLLISIONS
# ============================================================

print_section("CHECKING COLUMN COLLISIONS")

base_columns = set(base.columns)

performance_merge_columns = set(
    performance_selected.columns
) - {
    "Rndrng_NPI",
    "Year",
}

longitudinal_merge_columns = set(
    longitudinal_selected.columns
) - {
    "Rndrng_NPI",
}

performance_collisions = (
    base_columns & performance_merge_columns
)

longitudinal_collisions = (
    base_columns & longitudinal_merge_columns
)

print(
    "Performance collisions:"
)

if performance_collisions:
    for col in sorted(performance_collisions):
        print(f"  ⚠ {col}")
else:
    print("  ✓ None")

print(
    "\nLongitudinal collisions:"
)

if longitudinal_collisions:
    for col in sorted(longitudinal_collisions):
        print(f"  ⚠ {col}")
else:
    print("  ✓ None")


if performance_collisions:
    raise ValueError(
        "Performance feature collision detected. "
        "Resolve before merging."
    )

if longitudinal_collisions:
    raise ValueError(
        "Longitudinal feature collision detected. "
        "Resolve before merging."
    )


# ============================================================
# MERGE PERFORMANCE
# ============================================================

print_section("MERGING PROVIDER PERFORMANCE FEATURES")

original_rows = len(base)

final_df = base.merge(
    performance_selected,
    on=[
        "Rndrng_NPI",
        "Year",
    ],
    how="left",
    validate="one_to_one",
)

print(
    f"Rows after performance merge: "
    f"{len(final_df):,}"
)

if len(final_df) != original_rows:
    raise ValueError(
        "Performance merge changed row count."
    )

print("✓ Row count preserved.")


# ============================================================
# VALIDATE PERFORMANCE MERGE
# ============================================================

performance_feature_check = [
    "utilization_score",
    "cost_score",
    "provider_segment",
]

print(
    "\nPerformance feature coverage:"
)

for column in performance_feature_check:

    missing = final_df[column].isna().sum()

    print(
        f"{column}: "
        f"{missing:,} missing"
    )


# ============================================================
# MERGE LONGITUDINAL
# ============================================================

print_section("MERGING LONGITUDINAL FEATURES")

final_df = final_df.merge(
    longitudinal_selected,
    on="Rndrng_NPI",
    how="left",
    validate="many_to_one",
)

print(
    f"Rows after longitudinal merge: "
    f"{len(final_df):,}"
)

if len(final_df) != original_rows:
    raise ValueError(
        "Longitudinal merge changed row count."
    )

print("✓ Row count preserved.")


# ============================================================
# CHECK FINAL GRAIN
# ============================================================

print_section("VALIDATING FINAL DATASET GRAIN")

final_duplicates = final_df.duplicated(
    subset=[
        "Rndrng_NPI",
        "Year"
    ]
).sum()

print(
    f"Duplicate NPI-Year rows: "
    f"{final_duplicates:,}"
)

if final_duplicates != 0:
    raise ValueError(
        "Final dataset contains duplicate NPI-Year rows."
    )

print("✓ NPI + Year grain preserved.")


# ============================================================
# CHECK ACO
# ============================================================

print_section("VALIDATING ACO COVERAGE")

missing_aco = final_df["ACO_ID"].isna().sum()

unique_acos = (
    final_df["ACO_ID"]
    .dropna()
    .nunique()
)

print(
    f"Missing ACO_ID: {missing_aco:,}"
)

print(
    f"Unique ACOs: {unique_acos:,}"
)

if missing_aco != 0:
    raise ValueError(
        "Final dataset contains missing ACO_ID values."
    )

print("✓ All rows have ACO_ID.")


# ============================================================
# FINAL FEATURE COVERAGE
# ============================================================

print_section("CHECKING FINAL PERFORMANCE FEATURES")

required_final_features = [
    "utilization_score",
    "cost_score",
    "provider_segment",
    "high_utilization_flag",
    "high_cost_flag",
    "low_utilization_flag",
    "low_cost_flag",
    "dominant_provider_segment",
    "segment_year_count",
    "segment_stability",
    "overall_provider_segment",
    "history_class",
]

for column in required_final_features:

    if column not in final_df.columns:

        raise ValueError(
            f"Missing final feature: {column}"
        )

    print(f"✓ {column}")


# ============================================================
# CHECK LONGITUDINAL NULLS
# ============================================================

print_section("CHECKING LONGITUDINAL COVERAGE")

longitudinal_check = [
    "longitudinal_years_observed",
    "longitudinal_first_year",
    "longitudinal_last_year",
    "dominant_provider_segment",
    "segment_year_count",
    "segment_stability",
    "overall_provider_segment",
    "history_class",
]

for column in longitudinal_check:

    missing = final_df[column].isna().sum()

    print(
        f"{column}: "
        f"{missing:,} missing"
    )


# ============================================================
# SAVE
# ============================================================

print_section("SAVING FINAL DATASET")

final_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"✓ Final dataset saved successfully:"
)

print(
    OUTPUT_FILE
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 90)
print("FINAL PROVIDER + ACO FEATURE DATASET COMPLETE")
print("=" * 90)

print(
    f"\nRows:                 {len(final_df):,}"
)

print(
    f"Columns:              {len(final_df.columns):,}"
)

print(
    f"Unique providers:     "
    f"{final_df['Rndrng_NPI'].nunique():,}"
)

print(
    f"Unique years:         "
    f"{final_df['Year'].nunique():,}"
)

print(
    f"Unique ACOs:          "
    f"{final_df['ACO_ID'].nunique():,}"
)

print(
    f"Duplicate NPI-Year:   "
    f"{final_duplicates:,}"
)

print(
    f"Missing ACO_ID:       "
    f"{missing_aco:,}"
)

print("\nPerformance layer:")
print("✓ utilization_score")
print("✓ cost_score")
print("✓ provider_segment")
print("✓ performance flags")

print("\nLongitudinal layer:")
print("✓ dominant_provider_segment")
print("✓ segment_year_count")
print("✓ segment_stability")
print("✓ overall_provider_segment")
print("✓ history_class")

print("\nOutput:")
print(OUTPUT_FILE)

print("\n" + "=" * 90)