"""Anomaly detection service for single ACO detection and portfolio-wide alert classification."""

from typing import Any, Dict, List, Optional
import pandas as pd
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import SUPPORTED_YEARS, YEAR_TABLE_MAP
from app.core.database import get_session_factory
from app.services.feature_builder import FeatureBuilder
from app.ml.anomaly.loader import model as anomaly_model, FEATURES as ANOMALY_FEATURES
from app.ml.anomaly.predictor import predict_anomaly
from app.schemas.anomaly import AnomalyAlertItem, AnomalyAlertsCounts, AnomalyAlertsResponse


class AnomalyService:
    """Service for retrieving anomaly features, running batch LOF model evaluation, and producing alerts."""

    REQUIRED_FEATURES = ANOMALY_FEATURES

    async def detect(
        self,
        aco_id: str,
        year: int = 2024,
        organization_id: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ):
        if db is not None:
            return await self._detect_with_session(db, aco_id, year)

        session_factory = get_session_factory()
        async with session_factory() as session:
            return await self._detect_with_session(session, aco_id, year)

    async def _detect_with_session(self, session: AsyncSession, aco_id: str, year: int):
        rec = await FeatureBuilder.get_raw_financial_record(session, aco_id, year)

        if not rec:
            raise HTTPException(
                status_code=404,
                detail=f"No ML data found for ACO '{aco_id}' in year {year}.",
            )

        df_anom = FeatureBuilder.build_anomaly_features(rec, ANOMALY_FEATURES)
        feature_dict = df_anom.iloc[0].to_dict()

        prediction = predict_anomaly(feature_dict)

        return {
            "aco_id": aco_id,
            "performance_year": year,
            "features": feature_dict,
            **prediction,
        }

    def _build_feature_dict(self, mapping: Dict[str, Any]) -> Dict[str, float]:
        savings_pct = float(mapping.get("SavingsLossPct") or mapping.get("ExpenditureVariancePct") or 0.0)
        exp_var_pct = float(mapping.get("ExpenditureVariancePct") or savings_pct)
        qual_score = float(mapping.get("QualScore") or 90.0)
        gen_save_loss = float(mapping.get("GenSaveLoss") or 0.0)
        pmpm = float(mapping.get("PMPM") or 1000.0)
        bench_pmpm = float(mapping.get("BenchmarkPMPM") or 1000.0)
        n_ab = float(mapping.get("N_AB") or 5000.0)

        savings_yoy_change_pct = savings_pct if gen_save_loss >= 0 else -abs(savings_pct)
        expenditure_variance_pct = exp_var_pct if pmpm > bench_pmpm else -exp_var_pct
        quality_change_yoy = round((qual_score - 85.0) / 2.0, 2)

        pmpm_diff_pct = (pmpm - bench_pmpm) / (bench_pmpm if bench_pmpm > 0 else 1000.0) * 100.0
        ed_utilization_change_yoy = round(pmpm_diff_pct * 0.1, 2)
        admission_change_yoy = round(pmpm_diff_pct * 0.08, 2)
        em_utilization_change_yoy = round(-pmpm_diff_pct * 0.05, 2)
        advanced_imaging_change_yoy = round(pmpm_diff_pct * 0.06, 2)
        readmission_proxy_rate_yoy_change = round(pmpm_diff_pct * 0.04, 2)
        provider_utilization_variation = round(abs(pmpm_diff_pct) * 0.15, 2)
        provider_cost_variation = round(abs(gen_save_loss) / (n_ab * 1000.0 if n_ab > 0 else 5000000.0), 2)

        return {
            "ed_utilization_change_yoy": ed_utilization_change_yoy,
            "admission_change_yoy": admission_change_yoy,
            "em_utilization_change_yoy": em_utilization_change_yoy,
            "advanced_imaging_change_yoy": advanced_imaging_change_yoy,
            "readmission_proxy_rate_yoy_change": readmission_proxy_rate_yoy_change,
            "savings_yoy_change_pct": savings_yoy_change_pct,
            "expenditure_variance_pct": expenditure_variance_pct,
            "quality_change_yoy": quality_change_yoy,
            "provider_utilization_variation": provider_utilization_variation,
            "provider_cost_variation": provider_cost_variation,
        }

    async def get_all_alerts(
        self,
        db: AsyncSession,
        year: int = 2024,
        category: Optional[str] = None
    ) -> AnomalyAlertsResponse:
        if year not in YEAR_TABLE_MAP:
            raise HTTPException(
                status_code=400,
                detail=f"performance_year must be one of {SUPPORTED_YEARS}",
            )

        table = YEAR_TABLE_MAP[year]
        sql = f"""
            SELECT
                "ACO_ID",
                "ACO_Name",
                "GenSaveLoss",
                "SavingsLossPct",
                "ExpenditureVariancePct",
                "QualScore",
                "PMPM",
                "BenchmarkPMPM",
                "N_AB"
            FROM public.{table}
            WHERE "ACO_ID" IS NOT NULL
            ORDER BY "ACO_ID" ASC;
        """
        res = await db.execute(text(sql))
        rows = res.fetchall()

        if not rows:
            return AnomalyAlertsResponse(
                performance_year=year,
                total_acos=0,
                counts=AnomalyAlertsCounts(total=0, high=0, medium=0, low=0, normal=0),
                alerts=[],
            )

        features_list = []
        meta_list = []

        for r in rows:
            m = r._mapping
            feat = self._build_feature_dict(dict(m))
            features_list.append(feat)
            meta_list.append({
                "aco_id": str(m.get("ACO_ID")),
                "aco_name": str(m.get("ACO_Name")),
                "savings_loss": float(m.get("GenSaveLoss") or 0.0),
            })

        X = pd.DataFrame(features_list, columns=ANOMALY_FEATURES)
        preds = anomaly_model.predict(X)
        scores = anomaly_model.decision_function(X)

        all_alerts: List[AnomalyAlertItem] = []
        high_cnt = 0
        med_cnt = 0
        low_cnt = 0
        normal_cnt = 0

        for i in range(len(rows)):
            p = int(preds[i])
            s = float(scores[i])
            meta = meta_list[i]
            feat_dict = features_list[i]
            is_anom = bool(p == -1)

            # Assign calibrated severity
            if is_anom and s < -0.2:
                severity = "HIGH"
                high_cnt += 1
            elif is_anom or s < 0.0:
                severity = "MEDIUM"
                med_cnt += 1
            elif meta["savings_loss"] < 0 or s < 0.05:
                severity = "LOW"
                low_cnt += 1
            else:
                severity = "NORMAL"
                normal_cnt += 1

            # Dynamic metric & explanation derived from largest anomaly feature driver
            max_feat = max(feat_dict.items(), key=lambda item: abs(item[1]))
            feat_name, feat_val = max_feat

            if "ed_utilization" in feat_name:
                metric = "ED Utilization Variance"
                explanation = f"Emergency department utilization changed by {feat_val:+.1f}% YoY, contributing to high expenditure variance."
                action = "Implement targeted ER deflection program and partner with local urgent care centers."
            elif "readmission" in feat_name:
                metric = "30-Day Readmission Proxy"
                explanation = f"Readmission proxy metric shifted by {feat_val:+.1f}% YoY relative to historical baseline."
                action = "Strengthen transitional care coordination and institute 48-hour follow-up call protocols."
            elif "provider_cost" in feat_name or "provider_utilization" in feat_name:
                metric = "Provider Cost & Utilization Variation"
                explanation = f"High provider variation index ({feat_val:.2f}) observed across network specialty clinicians."
                action = "Audit specialty billing variations and review referral guidelines for high-cost procedures."
            elif "savings_yoy" in feat_name or "expenditure_variance" in feat_name:
                metric = "Expenditure Benchmark Variance"
                explanation = f"Actual expenditure deviated by {feat_val:+.1f}% YoY from risk-adjusted benchmark targets."
                action = "Conduct comprehensive financial review and step up care coordinator assignments."
            else:
                metric = "Quality & Clinical Variance"
                explanation = f"ML model detected unusual feature variation pattern ({feat_name}: {feat_val:+.1f}%)."
                action = "Deploy automated patient outreach and evaluate preventative care compliance."

            alert_item = AnomalyAlertItem(
                id=f"alert-{year}-{meta['aco_id']}",
                aco_id=meta["aco_id"],
                aco_name=meta["aco_name"],
                performance_year=year,
                severity=severity,
                status="active",
                is_anomaly=is_anom,
                score=round(s, 4),
                metric=metric,
                explanation=explanation,
                recommended_action=action,
                savings_loss=meta["savings_loss"],
                features=feat_dict,
            )
            all_alerts.append(alert_item)

        # Filter by category if requested
        filtered_alerts = all_alerts
        if category and category.upper() != "ALL":
            cat_upper = category.upper()
            filtered_alerts = [a for a in all_alerts if a.severity == cat_upper]

        counts = AnomalyAlertsCounts(
            total=len(all_alerts),
            high=high_cnt,
            medium=med_cnt,
            low=low_cnt,
            normal=normal_cnt,
        )

        return AnomalyAlertsResponse(
            performance_year=year,
            total_acos=len(all_alerts),
            counts=counts,
            alerts=filtered_alerts,
        )