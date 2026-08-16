# ============================================================
# ACO ANALYTICS - FEATURE ENGINEERING
# QUALITY + MEMBER ANALYTICS
# ============================================================

import json
import numpy as np
import pandas as pd


# ============================================================
# QUALITY ANALYTICS
# ============================================================

def build_quality_analytics(
    df,
    quality_measure_columns
):

    print()
    print("========================================")
    print("QUALITY ENGINE")
    print("========================================")

    quality = df[
        [
            "ACO_ID",
            "ACO_Name",
            "ACO_State",
            "performance_year",
            "QualScore",
            "Met_QPS"
        ]
    ].copy()

    quality = quality.sort_values(
        [
            "ACO_ID",
            "performance_year"
        ]
    )

    # --------------------------------------------------------
    # CURRENT QUALITY SCORE
    # --------------------------------------------------------

    quality["quality_score"] = (
        quality["QualScore"]
    )

    # --------------------------------------------------------
    # PREVIOUS YEAR
    # --------------------------------------------------------

    quality["previous_quality_score"] = (

        quality
        .groupby("ACO_ID")["quality_score"]
        .shift(1)
    )

    # --------------------------------------------------------
    # YOY CHANGE
    # --------------------------------------------------------

    quality["quality_change_yoy"] = (

        quality["quality_score"]
        -
        quality["previous_quality_score"]
    )

    # --------------------------------------------------------
    # YOY PERCENTAGE
    # --------------------------------------------------------

    quality["quality_change_yoy_pct"] = np.where(

        quality["previous_quality_score"].notna()
        &
        (quality["previous_quality_score"] != 0),

        (
            (
                quality["quality_score"]
                -
                quality["previous_quality_score"]
            )
            /
            quality["previous_quality_score"]
        ) * 100,

        np.nan
    )

    # --------------------------------------------------------
    # GAP TO 100
    # --------------------------------------------------------

    quality["quality_gap_to_100"] = (

        100
        -
        quality["quality_score"]
    )

    # --------------------------------------------------------
    # QUALITY CATEGORY
    # --------------------------------------------------------

    def quality_category(score):

        if pd.isna(score):
            return "Unknown"

        if score >= 90:
            return "Excellent"

        elif score >= 80:
            return "Good"

        elif score >= 70:
            return "Fair"

        else:
            return "Needs Attention"

    quality[
        "quality_performance_category"
    ] = (
        quality["quality_score"]
        .apply(quality_category)
    )

    # --------------------------------------------------------
    # QUALITY STATUS
    # --------------------------------------------------------

    quality["quality_status"] = (
        quality["Met_QPS"]
    )

    print(
        "Quality core metrics created."
    )

    return quality


# ============================================================
# QUALITY MEASURE ANALYTICS
# ============================================================

