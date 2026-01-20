"""
ArXiv Trend Radar - FastAPI Application
"""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import asyncio

from backend.app.database import SessionLocal, engine
from backend.app.models import models
from backend.app.repositories.paper_repo import PaperRepository
from backend.app.repositories.entity_repo import EntityRepository
from backend.app.services.ingestion_services import IngestionService
from backend.app.llm.entity_extraction import LLMService
from backend.app.llm.paper_classification import ClassificationService
from backend.app.api import papers_router, trends_router, entities_router, digest_router


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
app.include_router(digest_router.router)

# ============== Ingest Endpoint ==============

@app.post("/ingest")
async def ingest_papers(
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
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
        
        # Initialize all services
        paper_repo = PaperRepository(db)
        entity_repo = EntityRepository(db)
        llm_service = LLMService(api_key=api_key)
        classification_service = ClassificationService(api_key=api_key)
        
        service = IngestionService(
            paper_repo=paper_repo,
            entity_repo=entity_repo,
            llm_service=llm_service,
            classification_service=classification_service
        )
        
        count = await service.fetch_and_save(query=query, max_results=limit)
        db.commit()
        
        return {
            "message": f"Successfully ingested {count} papers",
            "query": query,
            "papers_added": count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ============== Health Check ==============

@app.get("/health")
def health_check():
    return {"status": "healthy"}