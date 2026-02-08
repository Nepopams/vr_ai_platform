"""Deterministic scoring policy for assist agent hints (v0)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence


_STATUS_RANK = {"ok": 0, "rejected": 1, "error": 2, "skipped": 3}
_MAX_LATENCY = 1_000_000_000


@dataclass(frozen=True)
class AgentHintCandidate:
    agent_id: str
    status: str
    applicable: bool
    latency_ms: Optional[int]
    payload: dict | None
    items: list[dict]


def select_best_candidate(
    candidates: Sequence[AgentHintCandidate],
) -> tuple[AgentHintCandidate | None, str | None]:
    if not candidates:
        return None, None
    ordered = sorted(candidates, key=_score)
    best = ordered[0]
    if len(ordered) == 1:
        return best, "single_candidate"
    reason = _selection_reason(best, ordered[1])
    return best, reason


def _score(candidate: AgentHintCandidate) -> tuple[int, int, int, str]:
    status_rank = _STATUS_RANK.get(candidate.status, 99)
    applicable_rank = 0 if candidate.applicable else 1
    if status_rank != 0:
        applicable_rank = 0
    latency_rank = candidate.latency_ms if candidate.latency_ms is not None else _MAX_LATENCY
    return (status_rank, applicable_rank, latency_rank, candidate.agent_id)


def _selection_reason(best: AgentHintCandidate, runner_up: AgentHintCandidate) -> str:
    best_score = _score(best)
    runner_score = _score(runner_up)
    if best_score[0] != runner_score[0]:
        return "status_rank"
    if best_score[1] != runner_score[1]:
        return "applicable_tiebreak"
    if best_score[2] != runner_score[2]:
        return "latency_tiebreak"
    return "agent_id_tiebreak"
