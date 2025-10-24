"""Pydantic models for API request/response schemas."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, field_validator


class IntentRequest(BaseModel):
    """Request model for intent detection."""

    utterance: str = Field(..., min_length=1, description="User utterance")
    channel: str = Field(default="web", description="Channel (web, whatsapp, etc.)")
    locale: str = Field(default="en-IN", description="Locale")
    tenant: str = Field(..., description="Tenant identifier")

    @field_validator("utterance")
    @classmethod
    def validate_utterance(cls, v: str) -> str:
        """Validate and clean utterance."""
        return v.strip()


class EntitySchema(BaseModel):
    """Extracted entities/slots."""

    channel: str | None = Field(None, description="Channel type")
    application: str | None = Field(None, description="Application name")
    department: str | None = Field(None, description="Department")
    operation: str | None = Field(None, description="Operation")
    operations: list[str] | None = Field(None, description="Multiple operations")
    amount: float | None = Field(None, description="Amount")
    account_type: str | None = Field(None, description="Account type")
    language: str | None = Field(None, description="Language preference")
    locale: str | None = Field(None, description="Locale")


class Citation(BaseModel):
    """Knowledge base citation."""

    doc: str = Field(..., description="Document name")
    page: int | None = Field(None, description="Page number")
    snippet: str = Field(..., description="Relevant snippet")
    score: float | None = Field(None, description="Relevance score")


class IntentResult(BaseModel):
    """Intent detection result."""

    intent: str = Field(..., description="Detected intent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    entities: EntitySchema = Field(default_factory=EntitySchema, description="Extracted entities")
    ood: bool = Field(default=False, description="Out-of-domain flag")
    trace_id: str = Field(..., alias="traceId", description="Trace ID")


class ChannelRecord(BaseModel):
    """Channel record summary."""

    id: str = Field(..., description="Channel ID")
    name: str = Field(..., description="Channel name")
    status: str = Field(..., description="Channel status")


class UnderstandAndOpenRequest(BaseModel):
    """Request to understand intent and open channel."""

    utterance: str = Field(..., min_length=1, description="User utterance")
    tenant: str = Field(..., description="Tenant identifier")
    defaults: dict[str, Any] = Field(
        default_factory=lambda: {"status": "active"},
        description="Default values",
    )


class UnderstandAndOpenResponse(BaseModel):
    """Response for understand-and-open."""

    intent: str = Field(..., description="Detected intent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    entities: EntitySchema = Field(..., description="Extracted entities")
    validated_from_kb: bool = Field(..., description="KB validation status")
    citations: list[Citation] = Field(..., description="Knowledge base citations")
    channel_record: ChannelRecord | None = Field(None, description="Created channel record")
    trace_id: str = Field(..., alias="traceId", description="Trace ID")
    error: str | None = Field(None, description="Error message if any")


class IngestRequest(BaseModel):
    """Document ingestion metadata."""

    tenant: str = Field(..., description="Tenant identifier")
    doc_type: str = Field(default="general", description="Document type")
    department: str | None = Field(None, description="Department")
    country: str | None = Field(None, description="Country")
    version: str | None = Field(None, description="Document version")


class IngestResponse(BaseModel):
    """Document ingestion response."""

    docs: int = Field(..., description="Number of documents processed")
    chunks: int = Field(..., description="Number of chunks created")
    index_path: str = Field(..., description="FAISS index path")
    trace_id: str = Field(..., alias="traceId", description="Trace ID")


class ChannelResponse(BaseModel):
    """Channel details response."""

    id: str = Field(..., description="Channel ID")
    name: str = Field(..., description="Channel name")
    channel_type: str = Field(..., description="Channel type")
    department: str | None = Field(None, description="Department")
    status: str = Field(..., description="Status")
    created_at: datetime = Field(..., description="Creation timestamp")
    tenant: str = Field(..., description="Tenant")
    details: list[dict[str, Any]] = Field(default_factory=list, description="Channel details")


class SimulateRequest(BaseModel):
    """Simulate intent detection request."""

    utterances: list[str] = Field(..., min_items=1, description="Utterances to test")
    tenant: str = Field(default="bank-asia", description="Tenant")
    channel: str = Field(default="web", description="Channel")
    locale: str = Field(default="en-IN", description="Locale")


class ErrorResponse(BaseModel):
    """Error response model."""

    type: str = Field(..., description="Error type")
    title: str = Field(..., description="Error title")
    status: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Error detail")
    trace_id: str = Field(..., alias="traceId", description="Trace ID")
