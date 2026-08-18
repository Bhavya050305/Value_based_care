from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

STAGE4_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_features_stage4.csv"
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

ACO_MAPPING_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "all_aco"
    / "aco_provider_mapping.csv"
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

    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


# ============================================================
# HEADER
# ============================================================

print("=" * 90)
print("BUILD FINAL PROVIDER + ACO FEATURE DATASET")
print("=" * 90)

print("\nProject root:")
print(PROJECT_ROOT)

print("\nStage 4 dataset:")
print(STAGE4_FILE)

print("\nPerformance dataset:")
print(PERFORMANCE_FILE)

print("\nLongitudinal dataset:")
print(LONGITUDINAL_FILE)

print("\nACO mapping:")
print(ACO_MAPPING_FILE)

print("\nOutput:")
print(OUTPUT_FILE)


# ============================================================
# CHECK INPUT FILES
# ============================================================

print_section("CHECKING INPUT FILES")

required_files = [
    STAGE4_FILE,
    PERFORMANCE_FILE,
    LONGITUDINAL_FILE,
    ACO_MAPPING_FILE,
]

for file_path in required_files:

    if not file_path.exists():

        raise FileNotFoundError(
            f"\nRequired file not found:\n{file_path}"
        )

    print(f"✓ Found: {file_path.name}")


# ============================================================
# LOAD STAGE 4
# ============================================================

print_section("LOADING STAGE 4 PROVIDER FEATURES")

stage4 = pd.read_csv(
    STAGE4_FILE,
    low_memory=False
)

print(
    f"Rows loaded: {len(stage4):,}"
)

print(
    f"Columns loaded: {len(stage4.columns):,}"
)


# ============================================================
# LOAD PERFORMANCE
# ============================================================

print_section("LOADING PROVIDER PERFORMANCE FEATURES")

performance = pd.read_csv(
    PERFORMANCE_FILE,
    low_memory=False
)

print(
    f"Rows loaded: {len(performance):,}"
)

print(
    f"Columns loaded: {len(performance.columns):,}"
)


# ============================================================
# LOAD LONGITUDINAL
# ============================================================

print_section("LOADING PROVIDER LONGITUDINAL FEATURES")

longitudinal = pd.read_csv(
    LONGITUDINAL_FILE,
    low_memory=False
)

print(
    f"Rows loaded: {len(longitudinal):,}"
)

print(
    f"Columns loaded: {len(longitudinal.columns):,}"
)


# ============================================================
# LOAD ACO MAPPING
# ============================================================

print_section("LOADING ACO PROVIDER MAPPING")

aco_mapping = pd.read_csv(
    ACO_MAPPING_FILE,
    low_memory=False
)

print(
    f"Rows loaded: {len(aco_mapping):,}"
)

print(
    f"Columns loaded: {len(aco_mapping.columns):,}"
)


# ============================================================
# REQUIRED COLUMN VALIDATION
# ============================================================

print_section("VALIDATING REQUIRED COLUMNS")


def check_columns(df, required, dataset_name):

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            f"\n{dataset_name} is missing required columns:\n"
            + "\n".join(missing)
        )

    print(
        f"✓ {dataset_name}: required columns present"
    )


check_columns(
    stage4,
    [
        "Rndrng_NPI",
        "Year",
    ],
    "Stage 4"
)


check_columns(
    performance,
    [
        "Rndrng_NPI",
        "Year",
        "utilization_score",
        "cost_score",
        "provider_segment",
    ],
    "Performance"
)


check_columns(
    longitudinal,
    [
        "Rndrng_NPI",
        "dominant_provider_segment",
        "segment_year_count",
        "segment_stability",
        "overall_provider_segment",
        "history_class",
    ],
    "Longitudinal"
)


check_columns(
    aco_mapping,
    [
        "ACO_ID",
        "Rndrng_NPI",
    ],
    "ACO Mapping"
)


# ============================================================
# STANDARDIZE NPI
# ============================================================

print_section("STANDARDIZING NPI VALUES")


def standardize_npi(df):

    df["Rndrng_NPI"] = pd.to_numeric(
        df["Rndrng_NPI"],
        errors="coerce"
    ).astype("Int64")

    return df


stage4 = standardize_npi(stage4)
performance = standardize_npi(performance)
longitudinal = standardize_npi(longitudinal)
aco_mapping = standardize_npi(aco_mapping)


# ============================================================
# STANDARDIZE YEAR
# ============================================================

print_section("STANDARDIZING YEAR VALUES")

stage4["Year"] = pd.to_numeric(
    stage4["Year"],
    errors="coerce"
).astype("Int64")

performance["Year"] = pd.to_numeric(
    performance["Year"],
    errors="coerce"
).astype("Int64")

print("✓ Year values standardized.")


# ============================================================
# BASIC VALIDATION
# ============================================================

