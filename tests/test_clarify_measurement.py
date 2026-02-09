"""Unit tests for clarify quality measurement script (ST-014)."""

import json
import os
from pathlib import Path

from scripts.analyze_clarify_quality import (
    ClarifyReport,
    FixtureResult,
    compute_report,
    format_report_human,
    format_report_json,
    load_expected_manifest,
    load_fixtures_with_expected,
    run_fixture,
)


FIXTURES_DIR = Path(__file__).resolve().parents[1] / "skills" / "graph-sanity" / "fixtures" / "commands"
MANIFEST_PATH = FIXTURES_DIR.parent / "clarify_expected.json"


def _make_fixture(action, missing_fields=None, text="тест", command_id="cmd-test"):
    fixture = {
        "command_id": command_id,
        "user_id": "user-test",
        "timestamp": "2026-01-01T00:00:00+00:00",
        "text": text,
        "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
        "context": {"household": {"members": [{"user_id": "user-test"}]}},
        "_expected": {"action": action},
        "_fixture_file": "test_fixture.json",
    }
    if missing_fields is not None:
        fixture["_expected"]["missing_fields"] = missing_fields
    return fixture


class _StubRouter:
    """Stub router that returns a predetermined decision."""

    def __init__(self, action, missing_fields=None):
        self._action = action
        self._missing_fields = missing_fields

    def decide(self, command):
        payload = {"question": "stub question"}
        if self._missing_fields is not None:
            payload["missing_fields"] = self._missing_fields
        return {
            "action": self._action,
            "status": self._action,
            "payload": payload,
        }


def test_run_fixture_action_match():
    """Action match when actual matches expected."""
    fixture = _make_fixture("clarify", ["intent"])
    router = _StubRouter("clarify", ["intent"])
    result = run_fixture(router, fixture)
    assert result.action_match is True
    assert result.missing_fields_match is True


def test_run_fixture_action_mismatch():
    """Action mismatch detected."""
    fixture = _make_fixture("clarify", ["intent"])
    router = _StubRouter("start_job")
    result = run_fixture(router, fixture)
    assert result.action_match is False


def test_run_fixture_missing_fields_mismatch():
    """Missing fields mismatch when sets differ."""
    fixture = _make_fixture("clarify", ["intent"])
    router = _StubRouter("clarify", ["text"])
    result = run_fixture(router, fixture)
    assert result.action_match is True
    assert result.missing_fields_match is False


def test_run_fixture_missing_fields_none_vs_expected():
    """Missing fields mismatch when actual is None but expected is set."""
    fixture = _make_fixture("clarify", ["intent"])
    router = _StubRouter("clarify", None)
    result = run_fixture(router, fixture)
    assert result.action_match is True
    assert result.missing_fields_match is False


def test_run_fixture_start_job_no_missing_fields_check():
    """Start_job fixtures skip missing_fields comparison."""
    fixture = _make_fixture("start_job")
    router = _StubRouter("start_job")
    result = run_fixture(router, fixture)
    assert result.action_match is True
    assert result.missing_fields_match is True


def test_compute_report_rates():
    """Report computes correct match rates."""
    fixtures = [
        _make_fixture("clarify", ["text"], text="   ", command_id="cmd-1"),
        _make_fixture("clarify", ["intent"], text="абв", command_id="cmd-2"),
        _make_fixture("start_job", text="Купи молоко", command_id="cmd-3"),
    ]
    router = _StubRouter("clarify", ["text"])
    report = compute_report("test", router, fixtures)

    assert report.annotated_fixtures == 3
    assert report.clarify_fixtures == 2
    # action: clarify matches 2/3 (stub always returns clarify, but fixture 3 expects start_job)
    assert report.action_matches == 2
    assert report.action_match_rate == 2 / 3
    # missing_fields: ["text"] matches fixture 1 but not fixture 2 (["intent"])
    assert report.missing_fields_matches == 1
    assert report.missing_fields_match_rate == 1 / 2


def test_format_report_json_no_raw_text():
    """JSON report contains no raw user text."""
    secret = "СЕКРЕТНЫЙ_ТЕКСТ_XYZ"
    fixture = _make_fixture("clarify", ["intent"], text=secret)
    router = _StubRouter("clarify", ["intent"])
    report = compute_report("test", router, [fixture])
    json_str = json.dumps(format_report_json(report), ensure_ascii=False)
    assert secret not in json_str


def test_format_report_human_no_raw_text():
    """Human report contains no raw user text."""
    secret = "СЕКРЕТНЫЙ_ТЕКСТ_ABC"
    fixture = _make_fixture("clarify", ["intent"], text=secret)
    router = _StubRouter("clarify", ["intent"])
    report = compute_report("test", router, [fixture])
    human_str = format_report_human(report)
    assert secret not in human_str


def test_load_expected_manifest():
    """Manifest loads and keys by command_id."""
    manifest = load_expected_manifest(MANIFEST_PATH)
    assert len(manifest) >= 5
    assert "cmd-wp000-005" in manifest
    assert manifest["cmd-wp000-005"]["expected_action"] == "clarify"


def test_load_fixtures_with_expected():
    """Fixtures matched with manifest have _expected attached."""
    manifest = load_expected_manifest(MANIFEST_PATH)
    fixtures = load_fixtures_with_expected(FIXTURES_DIR, manifest)
    assert len(fixtures) >= 5
    for f in fixtures:
        assert "_expected" in f
        assert "action" in f["_expected"]
        # Fixture itself must NOT have 'expected' key (clean CommandDTO)
        assert "expected" not in f
