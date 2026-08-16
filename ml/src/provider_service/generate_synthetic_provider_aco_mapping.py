"""
Generate Synthetic Provider -> ACO Mapping

Purpose:
    Create a reproducible synthetic relationship between provider NPI
    and ACO_ID because the available provider-service data does not
    contain a real provider-to-ACO relationship.

Important:
    This is SYNTHETIC data.
    It must NOT be interpreted as real CMS/ACO attribution.

Input:
    data/processed/provider_service/provider_features_stage4.csv

Output:
    data/processed/provider_service/provider_aco_mapping.csv

Mapping rule:
    One NPI is assigned to exactly one synthetic ACO.
    The same NPI keeps the same ACO across all available years.

Example:

    NPI        Year    ACO_ID
    123456     2021    ACO_004
    123456     2022    ACO_004
    123456     2023    ACO_004

    987654     2021    ACO_009
    987654     2022    ACO_009
"""

import hashlib
from pathlib import Path

import pandas as pd


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_features_stage4.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_aco_mapping.csv"
)


# ============================================================
# 2. CONFIGURATION
# ============================================================

# Number of synthetic ACOs.
NUMBER_OF_ACOS = 10

# Fixed seed.
# Keeping this fixed makes the mapping reproducible.
RANDOM_SEED = 42


# ============================================================
# 3. CREATE SYNTHETIC ACO NAMES
# ============================================================

ACO_IDS = [
    f"ACO_{i:03d}"
    for i in range(1, NUMBER_OF_ACOS + 1)
]


# ============================================================
# 4. PRINT CONFIGURATION
# ============================================================

print("=" * 80)
print("SYNTHETIC PROVIDER → ACO MAPPING")
print("=" * 80)

print(f"\nProject root:")
print(PROJECT_ROOT)

print(f"\nInput file:")
print(INPUT_FILE)

print(f"\nOutput file:")
print(OUTPUT_FILE)

print(f"\nNumber of synthetic ACOs:")
print(NUMBER_OF_ACOS)

print(f"\nSynthetic ACO IDs:")
print(", ".join(ACO_IDS))

print(f"\nFixed seed:")
print(RANDOM_SEED)


# ============================================================
# 5. CHECK INPUT FILE
# ============================================================

print("\n" + "-" * 80)
print("CHECKING INPUT FILE")
print("-" * 80)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nInput file was not found:\n{INPUT_FILE}\n\n"
        "Make sure provider_features_stage4.csv exists."
    )

print("Input file found.")


# ============================================================
# 6. LOAD ONLY REQUIRED COLUMNS
# ============================================================

print("\n" + "-" * 80)
print("LOADING PROVIDER DATA")
print("-" * 80)

df = pd.read_csv(
    INPUT_FILE,
    usecols=["Rndrng_NPI", "Year"],
    dtype={
        "Rndrng_NPI": "string",
        "Year": "Int64",
    },
)

print(f"Rows loaded: {len(df):,}")


# ============================================================
# 7. BASIC VALIDATION
# ============================================================

print("\n" + "-" * 80)
print("VALIDATING NPI DATA")
print("-" * 80)

missing_npi = df["Rndrng_NPI"].isna().sum()

print(f"Missing NPI values: {missing_npi:,}")

if missing_npi > 0:
    print("Removing rows with missing NPI.")

    df = df.dropna(subset=["Rndrng_NPI"])


# Convert NPI to clean string representation.
df["Rndrng_NPI"] = (
    df["Rndrng_NPI"]
    .astype("string")
    .str.strip()
)


# Remove empty strings.
empty_npi = (df["Rndrng_NPI"] == "").sum()

print(f"Empty NPI values: {empty_npi:,}")

if empty_npi > 0:
    df = df[df["Rndrng_NPI"] != ""]


# ============================================================
# 8. GET UNIQUE NPIs
# ============================================================

unique_npis = (
    df["Rndrng_NPI"]
    .drop_duplicates()
    .sort_values()
    .reset_index(drop=True)
)

print(f"\nUnique providers (NPI): {len(unique_npis):,}")


# ============================================================
# 9. CREATE DETERMINISTIC NPI → ACO ASSIGNMENT
# ============================================================

print("\n" + "-" * 80)
print("CREATING SYNTHETIC NPI → ACO ASSIGNMENT")
print("-" * 80)

print(
    "\nEach NPI will receive exactly one ACO."
)

print(
    "The same NPI will retain the same ACO across all years."
)


def assign_aco(npi):
    """
    Deterministically assign an NPI to one synthetic ACO.

    hashlib is used instead of Python's random module so that
    the same NPI always receives the same ACO.
    """

    value = f"{RANDOM_SEED}_{npi}"

    hash_value = hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()

    numeric_value = int(hash_value, 16)

    aco_index = numeric_value % NUMBER_OF_ACOS

    return ACO_IDS[aco_index]


