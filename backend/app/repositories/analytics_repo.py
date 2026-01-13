from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, desc
from datetime import datetime, timedelta, timezone
from backend.app.models import models

def get_top_entities_by_week(db: Session, week_start: datetime, entity_type: str, limit: int = 10):
    week_end = week_start + timedelta(days=7)

    return db.query(
        models.Entity.name,
        func.count(models.PaperEntity.paper_id).label("count")
    ).join(
        models.PaperEntity, models.Entity.id == models.PaperEntity.entity_id
    ).join(
        models.Paper, models.PaperEntity.paper_id == models.Paper.id
    ).filter(
        models.Paper.published_at >= week_start,
        models.Paper.published_at < week_end,
        models.Entity.type == entity_type
    ).group_by(
        models.Entity.name
    ).order_by(
        desc("count")
    ).limit(limit).all()

def get_fastest_growing_entities(db: Session, entity_type: str):
    this_week_start = datetime.utcnow() - timedelta(days=7)
    last_week_start = datetime.utcnow() - timedelta(days=14)

    current_counts = db.query(
        models.PaperEntity.entity_id,
        func.count(models.PaperEntity.paper_id).label("curr_count")
    ).join(
        models.Paper
    ).filter(
        models.Paper.published_at >= this_week_start
    ).group_by(
        models.PaperEntity.entity_id
    ).subquery()

    prev_counts = db.query(
        models.PaperEntity.entity_id,
        func.count(models.PaperEntity.paper_id).label("prev_count")
    ).join(
        models.Paper
    ).filter(
        models.Paper.published_at >= last_week_start,
        models.Paper.published_at < this_week_start
    ).group_by(
        models.PaperEntity.entity_id
    ).subquery()

    return db.query(
        models.Entity.name,
        (current_counts.c.curr_count - func.coalesce(prev_counts.c.prev_count, 0)).label("growth")
    ).join(
        current_counts, models.Entity.id == current_counts.c.entity_id
    ).outerjoin(
        prev_counts, models.Entity.id == prev_counts.c.entity_id
    ).filter(
        models.Entity.type == entity_type
    ).order_by(
        desc("growth")
    ).limit(
        10
    ).all()

def get_entity_cooccurence_edges(db: Session, entity_type: str, days: int = 30):
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    pe1 = aliased(models.PaperEntity, name='pe1')
    pe2 = aliased(models.PaperEntity, name='pe2')
    ent1 = aliased(models.Entity, name='ent1')
    ent2 = aliased(models.Entity, name='ent2')
    
    return db.query(
        ent1.name.label("entity_a"),
        ent2.name.label("entity_b"),
        func.count(pe1.paper_id).label("cooccurrence_count")
    ).select_from(pe1).join(
        ent1, ent1.id == pe1.entity_id
    ).join(
        pe2, pe1.paper_id == pe2.paper_id
    ).join(
        ent2, pe2.entity_id == ent2.id
    ).join(
        models.Paper, pe1.paper_id == models.Paper.id
    ).filter(
        models.Paper.published_at >= start_date,
        ent1.type == entity_type,
        ent2.type == entity_type,
        ent1.id < ent2.id
    ).group_by(
        ent1.name,
        ent2.name
    ).order_by(
        desc("cooccurrence_count")
    ).all()

def get_papers_for_an_entity(db: Session, entity_id: int):
    return db.query(
        models.Paper.id,
        models.Paper.title,
        models.Paper.authors,
        models.Paper.published_at,
        models.PaperEntity.evidence,
        models.PaperEntity.confidence
    ).join(
        models.PaperEntity, models.Paper.id == models.PaperEntity.paper_id
    ).filter(
        models.PaperEntity.entity_id == entity_id
    ).order_by(
        desc(models.Paper.published_at)
    ).all()

def category_distribution_over_time(db: Session):
    category_label = func.unnest(models.Paper.categories).column_valued("category")
    week_trunc = func.date_trunc("week", models.Paper.published_at)

    return db.query(
        week_trunc.label("week"),
        category_label.label("category"),
        func.count(models.Paper.id).label("count")
    ).group_by(
        "week",
        "category"
    ).order_by(
        desc("week"),
        desc("count")
    ).all()

def get_canonical_merges_report(db: Session):
    alias_ent = aliased(models.Entity, name='alias_ent')
    canon_ent = aliased(models.Entity, name='canon_ent')

    return db.query(
        canon_ent.name.label("canonical_name"),
        func.array_agg(alias_ent.name).label("aliases")
    ).select_from(
        alias_ent
    ).join(
        canon_ent, alias_ent.canonical_id == canon_ent.id
    ).group_by(
        canon_ent.name
    ).all()