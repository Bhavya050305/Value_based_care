from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PROVIDER RAW COMPONENT INSPECTION
# ============================================================
# PURPOSE
# -------
# Diagnose the relationships between total, medical, and drug
# provider/service source fields before any outlier treatment.
#
# IMPORTANT:
# This script is DIAGNOSTIC ONLY.
#
# It does NOT:
# - modify source data
# - remove rows
# - replace values
# - cap values
# - winsorize values
# - impute values
#
# Analytical grain:
#     Rndrng_NPI + Year
#
# Current pipeline position:
#
# Stage 4
#    ↓
# Raw Component Inspection
#    ↓
# Semantic Validation
#    ↓
# Outlier Analysis
#
# We are intentionally NOT doing outlier treatment here.
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

DIAGNOSTIC_FILE = (
    OUTPUT_DIR
    / "provider_raw_component_diagnostics.csv"
)

SUMMARY_FILE = (
    OUTPUT_DIR
    / "provider_raw_component_summary.csv"
)

YEAR_SUMMARY_FILE = (
    OUTPUT_DIR
    / "provider_raw_component_year_summary.csv"
)


# ============================================================
# 2. SOURCE COLUMN DEFINITIONS
# ============================================================
# These names come directly from the actual Stage 4 schema.
# We are NOT guessing these names anymore.
# ============================================================

SOURCE_COLUMNS = {
    "npi": "Rndrng_NPI",
    "year": "Year",

    "provider_type": "Rndrng_Prvdr_Type",

    "total_hcpcs": "Tot_HCPCS_Cds",
    "total_beneficiaries": "Tot_Benes",
    "total_services": "Tot_Srvcs",
    "total_charge": "Tot_Sbmtd_Chrg",
    "total_allowed": "Tot_Mdcr_Alowd_Amt",
    "total_payment": "Tot_Mdcr_Pymt_Amt",
    "total_standardized": "Tot_Mdcr_Stdzd_Amt",

    "drug_hcpcs": "Drug_Tot_HCPCS_Cds",
    "drug_beneficiaries": "Drug_Tot_Benes",
    "drug_services": "Drug_Tot_Srvcs",
    "drug_charge": "Drug_Sbmtd_Chrg",
    "drug_allowed": "Drug_Mdcr_Alowd_Amt",
    "drug_payment": "Drug_Mdcr_Pymt_Amt",
    "drug_standardized": "Drug_Mdcr_Stdzd_Amt",

    "medical_hcpcs": "Med_Tot_HCPCS_Cds",
    "medical_beneficiaries": "Med_Tot_Benes",
    "medical_services": "Med_Tot_Srvcs",
    "medical_charge": "Med_Sbmtd_Chrg",
    "medical_allowed": "Med_Mdcr_Alowd_Amt",
    "medical_payment": "Med_Mdcr_Pymt_Amt",
    "medical_standardized": "Med_Mdcr_Stdzd_Amt",
}


# ============================================================
# 3. CORE REQUIRED COLUMNS
# ============================================================

CORE_COLUMNS = [
    SOURCE_COLUMNS["npi"],
    SOURCE_COLUMNS["year"],
]


# ============================================================
# 4. RECONCILIATION DEFINITIONS
# ============================================================
# These checks ask whether:
#
# Medical + Drug = Total
#
# We do NOT assume that this MUST be true.
# We are testing the relationship to understand the data.
# ============================================================

RECONCILIATIONS = {
    "services": {
        "total": SOURCE_COLUMNS["total_services"],
        "medical": SOURCE_COLUMNS["medical_services"],
        "drug": SOURCE_COLUMNS["drug_services"],
    },

    "payment": {
        "total": SOURCE_COLUMNS["total_payment"],
        "medical": SOURCE_COLUMNS["medical_payment"],
        "drug": SOURCE_COLUMNS["drug_payment"],
    },

    "allowed": {
        "total": SOURCE_COLUMNS["total_allowed"],
        "medical": SOURCE_COLUMNS["medical_allowed"],
        "drug": SOURCE_COLUMNS["drug_allowed"],
    },

    "charge": {
        "total": SOURCE_COLUMNS["total_charge"],
        "medical": SOURCE_COLUMNS["medical_charge"],
        "drug": SOURCE_COLUMNS["drug_charge"],
    },

    "standardized": {
        "total": SOURCE_COLUMNS["total_standardized"],
        "medical": SOURCE_COLUMNS["medical_standardized"],
        "drug": SOURCE_COLUMNS["drug_standardized"],
    },
}


