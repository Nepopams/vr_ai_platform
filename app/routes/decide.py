"""Decision API route."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.models.api_models import CommandRequest, DecisionResponse
from app.services.decision_service import (
    CommandValidationError,
    decide,
)


router = APIRouter()


@router.post("/decide")
async def decide_route(command: CommandRequest) -> DecisionResponse:
    try:
        decision = decide(command.model_dump(exclude_none=True))
    except CommandValidationError:
        # Safety net: Pydantic already validates input, but jsonschema
        # inside decide() may catch edge cases. Re-raise as 400.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "CommandDTO validation failed (jsonschema)."},
        )
    except Exception:
        trace_id = f"trace-{uuid4().hex}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal error.", "trace_id": trace_id},
        )

    return DecisionResponse.model_validate(decision)
