"""Intent detection service."""

from typing import Any
from app.models.schemas import IntentResult, EntitySchema
from app.services.llm import llm_service
from app.services.prompts import prompt_service
from app.config import settings


class IntentDetectionService:
    """Service for detecting user intent."""

    def __init__(self) -> None:
        """Initialize intent detection service."""
        pass

    def detect_intent(
        self,
        utterance: str,
        channel: str = "web",
        locale: str = "en-IN",
        trace_id: str = "unknown",
    ) -> IntentResult:
        """Detect intent from utterance using LLM."""
        # Load router prompt
        system_prompt = prompt_service.get_system_prompt("router")
        user_prompt = prompt_service.format_prompt(
            "router",
            utterance=utterance,
            channel=channel,
            locale=locale,
        )

        # Get few-shot examples and build full prompt
        few_shot = prompt_service.get_few_shot_examples("router")
        full_prompt = self._build_few_shot_prompt(few_shot, user_prompt)

        # Call LLM
        try:
            response = llm_service.generate_json(full_prompt, system_prompt)
        except Exception as e:
            # Fallback to low confidence generic intent
            return IntentResult(
                intent="ood",
                confidence=0.3,
                entities=EntitySchema(),
                ood=True,
                traceId=trace_id,
            )

        # Parse response
        intent = response.get("intent", "ood")
        confidence = float(response.get("confidence", 0.5))
        entities_dict = response.get("entities", {})

        # Check OOD
        ood = intent == "ood" or confidence < settings.ood_threshold

        # Create entity schema
        entities = EntitySchema(**entities_dict)

        return IntentResult(
            intent=intent,
            confidence=confidence,
            entities=entities,
            ood=ood,
            traceId=trace_id,
        )

    def extract_entities(
        self,
        utterance: str,
        intent: str,
        kb_context: str = "",
    ) -> EntitySchema:
        """Extract entities using LLM with KB context."""
        system_prompt = prompt_service.get_system_prompt("entities")
        user_prompt = prompt_service.format_prompt(
            "entities",
            utterance=utterance,
            intent=intent,
            kb_context=kb_context or "No context available",
        )

        try:
            response = llm_service.generate_json(user_prompt, system_prompt)
            return EntitySchema(**response)
        except Exception:
            return EntitySchema()

    def _build_few_shot_prompt(
        self,
        examples: list[dict[str, str]],
        user_prompt: str,
    ) -> str:
        """Build few-shot prompt with examples."""
        prompt_parts = []

        for example in examples:
            prompt_parts.append(f"User: {example['user']}")
            prompt_parts.append(f"Assistant: {example['assistant']}")
            prompt_parts.append("")

        prompt_parts.append(user_prompt)

        return "\n".join(prompt_parts)


# Global intent detection service
intent_detection_service = IntentDetectionService()
