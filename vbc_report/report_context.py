"""
Assembles ONE ACO's complete Contract Review context from every table
your team has actually built. This is Layer 3 in the architecture from
your research: DATA -> ANALYTICS -> ML -> STRUCTURED CONTEXT -> Ollama.

Nothing here calls Ollama — this file only reads Supabase and returns
a plain Python dict. generate_report.py is what sends this to the LLM.
"""
import pandas as pd
from db import engine


def safe_query(sql, params):
    """Returns an empty DataFrame instead of crashing if a table/column doesn't exist yet."""
    try:
        return pd.read_sql(sql, engine, params=params)
    except Exception as e:
        print(f"  [safe_query] {e}")
        return pd.DataFrame()


def get_profile(aco_id, year):
    df = safe_query(
        """SELECT "ACO_Name", "ACO_State", "Agree_Type", "Current_Track", "Risk_Model",
                  "Assign_Type", "SNF_Waiver", "Current_Start_Date",
                  "N_Hosp", "N_PCP", "N_Spec", "N_NP", "N_PA"
           FROM fact_aco_performance
           WHERE "ACO_ID" = %(aco_id)s AND performance_year = %(year)s""",
        {"aco_id": aco_id, "year": year}
    )
    return df.iloc[0].to_dict() if not df.empty else {}


def get_financial(aco_id, year):
    df = safe_query(
        """SELECT "PMPM", "BenchmarkPMPM", "FinancialGap", "SavingsLossPct",
                  "ExpenditureVariancePct", "GenSaveLossYoYPct", "ABtotBnchmk",
                  "ABtotExp", "GenSaveLoss", "EarnSaveLoss", "FinalShareRate"
           FROM aco_financial_ml_training
           WHERE "ACO_ID" = %(aco_id)s AND target_year = %(year)s""",
        {"aco_id": aco_id, "year": year}
    )
    return df.iloc[0].to_dict() if not df.empty else {}


def get_financial_trend(aco_id):
    """Full 2020-2024 trend — uses fact_aco_performance directly since it has every year."""
    df = safe_query(
        """SELECT performance_year, "ABtotBnchmk" AS benchmark, "ABtotExp" AS expenditure,
                  "GenSaveLoss" AS savings, "Sav_rate" AS savings_rate
           FROM fact_aco_performance
           WHERE "ACO_ID" = %(aco_id)s
           ORDER BY performance_year""",
        {"aco_id": aco_id}
    )
    return df.to_dict(orient="records")


def get_quality(aco_id, year):
    df = safe_query(
        """SELECT quality_score, previous_quality_score, quality_change_yoy,
                  quality_gap_to_100, quality_performance_category, quality_status,
                  measures_increasing, measures_decreasing, attention_area_count,
                  attention_measures
           FROM aco_analytics
           WHERE aco_id = %(aco_id)s AND performance_year = %(year)s""",
        {"aco_id": aco_id, "year": year}
    )
    return df.iloc[0].to_dict() if not df.empty else {}


def get_utilization(aco_id, year):
    df = safe_query(
        """SELECT ed_visits_per_beneficiary, admissions_per_beneficiary,
                  snf_admissions_per_beneficiary, advanced_imaging_per_beneficiary,
                  em_visit_intensity, ed_utilization_change_yoy, admission_change_yoy,
                  em_utilization_change_yoy, advanced_imaging_change_yoy,
                  utilization_score, utilization_category,
                  high_utilization_flag, low_utilization_flag
           FROM aco_utilization_ml_features
           WHERE "ACO_ID" = %(aco_id)s AND performance_year = %(year)s""",
        {"aco_id": aco_id, "year": year}
    )
    return df.iloc[0].to_dict() if not df.empty else {}


def get_population(aco_id, year):
    df = safe_query(
        """SELECT assigned_beneficiaries, age_65_74_pct, age_75_84_pct, age_85_plus_pct,
                  dual_eligible_pct, disabled_pct, esrd_pct, average_available_risk_score,
                  risk_score_change_pct, risk_profile_category
           FROM aco_analytics
           WHERE aco_id = %(aco_id)s AND performance_year = %(year)s""",
        {"aco_id": aco_id, "year": year}
    )
    return df.iloc[0].to_dict() if not df.empty else {}


def get_service_variation(aco_id, year):
    """
    service_metrics has a REAL ACO_ID (unlike bhavya_provider_aco_features_final's
    synthetic scheme) — this is the legitimate source for provider/service
    variation now, tied to the actual ACO.
    """
    df = safe_query(
        """SELECT "HCPCS_Desc", service_category, total_payment, avg_payment_per_beneficiary,
                  utilization_change_pct, payment_change_pct, high_cost_service,
                  high_utilization_service, service_performance_segment
           FROM service_metrics
           WHERE "ACO_ID" = %(aco_id)s AND "Year" = %(year)s
           ORDER BY total_payment DESC
           LIMIT 5""",
        {"aco_id": aco_id, "year": year}
    )
    return df.to_dict(orient="records")


