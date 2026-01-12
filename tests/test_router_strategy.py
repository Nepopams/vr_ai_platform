from routers.factory import get_router
from routers.v1 import RouterV1Adapter
from routers.v2 import RouterV2Pipeline


def test_default_is_v1(monkeypatch):
    monkeypatch.delenv("DECISION_ROUTER_STRATEGY", raising=False)
    router = get_router()
    assert isinstance(router, RouterV1Adapter)


def test_select_v2(monkeypatch):
    monkeypatch.setenv("DECISION_ROUTER_STRATEGY", "v2")
    router = get_router()
    assert isinstance(router, RouterV2Pipeline)
