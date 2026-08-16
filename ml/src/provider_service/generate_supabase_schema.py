from pathlib import Path
import re
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "bhavya_provider_aco_features_final.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "database"
    / "provider_service_features_schema.sql"
)

# IMPORTANT:
# This must exactly match the Supabase table we created.
TABLE_NAME = "bhavya_provider_aco_features_final"


# ============================================================
# LOAD CSV
# ============================================================

print("=" * 80)
print("GENERATING SUPABASE TABLE SCHEMA")
print("=" * 80)

print(f"\nInput:")
print(INPUT_FILE)

print(f"\nOutput:")
print(OUTPUT_FILE)

print(f"\nTarget Supabase table:")
print(TABLE_NAME)


if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"CSV not found:\n{INPUT_FILE}"
    )


# Read only enough rows to determine column names and pandas types.
df = pd.read_csv(
    INPUT_FILE,
    nrows=1000,
    low_memory=False
)

print(f"\nColumns detected: {len(df.columns)}")


# ============================================================
# POSTGRES TYPE MAPPING
# ============================================================

integer_columns = {
    # Original CMS/provider fields
    "Rndrng_NPI",
    "Year",

    "Tot_HCPCS_Cds",
    "Tot_Benes",
    "Tot_Srvcs",

    "Drug_Tot_HCPCS_Cds",
    "Drug_Tot_Benes",
    "Drug_Tot_Srvcs",

    "Med_Tot_HCPCS_Cds",
    "Med_Tot_Benes",
    "Med_Tot_Srvcs",

    "Bene_Age_LT_65_Cnt",
    "Bene_Age_65_74_Cnt",
    "Bene_Age_75_84_Cnt",
    "Bene_Age_GT_84_Cnt",

    "Bene_Feml_Cnt",
    "Bene_Male_Cnt",
    "Bene_Dual_Cnt",
    "Bene_Ndual_Cnt",

    # Longitudinal integer features
    "provider_years_observed",
    "provider_history_span_years",

    "segment_year_count",

    "longitudinal_years_observed",
    "longitudinal_first_year",
    "longitudinal_last_year",

    "previous_year",
}


# ============================================================
# BOOLEAN COLUMNS
# ============================================================

boolean_columns = {
    "drug_data_suppressed",

    "complete_5_year_history",
    "is_first_provider_year",
    "is_last_provider_year",

    # IMPORTANT:
    # Diagnostic showed true/false values in this column.
    "consecutive_year",

    "high_utilization_flag",
    "high_cost_flag",
    "low_utilization_flag",
    "low_cost_flag",
}


# ============================================================
# TEXT COLUMNS
# ============================================================

text_columns = {
    "Rndrng_Prvdr_Last_Org_Name",
    "Rndrng_Prvdr_First_Name",
    "Rndrng_Prvdr_City",
    "Rndrng_Prvdr_State_Abrvtn",
    "Rndrng_Prvdr_RUCA_Desc",
    "Rndrng_Prvdr_Type",

    "provider_name",

    "ACO_ID",

    "provider_segment",
    "dominant_provider_segment",
    "overall_provider_segment",
    "history_class",
}


# ============================================================
# COLUMN NAME CLEANING
# ============================================================

def clean_column_name(column):
    """
    Convert CSV column names into safe PostgreSQL identifiers.

    Examples:

        Rndrng_NPI
        -> rndrng_npi

        ACO_ID
        -> aco_id

        medical_payment_per_service.1
        -> medical_payment_per_service_1

        payment%
        -> payment_pct
    """

    original = str(column).strip()

    column = original.lower()

    # Percent sign
    column = column.replace("%", "_pct")

    # Convert every non-alphanumeric character to underscore.
    column = re.sub(
        r"[^a-z0-9_]",
        "_",
        column
    )

    # Collapse repeated underscores
    column = re.sub(
        r"_+",
        "_",
        column
    )

    # Remove leading/trailing underscores
    column = column.strip("_")

    if not column:
        raise ValueError(
            f"Column name became empty after cleaning: {original!r}"
        )

    # PostgreSQL identifier safety
    if column[0].isdigit():
        column = f"col_{column}"

    return column


# ============================================================
# POSTGRES TYPE DETECTION
# ============================================================

def postgres_type(column):

    # Explicit integer mappings
    if column in integer_columns:
        return "BIGINT"

    # Explicit boolean mappings
    if column in boolean_columns:
        return "BOOLEAN"

    # Explicit text mappings
    if column in text_columns:
        return "TEXT"

    # Everything else:
    # numeric -> DOUBLE PRECISION
    if pd.api.types.is_numeric_dtype(df[column]):
        return "DOUBLE PRECISION"

    # String/categorical -> TEXT
    return "TEXT"


# ============================================================
# BUILD SQL
# ============================================================

sql_lines = []

sql_lines.append(
    f"DROP TABLE IF EXISTS {TABLE_NAME};"
)

sql_lines.append("")

sql_lines.append(
    f"CREATE TABLE {TABLE_NAME} ("
)

# Internal database ID
sql_lines.append(
    "    id BIGSERIAL PRIMARY KEY,"
)


# ============================================================
# BUILD COLUMN MAPPING
# ============================================================

used_names = set()

column_mapping = []


