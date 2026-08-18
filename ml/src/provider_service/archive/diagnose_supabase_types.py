from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CSV_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "bhavya_provider_aco_features_final.csv"
)


# ============================================================
# EXPECTED BIGINT COLUMNS
# ============================================================

BIGINT_COLUMNS = {
    "Rndrng_NPI",
    "Year",

    "Tot_HCPCS_Cds",
    "Tot_Benes",
    

    "Drug_Tot_HCPCS_Cds",
    "Drug_Tot_Benes",
    

    "Med_Tot_HCPCS_Cds",
    "Med_Tot_Benes",
    

    "Bene_Age_LT_65_Cnt",
    "Bene_Age_65_74_Cnt",
    "Bene_Age_75_84_Cnt",
    "Bene_Age_GT_84_Cnt",

    "Bene_Feml_Cnt",
    "Bene_Male_Cnt",
    "Bene_Dual_Cnt",
    "Bene_Ndual_Cnt",

    "previous_year",

    "provider_years_observed",
    "provider_history_span_years",
    "segment_year_count",

    "longitudinal_years_observed",
    "longitudinal_first_year",
    "longitudinal_last_year",
}


# ============================================================
# LOAD CSV
# ============================================================

print("=" * 80)
print("DIAGNOSE BIGINT VALUES IN PROVIDER + ACO DATASET")
print("=" * 80)

print(f"\nCSV:")
print(CSV_FILE)

if not CSV_FILE.exists():
    raise FileNotFoundError(
        f"CSV not found:\n{CSV_FILE}"
    )

print("\nLoading CSV...")

df = pd.read_csv(
    CSV_FILE,
    low_memory=False
)

print(f"[OK] Rows:    {len(df):,}")
print(f"[OK] Columns: {len(df.columns):,}")


# ============================================================
# CHECK BIGINT COLUMNS
# ============================================================

print("\n" + "=" * 80)
print("CHECKING BIGINT COLUMNS")
print("=" * 80)

found_problem = False

for column in BIGINT_COLUMNS:

    if column not in df.columns:
        print(f"\n[WARNING] Missing expected BIGINT column: {column}")
        continue

    series = df[column]

    # Convert to numeric where possible.
    numeric = pd.to_numeric(
        series,
        errors="coerce"
    )

    # Values that are non-null but not whole numbers.
    non_integer_mask = (
        numeric.notna()
        &
        ((numeric % 1) != 0)
    )

    non_integer_count = int(
        non_integer_mask.sum()
    )

    # Detect values represented as floats such as 0.0.
    float_like_count = int(
        series.astype(str)
        .str.match(r"^-?\d+\.0+$")
        .sum()
    )

    print(f"\n{column}")
    print(f"  Pandas dtype:       {series.dtype}")
    print(f"  Non-null values:    {series.notna().sum():,}")
    print(f"  Float-like values:  {float_like_count:,}")
    print(f"  Non-integer values: {non_integer_count:,}")

    if float_like_count > 0:

        found_problem = True

        examples = (
            series[
                series.astype(str)
                .str.match(r"^-?\d+\.0+$")
            ]
            .drop_duplicates()
            .head(10)
            .tolist()
        )

        print(
            f"  [FOUND] Examples: {examples}"
        )

    if non_integer_count > 0:

        found_problem = True

        examples = (
            numeric[non_integer_mask]
            .drop_duplicates()
            .head(10)
            .tolist()
        )

        print(
            f"  [ERROR] Non-integer examples: {examples}"
        )


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("DIAGNOSTIC SUMMARY")
print("=" * 80)

if found_problem:

    print(
        "\n[WARNING] BIGINT columns contain float-style values."
    )

    print(
        "\nThis is safe to fix during CSV → Supabase conversion "
        "when the values are whole numbers such as 0.0, 1.0, 2.0."
    )

    print(
        "\nDo NOT change the PostgreSQL schema."
    )

else:

    print(
    "\nBIGINT columns should contain only whole-number values."
   )

print(
    "\nDecimal-valued service-count columns are intentionally "
    "excluded from BIGINT validation and should be stored as "
    "DOUBLE PRECISION in PostgreSQL."
    )

print("\n" + "=" * 80)