"""Text chunking utilities."""

from typing import Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import settings


class ChunkingService:
    """Service for chunking documents."""

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        """Initialize chunking service."""
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk_text(self, text: str, metadata: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Chunk a single text into smaller pieces."""
        chunks = self._splitter.split_text(text)

        result = []
        for idx, chunk in enumerate(chunks):
            chunk_data = {
                "content": chunk,
                "chunk_index": idx,
                "metadata": metadata or {},
            }
            result.append(chunk_data)

        return result

    def chunk_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Chunk multiple documents."""
        all_chunks = []

        for doc in documents:
            text = doc.get("content", "")
            metadata = doc.get("metadata", {})

            chunks = self.chunk_text(text, metadata)
            all_chunks.extend(chunks)

        return all_chunks


# Global chunking service
chunking_service = ChunkingService()
