from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

ACO_FILE = (
    BASE_DIR
    / "data"
    / "interim"
    / "fact_aco_performance_raw_combined.csv"
)

PROVIDER_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "provider_service"
    / "provider_features_stage4.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "all_aco"
)

OUTPUT_FILE = OUTPUT_DIR / "aco_provider_mapping.csv"

RANDOM_SEED = 42


# ============================================================
# START
# ============================================================

print("=" * 80)
print("COMPLETE ALL-PROVIDER → ACO MAPPING")
print("=" * 80)


# ============================================================
# CHECK INPUT FILES
# ============================================================

if not ACO_FILE.exists():
    raise FileNotFoundError(
        f"ACO file not found:\n{ACO_FILE}"
    )

if not PROVIDER_FILE.exists():
    raise FileNotFoundError(
        f"Provider file not found:\n{PROVIDER_FILE}"
    )


# ============================================================
# LOAD ACO UNIVERSE
# ============================================================

print("\n" + "=" * 80)
print("LOADING ACO UNIVERSE")
print("=" * 80)

aco_df = pd.read_csv(
    ACO_FILE,
    usecols=[
        "ACO_ID",
        "performance_year"
    ],
    low_memory=False
)

aco_df["ACO_ID"] = (
    aco_df["ACO_ID"]
    .astype(str)
    .str.strip()
)

aco_df = aco_df[
    aco_df["ACO_ID"].notna()
    & (aco_df["ACO_ID"] != "")
]

aco_df = aco_df.drop_duplicates(
    subset=[
        "ACO_ID",
        "performance_year"
    ]
)

aco_ids = sorted(
    aco_df["ACO_ID"]
    .dropna()
    .unique()
    .tolist()
)

print(
    f"Unique ACOs: {len(aco_ids):,}"
)

print(
    f"Unique ACO-years: {len(aco_df):,}"
)

if len(aco_ids) == 0:
    raise ValueError(
        "No ACO IDs found."
    )


# ============================================================
# LOAD ALL PROVIDERS
# ============================================================

print("\n" + "=" * 80)
print("LOADING ALL PROVIDERS")
print("=" * 80)

provider_df = pd.read_csv(
    PROVIDER_FILE,
    usecols=[
        "Rndrng_NPI"
    ],
    low_memory=False
)

provider_df = provider_df.dropna(
    subset=[
        "Rndrng_NPI"
    ]
)

provider_df["Rndrng_NPI"] = (
    provider_df["Rndrng_NPI"]
    .astype(str)
    .str.strip()
)

provider_df = provider_df[
    provider_df["Rndrng_NPI"] != ""
]

# One row per unique provider
provider_df = (
    provider_df
    .drop_duplicates(
        subset=[
            "Rndrng_NPI"
        ]
    )
    .reset_index(drop=True)
)

print(
    f"Unique providers available: "
    f"{len(provider_df):,}"
)


# ============================================================
# VALIDATE PROVIDER COUNT
# ============================================================

provider_count = len(provider_df)
aco_count = len(aco_ids)

if provider_count == 0:
    raise ValueError(
        "No providers found."
    )

if aco_count == 0:
    raise ValueError(
        "No ACOs found."
    )


# ============================================================
# CALCULATE EXPECTED DISTRIBUTION
# ============================================================

base_providers_per_aco = (
    provider_count // aco_count
)

remainder = (
    provider_count % aco_count
)

print("\n" + "=" * 80)
print("ACO DISTRIBUTION")
print("=" * 80)

print(
    f"Total providers: {provider_count:,}"
)

print(
    f"Total ACOs: {aco_count:,}"
)

print(
    f"Base providers per ACO: "
    f"{base_providers_per_aco:,}"
)

print(
    f"Remaining providers: "
    f"{remainder:,}"
)

print(
    "\nEach ACO will receive either "
    f"{base_providers_per_aco:,} or "
    f"{base_providers_per_aco + 1:,} providers."
)


# ============================================================
# STABLE RANDOMIZATION
# ============================================================

print("\n" + "=" * 80)
print("CREATING DETERMINISTIC PROVIDER → ACO ASSIGNMENTS")
print("=" * 80)

# Randomize provider ordering using a fixed seed.
# This prevents the mapping from depending on the
# original CSV ordering while keeping it reproducible.

provider_df = (
    provider_df
    .sample(
        frac=1,
        random_state=RANDOM_SEED
    )
    .reset_index(drop=True)
)


