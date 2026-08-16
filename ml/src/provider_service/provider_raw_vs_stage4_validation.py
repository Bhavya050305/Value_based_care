from pathlib import Path
import numpy as np
import pandas as pd


# ============================================================
# RAW / CLEANED SOURCE vs STAGE 4 SEMANTIC VALIDATION
# ============================================================
#
# PURPOSE
# -------
# Determine whether the suspicious component behavior observed
# in Stage 4 already existed in the cleaned provider source or
# was introduced during Stage 4 feature engineering.
#
# THIS SCRIPT IS DIAGNOSTIC ONLY.
#
# It does NOT:
#   - modify source data
#   - remove rows
#   - impute values
#   - cap values
#   - winsorize values
#   - perform outlier treatment
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


SUMMARY_FILE = (
    OUTPUT_DIR
    / "raw_vs_stage4_semantic_summary.csv"
)

ROW_COMPARISON_FILE = (
    OUTPUT_DIR
    / "raw_vs_stage4_row_comparison.csv"
)

SUSPICIOUS_FILE = (
    OUTPUT_DIR
    / "raw_vs_stage4_suspicious_records.csv"
)

SUPPRESSION_FILE = (
    OUTPUT_DIR
    / "raw_vs_stage4_suppression_analysis.csv"
)


# ============================================================
# 2. SOURCE COLUMNS
# ============================================================

NPI = "Rndrng_NPI"
YEAR = "Year"
PROVIDER_TYPE = "Rndrng_Prvdr_Type"

DRUG_SUPPRESSED = "drug_data_suppressed"

RAW_COLUMNS = [
    "Tot_HCPCS_Cds",
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_Sbmtd_Chrg",
    "Tot_Mdcr_Alowd_Amt",
    "Tot_Mdcr_Pymt_Amt",
    "Tot_Mdcr_Stdzd_Amt",

    "Drug_Tot_HCPCS_Cds",
    "Drug_Tot_Benes",
    "Drug_Tot_Srvcs",
    "Drug_Sbmtd_Chrg",
    "Drug_Mdcr_Alowd_Amt",
    "Drug_Mdcr_Pymt_Amt",
    "Drug_Mdcr_Stdzd_Amt",

    "Med_Tot_HCPCS_Cds",
    "Med_Tot_Benes",
    "Med_Tot_Srvcs",
    "Med_Sbmtd_Chrg",
    "Med_Mdcr_Alowd_Amt",
    "Med_Mdcr_Pymt_Amt",
    "Med_Mdcr_Stdzd_Amt",
]


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


def pct(numerator, denominator):
    if denominator == 0:
        return 0.0
    return numerator / denominator * 100.0


# ============================================================
# 4. LOAD FILES
# ============================================================

header("1. LOADING SOURCE AND STAGE 4 DATA")

print(f"Project root : {PROJECT_ROOT}")
print(f"Source file  : {SOURCE_FILE}")
print(f"Stage 4 file : {STAGE4_FILE}")


if not SOURCE_FILE.exists():
    raise FileNotFoundError(
        f"\nClean source file not found:\n{SOURCE_FILE}"
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
    f"\nClean source rows    : {len(source):,}"
)

print(
    f"Clean source columns : {len(source.columns):,}"
)

print(
    f"Stage 4 rows         : {len(stage4):,}"
)

print(
    f"Stage 4 columns      : {len(stage4.columns):,}"
)


# ============================================================
# 5. SCHEMA VALIDATION
# ============================================================

header("2. SCHEMA VALIDATION")


required_source = [
    NPI,
    YEAR,
] + RAW_COLUMNS


missing_source = [
    c
    for c in required_source
    if c not in source.columns
]


missing_stage4 = [
    c
    for c in required_source
    if c not in stage4.columns
]


if missing_source:

    print("Missing from clean source:")

    for c in missing_source:
        print(f"  - {c}")

    raise ValueError(
        "Required columns missing from clean source."
    )


if missing_stage4:

    print("Missing from Stage 4:")

    for c in missing_stage4:
        print(f"  - {c}")

    raise ValueError(
        "Required columns missing from Stage 4."
    )


print("PASS: Required comparison columns exist.")


# ============================================================
# 6. CHECK GRAIN
# ============================================================

header("3. NPI-YEAR GRAIN VALIDATION")


source["__key"] = (
    source[NPI].astype(str)
    + "|"
    + source[YEAR].astype(str)
)


stage4["__key"] = (
    stage4[NPI].astype(str)
    + "|"
    + stage4[YEAR].astype(str)
)