# ============================================================
# 5. HELPER FUNCTIONS
# ============================================================

def print_header(title: str) -> None:
    """Print a readable terminal section header."""

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def safe_divide(
    numerator: pd.Series,
    denominator: pd.Series,
) -> pd.Series:
    """
    Safely divide two Series.

    Zero denominators become NaN.

    We intentionally do NOT replace NaN with zero.
    """

    denominator = denominator.replace(0, np.nan)

    return numerator / denominator


def validate_columns(
    df: pd.DataFrame,
    required_columns: list[str],
) -> bool:
    """Validate that required columns exist."""

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        print("FAIL: Missing required columns:")

        for column in missing_columns:
            print(f"  - {column}")

        return False

    print(
        f"PASS: All {len(required_columns)} "
        f"required columns are present."
    )

    return True


def numeric_copy(
    df: pd.DataFrame,
    column: str,
) -> pd.Series:
    """
    Create a numeric diagnostic copy of a source column.

    The original DataFrame column is NOT modified.
    """

    return pd.to_numeric(
        df[column],
        errors="coerce",
    )


# ============================================================
# 6. LOAD DATA
# ============================================================

print_header(
    "1. LOADING PROVIDER FEATURE DATA"
)

print(
    f"Project root : {PROJECT_ROOT}"
)

print(
    f"Input file   : {INPUT_FILE}"
)

print(
    f"Output dir   : {OUTPUT_DIR}"
)


if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"\nInput file does not exist:\n"
        f"{INPUT_FILE}"
    )


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


df = pd.read_csv(
    INPUT_FILE
)


print(
    f"\nRows loaded    : {len(df):,}"
)

print(
    f"Columns loaded : {len(df.columns):,}"
)


# ============================================================
# 7. SCHEMA VALIDATION
# ============================================================

print_header(
    "2. SOURCE SCHEMA VALIDATION"
)

required_source_columns = list(
    SOURCE_COLUMNS.values()
)

schema_passed = validate_columns(
    df,
    required_source_columns,
)

if not schema_passed:

    raise ValueError(
        "Source schema validation failed. "
        "No diagnostic analysis was performed."
    )


# ============================================================
# 8. GRAIN VALIDATION
# ============================================================

print_header(
    "3. GRAIN VALIDATION"
)

npi_column = SOURCE_COLUMNS["npi"]
year_column = SOURCE_COLUMNS["year"]


npi_nulls = df[npi_column].isna().sum()

year_nulls = df[year_column].isna().sum()


print(
    f"{npi_column} nulls : {npi_nulls:,}"
)

print(
    f"{year_column} nulls : {year_nulls:,}"
)


unique_npi_year = (
    df[
        [npi_column, year_column]
    ]
    .drop_duplicates()
    .shape[0]
)


duplicate_npi_year_rows = (
    df.duplicated(
        subset=[
            npi_column,
            year_column,
        ]
    )
    .sum()
)


print(
    f"Unique NPI-Year combinations : "
    f"{unique_npi_year:,}"
)

print(
    f"Duplicate NPI-Year rows       : "
    f"{duplicate_npi_year_rows:,}"
)


if (
    npi_nulls == 0
    and year_nulls == 0
    and duplicate_npi_year_rows == 0
):

    print(
        "PASS: Rndrng_NPI + Year grain is valid."
    )

else:

    print(
        "FAIL: NPI + Year grain validation failed."
    )


# ============================================================
# 9. YEAR CONSISTENCY CHECK
# ============================================================
# Stage 4 also contains performance_year.
#
# We do not use performance_year as the source grain.
# We only check whether it agrees with Year.
# ============================================================

print_header(
    "4. YEAR CONSISTENCY CHECK"
)

