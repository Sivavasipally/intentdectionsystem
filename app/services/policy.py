"""Policy routing service."""

from pathlib import Path
from typing import Any
import yaml


class PolicyService:
    """Service for managing intent routing policies."""

    def __init__(self, policy_file: str = "policies/router.yaml") -> None:
        """Initialize policy service."""
        self.policy_file = Path(policy_file)
        self._policy = self._load_policy()

    def _load_policy(self) -> dict[str, Any]:
        """Load policy from YAML file."""
        if not self.policy_file.exists():
            raise FileNotFoundError(f"Policy file not found: {self.policy_file}")

        with open(self.policy_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_min_confidence(self) -> float:
        """Get minimum confidence threshold."""
        return self._policy.get("min_confidence", 0.7)

    def get_route(self, intent: str) -> dict[str, Any] | None:
        """Get routing information for intent."""
        routes = self._policy.get("intent_routes", {})
        return routes.get(intent)

    def get_tool(self, intent: str) -> str | None:
        """Get tool name for intent."""
        route = self.get_route(intent)
        if route:
            return route.get("tool")
        return None

    def requires_kb_validation(self, intent: str) -> bool:
        """Check if intent requires KB validation."""
        route = self.get_route(intent)
        if route:
            return route.get("require_kb_validation", False)
        return False

    def should_route(self, intent: str, confidence: float) -> bool:
        """Check if intent should be routed based on policy."""
        if confidence < self.get_min_confidence():
            return False

        route = self.get_route(intent)
        return route is not None

    def get_fallback_tool(self) -> str:
        """Get fallback tool."""
        fallback = self._policy.get("fallback", {})
        return fallback.get("tool", "HumanHandover")


# Global policy service
policy_service = PolicyService()
