from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.app.database import SessionLocal
from backend.app.models.models import Paper
from backend.app.schemas.schemas import Paper as PaperSchema

router = APIRouter(prefix="/papers", tags=["Papers"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[PaperSchema])
def get_papers(
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get papers with optional filtering"""
    query = db.query(Paper)

    if category:
        query = query.filter(Paper.categories.contains([category]))
    
    return query.offset(skip).limit(limit).all()

@router.get("/{paper_id}", response_model=PaperSchema)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    """Get single paper by ID"""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper