from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import SessionLocal

from backend.app.models.models import Entity
from backend.app.schemas.schemas import Entity as EntitySchema, PaperWithEvidenceResponse
from backend.app.repositories import analytics_repo

router = APIRouter(prefix="/entities", tags=["Entities"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[EntitySchema])
def get_entities(
    entity_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get entites with optional filtering"""
    query = db.query(Entity)

    if entity_type:
        query = query.filter(Entity.type == entity_type)
    if search:
        query = query.filter(Entity.name.ilike(f"%{search}%"))

    return query.all()

@router.get("/{entity_id}/papers", response_model=List[PaperWithEvidenceResponse])
def get_papers_for_entity(
    entity_id: int,
    db: Session = Depends(get_db)
):
    """Get papers related to an entity"""
    results = analytics_repo.get_papers_for_an_entity(db, entity_id)
    return [
        {
            "id": r[0],
            "title": r[1],
            "authors": r[2],
            "published_at": r[3],
            "evidence": r[4],
            "confidence": r[5]
        }
        for r in results
    ]