import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path("data/raw/mssp")
INTERIM_DIR = Path("data/interim")

INTERIM_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    2020: "Performance_Year_Financial_and_Quality_Results_2020_suppress.csv",
    2021: "Performance_Year_Financial_and_Quality_Results_2021_suppress.csv",
    2022: "Performance_Year_Financial_and_Quality_Results_PUF_2022_01_01.csv",
    2023: "PY 2023 ACO Results PUF.csv",
    2024: "PY_Financial_and_Quality_Results_2024_revised 2026_07_17.csv",
}


def load_year(year, filename):
    path = RAW_DIR / filename

    print(f"\nLoading {year}: {filename}")

    df = pd.read_csv(
        path,
        na_values=["-", ""],
        keep_default_na=True,
        low_memory=False
    )

    df["performance_year"] = year

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    return df


frames = []

for year, filename in FILES.items():
    df = load_year(year, filename)
    frames.append(df)

mssp = pd.concat(frames, ignore_index=True, sort=False)

print("\nCombined MSSP:")
print("Rows:", len(mssp))
print("Columns:", len(mssp.columns))

# --------------------------------------------------
# Standardize important identifier columns
# --------------------------------------------------

if "ACO_ID" in mssp.columns:
    mssp["ACO_ID"] = mssp["ACO_ID"].astype("string").str.strip()

if "ACO_Name" in mssp.columns:
    mssp["ACO_Name"] = mssp["ACO_Name"].astype("string").str.strip()

if "ACO_State" in mssp.columns:
    mssp["ACO_State"] = (
        mssp["ACO_State"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

# --------------------------------------------------
# Convert important numeric fields
# --------------------------------------------------


"""numeric_columns = [
    "N_AB",
    "BnchmkMinExp",
    "ABtotExp",
    "GenSaveLoss",
    "EarnSaveLoss",
    "QualScore",
    "Sav_rate",
    "MinSavPerc",
    "ABtotBnchmk",
    "DisAdj",
    "UpdatedBnchmk",
    "HistBnchmk",
]"""
for col in mssp.columns:

    # Skip obvious identifier/text columns
    if col in ["ACO_ID", "ACO_Name", "performance_year"]:
        continue

    # Convert to string temporarily
    cleaned = (
        mssp[col]
        .astype("string")
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
    )

    # Try converting to numeric
    numeric = pd.to_numeric(cleaned, errors="coerce")

    # Calculate how many non-empty values can be converted
    original_non_null = cleaned.notna().sum()
    numeric_non_null = numeric.notna().sum()

    # If almost all populated values are numeric,
     # treat the column as numeric
    if original_non_null > 0 and numeric_non_null / original_non_null >= 0.90:
        mssp[col] = numeric
"""for col in numeric_columns:
    if col in mssp.columns:
        mssp[col] = (
            mssp[col]
            .astype("string")
            .str.replace(",", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.strip()
        )

        mssp[col] = pd.to_numeric(
            mssp[col],
            errors="coerce"
        )"""



# --------------------------------------------------
# Check duplicate ACO-year records
# --------------------------------------------------

duplicates = mssp.duplicated(
    subset=["ACO_ID", "performance_year"]
).sum()

print("\nDuplicate ACO-year rows:", duplicates)
# --------------------------------------------------
# Missing Value Analysis
# --------------------------------------------------

print("\nMissing Value Analysis:")

missing_report = pd.DataFrame({
    "column": mssp.columns,
    "missing_count": mssp.isna().sum(),
    "missing_percentage": (
        mssp.isna().mean() * 100
    ).round(2)
})

# Number of available values
missing_report["non_missing_count"] = (
    len(mssp) - missing_report["missing_count"]
)


# --------------------------------------------------
# Classify missingness
# --------------------------------------------------

def classify_missingness(percent):

    if percent == 0:
        return "Complete"

    elif percent <= 20:
        return "Low"

    elif percent <= 50:
        return "Moderate"

    elif percent <= 90:
        return "High"

    else:
        return "Very High"


missing_report["missing_category"] = (
    missing_report["missing_percentage"]
    .apply(classify_missingness)
)


# --------------------------------------------------
# Show highest missing columns
# --------------------------------------------------

print("\nTop 20 columns by missing percentage:")

print(
    missing_report
    .sort_values(
        "missing_percentage",
        ascending=False
    )
    .head(20)
    .to_string(index=False)
)


# --------------------------------------------------
# Missingness Summary
# --------------------------------------------------

print("\nMissingness Summary:")

print(
    missing_report["missing_category"]
    .value_counts()
)


# --------------------------------------------------
# Save Missing Value Report
# --------------------------------------------------

missing_report = missing_report.sort_values(
    "missing_percentage",
    ascending=False
)

missing_report.to_csv(
    INTERIM_DIR / "mssp_missing_value_report.csv",
    index=False
)

print(
    "\nMissing value report saved:",
    INTERIM_DIR / "mssp_missing_value_report.csv"
)

# --------------------------------------------------
# Save intermediate combined data
# --------------------------------------------------
# Defragment DataFrame before saving
"""mssp = mssp.copy()

mssp.to_parquet(output, index=False)
output = INTERIM_DIR / "fact_aco_performance_raw_combined.parquet"

mssp.to_parquet(output, index=False)

print(f"\nSaved: {output}")"""
# --------------------------------------------------
# Save intermediate combined data
# --------------------------------------------------

output = INTERIM_DIR / "fact_aco_performance_raw_combined.parquet"

# Defragment DataFrame before saving
mssp = mssp.copy()

mssp.to_parquet(output, index=False)

print(f"\nSaved: {output}")