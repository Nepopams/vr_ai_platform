"""Stable sampling utilities for partial trust corridor."""

from __future__ import annotations

import hashlib


def stable_sample(command_id: str | None, sample_rate: float) -> bool:
    if sample_rate <= 0.0:
        return False
    if sample_rate >= 1.0:
        return True
    value = "" if command_id is None else str(command_id)
    # SHA-256 ensures deterministic sampling across processes and restarts.
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    bucket = int(digest[:16], 16) / 16**16
    return bucket < sample_rate