if "performance_year" in df.columns:

    year_comparison = (
        df[year_column]
        == df["performance_year"]
    )

    mismatch_count = (
        ~year_comparison
    ).sum()

    null_comparison_count = (
        df["performance_year"]
        .isna()
        .sum()
    )

    print(
        f"Year vs performance_year mismatches : "
        f"{mismatch_count:,}"
    )

    print(
        f"performance_year nulls              : "
        f"{null_comparison_count:,}"
    )

    if mismatch_count == 0:

        print(
            "PASS: Year and performance_year "
            "match for all comparable rows."
        )

    else:

        print(
            "WARNING: Year and performance_year "
            "do not fully match."
        )

else:

    print(
        "INFO: performance_year is not present."
    )


# ============================================================
# 10. CREATE DIAGNOSTIC COPY
# ============================================================
# All calculations below use diagnostic copies.
# The source DataFrame values are not changed.
# ============================================================

diagnostics = df.copy()


numeric_columns = [
    column
    for logical_name, column in SOURCE_COLUMNS.items()
    if logical_name not in [
        "npi",
        "year",
        "provider_type",
    ]
]


for column in numeric_columns:

    diagnostics[
        f"__num_{column}"
    ] = numeric_copy(
        df,
        column,
    )


# ============================================================
# 11. BASIC SOURCE FIELD SUMMARY
# ============================================================

print_header(
    "5. BASIC SOURCE FIELD SUMMARY"
)

source_summary_records = []


for logical_name, column in SOURCE_COLUMNS.items():

    if logical_name in [
        "npi",
        "year",
        "provider_type",
    ]:

        continue

    series = diagnostics[
        f"__num_{column}"
    ]

    source_summary_records.append(
        {
            "logical_field": logical_name,
            "source_column": column,
            "rows": len(series),
            "null_rows": int(
                series.isna().sum()
            ),
            "zero_rows": int(
                (series == 0).sum()
            ),
            "negative_rows": int(
                (series < 0).sum()
            ),
            "positive_rows": int(
                (series > 0).sum()
            ),
            "min": series.min(),
            "median": series.median(),
            "max": series.max(),
        }
    )


source_summary_df = pd.DataFrame(
    source_summary_records
)


print(
    source_summary_df[
        [
            "logical_field",
            "null_rows",
            "zero_rows",
            "negative_rows",
            "min",
            "median",
            "max",
        ]
    ].to_string(
        index=False
    )
)


# ============================================================
# 12. COMPONENT RECONCILIATION
# ============================================================

print_header(
    "6. COMPONENT RECONCILIATION"
)

reconciliation_summary = []


for metric, definition in RECONCILIATIONS.items():

    total_column = definition["total"]
    medical_column = definition["medical"]
    drug_column = definition["drug"]

    total = diagnostics[
        f"__num_{total_column}"
    ]

    medical = diagnostics[
        f"__num_{medical_column}"
    ]

    drug = diagnostics[
        f"__num_{drug_column}"
    ]

    component_sum = (
        medical + drug
    )

    difference = (
        component_sum - total
    )

    absolute_difference = (
        difference.abs()
    )

    valid_mask = (
        total.notna()
        & medical.notna()
        & drug.notna()
    )

    exact_match = (
        np.isclose(
            component_sum,
            total,
            rtol=1e-9,
            atol=1e-6,
        )
    )

    exact_match = (
        exact_match
        & valid_mask
    )

    component_gt_total = (
        component_sum > total
    )

    component_gt_total = (
        component_gt_total
        & valid_mask
    )

    total_zero = (
        total == 0
    )

    valid_count = int(
        valid_mask.sum()
    )

    mismatch_count = int(
        (
            valid_mask
            & ~exact_match
        ).sum()
    )

    component_gt_total_count = int(
        component_gt_total.sum()
    )

    print(
        f"\n{metric.upper()}"
    )

    print(
        f"  Valid rows                  : "
        f"{valid_count:,}"
    )

    print(
        f"  Medical + Drug = Total      : "
        f"{exact_match.sum():,}"
    )

    print(
        f"  Reconciliation mismatches   : "
        f"{mismatch_count:,}"
    )

    print(
        f"  Component sum > Total       : "
        f"{component_gt_total_count:,}"
    )

    if valid_count > 0:

        mismatch_pct = (
            mismatch_count
            / valid_count
            * 100
        )

        print(
            f"  Mismatch percentage          : "
            f"{mismatch_pct:.4f}%"
        )

    print(
        f"  Maximum absolute difference  : "
        f"{absolute_difference.max():,.6f}"
    )

    # Save calculated diagnostic fields.
    diagnostics[
        f"component_sum_{metric}"
    ] = component_sum

    diagnostics[
        f"difference_{metric}"
    ] = difference

    diagnostics[
        f"absolute_difference_{metric}"
    ] = absolute_difference

    diagnostics[
        f"components_equal_total_{metric}"
    ] = exact_match

    diagnostics[
        f"components_gt_total_{metric}"
    ] = component_gt_total

    reconciliation_summary.append(
        {
            "metric": metric,
            "valid_rows": valid_count,
            "matching_rows": int(
                exact_match.sum()
            ),
            "mismatch_rows": mismatch_count,
            "mismatch_pct": (
                mismatch_count
                / valid_count
                * 100
                if valid_count > 0
                else np.nan
            ),
            "component_gt_total_rows":
                component_gt_total_count,
            "max_absolute_difference":
                absolute_difference.max(),
            "median_absolute_difference":
                absolute_difference.median(),
        }
    )


