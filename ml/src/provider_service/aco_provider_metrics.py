from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "serving"
    / "all_aco"
    / "all_aco_provider_selection.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "all_aco"
    / "aco_provider_metrics.csv"
)

REQUIRED_COLUMNS = [
    "ACO_ID",
    "Year",
    "Rndrng_NPI",
    "provider_rank",
    "selection_score",
    "Tot_Srvcs",
    "Tot_Benes",
    "Avg_Mdcr_Pymt_Amt",
    "cost_score",
    "utilization_score",
]


def safe_mean(series):
    return series.mean()


def safe_sum(series):
    return series.sum()


print("=" * 80)
print("BHAVYA VBC")
print("ALL-ACO PROVIDER METRICS")
print("=" * 80)

print("\nChecking input file...")
if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

print(f"OK  {INPUT_FILE}")

print("\n[1/6] LOADING SELECTED PROVIDERS")
df = pd.read_csv(INPUT_FILE, low_memory=False)

print(f"Rows              : {len(df):,}")
print(f"Columns           : {len(df.columns)}")
print(f"Unique ACOs       : {df['ACO_ID'].nunique():,}")
print(f"Unique providers  : {df['Rndrng_NPI'].nunique():,}")
print(f"Years             : {sorted(df['Year'].unique())}")

print("\n[2/6] VALIDATING REQUIRED COLUMNS")

missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]

if missing:
    raise ValueError(f"Missing required columns: {missing}")

print("PASS - All required columns are present.")

print("\n[3/6] VALIDATING PROVIDER-YEAR GRAIN")

duplicates = df.duplicated(
    ["ACO_ID", "Rndrng_NPI", "Year"]
).sum()

print(f"Duplicate ACO-NPI-Year rows: {duplicates}")

if duplicates != 0:
    raise ValueError("Duplicate ACO-NPI-Year rows detected.")

provider_counts = (
    df.groupby(["ACO_ID", "Year"])["Rndrng_NPI"]
    .nunique()
)

print(
    "Providers per ACO-year distribution:"
)
print(provider_counts.value_counts().sort_index())

if not (provider_counts == 5).all():
    raise ValueError(
        "Not every ACO-year has exactly 5 selected providers."
    )

print("PASS - Every ACO-year has exactly 5 providers.")

print("\n[4/6] BUILDING ACO-LEVEL METRICS")

grouped = df.groupby(["ACO_ID", "Year"], as_index=False)

aco = grouped.agg(
    provider_count=("Rndrng_NPI", "nunique"),
    total_services=("Tot_Srvcs", "sum"),
    total_beneficiaries=("Tot_Benes", "sum"),
    avg_provider_payment=("Avg_Mdcr_Pymt_Amt", "mean"),
    avg_cost_score=("cost_score", "mean"),
    avg_utilization_score=("utilization_score", "mean"),
    avg_selection_score=("selection_score", "mean"),
    avg_provider_rank=("provider_rank", "mean"),
    max_provider_cost_score=("cost_score", "max"),
    max_provider_utilization_score=("utilization_score", "max"),
)
# ============================================================
# PROVIDER PERFORMANCE PERCENTAGES
# ============================================================
#
# These percentages are calculated from the selected providers
# within each ACO-Year.
#
# High cost:
#     cost_score >= 0.70
#
# High utilization:
#     utilization_score >= 0.70
#
# High cost + high utilization:
#     both conditions are true.
#
# The denominator is the number of providers in each ACO-Year.
# ============================================================

df["high_cost_flag"] = (
    df["cost_score"] >= 0.70
)

df["high_utilization_flag"] = (
    df["utilization_score"] >= 0.70
)

df["high_cost_high_utilization_flag"] = (
    df["high_cost_flag"]
    & df["high_utilization_flag"]
)

provider_flags = (
    df.groupby(
        ["ACO_ID", "Year"],
        as_index=False
    )
    .agg(
        high_cost_provider_pct=(
            "high_cost_flag",
            "mean"
        ),
        high_utilization_provider_pct=(
            "high_utilization_flag",
            "mean"
        ),
        high_cost_high_utilization_pct=(
            "high_cost_high_utilization_flag",
            "mean"
        ),
    )
)

# Convert proportions to percentages
provider_flags[
    [
        "high_cost_provider_pct",
        "high_utilization_provider_pct",
        "high_cost_high_utilization_pct",
    ]
] *= 100

