from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PROVIDER RAW COMPONENT STRUCTURAL INVESTIGATION
# ============================================================
#
# PURPOSE
# -------
# Investigate the structural reason behind:
#
#   Medical + Drug != Total
#
# in the Stage 4 provider dataset.
#
# THIS SCRIPT IS DIAGNOSTIC ONLY.
#
# It does NOT:
#   - modify source data
#   - remove rows
#   - impute values
#   - winsorize values
#   - cap values
#   - perform outlier treatment
#
# Main questions:
#
# 1. Which provider types cause the mismatch?
# 2. Is mismatch associated with drug_data_suppressed?
# 3. Does mismatch vary by year?
# 4. Are component > total records concentrated in
#    particular provider types?
# 5. What happens when drug values are zero?
# 6. Are extreme payment/service values concentrated
#    in the mismatch population?
# 7. Which actual provider-year records are most unusual?
#
# ============================================================


# ============================================================
# 1. PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_features_stage4.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "diagnostics"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# Output files

STRUCTURAL_SUMMARY_FILE = (
    OUTPUT_DIR
    / "provider_component_structural_summary.csv"
)

PROVIDER_TYPE_FILE = (
    OUTPUT_DIR
    / "provider_component_by_provider_type.csv"
)

YEAR_FILE = (
    OUTPUT_DIR
    / "provider_component_by_year.csv"
)

SUPPRESSION_FILE = (
    OUTPUT_DIR
    / "provider_component_suppression_analysis.csv"
)

EXTREME_FILE = (
    OUTPUT_DIR
    / "provider_component_extreme_records.csv"
)

MISMATCH_SAMPLE_FILE = (
    OUTPUT_DIR
    / "provider_component_mismatch_sample.csv"
)


# ============================================================
# 2. SOURCE COLUMN DEFINITIONS
# ============================================================

NPI = "Rndrng_NPI"
YEAR = "Year"

PROVIDER_TYPE = "Rndrng_Prvdr_Type"

DRUG_SUPPRESSED = "drug_data_suppressed"


TOTAL_SERVICES = "Tot_Srvcs"
MEDICAL_SERVICES = "Med_Tot_Srvcs"
DRUG_SERVICES = "Drug_Tot_Srvcs"

TOTAL_PAYMENT = "Tot_Mdcr_Pymt_Amt"
MEDICAL_PAYMENT = "Med_Mdcr_Pymt_Amt"
DRUG_PAYMENT = "Drug_Mdcr_Pymt_Amt"

TOTAL_ALLOWED = "Tot_Mdcr_Alowd_Amt"
MEDICAL_ALLOWED = "Med_Mdcr_Alowd_Amt"
DRUG_ALLOWED = "Drug_Mdcr_Alowd_Amt"

TOTAL_CHARGE = "Tot_Sbmtd_Chrg"
MEDICAL_CHARGE = "Med_Sbmtd_Chrg"
DRUG_CHARGE = "Drug_Sbmtd_Chrg"

TOTAL_STANDARDIZED = "Tot_Mdcr_Stdzd_Amt"
MEDICAL_STANDARDIZED = "Med_Mdcr_Stdzd_Amt"
DRUG_STANDARDIZED = "Drug_Mdcr_Stdzd_Amt"

TOTAL_BENEFICIARIES = "Tot_Benes"
MEDICAL_BENEFICIARIES = "Med_Tot_Benes"
DRUG_BENEFICIARIES = "Drug_Tot_Benes"


# ============================================================
# 3. REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    NPI,
    YEAR,
    PROVIDER_TYPE,
    TOTAL_SERVICES,
    MEDICAL_SERVICES,
    DRUG_SERVICES,
    TOTAL_PAYMENT,
    MEDICAL_PAYMENT,
    DRUG_PAYMENT,
    TOTAL_ALLOWED,
    MEDICAL_ALLOWED,
    DRUG_ALLOWED,
    TOTAL_CHARGE,
    MEDICAL_CHARGE,
    DRUG_CHARGE,
    TOTAL_STANDARDIZED,
    MEDICAL_STANDARDIZED,
    DRUG_STANDARDIZED,
    TOTAL_BENEFICIARIES,
    MEDICAL_BENEFICIARIES,
    DRUG_BENEFICIARIES,
]


# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================

