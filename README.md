# arXiv Trend Radar

A system for tracking and analyzing trends in arXiv research papers. This project ingests papers from arXiv, extracts entities (models, datasets, methods) using LLM, stores everything in PostgreSQL, and provides trend analytics.

## Tech Stack

- **Python 3.13+**
- **FastAPI** - Backend API
- **Streamlit** - Frontend dashboard
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **LangChain + OpenAI** - LLM services (via OpenRouter)
- **Docker Compose** - Container orchestration

## Features

- ✅ **Paper Ingestion** - Fetch papers from arXiv API
- ✅ **LLM Entity Extraction** - Extract tasks, datasets, methods, libraries from abstracts
- ✅ **Paper Classification** - Taxonomy tagging (RAG, Agents, Multimodal, etc.)
- ✅ **Entity Canonicalization** - Merge duplicate entities (e.g., RLHF → Reinforcement Learning from Human Feedback)
- ✅ **Weekly Digest Generation** - LLM-generated markdown reports
- ✅ **CLI Tool** - Command-line interface for ingestion and operations
- ✅ **SQL Analytics** - Trend queries (top entities, growth, co-occurrence)
- ✅ **FastAPI Endpoints** - REST API for papers, entities, trends, and digest
- ✅ **Streamlit Dashboard** - Interactive web UI for exploring trends

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
- Docker & Docker Compose
- OpenRouter API Key (get one at https://openrouter.ai)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/osmangurlek/arxiv-trend-radar.git
   cd arxiv-trend-radar
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file**
   ```bash
   cat > .env << EOF
   POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/arxiv_radar
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=arxiv_radar
   OPENAI_API_KEY=your_openrouter_api_key_here
   EOF
   ```

5. **Start PostgreSQL**
   ```bash
   docker compose up -d
   ```

6. **Run migrations**
   ```bash
   alembic upgrade head
   ```

## Usage

### Running the Application

Start both backend and frontend:

```bash
# Terminal 1: Start FastAPI backend
source env/bin/activate
uvicorn backend.app.main:app --reload --port 8000

# Terminal 2: Start Streamlit frontend
source env/bin/activate
streamlit run frontend/streamlit_app.py --server.port 8501
```

Access the applications:
- **Streamlit Dashboard**: http://localhost:8501
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

### Streamlit Pages

| Page | Description |
|------|-------------|
| 📥 **Ingest** | Fetch and process papers from arXiv |
| 📈 **Trends** | View weekly trends and entity co-occurrence graphs |
| 🔍 **Entity Explorer** | Browse entities and their related papers |
| 📝 **Digest** | Generate and view weekly AI-powered digests |

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
├── docker-compose.yml       # Docker services
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (gitignored)
├── frontend/
│   ├── streamlit_app.py     # Streamlit main app
│   └── pages/
│       ├── 1_📥_Ingest.py       # Paper ingestion page
│       ├── 2_📈_Trends.py       # Trends visualization
│       ├── 3_🔍_Entity_Explorer.py  # Entity browser
│       └── 4_📝_Digest.py       # Weekly digest page
└── backend/
    ├── app/
    │   ├── main.py              # FastAPI application entry point
    │   ├── database.py          # Database connection setup
    │   ├── models/
    │   │   └── models.py        # SQLAlchemy models
    │   ├── schemas/
    │   │   └── schemas.py       # Pydantic schemas
    │   ├── api/
    │   │   ├── papers_router.py    # Papers endpoints
    │   │   ├── entities_router.py  # Entities endpoints
    │   │   ├── trends_router.py    # Trends analytics endpoints
    │   │   └── digest_router.py    # Digest endpoints
    │   ├── repositories/
    │   │   ├── paper_repo.py       # Paper data access layer
    │   │   ├── entity_repo.py      # Entity data access layer
    │   │   └── analytics_repo.py   # SQL analytics queries
    │   ├── services/
    │   │   └── ingestion_services.py  # Ingestion business logic
    │   └── llm/
    │       ├── entity_extraction.py     # LLM entity extraction
    │       ├── paper_classification.py  # Paper taxonomy tagging
    │       ├── canonicalization.py      # Entity deduplication
    │       └── digest_generator.py      # Weekly digest generation
    └── db/
        ├── env.py           # Alembic environment
        └── versions/        # Migration files
```

## LLM Pipeline

The system uses **OpenAI GPT-5.2** (via OpenRouter) for 4 processing steps:

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
- 🔥 Key Trends
- 📈 Rising Topics
- 🔗 Interesting Connections
- 📚 Recommended Reading Areas

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
