"""Logging utilities for partial trust risk events."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DEFAULT_LOG_PATH = Path("logs/partial_trust_risk.jsonl")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def resolve_log_path() -> Path:
    return Path(os.getenv("PARTIAL_TRUST_RISK_LOG_PATH", str(DEFAULT_LOG_PATH)))


def append_partial_trust_risk_log(payload: Dict[str, Any]) -> Path:
    # NO RAW USER OR LLM TEXT — PRIVACY GUARANTEE.
    path = resolve_log_path()
    _ensure_parent(path)
    record = dict(payload)
    record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{json.dumps(record, ensure_ascii=False)}\n")
    return path
