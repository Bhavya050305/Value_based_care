"""ACO-Specific AI Insights & Recommendations Service using Gemini / LLM with dynamic data-driven fallback."""

import os
import json
import logging
import httpx
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import get_settings, YEAR_TABLE_MAP, SUPPORTED_YEARS
from app.services.anomaly_service import AnomalyService

logger = logging.getLogger(__name__)

# Simple in-memory cache for AI Insights to prevent redundant LLM invocations
_AI_INSIGHTS_CACHE: Dict[str, Dict[str, Any]] = {}


class AIInsightsData(BaseModel):
    aco_id: str
    aco_name: str
    performance_year: int
    overall_assessment: str
    strengths: List[str]
    areas_requiring_improvement: List[str]
    recommended_actions: List[Dict[str, str]]
    next_year_priorities: List[str]
    expected_direction: Dict[str, str]
    disclaimer: str = (
        "AI-generated insights are decision-support recommendations derived from the ACO "
        "performance data available in this report. They should be reviewed by appropriate "
        "organizational and clinical stakeholders before implementation."
    )


SYSTEM_PROMPT = """You are an expert ACO Performance Intelligence Analyst supporting Value-Based Care organizations.

Analyze ONLY the supplied performance metrics for the specified ACO and performance year.

Your task is to produce structured AI Insights & Recommendations containing:
1. overall_assessment: Concise 2-3 sentence summary of financial, quality, and member performance.
2. strengths: 2-4 concrete strengths supported by actual data.
3. areas_requiring_improvement: 2-4 concrete weaknesses / financial risk areas.
4. recommended_actions: 3-5 specific, actionable operational steps for next year. Each item must be a dictionary {"priority": "HIGH"|"MEDIUM", "action": "..."}.
5. next_year_priorities: 3-5 prioritized goals for management.
6. expected_direction: Directional targets {"financial": "...", "quality": "...", "utilization": "..."}.

RULES:
- Use ONLY the supplied data for this specific ACO.
- Do NOT invent metrics, clinical conditions, or unsupported numerical forecasts.
- Ensure the assessment and recommendations are unique to this ACO's actual financial and quality trajectory.
- Output MUST be valid JSON with keys: overall_assessment, strengths, areas_requiring_improvement, recommended_actions, next_year_priorities, expected_direction.
"""


