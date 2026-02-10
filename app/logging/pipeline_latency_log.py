"""Logging utilities for pipeline-wide latency instrumentation."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DEFAULT_LOG_PATH = Path("logs/pipeline_latency.jsonl")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def is_pipeline_latency_log_enabled() -> bool:
    return os.getenv("PIPELINE_LATENCY_LOG_ENABLED", "true").lower() in {
        "1",
        "true",
        "yes",
    }


def resolve_log_path() -> Path:
    return Path(
        os.getenv("PIPELINE_LATENCY_LOG_PATH", str(DEFAULT_LOG_PATH))
    )


def append_pipeline_latency_log(payload: Dict[str, Any]) -> Path:
    path = resolve_log_path()
    _ensure_parent(path)
    record = dict(payload)
    record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{json.dumps(record, ensure_ascii=False)}\n")
    return path