source_duplicate_keys = (
    source["__key"]
    .duplicated()
    .sum()
)

stage4_duplicate_keys = (
    stage4["__key"]
    .duplicated()
    .sum()
)


print(
    f"Source duplicate NPI-Year rows : "
    f"{source_duplicate_keys:,}"
)

print(
    f"Stage 4 duplicate NPI-Year rows: "
    f"{stage4_duplicate_keys:,}"
)


if source_duplicate_keys != 0:

    raise ValueError(
        "Clean source is not unique at NPI-Year grain."
    )


if stage4_duplicate_keys != 0:

    raise ValueError(
        "Stage 4 is not unique at NPI-Year grain."
    )


source_keys = set(
    source["__key"]
)

stage4_keys = set(
    stage4["__key"]
)


source_only = source_keys - stage4_keys
stage4_only = stage4_keys - source_keys


print(
    f"Keys only in clean source : "
    f"{len(source_only):,}"
)

print(
    f"Keys only in Stage 4       : "
    f"{len(stage4_only):,}"
)


if source_only or stage4_only:

    print(
        "\nWARNING: NPI-Year populations differ."
    )

else:

    print(
        "PASS: Same NPI-Year population."
    )


# ============================================================
# 7. MERGE SOURCE AND STAGE 4
# ============================================================

header("4. ROW-LEVEL SOURCE / STAGE 4 COMPARISON")


source_compare = source[
    [
        NPI,
        YEAR,
        PROVIDER_TYPE,
        DRUG_SUPPRESSED,
    ]
    + RAW_COLUMNS
].copy()


stage4_compare = stage4[
    [
        NPI,
        YEAR,
    ]
    + RAW_COLUMNS
].copy()


source_compare = source_compare.rename(
    columns={
        c: f"source__{c}"
        for c in RAW_COLUMNS
    }
)


stage4_compare = stage4_compare.rename(
    columns={
        c: f"stage4__{c}"
        for c in RAW_COLUMNS
    }
)


comparison = source_compare.merge(
    stage4_compare,
    on=[
        NPI,
        YEAR,
    ],
    how="outer",
    indicator=True,
)


print(
    f"Comparison rows: {len(comparison):,}"
)


print(
    "\nMerge status:"
)

print(
    comparison["_merge"]
    .value_counts()
    .to_string()
)


# ============================================================
# 8. CHECK RAW VALUES PRESERVED
# ============================================================

header("5. RAW VALUE PRESERVATION")


comparison_results = []


for column in RAW_COLUMNS:

    source_col = f"source__{column}"
    stage4_col = f"stage4__{column}"

    source_values = numeric(
        comparison[source_col]
    )

    stage4_values = numeric(
        comparison[stage4_col]
    )

    both_present = (
        source_values.notna()
        & stage4_values.notna()
    )

    exact_match = (
        np.isclose(
            source_values[
                both_present
            ],
            stage4_values[
                both_present
            ],
            rtol=1e-9,
            atol=1e-8,
        )
    )

    matching = int(
        exact_match.sum()
    )

    valid = int(
        both_present.sum()
    )

    mismatching = valid - matching

    max_difference = 0.0

    if valid > 0:

        differences = (
            stage4_values[
                both_present
            ]
            - source_values[
                both_present
            ]
        ).abs()

        max_difference = float(
            differences.max()
        )


    comparison_results.append(
        {
            "column": column,
            "valid_comparisons": valid,
            "matching_rows": matching,
            "mismatching_rows": mismatching,
            "mismatch_pct": pct(
                mismatching,
                valid,
            ),
            "max_absolute_difference":
                max_difference,
        }
    )


preservation_summary = pd.DataFrame(
    comparison_results
)


print(
    preservation_summary.to_string(
        index=False
    )
)


# ============================================================
# 9. RAW COMPONENT RECONCILIATION ON CLEAN SOURCE
# ============================================================

header(
    "6. RECONCILIATION ON CLEAN SOURCE"
)


def reconciliation_result(
    df,
    total,
    medical,
    drug,
):

    total_values = numeric(
        df[total]
    )

    medical_values = numeric(
        df[medical]
    )

    drug_values = numeric(
        df[drug]
    )

    component_sum = (
        medical_values
        + drug_values
    )

    valid = (
        total_values.notna()
        & component_sum.notna()
    )

    matches = np.isclose(
        total_values[valid],
        component_sum[valid],
        rtol=1e-9,
        atol=1e-8,
    )

    mismatch = ~matches

    gt_total = (
        component_sum[valid]
        > total_values[valid]
    )

    return {
        "valid_rows": int(valid.sum()),
        "matching_rows": int(matches.sum()),
        "mismatch_rows": int(mismatch.sum()),
        "mismatch_pct": pct(
            int(mismatch.sum()),
            int(valid.sum()),
        ),
        "component_gt_total_rows": int(
            gt_total.sum()
        ),
    }