print_section("VALIDATING STAGE 4 GRAIN")

stage4_duplicates = stage4.duplicated(
    subset=[
        "Rndrng_NPI",
        "Year",
    ]
).sum()

print(
    f"Duplicate NPI-Year rows: "
    f"{stage4_duplicates:,}"
)

if stage4_duplicates != 0:

    raise ValueError(
        "Stage 4 does not have unique NPI-Year grain."
    )

print("✓ Stage 4 NPI-Year grain passed.")


# ============================================================
# PERFORMANCE GRAIN
# ============================================================

print_section("VALIDATING PERFORMANCE GRAIN")

performance_duplicates = performance.duplicated(
    subset=[
        "Rndrng_NPI",
        "Year",
    ]
).sum()

print(
    f"Duplicate NPI-Year rows: "
    f"{performance_duplicates:,}"
)

if performance_duplicates != 0:

    raise ValueError(
        "Performance dataset contains duplicate NPI-Year rows."
    )

print("✓ Performance NPI-Year grain passed.")


# ============================================================
# LONGITUDINAL GRAIN
# ============================================================

print_section("VALIDATING LONGITUDINAL GRAIN")

longitudinal_duplicates = longitudinal.duplicated(
    subset=["Rndrng_NPI"]
).sum()

print(
    f"Duplicate NPI rows: "
    f"{longitudinal_duplicates:,}"
)

if longitudinal_duplicates != 0:

    raise ValueError(
        "Longitudinal dataset must contain one row per NPI."
    )

print("✓ Longitudinal one-row-per-NPI grain passed.")


# ============================================================
# ACO MAPPING GRAIN
# ============================================================

print_section("VALIDATING ACO MAPPING")

aco_duplicates = aco_mapping.duplicated(
    subset=["Rndrng_NPI"]
).sum()

print(
    f"Duplicate provider mappings: "
    f"{aco_duplicates:,}"
)

if aco_duplicates != 0:

    raise ValueError(
        "ACO mapping contains multiple ACO assignments "
        "for the same NPI."
    )

print("✓ One ACO assignment per provider.")


# ============================================================
# ACO COVERAGE
# ============================================================

stage4_npis = set(
    stage4["Rndrng_NPI"]
    .dropna()
    .unique()
)

aco_npis = set(
    aco_mapping["Rndrng_NPI"]
    .dropna()
    .unique()
)

missing_aco_npis = stage4_npis - aco_npis

print(
    f"\nStage 4 unique providers: "
    f"{len(stage4_npis):,}"
)

print(
    f"Mapped providers: "
    f"{len(aco_npis):,}"
)

print(
    f"Stage 4 providers without ACO: "
    f"{len(missing_aco_npis):,}"
)

if missing_aco_npis:

    print(
        "\nWARNING: Some providers do not have an ACO mapping."
    )

else:

    print(
        "✓ All Stage 4 providers have an ACO mapping."
    )


# ============================================================
# SELECT ACO COLUMNS
# ============================================================

print_section("PREPARING ACO MAPPING")

aco_selected = aco_mapping[
    [
        "Rndrng_NPI",
        "ACO_ID",
        "provider_name",
        "mapping_type",
        "mapping_seed",
    ]
].copy()

# Rename mapping provider name before merge
# to avoid provider_name_x / provider_name_y.
aco_selected = aco_selected.rename(
    columns={"provider_name": "mapped_provider_name"}
)

print(
    f"ACO mapping columns: "
    f"{len(aco_selected.columns)}"
)

print(
    f"Unique ACOs: "
    f"{aco_selected['ACO_ID'].nunique():,}"
)


# ============================================================
# MERGE ACO
# ============================================================

print_section("MERGING ACO ASSIGNMENTS")

original_rows = len(stage4)

final_df = stage4.merge(
    aco_selected,
    on="Rndrng_NPI",
    how="left",
    validate="many_to_one",
)
# Preserve the Stage 4 provider name when available.
# Fall back to the complete ACO mapping name otherwise.
final_df["provider_name"] = (
    final_df["provider_name"]
    .combine_first(final_df["mapped_provider_name"])
)

final_df = final_df.drop(
    columns=["mapped_provider_name"],
    errors="ignore",

)

print(
    f"Rows after ACO merge: "
    f"{len(final_df):,}"
)

if len(final_df) != original_rows:

    raise ValueError(
        "ACO merge changed the Stage 4 row count."
    )

print("✓ Row count preserved.")


# ============================================================
# ACO VALIDATION
# ============================================================

missing_aco = final_df["ACO_ID"].isna().sum()

print(
    f"Missing ACO_ID: "
    f"{missing_aco:,}"
)

if missing_aco != 0:

    raise ValueError(
        "Some provider-year records have no ACO_ID."
    )

print("✓ ACO coverage passed.")


