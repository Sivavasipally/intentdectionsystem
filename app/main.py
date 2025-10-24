"""FastAPI application main entry point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db import init_db
from app.api import intent_router, channels_router, ingest_router
from app.utils import generate_trace_id, set_trace_id

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Intent Detection System...")
    logger.info(f"Environment: {settings.env}")
    logger.info(f"Tenant: {settings.tenant}")

    # Initialize database
    init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down Intent Detection System...")


# Create FastAPI app
app = FastAPI(
    title="GenAI Intent Understanding System",
    description="Multi-channel intent detection with RAG and LangGraph agents",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for trace ID
@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    """Add trace ID to request context."""
    trace_id = generate_trace_id()
    set_trace_id(trace_id)

    response = await call_next(request)
    response.headers["X-Trace-Id"] = trace_id

    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    from app.utils import get_trace_id

    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "type": "internal_error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": str(exc) if not settings.is_production else "An error occurred",
            "traceId": get_trace_id(),
        },
    )


# Include routers
app.include_router(intent_router)
app.include_router(channels_router)
app.include_router(ingest_router)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.env,
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "GenAI Intent Understanding System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.env == "development",
    )