reconciliation_rows = []


metric_map = {
    "services": (
        "Tot_Srvcs",
        "Med_Tot_Srvcs",
        "Drug_Tot_Srvcs",
    ),

    "payment": (
        "Tot_Mdcr_Pymt_Amt",
        "Med_Mdcr_Pymt_Amt",
        "Drug_Mdcr_Pymt_Amt",
    ),

    "allowed": (
        "Tot_Mdcr_Alowd_Amt",
        "Med_Mdcr_Alowd_Amt",
        "Drug_Mdcr_Alowd_Amt",
    ),

    "charge": (
        "Tot_Sbmtd_Chrg",
        "Med_Sbmtd_Chrg",
        "Drug_Sbmtd_Chrg",
    ),

    "standardized": (
        "Tot_Mdcr_Stdzd_Amt",
        "Med_Mdcr_Stdzd_Amt",
        "Drug_Mdcr_Stdzd_Amt",
    ),
}


for metric, columns in metric_map.items():

    result = reconciliation_result(
        source,
        columns[0],
        columns[1],
        columns[2],
    )

    result["metric"] = metric

    reconciliation_rows.append(
        result
    )


source_reconciliation = pd.DataFrame(
    reconciliation_rows
)


print(
    source_reconciliation.to_string(
        index=False
    )
)


# ============================================================
# 10. CHECK SUPPRESSION EFFECT
# ============================================================

header(
    "7. SUPPRESSION VS RECONCILIATION"
)


if DRUG_SUPPRESSED in source.columns:

    source["__drug_all_zero"] = (
        numeric(
            source["Drug_Tot_Srvcs"]
        ).fillna(0).eq(0)
        &
        numeric(
            source["Drug_Mdcr_Pymt_Amt"]
        ).fillna(0).eq(0)
        &
        numeric(
            source["Drug_Mdcr_Alowd_Amt"]
        ).fillna(0).eq(0)
        &
        numeric(
            source["Drug_Sbmtd_Chrg"]
        ).fillna(0).eq(0)
        &
        numeric(
            source["Drug_Mdcr_Stdzd_Amt"]
        ).fillna(0).eq(0)
    )


    source["__payment_mismatch"] = (
        ~np.isclose(
            numeric(
                source["Tot_Mdcr_Pymt_Amt"]
            ),
            (
                numeric(
                    source[
                        "Med_Mdcr_Pymt_Amt"
                    ]
                )
                +
                numeric(
                    source[
                        "Drug_Mdcr_Pymt_Amt"
                    ]
                )
            ),
            rtol=1e-9,
            atol=1e-8,
        )
    )


    suppression_summary = (
        source
        .groupby(
            DRUG_SUPPRESSED,
            dropna=False,
        )
        .agg(
            total_rows=(
                NPI,
                "size",
            ),
            drug_all_zero_rows=(
                "__drug_all_zero",
                "sum",
            ),
            payment_mismatch_rows=(
                "__payment_mismatch",
                "sum",
            ),
        )
        .reset_index()
    )


    suppression_summary[
        "drug_zero_pct"
    ] = (
        suppression_summary[
            "drug_all_zero_rows"
        ]
        / suppression_summary[
            "total_rows"
        ]
        * 100
    )


    suppression_summary[
        "payment_mismatch_pct"
    ] = (
        suppression_summary[
            "payment_mismatch_rows"
        ]
        / suppression_summary[
            "total_rows"
        ]
        * 100
    )


    print(
        suppression_summary.to_string(
            index=False
        )
    )

else:

    print(
        "drug_data_suppressed not available."
    )

    suppression_summary = pd.DataFrame()


# ============================================================
# 11. IDENTIFY REPEATED MEDICAL VALUES
# ============================================================

header(
    "8. REPEATED MEDICAL COMPONENT VALUES"
)


repeat_columns = [
    "Med_Tot_Srvcs",
    "Med_Mdcr_Pymt_Amt",
    "Med_Mdcr_Alowd_Amt",
    "Med_Sbmtd_Chrg",
    "Med_Mdcr_Stdzd_Amt",
]


for column in repeat_columns:

    counts = (
        source[column]
        .value_counts(
            dropna=False
        )
        .head(10)
    )

    print(
        f"\nTop repeated values: {column}"
    )

    print(
        counts.to_string()
    )


