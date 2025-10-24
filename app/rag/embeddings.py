"""Embedding utilities using OpenAI."""

from typing import Any
from langchain_openai import OpenAIEmbeddings
from app.config import settings


class EmbeddingService:
    """Service for generating embeddings using OpenAI."""

    def __init__(self) -> None:
        """Initialize embedding service."""
        self._embeddings = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            openai_api_key=settings.openai_api_key,
        )

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text."""
        return self._embeddings.embed_query(text)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts."""
        return self._embeddings.embed_documents(texts)

    @property
    def embeddings(self) -> Any:
        """Get underlying embeddings object for LangChain."""
        return self._embeddings


# Global embedding service
embedding_service = EmbeddingService()
