"""Prompt management service."""

from pathlib import Path
from typing import Any
import yaml


class PromptService:
    """Service for loading and managing prompts."""

    def __init__(self, prompts_dir: str = "prompts") -> None:
        """Initialize prompt service."""
        self.prompts_dir = Path(prompts_dir)
        self._cache: dict[str, dict[str, Any]] = {}

    def load_prompt(self, name: str) -> dict[str, Any]:
        """Load a prompt from YAML file."""
        if name in self._cache:
            return self._cache[name]

        prompt_file = self.prompts_dir / f"{name}.yaml"
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

        with open(prompt_file, "r", encoding="utf-8") as f:
            prompt_data = yaml.safe_load(f)

        self._cache[name] = prompt_data
        return prompt_data

    def format_prompt(self, name: str, **kwargs: Any) -> str:
        """Load and format a prompt template."""
        prompt_data = self.load_prompt(name)
        template = prompt_data.get("template", "")
        return template.format(**kwargs)

    def get_system_prompt(self, name: str) -> str:
        """Get system prompt."""
        prompt_data = self.load_prompt(name)
        return prompt_data.get("system", "")

    def get_few_shot_examples(self, name: str) -> list[dict[str, str]]:
        """Get few-shot examples."""
        prompt_data = self.load_prompt(name)
        return prompt_data.get("few_shot", [])


# Global prompt service
prompt_service = PromptService()
