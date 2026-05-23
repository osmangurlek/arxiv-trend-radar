# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

Python 3.13+. The project uses a plain `requirements.txt` + `env/` virtualenv — **not** `uv`, despite some sibling projects in `~/Developer/`. Always activate before running anything:

```bash
source env/bin/activate
```

All Python entry points must run from the **project root** because internal imports are absolute (`from backend.app.database import ...`). Running e.g. `cd backend && python -m app.main` will break.

`.env` lives at the repo root and is loaded by `backend/app/database.py` and `backend/db/env.py` via `python-dotenv`. Required vars: `POSTGRES_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `OPENAI_API_KEY`.

> **`OPENAI_API_KEY` is actually an OpenRouter key.** All LLM services hardcode `base_url="https://openrouter.ai/api/v1"` and `model="openai/gpt-5.2"` (see `backend/app/llm/*.py`). The variable name is misleading — do not point it at api.openai.com.

## Common commands

```bash
# Database (Postgres in Docker)
docker compose up -d            # start
docker compose down             # stop

# Migrations (Alembic config lives at repo root; script_location = backend/db)
alembic upgrade head
alembic revision --autogenerate -m "description"
alembic downgrade -1

# Backend (FastAPI on :8000)
uvicorn backend.app.main:app --reload --port 8000

# Frontend (Streamlit on :8501; talks to FastAPI over HTTP)
streamlit run frontend/streamlit_app.py --server.port 8501

# CLI pipeline
python cli.py ingest --query "retrieval augmented generation" --limit 10
python cli.py canonicalize
python cli.py digest --week-start 2026-01-06
```

There are no tests, no linter config, and no formatter config in this repo.

## Architecture

### Two-process runtime
The Streamlit frontend and FastAPI backend are **separate processes** that communicate over HTTP. The Streamlit pages do `requests.get(f"{API_URL}/...")` against `API_URL` (default `http://localhost:8000`). The frontend never touches the database directly — if a page is failing, check that uvicorn is also running. CORS is allowlisted for `localhost:8501` in `backend/app/main.py`.

### Backend layering (`backend/app/`)
Strict directional dependencies — each layer only imports from layers below it:

```
api/         FastAPI routers (papers, entities, trends, digest) + /ingest in main.py
  ↓
services/    Orchestration (only ingestion_services.py today)
  ↓
repositories/  Data access — paper_repo, entity_repo, analytics_repo (analytics is
               module-level functions, not a class, unlike the others)
  ↓
models/      SQLAlchemy ORM (single file: models.py)
llm/         LangChain-based services, used by services/ and cli.py
schemas/     Pydantic models for both API responses AND LLM structured output
             (PaperExtractionSchema, PaperClassificationSchema, CanonicalizationSchema)
```

`schemas/schemas.py` does double duty: API request/response shapes AND `.with_structured_output(...)` targets for the LLM. Changing one of the LLM schemas changes the LLM's output contract — don't refactor casually.

### The LLM pipeline (4 stages, OpenRouter via LangChain)
1. **Entity extraction** (`llm/entity_extraction.py`) — extracts tasks/datasets/methods/libraries per paper. Runs inline during ingestion.
2. **Paper classification** (`llm/paper_classification.py`) — assigns taxonomy tags. Also inline during ingestion.
3. **Canonicalization** (`llm/canonicalization.py`) — deduplicates entities via `canonical_id` self-FK on the `entities` table. Run **manually** via `python cli.py canonicalize`, not on every ingest.
4. **Digest generation** (`llm/digest_generator.py`) — turns analytics rows into a weekly markdown report. Run manually via `python cli.py digest --week-start YYYY-MM-DD`. Reads from `analytics_repo`, writes a row to the `digests` table.

Stages 1 and 2 each have per-paper retry on 429s (see `entity_extraction.py:60-72`); failures are caught in `ingestion_services.py` and logged so one bad paper doesn't kill a batch.

### Ingestion data flow
`IngestionService.fetch_and_save` (in `services/ingestion_services.py`) drives it: `arxiv` library → `paper_repo.upsert_paper` → `llm_service.extract_entities` → `entity_repo.upsert_entities` + `upsert_paper_entity` → `classification_service.classify_paper` → `paper_repo.add_paper_tag`. The transaction is committed once at the end by the caller (CLI or `/ingest` endpoint), not by the service.

### Schema management — two sources of truth (gotcha)
- `backend/app/main.py:23` calls `models.Base.metadata.create_all(bind=engine)` on FastAPI startup.
- Alembic also manages schema (`alembic.ini` → `backend/db/versions/`).

If you add a model and start the backend before running `alembic revision --autogenerate`, `create_all` will create the table without a migration, and the next autogenerate will produce an empty diff. Run migrations against a fresh DB to verify.

### Analytics queries (`repositories/analytics_repo.py`)
This is where the SQL-heavy logic lives. The cooccurrence query uses an aliased self-join on `paper_entities` with the `ent1.id < ent2.id` trick to avoid duplicate edges — keep that constraint if editing. `category_distribution_over_time` uses `func.unnest(...)` on the Postgres array column `papers.categories`, which is Postgres-specific.

## Conventions and quirks

- The user's primary language is Turkish; some inline comments are in Turkish (e.g. `# En yeniden en eskiye` in `ingestion_services.py`). Don't translate them.
- The `--days` flag on `cli.py ingest` and the `days` query param on `POST /ingest` are **not implemented** — the arXiv search uses `sort_by=SubmittedDate` and `max_results` only. Don't claim a date filter exists.
- The repo at `/Users/ogi/Developer/` is a thin shell; this project has its own git history. Commit here, not at the parent.
