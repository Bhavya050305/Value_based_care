# VBC CommandIQ — Contract Review Report Engine

Real-time report generation: click a button, get a full structured
report back as JSON, rendered as tables/cards (not prose paragraphs).
Nothing is pre-generated or stored for all 476 ACOs — this runs live,
per your research findings on why that's the right call.

## Setup

1. Copy `.env.example` to `.env`, fill in your real Supabase password.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Test the pipeline, one file at a time

### 1. Confirm context assembly works
```
python report_context.py
```
Prints one ACO's full structured JSON, pulled from every real table
(financial, quality, utilization, population, service variation, ML
segmentation, ML anomaly). **Change the ACO_ID/year near the bottom of
`report_context.py` to one you know has data** (e.g. one that showed up
in your `aco_anomalies` output — A1199 or A1241 for 2023 — guarantees
every section has real data to check against).

### 2. Generate one full report (calls Ollama)
```
python generate_report.py A1001 2023
```
This is slower than the small dashboard snippets — it's one large
prompt covering the whole ACO, not five small ones. Give it a bit.
Saves the full report to `sample_report_A1001_2023.json` so you can
inspect exactly what the frontend will receive, and prints just the
narrative portion to your terminal.

**Read the output carefully** — check every number mentioned in
`narrative.*` fields traces back to something in the `data.*` section.
Since this prompt is larger than your earlier dashboard snippets, a 3B
model has more room to drift — if you spot an invented number, tell me
the exact field and I'll tighten that section's instructions.

### 3. Start the live API
```
uvicorn api:app --reload --port 8001
```
Test in your browser: `http://localhost:8001/api/aco/A1001/report?performance_year=2023`

## Hand off to your frontend friend

Give her:
1. **The endpoint**: `GET http://localhost:8001/api/aco/{aco_id}/report?performance_year={year}` (or wherever you deploy `api.py`)
2. **`ContractReviewReport.jsx`** — a complete, working React component that calls that endpoint and renders the full report as tables/cards. She can drop it straight into a Next.js page, or use it as a reference for matching your existing component style.
3. **One `sample_report_*.json` file** (from step 2) — lets her build/test the UI without needing Ollama running on her machine at all.

Tell her explicitly: `report.data` = exact numbers (render directly in
tables), `report.narrative` = LLM-generated short insights (render as
text/cards) — never mix the two, and never let her re-derive a number
from `narrative` text.

## Notes on what's still incomplete

- **Peer Benchmark & Target Finder section**: intentionally shows "Not
  available yet" — Part 6 (peer/KNN target finder) isn't built. Once
  it is, add a `get_peer_targets()` function to `report_context.py`
  following the same pattern as the others, and the JSX component
  already has the section stubbed in to receive it.
- **`aco_report_cache`**: `generate_report.py` writes to this table
  automatically after every generation (best-effort — won't crash the
  report if the write fails). Not currently read back for caching
  (every request regenerates fresh) — add a cache-check at the top of
  `generate_report()` later if generation speed becomes a problem
  during the actual demo.
