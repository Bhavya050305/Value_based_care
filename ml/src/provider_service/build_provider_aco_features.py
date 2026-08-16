"""
Build Provider + ACO Feature Dataset

Purpose:
    Merge the synthetic NPI -> ACO mapping with the existing
    provider Stage-4 feature dataset.

IMPORTANT:
    The ACO assignment is SYNTHETIC and is intended only for
    analytical/dashboard prototyping.

Input 1:
    data/processed/provider_service/provider_features_stage4.csv

Input 2:
    data/processed/provider_service/provider_aco_mapping.csv

Output:
    data/processed/provider_service/provider_aco_features.csv

Join key:
    Rndrng_NPI

Expected output grain:
    One row per Provider-Year

Expected result:
    150,000 provider-year rows
    All Stage-4 provider features
    + ACO_ID
"""

from pathlib import Path

import pandas as pd


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

STAGE4_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_features_stage4.csv"
)

MAPPING_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_aco_mapping.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_aco_features.csv"
)


# ============================================================
# 2. PRINT PROJECT INFORMATION
# ============================================================

print("=" * 80)
print("BUILD PROVIDER + ACO FEATURE DATASET")
print("=" * 80)

print("\nProject root:")
print(PROJECT_ROOT)

print("\nStage-4 provider file:")
print(STAGE4_FILE)

print("\nSynthetic ACO mapping file:")
print(MAPPING_FILE)

print("\nOutput file:")
print(OUTPUT_FILE)


# ============================================================
# 3. CHECK INPUT FILES
# ============================================================

print("\n" + "-" * 80)
print("CHECKING INPUT FILES")
print("-" * 80)

if not STAGE4_FILE.exists():
    raise FileNotFoundError(
        f"\nStage-4 file was not found:\n{STAGE4_FILE}"
    )

print("✓ Stage-4 provider file found.")

if not MAPPING_FILE.exists():
    raise FileNotFoundError(
        f"\nACO mapping file was not found:\n{MAPPING_FILE}"
    )

print("✓ Synthetic ACO mapping file found.")


# ============================================================
# 4. LOAD STAGE-4 PROVIDER DATA
# ============================================================

print("\n" + "-" * 80)
print("LOADING STAGE-4 PROVIDER DATA")
print("-" * 80)

provider_df = pd.read_csv(
    STAGE4_FILE,
    dtype={
        "Rndrng_NPI": "string"
    }
)

print(f"Provider rows loaded: {len(provider_df):,}")
print(f"Provider columns loaded: {len(provider_df.columns):,}")


# ============================================================
# 5. LOAD SYNTHETIC ACO MAPPING
# ============================================================

print("\n" + "-" * 80)
print("LOADING SYNTHETIC ACO MAPPING")
print("-" * 80)

mapping_df = pd.read_csv(
    MAPPING_FILE,
    dtype={
        "Rndrng_NPI": "string",
        "ACO_ID": "string"
    }
)

print(f"Mapping rows loaded: {len(mapping_df):,}")
print(f"Mapping columns loaded: {len(mapping_df.columns):,}")


# ============================================================
# 6. CHECK REQUIRED COLUMNS
# ============================================================

print("\n" + "-" * 80)
print("CHECKING REQUIRED COLUMNS")
print("-" * 80)

if "Rndrng_NPI" not in provider_df.columns:
    raise ValueError(
        "Stage-4 provider dataset does not contain Rndrng_NPI."
    )

if "Year" not in provider_df.columns:
    raise ValueError(
        "Stage-4 provider dataset does not contain Year."
    )

if "Rndrng_NPI" not in mapping_df.columns:
    raise ValueError(
        "ACO mapping does not contain Rndrng_NPI."
    )

if "ACO_ID" not in mapping_df.columns:
    raise ValueError(
        "ACO mapping does not contain ACO_ID."
    )

print("✓ Provider dataset contains Rndrng_NPI.")
print("✓ Provider dataset contains Year.")
print("✓ Mapping contains Rndrng_NPI.")
print("✓ Mapping contains ACO_ID.")


# ============================================================
# 7. STANDARDIZE NPI VALUES
# ============================================================

print("\n" + "-" * 80)
print("STANDARDIZING NPI VALUES")
print("-" * 80)

provider_df["Rndrng_NPI"] = (
    provider_df["Rndrng_NPI"]
    .astype("string")
    .str.strip()
)

mapping_df["Rndrng_NPI"] = (
    mapping_df["Rndrng_NPI"]
    .astype("string")
    .str.strip()
)

mapping_df["ACO_ID"] = (
    mapping_df["ACO_ID"]
    .astype("string")
    .str.strip()
)

print("✓ NPI values standardized.")


# ============================================================
# 8. CHECK PROVIDER NPI COMPLETENESS
# ============================================================

print("\n" + "-" * 80)
print("CHECKING PROVIDER NPIs")
print("-" * 80)

provider_missing_npi = (
    provider_df["Rndrng_NPI"]
    .isna()
    .sum()
)

