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

# ============== Analytics Response Schemas ==============

class TopEntityResponse(BaseModel):
    name: str
    count: int

class GrowthEntityResponse(BaseModel):
    name: str
    growth: int

class CooccurrenceResponse(BaseModel):
    entity_a: str
    entity_b: str
    cooccurrence_count: int

class PaperWithEvidenceResponse(BaseModel):
    id: int
    title: str
    authors: List[str]
    published_at: datetime
    evidence: Optional[str]
    confidence: Optional[float]

class WeeklyTrendsResponse(BaseModel):
    top_entities: List[TopEntityResponse]
    fastest_growing: List[GrowthEntityResponse]

class CategoryDistributionResponse(BaseModel):
    week: datetime
    category: str
    count: int

class CanonicalMergeResponse(BaseModel):
    canonical_name: str
    aliases: List[str]


# ============== Step-A: LLM Extraction Schemas ==============
class ExtractedEntity(BaseModel):
    name: str = Field(description="Entities technical name")
    evidence: str = Field(description="Evidence from the paper")
    confidence: float = Field(description="Confidence score", ge=0.0, le=1.0)

class PaperExtractionSchema(BaseModel):
    tasks: List[ExtractedEntity] = Field(description="Tasks or problems solved in the paper (e.g., Image Classification)")
    datasets: List[ExtractedEntity] = Field(description="Datasets used in the paper (e.g., ImageNet)")
    methods: List[ExtractedEntity] = Field(description="Methods or architectures used (e.g., CNN, Adam Optimizer)")
    libraries: List[ExtractedEntity] = Field(description="Libraries or tools used (e.g., LangChain, TensorFlow)")

# ============== LLM Step B: Paper Classification ==============
class PaperClassificationTag(BaseModel):
    tag: str = Field(description="Taxonomy tag for the paper")
    confidence: float = Field(description="Confidence score", ge=0.0, le=1.0)

class PaperClassificationSchema(BaseModel):
    tags: List[PaperClassificationTag] = Field(description="List of taxonomy tags for the paper")

# ============== LLM Step C: Entity Canonicalization ==============
class CanonicalGroup(BaseModel):
    canonical: str = Field(description="The canonical (main) name for this entity")
    aliases: List[str] = Field(description="List of alternative names for this entity")

class CanonicalizationSchema(BaseModel):
    groups: List[CanonicalGroup] = Field(description="List of canonical entity groups")