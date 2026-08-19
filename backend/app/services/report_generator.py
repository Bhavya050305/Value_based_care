"""Report Generator Service.

Assembles real-time ACO executive reports using precomputed database analytics,
ML model predictions, and Ollama LLM narrative generation (with fallback).
Generates professional server-side PDF reports using ReportLab.
"""

from __future__ import annotations
import json
import re
from typing import Any, Dict, Optional
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import HTTPException

from app.core.config import get_settings, SUPPORTED_YEARS
from app.services.feature_builder import FeatureBuilder
from app.ml.segmentation.predictor import SegmentationPredictor
from app.ml.anomaly.loader import model as anomaly_model, FEATURES as ANOMALY_FEATURES
from app.ml.anomaly.predictor import predict_anomaly
from app.services.pdf_report import PdfReportService
from app.services.ai_insights import AIInsightsService


SYSTEM_PROMPT = """You are a Senior Healthcare Financial & ML Analyst for Value-Based Care.
Use ONLY the structured data provided to you.

Never invent:
- numerical values
- expenditures
- savings
- losses
- percentages
- risk scores
- quality scores
- utilization values
- provider counts
- member counts
- performance metrics

Do not infer a numerical value that is not explicitly supplied.
If a required fact is missing, state that the information is unavailable.
Do not contradict the supplied data.
Identify insights from the supplied values and trends only.
Recommendations must be based on observed evidence in the supplied data.

Return ONLY valid JSON matching the requested schema."""


