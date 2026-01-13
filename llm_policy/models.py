from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping


@dataclass(frozen=True)
class CallSpec:
    provider: str
    model: str
    temperature: float | None
    max_tokens: int | None
    timeout_ms: int | None
    base_url: str | None
    project: str | None


@dataclass(frozen=True)
class FallbackRule:
    event: str
    action: str
    profile: str | None
    max_retries: int | None


@dataclass(frozen=True)
class LlmPolicy:
    schema_version: str
    compat_adr: str
    compat_note: str
    profiles: tuple[str, ...]
    tasks: tuple[str, ...]
    routing: Mapping[str, Mapping[str, CallSpec]]
    fallback_chain: tuple[FallbackRule, ...]


@dataclass(frozen=True)
class TaskRunResult:
    status: str
    data: Mapping[str, object] | None
    error_type: str | None
    attempts: int
    profile: str
    escalated: bool


@dataclass(frozen=True)
class PolicyCall:
    profile: str
    spec: CallSpec
    prompt: str


LlmCaller = Callable[[CallSpec, str], str]
