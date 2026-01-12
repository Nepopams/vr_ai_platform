"""Decision API route."""

from __future__ import annotations

from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, status
from app.services.decision_service import (
    CommandValidationError,
    decide,
    format_validation_error,
)


router = APIRouter()


@router.post("/decide")
async def decide_route(request: Request) -> Dict[str, Any]:
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Invalid JSON body."},
        )

    try:
        decision = decide(payload)
    except CommandValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "CommandDTO validation failed.",
                "violations": [format_validation_error(exc.error)],
            },
        )
    except Exception:
        trace_id = f"trace-{uuid4().hex}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal error.", "trace_id": trace_id},
        )

    return decision
