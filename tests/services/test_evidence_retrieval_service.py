from unittest.mock import MagicMock

from app.services.embeddings.evidence_retrieval_service import (
    EvidenceRetrievalService,
)


def test_retrieve_returns_matching_evidence():
    service = EvidenceRetrievalService()

    service.vector_search.search_resume = MagicMock(
        return_value=[
            {
                "id": 1,
                "source_id": "resume-123",
                "chunk_type": "resume_skill",
                "content": "Python FastAPI",
                "similarity": 0.82,
            },
            {
                "id": 2,
                "source_id": "resume-123",
                "chunk_type": "resume_experience",
                "content": "Built REST APIs using Python",
                "similarity": 0.71,
            },
        ]
    )

    db = MagicMock()

    result = service.retrieve(
        db=db,
        resume_id="resume-123",
        requirement="Python backend development",
    )

    assert len(result) == 2
    assert result[0]["similarity"] == 0.82
    assert result[1]["similarity"] == 0.71

    service.vector_search.search_resume.assert_called_once_with(
        db=db,
        resume_id="resume-123",
        query="Python backend development",
        limit=3,
    )


def test_retrieve_filters_low_similarity_results():
    service = EvidenceRetrievalService()

    service.vector_search.search_resume = MagicMock(
        return_value=[
            {
                "id": 1,
                "source_id": "resume-123",
                "chunk_type": "resume_skill",
                "content": "Python",
                "similarity": 0.82,
            },
            {
                "id": 2,
                "source_id": "resume-123",
                "chunk_type": "resume_summary",
                "content": "Computer Science graduate",
                "similarity": 0.25,
            },
        ]
    )

    db = MagicMock()

    result = service.retrieve(
        db=db,
        resume_id="resume-123",
        requirement="Python",
        min_similarity=0.30,
    )

    assert len(result) == 1
    assert result[0]["similarity"] == 0.82


def test_retrieve_uses_custom_similarity_threshold():
    service = EvidenceRetrievalService()

    service.vector_search.search_resume = MagicMock(
        return_value=[
            {
                "id": 1,
                "source_id": "resume-123",
                "chunk_type": "resume_skill",
                "content": "Python",
                "similarity": 0.65,
            },
        ]
    )

    db = MagicMock()

    result = service.retrieve(
        db=db,
        resume_id="resume-123",
        requirement="Python",
        min_similarity=0.70,
    )

    assert result == []


def test_retrieve_uses_custom_limit():
    service = EvidenceRetrievalService()

    service.vector_search.search_resume = MagicMock(
        return_value=[]
    )

    db = MagicMock()

    service.retrieve(
        db=db,
        resume_id="resume-123",
        requirement="Kubernetes",
        limit=10,
    )

    service.vector_search.search_resume.assert_called_once_with(
        db=db,
        resume_id="resume-123",
        query="Kubernetes",
        limit=10,
    )


def test_retrieve_returns_empty_for_empty_requirement():
    service = EvidenceRetrievalService()

    service.vector_search.search_resume = MagicMock()

    db = MagicMock()

    result = service.retrieve(
        db=db,
        resume_id="resume-123",
        requirement="",
    )

    assert result == []

    service.vector_search.search_resume.assert_not_called()


def test_retrieve_returns_empty_for_whitespace_requirement():
    service = EvidenceRetrievalService()

    service.vector_search.search_resume = MagicMock()

    db = MagicMock()

    result = service.retrieve(
        db=db,
        resume_id="resume-123",
        requirement="   ",
    )

    assert result == []

    service.vector_search.search_resume.assert_not_called()


def test_retrieve_uses_default_similarity_threshold():
    service = EvidenceRetrievalService()

    service.vector_search.search_resume = MagicMock(
        return_value=[
            {
                "id": 1,
                "source_id": "resume-123",
                "chunk_type": "resume_skill",
                "content": "FastAPI",
                "similarity": 0.30,
            },
            {
                "id": 2,
                "source_id": "resume-123",
                "chunk_type": "resume_summary",
                "content": "Developer",
                "similarity": 0.29,
            },
        ]
    )

    db = MagicMock()

    result = service.retrieve(
        db=db,
        resume_id="resume-123",
        requirement="FastAPI",
    )

    assert len(result) == 1
    assert result[0]["similarity"] == 0.30