def header(title: str) -> None:

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def safe_divide(
    numerator: pd.Series,
    denominator: pd.Series,
) -> pd.Series:

    denominator = denominator.replace(
        0,
        np.nan,
    )

    return numerator / denominator


def to_numeric(
    df: pd.DataFrame,
    column: str,
) -> pd.Series:

    return pd.to_numeric(
        df[column],
        errors="coerce",
    )


# ============================================================
# 5. LOAD DATA
# ============================================================

header(
    "1. LOADING STAGE 4 DATA"
)

print(
    f"Project root : {PROJECT_ROOT}"
)

print(
    f"Input file   : {INPUT_FILE}"
)

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"\nInput file not found:\n{INPUT_FILE}"
    )


df = pd.read_csv(
    INPUT_FILE
)

print(
    f"Rows loaded    : {len(df):,}"
)

print(
    f"Columns loaded : {len(df.columns):,}"
)


# ============================================================
# 6. VALIDATE SCHEMA
# ============================================================

header(
    "2. SCHEMA VALIDATION"
)

missing = [
    column
    for column in REQUIRED_COLUMNS
    if column not in df.columns
]

if missing:

    print(
        "FAIL: Missing columns:"
    )

    for column in missing:

        print(
            f"  - {column}"
        )

    raise ValueError(
        "Structural investigation stopped "
        "because required columns are missing."
    )


print(
    f"PASS: All {len(REQUIRED_COLUMNS)} "
    f"required columns are present."
)


# ============================================================
# 7. CONVERT DIAGNOSTIC NUMERIC COPIES
# ============================================================

header(
    "3. PREPARING DIAGNOSTIC FIELDS"
)

numeric_columns = [
    TOTAL_SERVICES,
    MEDICAL_SERVICES,
    DRUG_SERVICES,

    TOTAL_PAYMENT,
    MEDICAL_PAYMENT,
    DRUG_PAYMENT,

    TOTAL_ALLOWED,
    MEDICAL_ALLOWED,
    DRUG_ALLOWED,

    TOTAL_CHARGE,
    MEDICAL_CHARGE,
    DRUG_CHARGE,

    TOTAL_STANDARDIZED,
    MEDICAL_STANDARDIZED,
    DRUG_STANDARDIZED,

    TOTAL_BENEFICIARIES,
    MEDICAL_BENEFICIARIES,
    DRUG_BENEFICIARIES,
]


for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    )


# ============================================================
# 8. CREATE RECONCILIATION DIFFERENCES
# ============================================================

header(
    "4. CALCULATING COMPONENT RECONCILIATIONS"
)


# -----------------------------
# Services
# -----------------------------

df["services_component_sum"] = (
    df[MEDICAL_SERVICES]
    + df[DRUG_SERVICES]
)

df["services_difference"] = (
    df["services_component_sum"]
    - df[TOTAL_SERVICES]
)

df["services_match"] = np.isclose(
    df["services_component_sum"],
    df[TOTAL_SERVICES],
    rtol=1e-9,
    atol=1e-6,
)

df["services_component_gt_total"] = (
    df["services_component_sum"]
    > df[TOTAL_SERVICES]
)


# -----------------------------
# Payment
# -----------------------------

df["payment_component_sum"] = (
    df[MEDICAL_PAYMENT]
    + df[DRUG_PAYMENT]
)

df["payment_difference"] = (
    df["payment_component_sum"]
    - df[TOTAL_PAYMENT]
)

df["payment_match"] = np.isclose(
    df["payment_component_sum"],
    df[TOTAL_PAYMENT],
    rtol=1e-9,
    atol=1e-6,
)

df["payment_component_gt_total"] = (
    df["payment_component_sum"]
    > df[TOTAL_PAYMENT]
)


# -----------------------------
# Allowed
# -----------------------------

df["allowed_component_sum"] = (
    df[MEDICAL_ALLOWED]
    + df[DRUG_ALLOWED]
)

df["allowed_difference"] = (
    df["allowed_component_sum"]
    - df[TOTAL_ALLOWED]
)

df["allowed_match"] = np.isclose(
    df["allowed_component_sum"],
    df[TOTAL_ALLOWED],
    rtol=1e-9,
    atol=1e-6,
)

df["allowed_component_gt_total"] = (
    df["allowed_component_sum"]
    > df[TOTAL_ALLOWED]
)


# -----------------------------
# Charges
# -----------------------------

