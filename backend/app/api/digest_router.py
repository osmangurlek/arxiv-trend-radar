from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
import os

from backend.app.database import SessionLocal
from backend.app.models.models import Digest
from backend.app.repositories import analytics_repo
from backend.app.llm.digest_generator import DigestService

router = APIRouter(prefix="/digest", tags=["Digest"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/generate")
async def generate_digest(
    week_start: date,
    db: Session = Depends(get_db)
):
    """Generate weekly digest using LLM"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    # Get analytics data
    week_start_dt = datetime.combine(week_start, datetime.min.time())
    
    top_entities = analytics_repo.get_top_entities_by_week(db, week_start_dt, "method", limit=10)
    fastest_growing = analytics_repo.get_fastest_growing_entities(db, "method")
    cooccurrence = analytics_repo.get_entity_cooccurence_edges(db, "method", days=7)
    categories = analytics_repo.category_distribution_over_time(db)
    
    # Format for LLM
    top_list = [{"name": r[0], "count": r[1]} for r in top_entities]
    growth_list = [{"name": r[0], "growth": r[1]} for r in fastest_growing]
    cooc_list = [{"entity_a": r[0], "entity_b": r[1], "count": r[2]} for r in cooccurrence[:10]]
    cat_list = [{"category": r[1], "count": r[2]} for r in categories[:10]]
    
    # Generate digest
    service = DigestService(api_key=api_key)
    content = await service.generate_digest(
        week_start=week_start,
        top_entities=top_list,
        fastest_growing=growth_list,
        cooccurrence=cooc_list,
        categories=cat_list
    )
    
    # Save to database
    week_end = week_start + timedelta(days=7)
    digest = Digest(
        week_start=week_start,
        week_end=week_end,
        content_md=content
    )
    db.add(digest)
    db.commit()
    
    return {"week_start": week_start, "content": content}

@router.get("/latest")
def get_latest_digest(db: Session = Depends(get_db)):
    """Get the most recent digest"""
    digest = db.query(Digest).order_by(Digest.created_at.desc()).first()
    if not digest:
        raise HTTPException(status_code=404, detail="No digests found")
    return {
        "week_start": digest.week_start,
        "week_end": digest.week_end,
        "content": digest.content_md
    }