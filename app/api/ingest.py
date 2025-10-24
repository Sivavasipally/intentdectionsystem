"""Document ingestion API endpoints."""

import os
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db_session
from app.models.schemas import IngestResponse
from app.services.ingestion import ingestion_service
from app.utils import generate_trace_id

router = APIRouter(prefix="/ingest", tags=["ingestion"])


@router.post("/", response_model=IngestResponse)
async def ingest_documents(
    files: list[UploadFile] = File(...),
    tenant: str = Form(...),
    doc_type: str = Form(default="general"),
    department: str | None = Form(default=None),
    country: str | None = Form(default=None),
    version: str | None = Form(default=None),
    db: Session = Depends(get_db_session),
) -> IngestResponse:
    """Ingest documents into knowledge base."""
    trace_id = generate_trace_id()

    # Create temp directory for uploads
    upload_dir = Path("./data/uploads") / trace_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_paths = []

    try:
        # Save uploaded files
        for file in files:
            if not file.filename:
                continue

            # Validate file type
            ext = Path(file.filename).suffix.lower()
            if ext not in [".pdf", ".docx", ".doc", ".md", ".markdown", ".txt"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type: {ext}. Supported: .pdf, .docx, .doc, .md, .txt",
                )

            file_path = upload_dir / file.filename
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            file_paths.append(str(file_path))

        if not file_paths:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid files provided",
            )

        # Ingest documents
        metadata = {
            "doc_type": doc_type,
            "department": department,
            "country": country,
            "version": version,
        }

        total_docs, total_chunks, index_path = ingestion_service.ingest_documents(
            file_paths=file_paths,
            tenant=tenant,
            db=db,
            metadata=metadata,
        )

        return IngestResponse(
            docs=total_docs,
            chunks=total_chunks,
            index_path=index_path,
            traceId=trace_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}",
        )

    finally:
        # Cleanup temp files
        if upload_dir.exists():
            shutil.rmtree(upload_dir, ignore_errors=True)