df["charge_component_sum"] = (
    df[MEDICAL_CHARGE]
    + df[DRUG_CHARGE]
)

df["charge_difference"] = (
    df["charge_component_sum"]
    - df[TOTAL_CHARGE]
)

df["charge_match"] = np.isclose(
    df["charge_component_sum"],
    df[TOTAL_CHARGE],
    rtol=1e-9,
    atol=1e-6,
)

df["charge_component_gt_total"] = (
    df["charge_component_sum"]
    > df[TOTAL_CHARGE]
)


# -----------------------------
# Standardized amount
# -----------------------------

df["standardized_component_sum"] = (
    df[MEDICAL_STANDARDIZED]
    + df[DRUG_STANDARDIZED]
)

df["standardized_difference"] = (
    df["standardized_component_sum"]
    - df[TOTAL_STANDARDIZED]
)

df["standardized_match"] = np.isclose(
    df["standardized_component_sum"],
    df[TOTAL_STANDARDIZED],
    rtol=1e-9,
    atol=1e-6,
)

df["standardized_component_gt_total"] = (
    df["standardized_component_sum"]
    > df[TOTAL_STANDARDIZED]
)


# ============================================================
# 9. OVERALL STRUCTURAL CLASSIFICATION
# ============================================================

header(
    "5. OVERALL STRUCTURAL CLASSIFICATION"
)


df["any_reconciliation_mismatch"] = ~(
    df["services_match"]
    & df["payment_match"]
    & df["allowed_match"]
    & df["charge_match"]
    & df["standardized_match"]
)


df["any_component_gt_total"] = (
    df["services_component_gt_total"]
    | df["payment_component_gt_total"]
    | df["allowed_component_gt_total"]
    | df["charge_component_gt_total"]
    | df["standardized_component_gt_total"]
)


df["drug_all_zero"] = (
    (df[DRUG_SERVICES] == 0)
    & (df[DRUG_PAYMENT] == 0)
    & (df[DRUG_ALLOWED] == 0)
    & (df[DRUG_CHARGE] == 0)
    & (df[DRUG_STANDARDIZED] == 0)
)


df["medical_all_zero"] = (
    (df[MEDICAL_SERVICES] == 0)
    & (df[MEDICAL_PAYMENT] == 0)
    & (df[MEDICAL_ALLOWED] == 0)
    & (df[MEDICAL_CHARGE] == 0)
    & (df[MEDICAL_STANDARDIZED] == 0)
)


# ============================================================
# 10. OVERALL COUNTS
# ============================================================

total_rows = len(df)

mismatch_rows = int(
    df["any_reconciliation_mismatch"].sum()
)

component_gt_total_rows = int(
    df["any_component_gt_total"].sum()
)

drug_zero_rows = int(
    df["drug_all_zero"].sum()
)

medical_zero_rows = int(
    df["medical_all_zero"].sum()
)


print(
    f"Total rows                         : "
    f"{total_rows:,}"
)

print(
    f"Any reconciliation mismatch        : "
    f"{mismatch_rows:,} "
    f"({mismatch_rows / total_rows * 100:.4f}%)"
)

print(
    f"Any component > total              : "
    f"{component_gt_total_rows:,} "
    f"({component_gt_total_rows / total_rows * 100:.4f}%)"
)

print(
    f"All drug components zero           : "
    f"{drug_zero_rows:,} "
    f"({drug_zero_rows / total_rows * 100:.4f}%)"
)

print(
    f"All medical components zero        : "
    f"{medical_zero_rows:,} "
    f"({medical_zero_rows / total_rows * 100:.4f}%)"
)


# ============================================================
# 11. PROVIDER TYPE ANALYSIS
# ============================================================

header(
    "6. MISMATCH ANALYSIS BY PROVIDER TYPE"
)


provider_type_summary = (
    df
    .groupby(
        PROVIDER_TYPE,
        dropna=False,
    )
    .agg(
        total_rows=(
            NPI,
            "size",
        ),

        mismatch_rows=(
            "any_reconciliation_mismatch",
            "sum",
        ),

        component_gt_total_rows=(
            "any_component_gt_total",
            "sum",
        ),

        drug_zero_rows=(
            "drug_all_zero",
            "sum",
        ),

        medical_zero_rows=(
            "medical_all_zero",
            "sum",
        ),

        total_payment_median=(
            TOTAL_PAYMENT,
            "median",
        ),

        total_payment_max=(
            TOTAL_PAYMENT,
            "max",
        ),

        total_services_median=(
            TOTAL_SERVICES,
            "median",
        ),

        total_services_max=(
            TOTAL_SERVICES,
            "max",
        ),
    )
    .reset_index()
)


