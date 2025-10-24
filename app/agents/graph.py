"""LangGraph agent orchestration."""

from typing import Any, TypedDict
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session
from app.agents.tools import (
    retriever_tool,
    intent_detector_tool,
    entity_extractor_tool,
    validation_tool,
    channel_writer_tool,
)
from app.services.policy import policy_service


class AgentState(TypedDict):
    """State for agent graph."""

    utterance: str
    tenant: str
    channel: str
    locale: str
    trace_id: str
    intent: str | None
    confidence: float | None
    entities: dict[str, Any] | None
    kb_results: list[dict[str, Any]] | None
    citations: list[dict[str, Any]] | None
    validated: bool
    channel_created: dict[str, Any] | None
    error: str | None
    db: Session | None
    defaults: dict[str, Any] | None


def plan_node(state: AgentState) -> AgentState:
    """Planning node - decides what to do."""
    # This is entry point, no planning needed yet
    return state


def detect_intent_node(state: AgentState) -> AgentState:
    """Detect intent from utterance."""
    result = intent_detector_tool.run(
        utterance=state["utterance"],
        channel=state["channel"],
        locale=state["locale"],
        trace_id=state["trace_id"],
    )

    state["intent"] = result["intent"]
    state["confidence"] = result["confidence"]
    state["entities"] = result["entities"]

    return state


def retrieve_kb_node(state: AgentState) -> AgentState:
    """Retrieve relevant KB information."""
    # Build query from intent and entities
    entity_parts = []
    if state["entities"]:
        for key, value in state["entities"].items():
            if value:
                entity_parts.append(f"{key}:{value}")

    query = f"{state['intent']} {' '.join(entity_parts)}"

    result = retriever_tool.run(
        query=query,
        tenant=state["tenant"],
    )

    state["kb_results"] = result["results"]
    state["citations"] = result["citations"]

    return state


def extract_entities_node(state: AgentState) -> AgentState:
    """Extract entities with KB context."""
    kb_context = ""
    if state["kb_results"]:
        kb_context = "\n".join([r["content"][:300] for r in state["kb_results"][:3]])

    entities = entity_extractor_tool.run(
        utterance=state["utterance"],
        intent=state["intent"] or "unknown",
        kb_context=kb_context,
    )

    # Merge with existing entities
    if state["entities"]:
        state["entities"].update(entities)
    else:
        state["entities"] = entities

    return state


def validate_kb_node(state: AgentState) -> AgentState:
    """Validate entities against KB."""
    intent = state["intent"] or ""

    # Check if validation required
    if not policy_service.requires_kb_validation(intent):
        state["validated"] = True
        return state

    result = validation_tool.run(
        entities=state["entities"] or {},
        tenant=state["tenant"],
    )

    state["validated"] = result["valid"]

    # Add validation citations
    if result.get("citations"):
        if state["citations"]:
            state["citations"].extend(result["citations"])
        else:
            state["citations"] = result["citations"]

    return state


def route_policy_node(state: AgentState) -> AgentState:
    """Route based on policy."""
    intent = state["intent"] or ""
    confidence = state["confidence"] or 0.0

    # Check if should route
    if not policy_service.should_route(intent, confidence):
        state["error"] = f"Intent {intent} with confidence {confidence} does not meet policy requirements"
        return state

    # Check validation if required
    if policy_service.requires_kb_validation(intent) and not state.get("validated", False):
        state["error"] = "KB validation failed"
        return state

    return state


def open_channel_node(state: AgentState) -> AgentState:
    """Open/create channel."""
    intent = state["intent"] or ""

    if intent not in ["open_channel", "modify_channel"]:
        return state

    if not state.get("db"):
        state["error"] = "Database session not provided"
        return state

    try:
        result = channel_writer_tool.run(
            db=state["db"],
            action="create",
            tenant=state["tenant"],
            entities=state["entities"] or {},
            citations=state["citations"] or [],
            defaults=state.get("defaults", {}),
        )

        state["channel_created"] = result

    except Exception as e:
        state["error"] = str(e)

    return state


def respond_node(state: AgentState) -> AgentState:
    """Final response node."""
    # This is the final node, state is complete
    return state


def should_continue(state: AgentState) -> str:
    """Determine next node based on state."""
    if state.get("error"):
        return "respond"

    if not state.get("intent"):
        return "detect_intent"

    if not state.get("kb_results"):
        return "retrieve_kb"

    if state.get("intent") in ["open_channel", "modify_channel"]:
        if not state.get("validated"):
            return "validate_kb"

        if not state.get("channel_created"):
            return "open_channel"

    return "respond"


def create_agent_graph() -> StateGraph:
    """Create LangGraph agent workflow."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("plan", plan_node)
    workflow.add_node("detect_intent", detect_intent_node)
    workflow.add_node("retrieve_kb", retrieve_kb_node)
    workflow.add_node("extract_entities", extract_entities_node)
    workflow.add_node("validate_kb", validate_kb_node)
    workflow.add_node("route_policy", route_policy_node)
    workflow.add_node("open_channel", open_channel_node)
    workflow.add_node("respond", respond_node)

    # Set entry point
    workflow.set_entry_point("plan")

    # Add edges
    workflow.add_edge("plan", "detect_intent")
    workflow.add_edge("detect_intent", "retrieve_kb")
    workflow.add_edge("retrieve_kb", "extract_entities")
    workflow.add_edge("extract_entities", "validate_kb")
    workflow.add_edge("validate_kb", "route_policy")
    workflow.add_edge("route_policy", "open_channel")
    workflow.add_edge("open_channel", "respond")
    workflow.add_edge("respond", END)

    return workflow.compile()


# Global agent graph
agent_graph = create_agent_graph()
