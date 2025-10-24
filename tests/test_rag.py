"""Tests for RAG components."""

import pytest
import numpy as np
from app.rag.embeddings import embedding_service
from app.rag.chunking import chunking_service
from app.rag.vector_store import FAISSVectorStore


class TestEmbeddings:
    """Test embedding service."""

    def test_embed_single_text(self):
        """Test embedding a single text."""
        text = "This is a test document"
        embedding = embedding_service.embed_text(text)

        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)

    def test_embed_multiple_texts(self):
        """Test embedding multiple texts."""
        texts = [
            "First document",
            "Second document",
            "Third document",
        ]

        embeddings = embedding_service.embed_texts(texts)

        assert len(embeddings) == len(texts)
        assert all(isinstance(e, list) for e in embeddings)


class TestChunking:
    """Test chunking service."""

    def test_chunk_short_text(self):
        """Test chunking a short text."""
        text = "This is a short text that should fit in one chunk."

        chunks = chunking_service.chunk_text(text)

        assert len(chunks) == 1
        assert chunks[0]["content"] == text

    def test_chunk_long_text(self):
        """Test chunking a long text."""
        # Create a long text
        text = " ".join(["This is sentence number {}." for _ in range(100)])

        chunks = chunking_service.chunk_text(text)

        assert len(chunks) > 1
        assert all("content" in c for c in chunks)
        assert all("chunk_index" in c for c in chunks)


class TestVectorStore:
    """Test FAISS vector store."""

    def test_add_and_search(self):
        """Test adding vectors and searching."""
        store = FAISSVectorStore(tenant="test-tenant", dimension=768)

        # Create test vectors
        vectors = np.random.rand(10, 768).astype(np.float32)
        metadata = [
            {"content": f"Document {i}", "doc_id": i}
            for i in range(10)
        ]

        # Add vectors
        store.add_vectors(vectors, metadata)

        assert store.count == 10

        # Search
        query_vector = vectors[0].tolist()
        results = store.search(query_vector, k=3)

        assert len(results) <= 3
        assert all("content" in r for r in results)
        assert all("metadata" in r for r in results)

    def test_search_with_filters(self):
        """Test searching with metadata filters."""
        store = FAISSVectorStore(tenant="test-tenant", dimension=768)

        vectors = np.random.rand(5, 768).astype(np.float32)
        metadata = [
            {"content": f"Doc {i}", "department": "retail" if i < 3 else "corporate"}
            for i in range(5)
        ]

        store.add_vectors(vectors, metadata)

        # Search with filter
        query_vector = vectors[0].tolist()
        results = store.search(
            query_vector,
            k=5,
            filters={"department": "retail"},
        )

        assert len(results) <= 3  # Only retail documents