provider_type_summary[
    "mismatch_pct"
] = safe_divide(
    provider_type_summary[
        "mismatch_rows"
    ],
    provider_type_summary[
        "total_rows"
    ],
) * 100


provider_type_summary[
    "component_gt_total_pct"
] = safe_divide(
    provider_type_summary[
        "component_gt_total_rows"
    ],
    provider_type_summary[
        "total_rows"
    ],
) * 100


provider_type_summary[
    "drug_zero_pct"
] = safe_divide(
    provider_type_summary[
        "drug_zero_rows"
    ],
    provider_type_summary[
        "total_rows"
    ],
) * 100


provider_type_summary = (
    provider_type_summary
    .sort_values(
        "mismatch_pct",
        ascending=False,
    )
)


print(
    provider_type_summary
    .head(30)
    .to_string(
        index=False
    )
)


# ============================================================
# 12. YEAR ANALYSIS
# ============================================================

header(
    "7. MISMATCH ANALYSIS BY YEAR"
)


year_summary = (
    df
    .groupby(YEAR)
    .agg(
        total_rows=(
            NPI,
            "size",
        ),

        mismatch_rows=(
            "any_reconciliation_mismatch",
            "sum",
        ),

        component_gt_total_rows=(
            "any_component_gt_total",
            "sum",
        ),

        drug_zero_rows=(
            "drug_all_zero",
            "sum",
        ),

        median_total_payment=(
            TOTAL_PAYMENT,
            "median",
        ),

        max_total_payment=(
            TOTAL_PAYMENT,
            "max",
        ),

        median_total_services=(
            TOTAL_SERVICES,
            "median",
        ),

        max_total_services=(
            TOTAL_SERVICES,
            "max",
        ),
    )
    .reset_index()
)


year_summary[
    "mismatch_pct"
] = safe_divide(
    year_summary["mismatch_rows"],
    year_summary["total_rows"],
) * 100


year_summary[
    "component_gt_total_pct"
] = safe_divide(
    year_summary[
        "component_gt_total_rows"
    ],
    year_summary[
        "total_rows"
    ],
) * 100


year_summary[
    "drug_zero_pct"
] = safe_divide(
    year_summary["drug_zero_rows"],
    year_summary["total_rows"],
) * 100


print(
    year_summary.to_string(
        index=False
    )
)


# ============================================================
# 13. DRUG SUPPRESSION ANALYSIS
# ============================================================

header(
    "8. DRUG SUPPRESSION ANALYSIS"
)


if DRUG_SUPPRESSED in df.columns:

    print(
        "drug_data_suppressed values:"
    )

    print(
        df[DRUG_SUPPRESSED]
        .value_counts(
            dropna=False
        )
        .to_string()
    )


    suppression_summary = (
        df
        .groupby(
            DRUG_SUPPRESSED,
            dropna=False,
        )
        .agg(
            total_rows=(
                NPI,
                "size",
            ),

            mismatch_rows=(
                "any_reconciliation_mismatch",
                "sum",
            ),

            component_gt_total_rows=(
                "any_component_gt_total",
                "sum",
            ),

            drug_all_zero_rows=(
                "drug_all_zero",
                "sum",
            ),

            median_drug_payment=(
                DRUG_PAYMENT,
                "median",
            ),

            max_drug_payment=(
                DRUG_PAYMENT,
                "max",
            ),

            median_total_payment=(
                TOTAL_PAYMENT,
                "median",
            ),

            max_total_payment=(
                TOTAL_PAYMENT,
                "max",
            ),
        )
        .reset_index()
    )


    suppression_summary[
        "mismatch_pct"
    ] = safe_divide(
        suppression_summary[
            "mismatch_rows"
        ],
        suppression_summary[
            "total_rows"
        ],
    ) * 100


    suppression_summary[
        "component_gt_total_pct"
    ] = safe_divide(
        suppression_summary[
            "component_gt_total_rows"
        ],
        suppression_summary[
            "total_rows"
        ],
    ) * 100


    print(
        "\nSuppression analysis:"
    )

    print(
        suppression_summary
        .to_string(
            index=False
        )
    )

