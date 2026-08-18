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
    / "provider_dashboard_analytics.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "aco_provider_metrics.csv"
)


# ============================================================
# 2. START
# ============================================================

print("=" * 70)
print("ACO PROVIDER METRICS")
print("=" * 70)

print(f"Input file: {INPUT_FILE}")


# ============================================================
# 3. CHECK INPUT
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found:\n{INPUT_FILE}"
    )


# ============================================================
# 4. LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print(f"Rows loaded: {len(df):,}")
print(f"Columns loaded: {len(df.columns):,}")


# ============================================================
# 5. REQUIRED COLUMNS
# ============================================================

required_columns = [

    "Rndrng_NPI",
    "Year",
    "ACO_ID",

    # Utilization
    "services_per_beneficiary",
    "service_intensity_per_beneficiary",
    "hcpcs_intensity_per_beneficiary",
    "risk_adjusted_services",
    "condition_adjusted_services",
    "utilization_score",

    # Cost
    "payment_per_service",
    "payment_per_beneficiary",
    "risk_adjusted_payment",
    "condition_adjusted_payment",
    "cost_score",

    # Efficiency
    "payment_efficiency",
    "standardized_payment_ratio",
    "payment_to_charge_ratio",
    "allowed_to_charge_ratio",
    "payment_vs_standardized_pct",

    # Provider flags
    "high_utilization_flag",
    "high_cost_flag",

    # Provider profile
    "cost_utilization_profile",
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    print()
    print("ERROR: Missing columns:")

    for column in missing_columns:
        print("-", column)

    raise ValueError(
        "Required columns are missing."
    )


print("Required column check: PASSED")


# ============================================================
# 6. PROVIDER-YEAR GRAIN CHECK
# ============================================================

duplicate_count = df.duplicated(
    ["Rndrng_NPI", "Year"]
).sum()


if duplicate_count != 0:

    raise ValueError(
        f"Duplicate Provider-Year records: "
        f"{duplicate_count}"
    )


print("Provider-Year grain check: PASSED")


# ============================================================
# 7. ACO-YEAR AGGREGATION
# ============================================================

aco_metrics = (
    df.groupby(
        ["ACO_ID", "Year"],
        as_index=False
    )
    .agg(

        # ----------------------------------------------------
        # Provider count
        # ----------------------------------------------------

        provider_count=(
            "Rndrng_NPI",
            "nunique"
        ),

        # ----------------------------------------------------
        # Utilization
        # ----------------------------------------------------

        avg_services_per_beneficiary=(
            "services_per_beneficiary",
            "mean"
        ),

        median_services_per_beneficiary=(
            "services_per_beneficiary",
            "median"
        ),

        avg_service_intensity_per_beneficiary=(
            "service_intensity_per_beneficiary",
            "mean"
        ),

        avg_hcpcs_intensity_per_beneficiary=(
            "hcpcs_intensity_per_beneficiary",
            "mean"
        ),

        avg_risk_adjusted_services=(
            "risk_adjusted_services",
            "mean"
        ),

        avg_condition_adjusted_services=(
            "condition_adjusted_services",
            "mean"
        ),

        avg_utilization_score=(
            "utilization_score",
            "mean"
        ),

        median_utilization_score=(
            "utilization_score",
            "median"
        ),

        # ----------------------------------------------------
        # Cost
        # ----------------------------------------------------

        avg_payment_per_service=(
            "payment_per_service",
            "mean"
        ),

        median_payment_per_service=(
            "payment_per_service",
            "median"
        ),

        avg_payment_per_beneficiary=(
            "payment_per_beneficiary",
            "mean"
        ),

        median_payment_per_beneficiary=(
            "payment_per_beneficiary",
            "median"
        ),

        avg_risk_adjusted_payment=(
            "risk_adjusted_payment",
            "mean"
        ),

        avg_condition_adjusted_payment=(
            "condition_adjusted_payment",
            "mean"
        ),

        avg_cost_score=(
            "cost_score",
            "mean"
        ),

        median_cost_score=(
            "cost_score",
            "median"
        ),

        # ----------------------------------------------------
        # Efficiency
        # ----------------------------------------------------

        avg_payment_efficiency=(
            "payment_efficiency",
            "mean"
        ),

        avg_standardized_payment_ratio=(
            "standardized_payment_ratio",
            "mean"
        ),

        avg_payment_to_charge_ratio=(
            "payment_to_charge_ratio",
            "mean"
        ),

        avg_allowed_to_charge_ratio=(
            "allowed_to_charge_ratio",
            "mean"
        ),

        avg_payment_vs_standardized_pct=(
            "payment_vs_standardized_pct",
            "mean"
        ),

        # ----------------------------------------------------
        # Provider composition
        # ----------------------------------------------------

        high_utilization_provider_count=(
            "high_utilization_flag",
            "sum"
        ),

        high_cost_provider_count=(
            "high_cost_flag",
            "sum"
        ),

        high_cost_high_utilization_count=(
            "cost_utilization_profile",
            lambda x: (
                x == "High Cost / High Utilization"
            ).sum()
        ),

        high_cost_low_utilization_count=(
            "cost_utilization_profile",
            lambda x: (
                x == "High Cost / Low Utilization"
            ).sum()
        ),

        low_cost_high_utilization_count=(
            "cost_utilization_profile",
            lambda x: (
                x == "Low Cost / High Utilization"
            ).sum()
        ),

        low_cost_low_utilization_count=(
            "cost_utilization_profile",
            lambda x: (
                x == "Low Cost / Low Utilization"
            ).sum()
        ),
    )
)


# ============================================================
# 8. PROVIDER PERCENTAGES
# ============================================================

aco_metrics["high_utilization_provider_pct"] = (
    aco_metrics["high_utilization_provider_count"]
    / aco_metrics["provider_count"]
    * 100
)

aco_metrics["high_cost_provider_pct"] = (
    aco_metrics["high_cost_provider_count"]
    / aco_metrics["provider_count"]
    * 100
)

aco_metrics["high_cost_high_utilization_pct"] = (
    aco_metrics["high_cost_high_utilization_count"]
    / aco_metrics["provider_count"]
    * 100
)

aco_metrics["high_cost_low_utilization_pct"] = (
    aco_metrics["high_cost_low_utilization_count"]
    / aco_metrics["provider_count"]
    * 100
)

aco_metrics["low_cost_high_utilization_pct"] = (
    aco_metrics["low_cost_high_utilization_count"]
    / aco_metrics["provider_count"]
    * 100
)

aco_metrics["low_cost_low_utilization_pct"] = (
    aco_metrics["low_cost_low_utilization_count"]
    / aco_metrics["provider_count"]
    * 100
)


# ============================================================
# 9. ACO RANKINGS
# ============================================================

aco_metrics["cost_rank"] = (
    aco_metrics
    .groupby("Year")["avg_cost_score"]
    .rank(
        ascending=False,
        method="min"
    )
)

aco_metrics["utilization_rank"] = (
    aco_metrics
    .groupby("Year")["avg_utilization_score"]
    .rank(
        ascending=False,
        method="min"
    )
)

aco_metrics["efficiency_rank"] = (
    aco_metrics
    .groupby("Year")["avg_payment_efficiency"]
    .rank(
        ascending=False,
        method="min"
    )
)


# ============================================================
# 10. VALIDATION
# ============================================================

expected_rows = (
    df["ACO_ID"].nunique()
    * df["Year"].nunique()
)

actual_rows = len(aco_metrics)

print()
print("Expected ACO-Year rows:", expected_rows)
print("Actual ACO-Year rows:", actual_rows)


if actual_rows != expected_rows:

    print(
        "WARNING: Some ACO-Year combinations may be missing."
    )


duplicate_aco_year = aco_metrics.duplicated(
    ["ACO_ID", "Year"]
).sum()


if duplicate_aco_year != 0:

    raise ValueError(
        "Duplicate ACO-Year rows detected."
    )


# ============================================================
# 11. SAVE
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

aco_metrics.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 12. FINAL REPORT
# ============================================================

print()
print("=" * 70)
print("ACO PROVIDER METRICS CREATED")
print("=" * 70)

print(f"Output file: {OUTPUT_FILE}")

print(f"Rows: {len(aco_metrics):,}")

print(f"Columns: {len(aco_metrics.columns):,}")

print(
    "Unique ACOs:",
    aco_metrics["ACO_ID"].nunique()
)

print(
    "Years:",
    sorted(aco_metrics["Year"].unique())
)

print(
    "Duplicate ACO-Year:",
    aco_metrics.duplicated(
        ["ACO_ID", "Year"]
    ).sum()
)


print()
print("=" * 70)
print("ACO PROVIDER COUNTS")
print("=" * 70)

print(
    aco_metrics[
        [
            "ACO_ID",
            "Year",
            "provider_count"
        ]
    ]
    .to_string(index=False)
)


print()
print("=" * 70)
print("DONE")
print("=" * 70)