# Security Architecture

## Authentication

- **Provider:** Supabase Auth
- **Mechanism:** JWT bearer tokens validated server-side
- **Password storage:** None in application database
- **MFA:** Provider-managed flow; backend validates session/MFA state

## Authorization

- Role-Based Access Control (RBAC)
- Organization-level data isolation on all business queries
- Admin-only endpoints gated by permission checks
- Settings that expose system configuration require elevated roles

## Secrets

| Secret | Exposure |
|--------|----------|
| `SUPABASE_SERVICE_ROLE_KEY` | Server only — never frontend, never logs |
| `SUPABASE_JWT_SECRET` | Server only |
| `LLM_API_KEY` | Server only |
| `DATABASE_URL` | Server only |

## API Security

- CORS restricted to configured origins
- Input validation via Pydantic v2 on all request bodies and query params
- Rate limiting (Phase 24)
- Request ID tracing for audit correlation
- No internal stack traces in client error responses

## Audit Logging

Sensitive operations to audit:

- Authentication failures
- Authorization denials
- Recommendation accept/dismiss
- Action create/update/complete
- Report generation and download
- Admin configuration changes
- Data import job execution

Audit records stored in `audit_logs` table once schema is supplied.

## File Handling

- Report downloads via authorized signed URLs (Supabase Storage)
- Validate content types and size limits on uploads (when applicable)

## Implementation Phases

| Control | Phase |
|---------|-------|
| JWT validation | 4 |
| RBAC dependencies | 4 |
| Organization scoping in repositories | 5 |
| Audit log writes | 5+ |
| Rate limiting | 24 |
| Production CORS/hardening | 24 |

## Required Inputs

- [ ] Supabase project URL and keys
- [ ] Role and permission matrix
- [ ] Organization model and user assignment rules
- [ ] MFA requirements per role/environment
