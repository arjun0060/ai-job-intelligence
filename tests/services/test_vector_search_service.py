from unittest.mock import MagicMock

from app.services.embeddings.vector_search_service import (
    VectorSearchService,
)


def test_search_resume_generates_query_embedding():
    service = VectorSearchService()

    service.embedding_service.embed = MagicMock(
        return_value=[0.1] * 384
    )

    db = MagicMock()

    query = db.query.return_value
    query.filter.return_value = query
    query.order_by.return_value = query
    query.limit.return_value = query
    query.all.return_value = []

    service.search_resume(
        db=db,
        resume_id="resume-123",
        query="Python backend developer",
    )

    service.embedding_service.embed.assert_called_once_with(
        "Python backend developer"
    )


def test_search_resume_returns_similarity():
    service = VectorSearchService()

    service.embedding_service.embed = MagicMock(
        return_value=[0.1] * 384
    )

    db = MagicMock()

    embedding = MagicMock()
    embedding.id = 10
    embedding.source_id = "resume-123"
    embedding.chunk_type = "resume_skill"
    embedding.content = "Python FastAPI PostgreSQL"

    query = db.query.return_value
    query.filter.return_value = query
    query.order_by.return_value = query
    query.limit.return_value = query
    query.all.return_value = [
        (embedding, 0.2),
    ]

    result = service.search_resume(
        db=db,
        resume_id="resume-123",
        query="Python backend",
    )

    assert len(result) == 1
    assert result[0]["id"] == 10
    assert result[0]["source_id"] == "resume-123"
    assert result[0]["chunk_type"] == "resume_skill"
    assert result[0]["content"] == "Python FastAPI PostgreSQL"
    assert result[0]["similarity"] == 0.8


def test_search_resume_rounds_similarity():
    service = VectorSearchService()

    service.embedding_service.embed = MagicMock(
        return_value=[0.1] * 384
    )

    db = MagicMock()

    embedding = MagicMock()
    embedding.id = 20
    embedding.source_id = "resume-456"
    embedding.chunk_type = "resume_experience"
    embedding.content = "Backend Developer"

    query = db.query.return_value
    query.filter.return_value = query
    query.order_by.return_value = query
    query.limit.return_value = query
    query.all.return_value = [
        (embedding, 0.123456),
    ]

    result = service.search_resume(
        db=db,
        resume_id="resume-456",
        query="backend development",
    )

    assert result[0]["similarity"] == 0.8765


def test_search_resume_returns_empty_list_when_no_results():
    service = VectorSearchService()

    service.embedding_service.embed = MagicMock(
        return_value=[0.1] * 384
    )

    db = MagicMock()

    query = db.query.return_value
    query.filter.return_value = query
    query.order_by.return_value = query
    query.limit.return_value = query
    query.all.return_value = []

    result = service.search_resume(
        db=db,
        resume_id="resume-123",
        query="Kubernetes",
    )

    assert result == []


def test_search_resume_applies_limit():
    service = VectorSearchService()

    service.embedding_service.embed = MagicMock(
        return_value=[0.1] * 384
    )

    db = MagicMock()

    query = db.query.return_value
    query.filter.return_value = query
    query.order_by.return_value = query
    query.limit.return_value = query
    query.all.return_value = []

    service.search_resume(
        db=db,
        resume_id="resume-123",
        query="Python",
        limit=3,
    )

    query.limit.assert_called_once_with(3)