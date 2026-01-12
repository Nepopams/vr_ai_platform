"""Decision logging utilities."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_LOG_PATH = Path("logs/decisions.jsonl")
DEFAULT_TEXT_LOG_PATH = Path("logs/decision_text.jsonl")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def resolve_log_path() -> Path:
    return Path(os.getenv("DECISION_LOG_PATH", str(DEFAULT_LOG_PATH)))


def resolve_text_log_path() -> Path:
    return Path(os.getenv("DECISION_TEXT_LOG_PATH", str(DEFAULT_TEXT_LOG_PATH)))


def append_decision_log(decision: Dict[str, Any]) -> Path:
    path = resolve_log_path()
    _ensure_parent(path)
    payload = dict(decision)
    if not payload.get("created_at"):
        payload["created_at"] = datetime.now(timezone.utc).isoformat()
    line = json.dumps(payload, ensure_ascii=False)
    _append_line(path, line)
    return path


def _append_line(path: Path, line: str) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{line}\n")


def append_decision_text(command: Dict[str, Any], trace_id: Optional[str]) -> Optional[Path]:
    if os.getenv("LOG_USER_TEXT", "false").lower() not in {"1", "true", "yes"}:
        return None

    path = resolve_text_log_path()
    _ensure_parent(path)
    payload = {
        "command_id": command.get("command_id"),
        "trace_id": trace_id,
        "text": command.get("text"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    line = json.dumps(payload, ensure_ascii=False)
    _append_line(path, line)
    return path
