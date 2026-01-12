# arXiv Trend Radar

A system for tracking and analyzing trends in arXiv research papers. This project ingests papers from arXiv, extracts entities (models, datasets, methods) using LLM, stores everything in PostgreSQL, and provides trend analytics.

## Tech Stack

- **Python 3.13+**
- **FastAPI** - Web framework
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **LangChain + Gemini** - LLM entity extraction
- **Docker Compose** - Container orchestration

## Features

- ✅ **Paper Ingestion** - Fetch papers from arXiv API
- ✅ **LLM Entity Extraction** - Extract tasks, datasets, methods, libraries from abstracts
- ✅ **CLI Tool** - Command-line interface for ingestion
- ⬜ **SQL Analytics** - Trend queries (coming soon)
- ⬜ **FastAPI Endpoints** - REST API (coming soon)
- ⬜ **Streamlit UI** - Dashboard (coming soon)

## Database Schema

| Table | Description |
|-------|-------------|
| `papers` | arXiv papers with title, abstract, authors, categories |
| `entities` | Extracted entities (dataset, method, task, library) |
| `paper_entities` | Many-to-many relation between papers and entities with evidence |
| `paper_tags` | Taxonomy tags assigned to papers with confidence scores |
| `digests` | Weekly markdown digest summaries |

## Setup

### Prerequisites

- Python 3.13+
- Docker & Docker Compose
- Gemini API Key

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
   POSTGRES_URL=postgresql://YOUR_DB_USERNAME:YOUR_DB_PASSWORD@localhost:5432/YOUR_DB_NAME
   POSTGRES_USER=YOUR_DB_USERNAME
   POSTGRES_PASSWORD=YOUR_DB_PASSWORD
   POSTGRES_DB=YOUR_DB_NAME
   GEMINI_API_KEY=your_gemini_api_key_here
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

### CLI - Ingest Papers

```bash
# Activate virtual environment
source env/bin/activate

# Ingest papers with entity extraction
python cli.py ingest --query "retrieval augmented generation" --limit 10

# Generate digest (coming soon)
python cli.py digest --week-start 2026-01-01
```

### FastAPI Server

```bash
uvicorn backend.app.main:app --reload
```

The API will be available at `http://localhost:8000`

- Swagger UI: `http://localhost:8000/docs`

## Project Structure

```
arxiv-trend-radar/
├── cli.py                   # CLI tool for ingestion
├── alembic.ini              # Alembic configuration
├── docker-compose.yml       # Docker services
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (gitignored)
└── backend/
    ├── app/
    │   ├── main.py              # FastAPI application entry point
    │   ├── database.py          # Database connection setup
    │   ├── models/
    │   │   └── models.py        # SQLAlchemy models
    │   ├── schemas/
    │   │   └── schemas.py       # Pydantic schemas
    │   ├── repositories/
    │   │   ├── paper_repo.py    # Paper data access layer
    │   │   └── entity_repo.py   # Entity data access layer
    │   ├── services/
    │   │   └── ingestion_services.py  # Ingestion business logic
    │   └── llm/
    │       └── entity_extraction.py   # LLM entity extraction service
    └── db/
        ├── env.py           # Alembic environment
        └── versions/        # Migration files
```

## How Entity Extraction Works

1. **Fetch papers** from arXiv API based on search query
2. **Save papers** to PostgreSQL (idempotent, no duplicates)
3. **Extract entities** from each abstract using Gemini LLM:
   - **Tasks**: Research problems (e.g., "Image Classification")
   - **Datasets**: Named datasets (e.g., "ImageNet", "MS MARCO")
   - **Methods**: Algorithms/architectures (e.g., "Transformer", "RAG")
   - **Libraries**: Tools/frameworks (e.g., "PyTorch", "LangChain")
4. **Store entities** with evidence quotes and confidence scores

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