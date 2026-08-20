"""
Calls Ollama with the assembled context, parses the JSON response (with
one retry if the small model returns malformed JSON — common with 3B
models), and combines it with the raw numeric context so the final
object has BOTH the LLM's narrative fields AND the exact numbers/tables
for the frontend to render directly (never re-typed by the LLM).

Run standalone with:  python generate_report.py
"""
import os
import json
import re
import ollama
from dotenv import load_dotenv

from report_context import assemble_report_context
from report_prompt import SYSTEM_PROMPT, build_report_prompt
from db import engine

load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


def extract_json(text: str) -> dict:
    """Small models sometimes wrap JSON in extra text/markdown fences — strip that."""
    text = text.strip()
    text = re.sub(r"^```json\s*|^```\s*|```$", "", text, flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model output")
    return json.loads(text[start:end + 1])


def call_ollama(prompt: str) -> dict:
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0.2, "num_predict": 1200},
        format="json",  # asks Ollama to constrain output to valid JSON where supported
    )
    raw = response["message"]["content"]
    try:
        return extract_json(raw)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"  First parse failed ({e}), retrying once...")
        retry_prompt = f"{prompt}\n\nYour previous response was not valid JSON. Return ONLY the raw JSON object, nothing else."
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": retry_prompt},
            ],
            options={"temperature": 0.1, "num_predict": 1200},
            format="json",
        )
        return extract_json(response["message"]["content"])


def generate_report(aco_id: str, performance_year: int, use_cache: bool = False, save_cache: bool = True) -> dict:
    """
    Real-time generation. Set use_cache=True to check aco_report_cache first
    (skip regenerating if a report already exists for this exact model/prompt
    version) — off by default since you're still iterating on the prompt.
    """
    context = assemble_report_context(aco_id, performance_year)

    if not context["profile"]:
        raise ValueError(f"No profile data for ACO_ID={aco_id}, performance_year={performance_year}")

    prompt = build_report_prompt(context)
    narrative = call_ollama(prompt)

    full_report = {
        "aco_id": aco_id,
        "performance_year": performance_year,
        "narrative": narrative,   # LLM-generated: status, insights, recommendations, questions
        "data": context,          # exact numbers/tables: frontend renders these directly, never from narrative
    }

    if save_cache:
        try:
            import pandas as pd
            cache_row = pd.DataFrame([{
                "aco_id": aco_id,
                "performance_year": performance_year,
                "report_version": "1.0",
                "model_version": MODEL,
                "generated_at": pd.Timestamp.now(),
                "report_json": json.dumps(full_report, default=str),
                "status": "generated",
            }])
            cache_row.to_sql("aco_report_cache", engine, if_exists="append", index=False)
        except Exception as e:
            print(f"  [cache] not saved: {e}")

    return full_report


if __name__ == "__main__":
    import sys
    aco_id = sys.argv[1] if len(sys.argv) > 1 else "A1001"
    year = int(sys.argv[2]) if len(sys.argv) > 2 else 2023

    print(f"Generating report for {aco_id}, {year}...")
    report = generate_report(aco_id, year)
    print(json.dumps(report["narrative"], indent=2))

    with open(f"sample_report_{aco_id}_{year}.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nFull report (narrative + data) saved to sample_report_{aco_id}_{year}.json")
