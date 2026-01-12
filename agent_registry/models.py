from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class RegistryAgent:
    agent_id: str
    role: str
    intents: Sequence[str]
    action: str | None = None


@dataclass(frozen=True)
class IntentSpec:
    intent: str
    required_fields_for_execution: Sequence[str]


@dataclass(frozen=True)
class AgentRegistry:
    registry_version: str
    compat_adr: str
    compat_mvp: str
    compat_contracts_version: str
    agents: Sequence[RegistryAgent]
    intents: Mapping[str, IntentSpec]
