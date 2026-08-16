"""
============================================================
PROVIDER FEATURE DEFINITION VALIDATION
============================================================

Purpose:
    Validate Stage 4 engineered ratio/share features against
    their raw source columns before performing outlier treatment.

IMPORTANT:
    This script DOES NOT modify Stage 4.
    This script DOES NOT remove rows.
    This script DOES NOT cap values.
    This script DOES NOT winsorize values.

It only checks whether the Stage 4 feature definitions are
mathematically consistent with the underlying raw columns.
============================================================
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_PATH = (
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
    / "provider_service"
    / "outlier_diagnostics"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "feature_definition_validation.csv"


# ============================================================
# CONFIGURATION
# ============================================================

TOLERANCE = 1e-8


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_divide(numerator, denominator):
    """
    Divide numerator by denominator.

    Returns NaN when denominator is zero.
    This preserves the distinction between:
        - no denominator/activity
        - a real calculated ratio
    """
    numerator = pd.to_numeric(numerator, errors="coerce")
    denominator = pd.to_numeric(denominator, errors="coerce")

    return numerator.div(
        denominator.replace(0, np.nan)
    )


def compare_feature(df, feature_name, expected_values):
    """
    Compare an existing engineered feature with an independently
    calculated expected value.
    """

    actual = pd.to_numeric(df[feature_name], errors="coerce")
    expected = pd.to_numeric(expected_values, errors="coerce")

    valid = actual.notna() & expected.notna()

    if valid.sum() == 0:
        return {
            "feature": feature_name,
            "valid_rows": 0,
            "matching_rows": 0,
            "mismatch_rows": 0,
            "mismatch_pct": np.nan,
            "max_absolute_difference": np.nan,
            "mean_absolute_difference": np.nan,
            "status": "NO_VALID_ROWS",
        }

    difference = (actual[valid] - expected[valid]).abs()

    mismatch = difference > TOLERANCE

    mismatch_count = int(mismatch.sum())
    valid_count = int(valid.sum())

    return {
        "feature": feature_name,
        "valid_rows": valid_count,
        "matching_rows": valid_count - mismatch_count,
        "mismatch_rows": mismatch_count,
        "mismatch_pct": round(
            mismatch_count / valid_count * 100,
            4,
        ),
        "max_absolute_difference": round(
            float(difference.max()),
            10,
        ),
        "mean_absolute_difference": round(
            float(difference.mean()),
            10,
        ),
        "status": (
            "PASSED"
            if mismatch_count == 0
            else "DEFINITION_MISMATCH"
        ),
    }


def range_check(df, feature_name, lower=0, upper=1):
    """
    Check whether a ratio/share feature stays within
    its expected mathematical range.
    """

    values = pd.to_numeric(df[feature_name], errors="coerce")

    below = int((values < lower).sum())
    above = int((values > upper).sum())

    return {
        "feature": feature_name,
        "expected_range": f"{lower} to {upper}",
        "below_range": below,
        "above_range": above,
        "minimum": values.min(),
        "maximum": values.max(),
    }


# ============================================================
# HEADER
# ============================================================

print("=" * 60)
print("PROVIDER FEATURE DEFINITION VALIDATION")
print("STAGE 4 RATIO / SHARE FORMULA INSPECTION")
print("=" * 60)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading Stage 4 dataset...")

if not INPUT_PATH.exists():
    raise FileNotFoundError(
        f"Stage 4 dataset not found:\n{INPUT_PATH}"
    )

df = pd.read_csv(
    INPUT_PATH,
    low_memory=False,
)

print(f"Rows loaded: {len(df):,}")
print(f"Columns loaded: {len(df.columns)}")


# ============================================================
# BASIC VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("BASIC VALIDATION")
print("=" * 60)

required_columns = [
    "Rndrng_NPI",
    "Year",

    # Raw totals
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_HCPCS_Cds",
    "Tot_Sbmtd_Chrg",
    "Tot_Mdcr_Alowd_Amt",
    "Tot_Mdcr_Pymt_Amt",
    "Tot_Mdcr_Stdzd_Amt",

    # Medical totals
    "Med_Tot_Benes",
    "Med_Tot_Srvcs",
    "Med_Tot_HCPCS_Cds",
    "Med_Sbmtd_Chrg",
    "Med_Mdcr_Alowd_Amt",
    "Med_Mdcr_Pymt_Amt",
    "Med_Mdcr_Stdzd_Amt",

    # Drug totals
    "Drug_Tot_Benes",
    "Drug_Tot_Srvcs",
    "Drug_Tot_HCPCS_Cds",
    "Drug_Sbmtd_Chrg",
    "Drug_Mdcr_Alowd_Amt",
    "Drug_Mdcr_Pymt_Amt",
    "Drug_Mdcr_Stdzd_Amt",

    # Stage 4 features
    "standardized_payment_ratio",
    "payment_to_charge_ratio",
    "allowed_to_charge_ratio",
    "medical_payment_share",
    "drug_payment_share",
    "medical_service_share_stage4",
    "drug_service_share_stage4",
]

missing_columns = [
    col
    for col in required_columns
    if col not in df.columns
]

if missing_columns:
    print("Required columns: FAILED")
    print("Missing columns:")

    for col in missing_columns:
        print(f"- {col}")

    raise ValueError(
        "Required columns are missing."
    )

print("Required columns: PASSED")


# ============================================================
# GRAIN VALIDATION
# ============================================================

duplicate_count = df.duplicated(
    subset=["Rndrng_NPI", "Year"]
).sum()

print(f"Duplicate NPI-Year rows: {duplicate_count}")

if duplicate_count == 0:
    print("NPI + Year grain: PASSED")
else:
    print("NPI + Year grain: FAILED")


# ============================================================
# FORMULA VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("FORMULA VALIDATION")
print("=" * 60)

results = []


# ------------------------------------------------------------
# 1. STANDARDIZED PAYMENT RATIO
# ------------------------------------------------------------

print("\n1. standardized_payment_ratio")

print(
    "Testing:"
    "\n  Tot_Mdcr_Stdzd_Amt / Tot_Mdcr_Pymt_Amt"
)

expected_standardized_ratio = safe_divide(
    df["Tot_Mdcr_Stdzd_Amt"],
    df["Tot_Mdcr_Pymt_Amt"],
)

result = compare_feature(
    df,
    "standardized_payment_ratio",
    expected_standardized_ratio,
)

results.append(result)

print(f"Valid rows: {result['valid_rows']:,}")
print(f"Mismatch rows: {result['mismatch_rows']:,}")
print(f"Mismatch %: {result['mismatch_pct']}%")
print(f"Status: {result['status']}")


# ------------------------------------------------------------
# 2. PAYMENT TO CHARGE RATIO
# ------------------------------------------------------------

print("\n2. payment_to_charge_ratio")

print(
    "Testing:"
    "\n  Tot_Mdcr_Pymt_Amt / Tot_Sbmtd_Chrg"
)

expected_payment_charge_ratio = safe_divide(
    df["Tot_Mdcr_Pymt_Amt"],
    df["Tot_Sbmtd_Chrg"],
)

result = compare_feature(
    df,
    "payment_to_charge_ratio",
    expected_payment_charge_ratio,
)

results.append(result)

print(f"Valid rows: {result['valid_rows']:,}")
print(f"Mismatch rows: {result['mismatch_rows']:,}")
print(f"Mismatch %: {result['mismatch_pct']}%")
print(f"Status: {result['status']}")


# ------------------------------------------------------------
# 3. ALLOWED TO CHARGE RATIO
# ------------------------------------------------------------

print("\n3. allowed_to_charge_ratio")

print(
    "Testing:"
    "\n  Tot_Mdcr_Alowd_Amt / Tot_Sbmtd_Chrg"
)

expected_allowed_charge_ratio = safe_divide(
    df["Tot_Mdcr_Alowd_Amt"],
    df["Tot_Sbmtd_Chrg"],
)

result = compare_feature(
    df,
    "allowed_to_charge_ratio",
    expected_allowed_charge_ratio,
)

results.append(result)

print(f"Valid rows: {result['valid_rows']:,}")
print(f"Mismatch rows: {result['mismatch_rows']:,}")
print(f"Mismatch %: {result['mismatch_pct']}%")
print(f"Status: {result['status']}")


# ------------------------------------------------------------
# 4. MEDICAL PAYMENT SHARE
# ------------------------------------------------------------

print("\n4. medical_payment_share")

print(
    "Testing:"
    "\n  Med_Mdcr_Pymt_Amt / Tot_Mdcr_Pymt_Amt"
)

expected_medical_payment_share = safe_divide(
    df["Med_Mdcr_Pymt_Amt"],
    df["Tot_Mdcr_Pymt_Amt"],
)

result = compare_feature(
    df,
    "medical_payment_share",
    expected_medical_payment_share,
)

results.append(result)

print(f"Valid rows: {result['valid_rows']:,}")
print(f"Mismatch rows: {result['mismatch_rows']:,}")
print(f"Mismatch %: {result['mismatch_pct']}%")
print(f"Status: {result['status']}")


# ------------------------------------------------------------
# 5. DRUG PAYMENT SHARE
# ------------------------------------------------------------

print("\n5. drug_payment_share")

print(
    "Testing:"
    "\n  Drug_Mdcr_Pymt_Amt / Tot_Mdcr_Pymt_Amt"
)

expected_drug_payment_share = safe_divide(
    df["Drug_Mdcr_Pymt_Amt"],
    df["Tot_Mdcr_Pymt_Amt"],
)

result = compare_feature(
    df,
    "drug_payment_share",
    expected_drug_payment_share,
)

results.append(result)

print(f"Valid rows: {result['valid_rows']:,}")
print(f"Mismatch rows: {result['mismatch_rows']:,}")
print(f"Mismatch %: {result['mismatch_pct']}%")
print(f"Status: {result['status']}")


# ------------------------------------------------------------
# 6. MEDICAL SERVICE SHARE
# ------------------------------------------------------------

print("\n6. medical_service_share_stage4")

print(
    "Testing:"
    "\n  Med_Tot_Srvcs / Tot_Srvcs"
)

expected_medical_service_share = safe_divide(
    df["Med_Tot_Srvcs"],
    df["Tot_Srvcs"],
)

result = compare_feature(
    df,
    "medical_service_share_stage4",
    expected_medical_service_share,
)

results.append(result)

print(f"Valid rows: {result['valid_rows']:,}")
print(f"Mismatch rows: {result['mismatch_rows']:,}")
print(f"Mismatch %: {result['mismatch_pct']}%")
print(f"Status: {result['status']}")


# ------------------------------------------------------------
# 7. DRUG SERVICE SHARE
# ------------------------------------------------------------

print("\n7. drug_service_share_stage4")

print(
    "Testing:"
    "\n  Drug_Tot_Srvcs / Tot_Srvcs"
)

expected_drug_service_share = safe_divide(
    df["Drug_Tot_Srvcs"],
    df["Tot_Srvcs"],
)

result = compare_feature(
    df,
    "drug_service_share_stage4",
    expected_drug_service_share,
)

results.append(result)

print(f"Valid rows: {result['valid_rows']:,}")
print(f"Mismatch rows: {result['mismatch_rows']:,}")
print(f"Mismatch %: {result['mismatch_pct']}%")
print(f"Status: {result['status']}")


# ============================================================
# RANGE DIAGNOSTICS
# ============================================================

print("\n" + "=" * 60)
print("RATIO / SHARE RANGE VALIDATION")
print("=" * 60)

range_results = []

range_features = [
    "standardized_payment_ratio",
    "payment_to_charge_ratio",
    "allowed_to_charge_ratio",
    "medical_payment_share",
    "drug_payment_share",
    "medical_service_share_stage4",
    "drug_service_share_stage4",
]

for feature in range_features:

    result = range_check(
        df,
        feature,
        lower=0,
        upper=1,
    )

    range_results.append(result)

    print(f"\n{feature}")
    print("Expected range: 0 to 1")
    print(f"Below range: {result['below_range']:,}")
    print(f"Above range: {result['above_range']:,}")
    print(
        f"Minimum: {result['minimum']:.6f}"
        if pd.notna(result["minimum"])
        else "Minimum: NaN"
    )
    print(
        f"Maximum: {result['maximum']:.6f}"
        if pd.notna(result["maximum"])
        else "Maximum: NaN"
    )


# ============================================================
# RAW COMPONENT CONSISTENCY
# ============================================================

print("\n" + "=" * 60)
print("RAW COMPONENT CONSISTENCY")
print("=" * 60)


# ------------------------------------------------------------
# MEDICAL + DRUG PAYMENT
# ------------------------------------------------------------

print("\nMedical + Drug payment compared with total payment")

payment_difference = (
    df["Med_Mdcr_Pymt_Amt"]
    + df["Drug_Mdcr_Pymt_Amt"]
    - df["Tot_Mdcr_Pymt_Amt"]
)

valid_payment = payment_difference.notna()

payment_mismatch = (
    payment_difference[valid_payment].abs()
    > TOLERANCE
)

print(
    f"Valid rows: {valid_payment.sum():,}"
)

print(
    f"Rows where Medical + Drug != Total: "
    f"{payment_mismatch.sum():,}"
)

print(
    f"Maximum absolute difference: "
    f"{payment_difference.abs().max():.6f}"
)


# ------------------------------------------------------------
# MEDICAL + DRUG SERVICES
# ------------------------------------------------------------

print("\nMedical + Drug services compared with total services")

service_difference = (
    df["Med_Tot_Srvcs"]
    + df["Drug_Tot_Srvcs"]
    - df["Tot_Srvcs"]
)

valid_service = service_difference.notna()

service_mismatch = (
    service_difference[valid_service].abs()
    > TOLERANCE
)

print(
    f"Valid rows: {valid_service.sum():,}"
)

print(
    f"Rows where Medical + Drug != Total: "
    f"{service_mismatch.sum():,}"
)

print(
    f"Maximum absolute difference: "
    f"{service_difference.abs().max():.6f}"
)


# ============================================================
# SUSPICIOUS MEDICAL SHARE RECORDS
# ============================================================

print("\n" + "=" * 60)
print("SUSPICIOUS MEDICAL SHARE RECORDS")
print("=" * 60)

medical_payment_problem = df[
    (
        df["medical_payment_share"] > 1
    )
    |
    (
        df["medical_payment_share"] < 0
    )
]

print(
    f"Medical payment share outside 0-1: "
    f"{len(medical_payment_problem):,}"
)

if len(medical_payment_problem) > 0:

    columns = [
        "Rndrng_NPI",
        "Year",
        "Tot_Mdcr_Pymt_Amt",
        "Med_Mdcr_Pymt_Amt",
        "Drug_Mdcr_Pymt_Amt",
        "medical_payment_share",
    ]

    print(
        "\nTop 10 suspicious medical payment share records:"
    )

    print(
        medical_payment_problem[
            columns
        ]
        .sort_values(
            "medical_payment_share",
            ascending=False,
        )
        .head(10)
        .to_string(index=False)
    )


# ============================================================
# SUSPICIOUS MEDICAL SERVICE RECORDS
# ============================================================

print("\n" + "=" * 60)
print("SUSPICIOUS MEDICAL SERVICE SHARE RECORDS")
print("=" * 60)

medical_service_problem = df[
    (
        df["medical_service_share_stage4"] > 1
    )
    |
    (
        df["medical_service_share_stage4"] < 0
    )
]

print(
    f"Medical service share outside 0-1: "
    f"{len(medical_service_problem):,}"
)

if len(medical_service_problem) > 0:

    columns = [
        "Rndrng_NPI",
        "Year",
        "Tot_Srvcs",
        "Med_Tot_Srvcs",
        "Drug_Tot_Srvcs",
        "medical_service_share_stage4",
    ]

    print(
        "\nTop 10 suspicious medical service share records:"
    )

    print(
        medical_service_problem[
            columns
        ]
        .sort_values(
            "medical_service_share_stage4",
            ascending=False,
        )
        .head(10)
        .to_string(index=False)
    )


# ============================================================
# SUSPICIOUS STANDARDIZED PAYMENT RATIO
# ============================================================

print("\n" + "=" * 60)
print("SUSPICIOUS STANDARDIZED PAYMENT RATIO RECORDS")
print("=" * 60)

standardized_problem = df[
    df["standardized_payment_ratio"] > 1
]

print(
    f"Standardized payment ratio > 1: "
    f"{len(standardized_problem):,}"
)

if len(standardized_problem) > 0:

    columns = [
        "Rndrng_NPI",
        "Year",
        "Tot_Mdcr_Pymt_Amt",
        "Tot_Mdcr_Stdzd_Amt",
        "standardized_payment_ratio",
    ]

    print(
        "\nTop 10 standardized payment ratio records:"
    )

    print(
        standardized_problem[
            columns
        ]
        .sort_values(
            "standardized_payment_ratio",
            ascending=False,
        )
        .head(10)
        .to_string(index=False)
    )


# ============================================================
# OVERALL RESULTS
# ============================================================

print("\n" + "=" * 60)
print("FEATURE DEFINITION VALIDATION SUMMARY")
print("=" * 60)

results_df = pd.DataFrame(results)

print(
    results_df[
        [
            "feature",
            "valid_rows",
            "mismatch_rows",
            "mismatch_pct",
            "status",
        ]
    ].to_string(index=False)
)


# ============================================================
# SAVE RESULTS
# ============================================================

results_df.to_csv(
    OUTPUT_PATH,
    index=False,
)

print("\n" + "=" * 60)
print("VALIDATION RESULTS SAVED")
print("=" * 60)

print(
    f"Output path: {OUTPUT_PATH}"
)


# ============================================================
# FINAL STATUS
# ============================================================

definition_failures = (
    results_df["status"]
    == "DEFINITION_MISMATCH"
).sum()

print("\n" + "=" * 60)
print("FINAL VALIDATION STATUS")
print("=" * 60)

if definition_failures == 0:
    print(
        "RESULT: All tested feature definitions "
        "match their raw-column formulas."
    )
else:
    print(
        f"RESULT: {definition_failures} feature definition(s) "
        "require investigation."
    )

print("\nIMPORTANT:")
print("This script DOES NOT modify Stage 4.")
print("This script DOES NOT remove rows.")
print("This script DOES NOT cap values.")
print("This script DOES NOT winsorize values.")
print("This script only validates feature definitions.")

print("\nNEXT STEP:")
print(
    "Review the formula-validation output before "
    "performing any outlier treatment."
)

print("=" * 60)