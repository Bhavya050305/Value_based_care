# 🏥 Value-Based Care Command Center (VBC Insights)

> **Enterprise Payer-Facing Analytics Dashboard & Decision Support System for Medicare Shared Savings Program (MSSP) ACOs**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=white)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4+-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![PostgreSQL / Supabase](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-3ECF8E?style=flat&logo=supabase&logoColor=white)](https://supabase.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Executive Overview

The **Value-Based Care (VBC) Command Center** is a specialized analytics platform built for healthcare payers and Accountable Care Organization (ACO) executives participating in the **CMS Medicare Shared Savings Program (MSSP)**. 

By unifying CMS financial & quality datasets with advanced Machine Learning (outlier detection, risk segmentation, predictive modeling, and SHAP explainability) and an interactive AI Assistant, the platform answers critical executive questions:
- *Which ACO contracts are at risk of missing gross savings targets?*
- *What specific clinical, financial, or operational features drive underperformance?*
- *What targeted interventions will maximize earned shared savings?*

---

## ✨ Key Features

- 📊 **CMS Financial & Quality Analytics:** Ingests and normalizes multi-year CMS MSSP performance datasets across 400+ active ACOs.
- 🔮 **Predictive Machine Learning Pipeline:**
  - **Financial Savings/Loss Prediction:** Random Forest / XGBoost model predicting `Generated Savings/Loss` based on 61 historical features.
  - **ACO Risk Segmentation:** K-Means clustering algorithm segmenting ACOs into 4 distinct performance risk tiers.
  - **Anomaly & Outlier Detection:** Local Outlier Factor (LOF) identifying anomalous spending patterns and data inconsistencies.
- 💡 **Explainable AI (SHAP Attributions):** Surfaces top feature attributions explaining *why* an ACO is predicted to over- or under-perform.
- 🤖 **Interactive LLM Decision Assistant:** Natural-language AI copilot for executive query processing and strategic recommendation generation.
- 🎨 **Modern Executive Dashboard UI:** Built with React 19, TypeScript, TailwindCSS, and Recharts with sleek dark mode visuals and responsive data exploration.

---

## 🏗 System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                         REACT 19 + VITE FRONTEND                       │
│        (Dashboard, ACO Explorer, ML Analytics, AI Assistant)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST API (JSON)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND API                          │
│     (Routers: Health, ACOs, Financials, Predictions, Segmentation)     │
└──────┬────────────────────────────┬─────────────────────────────┬──────┘
       │                            │                             │
       ▼                            ▼                             ▼
┌──────────────┐          ┌───────────────────┐         ┌────────────────┐
│  SQLAlchemy  │          │ Central Feature   │         │ ML Inference   │
│  2.0 Async   │          │     Builder       │         │ (Scikit-Learn, │
└──────┬───────┘          └─────────┬─────────┘         │  XGBoost, SHAP)│
       │                            │                   └────────────────┘
       ▼                            ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   SUPABASE POSTGRESQL DATABASE                         │
│       (public.aco_financial_ml_training, public.acos, etc.)            │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Layout

```
Value_based_care/
├── backend/                  # FastAPI Backend Application
│   ├── app/                  # Application Core
│   │   ├── api/v1/           # REST Endpoints (ACOs, ML, Health, Assistant)
│   │   ├── core/             # Configuration & Database Sessions
│   │   ├── db/               # SQLAlchemy Models & Migrations
│   │   ├── ml/               # Trained Model Artifacts & Feature Pipelines
│   │   ├── repositories/     # Database Access Layer
│   │   └── services/         # Business Logic & Feature Builder
│   ├── alembic/              # Database Migration Scripts
│   ├── scripts/              # Ingestion & Data Verification Scripts
│   ├── tests/                # Pytest Test Suite
│   ├── requirements.txt      # Python Dependencies
│   └── README.md             # Backend Documentation
│
├── frontend/                 # React 19 Frontend Application
│   ├── src/                  # Source Files
│   │   ├── components/       # UI Components (Charts, Cards, Navigation)
│   │   ├── pages/            # View Pages (Dashboard, Explorer, Analytics)
│   │   ├── services/         # API Service Clients (Axios/Fetch)
│   │   └── types/            # TypeScript Interface Definitions
│   ├── package.json          # Node.js Dependencies
│   ├── vite.config.ts        # Vite Build Configuration
│   └── README.md             # Frontend Documentation
│
├── docs/                     # Architecture & Product Documentation
├── data/                     # Data Templates & Schema Artifacts
└── README.md                 # Root Repository README
```

---

## 🛠 Tech Stack

### **Backend**
- **Language:** Python 3.10+
- **Framework:** FastAPI (0.115+)
- **ORM / Database Driver:** SQLAlchemy 2.0 (Async) + `asyncpg`
- **Database:** PostgreSQL (Supabase Hosted)
- **ML / Analytics:** Scikit-Learn, XGBoost, LightGBM, SHAP, Pandas, NumPy
- **Migrations:** Alembic
- **Testing:** Pytest & Pytest-Asyncio

### **Frontend**
- **Framework:** React 19 + Vite 8
- **Language:** TypeScript 5.0+
- **Styling:** Tailwind CSS 3.4
- **Icons:** Lucide React
- **Data Visualization:** Recharts 3.10+
- **Linter:** Oxlint

---

## 🚀 Getting Started

### **Prerequisites**
- Python `3.10` or higher
- Node.js `18.0` or higher & `npm`
- PostgreSQL database (Local or Supabase account)

---

### **1. Backend Setup**

```powershell
# Navigate to backend directory
cd backend

# Create and activate virtual environment (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt

# Create local environment configuration
cp .env.example .env
```

#### **Configure Backend `.env`**
Edit `backend/.env` with your database and environment settings:
```ini
APP_NAME="Value-Based Care Command Center API"
ENVIRONMENT="development"
DEBUG=true
API_V1_PREFIX="/api/v1"

# Database Connection (Supabase / Postgres)
DATABASE_URL="postgresql+asyncpg://postgres:your_password@localhost:5432/vbc_dev"

# Supabase Credentials
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_ANON_KEY="your-anon-key"
```

#### **Populate Database & Run Verification**
```powershell
# Populate database with real CMS ACO performance records
python scripts/populate_real_aco_data.py

# Run integration tests
pytest -v
```

#### **Start FastAPI Server**
```powershell
uvicorn app.main:app --reload --port 8000
```
- Interactive API Specs (Swagger UI): `http://localhost:8000/docs`
- Alternative API Specs (ReDoc): `http://localhost:8000/redoc`

---

### **2. Frontend Setup**

```powershell
# Open a new terminal and navigate to frontend directory
cd frontend

# Install Node modules
npm install

# Start Vite Development Server
npm run dev
```
- App will be accessible at: `http://localhost:5173`

---

## 📡 API Overview

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/health` | `GET` | Server health check |
| `/api/v1/health/models` | `GET` | Status of loaded ML models |
| `/api/v1/acos/{aco_id}/summary` | `GET` | Overall summary for specified ACO |
| `/api/v1/acos/{aco_id}/financial` | `GET` | Financial performance metrics by year |
| `/api/v1/predictions` | `POST` | Execute ML savings prediction & SHAP breakdown |
| `/api/v1/segmentation/predict` | `POST` | Assign risk cluster to input ACO features |
| `/api/v1/assistant/query` | `POST` | Execute AI Assistant natural language query |

---

## 🔒 Strict Data Integrity Policy

This project strictly adheres to **zero synthetic/fake data generation** for business analytics:
- All financial, benchmark, quality, and risk score metrics are directly derived from official **CMS MSSP public performance datasets** stored in PostgreSQL.
- Predictive models and clusterings are trained exclusively on verified historical performance year data.

---

## 📄 License

This repository is licensed under the [MIT License](LICENSE).

