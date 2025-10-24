"""Application configuration and settings."""

from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI
    openai_api_key: str = Field(..., description="OpenAI API Key")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model for LLM")
    openai_embedding_model: str = Field(default="text-embedding-3-small", description="OpenAI embedding model")

    # Database
    db_url: str = Field(
        default="sqlite:///./data/app.db",
        description="Database connection URL",
    )

    # Vector Store
    vector_dir: str = Field(
        default="./data/indexes",
        description="Directory for FAISS indexes",
    )

    # Tenant & Locale
    tenant: str = Field(default="bank-asia", description="Default tenant")
    language: str = Field(default="en-IN", description="Default language")

    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level",
    )

    # Intent Detection
    min_confidence: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold",
    )
    ood_threshold: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Out-of-domain threshold",
    )

    # RAG
    chunk_size: int = Field(default=800, description="Text chunk size")
    chunk_overlap: int = Field(default=120, description="Chunk overlap")
    retrieval_top_k: int = Field(default=6, description="Top K retrievals")

    # Redis (optional)
    redis_url: str | None = Field(default=None, description="Redis URL")

    # Environment
    env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Environment",
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.env == "production"


# Global settings instance
settings = Settings()