mapping = pd.DataFrame(
    {
        "Rndrng_NPI": unique_npis
    }
)

mapping["ACO_ID"] = mapping["Rndrng_NPI"].apply(assign_aco)


# ============================================================
# 10. VALIDATE NPI → ACO RELATIONSHIP
# ============================================================

print("\n" + "-" * 80)
print("VALIDATING NPI → ACO RELATIONSHIP")
print("-" * 80)

npi_to_aco_counts = (
    mapping
    .groupby("Rndrng_NPI")["ACO_ID"]
    .nunique()
)

providers_with_multiple_acos = (
    npi_to_aco_counts > 1
).sum()

print(
    f"Providers assigned to multiple ACOs: "
    f"{providers_with_multiple_acos:,}"
)

if providers_with_multiple_acos != 0:
    raise ValueError(
        "Validation failed: at least one NPI has multiple ACO assignments."
    )

print("✓ Every NPI has exactly one ACO.")


# ============================================================
# 11. CHECK MAPPING COMPLETENESS
# ============================================================

missing_aco = mapping["ACO_ID"].isna().sum()

print(f"Missing ACO_ID values: {missing_aco:,}")

if missing_aco != 0:
    raise ValueError(
        "Validation failed: some NPIs do not have an ACO_ID."
    )

print("✓ Every NPI has an ACO_ID.")


# ============================================================
# 12. CHECK DUPLICATE NPI MAPPINGS
# ============================================================

duplicate_npis = mapping["Rndrng_NPI"].duplicated().sum()

print(f"Duplicate NPI rows: {duplicate_npis:,}")

if duplicate_npis != 0:
    raise ValueError(
        "Validation failed: duplicate NPI mappings found."
    )

print("✓ No duplicate NPI mappings.")


# ============================================================
# 13. ACO DISTRIBUTION
# ============================================================

print("\n" + "-" * 80)
print("ACO DISTRIBUTION")
print("-" * 80)

aco_distribution = (
    mapping["ACO_ID"]
    .value_counts()
    .sort_index()
)

distribution = pd.DataFrame(
    {
        "ACO_ID": aco_distribution.index,
        "Provider_Count": aco_distribution.values,
    }
)

distribution["Provider_Percentage"] = (
    distribution["Provider_Count"]
    / len(mapping)
    * 100
)

print(
    distribution.to_string(
        index=False,
        formatters={
            "Provider_Percentage": "{:.2f}%".format
        },
    )
)


# ============================================================
# 14. MERGE YEARS ONLY FOR VALIDATION
# ============================================================

print("\n" + "-" * 80)
print("CHECKING YEAR COVERAGE")
print("-" * 80)

provider_years = (
    df[
        ["Rndrng_NPI", "Year"]
    ]
    .drop_duplicates()
)

provider_years = provider_years.merge(
    mapping,
    on="Rndrng_NPI",
    how="left",
    validate="many_to_one",
)

print(
    f"Provider-Year combinations: "
    f"{len(provider_years):,}"
)

missing_mapping = provider_years["ACO_ID"].isna().sum()

print(
    f"Provider-Year rows without ACO: "
    f"{missing_mapping:,}"
)

if missing_mapping != 0:
    raise ValueError(
        "Validation failed: some provider-year rows have no ACO."
    )

print("✓ Every provider-year has an ACO through its NPI mapping.")


# ============================================================
# 15. SAVE MAPPING
# ============================================================

print("\n" + "-" * 80)
print("SAVING MAPPING")
print("-" * 80)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

mapping.to_csv(
    OUTPUT_FILE,
    index=False
)

print(f"Saved successfully:")
print(OUTPUT_FILE)


# ============================================================
# 16. SHOW SAMPLE
# ============================================================

print("\n" + "-" * 80)
print("SAMPLE MAPPING")
print("-" * 80)

print(
    mapping
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 17. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("SYNTHETIC MAPPING COMPLETE")
print("=" * 80)

print(f"\nUnique providers:       {len(mapping):,}")
print(f"Synthetic ACOs:         {mapping['ACO_ID'].nunique():,}")
print(f"Provider-Year rows:     {len(provider_years):,}")
print(f"Missing NPI:            {missing_npi:,}")
print(f"Missing ACO:            {missing_aco:,}")
print(f"Duplicate NPIs:         {duplicate_npis:,}")
print(
    f"Providers with >1 ACO:  "
    f"{providers_with_multiple_acos:,}"
)

print("\nOutput:")
print(OUTPUT_FILE)

print("\nIMPORTANT:")
print(
    "This ACO assignment is SYNTHETIC and is only for "
    "pipeline/dashboard prototyping."
)

print("=" * 80)