import arxiv
from backend.app.repositories.paper_repo import PaperRepository
from backend.app.repositories.entity_repo import EntityRepository
from backend.app.llm.entity_extraction import LLMService
from backend.app.models.models import EntityType
from backend.app.schemas.schemas import PaperExtractionSchema

class IngestionService:
    def __init__(self, paper_repo: PaperRepository, entity_repo: EntityRepository, llm_service: LLMService):
        self.paper_repo = paper_repo
        self.entity_repo = entity_repo
        self.llm_service = llm_service

    async def fetch_and_save(self, query: str, max_results: int = 10):
        """
        Fetches papers from arXiv, saves them to DB, extracts entities via LLM,
        and saves entity relationships.
        """
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        results = list(client.results(search))

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
            
            # 2. Perform entity extraction with LLM
            extraction = await self.llm_service.extract_entities(paper_data["abstract"])
            
            # 3. Save extracted entities to DB
            self._save_extracted_entities(paper.id, extraction)

        return len(results)

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