aco = aco.merge(
    provider_flags,
    on=["ACO_ID", "Year"],
    how="left",
)

# Provider-level concentration measures
provider_cost_top = (
    df.sort_values(
        ["ACO_ID", "Year", "cost_score"],
        ascending=[True, True, False],
    )
    .groupby(["ACO_ID", "Year"])
    .head(1)[
        ["ACO_ID", "Year", "Rndrng_NPI", "cost_score"]
    ]
    .rename(
        columns={
            "Rndrng_NPI": "top_cost_provider",
            "cost_score": "top_provider_cost_score",
        }
    )
)

provider_util_top = (
    df.sort_values(
        ["ACO_ID", "Year", "utilization_score"],
        ascending=[True, True, False],
    )
    .groupby(["ACO_ID", "Year"])
    .head(1)[
        ["ACO_ID", "Year", "Rndrng_NPI", "utilization_score"]
    ]
    .rename(
        columns={
            "Rndrng_NPI": "top_utilization_provider",
            "utilization_score": "top_provider_utilization_score",
        }
    )
)

aco = aco.merge(
    provider_cost_top,
    on=["ACO_ID", "Year"],
    how="left",
)

aco = aco.merge(
    provider_util_top,
    on=["ACO_ID", "Year"],
    how="left",
)

# Year-over-year changes
aco = aco.sort_values(["ACO_ID", "Year"]).reset_index(drop=True)

for column in [
    "total_services",
    "total_beneficiaries",
    "avg_provider_payment",
    "avg_cost_score",
    "avg_utilization_score",
]:
    aco[f"{column}_change_pct"] = (
        aco.groupby("ACO_ID")[column]
        .pct_change()
        .replace([np.inf, -np.inf], np.nan)
        * 100
    )

# Overall ACO performance score
aco["aco_performance_score"] = (
    0.40 * aco["avg_cost_score"]
    + 0.40 * aco["avg_utilization_score"]
    + 0.20 * aco["avg_selection_score"]
)

# Performance segment
def classify(row):
    score = row["aco_performance_score"]

    if score >= 0.80:
        return "HIGH_PERFORMANCE"
    elif score >= 0.60:
        return "MODERATE_PERFORMANCE"
    else:
        return "LOW_PERFORMANCE"


aco["aco_performance_segment"] = aco.apply(
    classify,
    axis=1,
)

print(f"ACO-year rows created: {len(aco):,}")

print("\n[5/6] FINAL VALIDATION")

expected_rows = 686 * 5

print(f"Expected ACO-year rows : {expected_rows:,}")
print(f"Actual ACO-year rows   : {len(aco):,}")

print(f"Unique ACOs            : {aco['ACO_ID'].nunique():,}")
print(f"Years                  : {sorted(aco['Year'].unique())}")

duplicates_final = aco.duplicated(
    ["ACO_ID", "Year"]
).sum()

print(f"ACO-Year duplicates    : {duplicates_final}")

missing_final = aco[
    ["ACO_ID", "Year"]
].isna().sum().sum()

print(f"Critical missing keys  : {missing_final}")

if len(aco) != expected_rows:
    raise ValueError(
        f"Expected {expected_rows} ACO-year rows, got {len(aco)}."
    )

if aco["ACO_ID"].nunique() != 686:
    raise ValueError(
        "Expected exactly 686 ACOs."
    )

if duplicates_final != 0:
    raise ValueError(
        "Duplicate ACO-Year rows detected."
    )

print("PASS - ACO metrics validation successful.")
required_final_columns = [
    "high_cost_provider_pct",
    "high_utilization_provider_pct",
    "high_cost_high_utilization_pct",
]

for column in required_final_columns:

    if column not in aco.columns:
        raise ValueError(
            f"Missing final ACO metric: {column}"
        )

    if aco[column].isna().any():
        raise ValueError(
            f"Missing values found in {column}"
        )

print("PASS - Provider performance percentages validated.")

print("\n[6/6] SAVING OUTPUT")

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

aco.to_csv(
    OUTPUT_FILE,
    index=False,
)

print(f"Output: {OUTPUT_FILE}")
print(f"Rows  : {len(aco):,}")
print(f"Cols  : {len(aco.columns)}")

print("\n" + "=" * 80)
print("BUILD COMPLETE")
print("=" * 80)
