import arxiv
from backend.app.repositories.paper_repo import PaperRepository

class IngestionService:
    def __init__(self, repo: PaperRepository):
        self.repo = repo

    def fetch_and_save(self, query: str, max_results: int = 10):
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        results = list(client.results(search))

        formatted_results = []
        for result in results:
            formatted_results.append({
                "arxiv_id": result.entry_id,
                "title": result.title,
                "abstract": result.summary,
                "authors": [a.name for a in result.authors],
                "published_at": result.published,
                "categories": result.categories,
                "url": result.links[0].href
            })

        self.repo.upsert_papers(formatted_results)
        return len(formatted_results)