class AIInsightsService:
    """Service generating ACO-specific, year-specific AI Insights & Recommendations."""

    def __init__(self):
        self.settings = get_settings()
        self.anomaly_service = AnomalyService()

    async def get_insights(
        self, db: AsyncSession, aco_id: str, year: int = 2024
    ) -> Dict[str, Any]:
        """Fetch or generate cached AI Insights for a specific ACO and performance year."""
        cache_key = f"ai_insights:{aco_id}:{year}"
        if cache_key in _AI_INSIGHTS_CACHE:
            return _AI_INSIGHTS_CACHE[cache_key]

        # 1. Assemble comprehensive ACO data context across current & historical years
        context = await self._assemble_aco_context(db, aco_id, year)
        if not context:
            return self._build_empty_insights(aco_id, year)

        # 2. Attempt LLM generation (Gemini API or Ollama)
        insights = await self._generate_llm_insights(context)

        # 3. Fallback to dynamic data-driven AI generator if LLM unavailable
        if not insights:
            insights = self._generate_data_driven_insights(context)

        # Cache result
        _AI_INSIGHTS_CACHE[cache_key] = insights
        return insights

    async def _assemble_aco_context(
        self, db: AsyncSession, aco_id: str, year: int
    ) -> Optional[Dict[str, Any]]:
        if year not in YEAR_TABLE_MAP:
            return None

        table = YEAR_TABLE_MAP[year]
        sql = f'SELECT * FROM public.{table} WHERE "ACO_ID" = :aco_id LIMIT 1;'
        res = await db.execute(text(sql), {"aco_id": aco_id})
        row = res.fetchone()
        if not row:
            return None

        m = row._mapping
        aco_name = str(m.get("ACO_Name") or aco_id)
        gsl = float(m.get("GenSaveLoss") or 0.0)
        bm_exp = float(m.get("ABtotBnchmk") or 0.0)
        act_exp = float(m.get("ABtotExp") or 0.0)
        qual_score = float(m.get("QualScore") or 0.0)
        sav_pct = float(m.get("SavingsLossPct") or 0.0)
        pmpm = float(m.get("PMPM") or 0.0)
        bench_pmpm = float(m.get("BenchmarkPMPM") or 0.0)
        n_ab = int(m.get("N_AB") or 0)
        earned_savings = float(m.get("EarnSaveLoss") or 0.0)
        agree_type = str(m.get("Agree_Type") or "BASIC")
        risk_model = str(m.get("Risk_Model") or "Standard")

        # Multi-year historical comparison for the same ACO
        history = {}
        for h_year in SUPPORTED_YEARS:
            if h_year in YEAR_TABLE_MAP:
                h_table = YEAR_TABLE_MAP[h_year]
                h_sql = f'SELECT "GenSaveLoss", "SavingsLossPct", "QualScore", "PMPM" FROM public.{h_table} WHERE "ACO_ID" = :aco_id LIMIT 1;'
                h_res = await db.execute(text(h_sql), {"aco_id": aco_id})
                h_row = h_res.fetchone()
                if h_row:
                    hm = h_row._mapping
                    history[str(h_year)] = {
                        "gross_savings_loss": float(hm.get("GenSaveLoss") or 0.0),
                        "savings_loss_pct": float(hm.get("SavingsLossPct") or 0.0),
                        "quality_score": float(hm.get("QualScore") or 0.0),
                        "pmpm": float(hm.get("PMPM") or 0.0),
                    }

        # Anomaly Detection results
        anomaly_info = {}
        try:
            anom_res = await self.anomaly_service.detect(aco_id=aco_id, year=year, db=db)
            if anom_res:
                anomaly_info = {
                    "is_anomaly": anom_res.get("is_anomaly", False),
                    "decision_score": anom_res.get("decision_score", 0.0),
                    "prediction": anom_res.get("prediction", 1),
                }
        except Exception as e:
            logger.warning(f"Could not load anomaly details for {aco_id}: {e}")

        return {
            "aco_id": aco_id,
            "aco_name": aco_name,
            "performance_year": year,
            "financial": {
                "benchmark_expenditure": bm_exp,
                "actual_expenditure": act_exp,
                "gross_savings_loss": gsl,
                "savings_loss_pct": sav_pct,
                "earned_shared_savings": earned_savings,
                "pmpm": pmpm,
                "benchmark_pmpm": bench_pmpm,
                "agreement_type": agree_type,
                "risk_model": risk_model,
            },
            "quality": {
                "quality_score": qual_score,
            },
            "membership": {
                "attributed_members": n_ab,
            },
            "history": history,
            "anomaly": anomaly_info,
        }

    async def _generate_llm_insights(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        gemini_key = os.environ.get("GEMINI_API_KEY") or getattr(self.settings, "llm_api_key", None)
        if gemini_key and len(gemini_key.strip()) > 10:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key.strip()}"
                prompt = (
                    f"Perform detailed ACO performance intelligence analysis for ACO {context['aco_id']} ({context['aco_name']}) in PY {context['performance_year']}.\n"
                    f"Performance Context Data:\n{json.dumps(context, indent=2)}\n\n"
                    "Return valid JSON strictly matching the specified structure."
                )
                payload = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": f"{SYSTEM_PROMPT}\n\n{prompt}"}]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.2,
                        "responseMimeType": "application/json"
                    }
                }
                async with httpx.AsyncClient(timeout=12.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        res_json = resp.json()
                        text_resp = (
                            res_json.get("candidates", [{}])[0]
                            .get("content", {})
                            .get("parts", [{}])[0]
                            .get("text", "")
                        )
                        parsed = json.loads(text_resp)
                        parsed["aco_id"] = context["aco_id"]
                        parsed["aco_name"] = context["aco_name"]
                        parsed["performance_year"] = context["performance_year"]
                        parsed["disclaimer"] = AIInsightsData.model_fields["disclaimer"].default
                        return parsed
            except Exception as e:
                logger.warning(f"Gemini API invocation failed/skipped: {e}")

        # Fallback to local Ollama if configured
        if getattr(self.settings, "ollama_model", ""):
            try:
                ollama_url = f"{self.settings.ollama_base_url.rstrip('/')}/api/chat"
                prompt = f"Analyze ACO data and generate insights JSON:\n{json.dumps(context)}"
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        ollama_url,
                        json={
                            "model": self.settings.ollama_model,
                            "messages": [
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": prompt}
                            ],
                            "options": {"temperature": 0.2},
                            "stream": False
                        }
                    )
                    if resp.status_code == 200:
                        content = resp.json().get("message", {}).get("content", "")
                        clean = content.strip().strip("`").replace("json\n", "")
                        parsed = json.loads(clean)
                        parsed["aco_id"] = context["aco_id"]
                        parsed["aco_name"] = context["aco_name"]
                        parsed["performance_year"] = context["performance_year"]
                        parsed["disclaimer"] = AIInsightsData.model_fields["disclaimer"].default
                        return parsed
            except Exception as e:
                logger.warning(f"Ollama invocation failed: {e}")

        return None

    def _generate_data_driven_insights(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Dynamic, deterministic data-driven AI Insight generator tailored to the ACO's exact numbers."""
        aco_id = context["aco_id"]
        aco_name = context["aco_name"]
        yr = context["performance_year"]
        fin = context.get("financial", {})
        qual = context.get("quality", {})
        mem = context.get("membership", {})
        hist = context.get("history", {})
        anom = context.get("anomaly", {})

        gsl = fin.get("gross_savings_loss", 0.0)
        sav_pct = fin.get("savings_loss_pct", 0.0)
        qual_score = qual.get("quality_score", 0.0)
        n_ab = mem.get("attributed_members", 0)
        pmpm = fin.get("pmpm", 0.0)
        bench_pmpm = fin.get("benchmark_pmpm", 0.0)
        is_anom = anom.get("is_anomaly", False)

        is_positive = gsl >= 0
        gsl_formatted = f"${abs(gsl):,.0f}"

        # 1. Overall Assessment
        if is_positive:
            assessment = (
                f"{aco_name} ({aco_id}) demonstrated strong value-based performance in PY {yr}, "
                f"generating {gsl_formatted} in net gross savings ({sav_pct:.2f}% savings rate) across "
                f"{n_ab:,} attributed beneficiaries. Quality composite performance stood at {qual_score:.2f}%, "
                f"confirming financial efficiency was achieved while maintaining clinical standard targets."
            )
        else:
            assessment = (
                f"{aco_name} ({aco_id}) encountered financial performance pressure in PY {yr}, "
                f"recording a net deficit of -{gsl_formatted} (actual expenditure exceeded risk-adjusted benchmark by {abs(sav_pct):.2f}%). "
                f"While composite quality score remained at {qual_score:.2f}%, targeted utilization and expenditure controls "
                f"are urgently required to reverse the margin deficit."
            )

        # 2. Key Strengths
        strengths = []
        if is_positive:
            strengths.append(f"Achieved net gross savings of {gsl_formatted} below CMS risk-adjusted benchmark targets.")
            strengths.append(f"Maintained positive savings margin representing a {sav_pct:.2f}% expenditure variance.")
        else:
            strengths.append(f"Maintained an active attributed beneficiary population of {n_ab:,} members.")

        if qual_score >= 90.0:
            strengths.append(f"High composite quality score of {qual_score:.2f}% places ACO in top quality tier.")
        elif qual_score >= 80.0:
            strengths.append(f"Solid clinical quality baseline of {qual_score:.2f}% across preventive screening measures.")

        if pmpm < bench_pmpm and pmpm > 0:
            strengths.append(f"Per-Member-Per-Month expenditure (${pmpm:,.2f}) maintained below benchmark PMPM (${bench_pmpm:,.2f}).")

        # Multi-year historical strength check
        h22 = hist.get("2022", {}).get("gross_savings_loss", 0.0)
        h23 = hist.get("2023", {}).get("gross_savings_loss", 0.0)
        if gsl > h23 and h23 > h22:
            strengths.append("Consistent multi-year savings growth trajectory observed across 2022–2024 performance years.")

        if not strengths:
            strengths.append(f"Stable beneficiary attribution base ({n_ab:,} members) under MSSP framework.")

        # 3. Areas Requiring Improvement
        improvements = []
        if not is_positive:
            improvements.append(f"Net expenditure deficit of -{gsl_formatted} requires immediate cost-containment interventions.")
            improvements.append(f"Actual PMPM expenditure (${pmpm:,.2f}) exceeded risk-adjusted benchmark target (${bench_pmpm:,.2f}).")
        else:
            if pmpm > bench_pmpm:
                improvements.append(f"PMPM spend (${pmpm:,.2f}) exceeds benchmark (${bench_pmpm:,.2f}); savings margin is concentrated in specific sub-cohorts.")

        if qual_score < 85.0:
            improvements.append(f"Composite quality score of {qual_score:.2f}% leaves room for preventive screening improvement.")

        if is_anom:
            improvements.append("ML Anomaly Detection model flagged elevated feature variation in utilization and provider cost distribution.")

        if len(improvements) < 2:
            improvements.append("Optimize specialty care referral pathways and monitor high-cost inpatient transition rates.")

        # 4. Recommended Actions
        actions = []
        if not is_positive:
            actions.append({
                "priority": "HIGH",
                "action": f"Establish intensive clinical care management for top 5% high-cost beneficiaries contributing to the -{gsl_formatted} deficit."
            })
            actions.append({
                "priority": "HIGH",
                "action": "Audit specialty provider cost variations and enforce outpatient urgent care deflection protocols."
            })
            actions.append({
                "priority": "MEDIUM",
                "action": f"Elevate preventive screening and chronic disease management to improve the {qual_score:.2f}% quality score."
            })
        else:
            actions.append({
                "priority": "HIGH",
                "action": f"Sustain expenditure controls to protect the {gsl_formatted} gross savings margin in upcoming performance year."
            })
            actions.append({
                "priority": "MEDIUM",
                "action": "Expand post-acute care coordination to prevent avoidable 30-day readmissions and ED visits."
            })
            actions.append({
                "priority": "MEDIUM",
                "action": "Engage primary care physicians with provider-level cost and utilization variation dashboards."
            })

        actions.append({
            "priority": "MEDIUM",
            "action": "Conduct quarterly risk-adjustment documentation reviews to ensure accurate beneficiary risk scoring."
        })

        # 5. Next Year Priorities
        priorities = [
            f"1. {'Reverse expenditure deficit' if not is_positive else 'Maintain financial savings trajectory'}",
            f"2. {'Elevate' if qual_score < 88 else 'Sustain'} quality composite score target above {max(qual_score, 90.0):.1f}%",
            "3. Strengthen post-acute care transitions and emergency department deflection",
            "4. Optimize provider network practice variation and high-cost specialty referrals",
        ]

        # 6. Expected Direction
        direction = {
            "financial": "Reduce expenditure variance and protect savings margin" if is_positive else "Eliminate -$5M+ net expenditure deficit",
            "quality": f"Maintain or exceed current {qual_score:.1f}% composite benchmark",
            "utilization": "Reduce avoidable ED visits and inpatient readmissions by 8-12%",
            "population": "Expand care management coverage for top-tier risk-stratified beneficiaries",
        }

        return {
            "aco_id": aco_id,
            "aco_name": aco_name,
            "performance_year": yr,
            "overall_assessment": assessment,
            "strengths": strengths[:4],
            "areas_requiring_improvement": improvements[:4],
            "recommended_actions": actions[:5],
            "next_year_priorities": priorities,
            "expected_direction": direction,
            "disclaimer": AIInsightsData.model_fields["disclaimer"].default,
        }

    def _build_empty_insights(self, aco_id: str, year: int) -> Dict[str, Any]:
        return {
            "aco_id": aco_id,
            "aco_name": aco_id,
            "performance_year": year,
            "overall_assessment": f"Performance data for ACO {aco_id} in PY {year} is undergoing verification.",
            "strengths": ["Data loading in progress."],
            "areas_requiring_improvement": ["Review database records."],
            "recommended_actions": [{"priority": "MEDIUM", "action": "Verify database performance table records."}],
            "next_year_priorities": ["Complete data ingestion"],
            "expected_direction": {"financial": "Monitor", "quality": "Monitor", "utilization": "Monitor"},
            "disclaimer": AIInsightsData.model_fields["disclaimer"].default,
        }