print(
    f"Missing NPI values in Stage-4: "
    f"{provider_missing_npi:,}"
)

if provider_missing_npi > 0:
    raise ValueError(
        "Stage-4 provider dataset contains missing NPIs."
    )

print("✓ No missing NPIs in Stage-4.")


# ============================================================
# 9. CHECK MAPPING UNIQUENESS
# ============================================================

print("\n" + "-" * 80)
print("VALIDATING NPI → ACO MAPPING")
print("-" * 80)

duplicate_mapping_npi = (
    mapping_df["Rndrng_NPI"]
    .duplicated()
    .sum()
)

print(
    f"Duplicate NPI rows in mapping: "
    f"{duplicate_mapping_npi:,}"
)

if duplicate_mapping_npi > 0:
    raise ValueError(
        "ACO mapping contains duplicate NPIs. "
        "Each NPI must have exactly one ACO."
    )

print("✓ Mapping contains one row per NPI.")


# ============================================================
# 10. CHECK MULTIPLE ACO ASSIGNMENTS
# ============================================================

npi_aco_counts = (
    mapping_df
    .groupby("Rndrng_NPI")["ACO_ID"]
    .nunique()
)

multiple_aco_npis = (
    npi_aco_counts > 1
).sum()

print(
    f"NPIs assigned to multiple ACOs: "
    f"{multiple_aco_npis:,}"
)

if multiple_aco_npis > 0:
    raise ValueError(
        "At least one NPI has multiple ACO assignments."
    )

print("✓ Every NPI has exactly one ACO.")


# ============================================================
# 11. CHECK MISSING ACO IDs
# ============================================================

missing_aco = (
    mapping_df["ACO_ID"]
    .isna()
    .sum()
)

print(
    f"Missing ACO_ID values in mapping: "
    f"{missing_aco:,}"
)

if missing_aco > 0:
    raise ValueError(
        "ACO mapping contains missing ACO_ID values."
    )

print("✓ No missing ACO_ID values.")


# ============================================================
# 12. CHECK WHETHER ALL PROVIDER NPIs ARE MAPPED
# ============================================================

print("\n" + "-" * 80)
print("CHECKING PROVIDER → ACO COVERAGE")
print("-" * 80)

provider_npis = set(
    provider_df["Rndrng_NPI"]
    .dropna()
    .unique()
)

mapping_npis = set(
    mapping_df["Rndrng_NPI"]
    .dropna()
    .unique()
)

unmapped_provider_npis = (
    provider_npis - mapping_npis
)

extra_mapping_npis = (
    mapping_npis - provider_npis
)

print(
    f"Unique provider NPIs: "
    f"{len(provider_npis):,}"
)

print(
    f"Unique mapping NPIs: "
    f"{len(mapping_npis):,}"
)

print(
    f"Provider NPIs without mapping: "
    f"{len(unmapped_provider_npis):,}"
)

print(
    f"Mapping NPIs not present in provider data: "
    f"{len(extra_mapping_npis):,}"
)

if len(unmapped_provider_npis) > 0:
    raise ValueError(
        "Some provider NPIs do not have an ACO mapping."
    )

print("✓ Every provider NPI has an ACO mapping.")


# ============================================================
# 13. SAVE ORIGINAL ROW COUNT
# ============================================================

original_rows = len(provider_df)

original_columns = len(provider_df.columns)


# ============================================================
# 14. MERGE PROVIDER DATA WITH ACO MAPPING
# ============================================================

print("\n" + "-" * 80)
print("MERGING PROVIDER DATA + ACO MAPPING")
print("-" * 80)

provider_aco_df = provider_df.merge(
    mapping_df[
        [
            "Rndrng_NPI",
            "ACO_ID"
        ]
    ],
    on="Rndrng_NPI",
    how="left",
    validate="many_to_one"
)

print(
    f"Rows after merge: "
    f"{len(provider_aco_df):,}"
)

print(
    f"Columns after merge: "
    f"{len(provider_aco_df.columns):,}"
)


# ============================================================
# 15. CHECK ROW COUNT PRESERVATION
# ============================================================

print("\n" + "-" * 80)
print("CHECKING ROW COUNT PRESERVATION")
print("-" * 80)

if len(provider_aco_df) != original_rows:
    raise ValueError(
        "Row count changed during merge. "
        "This indicates a mapping/join problem."
    )

print(
    f"Original Stage-4 rows: "
    f"{original_rows:,}"
)

print(
    f"Rows after merge:      "
    f"{len(provider_aco_df):,}"
)

print("✓ Row count preserved.")


# ============================================================
# 16. CHECK ACO COVERAGE AFTER MERGE
# ============================================================

print("\n" + "-" * 80)
print("CHECKING ACO COVERAGE AFTER MERGE")
print("-" * 80)

missing_aco_after_merge = (
    provider_aco_df["ACO_ID"]
    .isna()
    .sum()
)

print(
    f"Provider-year rows without ACO_ID: "
    f"{missing_aco_after_merge:,}"
)

