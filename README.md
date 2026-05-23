# arXiv Trend Radar

A system for tracking and analyzing trends in arXiv research papers. This project ingests papers from arXiv, extracts entities (models, datasets, methods) using LLM, stores everything in PostgreSQL, and provides trend analytics.

## Tech Stack

- **Python 3.13+**
- **FastAPI** - Backend API
- **React 18 + Vite** - Frontend SPA
- **Tailwind CSS + Recharts** - UI styling and charts
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **LangChain + OpenRouter** - LLM services (model: `openai/gpt-5.2`)
- **Docker Compose** - Container orchestration

## Features

- **Paper Ingestion** - Fetch papers from arXiv API
- **LLM Entity Extraction** - Extract tasks, datasets, methods, libraries from abstracts
- **Paper Classification** - Taxonomy tagging (RAG, Agents, Multimodal, etc.)
- **Entity Canonicalization** - Merge duplicate entities (e.g., RLHF → Reinforcement Learning from Human Feedback)
- **Weekly Digest Generation** - LLM-generated markdown reports
- **CLI Tool** - Command-line interface for ingestion and operations
- **SQL Analytics** - Trend queries (top entities, growth, co-occurrence)
- **FastAPI Endpoints** - REST API for papers, entities, trends, and digest
- **React Dashboard** - Interactive web UI for exploring trends

## Database Schema

| Table | Description |
|-------|-------------|
| `papers` | arXiv papers with title, abstract, authors, categories |
| `entities` | Extracted entities (dataset, method, task, library) with canonical_name |
| `paper_entities` | Many-to-many relation between papers and entities with evidence |
| `paper_tags` | Taxonomy tags assigned to papers with confidence scores |
| `digests` | Weekly markdown digest summaries |

## Setup

### Prerequisites

