from functools import lru_cache

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    MODEL_NAME = "all-MiniLM-L6-v2"

    @staticmethod
    @lru_cache(maxsize=1)
    def _get_model() -> SentenceTransformer:
        return SentenceTransformer(
            EmbeddingService.MODEL_NAME
        )

    def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        model = self._get_model()

        embedding = model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()