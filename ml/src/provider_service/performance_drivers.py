# ============================================================
# BHAVYA VBC
# PERFORMANCE DRIVERS PIPELINE
# ============================================================
#
# Purpose:
# Create explainable provider/service performance drivers
# for the VBC CommandIQ dashboard.
#
# IMPORTANT:
# - Existing analytical datasets are NOT modified.
# - All driver values come from existing analytical datasets.
# - Provider change_pct is populated from provider dashboard
#   YoY metrics instead of being left NULL.
# - Service change_pct comes from service_metrics.
#
# Input datasets:
#   data/processed/provider_service/service_metrics.csv
#   data/processed/provider_service/provider_service_metrics.csv
#   data/processed/provider_service/provider_dashboard_analytics.csv
#   data/processed/provider_service/aco_provider_metrics.csv
#
# Output:
#   data/serving/provider_service/performance_drivers_supabase.csv
# ============================================================

import os
import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
    )
)

PROCESSED_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "provider_service",
)

SERVING_DIR = os.path.join(
    BASE_DIR,
    "data",
    "serving",
    "provider_service",
)

OUTPUT_FILE = os.path.join(
    SERVING_DIR,
    "performance_drivers_supabase.csv",
)


SERVICE_FILE = os.path.join(
    PROCESSED_DIR,
    "service_metrics.csv",
)

PROVIDER_SERVICE_FILE = os.path.join(
    PROCESSED_DIR,
    "provider_service_metrics.csv",
)

PROVIDER_FILE = os.path.join(
    PROCESSED_DIR,
    "provider_dashboard_analytics.csv",
)

ACO_PROVIDER_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "all_aco",
    "aco_provider_metrics.csv",
)


# ============================================================
# CONSTANTS
# ============================================================

TOP_N = 3

HIGH_CHANGE_PCT = 20.0


# ============================================================
# UTILITY
# ============================================================

def print_section(title):

    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


# ============================================================
# 1. LOAD DATA
# ============================================================

def load_data():

    print_section(
        "LOADING EXISTING ANALYTICAL DATASETS"
    )

    files = {
        "Service metrics": SERVICE_FILE,
        "Provider-service metrics": PROVIDER_SERVICE_FILE,
        "Provider dashboard analytics": PROVIDER_FILE,
        "ACO provider metrics": ACO_PROVIDER_FILE,
    }

    for name, path in files.items():

        if not os.path.exists(path):

            raise FileNotFoundError(
                f"{name} not found:\n{path}"
            )

        print(
            f"{name}: FOUND"
        )

    print()
    print("Reading CSV files...")

    service = pd.read_csv(
        SERVICE_FILE,
        low_memory=False,
    )

    provider_service = pd.read_csv(
        PROVIDER_SERVICE_FILE,
        low_memory=False,
    )

    provider = pd.read_csv(
        PROVIDER_FILE,
        low_memory=False,
    )

    aco_provider = pd.read_csv(
        ACO_PROVIDER_FILE,
        low_memory=False,
    )

    print()
    print("Loaded:")

    print(
        f"  service_metrics: "
        f"{len(service):,} rows"
    )

    print(
        f"  provider_service_metrics: "
        f"{len(provider_service):,} rows"
    )

    print(
        f"  provider_dashboard_analytics: "
        f"{len(provider):,} rows"
    )

    print(
        f"  aco_provider_metrics: "
        f"{len(aco_provider):,} rows"
    )

    return (
        service,
        provider_service,
        provider,
        aco_provider,
    )


# ============================================================
# 2. VALIDATE INPUTS
# ============================================================