for column in df.columns:

    clean_name = clean_column_name(column)

    original_clean_name = clean_name

    counter = 1

    # Protect against collisions after cleaning.
    while clean_name in used_names:

        counter += 1

        clean_name = (
            f"{original_clean_name}_{counter}"
        )

    used_names.add(clean_name)

    pg_type = postgres_type(column)

    column_mapping.append(
        {
            "original": column,
            "postgres": clean_name,
            "type": pg_type,
        }
    )

    sql_lines.append(
        f"    {clean_name} {pg_type},"
    )


# Remove comma from last feature column.
sql_lines[-1] = sql_lines[-1].rstrip(",")

sql_lines.append(");")

sql_lines.append("")


# ============================================================
# INDEXES
# ============================================================

sql_lines.append(
    f"CREATE INDEX idx_bhavya_provider_npi "
    f"ON {TABLE_NAME} (rndrng_npi);"
)

sql_lines.append("")

sql_lines.append(
    f"CREATE INDEX idx_bhavya_provider_year "
    f"ON {TABLE_NAME} (year);"
)

sql_lines.append("")

sql_lines.append(
    f"CREATE INDEX idx_bhavya_provider_aco "
    f"ON {TABLE_NAME} (aco_id);"
)

sql_lines.append("")

sql_lines.append(
    f"CREATE INDEX idx_bhavya_provider_npi_year "
    f"ON {TABLE_NAME} (rndrng_npi, year);"
)


# ============================================================
# SAVE SQL
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE.write_text(
    "\n".join(sql_lines),
    encoding="utf-8"
)


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "-" * 80)
print("SCHEMA VALIDATION")
print("-" * 80)

print(
    f"CSV columns:              {len(df.columns)}"
)

print(
    f"Generated table columns:  {len(column_mapping)}"
)


if len(df.columns) == len(column_mapping):

    print("✓ Column count preserved.")

else:

    raise ValueError(
        "Column count mismatch between CSV and generated schema."
    )


# ============================================================
# DUPLICATE POSTGRES COLUMN CHECK
# ============================================================

postgres_names = [
    item["postgres"]
    for item in column_mapping
]

duplicate_pg_names = (
    pd.Series(postgres_names)
    .value_counts()
)

duplicate_pg_names = duplicate_pg_names[
    duplicate_pg_names > 1
]


if len(duplicate_pg_names) == 0:

    print(
        "✓ No duplicate PostgreSQL column names."
    )

else:

    print(
        "✗ Duplicate PostgreSQL names detected:"
    )

    print(
        duplicate_pg_names
    )

    raise ValueError(
        "Duplicate PostgreSQL column names detected."
    )


# ============================================================
# DOT CHECK
# ============================================================

dot_names = [
    item["postgres"]
    for item in column_mapping
    if "." in item["postgres"]
]


if len(dot_names) == 0:

    print(
        "✓ No '.' characters in PostgreSQL column names."
    )

else:

    raise ValueError(
        f"Invalid '.' characters found: {dot_names}"
    )


# ============================================================
# CRITICAL COLUMN VALIDATION
# ============================================================

mapping_dict = {
    item["original"]: item
    for item in column_mapping
}


print("\nCritical type mappings:")

critical_columns = {
    "Rndrng_NPI": "BIGINT",
    "Year": "BIGINT",
    "ACO_ID": "TEXT",
    "consecutive_year": "BOOLEAN",
    "complete_5_year_history": "BOOLEAN",
    "high_utilization_flag": "BOOLEAN",
    "high_cost_flag": "BOOLEAN",
    "low_utilization_flag": "BOOLEAN",
    "low_cost_flag": "BOOLEAN",
    "drug_data_suppressed": "BOOLEAN",
    "provider_segment": "TEXT",
    "overall_provider_segment": "TEXT",
    "history_class": "TEXT",
}


for column, expected_type in critical_columns.items():

    if column not in mapping_dict:

        raise ValueError(
            f"Critical column missing from CSV: {column}"
        )

    actual_type = mapping_dict[column]["type"]

    postgres_name = mapping_dict[column]["postgres"]

    print(
        f"  {column}"
        f" -> "
        f"{postgres_name}"
        f" ({actual_type})"
    )

    if actual_type != expected_type:

        raise ValueError(
            f"Type mismatch for {column}: "
            f"expected {expected_type}, "
            f"got {actual_type}"
        )


# ============================================================
# IMPORTANT RENAMED COLUMNS
# ============================================================

print("\nImportant column mappings:")

important_columns = {
    "medical_payment_per_service.1",
    "medical_allowed_per_service.1",
    "medical_payment_per_beneficiary.1",
}


for item in column_mapping:

    if item["original"] in important_columns:

        print(
            f"  {item['original']}"
            f" -> "
            f"{item['postgres']}"
            f" ({item['type']})"
        )


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n" + "=" * 80)
print("SUPABASE TABLE SCHEMA GENERATED SUCCESSFULLY")
print("=" * 80)

print(
    f"\nSQL file:\n{OUTPUT_FILE}"
)

print(
    f"\nTable name:\n{TABLE_NAME}"
)

print(
    "\nIndexes:"
    "\n- rndrng_npi"
    "\n- year"
    "\n- aco_id"
    "\n- rndrng_npi + year"
)

print(
    "\nDataset:"
    "\n- 150,000 provider-year rows"
    "\n- 195 feature columns"
    "\n- Synthetic ACO_ID included"
    "\n- Provider performance features included"
    "\n- Longitudinal features included"
)

print("\n" + "=" * 80)