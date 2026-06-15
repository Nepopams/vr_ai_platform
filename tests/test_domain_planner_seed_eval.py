"""Tests for the Domain Planner v1 seed eval runner."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = BASE_DIR / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import evaluate_domain_planner_seed as eval_seed


def _write_seed_files(source_dir: Path, *, expected_outcome: str = "execute") -> None:
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "golden-scenarios-v0.yaml").write_text(
        f"""
schema_version: "golden-scenarios-v0"
suite_policy:
  seed_count: 1
  minimum_before_domain_planner_acceptance: 50
scenarios:
  - id: "GS-T1"
    input_text: "SECRET RAW COMMAND"
    context_fixture_id: "ctx-secret"
    expected_intent: "create_task"
    expected_decision_outcome: "{expected_outcome}"
    expected_entities:
      task_title: "SECRET TASK TITLE"
      items:
        - name: "SECRET ITEM"
    expected_actions:
      - action_type: "create_task"
        title: "SECRET TASK TITLE"
""".lstrip(),
        encoding="utf-8",
    )
    (source_dir / "context-fixtures-v0.yaml").write_text(
        """
schema_version: "golden-context-v0"
timezone: "Europe/Moscow"
reference_instant: "2026-06-15T12:00:00+03:00"
contexts:
  - id: "ctx-secret"
    household:
      household_id: "house-secret"
      name: "SECRET HOUSE"
    requester:
      user_id: "user-secret"
      display_name: "SECRET MEMBER"
    members:
      - user_id: "user-secret"
        display_name: "SECRET MEMBER"
        role: "admin"
        workload_score: 1
    zones:
      - zone_id: "zone-secret"
        name: "SECRET ZONE"
    shopping_lists:
      - list_id: "list-secret"
        name: "SECRET LIST"
    defaults:
      default_assignee_id: "user-secret"
      default_list_id: "list-secret"
    policies:
      max_open_tasks_per_user: 10
      quiet_hours: "23:00-07:00"
""".lstrip(),
        encoding="utf-8",
    )


def _decision(command: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "decision_id": "dec-test",
        "command_id": command["command_id"],
        "status": "ok",
        "action": "start_job",
        "confidence": 0.9,
        "payload": {
            "job_id": "job-test",
            "job_type": "create_task",
            "proposed_actions": [
                {
                    "action": "propose_create_task",
                    "payload": {
                        "task": {
                            "title": "SECRET RAW COMMAND",
                            "assignee_id": "user-secret",
                        }
                    },
                }
            ],
        },
        "explanation": "test",
        "trace_id": "trace-test",
        "schema_version": "2.0.0",
        "decision_version": "test-planner",
        "created_at": "2026-06-15T12:00:00Z",
    }


def test_report_uses_source_metadata_and_scenario_ids(tmp_path: Path) -> None:
    source_dir = tmp_path / "seed"
    _write_seed_files(source_dir)

    report = eval_seed.build_report(
        source_dir=source_dir,
        source_revision="rev-test",
        planner_version="planner-test",
        decide_fn=_decision,
    )

    assert report["source"]["revision"] == "rev-test"
    assert report["source"]["fixture_versions"]["scenarios"] == "golden-scenarios-v0"
    assert report["source"]["fixture_versions"]["contexts"] == "golden-context-v0"
    assert report["source"]["scenario_count"] == 1
    assert report["source"]["context_count"] == 1
    assert report["run"]["planner_version"] == "planner-test"
    assert report["results"][0]["scenario_id"] == "GS-T1"
    assert "input_text" not in report["results"][0]
    assert "text" not in report["results"][0]


def test_report_does_not_emit_raw_fixture_text(tmp_path: Path) -> None:
    source_dir = tmp_path / "seed"
    _write_seed_files(source_dir)

    report = eval_seed.build_report(source_dir=source_dir, decide_fn=_decision)
    report_text = json.dumps(report, ensure_ascii=False)

    for forbidden in (
        "SECRET RAW COMMAND",
        "SECRET ITEM",
        "SECRET MEMBER",
        "SECRET ZONE",
        "SECRET LIST",
        "SECRET TASK TITLE",
    ):
        assert forbidden not in report_text

    eval_seed.assert_no_sensitive_output(report_text, source_dir)


def test_failure_buckets_capture_unsupported_auto_execute(tmp_path: Path) -> None:
    source_dir = tmp_path / "seed"
    _write_seed_files(source_dir, expected_outcome="reject")

    report = eval_seed.build_report(source_dir=source_dir, decide_fn=_decision)
    result = report["results"][0]

    assert result["actual_outcome"] == "execute"
    assert "wrong_outcome" in result["failure_buckets"]
    assert "unsupported_auto_execute" in result["failure_buckets"]
    assert "unsafe_assignment_not_rejected" in result["failure_buckets"]
    assert report["metrics"]["blocker_failure_scenarios"] == 1


def test_context_inheritance_removes_disallowed_null_defaults(tmp_path: Path) -> None:
    source_dir = tmp_path / "seed"
    _write_seed_files(source_dir)
    (source_dir / "context-fixtures-v0.yaml").write_text(
        """
schema_version: "golden-context-v0"
contexts:
  - id: "base"
    household:
      household_id: "house"
    requester:
      user_id: "u1"
    members:
      - user_id: "u1"
    defaults:
      default_assignee_id: "u1"
      default_list_id: "list-1"
  - id: "ctx-secret"
    extends: "base"
    shopping_lists: []
    defaults:
      default_assignee_id: "u1"
      default_list_id: null
""".lstrip(),
        encoding="utf-8",
    )

    seed = eval_seed.load_seed_source(source_dir)
    command_context = eval_seed.command_context_from_hometusk(seed["contexts"]["ctx-secret"])

    assert "default_list_id" not in command_context["defaults"]
    assert "shopping_lists" not in command_context["household"]
