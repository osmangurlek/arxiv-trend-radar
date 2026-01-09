"""
ArXiv Trend Radar - FastAPI Application
"""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from backend.app.database import SessionLocal, engine
from backend.app.models import models
from backend.app.repositories.paper_repo import PaperRepository
from backend.app.services.ingestion_services import IngestionService
from backend.app.schemas.schemas import PaperCreate, Paper


# Create tables on startup
models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(
    title="ArXiv Trend Radar",
    description="Research intelligence product for arXiv papers",
    version="0.1.0"
)


# ============== Ingest Endpoint ==============

@app.post("/ingest")
def ingest_papers(
    query: str,
    days: int = 7,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Fetch papers from arXiv API and store them in database.
    
    - **query**: Search query (e.g., "retrieval augmented generation")
    - **days**: Number of days to look back (not yet implemented in arXiv search)
    - **limit**: Maximum number of papers to fetch
    """
    try:
        repo = PaperRepository(db)
        service = IngestionService(repo)
        count = service.fetch_and_save(query=query, max_results=limit)
        
        return {
            "message": f"Successfully ingested {count} papers",
            "query": query,
            "papers_added": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Papers Endpoints ==============

@app.get("/papers", response_model=list[Paper])
def get_papers(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all papers with pagination"""
    papers = db.query(models.Paper).offset(skip).limit(limit).all()
    return papers


@app.get("/papers/{paper_id}", response_model=Paper)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    """Get a single paper by ID"""
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


# ============== Health Check ==============

@app.get("/health")
def health_check():
    return {"status": "healthy"}