reconciliation_summary_df = pd.DataFrame(
    reconciliation_summary
)


# ============================================================
# 13. COMPONENT-TO-TOTAL RATIOS
# ============================================================

print_header(
    "7. COMPONENT-TO-TOTAL RATIOS"
)

ratio_definitions = {
    "medical_payment_to_total":
        (
            SOURCE_COLUMNS["medical_payment"],
            SOURCE_COLUMNS["total_payment"],
        ),

    "drug_payment_to_total":
        (
            SOURCE_COLUMNS["drug_payment"],
            SOURCE_COLUMNS["total_payment"],
        ),

    "medical_services_to_total":
        (
            SOURCE_COLUMNS["medical_services"],
            SOURCE_COLUMNS["total_services"],
        ),

    "drug_services_to_total":
        (
            SOURCE_COLUMNS["drug_services"],
            SOURCE_COLUMNS["total_services"],
        ),

    "medical_allowed_to_total":
        (
            SOURCE_COLUMNS["medical_allowed"],
            SOURCE_COLUMNS["total_allowed"],
        ),

    "drug_allowed_to_total":
        (
            SOURCE_COLUMNS["drug_allowed"],
            SOURCE_COLUMNS["total_allowed"],
        ),

    "medical_charge_to_total":
        (
            SOURCE_COLUMNS["medical_charge"],
            SOURCE_COLUMNS["total_charge"],
        ),

    "drug_charge_to_total":
        (
            SOURCE_COLUMNS["drug_charge"],
            SOURCE_COLUMNS["total_charge"],
        ),

    "medical_standardized_to_total":
        (
            SOURCE_COLUMNS["medical_standardized"],
            SOURCE_COLUMNS["total_standardized"],
        ),

    "drug_standardized_to_total":
        (
            SOURCE_COLUMNS["drug_standardized"],
            SOURCE_COLUMNS["total_standardized"],
        ),
}


ratio_summary_records = []


for ratio_name, (
    numerator_column,
    denominator_column,
) in ratio_definitions.items():

    numerator = diagnostics[
        f"__num_{numerator_column}"
    ]

    denominator = diagnostics[
        f"__num_{denominator_column}"
    ]

    ratio = safe_divide(
        numerator,
        denominator,
    )

    diagnostics[
        ratio_name
    ] = ratio

    valid = ratio.dropna()

    if valid.empty:

        continue

    above_one = (
        valid > 1
    ).sum()

    below_zero = (
        valid < 0
    ).sum()

    print(
        f"\n{ratio_name}"
    )

    print(
        f"  Valid rows : {len(valid):,}"
    )

    print(
        f"  Min        : {valid.min():,.6f}"
    )

    print(
        f"  Median     : {valid.median():,.6f}"
    )

    print(
        f"  95th pct   : "
        f"{valid.quantile(0.95):,.6f}"
    )

    print(
        f"  99th pct   : "
        f"{valid.quantile(0.99):,.6f}"
    )

    print(
        f"  Max        : {valid.max():,.6f}"
    )

    print(
        f"  > 1 rows   : {above_one:,}"
    )

    print(
        f"  < 0 rows   : {below_zero:,}"
    )

    ratio_summary_records.append(
        {
            "ratio": ratio_name,
            "valid_rows": len(valid),
            "min": valid.min(),
            "median": valid.median(),
            "p95": valid.quantile(0.95),
            "p99": valid.quantile(0.99),
            "max": valid.max(),
            "above_1_rows": int(
                above_one
            ),
            "below_0_rows": int(
                below_zero
            ),
        }
    )


