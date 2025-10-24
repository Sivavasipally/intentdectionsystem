"""SQLAlchemy database models."""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Text,
    ForeignKey,
    LargeBinary,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Channel(Base):
    """Channel model."""

    __tablename__ = "channels"

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    channel_type = Column(String(50), nullable=False)
    department = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant = Column(String(100), nullable=False, index=True)

    # Relationships
    details = relationship("ChannelDetail", back_populates="channel", cascade="all, delete-orphan")


class ChannelDetail(Base):
    """Channel detail model (normalized key-value pairs)."""

    __tablename__ = "channel_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String(50), ForeignKey("channels.id"), nullable=False, index=True)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    source_doc = Column(String(500), nullable=True)
    citation = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    channel = relationship("Channel", back_populates="details")


class Event(Base):
    """Event log model."""

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String(50), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    tenant = Column(String(100), nullable=False, index=True)
    channel = Column(String(50), nullable=True)
    utterance = Column(Text, nullable=True)  # Redacted in logs
    intent = Column(String(100), nullable=True)
    confidence = Column(Float, nullable=True)
    entities = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class KbDoc(Base):
    """Knowledge base document model."""

    __tablename__ = "kb_docs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(500), nullable=False)
    filename = Column(String(255), nullable=False)
    doc_type = Column(String(50), nullable=False)
    tenant = Column(String(100), nullable=False, index=True)
    department = Column(String(100), nullable=True)
    country = Column(String(10), nullable=True)
    version = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chunks = relationship("KbChunk", back_populates="doc", cascade="all, delete-orphan")


class KbChunk(Base):
    """Knowledge base chunk model."""

    __tablename__ = "kb_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey("kb_docs.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(LargeBinary, nullable=True)  # Stored in FAISS primarily
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    chunk_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    doc = relationship("KbDoc", back_populates="chunks")