def build_quality_measure_analytics(
    df,
    quality_measure_columns
):

    print()
    print("Building quality measure analytics...")

    measure_data = df[
        [
            "ACO_ID",
            "performance_year"
        ]
        +
        quality_measure_columns
    ].copy()

    measure_data = measure_data.sort_values(
        [
            "ACO_ID",
            "performance_year"
        ]
    )

    # --------------------------------------------------------
    # PREVIOUS YEAR MEASURES
    # --------------------------------------------------------

    previous_measure_data = (

        measure_data
        .groupby("ACO_ID")[quality_measure_columns]
        .shift(1)
    )

    # --------------------------------------------------------
    # CHANGE
    # --------------------------------------------------------

    measure_changes = (

        measure_data[quality_measure_columns]
        -
        previous_measure_data
    )

    # --------------------------------------------------------
    # PERCENTAGE CHANGE
    # --------------------------------------------------------

    measure_pct_changes = (

        measure_changes
        .div(
            previous_measure_data.replace(
                0,
                np.nan
            )
        )
        * 100
    )

    # Keep available for downstream use
    _ = measure_pct_changes

    # --------------------------------------------------------
    # BUILD SUMMARY
    # --------------------------------------------------------

    summary_records = []

    for i in range(
        len(measure_data)
    ):

        changes = (
            measure_changes.iloc[i]
        )

        valid_changes = (
            changes.dropna()
        )

        increasing = (
            valid_changes[
                valid_changes > 0
            ]
            .sort_values(
                ascending=False
            )
        )

        decreasing = (
            valid_changes[
                valid_changes < 0
            ]
            .sort_values()
        )

        attention = (
            decreasing.head(5)
        )

        attention_list = []

        for measure, change in (
            attention.items()
        ):

            attention_list.append(
                {
                    "measure": measure,
                    "change": round(
                        float(change),
                        4
                    )
                }
            )

        summary_records.append(
            {
                "ACO_ID":
                    measure_data.iloc[i]["ACO_ID"],

                "performance_year":
                    measure_data.iloc[i][
                        "performance_year"
                    ],

                "measures_available":
                    int(
                        valid_changes.shape[0]
                    ),

                "measures_increasing":
                    int(
                        (valid_changes > 0).sum()
                    ),

                "measures_decreasing":
                    int(
                        (valid_changes < 0).sum()
                    ),

                "attention_area_count":
                    len(attention_list),

                "attention_measures":
                    json.dumps(
                        attention_list
                    )
            }
        )

    measure_summary = pd.DataFrame(
        summary_records
    )

    print(
        "Individual quality measure analysis completed."
    )

    print(
        "Number of measures:",
        len(quality_measure_columns)
    )

    return (
        measure_data,
        measure_summary
    )


# ============================================================
# MEMBER ANALYTICS
# ============================================================

