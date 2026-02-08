"""
ArXiv Trend Radar - FastAPI Application
"""
import logging
import os

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal, engine
from backend.app.models import models
from backend.app.repositories.paper_repo import PaperRepository
from backend.app.repositories.entity_repo import EntityRepository
from backend.app.services.ingestion_services import IngestionService
from backend.app.llm.entity_extraction import LLMService
from backend.app.llm.paper_classification import ClassificationService
from backend.app.api import papers_router, trends_router, entities_router, digest_router

logger = logging.getLogger(__name__)

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

_cors_origins = ["http://localhost:8501", "http://127.0.0.1:8501"]
if os.environ.get("CORS_ORIGIN"):
    _cors_origins.append(os.environ.get("CORS_ORIGIN", "").rstrip("/"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        
        count, saved_papers = await service.fetch_and_save(query=query, max_results=limit)
        db.commit()
        
        return {
            "message": f"Successfully ingested {count} papers",
            "query": query,
            "papers_added": count,
            "papers": saved_papers,
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.exception("Ingest failed")
        raise HTTPException(
            status_code=500,
            detail="Ingestion failed. Check server logs for details."
        )

# ============== Health Check ==============

@app.get("/health")
def health_check():
    return {"status": "healthy"}