from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
from enum import Enum


# ============== Enums ==============

class EntityType(str, Enum):
    dataset = "dataset"
    method = "method"
    task = "task"
    library = "library"


# ============== Paper Schemas ==============

class PaperCreate(BaseModel):
    """For creating a new paper - data from arXiv API"""
    arxiv_id: str
    title: str
    abstract: str
    authors: List[str]
    published_at: datetime
    categories: List[str]
    url: str


class Paper(PaperCreate):
    """Paper read from DB - includes id and created_at"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Entity Schemas ==============

class EntityCreate(BaseModel):
    """For creating a new entity"""
    name: str
    type: EntityType
    canonical_id: Optional[int] = None


class Entity(EntityCreate):
    """Entity read from DB"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class EntityUpdate(BaseModel):
    """For updating an entity - mainly for canonical_id (dedup/alias)"""
    name: Optional[str] = None
    type: Optional[EntityType] = None
    canonical_id: Optional[int] = None


# ============== PaperEntity Schemas ==============

class PaperEntityCreate(BaseModel):
    """For creating a Paper-Entity relationship"""
    paper_id: int
    entity_id: int
    evidence: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class PaperEntity(PaperEntityCreate):
    """Paper-entity relationship read from DB"""
    created_at: datetime

    class Config:
        from_attributes = True


# ============== PaperTag Schemas ==============

class PaperTagCreate(BaseModel):
    """For adding a tag to a paper"""
    paper_id: int
    tag: str
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class PaperTag(PaperTagCreate):
    """Paper tag read from DB"""
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Digest Schemas ==============

class DigestCreate(BaseModel):
    """For creating a weekly digest"""
    week_start: date
    week_end: date
    content_md: str


class Digest(DigestCreate):
    """Digest read from DB"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True