else:

    print(
        "WARNING: "
        "drug_data_suppressed column "
        "does not exist."
    )

    suppression_summary = pd.DataFrame()


# ============================================================
# 14. DRUG ZERO VS NON-ZERO ANALYSIS
# ============================================================

header(
    "9. DRUG ZERO VS NON-ZERO STRUCTURE"
)


drug_zero_summary = (
    df
    .groupby(
        "drug_all_zero"
    )
    .agg(
        total_rows=(
            NPI,
            "size",
        ),

        mismatch_rows=(
            "any_reconciliation_mismatch",
            "sum",
        ),

        component_gt_total_rows=(
            "any_component_gt_total",
            "sum",
        ),

        median_total_payment=(
            TOTAL_PAYMENT,
            "median",
        ),

        max_total_payment=(
            TOTAL_PAYMENT,
            "max",
        ),

        median_total_services=(
            TOTAL_SERVICES,
            "median",
        ),

        max_total_services=(
            TOTAL_SERVICES,
            "max",
        ),
    )
    .reset_index()
)


drug_zero_summary[
    "mismatch_pct"
] = safe_divide(
    drug_zero_summary[
        "mismatch_rows"
    ],
    drug_zero_summary[
        "total_rows"
    ],
) * 100


drug_zero_summary[
    "component_gt_total_pct"
] = safe_divide(
    drug_zero_summary[
        "component_gt_total_rows"
    ],
    drug_zero_summary[
        "total_rows"
    ],
) * 100


print(
    drug_zero_summary.to_string(
        index=False
    )
)


# ============================================================
# 15. INDIVIDUAL RECONCILIATION ANALYSIS
# ============================================================

header(
    "10. INDIVIDUAL RECONCILIATION ANALYSIS"
)


metrics = {
    "services": "services_match",
    "payment": "payment_match",
    "allowed": "allowed_match",
    "charge": "charge_match",
    "standardized": "standardized_match",
}


individual_records = []


for metric, match_column in metrics.items():

    mismatch = ~df[match_column]

    mismatch_count = int(
        mismatch.sum()
    )

    individual_records.append(
        {
            "metric": metric,
            "total_rows": total_rows,
            "matching_rows": int(
                df[match_column].sum()
            ),
            "mismatch_rows": mismatch_count,
            "mismatch_pct": (
                mismatch_count
                / total_rows
                * 100
            ),
        }
    )

    print(
        f"{metric:15s} "
        f"mismatch = "
        f"{mismatch_count:,} "
        f"({mismatch_count / total_rows * 100:.4f}%)"
    )


individual_summary = pd.DataFrame(
    individual_records
)


# ============================================================
# 16. COMBINED MISMATCH PATTERNS
# ============================================================

header(
    "11. COMBINED MISMATCH PATTERNS"
)


df["mismatch_pattern"] = (
    np.where(
        df["services_match"],
        "",
        "S",
    )
    + np.where(
        df["payment_match"],
        "",
        "P",
    )
    + np.where(
        df["allowed_match"],
        "",
        "A",
    )
    + np.where(
        df["charge_match"],
        "",
        "C",
    )
    + np.where(
        df["standardized_match"],
        "",
        "Z",
    )
)


pattern_summary = (
    df["mismatch_pattern"]
    .value_counts()
    .rename_axis(
        "mismatch_pattern"
    )
    .reset_index(
        name="rows"
    )
)


pattern_summary[
    "percentage"
] = (
    pattern_summary["rows"]
    / total_rows
    * 100
)


print(
    pattern_summary
    .head(20)
    .to_string(
        index=False
    )
)


# ============================================================
# 17. EXTREME PAYMENT / SERVICE ANALYSIS
# ============================================================

header(
    "12. EXTREME PAYMENT AND SERVICE ANALYSIS"
)

# Percentile thresholds are used ONLY for investigation.
# They are NOT being used to remove or modify observations.

payment_p99 = df[
    TOTAL_PAYMENT
].quantile(0.99)

payment_p999 = df[
    TOTAL_PAYMENT
].quantile(0.999)

services_p99 = df[
    TOTAL_SERVICES
].quantile(0.99)

services_p999 = df[
    TOTAL_SERVICES
].quantile(0.999)


