from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.dialects.postgresql import insert
from backend.app.models.models import Paper

class PaperRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_papers(self, papers_data: List):
        """
        Inserts papers in bulk. If arxiv_id already exists, it does not 
        raise an error (idempotent) and updates the record if necessary.
        """
        for data in papers_data:
            stmt = insert(Paper).values(
                arxiv_id=data["arxiv_id"],
                title=data["title"],
                abstract=data["abstract"],
                authors=data["authors"],
                published_at=data["published_at"],
                categories=data["categories"],
                url=data["url"],
            )

            stmt = stmt.on_conflict_do_nothing(index_elements=['arxiv_id'])
            self.db.execute(stmt)

        self.db.commit()

    def upsert_paper(self, data: dict) -> Paper:
        """
        Upserts a single paper and returns the Paper object.
        Needed for entity extraction which requires paper ID.
        """
        existing = self.db.query(Paper).filter(Paper.arxiv_id == data["arxiv_id"]).first()
        
        if existing:
            return existing
        
        paper = Paper(
            arxiv_id=data["arxiv_id"],
            title=data["title"],
            abstract=data["abstract"],
            authors=data["authors"],
            published_at=data["published_at"],
            categories=data["categories"],
            url=data["url"],
        )
        self.db.add(paper)
        self.db.flush()
        return paper