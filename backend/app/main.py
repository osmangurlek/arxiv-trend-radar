"""
ArXiv Trend Radar - FastAPI Application
"""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal, engine
from backend.app.models import models
from backend.app.repositories.paper_repo import PaperRepository
from backend.app.services.ingestion_services import IngestionService
from backend.app.api import papers_router, trends_router, entities_router


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

app.include_router(papers_router.router)
app.include_router(trends_router.router)
app.include_router(entities_router.router)


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

# ============== Health Check ==============

@app.get("/health")
def health_check():
    return {"status": "healthy"}