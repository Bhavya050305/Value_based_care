# ============================================================
# ACO ANALYTICS - MAIN PIPELINE
# ============================================================

import sys
from pathlib import Path

import numpy as np
import pandas as pd


# ------------------------------------------------------------
# ADD PROJECT ROOT TO PYTHON PATH
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


# ------------------------------------------------------------
# IMPORT PROJECT MODULES
# ------------------------------------------------------------

from ml.src.data_loader import (
    load_aco_performance
)

from ml.src.preprocessing import (
    preprocess_data
)

from ml.src.feature_engineering import (
    build_quality_analytics,
    build_quality_measure_analytics,
    build_member_analytics,
    build_aco_analytics
)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("================================================")
    print("ACO QUALITY + MEMBER ANALYTICS PIPELINE")
    print("================================================")
    print()

    # --------------------------------------------------------
    # STEP 1 — LOAD FROM SUPABASE
    # --------------------------------------------------------

    df = load_aco_performance()

    # --------------------------------------------------------
    # STEP 2 — PREPROCESS
    # --------------------------------------------------------

    (
        df,
        quality_measure_columns
    ) = preprocess_data(df)

    # --------------------------------------------------------
    # STEP 3 — QUALITY ENGINE
    # --------------------------------------------------------

    quality = build_quality_analytics(

        df,

        quality_measure_columns
    )

    # --------------------------------------------------------
    # STEP 4 — QUALITY MEASURES
    # --------------------------------------------------------

    (
        measure_data,
        measure_summary
    ) = build_quality_measure_analytics(

        df,

        quality_measure_columns
    )

    # --------------------------------------------------------
    # STEP 5 — MEMBER ENGINE
    # --------------------------------------------------------

    member = build_member_analytics(
        df
    )

    # --------------------------------------------------------
    # STEP 6 — FINAL ANALYTICS
    # --------------------------------------------------------

    aco_analytics = build_aco_analytics(

        quality,

        measure_data,

        measure_summary,

        member
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    print()
    print("================================================")
    print("FINAL VALIDATION")
    print("================================================")

    print(
        "Rows:",
        len(aco_analytics)
    )

    print(
        "Unique ACOs:",
        aco_analytics["aco_id"].nunique()
    )

    print(
        "Years:",
        sorted(
            aco_analytics[
                "performance_year"
            ]
            .dropna()
            .unique()
        )
    )

    # --------------------------------------------------------
    # CHECK DUPLICATES
    # --------------------------------------------------------

    duplicate_count = (
        aco_analytics
        .duplicated(
            subset=[
                "aco_id",
                "performance_year"
            ]
        )
        .sum()
    )

    print(
        "Duplicate ACO + Year rows:",
        duplicate_count
    )

    if duplicate_count != 0:

        raise ValueError(
            "Duplicate aco_id + performance_year "
            "rows found."
        )

    # --------------------------------------------------------
    # CHECK PERCENTAGES
    # --------------------------------------------------------

    distribution_percentage_columns = [

        col

        for col in aco_analytics.columns

        if col.endswith("_pct")

        and col not in [
            "quality_change_yoy_pct",
            "beneficiary_change_yoy_pct",
            "risk_score_change_pct"
        ]
    ]

    invalid_distribution_percentages = {}

    for col in distribution_percentage_columns:

        invalid = (

            (
                aco_analytics[col] < 0
            )

            |

            (
                aco_analytics[col] > 100
            )

        ).sum()

        if invalid > 0:

            invalid_distribution_percentages[
                col
            ] = int(invalid)

    print(
        "Invalid distribution percentages:",
        invalid_distribution_percentages
    )

    # --------------------------------------------------------
    # CHECK CHANGE PERCENTAGES
    # --------------------------------------------------------

    change_percentage_columns = [

        "quality_change_yoy_pct",

        "beneficiary_change_yoy_pct",

        "risk_score_change_pct"
    ]

    invalid_change_percentages = {}

    for col in change_percentage_columns:

        if col not in aco_analytics.columns:
            continue

        values = (
            aco_analytics[col]
            .dropna()
        )

        invalid = (
            ~np.isfinite(values)
        ).sum()

        if invalid > 0:

            invalid_change_percentages[
                col
            ] = int(invalid)

    print(
        "Invalid change percentages:",
        invalid_change_percentages
    )

    # --------------------------------------------------------
    # SAVE LOCAL CSV
    # --------------------------------------------------------

    output_directory = (
        PROJECT_ROOT
        / "ml"
        / "data"
        / "processed"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_directory
        / "aco_analytics.csv"
    )

    aco_analytics.to_csv(
        output_file,
        index=False
    )

    print()
    print(
        "CSV saved to:"
    )

    print(
        output_file
    )

    # --------------------------------------------------------
    # DISPLAY SAMPLE
    # --------------------------------------------------------

    print()
    print("Sample output:")

    print(
        aco_analytics[
            [
                "aco_id",
                "aco_name",
                "performance_year",
                "quality_score",
                "quality_change_yoy",
                "assigned_beneficiaries",
                "average_available_risk_score",
                "risk_profile_category"
            ]
        ].head(10).to_string(
            index=False
        )
    )

    print()
    print("================================================")
    print("ANALYTICS PIPELINE COMPLETED")
    print("================================================")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()