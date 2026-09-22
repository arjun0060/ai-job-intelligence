from sqlalchemy.orm import Session

from app.models.embedding import Embedding
from app.services.embeddings.embedding_service import EmbeddingService


class VectorSearchService:

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def search_resume(
        self,
        db: Session,
        resume_id,
        query: str,
        limit: int = 5,
    ) -> list[dict]:

        query_embedding = self.embedding_service.embed(query)

        distance = Embedding.embedding.cosine_distance(
            query_embedding
        ).label("distance")

        results = (
            db.query(
                Embedding,
                distance,
            )
            .filter(
                Embedding.source_type == "resume",
                Embedding.source_id == str(resume_id),
            )
            .order_by(distance)
            .limit(limit)
            .all()
        )

        return [
            {
                "id": embedding.id,
                "source_id": embedding.source_id,
                "chunk_type": embedding.chunk_type,
                "content": embedding.content,
                "similarity": round(
                    1 - float(distance_value),
                    4,
                ),
            }
            for embedding, distance_value in results
        ]