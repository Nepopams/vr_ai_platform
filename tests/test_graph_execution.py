import importlib.util
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
GRAPH_SUITE_PATH = (
    BASE_DIR / "skills" / "graph-sanity" / "scripts" / "run_graph_suite.py"
)


def _load_graph_suite_module():
    spec = importlib.util.spec_from_file_location("run_graph_suite", GRAPH_SUITE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load graph suite module at {GRAPH_SUITE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_process_command_returns_valid_decisions():
    graph_suite = _load_graph_suite_module()
    fixture_commands = graph_suite.load_fixture_commands()
    decisions = graph_suite.run_graph_suite()

    assert decisions
    assert {decision["command_id"] for decision in decisions} == {
        command["command_id"] for command in fixture_commands
    }
    assert {decision["action"] for decision in decisions}.issubset(
        {
            "start_job",
            "propose_create_task",
            "propose_add_shopping_item",
            "clarify",
        }
    )
