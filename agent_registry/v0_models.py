from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class RunnerSpec:
    kind: str
    ref: str


@dataclass(frozen=True)
class AgentCapability:
    capability_id: str
    allowed_intents: Sequence[str]
    risk_level: str | None = None


@dataclass(frozen=True)
class TimeoutSpec:
    timeout_ms: int | None = None


@dataclass(frozen=True)
class PrivacySpec:
    allow_raw_logs: bool = False


@dataclass(frozen=True)
class AgentSpec:
    agent_id: str
    enabled: bool
    mode: str
    capabilities: Sequence[AgentCapability]
    runner: RunnerSpec
    timeouts: TimeoutSpec | None = None
    privacy: PrivacySpec | None = None
    llm_profile_id: str | None = None


@dataclass(frozen=True)
class AgentRegistryV0:
    registry_version: str
    compat_adr: str | None
    compat_note: str | None
    agents: Sequence[AgentSpec]
