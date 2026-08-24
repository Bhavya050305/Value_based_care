# Data Mapping Plan

## Status

**Awaiting cleaned production dataset.**

## Pipeline Architecture

```
Supplied Dataset (CSV/Parquet/etc.)
    ↓
scripts/validate_data.py      → validation report (JSON + human summary)
    ↓
Column Mapping Config         → supplied with dataset or data dictionary
    ↓
scripts/import_data.py        → transform + load to Supabase PostgreSQL
    ↓
Analytics + ML Feature Builder
```

## Validation Report Requirements

`validate_data.py` must produce:

- Row count
- Column list
- Missing value summary per column
- Duplicate detection
- Invalid value checks (types, ranges per data dictionary)
- Date coverage
- ACO count
- Provider count (if available)
- Performance years present
- Data quality issues (never silently discard invalid rows)

## Import Rules

1. Invalid rows are logged and excluded with explicit counts — not silently dropped.
2. No fake or demo records inserted at any stage.
3. Idempotent import strategy to be defined when dataset format is known.
4. Import jobs tracked in `ingestion_jobs` table (once schema supplied).

## Required Inputs

- [ ] Cleaned production dataset file(s)
- [ ] Data dictionary / column definitions
- [ ] Column → database table mapping
- [ ] Performance year and ACO key conventions
- [ ] Null handling and business validation rules
- [ ] Target Supabase connection for staging import

## Phase 6 Deliverables

- Working `validate_data.py` against supplied dataset
- Working `import_data.py` loading into supplied schema
- Updated mapping tables in this document