def get_ml_segmentation(aco_id, year):
    df = safe_query(
        """SELECT cluster_id, performance_segment, performance_index
           FROM aco_segmentation_results
           WHERE "ACO_ID" = %(aco_id)s AND performance_year = %(year)s""",
        {"aco_id": aco_id, "year": year}
    )
    return df.iloc[0].to_dict() if not df.empty else {}


def get_ml_anomaly(aco_id, year):
    anomaly = safe_query(
        """SELECT anomaly_score, top_anomalous_metric, severity
           FROM aco_anomalies
           WHERE "ACO_ID" = %(aco_id)s AND performance_year = %(year)s""",
        {"aco_id": aco_id, "year": year}
    )
    risk = safe_query(
        """SELECT ml_anomaly_score, risk_level, is_anomaly
           FROM aco_risk_scores
           WHERE "ACO_ID" = %(aco_id)s AND performance_year = %(year)s""",
        {"aco_id": aco_id, "year": year}
    )
    result = risk.iloc[0].to_dict() if not risk.empty else {}
    if not anomaly.empty:
        result.update(anomaly.iloc[0].to_dict())
    return result


def get_alerts(aco_id, year):
    df = safe_query(
        """SELECT alert_type, severity, message
           FROM aco_alerts
           WHERE "ACO_ID" = %(aco_id)s AND performance_year = %(year)s""",
        {"aco_id": aco_id, "year": year}
    )
    return df.to_dict(orient="records")


def build_drivers(utilization, financial, quality):
    """
    Rule-based driver decomposition (per your research: this is calculated,
    not left for the LLM to invent). Simple sign/magnitude thresholds.
    """
    positive, attention = [], []

    def add(bucket, label, value, unit="%"):
        if value is None or pd.isna(value):
            return
        bucket.append({"driver": label, "value": round(float(value), 2), "unit": unit})

    # utilization deltas: negative change = good (less utilization)
    if utilization.get("ed_utilization_change_yoy") is not None:
        target = positive if utilization["ed_utilization_change_yoy"] < 0 else attention
        add(target, "Emergency Department utilization", utilization["ed_utilization_change_yoy"] * 100)
    if utilization.get("admission_change_yoy") is not None:
        target = positive if utilization["admission_change_yoy"] < 0 else attention
        add(target, "Hospital admissions", utilization["admission_change_yoy"] * 100)
    if utilization.get("advanced_imaging_change_yoy") is not None:
        target = positive if utilization["advanced_imaging_change_yoy"] < 0 else attention
        add(target, "Advanced imaging utilization", utilization["advanced_imaging_change_yoy"] * 100)

    # financial: expenditure variance negative (below benchmark) = good
    if financial.get("ExpenditureVariancePct") is not None:
        target = positive if financial["ExpenditureVariancePct"] < 0 else attention
        add(target, "Expenditure vs. benchmark", financial["ExpenditureVariancePct"])

    # quality: positive change = good
    if quality.get("quality_change_yoy") is not None:
        target = positive if quality["quality_change_yoy"] >= 0 else attention
        add(target, "Quality score trend", quality["quality_change_yoy"], unit="pts")

    return {"positive_drivers": positive, "attention_drivers": attention}


def assemble_report_context(aco_id, year):
    profile = get_profile(aco_id, year)
    financial = get_financial(aco_id, year)
    quality = get_quality(aco_id, year)
    utilization = get_utilization(aco_id, year)
    population = get_population(aco_id, year)

    context = {
        "aco_id": aco_id,
        "performance_year": year,
        "profile": profile,
        "financial": financial,
        "financial_trend": get_financial_trend(aco_id),
        "quality": quality,
        "utilization": utilization,
        "population": population,
        "service_variation": get_service_variation(aco_id, year),
        "drivers": build_drivers(utilization, financial, quality),
        "ml_segmentation": get_ml_segmentation(aco_id, year),
        "ml_anomaly": get_ml_anomaly(aco_id, year),
        "alerts": get_alerts(aco_id, year),
        # Not built yet (Part 6) — explicitly marked, never fabricated by the LLM
        "peer_targets": None,
    }
    return context


if __name__ == "__main__":
    import json
    ctx = assemble_report_context("A1001", 2023)  # CHANGE to a real ACO_ID/year you know has data
    print(json.dumps(ctx, indent=2, default=str))
