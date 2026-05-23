import asyncio
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
        client = arxiv.Client(num_retries=5, delay_seconds=5.0)
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        results = list(client.results(search))
        # En yeniden en eskiye: published_at azalan sıra
        results.sort(key=lambda r: r.published or datetime.min, reverse=True)

        # Phase 1: Save all papers to DB first (sync, no LLM yet)
        papers_data = []
        paper_objects = []
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
            paper = self.paper_repo.upsert_paper(paper_data)
            papers_data.append(paper_data)
            paper_objects.append(paper)

        saved_papers = [
            {
                "title": pd["title"],
                "published_at": pd["published_at"].isoformat() if hasattr(pd["published_at"], "isoformat") else str(pd["published_at"]),
                "arxiv_id": pd["arxiv_id"],
            }
            for pd in papers_data
        ]

        # Phase 2: Run all LLM calls in parallel across papers
        async def _llm_for_paper(paper_data, paper):
            llm_results = await asyncio.gather(
                self.llm_service.extract_entities(paper_data["abstract"]),
                self.classification_service.classify_paper(paper_data["abstract"]),
                return_exceptions=True
            )
            extraction = llm_results[0] if not isinstance(llm_results[0], Exception) else None
            classification = llm_results[1] if not isinstance(llm_results[1], Exception) else None
            if isinstance(llm_results[0], Exception):
                print(f"⚠️  Entity extraction failed for paper {paper.id}: {llm_results[0]}")
            if isinstance(llm_results[1], Exception):
                print(f"⚠️  Classification failed for paper {paper.id}: {llm_results[1]}")
            return paper, extraction, classification

        llm_results = await asyncio.gather(
            *[_llm_for_paper(pd, po) for pd, po in zip(papers_data, paper_objects)],
            return_exceptions=True
        )

        # Phase 3: Save all LLM results to DB (sync, no concurrent session access)
        for res in llm_results:
            if isinstance(res, Exception):
                print(f"⚠️  Unexpected LLM error: {res}")
                continue
            paper, extraction, classification = res
            if extraction:
                try:
                    self._save_extracted_entities(paper.id, extraction)
                except Exception as e:
                    print(f"⚠️  Entity save failed for paper {paper.id}: {e}")
            if classification:
                try:
                    for tag_item in classification.tags:
                        self.paper_repo.add_paper_tag(paper.id, tag_item.tag, tag_item.confidence)
                except Exception as e:
                    print(f"⚠️  Tag save failed for paper {paper.id}: {e}")

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