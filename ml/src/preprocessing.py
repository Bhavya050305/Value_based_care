# ============================================================
# ACO ANALYTICS - PREPROCESSING
# ============================================================

import pandas as pd
import numpy as np


# ------------------------------------------------------------
# REQUIRED SOURCE COLUMNS
# ------------------------------------------------------------

REQUIRED_COLUMNS = [

    "ACO_ID",
    "ACO_Name",
    "performance_year",

    "N_AB",
    "QualScore",
    "Met_QPS",

    "N_AB_Year_ESRD_BY3",
    "N_AB_Year_DIS_BY3",
    "N_AB_Year_AGED_Dual_BY3",
    "N_AB_Year_AGED_NonDual_BY3",

    "N_Ben_Age_0_64",
    "N_Ben_Age_65_74",
    "N_Ben_Age_75_84",
    "N_Ben_Age_85plus",

    "N_Ben_Female",
    "N_Ben_Male",

    "N_Ben_Race_White",
    "N_Ben_Race_Black",
    "N_Ben_Race_Asian",
    "N_Ben_Race_Hisp",
    "N_Ben_Race_Native",
    "N_Ben_Race_Other",
    "N_Ben_Race_Unknown",

    "Perc_Dual",

    "CMS_HCC_RiskScore_ESRD_BY3",
    "CMS_HCC_RiskScore_DIS_BY3",
    "CMS_HCC_RiskScore_AGDU_BY3",
    "CMS_HCC_RiskScore_AGND_BY3"
]


# ------------------------------------------------------------
# NUMERIC SOURCE COLUMNS
# ------------------------------------------------------------

MEMBER_NUMERIC_COLUMNS = [

    "N_AB",

    "N_AB_Year_ESRD_BY3",
    "N_AB_Year_DIS_BY3",
    "N_AB_Year_AGED_Dual_BY3",
    "N_AB_Year_AGED_NonDual_BY3",

    "N_Ben_Age_0_64",
    "N_Ben_Age_65_74",
    "N_Ben_Age_75_84",
    "N_Ben_Age_85plus",

    "N_Ben_Female",
    "N_Ben_Male",

    "N_Ben_Race_White",
    "N_Ben_Race_Black",
    "N_Ben_Race_Asian",
    "N_Ben_Race_Hisp",
    "N_Ben_Race_Native",
    "N_Ben_Race_Other",
    "N_Ben_Race_Unknown",

    "Perc_Dual"
]


RISK_COLUMNS = [

    "CMS_HCC_RiskScore_ESRD_BY3",
    "CMS_HCC_RiskScore_DIS_BY3",
    "CMS_HCC_RiskScore_AGDU_BY3",
    "CMS_HCC_RiskScore_AGND_BY3"
]


# ------------------------------------------------------------
# VALIDATE REQUIRED COLUMNS
# ------------------------------------------------------------

def validate_required_columns(df):

    missing = [
        col
        for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing required columns:\n"
            + "\n".join(missing)
        )

    print(
        "All required source columns are present."
    )


# ------------------------------------------------------------
# FIND QUALITY MEASURES
# ------------------------------------------------------------

def find_quality_measure_columns(df):

    quality_measure_columns = [

        col
        for col in df.columns

        if (
            col.startswith("CAHPS_")
            or col.startswith("Measure_")
            or col.startswith("QualityID_")
        )
    ]

    print(
        "Quality measure columns found:",
        len(quality_measure_columns)
    )

    return quality_measure_columns


# ------------------------------------------------------------
# NUMERIC CONVERSION
# ------------------------------------------------------------

def convert_numeric_columns(
    df,
    quality_measure_columns
):

    numeric_columns = (

        ["QualScore"]

        + quality_measure_columns

        + MEMBER_NUMERIC_COLUMNS

        + RISK_COLUMNS
    )

    numeric_columns = [

        col
        for col in numeric_columns
        if col in df.columns
    ]

    for col in numeric_columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df["performance_year"] = pd.to_numeric(
        df["performance_year"],
        errors="coerce"
    )

    print(
        "Numeric conversion completed."
    )

    return df


# ------------------------------------------------------------
# VALIDATE ACO + YEAR
# ------------------------------------------------------------

def validate_aco_year(df):

    duplicate_mask = df.duplicated(
        subset=[
            "ACO_ID",
            "performance_year"
        ],
        keep=False
    )

    duplicate_rows = df[
        duplicate_mask
    ]

    print(
        "Total rows:",
        len(df)
    )

    print(
        "Unique ACOs:",
        df["ACO_ID"].nunique()
    )

    print(
        "Performance years:",
        sorted(
            df["performance_year"]
            .dropna()
            .unique()
        )
    )

    print(
        "Duplicate ACO + Year rows:",
        len(duplicate_rows)
    )

    if len(duplicate_rows) > 0:

        print(
            duplicate_rows[
                [
                    "ACO_ID",
                    "ACO_Name",
                    "performance_year"
                ]
            ].sort_values(
                [
                    "ACO_ID",
                    "performance_year"
                ]
            )
        )

        raise ValueError(
            "Duplicate ACO_ID + performance_year "
            "combinations found."
        )

    print(
        "ACO + performance_year validation PASSED."
    )


# ------------------------------------------------------------
# SORT DATA
# ------------------------------------------------------------

def sort_data(df):

    df = df.sort_values(
        [
            "ACO_ID",
            "performance_year"
        ]
    ).reset_index(
        drop=True
    )

    print(
        "Dataset sorted by ACO_ID and performance_year."
    )

    return df


# ------------------------------------------------------------
# COMPLETE PREPROCESSING PIPELINE
# ------------------------------------------------------------

def preprocess_data(df):

    print()
    print("========================================")
    print("PREPROCESSING")
    print("========================================")

    validate_required_columns(df)

    quality_measure_columns = (
        find_quality_measure_columns(df)
    )

    validate_aco_year(df)

    df = convert_numeric_columns(
        df,
        quality_measure_columns
    )

    df = sort_data(df)

    return (
        df,
        quality_measure_columns
    )