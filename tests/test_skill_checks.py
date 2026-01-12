import runpy
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def load_script(path: Path) -> dict:
    return runpy.run_path(str(path), run_name="__test__")


def test_contract_checker_fixtures():
    script = load_script(
        BASE_DIR / "skills" / "contract-checker" / "scripts" / "validate_contracts.py"
    )
    failures = script["validate_fixtures"]()
    assert failures == []


def test_decision_log_audit_fixture():
    script = load_script(
        BASE_DIR
        / "skills"
        / "decision-log-audit"
        / "scripts"
        / "audit_decision_logs.py"
    )
    log_path = (
        BASE_DIR
        / "skills"
        / "decision-log-audit"
        / "fixtures"
        / "sample_decision_log.jsonl"
    )
    errors = script["audit_log"](log_path)
    assert errors == []


def test_graph_sanity_runs():
    script = load_script(
        BASE_DIR / "skills" / "graph-sanity" / "scripts" / "run_graph_suite.py"
    )
    fixture_path = (
        BASE_DIR
        / "skills"
        / "contract-checker"
        / "fixtures"
        / "valid_command_create_task.json"
    )
    failures = script["run_graph_suite"]([fixture_path])
    assert failures == []


def test_schema_bump_breaking_changes():
    script = load_script(
        BASE_DIR
        / "skills"
        / "schema-bump"
        / "scripts"
        / "check_breaking_changes.py"
    )
    old_schema = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example.schema.json"
    new_schema = (
        BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example.schema.next.json"
    )
    breaking = script["find_breaking_changes"](old_schema, new_schema)
    assert breaking == []