if missing_aco_after_merge > 0:
    raise ValueError(
        "Some provider-year rows were not assigned an ACO."
    )

print("✓ Every provider-year row has an ACO_ID.")


# ============================================================
# 17. CHECK PROVIDER-YEAR DUPLICATES
# ============================================================

print("\n" + "-" * 80)
print("CHECKING PROVIDER-YEAR GRAIN")
print("-" * 80)

duplicate_provider_years = (
    provider_aco_df
    .duplicated(
        subset=[
            "Rndrng_NPI",
            "Year"
        ]
    )
    .sum()
)

print(
    f"Duplicate NPI-Year rows: "
    f"{duplicate_provider_years:,}"
)

if duplicate_provider_years > 0:
    raise ValueError(
        "Duplicate NPI-Year rows detected."
    )

print("✓ NPI + Year remains the dataset grain.")


# ============================================================
# 18. CHECK ACO COUNT
# ============================================================

unique_acos = (
    provider_aco_df["ACO_ID"]
    .nunique()
)

print("\n" + "-" * 80)
print("ACO SUMMARY")
print("-" * 80)

print(
    f"Unique synthetic ACOs: "
    f"{unique_acos:,}"
)

print("\nACO IDs:")

for aco_id in sorted(
    provider_aco_df["ACO_ID"]
    .dropna()
    .unique()
):
    print(f"    - {aco_id}")


# ============================================================
# 19. PROVIDER COUNT BY ACO
# ============================================================

print("\n" + "-" * 80)
print("PROVIDER COUNT BY ACO")
print("-" * 80)

provider_count_by_aco = (
    provider_aco_df[
        [
            "Rndrng_NPI",
            "ACO_ID"
        ]
    ]
    .drop_duplicates()
    .groupby("ACO_ID")
    .size()
    .reset_index(
        name="Provider_Count"
    )
    .sort_values("ACO_ID")
)

provider_count_by_aco[
    "Provider_Percentage"
] = (
    provider_count_by_aco["Provider_Count"]
    / len(mapping_df)
    * 100
)

print(
    provider_count_by_aco.to_string(
        index=False,
        formatters={
            "Provider_Percentage": "{:.2f}%".format
        }
    )
)


# ============================================================
# 20. PROVIDER-YEAR COUNT BY ACO
# ============================================================

print("\n" + "-" * 80)
print("PROVIDER-YEAR COUNT BY ACO")
print("-" * 80)

provider_year_count_by_aco = (
    provider_aco_df
    .groupby("ACO_ID")
    .size()
    .reset_index(
        name="Provider_Year_Count"
    )
    .sort_values("ACO_ID")
)

print(
    provider_year_count_by_aco.to_string(
        index=False
    )
)


# ============================================================
# 21. SHOW SAMPLE RECORDS
# ============================================================

print("\n" + "-" * 80)
print("SAMPLE PROVIDER + ACO RECORDS")
print("-" * 80)

sample_columns = [
    "Rndrng_NPI",
    "Year",
    "ACO_ID"
]

print(
    provider_aco_df[
        sample_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 22. SAVE OUTPUT
# ============================================================

print("\n" + "-" * 80)
print("SAVING PROVIDER + ACO FEATURE DATASET")
print("-" * 80)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

provider_aco_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("✓ Dataset saved successfully.")

print("\nOutput:")
print(OUTPUT_FILE)


# ============================================================
# 23. FINAL VALIDATION SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("PROVIDER + ACO FEATURE DATASET COMPLETE")
print("=" * 80)

print(
    f"\nOriginal provider rows:       "
    f"{original_rows:,}"
)

print(
    f"Final provider-ACO rows:      "
    f"{len(provider_aco_df):,}"
)

print(
    f"Original provider columns:    "
    f"{original_columns:,}"
)

print(
    f"Final columns:                "
    f"{len(provider_aco_df.columns):,}"
)

print(
    f"Unique providers:             "
    f"{provider_aco_df['Rndrng_NPI'].nunique():,}"
)

print(
    f"Unique years:                 "
    f"{provider_aco_df['Year'].nunique():,}"
)

print(
    f"Unique synthetic ACOs:        "
    f"{provider_aco_df['ACO_ID'].nunique():,}"
)

print(
    f"Missing ACO_ID:               "
    f"{missing_aco_after_merge:,}"
)

print(
    f"Duplicate NPI-Year rows:      "
    f"{duplicate_provider_years:,}"
)

print("\nValidation results:")

print("✓ Row count preserved")
print("✓ All provider NPIs mapped")
print("✓ No missing ACO IDs")
print("✓ One ACO per NPI")
print("✓ NPI + Year grain preserved")
print("✓ No duplicate NPI-Year rows")
print("✓ Stage-4 provider features preserved")

print("\nIMPORTANT:")
print(
    "ACO_ID is SYNTHETIC and must only be used for "
    "analytical/dashboard prototyping."
)

print("\nOutput file:")
print(OUTPUT_FILE)

print("=" * 80)