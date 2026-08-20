"""
The prompt that turns report_context.py's dict into the LLM instructions.
Asks for JSON back (not prose), matching your researched report schema,
so the frontend can render tables/cards directly from the response
instead of parsing paragraphs.
"""
import json

SYSTEM_PROMPT = """You are a Value-Based Care contract analytics assistant working for a US healthcare payer. Your audience is a payer contract manager preparing for an ACO provider review meeting.

STRICT RULES:
1. Never invent numbers. Use ONLY values present in the supplied CONTEXT.
2. Never calculate a value that is not supplied — all percentages, scores, and totals are already computed.
3. If a field is missing or null, omit it or state "Not available" — never guess.
4. Do not claim a provider belongs to this ACO unless the data explicitly supports it.
5. Do not describe a peer target as an official CMS benchmark or forecast.
6. Keep every text field SHORT — one or two sentences maximum, no long paragraphs.
7. Every recommendation must reference specific evidence from the CONTEXT.
8. Respond with ONLY valid JSON matching the exact schema below. No markdown, no code fences, no explanation before or after — just the raw JSON object.

OUTPUT SCHEMA (fill every field using only CONTEXT data; use "Not available" for missing data, never leave a field out):
{
  "overall_status": "GOOD | ATTENTION | HIGH_RISK",
  "overall_score": <number 0-100, based on combining financial/quality/utilization status, your best evidence-based estimate>,
  "headline": "<one sentence executive assessment>",
  "strengths": ["<short bullet>", "..."],
  "concerns": ["<short bullet>", "..."],
  "priority_focus": "<one sentence: what to focus on next>",
  "financial_insight": "<1-2 sentences interpreting the financial numbers>",
  "quality_insight": "<1-2 sentences interpreting the quality numbers>",
  "utilization_insight": "<1-2 sentences interpreting the utilization numbers>",
  "population_insight": "<1-2 sentences on what the population profile means for interpreting cost>",
  "ml_segmentation_explanation": "<1-2 sentences translating the cluster/segment into plain business language, per rule: never say 'the model says X is dangerous', frame it as 'falls within the X segment based on its multi-dimensional profile'>",
  "anomaly_explanation": "<1-2 sentences on what the anomaly detection found, or 'No anomaly detected for this ACO-year.' if none>",
  "recommendations": [
    {"priority": "HIGH | MEDIUM | LOW", "issue": "<short>", "evidence": "<short, cite a specific number from CONTEXT>", "action": "<short>", "expected_direction": "<short>"}
  ],
  "meeting_questions": ["<evidence-based question for the ACO>", "..."]
}
"""


def build_report_prompt(context: dict) -> str:
    # Trim to only what the LLM needs to reason over — keep the raw dict
    # separately for the frontend, which renders numeric tables directly
    # from report_context.py's output, NOT from the LLM's response.
    trimmed = {
        "aco_name": context["profile"].get("ACO_Name"),
        "performance_year": context["performance_year"],
        "financial": context["financial"],
        "quality": context["quality"],
        "utilization": context["utilization"],
        "population": context["population"],
        "drivers": context["drivers"],
        "ml_segmentation": context["ml_segmentation"],
        "ml_anomaly": context["ml_anomaly"],
        "alerts": context["alerts"],
    }
    return f"CONTEXT:\n{json.dumps(trimmed, indent=2, default=str)}\n\nGenerate the JSON report now."
