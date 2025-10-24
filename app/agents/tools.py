"""LangGraph tools for agent orchestration."""

from datetime import datetime
from typing import Any
from sqlalchemy.orm import Session
from app.models.database import Channel, ChannelDetail
from app.models.schemas import Citation
from app.services.intent import intent_detection_service
from app.services.retrieval import retrieval_service


class RetrieverTool:
    """Tool for retrieving information from KB."""

    def __init__(self) -> None:
        """Initialize retriever tool."""
        self.name = "retriever"

    def run(self, query: str, tenant: str, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run retrieval."""
        results, citations = retrieval_service.retrieve(query, tenant, filters=filters)
        return {
            "results": results,
            "citations": [c.model_dump() for c in citations],
        }


class IntentDetectorTool:
    """Tool for detecting intent."""

    def __init__(self) -> None:
        """Initialize intent detector tool."""
        self.name = "intent_detector"

    def run(
        self,
        utterance: str,
        channel: str = "web",
        locale: str = "en-IN",
        trace_id: str = "unknown",
    ) -> dict[str, Any]:
        """Run intent detection."""
        result = intent_detection_service.detect_intent(utterance, channel, locale, trace_id)
        return result.model_dump()


class EntityExtractorTool:
    """Tool for extracting entities."""

    def __init__(self) -> None:
        """Initialize entity extractor tool."""
        self.name = "entity_extractor"

    def run(self, utterance: str, intent: str, kb_context: str = "") -> dict[str, Any]:
        """Run entity extraction."""
        entities = intent_detection_service.extract_entities(utterance, intent, kb_context)
        return entities.model_dump()


class ValidationTool:
    """Tool for validating entities with KB."""

    def __init__(self) -> None:
        """Initialize validation tool."""
        self.name = "validator"

    def run(self, entities: dict[str, Any], tenant: str) -> dict[str, Any]:
        """Run validation."""
        is_valid, citations = retrieval_service.validate_entities_with_kb(entities, tenant)
        return {
            "valid": is_valid,
            "citations": [c.model_dump() for c in citations],
        }


class ChannelWriterTool:
    """Tool for creating/updating channels."""

    def __init__(self) -> None:
        """Initialize channel writer tool."""
        self.name = "channel_writer"

    def create_channel(
        self,
        db: Session,
        tenant: str,
        channel_type: str,
        department: str | None,
        entities: dict[str, Any],
        citations: list[Citation],
        status: str = "active",
    ) -> Channel:
        """Create a new channel."""
        # Generate channel ID
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        existing_count = db.query(Channel).filter(
            Channel.tenant == tenant,
            Channel.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0),
        ).count()

        channel_id = f"CH-{timestamp}-{existing_count + 1:04d}"

        # Create channel name
        channel_name = f"{channel_type}-{department or 'general'}"

        # Create channel record
        channel = Channel(
            id=channel_id,
            name=channel_name,
            channel_type=channel_type,
            department=department,
            status=status,
            tenant=tenant,
        )
        db.add(channel)
        db.flush()

        # Add channel details
        for key, value in entities.items():
            if value is not None:
                # Handle list values
                if isinstance(value, list):
                    value_str = ",".join(map(str, value))
                else:
                    value_str = str(value)

                # Find relevant citation
                citation_text = None
                if citations:
                    citation_text = f"{citations[0].doc}"
                    if citations[0].page:
                        citation_text += f" (page {citations[0].page})"

                detail = ChannelDetail(
                    channel_id=channel_id,
                    key=key,
                    value=value_str,
                    source_doc=citations[0].doc if citations else None,
                    citation=citation_text,
                )
                db.add(detail)

        db.flush()
        return channel

    def run(
        self,
        db: Session,
        action: str,
        tenant: str,
        entities: dict[str, Any],
        citations: list[dict[str, Any]],
        defaults: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run channel operation."""
        defaults = defaults or {}

        if action == "create":
            channel_type = entities.get("channel", "web")
            department = entities.get("department")
            status = defaults.get("status", "active")

            # Convert citation dicts to Citation objects
            citation_objects = [Citation(**c) for c in citations]

            channel = self.create_channel(
                db=db,
                tenant=tenant,
                channel_type=channel_type,
                department=department,
                entities=entities,
                citations=citation_objects,
                status=status,
            )

            return {
                "success": True,
                "channel_id": channel.id,
                "channel_name": channel.name,
                "status": channel.status,
            }

        return {"success": False, "error": f"Unknown action: {action}"}


# Tool instances
retriever_tool = RetrieverTool()
intent_detector_tool = IntentDetectorTool()
entity_extractor_tool = EntityExtractorTool()
validation_tool = ValidationTool()
channel_writer_tool = ChannelWriterTool()
