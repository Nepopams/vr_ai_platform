"""Reasoning log utilities."""

from __future__ import annotations

from typing import Iterable, List, Dict


def build_reasoning_log(
    command_id: str,
    steps: Iterable[str],
    model_version: str,
    prompt_version: str,
) -> Dict[str, object]:
    return {
        "command_id": command_id,
        "steps": list(steps),
        "model_version": model_version,
        "prompt_version": prompt_version,
    }


def format_reasoning_log(reasoning_log: Dict[str, object]) -> List[str]:
    steps = reasoning_log.get("steps", [])
    return [f"{index + 1}. {step}" for index, step in enumerate(steps)]
