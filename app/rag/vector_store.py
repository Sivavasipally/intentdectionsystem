"""FAISS vector store management."""

import os
import pickle
from pathlib import Path
from typing import Any
import faiss
import numpy as np
from app.config import settings
from app.rag.embeddings import embedding_service


class FAISSVectorStore:
    """FAISS-based vector store."""

    def __init__(self, tenant: str, dimension: int = 1536) -> None:
        """Initialize FAISS vector store."""
        self.tenant = tenant
        self.dimension = dimension
        self.index_path = Path(settings.vector_dir) / tenant
        self.index_path.mkdir(parents=True, exist_ok=True)

        self.index_file = self.index_path / "faiss.index"
        self.metadata_file = self.index_path / "metadata.pkl"

        # Initialize or load index
        if self.index_file.exists():
            self.index = faiss.read_index(str(self.index_file))
            with open(self.metadata_file, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(dimension)
            self.metadata: list[dict[str, Any]] = []

    def add_vectors(
        self,
        vectors: np.ndarray | list[list[float]],
        metadata: list[dict[str, Any]],
    ) -> None:
        """Add vectors to the index."""
        if isinstance(vectors, list):
            vectors = np.array(vectors, dtype=np.float32)

        self.index.add(vectors)
        self.metadata.extend(metadata)

    def search(
        self,
        query_vector: list[float] | np.ndarray,
        k: int | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors."""
        k = k or settings.retrieval_top_k

        if isinstance(query_vector, list):
            query_vector = np.array([query_vector], dtype=np.float32)
        elif len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)

        # Search
        distances, indices = self.index.search(query_vector, min(k * 2, self.index.ntotal))

        # Collect results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue

            meta = self.metadata[idx]

            # Apply filters
            if filters:
                if not all(meta.get(key) == value for key, value in filters.items()):
                    continue

            results.append({
                "content": meta.get("content", ""),
                "metadata": meta,
                "score": float(1 / (1 + dist)),  # Convert distance to similarity
            })

            if len(results) >= k:
                break

        return results

    def save(self) -> None:
        """Save index and metadata to disk."""
        faiss.write_index(self.index, str(self.index_file))
        with open(self.metadata_file, "wb") as f:
            pickle.dump(self.metadata, f)

    @property
    def count(self) -> int:
        """Get number of vectors in index."""
        return self.index.ntotal


class VectorStoreService:
    """Service for managing vector stores per tenant."""

    def __init__(self) -> None:
        """Initialize vector store service."""
        self._stores: dict[str, FAISSVectorStore] = {}

    def get_store(self, tenant: str) -> FAISSVectorStore:
        """Get or create vector store for tenant."""
        if tenant not in self._stores:
            self._stores[tenant] = FAISSVectorStore(tenant)
        return self._stores[tenant]

    def search(
        self,
        query: str,
        tenant: str,
        k: int | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search across tenant's vector store."""
        store = self.get_store(tenant)
        query_vector = embedding_service.embed_text(query)
        return store.search(query_vector, k=k, filters=filters)


# Global vector store service
vector_store_service = VectorStoreService()
