"""Router strategy V1 adapter for the legacy graph pipeline."""

from __future__ import annotations

from typing import Any, Dict

from graphs.core_graph import process_command
from routers.base import RouterStrategy


class RouterV1Adapter(RouterStrategy):
    def decide(self, command: Dict[str, Any]) -> Dict[str, Any]:
        return process_command(command)
