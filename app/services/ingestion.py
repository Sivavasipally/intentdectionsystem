"""Document ingestion service."""

import os
from pathlib import Path
from typing import Any
import docx2txt
from pypdf import PdfReader
from sqlalchemy.orm import Session
from app.models.database import KbDoc, KbChunk
from app.rag import chunking_service, embedding_service, vector_store_service
from app.config import settings


class IngestionService:
    """Service for ingesting documents into knowledge base."""

    def __init__(self) -> None:
        """Initialize ingestion service."""
        pass

    def extract_text_from_pdf(self, file_path: str) -> list[dict[str, Any]]:
        """Extract text from PDF file."""
        reader = PdfReader(file_path)
        pages = []

        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text.strip():
                pages.append({
                    "content": text,
                    "page_number": page_num,
                })

        return pages

    def extract_text_from_docx(self, file_path: str) -> list[dict[str, Any]]:
        """Extract text from DOCX file."""
        text = docx2txt.process(file_path)
        return [{
            "content": text,
            "page_number": None,
        }]

    def extract_text_from_markdown(self, file_path: str) -> list[dict[str, Any]]:
        """Extract text from Markdown file."""
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return [{
            "content": text,
            "page_number": None,
        }]

    def extract_text(self, file_path: str) -> list[dict[str, Any]]:
        """Extract text based on file extension."""
        ext = Path(file_path).suffix.lower()

        if ext == ".pdf":
            return self.extract_text_from_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return self.extract_text_from_docx(file_path)
        elif ext in [".md", ".markdown", ".txt"]:
            return self.extract_text_from_markdown(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def ingest_document(
        self,
        file_path: str,
        tenant: str,
        db: Session,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[KbDoc, list[KbChunk]]:
        """Ingest a single document."""
        metadata = metadata or {}

        filename = os.path.basename(file_path)

        # Create document record
        kb_doc = KbDoc(
            path=file_path,
            filename=filename,
            doc_type=metadata.get("doc_type", "general"),
            tenant=tenant,
            department=metadata.get("department"),
            country=metadata.get("country"),
            version=metadata.get("version"),
        )
        db.add(kb_doc)
        db.flush()

        # Extract text
        pages = self.extract_text(file_path)

        # Chunk all pages
        all_chunks = []
        chunk_records = []

        for page in pages:
            page_metadata = {
                "tenant": tenant,
                "doc_id": kb_doc.id,
                "filename": filename,
                "page_number": page.get("page_number"),
                "doc_type": metadata.get("doc_type", "general"),
                "department": metadata.get("department"),
            }

            chunks = chunking_service.chunk_text(page["content"], page_metadata)

            for chunk in chunks:
                chunk_record = KbChunk(
                    doc_id=kb_doc.id,
                    content=chunk["content"],
                    chunk_index=chunk["chunk_index"],
                    page_number=page.get("page_number"),
                    chunk_metadata=chunk["metadata"],
                )
                db.add(chunk_record)
                chunk_records.append(chunk_record)
                all_chunks.append(chunk)

        db.flush()

        # Generate embeddings
        chunk_texts = [c["content"] for c in all_chunks]
        embeddings = embedding_service.embed_texts(chunk_texts)

        # Add to vector store
        vector_store = vector_store_service.get_store(tenant)

        vector_metadata = []
        for chunk, embedding in zip(all_chunks, embeddings):
            meta = chunk["metadata"].copy()
            meta["content"] = chunk["content"]
            vector_metadata.append(meta)

        vector_store.add_vectors(embeddings, vector_metadata)
        vector_store.save()

        return kb_doc, chunk_records

    def ingest_documents(
        self,
        file_paths: list[str],
        tenant: str,
        db: Session,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[int, int, str]:
        """Ingest multiple documents."""
        total_docs = 0
        total_chunks = 0

        for file_path in file_paths:
            doc, chunks = self.ingest_document(file_path, tenant, db, metadata)
            total_docs += 1
            total_chunks += len(chunks)

        db.commit()

        index_path = str(Path(settings.vector_dir) / tenant)
        return total_docs, total_chunks, index_path


# Global ingestion service
ingestion_service = IngestionService()
