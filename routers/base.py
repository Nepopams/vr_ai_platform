"""Base interfaces for decision routing."""

from __future__ import annotations

from typing import Any, Dict, Protocol


class RouterStrategy(Protocol):
    def decide(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Build a DecisionDTO for the provided command."""
        raise NotImplementedError
