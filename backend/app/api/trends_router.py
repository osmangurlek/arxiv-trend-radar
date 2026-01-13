from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.app.database import SessionLocal
from backend.app.repositories import analytics_repo

router = APIRouter(prefix="/trends", tags=["Trends"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/week")
def get_weekly_trends(
    week_start: datetime,
    entity_type: str,
    db: Session = Depends(get_db)
):
    """Get weekly trend analytics"""
    top = analytics_repo.get_top_entities_by_week(db, week_start, entity_type)
    growing = analytics_repo.get_fastest_growing_entities(db, entity_type)

    return {
        "top_entities": [{"name": r[0], "count": r[1]} for r in top],
        "fastest_growing": [{"name": r[0], "growth": r[1]} for r in growing]
    }

@router.get("/cooccurrence")
def get_cooccurrence(
    entity_type: str = "method",
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get entity co-occurrence edges"""
    results = analytics_repo.get_entity_cooccurence_edges(db, entity_type, days)
    return [
        {
            "entity_a": r[0], 
            "entity_b": r[1], 
            "cooccurrence_count": r[2]
        } 
        for r in results
    ]