df["payment_top_1pct"] = (
    df[TOTAL_PAYMENT]
    >= payment_p99
)

df["payment_top_01pct"] = (
    df[TOTAL_PAYMENT]
    >= payment_p999
)

df["services_top_1pct"] = (
    df[TOTAL_SERVICES]
    >= services_p99
)

df["services_top_01pct"] = (
    df[TOTAL_SERVICES]
    >= services_p999
)


print(
    f"Payment 99th percentile  : "
    f"{payment_p99:,.2f}"
)

print(
    f"Payment 99.9th percentile: "
    f"{payment_p999:,.2f}"
)

print(
    f"Services 99th percentile : "
    f"{services_p99:,.2f}"
)

print(
    f"Services 99.9th percentile: "
    f"{services_p999:,.2f}"
)


extreme_groups = {
    "payment_top_1pct": df[
        "payment_top_1pct"
    ],

    "payment_top_01pct": df[
        "payment_top_01pct"
    ],

    "services_top_1pct": df[
        "services_top_1pct"
    ],

    "services_top_01pct": df[
        "services_top_01pct"
    ],
}


extreme_records = []


for group_name, mask in extreme_groups.items():

    subset = df[mask]

    if subset.empty:

        continue

    extreme_records.append(
        {
            "group": group_name,
            "rows": len(subset),
            "mismatch_rows": int(
                subset[
                    "any_reconciliation_mismatch"
                ].sum()
            ),
            "mismatch_pct": (
                subset[
                    "any_reconciliation_mismatch"
                ].mean()
                * 100
            ),
            "component_gt_total_rows": int(
                subset[
                    "any_component_gt_total"
                ].sum()
            ),
            "component_gt_total_pct": (
                subset[
                    "any_component_gt_total"
                ].mean()
                * 100
            ),
            "drug_zero_rows": int(
                subset[
                    "drug_all_zero"
                ].sum()
            ),
            "drug_zero_pct": (
                subset[
                    "drug_all_zero"
                ].mean()
                * 100
            ),
            "median_payment": subset[
                TOTAL_PAYMENT
            ].median(),
            "max_payment": subset[
                TOTAL_PAYMENT
            ].max(),
            "median_services": subset[
                TOTAL_SERVICES
            ].median(),
            "max_services": subset[
                TOTAL_SERVICES
            ].max(),
        }
    )


extreme_summary = pd.DataFrame(
    extreme_records
)


print(
    extreme_summary.to_string(
        index=False
    )
)


# ============================================================
# 18. TOP EXTREME RECORDS
# ============================================================

header(
    "13. TOP EXTREME PROVIDER-YEAR RECORDS"
)


extreme_columns = [
    NPI,
    YEAR,
    PROVIDER_TYPE,

    TOTAL_SERVICES,
    MEDICAL_SERVICES,
    DRUG_SERVICES,

    TOTAL_PAYMENT,
    MEDICAL_PAYMENT,
    DRUG_PAYMENT,

    TOTAL_ALLOWED,
    MEDICAL_ALLOWED,
    DRUG_ALLOWED,

    TOTAL_STANDARDIZED,
    MEDICAL_STANDARDIZED,
    DRUG_STANDARDIZED,

    DRUG_SUPPRESSED,

    "drug_all_zero",
    "any_reconciliation_mismatch",
    "any_component_gt_total",

    "payment_difference",
    "services_difference",
]


extreme_columns = [
    column
    for column in extreme_columns
    if column in df.columns
]


top_payment = (
    df
    .sort_values(
        TOTAL_PAYMENT,
        ascending=False,
    )
    .head(100)
)


top_services = (
    df
    .sort_values(
        TOTAL_SERVICES,
        ascending=False,
    )
    .head(100)
)


combined_extreme = pd.concat(
    [
        top_payment,
        top_services,
    ],
    ignore_index=True,
)


combined_extreme = (
    combined_extreme
    .drop_duplicates(
        subset=[
            NPI,
            YEAR,
        ]
    )
)


print(
    combined_extreme[
        extreme_columns
    ]
    .head(50)
    .to_string(
        index=False
    )
)


# ============================================================
# 19. MISMATCH SAMPLE
# ============================================================

header(
    "14. MISMATCH PROVIDER-YEAR SAMPLE"
)


mismatch_df = df[
    df["any_reconciliation_mismatch"]
].copy()