def build_member_analytics(df):

    print()
    print("========================================")
    print("MEMBER ENGINE")
    print("========================================")

    member = df[
        [
            "ACO_ID",
            "performance_year",

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

            "Perc_Dual",

            "CMS_HCC_RiskScore_ESRD_BY3",
            "CMS_HCC_RiskScore_DIS_BY3",
            "CMS_HCC_RiskScore_AGDU_BY3",
            "CMS_HCC_RiskScore_AGND_BY3"
        ]
    ].copy()

    member = member.sort_values(
        [
            "ACO_ID",
            "performance_year"
        ]
    ).reset_index(
        drop=True
    )

    # ========================================================
    # POPULATION
    # ========================================================

    member["assigned_beneficiaries"] = (
        member["N_AB"]
    )

    member[
        "previous_assigned_beneficiaries"
    ] = (

        member
        .groupby("ACO_ID")[
            "assigned_beneficiaries"
        ]
        .shift(1)
    )

    member[
        "beneficiary_change_yoy"
    ] = (

        member["assigned_beneficiaries"]
        -
        member[
            "previous_assigned_beneficiaries"
        ]
    )

    member[
        "beneficiary_change_yoy_pct"
    ] = np.where(

        member[
            "previous_assigned_beneficiaries"
        ].notna()
        &
        (
            member[
                "previous_assigned_beneficiaries"
            ] != 0
        ),

        (
            member[
                "beneficiary_change_yoy"
            ]
            /
            member[
                "previous_assigned_beneficiaries"
            ]
        ) * 100,

        np.nan
    )

    # ========================================================
    # AGE
    # ========================================================

    member["age_0_64_count"] = (
        member["N_Ben_Age_0_64"]
    )

    member["age_65_74_count"] = (
        member["N_Ben_Age_65_74"]
    )

    member["age_75_84_count"] = (
        member["N_Ben_Age_75_84"]
    )

    member["age_85_plus_count"] = (
        member["N_Ben_Age_85plus"]
    )

    denominator = (
        member["assigned_beneficiaries"]
    )

    # Avoid division-by-zero
    safe_denominator = denominator.replace(
        0,
        np.nan
    )

    member["age_0_64_pct"] = (
        member["age_0_64_count"]
        /
        safe_denominator
        * 100
    )

    member["age_65_74_pct"] = (
        member["age_65_74_count"]
        /
        safe_denominator
        * 100
    )

    member["age_75_84_pct"] = (
        member["age_75_84_count"]
        /
        safe_denominator
        * 100
    )

    member["age_85_plus_pct"] = (
        member["age_85_plus_count"]
        /
        safe_denominator
        * 100
    )

    # ========================================================
    # GENDER
    # ========================================================

    member["female_count"] = (
        member["N_Ben_Female"]
    )

    member["male_count"] = (
        member["N_Ben_Male"]
    )

    member["female_pct"] = (
        member["female_count"]
        /
        safe_denominator
        * 100
    )

    member["male_pct"] = (
        member["male_count"]
        /
        safe_denominator
        * 100
    )

    # ========================================================
    # HEALTH CHARACTERISTICS
    # ========================================================

    member["disabled_count"] = (
        member["N_AB_Year_DIS_BY3"]
    )

    member["disabled_pct"] = (
        member["disabled_count"]
        /
        safe_denominator
        * 100
    )

    member["esrd_count"] = (
        member["N_AB_Year_ESRD_BY3"]
    )

    member["esrd_pct"] = (
        member["esrd_count"]
        /
        safe_denominator
        * 100
    )

    member["dual_eligible_count"] = (
        member["N_AB_Year_AGED_Dual_BY3"]
    )

    member["dual_eligible_pct"] = (
        member["Perc_Dual"]
    )

    # ========================================================
    # RACE
    # ========================================================

    race_mapping = {

        "white":
            "N_Ben_Race_White",

        "black":
            "N_Ben_Race_Black",

        "asian":
            "N_Ben_Race_Asian",

        "hispanic":
            "N_Ben_Race_Hisp",

        "native":
            "N_Ben_Race_Native",

        "other":
            "N_Ben_Race_Other",

        "unknown":
            "N_Ben_Race_Unknown"
    }

    for race_name, source_column in (
        race_mapping.items()
    ):

        member[
            f"{race_name}_count"
        ] = member[
            source_column
        ]

        member[
            f"{race_name}_pct"
        ] = (

            member[
                f"{race_name}_count"
            ]
            /
            safe_denominator
            * 100
        )

    # ========================================================
    # RISK
    # ========================================================

    risk_score_columns = {

        "risk_score_esrd":
            "CMS_HCC_RiskScore_ESRD_BY3",

        "risk_score_disabled":
            "CMS_HCC_RiskScore_DIS_BY3",

        "risk_score_aged_dual":
            "CMS_HCC_RiskScore_AGDU_BY3",

        "risk_score_aged_nondual":
            "CMS_HCC_RiskScore_AGND_BY3"
    }

    for (
        output_name,
        source_name
    ) in risk_score_columns.items():

        member[output_name] = (
            member[source_name]
        )

    risk_values = member[
        list(
            risk_score_columns.keys()
        )
    ]

    member[
        "average_available_risk_score"
    ] = (

        risk_values.mean(
            axis=1,
            skipna=True
        )
    )

    member[
        "previous_average_risk_score"
    ] = (

        member
        .groupby("ACO_ID")[
            "average_available_risk_score"
        ]
        .shift(1)
    )

    member[
        "risk_score_change"
    ] = (

        member[
            "average_available_risk_score"
        ]
        -
        member[
            "previous_average_risk_score"
        ]
    )

    member[
        "risk_score_change_pct"
    ] = np.where(

        member[
            "previous_average_risk_score"
        ].notna()
        &
        (
            member[
                "previous_average_risk_score"
            ] != 0
        ),

        (
            member[
                "risk_score_change"
            ]
            /
            member[
                "previous_average_risk_score"
            ]
        ) * 100,

        np.nan
    )

    # ========================================================
    # RISK CATEGORY
    # ========================================================

    risk_score = member[
        "average_available_risk_score"
    ]

    q25 = risk_score.quantile(0.25)
    q50 = risk_score.quantile(0.50)
    q75 = risk_score.quantile(0.75)

    def risk_category(value):

        if pd.isna(value):
            return "Unknown"

        if value <= q25:
            return "Low"

        elif value <= q50:
            return "Moderate"

        elif value <= q75:
            return "High"

        else:
            return "Very High"

    member[
        "risk_profile_category"
    ] = (
        risk_score.apply(
            risk_category
        )
    )

    print(
        "Member analytics created."
    )

    print()
    print("Risk thresholds:")
    print("25th percentile:", q25)
    print("50th percentile:", q50)
    print("75th percentile:", q75)

    return member


