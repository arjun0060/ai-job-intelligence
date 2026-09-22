from sqlalchemy.orm import Session

from app.services.embeddings.vector_search_service import (
    VectorSearchService,
)


class EvidenceRetrievalService:

    def __init__(self):
        self.vector_search = VectorSearchService()

    def retrieve(
        self,
        db: Session,
        resume_id,
        requirement: str,
        limit: int = 3,
        min_similarity: float = 0.30,
    ) -> list[dict]:

        if not requirement or not requirement.strip():
            return []

        results = self.vector_search.search_resume(
            db=db,
            resume_id=resume_id,
            query=requirement,
            limit=limit,
        )

        return [
            result
            for result in results
            if result["similarity"] >= min_similarity
        ]