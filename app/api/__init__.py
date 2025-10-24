"""API routers module."""

from app.api.intent import router as intent_router
from app.api.channels import router as channels_router
from app.api.ingest import router as ingest_router

__all__ = ["intent_router", "channels_router", "ingest_router"]
