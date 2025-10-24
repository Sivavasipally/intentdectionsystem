"""Tracing utilities."""

import uuid
from contextvars import ContextVar

# Context variable for trace ID
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")


def generate_trace_id() -> str:
    """Generate a new trace ID."""
    return str(uuid.uuid4())[:8]


def get_trace_id() -> str:
    """Get current trace ID from context."""
    trace_id = trace_id_var.get()
    if not trace_id:
        trace_id = generate_trace_id()
        trace_id_var.set(trace_id)
    return trace_id


def set_trace_id(trace_id: str) -> None:
    """Set trace ID in context."""
    trace_id_var.set(trace_id)
