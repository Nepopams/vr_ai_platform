"""Logging utilities for unified fallback and error rate metrics."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DEFAULT_LOG_PATH = Path("logs/fallback_metrics.jsonl")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def is_fallback_metrics_log_enabled() -> bool:
    return os.getenv("FALLBACK_METRICS_LOG_ENABLED", "true").lower() in {
        "1",
        "true",
        "yes",
    }


def resolve_log_path() -> Path:
    return Path(
        os.getenv("FALLBACK_METRICS_LOG_PATH", str(DEFAULT_LOG_PATH))
    )


def append_fallback_metrics_log(payload: Dict[str, Any]) -> Path:
    # NO RAW USER OR LLM TEXT — PRIVACY GUARANTEE.
    path = resolve_log_path()
    _ensure_parent(path)
    record = dict(payload)
    record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{json.dumps(record, ensure_ascii=False)}\n")
    return path