- Python 3.13+
- Node.js 18+
- Docker & Docker Compose
- OpenRouter API Key (get one at https://openrouter.ai)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/osmangurlek/arxiv-trend-radar.git
   cd arxiv-trend-radar
   ```

2. **Create Python virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Create `.env` file**
   ```bash
   cat > .env << EOF
   POSTGRES_URL=postgresql://YOUR_DB_USERNAME:YOUR_DB_PASSWORD@localhost:5433/YOUR_DB_NAME
   POSTGRES_USER=YOUR_DB_USERNAME
   POSTGRES_PASSWORD=YOUR_DB_PASSWORD
   POSTGRES_DB=YOUR_DB_NAME
   OPENAI_API_KEY=your_openrouter_api_key_here
   EOF
   ```
   > `OPENAI_API_KEY` holds your **OpenRouter** key. All LLM calls go to `https://openrouter.ai/api/v1`.

5. **Start PostgreSQL**
   ```bash
   docker compose up -d
   ```
   > PostgreSQL is exposed on port **5433** (mapped from container port 5432).

6. **Run migrations**
   ```bash
   alembic upgrade head
   ```

## Usage

### Running the Application

Start backend and frontend in separate terminals:

```bash
# Terminal 1: FastAPI backend
source env/bin/activate
uvicorn backend.app.main:app --reload --port 8000

# Terminal 2: React frontend (Vite dev server)
cd frontend
npm run dev
```

Access the applications:
- **React Dashboard**: http://localhost:5173
- **FastAPI Swagger UI**: http://localhost:8000/docs

### CLI Commands

```bash
# Activate virtual environment
source env/bin/activate

# Ingest papers with entity extraction + classification
python cli.py ingest --query "retrieval augmented generation" --limit 10

# Canonicalize entities (merge duplicates)
python cli.py canonicalize

# Generate weekly digest
python cli.py digest --week-start 2026-01-06
```

### Frontend Pages

| Page | Route | Description |
|------|-------|-------------|
| **Home** | `/` | Overview and quick stats |
| **Ingest** | `/ingest` | Fetch and process papers from arXiv |
| **Trends** | `/trends` | Weekly trends and entity charts |
| **Entity Explorer** | `/entities` | Browse entities and their related papers |
| **Digest** | `/digest` | Generate and view weekly AI-powered digests |

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/papers/` | List all papers |
| GET | `/papers/{id}` | Get paper by ID |
| POST | `/ingest` | Ingest papers from arXiv |
| GET | `/entities/` | List entities with filtering |
| GET | `/entities/{id}/papers` | Get papers for an entity |
| GET | `/trends/week` | Weekly trend analysis |
| GET | `/trends/cooccurrence` | Entity co-occurrence |
| GET | `/digest/latest` | Get latest digest |
| POST | `/digest/generate` | Generate new digest |
| GET | `/health` | Health check |

## Project Structure

```
arxiv-trend-radar/
├── cli.py                   # CLI tool for ingestion
├── alembic.ini              # Alembic configuration
├── docker-compose.yml       # Docker services (Postgres on :5433)
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (gitignored)
├── frontend/
│   ├── index.html
│   ├── package.json         # Node dependencies (React, Vite, Tailwind, Recharts)
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── main.jsx         # React entry point
│       ├── App.jsx          # Router setup
│       ├── api/
│       │   └── client.js    # Axios client pointing at FastAPI
│       ├── components/
│       │   ├── Layout.jsx
│       │   └── Sidebar.jsx
│       └── pages/
│           ├── Home.jsx
│           ├── Ingest.jsx
│           ├── Trends.jsx
│           ├── EntityExplorer.jsx
│           └── Digest.jsx
└── backend/
    ├── app/
    │   ├── main.py              # FastAPI application entry point
    │   ├── database.py          # Database connection setup
    │   ├── models/
    │   │   └── models.py        # SQLAlchemy models
    │   ├── schemas/
    │   │   └── schemas.py       # Pydantic schemas (API + LLM structured output)
    │   ├── api/
    │   │   ├── papers_router.py
    │   │   ├── entities_router.py
    │   │   ├── trends_router.py
    │   │   └── digest_router.py
    │   ├── repositories/
    │   │   ├── paper_repo.py
    │   │   ├── entity_repo.py
    │   │   └── analytics_repo.py
    │   ├── services/
    │   │   └── ingestion_services.py
    │   └── llm/
    │       ├── entity_extraction.py
    │       ├── paper_classification.py
    │       ├── canonicalization.py
    │       └── digest_generator.py
    └── db/
        ├── env.py
        └── versions/            # Alembic migration files
```

## LLM Pipeline

The system uses **openai/gpt-5.2** via OpenRouter for 4 processing steps:

### Step A: Entity Extraction
Extracts structured entities from paper abstracts:
- **Tasks**: Research problems (e.g., "Image Classification")
- **Datasets**: Named datasets (e.g., "ImageNet", "MS MARCO")
- **Methods**: Algorithms/architectures (e.g., "Transformer", "RAG")
- **Libraries**: Tools/frameworks (e.g., "PyTorch", "LangChain")

### Step B: Paper Classification
Assigns taxonomy tags to papers:
- Retrieval/RAG
- Agents/Tool Use
- Evaluation/Benchmarks
- Alignment/Safety
- Multimodal
- Systems/Optimization

### Step C: Entity Canonicalization
Merges duplicate entities:
- "RLHF", "rlhf" → "Reinforcement Learning from Human Feedback"
- "RAG", "retrieval augmented generation" → "Retrieval-Augmented Generation"

### Step D: Weekly Digest Generation
Generates markdown reports with:
- Key Trends
- Rising Topics
- Interesting Connections
- Recommended Reading Areas

## SQL Analytics

The `analytics_repo.py` provides 6 core queries:

1. **Top Entities by Week** - Most mentioned entities
2. **Fastest Growing Entities** - Week-over-week growth
3. **Entity Co-occurrence** - What's used together
4. **Tag Distribution** - Papers by taxonomy
5. **Entity Timeline** - Mentions over time
6. **Papers by Entity** - Related papers lookup

## Development

### Create new migration
```bash
alembic revision --autogenerate -m "description"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

## License

MIT
