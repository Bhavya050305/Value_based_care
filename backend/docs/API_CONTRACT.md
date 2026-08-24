# API Contract Plan

Base URL: `/api/v1`

## Response Envelopes

### Success

```json
{
  "success": true,
  "data": {},
  "meta": {
    "request_id": "uuid",
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 0,
      "total_pages": 0
    }
  }
}
```

### Error

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Human-readable message",
    "request_id": "uuid",
    "details": {}
  }
}
```

### Data Unavailability

When required source data or models are missing:

```json
{
  "available": false,
  "value": null,
  "data_status": "INSUFFICIENT_DATA",
  "reason": "Required source data is not available.",
  "source": null,
  "required_source": "supabase.aco_financial_ml_training",
  "last_updated": null
}
```

## Page-to-Endpoint Mapping

| UI Page | Method | Endpoint | Phase |
|---------|--------|----------|-------|
| Login | GET | `/auth/me` | 4 |
| MFA | — | Supabase Auth flow; backend validates session | 4 |
| Portfolio Overview | GET | `/portfolio/summary` | 7 |
| Portfolio Overview | GET | `/portfolio/risk-distribution` | 7 |
| Portfolio Overview | GET | `/portfolio/trends` | 7 |
| Portfolio Overview | GET | `/portfolio/performance-categories` | 7 |
| Portfolio Overview | GET | `/portfolio/acos` | 7 |
| Portfolio Overview | GET | `/portfolio/opportunities` | 7 |
| Portfolio Overview | GET | `/portfolio/alerts` | 7 |
| ACO Explorer | GET | `/acos` | 8 |
| ACO Explorer | GET | `/acos/{aco_id}` | 8 |
| ACO Performance | GET | `/acos/{aco_id}/summary` | 9 |
| ACO Performance | GET | `/acos/{aco_id}/financial` | 9 |
| ACO Performance | GET | `/acos/{aco_id}/quality` | 9 |
| ACO Performance | GET | `/acos/{aco_id}/utilization` | 9 |
| ACO Performance | GET | `/acos/{aco_id}/value` | 9 |
| ACO Performance | GET | `/acos/{aco_id}/snapshot` | 9 |
| ACO Performance | GET | `/acos/{aco_id}/contract` | 9 |
| Historical Trends | GET | `/acos/{aco_id}/trends` | 10 |
| Historical Trends | GET | `/acos/{aco_id}/trends/financial` | 10 |
| Historical Trends | GET | `/acos/{aco_id}/trends/quality` | 10 |
| Historical Trends | GET | `/acos/{aco_id}/trends/utilization` | 10 |
| Performance Drivers | GET | `/acos/{aco_id}/drivers` | 13 |
| Performance Drivers | GET | `/acos/{aco_id}/predictions` | 12 |
| Performance Drivers | GET | `/predictions/{prediction_id}/explanations` | 13 |
| What-If Simulator | POST | `/simulations` | 14 |
| What-If Simulator | GET | `/simulations/{simulation_id}` | 14 |
| What-If Simulator | GET | `/acos/{aco_id}/simulations` | 14 |
| Recommendations | GET | `/recommendations` | 15 |
| Recommendations | GET | `/recommendations/{recommendation_id}` | 15 |
| Recommendations | POST | `/recommendations/{recommendation_id}/accept` | 15 |
| Recommendations | POST | `/recommendations/{recommendation_id}/dismiss` | 15 |
| Action Tracking | GET | `/actions` | 16 |
| Action Tracking | POST | `/actions` | 16 |
| Action Tracking | GET | `/actions/{action_id}` | 16 |
| Action Tracking | PATCH | `/actions/{action_id}` | 16 |
| Action Tracking | POST | `/actions/{action_id}/complete` | 16 |
| Outcomes | GET | `/actions/{action_id}/outcomes` | 17 |
| AI Assistant | POST | `/assistant/conversations` | 19 |
| AI Assistant | GET | `/assistant/conversations` | 19 |
| AI Assistant | GET | `/assistant/conversations/{id}` | 19 |
| AI Assistant | POST | `/assistant/conversations/{id}/messages` | 19 |
| Reports | POST | `/reports` | 20 |
| Reports | GET | `/reports` | 20 |
| Reports | GET | `/reports/{report_id}` | 20 |
| Reports | GET | `/reports/{report_id}/download` | 20 |
| Settings | GET/PATCH | `/settings/profile` | 21 |
| Settings | GET/PATCH | `/settings/preferences` | 21 |
| Admin | TBD | `/admin/*` | 21 |
| Health | GET | `/health`, `/health/ready` | 2 |

## Common Query Parameters

| Parameter | Used By | Description |
|-----------|---------|-------------|
| `page` | List endpoints | 1-based page number |
| `page_size` | List endpoints | Items per page (max enforced server-side) |
| `search` | ACO Explorer, recommendations | Text search |
| `year` | Portfolio, ACO endpoints | Performance year filter |
| `risk_level` | ACO Explorer | Risk filter |
| `track` | ACO Explorer | MSSP track filter |
| `agreement_type` | ACO Explorer | Agreement type filter |
| `sort_by` | List endpoints | Column to sort |
| `sort_order` | List endpoints | `asc` or `desc` |

## Contract Rules

1. Routers delegate to services; services return Pydantic schemas.
2. Pagination metadata reflects actual database counts.
3. ML endpoints return `MODEL_UNAVAILABLE` when artifacts are absent.
4. Simulation responses include baseline source, model version, limitations.
5. Recommendations include evidence arrays traceable to metrics/rules/ML signals.
6. AI responses include evidence references where available.
7. Final field names will align with supplied Supabase schema and frontend types in Phase 5+.

## Pending Alignment

- Exact response field names per entity (awaiting Supabase schema)
- Recommendation category enum (awaiting business schema)
- Simulation scenario variable list (awaiting ML YAML)
- Report type enum and storage paths (awaiting product sign-off)
