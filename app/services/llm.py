"""LLM service using OpenAI."""

import json
from typing import Any
from langchain_openai import ChatOpenAI
from app.config import settings


class LLMService:
    """Service for interacting with OpenAI LLM."""

    def __init__(self) -> None:
        """Initialize LLM service."""
        self._llm = ChatOpenAI(
            model=settings.openai_model,
            openai_api_key=settings.openai_api_key,
            temperature=0.0,
        )

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
    ) -> str:
        """Generate text from prompt."""
        messages = []

        if system_prompt:
            messages.append(("system", system_prompt))

        messages.append(("user", prompt))

        response = self._llm.invoke(messages)
        return response.content

    def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Generate JSON response from prompt."""
        response_text = self.generate(prompt, system_prompt, temperature=0.0)

        # Extract JSON from response (handle markdown code blocks)
        response_text = response_text.strip()

        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]

        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {response_text}") from e

    def batch_generate(
        self,
        prompts: list[str],
        system_prompt: str | None = None,
    ) -> list[str]:
        """Generate responses for multiple prompts."""
        return [self.generate(p, system_prompt) for p in prompts]


# Global LLM service
llm_service = LLMService()
