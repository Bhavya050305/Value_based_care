# Database Mapping Plan

## Status

**Awaiting supplied Supabase PostgreSQL schema.**

This document will map ORM models, repositories, and analytics queries to the
final database tables and columns. Do not invent schema here.

## Conceptual Domains (Not Final Tables)

These domains guide service and repository boundaries only:

| Domain | Likely Concerns | Backend Packages |
|--------|-----------------|------------------|
| Organizations | Tenant isolation | `repositories/organizations` |
| Users / Profiles | Auth profile extension | `repositories/users` |
| ACOs | Contract metadata, identifiers | `repositories/acos` |
| Performance | Financial, quality, utilization | `repositories/performance` |
| Predictions | Model outputs, versioning | `repositories/predictions` |
| Prediction Explanations | SHAP records | `repositories/explanations` |
| Alerts | Portfolio and ACO alerts | `repositories/alerts` |
| Recommendations | Generated recommendations | `repositories/recommendations` |
| Actions | Accepted recommendation tasks | `repositories/actions` |
| Action Outcomes | Measured impact | `repositories/outcomes` |
| Simulations | What-if scenarios | `repositories/simulations` |
| AI Conversations / Messages | Assistant history | `repositories/assistant` |
| Knowledge Documents / Embeddings | RAG (pgvector) | `repositories/knowledge` |
| Reports | Async report jobs | `repositories/reports` |
| Data Sources / Ingestion Jobs | Pipeline tracking | `repositories/ingestion` |
| Audit Logs | Security and business audit | `repositories/audit` |

## Integration Steps (Phase 5)

1. Receive final Supabase schema (SQL migration or ERD).
2. Create SQLAlchemy models in `app/models/` matching supplied tables exactly.
3. Generate or align Alembic migrations — do not replace supplied schema.
4. Implement repositories with organization-scoped queries.
5. Update this document with table → model → repository → service mapping.
6. Add indexes verification checklist against analytics query patterns.

## Organization Scoping

All business data queries must filter by authenticated user's `organization_id`
unless explicitly admin-global (RBAC-gated).

## Required Inputs

- [ ] Supabase schema SQL or migration files
- [ ] Primary keys and foreign key relationships
- [ ] Performance year column conventions
- [ ] ACO identifier field(s) used across tables
- [ ] pgvector extension and embedding table definitions (for Phase 18)
- [ ] RLS policies (if enforced at DB level vs application level)
