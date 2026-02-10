from __future__ import annotations

from typing import Any

from agent_registry.v0_models import AgentRegistryV0, AgentSpec


class CapabilitiesLookup:
    """Consolidated agent filtering by intent and mode."""

    def __init__(
        self,
        registry: AgentRegistryV0,
        catalog: dict[str, dict[str, Any]] | None = None,
    ):
        self._registry = registry
        self._catalog = catalog or {}

    def find_agents(self, intent: str, mode: str) -> list[AgentSpec]:
        """Return enabled agents matching both intent and mode."""
        result: list[AgentSpec] = []
        for agent in self._registry.agents:
            if not agent.enabled:
                continue
            if agent.mode != mode:
                continue
            for cap in agent.capabilities:
                if intent in cap.allowed_intents:
                    result.append(agent)
                    break
        return result

    def has_capability(self, intent: str, mode: str) -> bool:
        """Check if any enabled agent can handle intent in given mode."""
        return len(self.find_agents(intent, mode)) > 0

    def list_capabilities(self) -> list[str]:
        """Return all capability IDs from the catalog."""
        return list(self._catalog.keys())
