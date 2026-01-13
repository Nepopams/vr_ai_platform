"""Internal types for shadow router suggestions (not part of public contracts)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class RouterSuggestion:
    suggested_intent: Optional[str]
    entities: Dict[str, Any]
    missing_fields: Optional[List[str]]
    clarify_question: Optional[str]
    confidence: Optional[float]
    explain: Optional[str]
    error_type: Optional[str]
    latency_ms: Optional[int]
    model_meta: Optional[Dict[str, Any]]