ratio_summary_df = pd.DataFrame(
    ratio_summary_records
)


# ============================================================
# 14. STANDARDIZED PAYMENT RECONCILIATION
# ============================================================
# This is particularly important because Stage 4 showed that
# standardized_payment_ratio behaved unexpectedly.
#
# We compare:
#
# Medical standardized + Drug standardized
#                     vs
# Total standardized
#
# AND:
#
# Total payment / Total standardized
#
# The latter is diagnostic only.
# ============================================================

print_header(
    "8. STANDARDIZED PAYMENT INVESTIGATION"
)

total_standardized = diagnostics[
    f"__num_{SOURCE_COLUMNS['total_standardized']}"
]

medical_standardized = diagnostics[
    f"__num_{SOURCE_COLUMNS['medical_standardized']}"
]

drug_standardized = diagnostics[
    f"__num_{SOURCE_COLUMNS['drug_standardized']}"
]

total_payment = diagnostics[
    f"__num_{SOURCE_COLUMNS['total_payment']}"
]


diagnostics[
    "standardized_payment_ratio_raw"
] = safe_divide(
    total_payment,
    total_standardized,
)


standardized_component_sum = (
    medical_standardized
    + drug_standardized
)


diagnostics[
    "standardized_component_sum"
] = standardized_component_sum


diagnostics[
    "standardized_component_difference"
] = (
    standardized_component_sum
    - total_standardized
)


diagnostics[
    "standardized_component_ratio"
] = safe_divide(
    standardized_component_sum,
    total_standardized,
)


standardized_valid = (
    total_standardized.notna()
    & total_payment.notna()
)


standardized_ratio = diagnostics[
    "standardized_payment_ratio_raw"
].dropna()


print(
    f"Valid payment / standardized ratios : "
    f"{len(standardized_ratio):,}"
)


if not standardized_ratio.empty:

    print(
        f"Minimum ratio : "
        f"{standardized_ratio.min():,.6f}"
    )

    print(
        f"Median ratio  : "
        f"{standardized_ratio.median():,.6f}"
    )

    print(
        f"95th pct      : "
        f"{standardized_ratio.quantile(0.95):,.6f}"
    )

    print(
        f"99th pct      : "
        f"{standardized_ratio.quantile(0.99):,.6f}"
    )

    print(
        f"Maximum ratio : "
        f"{standardized_ratio.max():,.6f}"
    )

    print(
        f"Ratios > 1   : "
        f"{(standardized_ratio > 1).sum():,}"
    )

    print(
        f"Ratios < 0   : "
        f"{(standardized_ratio < 0).sum():,}"
    )


standardized_component_difference = diagnostics[
    "standardized_component_difference"
]

standardized_valid_components = (
    total_standardized.notna()
    & medical_standardized.notna()
    & drug_standardized.notna()
)


standardized_component_match = (
    np.isclose(
        standardized_component_sum,
        total_standardized,
        rtol=1e-9,
        atol=1e-6,
    )
    & standardized_valid_components
)


print(
    f"\nStandardized component valid rows : "
    f"{standardized_valid_components.sum():,}"
)

print(
    f"Standardized components match total: "
    f"{standardized_component_match.sum():,}"
)

standardized_mismatch_count = int(
    (
        standardized_valid_components
        & ~standardized_component_match
    ).sum()
)

print(
    f"Standardized mismatches            : "
    f"{standardized_mismatch_count:,}"
)

print(
    f"Maximum standardized difference    : "
    f"{standardized_component_difference.abs().max():,.6f}"
)


# ============================================================
# 15. SUSPICIOUS RELATIONSHIP FLAGS
# ============================================================
# These are diagnostic flags only.
#
# They do NOT mean the records are errors.
# ============================================================

print_header(
    "9. SUSPICIOUS RELATIONSHIP FLAGS"
)

suspicious_flags = []

for column in diagnostics.columns:

    if column.startswith(
        "components_gt_total_"
    ):

        suspicious_flags.append(
            diagnostics[column]
        )


