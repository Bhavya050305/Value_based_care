# Value-Based Care Command Center — Backend

Enterprise backend for the VBC Command Center: analytics, ML predictions, risk segmentation, anomaly detection, recommendations, actions, and decision support for Medicare Shared Savings Program (MSSP) ACOs.

---

## Architecture Overview

```
REAL SUPABASE / POSTGRESQL DATABASE
        ↓
DATABASE CONNECTION (Async SQLAlchemy 2.0 / asyncpg)
        ↓
SQLAlchemy ORM (public.aco_financial_ml_training, acos, etc.)
        ↓
DOMAIN REPOSITORIES & SERVICES
        ↓
CENTRAL FEATURE BUILDER (app/services/feature_builder.py)
        ↓
ML MODELS (Financial RandomForest, Segmentation KMeans, Anomaly LOF)
        ↓
FASTAPI API (Swagger UI / ReDoc)
        ↓
FRONTEND COMMAND CENTER
```

---

## Status

- **Database Source of Truth:** Async SQLAlchemy connected to PostgreSQL (`vbc_dev` / Supabase).
- **Precomputed CMS Financial Dataset:** Integrated `public.aco_financial_ml_training` table containing 407 real ACO records for MSSP performance years.
- **ML Models Integrated:**
  - **Financial Prediction:** `app/ml/artifacts/best_GenSaveLoss_model.joblib` (61 candidate features).
  - **Segmentation:** `app/ml/segmentation/model.pkl` (15 features).
  - **Anomaly Detection:** `app/ml/anomaly/model.pkl` (10 features).
- **Health & Readiness Endpoints:** `GET /api/v1/health`, `GET /api/v1/health/ready`, `GET /api/v1/health/models`.
- **Test Suite:** 27 automated unit/integration tests passing.

---

## Environment Setup & Configuration

1. **Clone & Setup Virtual Environment (Windows PowerShell):**
   ```powershell
   cd c:\Users\User\Value_based_care\backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables (`.env`):**
   ```ini
   APP_NAME=Value-Based Care Command Center API
   ENVIRONMENT=development
   DEBUG=false
   API_V1_PREFIX=/api/v1

   # PostgreSQL / Supabase Async Connection URL
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/vbc_dev
   DATABASE_SSL=false

   # Supabase Credentials
   SUPABASE_URL=https://wuazaratvveeemdpeait.supabase.co
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_JWT_SECRET=8AYSVhRZTu5amqHlxuiLDWYVD5muyPWpqAMiFceR0gD1PRDwt5GbwziupDpjKbV9RjHL/MLGjdOttj+nkYbVAA==

   # ML Artifact Paths
   ML_ARTIFACTS_PATH=app/ml/artifacts
   ```

---

## Database Population & Verification Commands

```powershell
# 1. Populate vbc_dev with 407 real CMS ACO records from ML evaluation artifacts
python scripts/populate_real_aco_data.py

# 2. Run End-to-End Integration Verification Script
python scripts/check_backend_integration.py

# 3. Run Pytest Test Suite
pytest -v
```

---

## Running the Backend API

```powershell
uvicorn app.main:app --reload --port 8000
```

- **Swagger Documentation:** `http://localhost:8000/docs`
- **ReDoc Documentation:** `http://localhost:8000/redoc`

---

## Core API Endpoints & Example Requests

### Health & Model Status
- `GET /api/v1/health`
- `GET /api/v1/health/models`

### ACO Explorer & Financial Performance
- `GET /api/v1/acos/A1001/summary`
- `GET /api/v1/acos/A1001/financial?year=2024`
- `GET /api/v1/acos/A4604/financial?year=2024`

### ML Predictions & Risk Analytics
- `POST /api/v1/segmentation/predict`
- `POST /api/v1/predictions`

---

## Troubleshooting

- **Supabase Connectivity:** If direct Supabase DB host resolution fails on IPv4 Windows networks, configure an explicit IPv4 pooler connection string in `DATABASE_URL`.
- **Model Loading Health:** Inspect `GET /api/v1/health/models` to confirm all 3 ML models report `"loaded"`.
