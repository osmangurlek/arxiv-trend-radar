# arXiv Trend Radar

A system for tracking and analyzing trends in arXiv research papers. This project ingests papers from arXiv, extracts entities (models, datasets, methods), tags papers, and generates weekly digest summaries.

## Tech Stack

- **Python 3.13+**
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Docker Compose** - Container orchestration

## Database Schema

| Table | Description |
|-------|-------------|
| `papers` | arXiv papers with title, summary, authors, categories |
| `entities` | Extracted entities (models, datasets, methods) |
| `paper_entities` | Many-to-many relation between papers and entities |
| `paper_tags` | Tags assigned to papers with confidence scores |
| `digests` | Weekly markdown digest summaries |

## Setup

### Prerequisites

- Python 3.13+
- Docker & Docker Compose
- PostgreSQL (via Docker)

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
   echo 'POSTGRES_URL=postgresql://USERNAME:PASSWORD@localhost:5432/DB_NAME
   POSTGRES_USER=USERNAME
   POSTGRES_PASSWORD=PASSWORD
   POSTGRES_DB=DB_NAME' > .env
   ```

5. **Start PostgreSQL**
   ```bash
   docker compose up -d
   ```

6. **Run migrations**
   ```bash
   alembic revision --autogenerate -m "description"
   alembic upgrade head
   ```

## Project Structure

```
arxiv-trend-radar/
├── alembic.ini              # Alembic configuration
├── docker-compose.yml       # Docker services
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (gitignored)
└── backend/
    ├── app/
    │   ├── models.py        # SQLAlchemy models
    │   └── ingest.py        # arXiv paper ingestion
    └── db/
        ├── env.py           # Alembic environment
        └── versions/        # Migration files
```

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