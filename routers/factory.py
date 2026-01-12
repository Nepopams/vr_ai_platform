"""Factory for router strategy selection."""

from __future__ import annotations

from typing import Any, Dict

from routers.base import RouterStrategy
from routers.config import get_strategy_name
from routers.v1 import RouterV1Adapter
from routers.v2 import RouterV2Pipeline


def get_router() -> RouterStrategy:
    strategy = get_strategy_name()
    if strategy == "v2":
        return RouterV2Pipeline()
    return RouterV1Adapter()


def decide(command: Dict[str, Any]) -> Dict[str, Any]:
    router = get_router()
    return router.decide(command)
