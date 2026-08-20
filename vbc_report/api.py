"""
Real-time endpoint your backend/frontend friend calls to generate the
report on demand — this IS the "fetch in real time" you asked about.
Each call assembles fresh context and calls Ollama live (takes a few
seconds, unlike your pre-generated dashboard snippets).

Run with:  uvicorn api:app --reload --port 8001
(port 8001, not 8000 — keeps this separate from your other LLM project's
api.py if you ever run both at once)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from generate_report import generate_report

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/aco/{aco_id}/report")
def get_report(aco_id: str, performance_year: int = 2023):
    try:
        report = generate_report(aco_id, performance_year)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")
