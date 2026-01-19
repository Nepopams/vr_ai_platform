"""JSONL logging for shadow agent diffs (privacy-safe, best-effort)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DEFAULT_LOG_PATH = Path("logs/shadow_agent_diff.jsonl")


def _enabled() -> bool:
    return os.getenv("SHADOW_AGENT_DIFF_LOG_ENABLED", "false").strip().lower() in {"1", "true", "yes"}


def resolve_log_path() -> Path:
    return Path(os.getenv("SHADOW_AGENT_DIFF_LOG_PATH", str(DEFAULT_LOG_PATH)))


def log_shadow_agent_diff(event: Dict[str, Any]) -> None:
    if not _enabled():
        return
    try:
        path = resolve_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        record = dict(event)
        record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"{json.dumps(record, ensure_ascii=False)}\n")
    except Exception:
        return


def summarize_agent_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "keys_present": [],
            "list_count_fields": {},
            "bool_flags": {},
            "nested_keys_count": 0,
        }
    keys_present = sorted(payload.keys())
    list_count_fields: Dict[str, int] = {}
    bool_flags: Dict[str, bool] = {}
    nested_keys_count = 0

    for key, value in payload.items():
        if isinstance(value, list):
            list_count_fields[key] = len(value)
            nested_keys_count += _nested_keys_count_from_list(value)
            continue
        if isinstance(value, dict):
            nested_keys_count += len(value.keys())
            continue
        if isinstance(value, bool):
            bool_flags[key] = value
            continue
        if isinstance(value, (int, float)):
            bool_flags[f"has_{key}"] = True
            continue
        if isinstance(value, str):
            bool_flags[f"has_{key}"] = True
            continue

    return {
        "keys_present": keys_present,
        "list_count_fields": list_count_fields,
        "bool_flags": bool_flags,
        "nested_keys_count": nested_keys_count,
    }


def _nested_keys_count_from_list(values: list[Any]) -> int:
    count = 0
    for item in values:
        if isinstance(item, dict):
            count += len(item.keys())
        if isinstance(item, list):
            count += _nested_keys_count_from_list(item)
    return count