if suspicious_flags:

    combined_suspicious = suspicious_flags[0].copy()

    for flag in suspicious_flags[1:]:

        combined_suspicious = (
            combined_suspicious
            | flag
        )

else:

    combined_suspicious = pd.Series(
        False,
        index=diagnostics.index,
    )


diagnostics[
    "raw_component_relationship_suspicious"
] = combined_suspicious.fillna(False)


suspicious_count = int(
    diagnostics[
        "raw_component_relationship_suspicious"
    ].sum()
)


print(
    f"Rows with at least one "
    f"component > total relationship: "
    f"{suspicious_count:,}"
)

print(
    f"Percentage: "
    f"{suspicious_count / len(df) * 100:.4f}%"
)


# ============================================================
# 16. SUSPICIOUS RECORDS BY YEAR
# ============================================================

print_header(
    "10. SUSPICIOUS RECORDS BY YEAR"
)

year_summary_df = (
    diagnostics
    .groupby(year_column)
    .agg(
        total_rows=(
            npi_column,
            "size",
        ),
        suspicious_rows=(
            "raw_component_relationship_suspicious",
            "sum",
        ),
    )
    .reset_index()
)


year_summary_df[
    "suspicious_pct"
] = safe_divide(
    year_summary_df["suspicious_rows"],
    year_summary_df["total_rows"],
) * 100


print(
    year_summary_df.to_string(
        index=False
    )
)


# ============================================================
# 17. PROVIDER TYPE DISTRIBUTION
# ============================================================

print_header(
    "11. SUSPICIOUS RECORDS BY PROVIDER TYPE"
)

provider_type_column = (
    SOURCE_COLUMNS["provider_type"]
)


if provider_type_column in diagnostics.columns:

    provider_type_summary = (
        diagnostics
        .groupby(
            provider_type_column,
            dropna=False,
        )
        .agg(
            total_rows=(
                npi_column,
                "size",
            ),
            suspicious_rows=(
                "raw_component_relationship_suspicious",
                "sum",
            ),
        )
        .reset_index()
    )

    provider_type_summary[
        "suspicious_pct"
    ] = safe_divide(
        provider_type_summary[
            "suspicious_rows"
        ],
        provider_type_summary[
            "total_rows"
        ],
    ) * 100

    provider_type_summary = (
        provider_type_summary
        .sort_values(
            "suspicious_rows",
            ascending=False,
        )
    )

    print(
        provider_type_summary
        .head(25)
        .to_string(
            index=False
        )
    )


# ============================================================
# 18. TOP SUSPICIOUS RECORDS
# ============================================================

print_header(
    "12. TOP SUSPICIOUS RECORDS"
)

suspicious_df = diagnostics[
    diagnostics[
        "raw_component_relationship_suspicious"
    ]
].copy()


display_columns = [
    npi_column,
    year_column,
    provider_type_column,

    SOURCE_COLUMNS["total_services"],
    SOURCE_COLUMNS["medical_services"],
    SOURCE_COLUMNS["drug_services"],

    SOURCE_COLUMNS["total_payment"],
    SOURCE_COLUMNS["medical_payment"],
    SOURCE_COLUMNS["drug_payment"],

    SOURCE_COLUMNS["total_allowed"],
    SOURCE_COLUMNS["medical_allowed"],
    SOURCE_COLUMNS["drug_allowed"],

    SOURCE_COLUMNS["total_standardized"],
    SOURCE_COLUMNS["medical_standardized"],
    SOURCE_COLUMNS["drug_standardized"],

    "medical_payment_to_total",
    "drug_payment_to_total",
    "medical_services_to_total",
    "drug_services_to_total",

    "standardized_payment_ratio_raw",
]


display_columns = [
    column
    for column in display_columns
    if column in suspicious_df.columns
]


if not suspicious_df.empty:

    # Create a diagnostic sorting metric.
    ratio_columns_for_sort = [
        column
        for column in [
            "medical_payment_to_total",
            "drug_payment_to_total",
            "medical_services_to_total",
            "drug_services_to_total",
            "medical_allowed_to_total",
            "drug_allowed_to_total",
        ]
        if column in suspicious_df.columns
    ]

    if ratio_columns_for_sort:

        suspicious_df[
            "__largest_component_ratio"
        ] = suspicious_df[
            ratio_columns_for_sort
        ].abs().max(
            axis=1
        )

        suspicious_df = (
            suspicious_df
            .sort_values(
                "__largest_component_ratio",
                ascending=False,
            )
        )

    print(
        suspicious_df[
            display_columns
        ]
        .head(30)
        .to_string(
            index=False
        )
    )

