"""Intent detection API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db_session
from app.models.schemas import (
    IntentRequest,
    IntentResult,
    UnderstandAndOpenRequest,
    UnderstandAndOpenResponse,
    ChannelRecord,
    EntitySchema,
    SimulateRequest,
)
from app.services.intent import intent_detection_service
from app.agents.graph import agent_graph, AgentState
from app.utils import generate_trace_id
from app.models.database import Event

router = APIRouter(prefix="/intent/v1", tags=["intent"])


@router.post("/detect", response_model=IntentResult)
async def detect_intent(
    request: IntentRequest,
    db: Session = Depends(get_db_session),
) -> IntentResult:
    """Detect intent from user utterance."""
    trace_id = generate_trace_id()

    try:
        result = intent_detection_service.detect_intent(
            utterance=request.utterance,
            channel=request.channel,
            locale=request.locale,
            trace_id=trace_id,
        )

        # Log event
        event = Event(
            trace_id=trace_id,
            event_type="intent_detection",
            tenant=request.tenant,
            channel=request.channel,
            utterance="[REDACTED]",  # Never log PII
            intent=result.intent,
            confidence=result.confidence,
            entities=result.entities.model_dump(),
            status="success",
        )
        db.add(event)
        db.commit()

        return result

    except Exception as e:
        # Log error event
        event = Event(
            trace_id=trace_id,
            event_type="intent_detection",
            tenant=request.tenant,
            channel=request.channel,
            status="error",
            error=str(e),
        )
        db.add(event)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intent detection failed: {str(e)}",
        )


@router.post("/understand-and-open", response_model=UnderstandAndOpenResponse)
async def understand_and_open(
    request: UnderstandAndOpenRequest,
    db: Session = Depends(get_db_session),
) -> UnderstandAndOpenResponse:
    """Understand intent and open channel in one call."""
    trace_id = generate_trace_id()

    try:
        # Initialize agent state
        initial_state: AgentState = {
            "utterance": request.utterance,
            "tenant": request.tenant,
            "channel": "web",
            "locale": "en-IN",
            "trace_id": trace_id,
            "intent": None,
            "confidence": None,
            "entities": None,
            "kb_results": None,
            "citations": None,
            "validated": False,
            "channel_created": None,
            "error": None,
            "db": db,
            "defaults": request.defaults,
        }

        # Run agent graph
        final_state = agent_graph.invoke(initial_state)

        # Build response
        if final_state.get("error"):
            response = UnderstandAndOpenResponse(
                intent=final_state.get("intent", "unknown"),
                confidence=final_state.get("confidence", 0.0),
                entities=EntitySchema(**(final_state.get("entities") or {})),
                validated_from_kb=False,
                citations=[],
                channel_record=None,
                traceId=trace_id,
                error=final_state["error"],
            )
        else:
            channel_info = final_state.get("channel_created")
            channel_record = None

            if channel_info and channel_info.get("success"):
                channel_record = ChannelRecord(
                    id=channel_info["channel_id"],
                    name=channel_info["channel_name"],
                    status=channel_info["status"],
                )

            from app.models.schemas import Citation

            citations = [
                Citation(**c) for c in (final_state.get("citations") or [])
            ]

            response = UnderstandAndOpenResponse(
                intent=final_state.get("intent", "unknown"),
                confidence=final_state.get("confidence", 0.0),
                entities=EntitySchema(**(final_state.get("entities") or {})),
                validated_from_kb=final_state.get("validated", False),
                citations=citations,
                channel_record=channel_record,
                traceId=trace_id,
            )

        # Log event
        event = Event(
            trace_id=trace_id,
            event_type="understand_and_open",
            tenant=request.tenant,
            utterance="[REDACTED]",
            intent=response.intent,
            confidence=response.confidence,
            entities=response.entities.model_dump(),
            status="success" if not response.error else "error",
            error=response.error,
        )
        db.add(event)
        db.commit()

        return response

    except Exception as e:
        # Log error event
        event = Event(
            trace_id=trace_id,
            event_type="understand_and_open",
            tenant=request.tenant,
            status="error",
            error=str(e),
        )
        db.add(event)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}",
        )


@router.post("/simulate")
async def simulate_intent_detection(
    request: SimulateRequest,
    db: Session = Depends(get_db_session),
) -> dict[str, list[dict]]:
    """Simulate intent detection on multiple utterances."""
    results = []

    for utterance in request.utterances:
        trace_id = generate_trace_id()

        try:
            result = intent_detection_service.detect_intent(
                utterance=utterance,
                channel=request.channel,
                locale=request.locale,
                trace_id=trace_id,
            )

            results.append({
                "utterance": utterance,
                "intent": result.intent,
                "confidence": result.confidence,
                "entities": result.entities.model_dump(),
                "ood": result.ood,
                "traceId": trace_id,
            })

        except Exception as e:
            results.append({
                "utterance": utterance,
                "error": str(e),
                "traceId": trace_id,
            })

    return {"results": results}
