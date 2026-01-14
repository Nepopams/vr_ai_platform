"""JSONL logging for agent runs (privacy-safe, best-effort)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DEFAULT_LOG_PATH = Path("logs/agent_run.jsonl")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _enabled() -> bool:
    return os.getenv("AGENT_RUN_LOG_ENABLED", "false").strip().lower() in {"1", "true", "yes"}


def resolve_log_path() -> Path:
    return Path(os.getenv("AGENT_RUN_LOG_PATH", str(DEFAULT_LOG_PATH)))


def log_agent_run(event: Dict[str, Any]) -> None:
    if not _enabled():
        return
    try:
        path = resolve_log_path()
        _ensure_parent(path)
        record = dict(event)
        record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"{json.dumps(record, ensure_ascii=False)}\n")
    except Exception:
        return
