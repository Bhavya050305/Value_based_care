# Value-Based Care Command Center — Backend Architecture

## Purpose

This backend is the business intelligence layer for the Value-Based Care Command Center.
It converts ACO performance data into analytics, risk detection, predictions, recommendations,
actions, and AI-assisted decision support for payer and ACO operators.

The architecture is **integration-ready**: final database schema, dataset columns, ML YAML,
and model artifacts are supplied separately and wired in without replacing this structure.

## Layered Architecture

```
Frontend (supplied separately)
    ↓
FastAPI REST API (/api/v1)
    ↓
Authentication (Supabase JWT)
    ↓
Authorization (RBAC + organization scope)
    ↓
Pydantic validation (schemas/)
    ↓
Service layer (services/)
    ↓
Repository layer (repositories/)
    ↓
Supabase PostgreSQL
```

Parallel domains (never in routers):

| Domain | Package | Responsibility |
|--------|---------|----------------|
| Analytics | `app/analytics/` | Aggregations, KPIs, trends, portfolio metrics |
| ML | `app/ml/` | Feature build, inference, SHAP, artifact loading |
| AI | `app/ai/` | Intent routing, RAG, evidence, LLM explanation |
| Workers | `app/workers/` | Async reports, ingestion jobs, background tasks |

## Non-Negotiable Rule

**No business logic in FastAPI routers.** Routers are thin controllers.

```
Router → Schema → Service → Repository → Database
```

## Domain Boundaries

### 1. Identity & Access (`core/security`, `services/auth`, `repositories/users`)
- Supabase Auth JWT validation
- User profile, organization, role, permissions resolution
- MFA state from auth provider (no custom password storage)
- Audit logging for sensitive operations

### 2. Portfolio (`services/portfolio`, `analytics/portfolio`, `repositories/acos`)
- Executive summary KPIs
- Risk distribution, trends, performance categories
- Portfolio ACO table, opportunities, alerts
- **Source:** PostgreSQL only

### 3. ACO Explorer (`services/aco`, `repositories/acos`)
- Search, filter, pagination, sorting
- ACO list and detail views

### 4. ACO Performance (`services/performance`, `analytics/performance`)
- Financial, quality, utilization, value, snapshot, contract
- Centralized analytics — no duplicate calculations across endpoints

### 5. Historical Trends (`services/trends`, `analytics/trends`)
- Multi-year chart-ready time series
- YoY changes and trajectory

### 6. Performance Drivers / XAI (`services/drivers`, `ml/inference`, `ml/explainability`)
- Predictions + SHAP + business interpretation
- Never fabricate feature importance

### 7. What-If Simulator (`services/simulator`, `ml/inference`)
- Baseline → scenario → delta
- Explicit limitations; never guaranteed forecasts

### 8. Recommendations (`services/recommendations`, `analytics/opportunities`)
- Analytics + business rules + ML signals + evidence
- LLM may explain; LLM must not invent evidence

### 9. Actions & Outcomes (`services/actions`, `services/outcomes`)
- Recommendation → Action → Outcome closed loop

### 10. AI Assistant (`ai/assistant`, `ai/rag`, `ai/evidence`)
- Intent: SQL analytics | RAG | hybrid
- Numerical truth from PostgreSQL; methodology from RAG

### 11. Reports (`services/reports`, `workers/reports`)
- Async generation → Supabase Storage → authorized download

### 12. Settings & Admin (`services/settings`, `services/admin`)
- Profile, preferences, org config (RBAC-gated)

## Data Flow

```
Supplied Dataset
    ↓
scripts/validate_data.py
    ↓
scripts/import_data.py
    ↓
Supabase PostgreSQL (supplied schema)
    ↓
Analytics Services
    ↓
ML Feature Builder (supplied YAML)
    ↓
Model Inference (supplied artifacts)
    ↓
API Responses (with data lineage metadata)
```

## Source-of-Truth Policy

Every value must originate from:

1. Supabase PostgreSQL records
2. Validated ingested production dataset
3. Analytics computed from real DB data
4. Supplied ML model artifacts
5. Actual SHAP values from supplied models
6. Simulator calculations with real baseline + available model
7. Recommendations with traceable evidence
8. Approved RAG knowledge documents
9. LLM explanations grounded in the above
10. Authenticated user/configuration data

When data is unavailable, return explicit structured unavailability — never fake values.

See `app/schemas/common.py` → `DataAvailability`.

## Integration Points (Pending External Inputs)

| Input | Phase | Integration Location |
|-------|-------|---------------------|
| Supabase PostgreSQL schema | 5 | `app/models/`, `alembic/`, `docs/DATABASE_MAPPING.md` |
| Cleaned production dataset | 6 | `scripts/validate_data.py`, `scripts/import_data.py` |
| ML YAML + artifacts | 12 | `app/ml/inference/`, `app/ml/features/` |
| RAG knowledge documents | 18 | `app/ai/rag/` |
| LLM provider config | 19 | `app/ai/llm/` |
| Frontend API contract alignment | 7+ | `docs/API_CONTRACT.md` |

## Implementation Phases

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Architecture + project structure | **Current** |
| 2 | FastAPI foundation (app factory, health, error handlers) | Next |
| 3 | Supabase/PostgreSQL connection | Pending |
| 4 | Authentication + RBAC | Pending |
| 5 | Database schema integration | Pending |
| 6 | Dataset validation/import | Pending |
| 7 | Portfolio APIs | Pending |
| 8 | ACO Explorer APIs | Pending |
| 9 | ACO Performance APIs | Pending |
| 10 | Historical Trends | Pending |
| 11 | Alerts | Pending |
| 12 | ML integration | Pending |
| 13 | SHAP/XAI | Pending |
| 14 | What-If Simulator | Pending |
| 15 | Recommendation Engine | Pending |
| 16 | Action Tracking | Pending |
| 17 | Outcome Tracking | Pending |
| 18 | RAG | Pending |
| 19 | AI Assistant | Pending |
| 20 | Reports | Pending |
| 21 | Settings/Admin | Pending |
| 22 | Testing | Pending |
| 23 | Docker/CI/CD | Pending |
| 24 | Production hardening | Pending |

## Technology Stack

- Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.x async, asyncpg, Alembic
- Supabase PostgreSQL, Auth, Storage
- Redis (cache/background jobs)
- XGBoost, LightGBM, SHAP (when artifacts supplied)
- pgvector RAG, LLM provider abstraction
- pytest, Docker, GitHub Actions

## Notes on Existing Repository Artifacts

The repository contained only a skeleton before Phase 1:

- Root `README.md`, `.env.example`, `docker-compose.yml` skeleton
- `backend/requirements.txt` (minimal, updated in Phase 1)
- Empty `app/routers/` and `app/ollama/` directories (not part of approved structure — use `app/api/v1/` and `app/ai/llm/` instead)