print(
    f"Mismatch provider-year rows: "
    f"{len(mismatch_df):,}"
)


# Take a reproducible sample.
if len(mismatch_df) > 1000:

    mismatch_sample = (
        mismatch_df
        .sample(
            n=1000,
            random_state=42,
        )
    )

else:

    mismatch_sample = mismatch_df.copy()


mismatch_columns = [
    NPI,
    YEAR,
    PROVIDER_TYPE,

    DRUG_SUPPRESSED,

    TOTAL_SERVICES,
    MEDICAL_SERVICES,
    DRUG_SERVICES,
    "services_difference",

    TOTAL_PAYMENT,
    MEDICAL_PAYMENT,
    DRUG_PAYMENT,
    "payment_difference",

    TOTAL_ALLOWED,
    MEDICAL_ALLOWED,
    DRUG_ALLOWED,
    "allowed_difference",

    TOTAL_CHARGE,
    MEDICAL_CHARGE,
    DRUG_CHARGE,
    "charge_difference",

    TOTAL_STANDARDIZED,
    MEDICAL_STANDARDIZED,
    DRUG_STANDARDIZED,
    "standardized_difference",

    "drug_all_zero",
    "medical_all_zero",
]


mismatch_columns = [
    column
    for column in mismatch_columns
    if column in mismatch_sample.columns
]


print(
    mismatch_sample[
        mismatch_columns
    ]
    .head(30)
    .to_string(
        index=False
    )
)


# ============================================================
# 20. SAVE OUTPUTS
# ============================================================

header(
    "15. SAVING INVESTIGATION OUTPUTS"
)


# Structural summary

structural_summary = pd.DataFrame(
    [
        {
            "metric": "total_rows",
            "value": total_rows,
        },
        {
            "metric": "reconciliation_mismatch_rows",
            "value": mismatch_rows,
        },
        {
            "metric": "reconciliation_mismatch_pct",
            "value": (
                mismatch_rows
                / total_rows
                * 100
            ),
        },
        {
            "metric": "component_gt_total_rows",
            "value": component_gt_total_rows,
        },
        {
            "metric": "component_gt_total_pct",
            "value": (
                component_gt_total_rows
                / total_rows
                * 100
            ),
        },
        {
            "metric": "drug_all_zero_rows",
            "value": drug_zero_rows,
        },
        {
            "metric": "drug_all_zero_pct",
            "value": (
                drug_zero_rows
                / total_rows
                * 100
            ),
        },
        {
            "metric": "medical_all_zero_rows",
            "value": medical_zero_rows,
        },
        {
            "metric": "medical_all_zero_pct",
            "value": (
                medical_zero_rows
                / total_rows
                * 100
            ),
        },
    ]
)


structural_summary.to_csv(
    STRUCTURAL_SUMMARY_FILE,
    index=False,
)

provider_type_summary.to_csv(
    PROVIDER_TYPE_FILE,
    index=False,
)

year_summary.to_csv(
    YEAR_FILE,
    index=False,
)

if not suppression_summary.empty:

    suppression_summary.to_csv(
        SUPPRESSION_FILE,
        index=False,
    )

combined_extreme[
    extreme_columns
].to_csv(
    EXTREME_FILE,
    index=False,
)

mismatch_sample[
    mismatch_columns
].to_csv(
    MISMATCH_SAMPLE_FILE,
    index=False,
)


# ============================================================
# 21. FINAL REPORT
# ============================================================

header(
    "16. INVESTIGATION COMPLETE"
)

print(
    "\nIMPORTANT:"
)

print(
    "No source values were modified."
)

print(
    "No rows were removed."
)

print(
    "No outlier treatment was performed."
)

print(
    "Percentiles were used ONLY for investigation."
)

print(
    "\nOutput files:"
)

print(
    f"  {STRUCTURAL_SUMMARY_FILE}"
)

print(
    f"  {PROVIDER_TYPE_FILE}"
)

print(
    f"  {YEAR_FILE}"
)

if not suppression_summary.empty:

    print(
        f"  {SUPPRESSION_FILE}"
    )

print(
    f"  {EXTREME_FILE}"
)

print(
    f"  {MISMATCH_SAMPLE_FILE}"
)

print(
    "\nNEXT STEP:"
)

print(
    "Review provider type, year, suppression, "
    "and extreme-value patterns before deciding "
    "whether any observations require treatment."
)