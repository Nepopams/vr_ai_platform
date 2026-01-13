"""Logging utilities for shadow router runs."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DEFAULT_LOG_PATH = Path("logs/shadow_router.jsonl")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def resolve_log_path() -> Path:
    return Path(os.getenv("SHADOW_ROUTER_LOG_PATH", str(DEFAULT_LOG_PATH)))


def append_shadow_router_log(payload: Dict[str, Any]) -> Path:
    path = resolve_log_path()
    _ensure_parent(path)
    record = dict(payload)
    record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{json.dumps(record, ensure_ascii=False)}\n")
    return path
