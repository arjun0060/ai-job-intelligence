import numpy as np
import pytest

from app.services.embeddings.embedding_service import EmbeddingService


class FakeEmbeddingModel:
    def encode(self, text, normalize_embeddings=False):
        assert normalize_embeddings is True

        return np.ones(384, dtype=np.float32)


def test_embed_rejects_empty_text():
    service = EmbeddingService()

    with pytest.raises(ValueError, match="Text cannot be empty"):
        service.embed("")


def test_embed_rejects_whitespace():
    service = EmbeddingService()

    with pytest.raises(ValueError, match="Text cannot be empty"):
        service.embed("   ")


def test_embed_returns_384_dimensions(monkeypatch):
    service = EmbeddingService()

    monkeypatch.setattr(
        service,
        "_get_model",
        lambda: FakeEmbeddingModel(),
    )

    embedding = service.embed(
        "Python backend development"
    )

    assert len(embedding) == 384


def test_embed_returns_list(monkeypatch):
    service = EmbeddingService()

    monkeypatch.setattr(
        service,
        "_get_model",
        lambda: FakeEmbeddingModel(),
    )

    embedding = service.embed(
        "FastAPI REST API"
    )

    assert isinstance(embedding, list)


def test_embed_uses_normalized_embeddings(monkeypatch):
    service = EmbeddingService()

    model = FakeEmbeddingModel()

    monkeypatch.setattr(
        service,
        "_get_model",
        lambda: model,
    )

    embedding = service.embed(
        "PostgreSQL and AWS"
    )

    # Fake model returns ones, so the important assertion here
    # is that the embedding was successfully converted to a list.
    assert len(embedding) == 384
    assert all(isinstance(value, float) for value in embedding)