class ReportGeneratorService:
    def __init__(self):
        self.settings = get_settings()
        self.seg_predictor = SegmentationPredictor()
        self.pdf_service = PdfReportService()
        self.ai_insights_service = AIInsightsService()

    async def assemble_report_context(
        self, db: AsyncSession, aco_id: str, performance_year: int
    ) -> Dict[str, Any]:
        """Retrieve real precomputed ACO record and construct full numerical context."""
        if performance_year not in SUPPORTED_YEARS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported performance year {performance_year}. Supported years are {SUPPORTED_YEARS}",
            )

        rec = await FeatureBuilder.get_raw_financial_record(db, aco_id, performance_year)
        
        # Query ACO entity details from public.acos if present
        res_aco = await db.execute(
            text("SELECT * FROM public.acos WHERE aco_id = :aco_id OR id = :aco_id LIMIT 1"),
            {"aco_id": aco_id}
        )
        aco_row = res_aco.fetchone()
        aco_name = f"ACO {aco_id} Health Network"
        aco_state = "FL"
        if aco_row:
            aco_mapping = aco_row._mapping if hasattr(aco_row, "_mapping") else aco_row.__dict__
            aco_name = aco_mapping.get("name", aco_name)
            aco_state = aco_mapping.get("state", aco_state)

        if not rec:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for the selected ACO and performance year.",
            )

        mapping = rec._mapping if hasattr(rec, "_mapping") else rec.__dict__

        bm = float(mapping.get("ABtotBnchmk")) if mapping.get("ABtotBnchmk") is not None else None
        exp = float(mapping.get("ABtotExp")) if mapping.get("ABtotExp") is not None else None
        gsl = float(mapping.get("GenSaveLoss")) if mapping.get("GenSaveLoss") is not None else (
            (bm - exp) if (bm is not None and exp is not None) else None
        )
        earned = float(mapping.get("EarnSaveLoss")) if mapping.get("EarnSaveLoss") is not None else (
            (gsl * 0.75) if gsl is not None else None
        )
        pmpm_val = float(mapping.get("PMPM")) if mapping.get("PMPM") is not None else None
        bm_pmpm = float(mapping.get("BenchmarkPMPM")) if mapping.get("BenchmarkPMPM") is not None else None
        fin_gap = float(mapping.get("FinancialGap")) if mapping.get("FinancialGap") is not None else (
            (bm - exp) if (bm is not None and exp is not None) else None
        )
        sav_pct = float(mapping.get("SavingsLossPct")) if mapping.get("SavingsLossPct") is not None else (
            ((gsl / bm) * 100.0) if (gsl is not None and bm) else None
        )

        # Query historical financial trend
        res_trend = await db.execute(
            text("""
                SELECT target_year, "ABtotBnchmk", "ABtotExp", "GenSaveLoss", "SavingsLossPct"
                FROM public.aco_financial_ml_training
                WHERE "ACO_ID" = :aco_id
                ORDER BY target_year ASC
            """),
            {"aco_id": aco_id}
        )
        trend_rows = res_trend.fetchall()
        financial_trend = []
        for tr in trend_rows:
            tr_m = tr._mapping if hasattr(tr, "_mapping") else tr.__dict__
            financial_trend.append({
                "performance_year": int(tr_m.get("target_year", 2024)),
                "benchmark": float(tr_m.get("ABtotBnchmk") or 0.0),
                "expenditure": float(tr_m.get("ABtotExp") or 0.0),
                "savings": float(tr_m.get("GenSaveLoss") or 0.0),
                "savings_rate": float(tr_m.get("SavingsLossPct") or 0.0)
            })

        # Run Segmentation ML model if predictor is valid
        cluster_id = 0
        seg_label = "Standard Performing"
        try:
            X_seg = FeatureBuilder.build_segmentation_features(rec, self.seg_predictor.features)
            if hasattr(self.seg_predictor, "model") and self.seg_predictor.model:
                cluster_id = int(self.seg_predictor.model.predict(X_seg)[0])
                seg_label = self.seg_predictor.cluster_mapping.get(cluster_id, "Standard Performing")
        except Exception:
            pass

        # Run Anomaly ML model if predictor is valid
        is_anom = False
        anom_score = 1.0
        try:
            if anomaly_model is not None:
                df_anom = FeatureBuilder.build_anomaly_features(rec, ANOMALY_FEATURES)
                anom_res = predict_anomaly(df_anom.iloc[0].to_dict())
                is_anom = anom_res.get("is_anomaly", False)
                anom_score = abs(anom_res.get("decision_score", 1.0))
        except Exception:
            pass

        qual_score = float(mapping.get("QualScore")) if mapping.get("QualScore") is not None else None
        adm_val = float(mapping.get("ADM")) if mapping.get("ADM") is not None else None
        ed_val = float(mapping.get("P_EDV_Vis")) if mapping.get("P_EDV_Vis") is not None else None
        n_ab = int(mapping.get("N_AB")) if mapping.get("N_AB") is not None else None

        return {
            "aco_id": aco_id,
            "performance_year": performance_year,
            "profile": {
                "ACO_Name": aco_name,
                "ACO_State": aco_state,
                "Agree_Type": str(mapping.get("Agree_Type") or "BASIC"),
                "Current_Track": str(mapping.get("track") or aco_row._mapping.get("track") if aco_row else "Track 1+"),
                "Risk_Model": str(mapping.get("Risk_Model") or "ONE-SIDED"),
                "Assign_Type": str(mapping.get("Assign_Type") or "Retrospective"),
                "N_PCP": int(mapping.get("N_PCP")) if mapping.get("N_PCP") is not None else None,
                "N_Spec": int(mapping.get("N_Spec")) if mapping.get("N_Spec") is not None else None,
            },
            "financial": {
                "PMPM": pmpm_val,
                "BenchmarkPMPM": bm_pmpm,
                "FinancialGap": fin_gap,
                "SavingsLossPct": sav_pct,
                "ABtotBnchmk": bm,
                "ABtotExp": exp,
                "GenSaveLoss": gsl,
                "EarnSaveLoss": earned,
                "FinalShareRate": float(mapping.get("FinalShareRate")) if mapping.get("FinalShareRate") is not None else None
            },
            "financial_trend": financial_trend,
            "quality": {
                "quality_score": qual_score,
            },
            "utilization": {
                "ed_visits_per_beneficiary": ed_val,
                "admissions_per_beneficiary": adm_val,
            },
            "population": {
                "assigned_beneficiaries": n_ab,
            },
            "ml_segmentation": {
                "cluster_id": cluster_id,
                "performance_segment": seg_label,
            },
            "ml_anomaly": {
                "ml_anomaly_score": float(anom_score),
                "risk_level": "HIGH" if is_anom else "LOW",
                "is_anomaly": is_anom
            }
        }

    def _generate_fallback_narrative(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured executive narrative deterministically when Ollama LLM is unavailable."""
        aco_id = context["aco_id"]
        profile = context.get("profile", {})
        aco_name = profile.get("ACO_Name", f"ACO {aco_id}")
        fin = context.get("financial", {})
        qual = context.get("quality", {})
        gsl = fin.get("GenSaveLoss")
        qual_score = qual.get("quality_score")
        seg = context.get("ml_segmentation", {}).get("performance_segment", "Standard Performing")

        gsl_str = f"${gsl:,.0f}" if gsl is not None else "N/A"
        qual_str = f"{qual_score:.2f}%" if qual_score is not None else "N/A"
        sav_pct = fin.get("SavingsLossPct")
        sav_pct_str = f"{sav_pct:.2f}%" if sav_pct is not None else "N/A"

        return {
            "overall_status": "GOOD" if (gsl is not None and gsl > 0) else "NEEDS_ATTENTION",
            "overall_score": qual_score if qual_score is not None else "N/A",
            "headline": f"{aco_name} evaluation for year {context['performance_year']}: Gross savings of {gsl_str} achieved with quality score of {qual_str}.",
            "strengths": [
                f"Quality composite score of {qual_str} recorded in database.",
                f"Gross savings balance of {gsl_str} below benchmark expenditure."
            ],
            "concerns": [
                "Continuous monitoring required for high-risk member utilization and care coordination."
            ],
            "priority_focus": "Maintain expenditure discipline and sustain quality performance targets.",
            "financial_insight": f"The ACO generated gross savings of {gsl_str} representing a savings rate of {sav_pct_str}.",
            "quality_insight": f"The composite quality score is {qual_str}.",
            "utilization_insight": "Utilization metrics are tracked based on verified claim records.",
            "ml_segmentation_explanation": f"Assigned to {seg} cluster based on multi-dimensional ML profile.",
            "anomaly_explanation": "Isolation Forest anomaly score calculated from feature metrics.",
            "recommendations": [
                {
                    "priority": "HIGH",
                    "issue": "Sustain gross savings margin below benchmark",
                    "evidence": f"Gross savings of {gsl_str} achieved",
                    "action": "Maintain cost management and post-acute protocols",
                },
                {
                    "priority": "MEDIUM",
                    "issue": "Monitor quality measure targets",
                    "evidence": f"Composite quality score of {qual_str}",
                    "action": "Review measure-level performance for continuous improvement",
                }
            ],
            "meeting_questions": [
                "What clinical initiatives contributed to current financial performance?",
                "How can care managers further optimize post-acute care transitions?"
            ]
        }

    async def generate_report(
        self, db: AsyncSession, aco_id: str, performance_year: int = 2024
    ) -> Dict[str, Any]:
        """Generate full executive report object (context data + narrative)."""
        context = await self.assemble_report_context(db, aco_id, performance_year)
        
        # Fetch AI Insights
        ai_insights = await self.ai_insights_service.get_insights(db, aco_id, performance_year)

        prompt = (
            f"Generate narrative report for ACO {aco_id} for year {performance_year}:\n"
            f"Context: {json.dumps(context)}\n"
        )

        narrative = None
        ollama_url = f"{self.settings.ollama_base_url.rstrip('/')}/api/chat"
        model_name = self.settings.ollama_model or "llama3.2:3b"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    ollama_url,
                    json={
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        "options": {"temperature": 0.2, "num_predict": 1200},
                        "stream": False
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    content = data.get("message", {}).get("content", "")
                    content_clean = re.sub(r"^```json\s*|^```\s*|```$", "", content.strip(), flags=re.MULTILINE).strip()
                    start, end = content_clean.find("{"), content_clean.rfind("}")
                    if start != -1 and end != -1:
                        narrative = json.loads(content_clean[start:end+1])
        except Exception:
            narrative = None

        if not narrative:
            narrative = self._generate_fallback_narrative(context)

        return {
            "aco_id": aco_id,
            "performance_year": performance_year,
            "narrative": narrative,
            "ai_insights": ai_insights,
            "data": context
        }

    async def generate_report_pdf(
        self, db: AsyncSession, aco_id: str, performance_year: int = 2024
    ) -> bytes:
        """Generate executive PDF report bytes using ReportLab."""
        report_data = await self.generate_report(db, aco_id, performance_year)
        return self.pdf_service.generate_pdf(report_data)
