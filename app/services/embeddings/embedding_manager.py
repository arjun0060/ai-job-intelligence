from sqlalchemy.orm import Session

from app.services.embeddings.embedding_repository import (
    EmbeddingRepository,
)
from app.services.embeddings.embedding_service import (
    EmbeddingService,
)
from app.services.embeddings.text_chunker import TextChunker


class EmbeddingManager:

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def create_embedding(
        self,
        db: Session,
        source_type: str,
        source_id: str,
        chunk_type: str,
        content: str,
    ):

        embedding = self.embedding_service.embed(
            content
        )

        return EmbeddingRepository.create(
            db=db,
            source_type=source_type,
            source_id=source_id,
            chunk_type=chunk_type,
            content=content,
            embedding=embedding,
        )

    def create_resume_embeddings(
        self,
        db: Session,
        resume_id,
        resume_data: dict,
    ):

        source_id = str(resume_id)

        EmbeddingRepository.delete_by_source(
            db=db,
            source_type="resume",
            source_id=source_id,
        )

        chunks = TextChunker.chunk_resume(
            resume_data
        )

        records = []

        for chunk in chunks:

            embedding = self.embedding_service.embed(
                chunk["content"]
            )

            records.append(
                {
                    "source_type": "resume",
                    "source_id": source_id,
                    "chunk_type": chunk["chunk_type"],
                    "content": chunk["content"],
                    "embedding": embedding,
                }
            )

        return EmbeddingRepository.create_many(
            db=db,
            records=records,
        )

    def create_job_embeddings(
        self,
        db: Session,
        job_id: int,
        job_data: dict,
    ):

        source_id = str(job_id)

        EmbeddingRepository.delete_by_source(
            db=db,
            source_type="job",
            source_id=source_id,
        )

        chunks = TextChunker.chunk_job(
            job_data
        )

        records = []

        for chunk in chunks:

            embedding = self.embedding_service.embed(
                chunk["content"]
            )

            records.append(
                {
                    "source_type": "job",
                    "source_id": source_id,
                    "chunk_type": chunk["chunk_type"],
                    "content": chunk["content"],
                    "embedding": embedding,
                }
            )

        return EmbeddingRepository.create_many(
            db=db,
            records=records,
        )