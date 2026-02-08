import arxiv
from datetime import datetime
from backend.app.repositories.paper_repo import PaperRepository
from backend.app.repositories.entity_repo import EntityRepository
from backend.app.llm.entity_extraction import LLMService
from backend.app.llm.paper_classification import ClassificationService
from backend.app.models.models import EntityType
from backend.app.schemas.schemas import PaperExtractionSchema

class IngestionService:
    def __init__(self, paper_repo: PaperRepository, entity_repo: EntityRepository, llm_service: LLMService, classification_service: ClassificationService):
        self.paper_repo = paper_repo
        self.entity_repo = entity_repo
        self.llm_service = llm_service
        self.classification_service = classification_service

    async def fetch_and_save(self, query: str, max_results: int = 10):
        """
        Fetches papers from arXiv, saves them to DB, extracts entities via LLM,
        and saves entity relationships. Returns (count, list of saved papers with title, published_at, arxiv_id).
        Papers are sorted newest first (by published_at desc).
        """
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        results = list(client.results(search))
        # En yeniden en eskiye: published_at azalan sıra
        results.sort(key=lambda r: r.published or datetime.min, reverse=True)

        saved_papers = []

        for result in results:
            paper_data = {
                "arxiv_id": result.entry_id,
                "title": result.title,
                "abstract": result.summary,
                "authors": [a.name for a in result.authors],
                "published_at": result.published,
                "categories": result.categories,
                "url": result.links[0].href
            }

            # 1. Save paper and get the object (for ID)
            paper = self.paper_repo.upsert_paper(paper_data)
            saved_papers.append({
                "title": paper_data["title"],
                "published_at": paper_data["published_at"].isoformat() if hasattr(paper_data["published_at"], "isoformat") else str(paper_data["published_at"]),
                "arxiv_id": paper_data["arxiv_id"],
            })

            # 2. Perform entity extraction with LLM (with error handling)
            try:
                extraction = await self.llm_service.extract_entities(paper_data["abstract"])
                # 3. Save extracted entities to DB
                self._save_extracted_entities(paper.id, extraction)
            except Exception as e:
                print(f"⚠️  Entity extraction failed for paper {paper.id}: {e}")
                # Continue with next paper even if extraction fails

            # 4. Classify Paper
            try:
                classification = await self.classification_service.classify_paper(paper_data["abstract"])
                for tag_item in classification.tags:
                    self.paper_repo.add_paper_tag(paper.id, tag_item.tag, tag_item.confidence)
            except Exception as e:
                print(f"⚠️  Classification failed for paper {paper.id}: {e}")

        return len(results), saved_papers

    def _save_extracted_entities(self, paper_id: int, extraction: PaperExtractionSchema):
        """
        Saves entities from LLM into entities and paper_entities tables.
        """
        # Tasks
        for item in extraction.tasks:
            entity = self.entity_repo.upsert_entities(item.name, EntityType.task)
            self.entity_repo.upsert_paper_entity(paper_id, entity.id, item.evidence, item.confidence)
        
        # Datasets
        for item in extraction.datasets:
            entity = self.entity_repo.upsert_entities(item.name, EntityType.dataset)
            self.entity_repo.upsert_paper_entity(paper_id, entity.id, item.evidence, item.confidence)
        
        # Methods
        for item in extraction.methods:
            entity = self.entity_repo.upsert_entities(item.name, EntityType.method)
            self.entity_repo.upsert_paper_entity(paper_id, entity.id, item.evidence, item.confidence)
        
        # Libraries
        for item in extraction.libraries:
            entity = self.entity_repo.upsert_entities(item.name, EntityType.library)
            self.entity_repo.upsert_paper_entity(paper_id, entity.id, item.evidence, item.confidence)