# ============================================================
# ASSIGN ACOs
# ============================================================

# Repeat ACO IDs enough times to cover every provider.
#
# Example:
#
# providers = 135041
# ACOs = 686
#
# Every provider gets exactly one ACO.

aco_assignment = []

for index in range(provider_count):

    aco_index = index % aco_count

    aco_assignment.append(
        aco_ids[aco_index]
    )


provider_df["ACO_ID"] = (
    aco_assignment
)


# ============================================================
# ADD METADATA
# ============================================================

provider_df["provider_name"] = (
    "Provider_" +
    provider_df["Rndrng_NPI"].astype(str)
)

provider_df["mapping_type"] = (
    "synthetic_complete"
)

provider_df["mapping_seed"] = (
    RANDOM_SEED
)


# ============================================================
# FINAL COLUMN ORDER
# ============================================================

mapping_df = provider_df[
    [
        "ACO_ID",
        "Rndrng_NPI",
        "provider_name",
        "mapping_type",
        "mapping_seed"
    ]
].copy()


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("VALIDATING COMPLETE MAPPING")
print("=" * 80)


# ------------------------------------------------------------
# Provider uniqueness
# ------------------------------------------------------------

duplicate_providers = (
    mapping_df[
        "Rndrng_NPI"
    ]
    .duplicated()
    .sum()
)


# ------------------------------------------------------------
# Provider-ACO pair uniqueness
# ------------------------------------------------------------

duplicate_pairs = (
    mapping_df[
        [
            "ACO_ID",
            "Rndrng_NPI"
        ]
    ]
    .duplicated()
    .sum()
)


# ------------------------------------------------------------
# Missing ACO
# ------------------------------------------------------------

missing_aco = (
    mapping_df[
        "ACO_ID"
    ]
    .isna()
    .sum()
)


# ------------------------------------------------------------
# Unique counts
# ------------------------------------------------------------

mapped_providers = (
    mapping_df[
        "Rndrng_NPI"
    ]
    .nunique()
)

mapped_acos = (
    mapping_df[
        "ACO_ID"
    ]
    .nunique()
)


print(
    f"Mapping rows: {len(mapping_df):,}"
)

print(
    f"Mapped providers: {mapped_providers:,}"
)

print(
    f"Unique ACOs: {mapped_acos:,}"
)

print(
    f"Duplicate providers: "
    f"{duplicate_providers:,}"
)

print(
    f"Duplicate provider-ACO pairs: "
    f"{duplicate_pairs:,}"
)

print(
    f"Missing ACO IDs: "
    f"{missing_aco:,}"
)


# ============================================================
# PROVIDER DISTRIBUTION
# ============================================================

providers_per_aco = (
    mapping_df
    .groupby(
        "ACO_ID"
    )[
        "Rndrng_NPI"
    ]
    .nunique()
)

print("\nProviders per ACO:")

print(
    providers_per_aco.describe()
)


# ============================================================
# HARD VALIDATION
# ============================================================

if mapped_providers != provider_count:

    raise ValueError(
        "Not every provider received an ACO assignment."
    )


if mapped_acos != aco_count:

    raise ValueError(
        "Not every ACO received providers."
    )


if duplicate_providers != 0:

    raise ValueError(
        "Duplicate provider assignments detected."
    )


if duplicate_pairs != 0:

    raise ValueError(
        "Duplicate provider-ACO pairs detected."
    )


if missing_aco != 0:

    raise ValueError(
        "Missing ACO_ID values detected."
    )


# ============================================================
# SAVE
# ============================================================

print("\n" + "=" * 80)
print("SAVING COMPLETE MAPPING")
print("=" * 80)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

mapping_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"Output: {OUTPUT_FILE}"
)

print(
    f"Rows: {len(mapping_df):,}"
)

print(
    f"Providers: "
    f"{mapping_df['Rndrng_NPI'].nunique():,}"
)

print(
    f"ACOs: "
    f"{mapping_df['ACO_ID'].nunique():,}"
)

print(
    f"Minimum providers per ACO: "
    f"{providers_per_aco.min():,}"
)

print(
    f"Maximum providers per ACO: "
    f"{providers_per_aco.max():,}"
)

print("\n" + "=" * 80)
print("MAPPING CREATED SUCCESSFULLY")
print("=" * 80)