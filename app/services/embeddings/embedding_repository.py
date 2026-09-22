from sqlalchemy.orm import Session

from app.models.embedding import Embedding


class EmbeddingRepository:

    @staticmethod
    def create(
        db: Session,
        source_type: str,
        source_id: str,
        chunk_type: str,
        content: str,
        embedding: list[float],
    ) -> Embedding:

        record = Embedding(
            source_type=source_type,
            source_id=source_id,
            chunk_type=chunk_type,
            content=content,
            embedding=embedding,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    @staticmethod
    def create_many(
        db: Session,
        records: list[dict],
    ) -> list[Embedding]:

        if not records:
            return []

        embeddings = [
            Embedding(
                source_type=record["source_type"],
                source_id=record["source_id"],
                chunk_type=record["chunk_type"],
                content=record["content"],
                embedding=record["embedding"],
            )
            for record in records
        ]

        db.add_all(embeddings)
        db.commit()

        for embedding in embeddings:
            db.refresh(embedding)

        return embeddings

    @staticmethod
    def delete_by_source(
        db: Session,
        source_type: str,
        source_id: str,
    ) -> None:

        db.query(Embedding).filter(
            Embedding.source_type == source_type,
            Embedding.source_id == source_id,
        ).delete(
            synchronize_session=False
        )

        db.commit()