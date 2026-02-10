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


def test_release_sanity_runs():
    script = load_script(
        BASE_DIR / "skills" / "release-sanity" / "scripts" / "release_sanity.py"
    )
    failures = script["run_checks"]()
    assert failures == []


def test_release_sanity_includes_decision_log_audit():
    script = load_script(
        BASE_DIR / "skills" / "release-sanity" / "scripts" / "release_sanity.py"
    )
    checks = script["CHECKS"]
    check_names = [name for name, _ in checks]
    assert "contract-checker" in check_names
    assert "decision-log-audit" in check_names
    assert "graph-sanity" in check_names


def test_detect_field_deletion():
    script = load_script(
        BASE_DIR / "skills" / "schema-bump" / "scripts" / "check_breaking_changes.py"
    )
    old = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example.schema.json"
    new = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example_deleted_field.schema.json"
    breaking = script["find_breaking_changes"](old, new)
    assert any("Removed property: status" in b for b in breaking)


def test_detect_type_change():
    script = load_script(
        BASE_DIR / "skills" / "schema-bump" / "scripts" / "check_breaking_changes.py"
    )
    old = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example.schema.json"
    new = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example_type_change.schema.json"
    breaking = script["find_breaking_changes"](old, new)
    assert any("Type changed for property 'status': string -> object" in b for b in breaking)


def test_detect_new_required_field():
    script = load_script(
        BASE_DIR / "skills" / "schema-bump" / "scripts" / "check_breaking_changes.py"
    )
    old = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example.schema.json"
    new = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example_new_required.schema.json"
    breaking = script["find_breaking_changes"](old, new)
    assert any("New required field: name" in b for b in breaking)


def test_detect_removed_required_backward_compat():
    script = load_script(
        BASE_DIR / "skills" / "schema-bump" / "scripts" / "check_breaking_changes.py"
    )
    old = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example.schema.json"
    new = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example_deleted_field.schema.json"
    breaking = script["find_breaking_changes"](old, new)
    assert any("Removed required field: status" in b for b in breaking)


def test_non_breaking_optional_addition():
    script = load_script(
        BASE_DIR / "skills" / "schema-bump" / "scripts" / "check_breaking_changes.py"
    )
    old = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example.schema.json"
    new = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example_optional_added.schema.json"
    breaking = script["find_breaking_changes"](old, new)
    assert breaking == []


def test_real_schemas_against_baseline_no_breaking():
    script = load_script(
        BASE_DIR / "skills" / "schema-bump" / "scripts" / "check_breaking_changes.py"
    )
    breaking = script["compare_all_schemas"]()
    assert breaking == []
