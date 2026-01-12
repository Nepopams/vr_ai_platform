"""Logging for LLM runner shadow calls."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DEFAULT_LOG_PATH = Path("logs/llm_runner.jsonl")


def append_llm_runner_log(payload: Dict[str, Any]) -> Path:
    path = DEFAULT_LOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    record = dict(payload)
    record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{json.dumps(record, ensure_ascii=False)}\n")
    return path