# ============================================================
# 12. IDENTIFY SUSPICIOUS RECORDS
# ============================================================

header(
    "9. SUSPICIOUS SOURCE RECORDS"
)


source["__payment_component_sum"] = (
    numeric(
        source["Med_Mdcr_Pymt_Amt"]
    )
    +
    numeric(
        source["Drug_Mdcr_Pymt_Amt"]
    )
)


source["__payment_difference"] = (
    source["__payment_component_sum"]
    -
    numeric(
        source["Tot_Mdcr_Pymt_Amt"]
    )
)


source["__services_component_sum"] = (
    numeric(
        source["Med_Tot_Srvcs"]
    )
    +
    numeric(
        source["Drug_Tot_Srvcs"]
    )
)


source["__services_difference"] = (
    source["__services_component_sum"]
    -
    numeric(
        source["Tot_Srvcs"]
    )
)


source["__component_gt_total"] = (
    (
        source["__payment_component_sum"]
        > numeric(
            source["Tot_Mdcr_Pymt_Amt"]
        )
    )
    |
    (
        source["__services_component_sum"]
        > numeric(
            source["Tot_Srvcs"]
        )
    )
)


suspicious = source[
    source["__component_gt_total"]
].copy()


print(
    f"Source rows with component > total: "
    f"{len(suspicious):,}"
)


suspicious_columns = [
    NPI,
    YEAR,
    PROVIDER_TYPE,
    DRUG_SUPPRESSED,

    "Tot_Srvcs",
    "Med_Tot_Srvcs",
    "Drug_Tot_Srvcs",
    "__services_difference",

    "Tot_Mdcr_Pymt_Amt",
    "Med_Mdcr_Pymt_Amt",
    "Drug_Mdcr_Pymt_Amt",
    "__payment_difference",

    "Tot_Mdcr_Alowd_Amt",
    "Med_Mdcr_Alowd_Amt",
    "Drug_Mdcr_Alowd_Amt",

    "Tot_Sbmtd_Chrg",
    "Med_Sbmtd_Chrg",
    "Drug_Sbmtd_Chrg",

    "Tot_Mdcr_Stdzd_Amt",
    "Med_Mdcr_Stdzd_Amt",
    "Drug_Mdcr_Stdzd_Amt",
]


suspicious_columns = [
    c
    for c in suspicious_columns
    if c in suspicious.columns
]


print(
    suspicious[
        suspicious_columns
    ]
    .head(30)
    .to_string(
        index=False
    )
)


# ============================================================
# 13. FINAL SUMMARY
# ============================================================

header("10. FINAL SEMANTIC VALIDATION SUMMARY")


print(
    "The investigation distinguishes between:"
)

print(
    "  1. Values already present in the clean source"
)

print(
    "  2. Values changed during Stage 4"
)

print(
    "  3. Component reconciliation behavior"
)

print(
    "  4. Drug suppression behavior"
)

print(
    "  5. Repeated component values"
)

print(
    "No outlier treatment was performed."
)

print(
    "No source values were modified."
)


# ============================================================
# 14. SAVE OUTPUTS
# ============================================================

header("11. SAVING OUTPUT FILES")


summary_rows = []


for row in reconciliation_rows:

    summary_rows.append(
        {
            "analysis": "source_reconciliation",
            **row,
        }
    )


for row in comparison_results:

    summary_rows.append(
        {
            "analysis": "stage4_value_preservation",
            **row,
        }
    )


summary = pd.DataFrame(
    summary_rows
)


summary.to_csv(
    SUMMARY_FILE,
    index=False,
)


comparison[
    [
        c
        for c in comparison.columns
        if c not in RAW_COLUMNS
    ]
].head(10000).to_csv(
    ROW_COMPARISON_FILE,
    index=False,
)


suspicious[
    suspicious_columns
].to_csv(
    SUSPICIOUS_FILE,
    index=False,
)


if not suppression_summary.empty:

    suppression_summary.to_csv(
        SUPPRESSION_FILE,
        index=False,
    )


print(
    "\nCreated:"
)

print(
    f"  {SUMMARY_FILE}"
)

print(
    f"  {ROW_COMPARISON_FILE}"
)

print(
    f"  {SUSPICIOUS_FILE}"
)

if not suppression_summary.empty:

    print(
        f"  {SUPPRESSION_FILE}"
    )


print(
    "\nNEXT STEP:"
)

print(
    "Review these outputs before changing any feature "
    "definitions or performing outlier treatment."
)