else:

    print(
        "No component > total records found."
    )


# ============================================================
# 19. REPEATED COMPONENT VALUES
# ============================================================
# This checks whether the same exact numeric component values
# appear repeatedly.
#
# Repetition does NOT automatically indicate bad data.
# It is only a diagnostic clue.
# ============================================================

print_header(
    "13. REPEATED COMPONENT VALUE INSPECTION"
)

repeat_records = []


for logical_name, column in SOURCE_COLUMNS.items():

    if logical_name in [
        "npi",
        "year",
        "provider_type",
    ]:

        continue

    numeric_column = (
        f"__num_{column}"
    )

    series = diagnostics[
        numeric_column
    ]

    value_counts = (
        series
        .value_counts(
            dropna=True
        )
    )

    repeated_values = (
        value_counts[
            value_counts > 1
        ]
    )

    repeat_records.append(
        {
            "logical_field": logical_name,
            "source_column": column,
            "distinct_values": int(
                value_counts.size
            ),
            "repeated_distinct_values": int(
                repeated_values.size
            ),
            "rows_in_repeated_values": int(
                repeated_values.sum()
            ),
            "most_repeated_value": (
                repeated_values.index[0]
                if not repeated_values.empty
                else np.nan
            ),
            "most_repeated_count": (
                int(
                    repeated_values.iloc[0]
                )
                if not repeated_values.empty
                else 0
            ),
        }
    )


repeat_summary_df = pd.DataFrame(
    repeat_records
)


print(
    repeat_summary_df.to_string(
        index=False
    )
)


# ============================================================
# 20. SAVE DIAGNOSTIC CSV
# ============================================================

print_header(
    "14. SAVING DIAGNOSTIC OUTPUT"
)

# Remove temporary numeric copies only.
# Calculated diagnostic columns are retained.
temporary_columns = [
    column
    for column in diagnostics.columns
    if column.startswith("__num_")
]


diagnostic_output = diagnostics.drop(
    columns=temporary_columns,
    errors="ignore",
)


diagnostic_output.to_csv(
    DIAGNOSTIC_FILE,
    index=False,
)


summary_output = pd.concat(
    [
        source_summary_df,
        reconciliation_summary_df,
    ],
    axis=0,
    ignore_index=True,
)


summary_output.to_csv(
    SUMMARY_FILE,
    index=False,
)


year_summary_df.to_csv(
    YEAR_SUMMARY_FILE,
    index=False,
)


print(
    f"Diagnostic file:\n"
    f"{DIAGNOSTIC_FILE}"
)

print(
    f"Summary file:\n"
    f"{SUMMARY_FILE}"
)

print(
    f"Year summary file:\n"
    f"{YEAR_SUMMARY_FILE}"
)


# ============================================================
# 21. FINAL OUTPUT VALIDATION
# ============================================================

print_header(
    "15. FINAL OUTPUT VALIDATION"
)

output_rows = len(
    diagnostic_output
)


if output_rows == len(df):

    print(
        "PASS: Diagnostic output "
        "preserved row count."
    )

else:

    print(
        "FAIL: Diagnostic output "
        "changed row count."
    )


output_duplicate_npi_year = (
    diagnostic_output
    .duplicated(
        subset=[
            npi_column,
            year_column,
        ]
    )
    .sum()
)


if (
    output_duplicate_npi_year
    == duplicate_npi_year_rows
):

    print(
        "PASS: NPI + Year grain "
        "preserved."
    )

else:

    print(
        "FAIL: NPI + Year grain "
        "changed."
    )


print(
    "\nNo source rows were removed."
)

print(
    "No source values were modified."
)

print(
    "No outlier treatment was performed."
)

print(
    "No winsorization was performed."
)

print(
    "No imputation was performed."
)

print(
    "\nRAW COMPONENT INSPECTION COMPLETE."
)

print(
    "Review the diagnostic output "
    "before making any outlier decision."
)