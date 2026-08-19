# Deployment Architecture

## Status

Skeleton only — full deployment in Phase 23.

## Components

| Service | Purpose |
|---------|---------|
| `backend` | FastAPI application (uvicorn) |
| `redis` | Cache and background job broker |
| Supabase | Managed PostgreSQL, Auth, Storage |
| Worker (optional) | Report generation, ingestion jobs |

Frontend is supplied and deployed separately.

## Environment Variables

See `backend/.env.example`. Required for production:

- `DATABASE_URL` (asyncpg format)
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_JWT_SECRET`
- `REDIS_URL`
- `CORS_ORIGINS`
- LLM provider settings (when AI is enabled)

## Docker

- `backend/Dockerfile` — multi-stage Python 3.12 image
- Root `docker-compose.yml` — local development stack skeleton

Production compose and orchestration finalized in Phase 23.

## CI/CD (Phase 23)

GitHub Actions pipeline planned:

1. Lint / type check
2. pytest (unit + integration + api)
3. Docker build
4. Deploy to staging (manual approval for production)

## Health Checks

- `GET /api/v1/health` — process alive
- `GET /api/v1/health/ready` — database and redis connectivity

## Production Hardening (Phase 24)

- Structured JSON logging
- Rate limiting
- Secret rotation runbook
- Connection pool tuning
- Query performance review

## Required Inputs

- [ ] Target deployment platform (AWS/GCP/Azure/VPS)
- [ ] Staging and production Supabase projects
- [ ] Domain and TLS configuration
- [ ] GitHub Actions secrets
