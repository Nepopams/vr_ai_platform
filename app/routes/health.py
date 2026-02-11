"""Health and readiness endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter
from fastapi.responses import JSONResponse

BASE_DIR = Path(__file__).resolve().parents[2]
VERSION_PATH = BASE_DIR / "contracts" / "VERSION"
COMMAND_SCHEMA_PATH = BASE_DIR / "contracts" / "schemas" / "command.schema.json"
DECISION_SCHEMA_PATH = BASE_DIR / "contracts" / "schemas" / "decision.schema.json"


def _read_version() -> str:
    try:
        return VERSION_PATH.read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"


router = APIRouter()


@router.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "ok", "version": _read_version()}


@router.get("/ready")
async def ready() -> JSONResponse:
    checks: Dict[str, str] = {}
    try:
        COMMAND_SCHEMA_PATH.read_text(encoding="utf-8")
        DECISION_SCHEMA_PATH.read_text(encoding="utf-8")
        checks["decision_service"] = "ok"
    except Exception as exc:
        checks["decision_service"] = f"error: {exc}"
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "checks": checks},
        )
    return JSONResponse(
        status_code=200,
        content={"status": "ready", "checks": checks},
    )
