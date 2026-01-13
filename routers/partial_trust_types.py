"""Internal types for partial trust corridor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class LLMDecisionCandidate:
    intent: str
    job_type: Optional[str]
    proposed_actions: Optional[List[Dict[str, Any]]]
    clarify_question: Optional[str]
    clarify_missing_fields: Optional[List[str]]
    confidence: Optional[float]
    model_meta: Optional[Dict[str, Any]]
    latency_ms: Optional[int]
    error_type: Optional[str]


@dataclass(frozen=True)
class PartialTrustMeta:
    source: str
    reason_code: str
    baseline_summary: Optional[Dict[str, Any]]
    llm_summary: Optional[Dict[str, Any]]
    diff_summary: Optional[Dict[str, Any]]
