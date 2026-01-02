from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text, ARRAY, Integer, UniqueConstraint, Index
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Paper(Base):
    __tablename__ = "papers"
    
    id = Column(Integer, primary_key=True)
    arxiv_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text)
    authors = Column(ARRAY(String))
    published_at = Column(DateTime, index=True)
    categories = Column(ARRAY(String))
    url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Entity(Base):
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, index=True)
    canonical_id = Column(Integer, ForeignKey("entities.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PaperEntity(Base):
    __tablename__ = "paper_entities"
    
    paper_id = Column(Integer, ForeignKey("papers.id"), primary_key=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    evidence = Column(Text)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('paper_id', 'entity_id', name='uq_paper_entity'),
        Index('ix_paper_entities_paper_id', 'paper_id'),
        Index('ix_paper_entities_entity_id', 'entity_id'),
    )

class PaperTag(Base):
    __tablename__ = "paper_tags"
    
    paper_id = Column(Integer, ForeignKey("papers.id"), primary_key=True)
    tag = Column(String, primary_key=True)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('paper_id', 'tag', name='uq_paper_tag'),
    )

class Digest(Base):
    __tablename__ = "digests"
    
    id = Column(Integer, primary_key=True)
    week_start = Column(DateTime, nullable=False)
    week_end = Column(DateTime, nullable=False)
    content_md = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)