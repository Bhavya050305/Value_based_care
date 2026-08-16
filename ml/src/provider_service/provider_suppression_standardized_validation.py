from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PROVIDER SUPPRESSION + STANDARDIZED PAYMENT VALIDATION
# ============================================================
#
# PURPOSE
# -------
# Investigate:
#
# 1. drug_data_suppressed semantics
# 2. Drug component zeros under suppression
# 3. Medical / drug shares under suppression
# 4. Standardized payment ratio definition
# 5. Whether standardized payment ratio is mathematically
#    consistent with the source fields
#
# IMPORTANT
# ---------
# THIS IS A DIAGNOSTIC SCRIPT ONLY.
#
# It does NOT:
#   - modify source data
#   - remove rows
#   - replace values
#   - cap values
#   - winsorize values
#   - perform outlier treatment
#   - overwrite Stage 4
#
# ============================================================


# ============================================================
# 1. PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SOURCE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_combined_clean.csv"
)

STAGE4_FILE = (
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


SUPPRESSION_SUMMARY_FILE = (
    OUTPUT_DIR
    / "provider_suppression_semantic_summary.csv"
)

SUPPRESSION_EXAMPLES_FILE = (
    OUTPUT_DIR
    / "provider_suppression_examples.csv"
)

STANDARDIZED_SUMMARY_FILE = (
    OUTPUT_DIR
    / "provider_standardized_payment_validation.csv"
)

STANDARDIZED_EXAMPLES_FILE = (
    OUTPUT_DIR
    / "provider_standardized_payment_examples.csv"
)

FEATURE_SEMANTIC_FILE = (
    OUTPUT_DIR
    / "provider_suppression_feature_semantics.csv"
)


# ============================================================
# 2. COLUMN NAMES
# ============================================================

NPI = "Rndrng_NPI"
YEAR = "Year"
PROVIDER_TYPE = "Rndrng_Prvdr_Type"

SUPPRESSED = "drug_data_suppressed"


TOTAL_SERVICES = "Tot_Srvcs"
MEDICAL_SERVICES = "Med_Tot_Srvcs"
DRUG_SERVICES = "Drug_Tot_Srvcs"

TOTAL_PAYMENT = "Tot_Mdcr_Pymt_Amt"
MEDICAL_PAYMENT = "Med_Mdcr_Pymt_Amt"
DRUG_PAYMENT = "Drug_Mdcr_Pymt_Amt"

TOTAL_ALLOWED = "Tot_Mdcr_Alowd_Amt"
MEDICAL_ALLOWED = "Med_Mdcr_Alowd_Amt"
DRUG_ALLOWED = "Drug_Mdcr_Alowd_Amt"

TOTAL_STANDARDIZED = "Tot_Mdcr_Stdzd_Amt"
MEDICAL_STANDARDIZED = "Med_Mdcr_Stdzd_Amt"
DRUG_STANDARDIZED = "Drug_Mdcr_Stdzd_Amt"

TOTAL_CHARGE = "Tot_Sbmtd_Chrg"
MEDICAL_CHARGE = "Med_Sbmtd_Chrg"
DRUG_CHARGE = "Drug_Sbmtd_Chrg"

STAGE4_STANDARDIZED_RATIO = (
    "standardized_payment_ratio"
)


# ============================================================
# 3. HELPERS
# ============================================================

def header(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def numeric(series):
    return pd.to_numeric(
        series,
        errors="coerce",
    )


def percentage(numerator, denominator):
    if denominator == 0:
        return 0.0

    return (
        numerator
        / denominator
        * 100.0
    )


def safe_ratio(numerator, denominator):
    denominator = denominator.replace(
        0,
        np.nan,
    )

    return numerator / denominator


# ============================================================
# 4. LOAD DATA
# ============================================================

header(
    "1. LOADING SOURCE AND STAGE 4"
)

print(
    f"Project root : {PROJECT_ROOT}"
)

print(
    f"Source       : {SOURCE_FILE}"
)

print(
    f"Stage 4      : {STAGE4_FILE}"
)


if not SOURCE_FILE.exists():

    raise FileNotFoundError(
        f"\nSource file not found:\n{SOURCE_FILE}"
    )


if not STAGE4_FILE.exists():

    raise FileNotFoundError(
        f"\nStage 4 file not found:\n{STAGE4_FILE}"
    )


source = pd.read_csv(
    SOURCE_FILE
)

stage4 = pd.read_csv(
    STAGE4_FILE
)


print(
    f"\nSource rows : {len(source):,}"
)

print(
    f"Stage 4 rows: {len(stage4):,}"
)


# ============================================================
# 5. REQUIRED COLUMN VALIDATION
# ============================================================

header(
    "2. REQUIRED COLUMN VALIDATION"
)


required_source_columns = [
    NPI,
    YEAR,
    PROVIDER_TYPE,
    SUPPRESSED,

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

    TOTAL_CHARGE,
    MEDICAL_CHARGE,
    DRUG_CHARGE,
]


missing_source = [
    column
    for column in required_source_columns
    if column not in source.columns
]


if missing_source:

    print(
        "Missing source columns:"
    )

    for column in missing_source:
        print(
            f"  - {column}"
        )

    raise ValueError(
        "Required source columns are missing."
    )


if STAGE4_STANDARDIZED_RATIO not in stage4.columns:

    raise ValueError(
        "standardized_payment_ratio is missing "
        "from Stage 4."
    )


print(
    "PASS: All required columns exist."
)


# ============================================================
# 6. SUPPRESSION DISTRIBUTION
# ============================================================

header(
    "3. DRUG SUPPRESSION DISTRIBUTION"
)


suppression_counts = (
    source[SUPPRESSED]
    .value_counts(
        dropna=False
    )
)


print(
    suppression_counts.to_string()
)


suppression_summary = (
    source
    .groupby(
        SUPPRESSED,
        dropna=False,
    )
    .size()
    .reset_index(
        name="rows"
    )
)


suppression_summary[
    "row_pct"
] = (
    suppression_summary["rows"]
    / len(source)
    * 100
)


print(
    "\nSuppression summary:"
)

print(
    suppression_summary.to_string(
        index=False
    )
)


# ============================================================
# 7. CHECK DRUG VALUES UNDER SUPPRESSION
# ============================================================

header(
    "4. DRUG VALUES UNDER SUPPRESSION"
)


drug_columns = [
    DRUG_SERVICES,
    DRUG_PAYMENT,
    DRUG_ALLOWED,
    DRUG_CHARGE,
    DRUG_STANDARDIZED,
]


drug_analysis_rows = []


for suppressed_value, group in source.groupby(
    SUPPRESSED,
    dropna=False,
):

    row = {
        SUPPRESSED: suppressed_value,
        "rows": len(group),
    }

    for column in drug_columns:

        values = numeric(
            group[column]
        )

        row[
            f"{column}_zero_rows"
        ] = int(
            values.eq(0).sum()
        )

        row[
            f"{column}_positive_rows"
        ] = int(
            values.gt(0).sum()
        )

        row[
            f"{column}_negative_rows"
        ] = int(
            values.lt(0).sum()
        )

        row[
            f"{column}_null_rows"
        ] = int(
            values.isna().sum()
        )

    drug_analysis_rows.append(
        row
    )


drug_analysis = pd.DataFrame(
    drug_analysis_rows
)


print(
    drug_analysis.to_string(
        index=False
    )
)


# ============================================================
# 8. CHECK WHETHER SUPPRESSED ROWS CAN RECONCILE
# ============================================================

header(
    "5. COMPONENT RECONCILIATION BY SUPPRESSION"
)


reconciliation_definitions = {
    "services": (
        TOTAL_SERVICES,
        MEDICAL_SERVICES,
        DRUG_SERVICES,
    ),

    "payment": (
        TOTAL_PAYMENT,
        MEDICAL_PAYMENT,
        DRUG_PAYMENT,
    ),

    "allowed": (
        TOTAL_ALLOWED,
        MEDICAL_ALLOWED,
        DRUG_ALLOWED,
    ),

    "charge": (
        TOTAL_CHARGE,
        MEDICAL_CHARGE,
        DRUG_CHARGE,
    ),

    "standardized": (
        TOTAL_STANDARDIZED,
        MEDICAL_STANDARDIZED,
        DRUG_STANDARDIZED,
    ),
}


reconciliation_rows = []


for suppressed_value, group in source.groupby(
    SUPPRESSED,
    dropna=False,
):

    for metric, columns in reconciliation_definitions.items():

        total = numeric(
            group[columns[0]]
        )

        medical = numeric(
            group[columns[1]]
        )

        drug = numeric(
            group[columns[2]]
        )

        component_sum = (
            medical + drug
        )

        valid = (
            total.notna()
            &
            component_sum.notna()
        )

        matches = np.isclose(
            total[valid],
            component_sum[valid],
            rtol=1e-9,
            atol=1e-8,
        )

        mismatch = ~matches

        component_gt_total = (
            component_sum[valid]
            > total[valid]
        )

        reconciliation_rows.append(
            {
                SUPPRESSED: suppressed_value,
                "metric": metric,
                "valid_rows": int(
                    valid.sum()
                ),
                "matching_rows": int(
                    matches.sum()
                ),
                "mismatch_rows": int(
                    mismatch.sum()
                ),
                "mismatch_pct": percentage(
                    int(mismatch.sum()),
                    int(valid.sum()),
                ),
                "component_gt_total_rows": int(
                    component_gt_total.sum()
                ),
            }
        )


reconciliation_summary = pd.DataFrame(
    reconciliation_rows
)


print(
    reconciliation_summary.to_string(
        index=False
    )
)


# ============================================================
# 9. DERIVED SHARE DIAGNOSTICS
# ============================================================

header(
    "6. MEDICAL / DRUG SHARE BEHAVIOR"
)


share_source = source.copy()


share_source[
    "__medical_service_share"
] = safe_ratio(
    numeric(
        share_source[MEDICAL_SERVICES]
    ),
    numeric(
        share_source[TOTAL_SERVICES]
    ),
)


share_source[
    "__drug_service_share"
] = safe_ratio(
    numeric(
        share_source[DRUG_SERVICES]
    ),
    numeric(
        share_source[TOTAL_SERVICES]
    ),
)


share_source[
    "__medical_payment_share"
] = safe_ratio(
    numeric(
        share_source[MEDICAL_PAYMENT]
    ),
    numeric(
        share_source[TOTAL_PAYMENT]
    ),
)


share_source[
    "__drug_payment_share"
] = safe_ratio(
    numeric(
        share_source[DRUG_PAYMENT]
    ),
    numeric(
        share_source[TOTAL_PAYMENT]
    ),
)


share_rows = []


share_definitions = {
    "medical_service_share":
        "__medical_service_share",

    "drug_service_share":
        "__drug_service_share",

    "medical_payment_share":
        "__medical_payment_share",

    "drug_payment_share":
        "__drug_payment_share",
}


for suppressed_value, group in share_source.groupby(
    SUPPRESSED,
    dropna=False,
):

    for name, column in share_definitions.items():

        values = group[column]

        valid = values.notna()

        greater_than_one = (
            values[valid] > 1
        )

        less_than_zero = (
            values[valid] < 0
        )

        share_rows.append(
            {
                SUPPRESSED: suppressed_value,
                "feature": name,
                "valid_rows": int(
                    valid.sum()
                ),
                "greater_than_1_rows": int(
                    greater_than_one.sum()
                ),
                "greater_than_1_pct": percentage(
                    int(greater_than_one.sum()),
                    int(valid.sum()),
                ),
                "less_than_0_rows": int(
                    less_than_zero.sum()
                ),
                "median": float(
                    values[valid].median()
                )
                if valid.any()
                else np.nan,
                "maximum": float(
                    values[valid].max()
                )
                if valid.any()
                else np.nan,
            }
        )


share_summary = pd.DataFrame(
    share_rows
)


print(
    share_summary.to_string(
        index=False
    )
)


# ============================================================
# 10. STANDARDIZED PAYMENT RATIO INVESTIGATION
# ============================================================

header(
    "7. STANDARDIZED PAYMENT RATIO INVESTIGATION"
)


total_payment = numeric(
    source[TOTAL_PAYMENT]
)

total_standardized = numeric(
    source[TOTAL_STANDARDIZED]
)

stage4_ratio = numeric(
    stage4[STAGE4_STANDARDIZED_RATIO]
)


source_expected_ratio = safe_ratio(
    total_payment,
    total_standardized,
)


stage4_ratio_comparison = pd.DataFrame(
    {
        NPI: stage4[NPI],
        YEAR: stage4[YEAR],

        "source_payment":
            total_payment.values,

        "source_standardized":
            total_standardized.values,

        "source_payment_over_standardized":
            source_expected_ratio.values,

        "stage4_standardized_payment_ratio":
            stage4_ratio.values,
    }
)


stage4_ratio_comparison[
    "__difference"
] = (
    stage4_ratio_comparison[
        "stage4_standardized_payment_ratio"
    ]
    -
    stage4_ratio_comparison[
        "source_payment_over_standardized"
    ]
).abs()


valid_ratio = (
    stage4_ratio_comparison[
        "source_payment_over_standardized"
    ].notna()
    &
    stage4_ratio_comparison[
        "stage4_standardized_payment_ratio"
    ].notna()
)


ratio_exact_matches = np.isclose(
    stage4_ratio_comparison.loc[
        valid_ratio,
        "source_payment_over_standardized",
    ],
    stage4_ratio_comparison.loc[
        valid_ratio,
        "stage4_standardized_payment_ratio",
    ],
    rtol=1e-9,
    atol=1e-8,
)


ratio_mismatches = (
    ~ratio_exact_matches
)


print(
    "Candidate formula:"
)

print(
    "Tot_Mdcr_Pymt_Amt / Tot_Mdcr_Stdzd_Amt"
)

print(
    f"\nValid rows       : "
    f"{valid_ratio.sum():,}"
)

print(
    f"Matching rows    : "
    f"{ratio_exact_matches.sum():,}"
)

print(
    f"Mismatching rows : "
    f"{ratio_mismatches.sum():,}"
)

print(
    f"Mismatch %       : "
    f"{percentage(ratio_mismatches.sum(), valid_ratio.sum()):.4f}%"
)


# ============================================================
# 11. TEST REVERSE FORMULA
# ============================================================

header(
    "8. TEST REVERSE STANDARDIZED RATIO"
)


reverse_ratio = safe_ratio(
    total_standardized,
    total_payment,
)


reverse_comparison = pd.DataFrame(
    {
        "source_payment":
            total_payment.values,

        "source_standardized":
            total_standardized.values,

        "stage4_ratio":
            stage4_ratio.values,

        "payment_over_standardized":
            source_expected_ratio.values,

        "standardized_over_payment":
            reverse_ratio.values,
    }
)


reverse_valid = (
    reverse_comparison[
        "standardized_over_payment"
    ].notna()
    &
    reverse_comparison[
        "stage4_ratio"
    ].notna()
)


reverse_matches = np.isclose(
    reverse_comparison.loc[
        reverse_valid,
        "standardized_over_payment",
    ],
    reverse_comparison.loc[
        reverse_valid,
        "stage4_ratio",
    ],
    rtol=1e-9,
    atol=1e-8,
)


print(
    "Reverse candidate:"
)

print(
    "Tot_Mdcr_Stdzd_Amt / Tot_Mdcr_Pymt_Amt"
)

print(
    f"\nValid rows       : "
    f"{reverse_valid.sum():,}"
)

print(
    f"Matching rows    : "
    f"{reverse_matches.sum():,}"
)

print(
    f"Mismatching rows : "
    f"{(~reverse_matches).sum():,}"
)

print(
    f"Mismatch %       : "
    f"{percentage((~reverse_matches).sum(), reverse_valid.sum()):.4f}%"
)


# ============================================================
# 12. TEST ALLOWED-BASED CANDIDATES
# ============================================================

header(
    "9. TEST ALLOWED-BASED RATIOS"
)


total_allowed = numeric(
    source[TOTAL_ALLOWED]
)


payment_over_allowed = safe_ratio(
    total_payment,
    total_allowed,
)


standardized_over_allowed = safe_ratio(
    total_standardized,
    total_allowed,
)


allowed_tests = {
    "payment_over_allowed":
        payment_over_allowed,

    "standardized_over_allowed":
        standardized_over_allowed,
}


allowed_rows = []


for name, candidate in allowed_tests.items():

    valid_candidate = (
        candidate.notna()
        &
        stage4_ratio.notna()
    )

    matches = np.isclose(
        candidate[valid_candidate],
        stage4_ratio[valid_candidate],
        rtol=1e-9,
        atol=1e-8,
    )

    allowed_rows.append(
        {
            "candidate_formula": name,
            "valid_rows": int(
                valid_candidate.sum()
            ),
            "matching_rows": int(
                matches.sum()
            ),
            "mismatching_rows": int(
                (~matches).sum()
            ),
            "mismatch_pct": percentage(
                int((~matches).sum()),
                int(valid_candidate.sum()),
            ),
        }
    )


allowed_summary = pd.DataFrame(
    allowed_rows
)


print(
    allowed_summary.to_string(
        index=False
    )
)


# ============================================================
# 13. DISTRIBUTION OF STAGE 4 RATIO
# ============================================================

header(
    "10. STANDARDIZED PAYMENT RATIO DISTRIBUTION"
)


ratio_values = stage4_ratio.dropna()


print(
    f"Valid values : {len(ratio_values):,}"
)

print(
    f"Minimum      : {ratio_values.min()}"
)

print(
    f"Median       : {ratio_values.median()}"
)

print(
    f"Maximum      : {ratio_values.max()}"
)

print(
    f"Values > 1   : {(ratio_values > 1).sum():,}"
)

print(
    f"Values = 1   : {(ratio_values == 1).sum():,}"
)

print(
    f"Values < 1   : {(ratio_values < 1).sum():,}"
)


# ============================================================
# 14. STANDARDIZED RATIO BY SUPPRESSION
# ============================================================

header(
    "11. STANDARDIZED RATIO BY DRUG SUPPRESSION"
)


ratio_by_suppression = stage4[
    [
        NPI,
        YEAR,
        STAGE4_STANDARDIZED_RATIO,
    ]
].merge(
    source[
        [
            NPI,
            YEAR,
            SUPPRESSED,
        ]
    ],
    on=[
        NPI,
        YEAR,
    ],
    how="left",
)


suppression_ratio_summary = (
    ratio_by_suppression
    .groupby(
        SUPPRESSED,
        dropna=False,
    )[STAGE4_STANDARDIZED_RATIO]
    .agg(
        rows="count",
        median="median",
        minimum="min",
        maximum="max",
    )
    .reset_index()
)


print(
    suppression_ratio_summary.to_string(
        index=False
    )
)


# ============================================================
# 15. EXTRACT EXAMPLES
# ============================================================

header(
    "12. EXTRACTING DIAGNOSTIC EXAMPLES"
)


# Suppressed examples
suppressed_examples = source[
    source[SUPPRESSED].eq(True)
].copy()


suppressed_examples = suppressed_examples[
    [
        NPI,
        YEAR,
        PROVIDER_TYPE,
        SUPPRESSED,

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
    ]
].head(100)


# Standardized ratio examples
standardized_examples = stage4[
    [
        NPI,
        YEAR,
        STAGE4_STANDARDIZED_RATIO,
    ]
].copy()


standardized_examples = standardized_examples.merge(
    source[
        [
            NPI,
            YEAR,
            TOTAL_PAYMENT,
            TOTAL_STANDARDIZED,
            TOTAL_ALLOWED,
            SUPPRESSED,
        ]
    ],
    on=[
        NPI,
        YEAR,
    ],
    how="left",
)


standardized_examples[
    "payment_over_standardized"
] = safe_ratio(
    numeric(
        standardized_examples[
            TOTAL_PAYMENT
        ]
    ),
    numeric(
        standardized_examples[
            TOTAL_STANDARDIZED
        ]
    ),
)


standardized_examples[
    "standardized_over_payment"
] = safe_ratio(
    numeric(
        standardized_examples[
            TOTAL_STANDARDIZED
        ]
    ),
    numeric(
        standardized_examples[
            TOTAL_PAYMENT
        ]
    ),
)


standardized_examples[
    "payment_over_allowed"
] = safe_ratio(
    numeric(
        standardized_examples[
            TOTAL_PAYMENT
        ]
    ),
    numeric(
        standardized_examples[
            TOTAL_ALLOWED
        ]
    ),
)


# Select records where Stage 4 ratio is > 1
standardized_examples = (
    standardized_examples[
        standardized_examples[
            STAGE4_STANDARDIZED_RATIO
        ]
        > 1
    ]
    .head(100)
)


# ============================================================
# 16. FEATURE SEMANTIC RECOMMENDATION TABLE
# ============================================================

header(
    "13. FEATURE SEMANTIC STATUS"
)


feature_semantics = pd.DataFrame(
    [
        {
            "feature":
                "drug_service_share",
            "current_issue":
                "Drug values are zero when suppression is True.",
            "status":
                "REQUIRES_SEMANTIC_DECISION",
            "outlier_treatment":
                "DO_NOT_TREAT_YET",
        },

        {
            "feature":
                "drug_payment_share",
            "current_issue":
                "Drug values are zero when suppression is True.",
            "status":
                "REQUIRES_SEMANTIC_DECISION",
            "outlier_treatment":
                "DO_NOT_TREAT_YET",
        },

        {
            "feature":
                "medical_service_share",
            "current_issue":
                "Medical component may exceed total when drug data is suppressed.",
            "status":
                "REQUIRES_SEMANTIC_DECISION",
            "outlier_treatment":
                "DO_NOT_TREAT_YET",
        },

        {
            "feature":
                "medical_payment_share",
            "current_issue":
                "Medical component may exceed total when drug data is suppressed.",
            "status":
                "REQUIRES_SEMANTIC_DECISION",
            "outlier_treatment":
                "DO_NOT_TREAT_YET",
        },

        {
            "feature":
                "standardized_payment_ratio",
            "current_issue":
                "Current formula has not been semantically validated.",
            "status":
                "DEFINITION_UNRESOLVED",
            "outlier_treatment":
                "DO_NOT_TREAT_YET",
        },
    ]
)


print(
    feature_semantics.to_string(
        index=False
    )
)


# ============================================================
# 17. SAVE OUTPUTS
# ============================================================

header(
    "14. SAVING DIAGNOSTIC OUTPUTS"
)


suppression_output = (
    suppression_summary
    .merge(
        drug_analysis,
        on=SUPPRESSED,
        how="left",
    )
)


suppression_output.to_csv(
    SUPPRESSION_SUMMARY_FILE,
    index=False,
)


suppressed_examples.to_csv(
    SUPPRESSION_EXAMPLES_FILE,
    index=False,
)


standardized_summary = pd.concat(
    [
        pd.DataFrame(
            [
                {
                    "test":
                        "payment_over_standardized",
                    **{
                        k: v
                        for k, v in allowed_rows[0].items()
                        if k != "candidate_formula"
                    },
                }
            ]
        ),
        pd.DataFrame(
            [
                {
                    "test":
                        "standardized_over_payment",
                    "valid_rows":
                        int(
                            reverse_valid.sum()
                        ),
                    "matching_rows":
                        int(
                            reverse_matches.sum()
                        ),
                    "mismatching_rows":
                        int(
                            (~reverse_matches).sum()
                        ),
                    "mismatch_pct":
                        percentage(
                            int(
                                (~reverse_matches).sum()
                            ),
                            int(
                                reverse_valid.sum()
                            ),
                        ),
                }
            ]
        ),
    ],
    ignore_index=True,
)


standardized_summary.to_csv(
    STANDARDIZED_SUMMARY_FILE,
    index=False,
)


standardized_examples.to_csv(
    STANDARDIZED_EXAMPLES_FILE,
    index=False,
)


feature_semantics.to_csv(
    FEATURE_SEMANTIC_FILE,
    index=False,
)


print(
    "\nCreated:"
)

print(
    f"  {SUPPRESSION_SUMMARY_FILE}"
)

print(
    f"  {SUPPRESSION_EXAMPLES_FILE}"
)

print(
    f"  {STANDARDIZED_SUMMARY_FILE}"
)

print(
    f"  {STANDARDIZED_EXAMPLES_FILE}"
)

print(
    f"  {FEATURE_SEMANTIC_FILE}"
)


# ============================================================
# 18. FINAL MESSAGE
# ============================================================

header(
    "15. INVESTIGATION COMPLETE"
)

print(
    "No source values were changed."
)

print(
    "No feature values were changed."
)

print(
    "No rows were removed."
)

print(
    "No outlier treatment was performed."
)

print(
    "\nNEXT STEP:"
)

print(
    "Review the generated diagnostics before making "
    "any feature-definition or outlier decision."
)