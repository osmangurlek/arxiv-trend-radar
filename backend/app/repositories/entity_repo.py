from sqlalchemy.orm import Session
from backend.app.models.models import Entity, PaperEntity, EntityType

class EntityRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_entities(self, name: str, entity_type: EntityType) -> Entity:
        entity = self.db.query(Entity).filter(
            Entity.name == name,
            Entity.type == entity_type
        ).first()
        
        if not entity:
            entity = Entity(name=name, type=entity_type)
            self.db.add(entity)
            self.db.flush()
        return entity

    def upsert_paper_entity(self, paper_id: int, entity_id: int, evidence: str, confidence: float) -> PaperEntity:
        existing = self.db.query(PaperEntity).filter(
            PaperEntity.paper_id == paper_id,
            PaperEntity.entity_id == entity_id
        ).first()

        if existing:
            return existing

        paper_entity = PaperEntity(
            paper_id=paper_id,
            entity_id=entity_id,
            evidence=evidence,
            confidence=confidence
        )
        self.db.add(paper_entity)
        self.db.flush()
        return paper_entity

    def get_entities_without_canonical(self):
        """Get all entities that don't have a canonical_id set"""
        return self.db.query(Entity).filter(Entity.canonical_id.is_(None)).all()

    def set_canonical_id(self, alias_id: int, canonical_id: int):
        """Set the canonical_id for an alias entity"""
        entity = self.db.query(Entity).filter(Entity.id == alias_id).first()
        if entity:
            entity.canonical_id = canonical_id
            self.db.flush()
        return entity

    def get_entity_by_name(self, name: str):
        """Get entity by name"""
        return self.db.query(Entity).filter(Entity.name == name).first()