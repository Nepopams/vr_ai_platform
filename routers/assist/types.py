"""Internal types for LLM assist hints (not part of public contracts)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class NormalizationHint:
    normalized_text: Optional[str]
    intent_hint: Optional[str]
    entities_hint: Optional[Dict[str, object]]
    confidence: Optional[float]
    error_type: Optional[str]
    latency_ms: Optional[int]


@dataclass(frozen=True)
class EntityHints:
    items: List[dict]
    task_hints: Dict[str, object]
    confidence: Optional[float]
    error_type: Optional[str]
    latency_ms: Optional[int]


@dataclass(frozen=True)
class AgentEntityHint:
    status: str
    items: List[dict]
    latency_ms: Optional[int]
    candidates_count: int = 0
    selected_agent_id: Optional[str] = None
    selected_status: Optional[str] = None
    selection_reason: Optional[str] = None


@dataclass(frozen=True)
class ClarifyHint:
    question: Optional[str]
    missing_fields: Optional[List[str]]
    confidence: Optional[float]
    error_type: Optional[str]
    latency_ms: Optional[int]


@dataclass(frozen=True)
class AssistHints:
    normalization: Optional[NormalizationHint]
    entities: Optional[EntityHints]
    clarify: Optional[ClarifyHint]


@dataclass(frozen=True)
class AssistApplication:
    normalized: Dict[str, object]
    clarify_question: Optional[str]
    clarify_missing_fields: Optional[List[str]]
