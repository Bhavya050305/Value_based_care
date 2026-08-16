from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_aco_features.csv"
)


# ============================================================
# HEADER
# ============================================================

print("=" * 90)
print("PROVIDER + ACO DASHBOARD FEATURE READINESS AUDIT")
print("=" * 90)

print("\nInput file:")
print(INPUT_FILE)


# ============================================================
# CHECK FILE
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nInput file not found:\n{INPUT_FILE}"
    )

print("\n✓ Input file found.")


# ============================================================
# LOAD HEADER ONLY
# ============================================================

df = pd.read_csv(
    INPUT_FILE,
    nrows=0,
    low_memory=False
)

columns = df.columns.tolist()

print("\nTotal columns:")
print(len(columns))


# ============================================================
# DASHBOARD REQUIREMENTS
# ============================================================

requirements = {

    "IDENTITY": [
        "Rndrng_NPI",
        "Rndrng_Prvdr_Last_Org_Name",
        "Rndrng_Prvdr_First_Name",
        "Rndrng_Prvdr_City",
        "Rndrng_Prvdr_State_Abrvtn",
        "Rndrng_Prvdr_Zip5",
        "Rndrng_Prvdr_Type",
    ],

    "TIME": [
        "Year",
    ],

    "ACO": [
        "ACO_ID",
    ],

    "SCALE": [
        "Tot_Benes",
        "Tot_Srvcs",
        "Tot_HCPCS_Cds",
    ],

    "COST": [
        "Tot_Mdcr_Pymt_Amt",
        "Tot_Mdcr_Alowd_Amt",
        "Tot_Mdcr_Stdzd_Amt",
    ],

    "RISK": [
        "Bene_Avg_Risk_Scre",
    ],

    "UTILIZATION_FEATURES": [
        "service_intensity_per_beneficiary",
        "hcpcs_intensity_per_beneficiary",
        "services_per_condition_burden",
        "services_per_risk_score",
    ],

    "COST_FEATURES": [
        "payment_per_beneficiary",
        "payment_per_service",
        "payment_efficiency",
        "standardized_payment_ratio",
        "payment_vs_standardized_pct",
    ],

    "RISK_ADJUSTED_FEATURES": [
        "risk_adjusted_services",
        "risk_adjusted_payment",
        "risk_adjusted_allowed",
    ],

    "CONDITION_ADJUSTED_FEATURES": [
        "condition_adjusted_services",
        "condition_adjusted_payment",
    ],

    "PERFORMANCE": [
        "utilization_score",
        "cost_score",
        "provider_segment",
    ],

    "LONGITUDINAL": [
        "dominant_provider_segment",
        "segment_stability",
        "history_class",
        "years_observed",
        "first_year",
        "last_year",
        "overall_provider_segment",
    ],

    "TEMPORAL": [
        "performance_payment_trend",
        "performance_service_trend",
        "performance_beneficiary_trend",
        "performance_payment_per_service_trend",
        "performance_risk_trend",
    ],

    "MEDICAL_DRUG": [
        "drug_data_suppressed",
        "medical_payment_share",
        "drug_payment_share",
        "medical_service_share_stage4",
        "drug_service_share_stage4",
    ],

}


# ============================================================
# ALIASES
# ============================================================

# Some projects use slightly different capitalization/naming.
# This allows the audit to detect close variations.

normalized_columns = {
    str(column).strip().lower(): column
    for column in columns
}


def find_actual_column(expected):
    """
    Try exact match first, then case-insensitive match.
    """

    if expected in columns:
        return expected

    return normalized_columns.get(
        expected.strip().lower()
    )


# ============================================================
# AUDIT
# ============================================================

print("\n" + "-" * 90)
print("DASHBOARD FEATURE CHECK")
print("-" * 90)

total_required = 0
total_found = 0
total_missing = 0


for category, required_columns in requirements.items():

    print(f"\n[{category}]")

    for expected_column in required_columns:

        total_required += 1

        actual_column = find_actual_column(
            expected_column
        )

        if actual_column is not None:

            print(
                f"  ✓ {expected_column}"
            )

            total_found += 1

        else:

            print(
                f"  ✗ MISSING: {expected_column}"
            )

            total_missing += 1


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 90)
print("AUDIT SUMMARY")
print("=" * 90)

print(
    f"\nDataset columns:       {len(columns):,}"
)

print(
    f"Required features:     {total_required:,}"
)

print(
    f"Features found:        {total_found:,}"
)

print(
    f"Features missing:      {total_missing:,}"
)


coverage = (
    total_found / total_required * 100
    if total_required > 0
    else 0
)

print(
    f"Dashboard coverage:    {coverage:.2f}%"
)


# ============================================================
# KEY STRUCTURAL CHECKS
# ============================================================

print("\n" + "-" * 90)
print("STRUCTURAL CHECKS")
print("-" * 90)


structural_columns = [
    "Rndrng_NPI",
    "Year",
    "ACO_ID",
]

for column in structural_columns:

    actual = find_actual_column(column)

    if actual:

        print(
            f"✓ Structural column present: {actual}"
        )

    else:

        print(
            f"✗ CRITICAL STRUCTURAL COLUMN MISSING: {column}"
        )


# ============================================================
# PRINT ALL COLUMNS
# ============================================================

print("\n" + "-" * 90)
print("ALL DATASET COLUMNS")
print("-" * 90)

for index, column in enumerate(
    columns,
    start=1
):

    print(
        f"{index:03d}. {column}"
    )


# ============================================================
# FINAL INTERPRETATION
# ============================================================

print("\n" + "=" * 90)
print("FINAL INTERPRETATION")
print("=" * 90)

if total_missing == 0:

    print(
        "\n✓ ALL CHECKED DASHBOARD FEATURES ARE PRESENT."
    )

    print(
        "\nThe dataset is structurally ready for the "
        "next validation stage before Supabase upload."
    )

else:

    print(
        f"\n⚠ {total_missing} CHECKED FEATURES ARE MISSING."
    )

    print(
        "\nDo NOT upload blindly yet."
    )

    print(
        "We need to determine whether the missing features:"
    )

    print(
        "1. exist under a different name,"
    )

    print(
        "2. are stored in another existing analytical file,"
    )

    print(
        "3. need to be merged into the final feature dataset,"
    )

    print(
        "4. or are intentionally not required."
    )


print("\n" + "=" * 90)