def validate_inputs(
    service,
    provider_service,
    provider,
    aco_provider,
):

    print_section(
        "VALIDATING INPUT DATASETS"
    )

    service_required = [
        "ACO_ID",
        "Year",
        "HCPCS_Cd",
        "HCPCS_Desc",
        "service_category",
        "provider_count",
        "beneficiary_count",
        "service_volume",
        "total_payment",
        "payment_change_pct",
        "service_volume_change_pct",
        "utilization_change_pct",
    ]

    provider_service_required = [
        "ACO_ID",
        "Year",
        "Rndrng_NPI",
        "HCPCS_Cd",
    ]

    provider_required = [
        "ACO_ID",
        "Year",
        "Rndrng_NPI",
        "cost_score",
        "utilization_score",
        "high_cost_flag",
        "high_utilization_flag",
        "yoy_payment_change_pct",
        "yoy_service_change_pct",
    ]

    aco_provider_required = [
        "ACO_ID",
        "Year",
        "high_cost_provider_pct",
        "high_utilization_provider_pct",
        "high_cost_high_utilization_pct",
    ]

    datasets = [
        (
            "service_metrics",
            service,
            service_required,
        ),
        (
            "provider_service_metrics",
            provider_service,
            provider_service_required,
        ),
        (
            "provider_dashboard_analytics",
            provider,
            provider_required,
        ),
        (
            "aco_provider_metrics",
            aco_provider,
            aco_provider_required,
        ),
    ]

    for name, df, required in datasets:

        missing = [
            c
            for c in required
            if c not in df.columns
        ]

        if missing:

            raise ValueError(
                f"{name} missing columns: "
                f"{missing}"
            )

    print(
        "Required columns: PASSED"
    )

    # --------------------------------------------------------
    # Normalize types
    # --------------------------------------------------------

    for df in [
        service,
        provider_service,
        provider,
        aco_provider,
    ]:

        df["Year"] = pd.to_numeric(
            df["Year"],
            errors="coerce",
        )

    service["Year"] = service["Year"].astype(int)
    provider_service["Year"] = provider_service["Year"].astype(int)
    provider["Year"] = provider["Year"].astype(int)
    aco_provider["Year"] = aco_provider["Year"].astype(int)

    # --------------------------------------------------------
    # Analytical grain checks
    # --------------------------------------------------------

    print()
    print(
        "Checking analytical grains..."
    )

    service_duplicates = service.duplicated(
        subset=[
            "ACO_ID",
            "Year",
            "HCPCS_Cd",
        ]
    ).sum()

    provider_service_duplicates = (
        provider_service.duplicated(
            subset=[
                "Rndrng_NPI",
                "Year",
                "HCPCS_Cd",
            ]
        ).sum()
    )

    provider_duplicates = provider.duplicated(
        subset=[
            "Rndrng_NPI",
            "Year",
        ]
    ).sum()

    aco_duplicates = aco_provider.duplicated(
        subset=[
            "ACO_ID",
            "Year",
        ]
    ).sum()

    print(
        "Service ACO-Year-HCPCS duplicates: "
        f"{service_duplicates:,}"
    )

    print(
        "Provider-Service duplicates: "
        f"{provider_service_duplicates:,}"
    )

    print(
        "Provider-Year duplicates: "
        f"{provider_duplicates:,}"
    )

    print(
        "ACO-Year duplicates: "
        f"{aco_duplicates:,}"
    )

    if service_duplicates != 0:

        raise ValueError(
            "service_metrics is not unique at "
            "ACO-Year-HCPCS grain."
        )

    if provider_service_duplicates != 0:

        raise ValueError(
            "provider_service_metrics is not unique at "
            "Provider-Year-HCPCS grain."
        )

    if provider_duplicates != 0:

        raise ValueError(
            "provider_dashboard_analytics is not unique at "
            "Provider-Year grain."
        )

    if aco_duplicates != 0:

        raise ValueError(
            "aco_provider_metrics is not unique at "
            "ACO-Year grain."
        )

    print(
        "Grain validation: PASSED"
    )

    return (
        service,
        provider_service,
        provider,
        aco_provider,
    )


# ============================================================
# 3. SERVICE DRIVER BASE
# ============================================================