# ============================================================
# SELECT PERFORMANCE FEATURES
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

missing_performance_columns = [
    col
    for col in performance_columns
    if col not in performance.columns
]

if missing_performance_columns:

    raise ValueError(
        "Missing performance columns:\n"
        + "\n".join(missing_performance_columns)
    )

performance_selected = performance[
    performance_columns
].copy()

print(
    f"Performance features selected: "
    f"{len(performance_columns) - 2}"
)


# ============================================================
# MERGE PERFORMANCE
# ============================================================

print_section("MERGING PERFORMANCE FEATURES")

performance_merge_columns = set(
    performance_selected.columns
) - {
    "Rndrng_NPI",
    "Year",
}

collisions = (
    set(final_df.columns)
    & performance_merge_columns
)

if collisions:

    raise ValueError(
        f"Performance column collisions detected: "
        f"{sorted(collisions)}"
    )

final_df = final_df.merge(
    performance_selected,
    on=[
        "Rndrng_NPI",
        "Year",
    ],
    how="left",
    validate="one_to_one",
)

if len(final_df) != original_rows:

    raise ValueError(
        "Performance merge changed row count."
    )

print("✓ Performance merge completed.")
print("✓ Row count preserved.")


# ============================================================
# PERFORMANCE COVERAGE
# ============================================================

print("\nPerformance coverage:")

for column in [
    "utilization_score",
    "cost_score",
    "provider_segment",
]:

    missing = final_df[column].isna().sum()

    print(
        f"- {column}: "
        f"{missing:,} missing"
    )


# ============================================================
# SELECT LONGITUDINAL FEATURES
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

missing_longitudinal_columns = [
    col
    for col in longitudinal_columns
    if col not in longitudinal.columns
]

if missing_longitudinal_columns:

    raise ValueError(
        "Missing longitudinal columns:\n"
        + "\n".join(missing_longitudinal_columns)
    )

longitudinal_selected = longitudinal[
    longitudinal_columns
].copy()

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

print(
    f"Longitudinal features selected: "
    f"{len(longitudinal_selected.columns) - 1}"
)


# ============================================================
# MERGE LONGITUDINAL
# ============================================================

print_section("MERGING LONGITUDINAL FEATURES")

longitudinal_merge_columns = set(
    longitudinal_selected.columns
) - {
    "Rndrng_NPI",
}

collisions = (
    set(final_df.columns)
    & longitudinal_merge_columns
)

if collisions:

    raise ValueError(
        f"Longitudinal column collisions detected: "
        f"{sorted(collisions)}"
    )

final_df = final_df.merge(
    longitudinal_selected,
    on="Rndrng_NPI",
    how="left",
    validate="many_to_one",
)

if len(final_df) != original_rows:

    raise ValueError(
        "Longitudinal merge changed row count."
    )

print("✓ Longitudinal merge completed.")
print("✓ Row count preserved.")


# ============================================================
# FINAL GRAIN
# ============================================================

print_section("VALIDATING FINAL DATASET GRAIN")

final_duplicates = final_df.duplicated(
    subset=[
        "Rndrng_NPI",
        "Year",
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

print("✓ Final NPI-Year grain passed.")


# ============================================================
# FINAL ACO VALIDATION
# ============================================================

print_section("VALIDATING FINAL ACO DATA")

missing_aco = final_df["ACO_ID"].isna().sum()

unique_acos = (
    final_df["ACO_ID"]
    .dropna()
    .nunique()
)

print(
    f"Missing ACO_ID: "
    f"{missing_aco:,}"
)

print(
    f"Unique ACOs: "
    f"{unique_acos:,}"
)

if missing_aco != 0:

    raise ValueError(
        "Final dataset contains missing ACO_ID values."
    )

print("✓ Final ACO validation passed.")


# ============================================================
# FINAL FEATURE VALIDATION
# ============================================================

print_section("VALIDATING FINAL FEATURES")

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

    print(
        f"✓ {column}"
    )


# ============================================================
# LONGITUDINAL COVERAGE
# ============================================================

print_section("CHECKING LONGITUDINAL COVERAGE")

for column in [
    "dominant_provider_segment",
    "segment_year_count",
    "segment_stability",
    "overall_provider_segment",
    "history_class",
]:

    missing = final_df[column].isna().sum()

    print(
        f"{column}: "
        f"{missing:,} missing"
    )


# ============================================================
# SAVE FINAL DATASET
# ============================================================

print_section("SAVING FINAL DATASET")

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

final_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    "✓ Final dataset saved:"
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

print("\nPipeline layers:")
print("✓ Stage 4 provider features")
print("✓ ACO provider mapping")
print("✓ Provider performance")
print("✓ Provider longitudinal profile")

print("\nOutput:")
print(OUTPUT_FILE)

print("\n" + "=" * 90)