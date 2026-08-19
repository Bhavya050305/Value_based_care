# RAG Architecture

## Status

**Awaiting approved knowledge documents and pgvector schema.**

## Purpose

RAG supports methodology, contract documentation, program documentation,
data dictionary, business definitions, and model documentation.

RAG is **not** the source of truth for numerical analytics.

## Pipeline

```
Approved Document
    ↓
Chunker
    ↓
Embedding (provider abstraction)
    ↓
pgvector storage (knowledge_embeddings)
    ↓
Retriever (similarity search + filters)
    ↓
Evidence Builder
    ↓
LLM (grounded explanation only)
```

## AI Assistant Routing

| Question Type | Source |
|---------------|--------|
| Numerical / performance | PostgreSQL analytics |
| Methodology / documentation | RAG |
| Hybrid | SQL analytics + RAG, merged in evidence builder |

## Rules

1. LLM must not invent financial metrics, scores, or predictions.
2. Every RAG-backed answer should cite retrieved document chunks.
3. If retrieval returns insufficient context, respond with explicit unavailability.

## Integration Steps (Phase 18–19)

1. Receive knowledge document set and ingestion approval process.
2. Confirm pgvector table schema from Supabase team.
3. Implement document ingestion worker (not fake content).
4. Implement retriever with organization/global scope rules.
5. Wire intent classifier in `app/ai/assistant.py`.
6. Connect evidence builder before LLM call.

## Required Inputs

- [ ] Approved document corpus list
- [ ] pgvector embedding table schema
- [ ] Embedding model/provider choice
- [ ] Chunk size and metadata conventions
- [ ] Access control rules per document type