# ============================================================
# COMBINE QUALITY + MEMBER
# ============================================================

def build_aco_analytics(
    quality,
    measure_data,
    measure_summary,
    member
):

    final_quality = quality[
        [
            "ACO_ID",
            "ACO_Name",
            "ACO_State",
            "performance_year",

            "quality_score",
            "previous_quality_score",
            "quality_change_yoy",
            "quality_change_yoy_pct",
            "quality_gap_to_100",

            "quality_performance_category",
            "quality_status"
        ]
    ].copy()

    # --------------------------------------------------------
    # CURRENT QUALITY MEASURES
    # --------------------------------------------------------

    final_quality = final_quality.merge(
        measure_data,
        on=[
            "ACO_ID",
            "performance_year"
        ],
        how="left"
    )

    # --------------------------------------------------------
    # MEASURE SUMMARY
    # --------------------------------------------------------

    final_quality = final_quality.merge(
        measure_summary,
        on=[
            "ACO_ID",
            "performance_year"
        ],
        how="left"
    )

    # --------------------------------------------------------
    # MEMBER OUTPUT
    # --------------------------------------------------------

    member_output_columns = [

        "ACO_ID",
        "performance_year",

        "assigned_beneficiaries",
        "previous_assigned_beneficiaries",
        "beneficiary_change_yoy",
        "beneficiary_change_yoy_pct",

        "age_0_64_count",
        "age_65_74_count",
        "age_75_84_count",
        "age_85_plus_count",

        "age_0_64_pct",
        "age_65_74_pct",
        "age_75_84_pct",
        "age_85_plus_pct",

        "female_count",
        "male_count",
        "female_pct",
        "male_pct",

        "disabled_count",
        "disabled_pct",

        "esrd_count",
        "esrd_pct",

        "dual_eligible_count",
        "dual_eligible_pct",

        "white_count",
        "black_count",
        "asian_count",
        "hispanic_count",
        "native_count",
        "other_count",
        "unknown_count",

        "white_pct",
        "black_pct",
        "asian_pct",
        "hispanic_pct",
        "native_pct",
        "other_pct",
        "unknown_pct",

        "risk_score_esrd",
        "risk_score_disabled",
        "risk_score_aged_dual",
        "risk_score_aged_nondual",

        "average_available_risk_score",
        "previous_average_risk_score",
        "risk_score_change",
        "risk_score_change_pct",

        "risk_profile_category"
    ]

    final_member = member[
        member_output_columns
    ].copy()

    # --------------------------------------------------------
    # FINAL MERGE
    # --------------------------------------------------------

    aco_analytics = final_quality.merge(

        final_member,

        on=[
            "ACO_ID",
            "performance_year"
        ],

        how="left"
    )

    # --------------------------------------------------------
    # DATABASE NAMING
    # --------------------------------------------------------

    aco_analytics = (
        aco_analytics.rename(
            columns={
                "ACO_ID": "aco_id",
                "ACO_Name": "aco_name",
                "ACO_State": "aco_state"
            }
        )
    )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    aco_analytics = (
        aco_analytics.sort_values(
            [
                "aco_id",
                "performance_year"
            ]
        )
        .reset_index(drop=True)
    )

    print()
    print("========================================")
    print("FINAL ACO ANALYTICS CREATED")
    print("========================================")

    print(
        "Rows:",
        len(aco_analytics)
    )

    print(
        "Columns:",
        len(aco_analytics.columns)
    )

    return aco_analytics