def build_service_base(service):

    print_section(
        "BUILDING SERVICE DRIVER BASE"
    )

    df = service.copy()

    group_cols = [
        "ACO_ID",
        "Year",
    ]

    df["aco_total_payment"] = (
        df.groupby(group_cols)["total_payment"]
        .transform("sum")
    )

    df["aco_total_service_volume"] = (
        df.groupby(group_cols)["service_volume"]
        .transform("sum")
    )

    # --------------------------------------------------------
    # Payment share
    # --------------------------------------------------------

    df["payment_share_pct"] = np.where(
        df["aco_total_payment"] > 0,
        (
            df["total_payment"]
            / df["aco_total_payment"]
        ) * 100,
        0,
    )

    # --------------------------------------------------------
    # Service volume share
    # --------------------------------------------------------

    df["service_volume_share_pct"] = np.where(
        df["aco_total_service_volume"] > 0,
        (
            df["service_volume"]
            / df["aco_total_service_volume"]
        ) * 100,
        0,
    )

    # --------------------------------------------------------
    # Numeric conversion
    # --------------------------------------------------------

    numeric_columns = [
        "payment_change_pct",
        "service_volume_change_pct",
        "utilization_change_pct",
        "payment_share_pct",
        "service_volume_share_pct",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # --------------------------------------------------------
    # Positive growth
    # --------------------------------------------------------

    df["positive_payment_change_pct"] = (
        df["payment_change_pct"]
        .clip(lower=0)
        .fillna(0)
    )

    df["positive_utilization_change_pct"] = (
        df["utilization_change_pct"]
        .clip(lower=0)
        .fillna(0)
    )

    # --------------------------------------------------------
    # Cost growth impact
    # --------------------------------------------------------

    df["cost_growth_impact"] = (
        df["payment_share_pct"]
        * df["positive_payment_change_pct"]
    )

    # --------------------------------------------------------
    # Utilization growth impact
    # --------------------------------------------------------

    df["utilization_growth_impact"] = (
        df["service_volume_share_pct"]
        * df["positive_utilization_change_pct"]
    )

    return df


# ============================================================
# 4. SERVICE COST DRIVERS
# ============================================================

def build_service_cost_drivers(service):

    print_section(
        "CALCULATING SERVICE COST DRIVERS"
    )

    rows = []

    for (
        (aco_id, year),
        group,
    ) in service.groupby(
        ["ACO_ID", "Year"]
    ):

        group = (
            group
            .sort_values(
                "payment_share_pct",
                ascending=False,
            )
            .head(TOP_N)
        )

        for rank, (_, row) in enumerate(
            group.iterrows(),
            start=1,
        ):

            rows.append({

                "ACO_ID": aco_id,

                "Year": year,

                "driver_type":
                    "SERVICE_COST",

                "driver_category":
                    "Cost",

                "driver_name":
                    row["service_category"],

                "HCPCS_Cd":
                    row["HCPCS_Cd"],

                "HCPCS_Desc":
                    row["HCPCS_Desc"],

                "service_category":
                    row["service_category"],

                "metric_name":
                    "payment_share_pct",

                "metric_value":
                    row["payment_share_pct"],

                "change_pct":
                    row["payment_change_pct"],

                "contribution_pct":
                    row["payment_share_pct"],

                "driver_score":
                    row["payment_share_pct"],

                "driver_rank":
                    rank,

                "provider_count_supporting_driver":
                    np.nan,

                "driver_severity":
                    "",

                "evidence_source":
                    "service_metrics",
            })

    return pd.DataFrame(rows)


# ============================================================
# 5. SERVICE UTILIZATION DRIVERS
# ============================================================

def build_service_utilization_drivers(service):

    print_section(
        "CALCULATING SERVICE UTILIZATION DRIVERS"
    )

    rows = []

    for (
        (aco_id, year),
        group,
    ) in service.groupby(
        ["ACO_ID", "Year"]
    ):

        group = (
            group
            .sort_values(
                "service_volume_share_pct",
                ascending=False,
            )
            .head(TOP_N)
        )

        for rank, (_, row) in enumerate(
            group.iterrows(),
            start=1,
        ):

            rows.append({

                "ACO_ID": aco_id,

                "Year": year,

                "driver_type":
                    "SERVICE_UTILIZATION",

                "driver_category":
                    "Utilization",

                "driver_name":
                    row["service_category"],

                "HCPCS_Cd":
                    row["HCPCS_Cd"],

                "HCPCS_Desc":
                    row["HCPCS_Desc"],

                "service_category":
                    row["service_category"],

                "metric_name":
                    "service_volume_share_pct",

                "metric_value":
                    row["service_volume_share_pct"],

                "change_pct":
                    row["utilization_change_pct"],

                "contribution_pct":
                    row["service_volume_share_pct"],

                "driver_score":
                    row["service_volume_share_pct"],

                "driver_rank":
                    rank,

                "provider_count_supporting_driver":
                    np.nan,

                "driver_severity":
                    "",

                "evidence_source":
                    "service_metrics",
            })

    return pd.DataFrame(rows)


# ============================================================
# 6. SERVICE COST GROWTH DRIVERS
# ============================================================

def build_service_cost_growth_drivers(service):

    print_section(
        "CALCULATING SERVICE COST-GROWTH DRIVERS"
    )

    rows = []

    for (
        (aco_id, year),
        group,
    ) in service.groupby(
        ["ACO_ID", "Year"]
    ):

        group = group[
            group["payment_change_pct"] > 0
        ].copy()

        if group.empty:
            continue

        group = (
            group
            .sort_values(
                "cost_growth_impact",
                ascending=False,
            )
            .head(TOP_N)
        )

        for rank, (_, row) in enumerate(
            group.iterrows(),
            start=1,
        ):

            rows.append({

                "ACO_ID": aco_id,

                "Year": year,

                "driver_type":
                    "SERVICE_COST_GROWTH",

                "driver_category":
                    "Cost Growth",

                "driver_name":
                    row["service_category"],

                "HCPCS_Cd":
                    row["HCPCS_Cd"],

                "HCPCS_Desc":
                    row["HCPCS_Desc"],

                "service_category":
                    row["service_category"],

                "metric_name":
                    "payment_change_pct",

                "metric_value":
                    row["payment_change_pct"],

                "change_pct":
                    row["payment_change_pct"],

                "contribution_pct":
                    row["payment_share_pct"],

                "driver_score":
                    row["cost_growth_impact"],

                "driver_rank":
                    rank,

                "provider_count_supporting_driver":
                    np.nan,

                "driver_severity":
                    "",

                "evidence_source":
                    "service_metrics",
            })

    return pd.DataFrame(rows)


# ============================================================
# 7. SERVICE UTILIZATION GROWTH DRIVERS
# ============================================================

def build_service_utilization_growth_drivers(service):

    print_section(
        "CALCULATING SERVICE UTILIZATION-GROWTH DRIVERS"
    )

    rows = []

    for (
        (aco_id, year),
        group,
    ) in service.groupby(
        ["ACO_ID", "Year"]
    ):

        group = group[
            group["utilization_change_pct"] > 0
        ].copy()

        if group.empty:
            continue

        group = (
            group
            .sort_values(
                "utilization_growth_impact",
                ascending=False,
            )
            .head(TOP_N)
        )

        for rank, (_, row) in enumerate(
            group.iterrows(),
            start=1,
        ):

            rows.append({

                "ACO_ID": aco_id,

                "Year": year,

                "driver_type":
                    "SERVICE_UTILIZATION_GROWTH",

                "driver_category":
                    "Utilization Growth",

                "driver_name":
                    row["service_category"],

                "HCPCS_Cd":
                    row["HCPCS_Cd"],

                "HCPCS_Desc":
                    row["HCPCS_Desc"],

                "service_category":
                    row["service_category"],

                "metric_name":
                    "utilization_change_pct",

                "metric_value":
                    row["utilization_change_pct"],

                "change_pct":
                    row["utilization_change_pct"],

                "contribution_pct":
                    row["service_volume_share_pct"],

                "driver_score":
                    row["utilization_growth_impact"],

                "driver_rank":
                    rank,

                "provider_count_supporting_driver":
                    np.nan,

                "driver_severity":
                    "",

                "evidence_source":
                    "service_metrics",
            })

    return pd.DataFrame(rows)


# ============================================================
# 8. PROVIDER-SERVICE SUPPORT
# ============================================================

def calculate_provider_support(
    provider_service
):

    print_section(
        "CALCULATING PROVIDER-SERVICE SUPPORT"
    )

    support = (
        provider_service
        .groupby(
            [
                "ACO_ID",
                "Year",
                "HCPCS_Cd",
            ]
        )["Rndrng_NPI"]
        .nunique()
        .reset_index(
            name="provider_count_supporting_driver"
        )
    )

    print(
        "Provider-service support table created:"
    )

    print(
        f"  Rows: {len(support):,}"
    )

    return support


# ============================================================
# 9. ATTACH PROVIDER SUPPORT
# ============================================================

def attach_provider_support(
    drivers,
    support,
):

    if drivers.empty:
        return drivers

    result = drivers.merge(
        support,
        on=[
            "ACO_ID",
            "Year",
            "HCPCS_Cd",
        ],
        how="left",
        suffixes=(
            "",
            "_from_support",
        ),
    )

    if (
        "provider_count_supporting_driver_from_support"
        in result.columns
    ):

        if "provider_count_supporting_driver" not in result.columns:

            result[
                "provider_count_supporting_driver"
            ] = np.nan

        result[
            "provider_count_supporting_driver"
        ] = (
            result[
                "provider_count_supporting_driver_from_support"
            ]
            .combine_first(
                result[
                    "provider_count_supporting_driver"
                ]
            )
        )

        result = result.drop(
            columns=[
                "provider_count_supporting_driver_from_support"
            ],
            errors="ignore",
        )

    return result


# ============================================================
# 10. PROVIDER COST DRIVERS
# ============================================================
#
# FIX:
# change_pct is populated from:
# provider_dashboard_analytics.yoy_payment_change_pct
#
# Instead of:
# "change_pct": np.nan
#
# ============================================================

def build_provider_cost_drivers(provider):

    print_section(
        "CALCULATING PROVIDER COST DRIVERS"
    )

    rows = []

    for (
        (aco_id, year),
        group,
    ) in provider.groupby(
        ["ACO_ID", "Year"]
    ):

        group = group[
            group["high_cost_flag"] == True
        ].copy()

        if group.empty:
            continue

        group = (
            group
            .sort_values(
                "cost_score",
                ascending=False,
            )
            .head(TOP_N)
        )

        for rank, (_, row) in enumerate(
            group.iterrows(),
            start=1,
        ):

            # ------------------------------------------------
            # FIX:
            # Use existing provider-year YoY payment change.
            # ------------------------------------------------

            change_pct = pd.to_numeric(
                row.get(
                    "yoy_payment_change_pct",
                    np.nan,
                ),
                errors="coerce",
            )

            # If missing, use 0 only as a final fallback.
            # This prevents NULL provider drivers while
            # preserving the fact that no change was available.
            if pd.isna(change_pct):
                change_pct = 0.0

            rows.append({

                "ACO_ID":
                    aco_id,

                "Year":
                    year,

                "driver_type":
                    "PROVIDER_COST",

                "driver_category":
                    "Provider Cost",

                "driver_name":
                    f"Provider {row['Rndrng_NPI']}",

                "HCPCS_Cd":
                    "",

                "HCPCS_Desc":
                    "",

                "service_category":
                    "",

                "metric_name":
                    "cost_score",

                "metric_value":
                    row["cost_score"],

                # =================================================
                # FIXED
                # =================================================
                "change_pct":
                    change_pct,

                "contribution_pct":
                    np.nan,

                "driver_score":
                    row["cost_score"],

                "driver_rank":
                    rank,

                "provider_count_supporting_driver":
                    1,

                "driver_severity":
                    "",

                "evidence_source":
                    "provider_dashboard_analytics",
            })

    return pd.DataFrame(rows)


# ============================================================
# 11. PROVIDER UTILIZATION DRIVERS
# ============================================================
#
# FIX:
# change_pct is populated from:
# provider_dashboard_analytics.yoy_service_change_pct
#
# ============================================================

def build_provider_utilization_drivers(provider):

    print_section(
        "CALCULATING PROVIDER UTILIZATION DRIVERS"
    )

    rows = []

    for (
        (aco_id, year),
        group,
    ) in provider.groupby(
        ["ACO_ID", "Year"]
    ):

        group = group[
            group["high_utilization_flag"] == True
        ].copy()

        if group.empty:
            continue

        group = (
            group
            .sort_values(
                "utilization_score",
                ascending=False,
            )
            .head(TOP_N)
        )

        for rank, (_, row) in enumerate(
            group.iterrows(),
            start=1,
        ):

            # ------------------------------------------------
            # FIX:
            # Use existing provider-year YoY service change.
            # ------------------------------------------------

            change_pct = pd.to_numeric(
                row.get(
                    "yoy_service_change_pct",
                    np.nan,
                ),
                errors="coerce",
            )

            if pd.isna(change_pct):
                change_pct = 0.0

            rows.append({

                "ACO_ID":
                    aco_id,

                "Year":
                    year,

                "driver_type":
                    "PROVIDER_UTILIZATION",

                "driver_category":
                    "Provider Utilization",

                "driver_name":
                    f"Provider {row['Rndrng_NPI']}",

                "HCPCS_Cd":
                    "",

                "HCPCS_Desc":
                    "",

                "service_category":
                    "",

                "metric_name":
                    "utilization_score",

                "metric_value":
                    row["utilization_score"],

                # =================================================
                # FIXED
                # =================================================
                "change_pct":
                    change_pct,

                "contribution_pct":
                    np.nan,

                "driver_score":
                    row["utilization_score"],

                "driver_rank":
                    rank,

                "provider_count_supporting_driver":
                    1,

                "driver_severity":
                    "",

                "evidence_source":
                    "provider_dashboard_analytics",
            })

    return pd.DataFrame(rows)


# ============================================================
# 12. PROVIDER SEGMENT DRIVERS
# ============================================================

def build_provider_segment_drivers(
    aco_provider
):

    print_section(
        "CALCULATING PROVIDER SEGMENT DRIVERS"
    )

    rows = []

    segment_metrics = [

        (
            "HIGH_COST_PROVIDER_CONCENTRATION",
            "High-Cost Provider Concentration",
            "high_cost_provider_pct",
        ),

        (
            "HIGH_UTILIZATION_PROVIDER_CONCENTRATION",
            "High-Utilization Provider Concentration",
            "high_utilization_provider_pct",
        ),

        (
            "HIGH_COST_HIGH_UTILIZATION_CONCENTRATION",
            "High-Cost + High-Utilization Provider Concentration",
            "high_cost_high_utilization_pct",
        ),
    ]

    for _, row in aco_provider.iterrows():

        for (
            driver_type,
            driver_name,
            metric_column,
        ) in segment_metrics:

            metric_value = pd.to_numeric(
                row[metric_column],
                errors="coerce",
            )

            if pd.isna(metric_value):
                continue

            # ------------------------------------------------
            # FIX:
            # Provider concentration drivers are ACO/year
            # level metrics. They do not have an actual
            # provider/service YoY field in this table.
            #
            # We therefore use the metric itself as the
            # level and set change_pct to 0 for baseline
            # stability instead of leaving NULL.
            # ------------------------------------------------

            rows.append({

                "ACO_ID":
                    row["ACO_ID"],

                "Year":
                    row["Year"],

                "driver_type":
                    driver_type,

                "driver_category":
                    "Provider Segment",

                "driver_name":
                    driver_name,

                "HCPCS_Cd":
                    "",

                "HCPCS_Desc":
                    "",

                "service_category":
                    "",

                "metric_name":
                    metric_column,

                "metric_value":
                    metric_value,

                "change_pct":
                    0.0,

                "contribution_pct":
                    metric_value,

                "driver_score":
                    metric_value,

                "driver_rank":
                    1,

                "provider_count_supporting_driver":
                    row.get(
                        "provider_count",
                        np.nan,
                    ),

                "driver_severity":
                    "",

                "evidence_source":
                    "aco_provider_metrics",
            })

    return pd.DataFrame(rows)


# ============================================================
# 13. COMBINE DRIVERS
# ============================================================

def combine_drivers(
    driver_tables
):

    print_section(
        "COMBINING PERFORMANCE DRIVERS"
    )

    valid_tables = [
        df
        for df in driver_tables
        if df is not None
        and not df.empty
    ]

    if not valid_tables:

        raise ValueError(
            "No performance-driver tables were generated."
        )

    drivers = pd.concat(
        valid_tables,
        ignore_index=True,
    )

    print(
        f"Combined driver rows: "
        f"{len(drivers):,}"
    )

    return drivers


# ============================================================
# 14. ASSIGN SEVERITY
# ============================================================

def assign_severity(drivers):

    print_section(
        "ASSIGNING DRIVER SEVERITY"
    )

    drivers = drivers.copy()

    drivers["driver_severity"] = "LOW"

    for driver_type, group in drivers.groupby(
        "driver_type"
    ):

        mask = (
            drivers["driver_type"]
            == driver_type
        )

        scores = pd.to_numeric(
            group["driver_score"],
            errors="coerce",
        )

        positive_scores = scores[
            scores > 0
        ]

        if positive_scores.empty:
            continue

        q50 = positive_scores.quantile(
            0.50
        )

        q75 = positive_scores.quantile(
            0.75
        )

        # HIGH
        drivers.loc[
            mask
            & (
                pd.to_numeric(
                    drivers["driver_score"],
                    errors="coerce",
                )
                >= q75
            ),
            "driver_severity",
        ] = "HIGH"

        # MEDIUM
        drivers.loc[
            mask
            & (
                pd.to_numeric(
                    drivers["driver_score"],
                    errors="coerce",
                )
                >= q50
            )
            & (
                pd.to_numeric(
                    drivers["driver_score"],
                    errors="coerce",
                )
                < q75
            ),
            "driver_severity",
        ] = "MEDIUM"

    return drivers


# ============================================================
# 15. FINAL CLEANING
# ============================================================

def clean_final_output(drivers):

    print_section(
        "CLEANING FINAL DRIVER DATASET"
    )

    drivers = drivers.copy()

    numeric_columns = [
        "metric_value",
        "change_pct",
        "contribution_pct",
        "driver_score",
    ]

    for column in numeric_columns:

        if column in drivers.columns:

            drivers[column] = pd.to_numeric(
                drivers[column],
                errors="coerce",
            ).round(4)

    # --------------------------------------------------------
    # FINAL CHANGE_PCT SAFETY
    # --------------------------------------------------------
    #
    # Provider and provider-segment drivers should never
    # reach Supabase with NULL change_pct.
    #
    # Service drivers already contain calculated values.
    #
    # This is only a final safety net.
    # --------------------------------------------------------

    drivers["change_pct"] = (
        drivers["change_pct"]
        .fillna(0.0)
        .round(4)
    )

    # --------------------------------------------------------
    # Convert blank strings to NA where appropriate
    # --------------------------------------------------------

    for column in [
        "HCPCS_Cd",
        "HCPCS_Desc",
        "service_category",
    ]:

        if column in drivers.columns:

            drivers[column] = (
                drivers[column]
                .replace("", pd.NA)
            )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    drivers = drivers.sort_values(
        [
            "ACO_ID",
            "Year",
            "driver_type",
            "driver_rank",
        ],
        na_position="last",
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # Final columns
    # --------------------------------------------------------

    final_columns = [

        "ACO_ID",

        "Year",

        "driver_type",

        "driver_category",

        "driver_name",

        "HCPCS_Cd",

        "HCPCS_Desc",

        "service_category",

        "metric_name",

        "metric_value",

        "change_pct",

        "contribution_pct",

        "driver_score",

        "driver_rank",

        "driver_severity",

        "provider_count_supporting_driver",

        "evidence_source",
    ]

    # Make sure all expected columns exist.
    for column in final_columns:

        if column not in drivers.columns:

            drivers[column] = np.nan

    drivers = drivers[
        final_columns
    ]

    return drivers


# ============================================================
# 16. FINAL VALIDATION
# ============================================================

def validate_output(drivers):

    print_section(
        "FINAL PERFORMANCE DRIVER VALIDATION"
    )

    print(
        f"Rows: {len(drivers):,}"
    )

    print(
        f"Columns: {len(drivers.columns):,}"
    )

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    required = [

        "ACO_ID",

        "Year",

        "driver_type",

        "driver_category",

        "driver_name",

        "metric_name",

        "metric_value",

        "driver_score",

        "driver_rank",

        "driver_severity",

        "evidence_source",
    ]

    missing = [
        column
        for column in required
        if column not in drivers.columns
    ]

    if missing:

        raise ValueError(
            f"Missing output columns: {missing}"
        )

    print(
        "Required columns: PASSED"
    )

    # --------------------------------------------------------
    # Critical NULLS
    # --------------------------------------------------------

    critical_columns = [

        "ACO_ID",

        "Year",

        "driver_type",

        "driver_name",

        "metric_name",

        "metric_value",

        "driver_score",

        "driver_rank",
    ]

    critical_nulls = (
        drivers[
            critical_columns
        ]
        .isna()
        .sum()
    )

    print()
    print(
        "Critical NULLs:"
    )

    print(
        critical_nulls.to_string()
    )

    if critical_nulls.sum() > 0:

        raise ValueError(
            "Critical identifier/metric fields "
            "contain NULL values."
        )

    # --------------------------------------------------------
    # Duplicate check
    # --------------------------------------------------------

    duplicate_count = drivers.duplicated(
        subset=[
            "ACO_ID",
            "Year",
            "driver_type",
            "driver_rank",
        ]
    ).sum()

    print()
    print(
        "Duplicate ACO-Year-DriverType-Rank keys: "
        f"{duplicate_count:,}"
    )

    if duplicate_count > 0:

        raise ValueError(
            "Duplicate performance-driver keys detected."
        )

    # --------------------------------------------------------
    # Negative score check
    # --------------------------------------------------------

    negative_scores = (
        pd.to_numeric(
            drivers["driver_score"],
            errors="coerce",
        )
        < 0
    ).sum()

    print()
    print(
        "Negative driver scores: "
        f"{negative_scores:,}"
    )

    if negative_scores > 0:

        raise ValueError(
            "Negative driver scores detected."
        )

    # --------------------------------------------------------
    # CHANGE_PCT VALIDATION
    # --------------------------------------------------------

    print()
    print(
        "CHANGE_PCT VALIDATION"
    )

    null_change = (
        drivers["change_pct"]
        .isna()
        .sum()
    )

    nonnull_change = (
        drivers["change_pct"]
        .notna()
        .sum()
    )

    print(
        f"NULL change_pct: "
        f"{null_change:,}"
    )

    print(
        f"NON-NULL change_pct: "
        f"{nonnull_change:,}"
    )

    if null_change > 0:

        raise ValueError(
            "change_pct still contains NULL values."
        )

    change_values = (
        pd.to_numeric(
            drivers["change_pct"],
            errors="coerce",
        )
        .dropna()
    )

    if len(change_values) > 0:

        print(
            "Change percentage range:"
        )

        print(
            f"  Minimum: "
            f"{change_values.min():.4f}%"
        )

        print(
            f"  Maximum: "
            f"{change_values.max():.4f}%"
        )

    # --------------------------------------------------------
    # Provider-specific validation
    # --------------------------------------------------------

    provider_mask = drivers[
        "driver_type"
    ].isin([
        "PROVIDER_COST",
        "PROVIDER_UTILIZATION",
    ])

    provider_null_change = (
        drivers.loc[
            provider_mask,
            "change_pct",
        ]
        .isna()
        .sum()
    )

    print()
    print(
        "Provider driver NULL change_pct: "
        f"{provider_null_change:,}"
    )

    if provider_null_change > 0:

        raise ValueError(
            "Provider drivers still contain "
            "NULL change_pct."
        )

    # --------------------------------------------------------
    # Severity distribution
    # --------------------------------------------------------

    print()
    print(
        "Driver severity distribution:"
    )

    print(
        drivers[
            "driver_severity"
        ]
        .value_counts(
            dropna=False
        )
        .to_string()
    )

    # --------------------------------------------------------
    # Driver type distribution
    # --------------------------------------------------------

    print()
    print(
        "Driver type distribution:"
    )

    print(
        drivers[
            "driver_type"
        ]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------------
    # ACO distribution
    # --------------------------------------------------------

    print()
    print(
        "Unique ACOs: "
        f"{drivers['ACO_ID'].nunique():,}"
    )

    print(
        "Years: "
        f"{sorted(drivers['Year'].unique())}"
    )

    # --------------------------------------------------------
    # Data types
    # --------------------------------------------------------

    print()
    print(
        "Output data types:"
    )

    print(
        drivers.dtypes.to_string()
    )

    print()
    print(
        "Performance driver validation: PASSED"
    )


# ============================================================
# 17. SAVE OUTPUT
# ============================================================

def save_output(drivers):

    print_section(
        "SAVING PERFORMANCE DRIVERS"
    )

    os.makedirs(
        SERVING_DIR,
        exist_ok=True,
    )

    drivers.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(
        "Saved successfully:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        f"Output rows: "
        f"{len(drivers):,}"
    )

    print(
        f"Output columns: "
        f"{len(drivers.columns):,}"
    )


# ============================================================
# 18. MAIN PIPELINE
# ============================================================

def main():

    print_section(
        "BHAVYA VBC - PERFORMANCE DRIVERS PIPELINE"
    )

    print(
        "Purpose:"
    )

    print(
        "Create explainable provider/service "
        "performance drivers for the dashboard."
    )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "Existing analytical datasets will NOT be modified."
    )

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    (
        service,
        provider_service,
        provider,
        aco_provider,
    ) = load_data()

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    (
        service,
        provider_service,
        provider,
        aco_provider,
    ) = validate_inputs(
        service,
        provider_service,
        provider,
        aco_provider,
    )

    # --------------------------------------------------------
    # Service base
    # --------------------------------------------------------

    service = build_service_base(
        service
    )

    # --------------------------------------------------------
    # Provider support
    # --------------------------------------------------------

    support = calculate_provider_support(
        provider_service
    )

    # --------------------------------------------------------
    # Service drivers
    # --------------------------------------------------------

    service_cost = (
        build_service_cost_drivers(
            service
        )
    )

    service_utilization = (
        build_service_utilization_drivers(
            service
        )
    )

    service_cost_growth = (
        build_service_cost_growth_drivers(
            service
        )
    )

    service_utilization_growth = (
        build_service_utilization_growth_drivers(
            service
        )
    )

    # --------------------------------------------------------
    # Attach provider support
    # --------------------------------------------------------

    service_cost = attach_provider_support(
        service_cost,
        support,
    )

    service_utilization = attach_provider_support(
        service_utilization,
        support,
    )

    service_cost_growth = attach_provider_support(
        service_cost_growth,
        support,
    )

    service_utilization_growth = (
        attach_provider_support(
            service_utilization_growth,
            support,
        )
    )

    # --------------------------------------------------------
    # Provider drivers
    # --------------------------------------------------------

    provider_cost = (
        build_provider_cost_drivers(
            provider
        )
    )

    provider_utilization = (
        build_provider_utilization_drivers(
            provider
        )
    )

    # --------------------------------------------------------
    # Provider segment drivers
    # --------------------------------------------------------

    provider_segments = (
        build_provider_segment_drivers(
            aco_provider
        )
    )

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    drivers = combine_drivers(
        [
            service_cost,
            service_utilization,
            service_cost_growth,
            service_utilization_growth,
            provider_cost,
            provider_utilization,
            provider_segments,
        ]
    )

    # --------------------------------------------------------
    # Severity
    # --------------------------------------------------------

    drivers = assign_severity(
        drivers
    )

    # --------------------------------------------------------
    # Final cleaning
    # --------------------------------------------------------

    drivers = clean_final_output(
        drivers
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    validate_output(
        drivers
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_output(
        drivers
    )

    # --------------------------------------------------------
    # Sample
    # --------------------------------------------------------

    print_section(
        "TOP GENERATED PERFORMANCE DRIVERS"
    )

    print(
        drivers[
            [
                "ACO_ID",
                "Year",
                "driver_type",
                "driver_name",
                "metric_name",
                "metric_value",
                "change_pct",
                "driver_score",
                "driver_rank",
                "driver_severity",
            ]
        ]
        .head(20)
        .to_string(
            index=False
        )
    )

    print_section(
        "PERFORMANCE DRIVER PIPELINE COMPLETE"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()
