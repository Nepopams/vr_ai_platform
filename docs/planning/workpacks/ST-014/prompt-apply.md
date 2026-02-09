# Codex APPLY Prompt — ST-014: Clarify Golden Dataset Ground Truth and Quality Measurement

## Role

You are an implementation agent. Apply changes exactly as specified below.

## Environment

- Python binary: `python3` (NOT `python`)
- All tests: `python3 -m pytest tests/ -v`

## STOP-THE-LINE

If any instruction contradicts what you see in the codebase, STOP and report.

---

## Context

Implementing ST-014: Add ground truth annotations to golden fixtures, create 2 new clarify edge-case fixtures, and build a measurement script.

**PLAN findings confirmed:**
- empty_text.json: text="   " → V1 & V2: action=clarify, missing_fields=["text"]
- unknown_intent.json: text="Что-то непонятное про погоду" → V2: missing_fields=["intent"], V1: missing_fields=None (V1 doesn't pass missing_fields for this trigger)
- minimal_context.json: text="Сделай что-нибудь полезное" → "сделай" matches TASK_KEYWORDS → create_task → start_job (NOT clarify!)
- build_clarify_decision: missing_fields in payload only if truthy (line 139)
- V1 (process_command line 193): no missing_fields for "no capability" trigger
- V2 (validate_and_build line 146): missing_fields=["capability.start_job"] for "no capability" trigger
- 14 fixtures total, no existing `expected` annotations
- Analyzer scripts follow argparse + dataclass + self-test pattern

---

## Step 1: Add `expected` annotation to `skills/graph-sanity/fixtures/commands/empty_text.json`

Replace the entire file with:
```json
{
  "command_id": "cmd-wp000-005",
  "user_id": "user-205",
  "timestamp": "2026-02-01T10:04:00+00:00",
  "text": "   ",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-205",
      "members": [{"user_id": "user-205", "display_name": "Коля"}]
    }
  },
  "expected": {
    "action": "clarify",
    "missing_fields": ["text"]
  }
}
```

---

## Step 2: Add `expected` annotation to `skills/graph-sanity/fixtures/commands/unknown_intent.json`

Replace the entire file with:
```json
{
  "command_id": "cmd-wp000-006",
  "user_id": "user-206",
  "timestamp": "2026-02-01T10:05:00+00:00",
  "text": "Что-то непонятное про погоду",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-206",
      "members": [{"user_id": "user-206", "display_name": "Саша"}]
    }
  },
  "expected": {
    "action": "clarify",
    "missing_fields": ["intent"]
  }
}
```

---

## Step 3: Add `expected` annotation to `skills/graph-sanity/fixtures/commands/minimal_context.json`

**NOTE:** "Сделай что-нибудь полезное" → "сделай" matches TASK_KEYWORDS → intent=create_task → start_job. This is NOT a clarify fixture.

Replace the entire file with:
```json
{
  "command_id": "cmd-wp000-007",
  "user_id": "user-207",
  "timestamp": "2026-02-01T10:06:00+00:00",
  "text": "Сделай что-нибудь полезное",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "members": [{"user_id": "user-207"}]
    }
  },
  "expected": {
    "action": "start_job"
  }
}
```

---

## Step 4: Create `skills/graph-sanity/fixtures/commands/clarify_partial_shopping.json`

Create this NEW file. Text "Купи" matches shopping intent but no item name extractable → clarify.

```json
{
  "command_id": "cmd-wp000-015",
  "user_id": "user-215",
  "timestamp": "2026-02-01T10:14:00+00:00",
  "text": "Купи",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-215",
      "members": [{"user_id": "user-215", "display_name": "Марина"}],
      "shopping_lists": [{"list_id": "list-1", "name": "Продукты"}]
    },
    "defaults": {"default_list_id": "list-1"}
  },
  "expected": {
    "action": "clarify",
    "missing_fields": ["item.name"]
  }
}
```

---

## Step 5: Create `skills/graph-sanity/fixtures/commands/clarify_ambiguous_intent.json`

Create this NEW file. Text "Это очень важно" matches no intent keywords → clarify_needed.

```json
{
  "command_id": "cmd-wp000-016",
  "user_id": "user-216",
  "timestamp": "2026-02-01T10:15:00+00:00",
  "text": "Это очень важно",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-216",
      "members": [{"user_id": "user-216", "display_name": "Олег"}]
    }
  },
  "expected": {
    "action": "clarify",
    "missing_fields": ["intent"]
  }
}
```

---

## Step 6: Create `scripts/analyze_clarify_quality.py`

Create this NEW file with the following exact content:

```python
#!/usr/bin/env python3
"""Clarify quality measurement across golden dataset fixtures.

Runs each annotated fixture through V1 and V2 routers, compares actual
decision against expected ground truth.  Reports action match rate and
missing_fields match rate.

Privacy: never print raw user text or LLM output.
Only aggregated numeric metrics in report.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class FixtureResult:
    fixture_file: str
    command_id: str
    expected_action: str
    expected_missing_fields: Optional[List[str]]
    actual_action: str
    actual_missing_fields: Optional[List[str]]
    action_match: bool
    missing_fields_match: bool


@dataclass
class ClarifyReport:
    router_version: str = ""
    total_fixtures: int = 0
    annotated_fixtures: int = 0
    action_matches: int = 0
    action_match_rate: Optional[float] = None
    clarify_fixtures: int = 0
    missing_fields_matches: int = 0
    missing_fields_match_rate: Optional[float] = None
    results: List[FixtureResult] = field(default_factory=list)


def load_annotated_fixtures(fixtures_dir: Path) -> List[Dict[str, Any]]:
    """Load all fixture JSON files that have an 'expected' annotation."""
    annotated = []
    for path in sorted(fixtures_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if "expected" in data:
            data["_fixture_file"] = path.name
            annotated.append(data)
    return annotated


def run_fixture(
    router,
    fixture: Dict[str, Any],
) -> FixtureResult:
    """Run a single fixture through a router and compare against expected."""
    expected = fixture["expected"]
    expected_action = expected["action"]
    expected_mf = expected.get("missing_fields")

    decision = router.decide(fixture)
    actual_action = decision.get("action", "")
    actual_mf = decision.get("payload", {}).get("missing_fields")

    action_match = actual_action == expected_action

    if expected_action != "clarify" or expected_mf is None:
        mf_match = True
    else:
        actual_set = set(actual_mf) if actual_mf else set()
        expected_set = set(expected_mf)
        mf_match = actual_set == expected_set

    return FixtureResult(
        fixture_file=fixture.get("_fixture_file", ""),
        command_id=fixture.get("command_id", ""),
        expected_action=expected_action,
        expected_missing_fields=expected_mf,
        actual_action=actual_action,
        actual_missing_fields=actual_mf,
        action_match=action_match,
        missing_fields_match=mf_match,
    )


def compute_report(
    router_version: str,
    router,
    fixtures: List[Dict[str, Any]],
) -> ClarifyReport:
    """Compute quality report for a router across all annotated fixtures."""
    report = ClarifyReport(router_version=router_version)
    report.annotated_fixtures = len(fixtures)

    for fixture in fixtures:
        report.total_fixtures += 1
        result = run_fixture(router, fixture)
        report.results.append(result)

        if result.action_match:
            report.action_matches += 1

        if result.expected_action == "clarify" and result.expected_missing_fields is not None:
            report.clarify_fixtures += 1
            if result.missing_fields_match:
                report.missing_fields_matches += 1

    if report.annotated_fixtures > 0:
        report.action_match_rate = report.action_matches / report.annotated_fixtures
    if report.clarify_fixtures > 0:
        report.missing_fields_match_rate = report.missing_fields_matches / report.clarify_fixtures

    return report


def format_report_json(report: ClarifyReport) -> Dict[str, Any]:
    """Convert report to JSON-serializable dict (no raw text)."""
    return {
        "router_version": report.router_version,
        "total_fixtures": report.total_fixtures,
        "annotated_fixtures": report.annotated_fixtures,
        "action_matches": report.action_matches,
        "action_match_rate": report.action_match_rate,
        "clarify_fixtures": report.clarify_fixtures,
        "missing_fields_matches": report.missing_fields_matches,
        "missing_fields_match_rate": report.missing_fields_match_rate,
        "per_fixture": [
            {
                "fixture_file": r.fixture_file,
                "action_match": r.action_match,
                "missing_fields_match": r.missing_fields_match,
            }
            for r in report.results
        ],
    }


def format_report_human(report: ClarifyReport) -> str:
    """Human-readable text summary (no raw text)."""
    lines = [
        f"=== Clarify Quality Report ({report.router_version}) ===",
        f"Annotated fixtures:       {report.annotated_fixtures}",
        f"Action match rate:        {_fmt_rate(report.action_match_rate)}",
        f"Clarify fixtures:         {report.clarify_fixtures}",
        f"Missing fields match:     {_fmt_rate(report.missing_fields_match_rate)}",
    ]
    lines.append("Per fixture:")
    for r in report.results:
        status = "OK" if (r.action_match and r.missing_fields_match) else "MISMATCH"
        lines.append(f"  {r.fixture_file}: {status}")
    return "\n".join(lines)


def _fmt_rate(v: Optional[float]) -> str:
    return "n/a" if v is None else f"{v:.4f}"


def run_self_test() -> None:
    """Privacy self-test: ensure no raw text leaks into report output."""
    import tempfile

    SECRET = "ТЕСТОВЫЙ_СЕКРЕТ_CQ_12345"

    fixture = {
        "command_id": "cmd-self-test",
        "user_id": "user-self-test",
        "timestamp": "2026-01-01T00:00:00+00:00",
        "text": SECRET,
        "capabilities": ["start_job", "clarify"],
        "context": {"household": {"members": []}},
        "expected": {"action": "clarify", "missing_fields": ["intent"]},
        "_fixture_file": "self_test.json",
    }

    result = FixtureResult(
        fixture_file="self_test.json",
        command_id="cmd-self-test",
        expected_action="clarify",
        expected_missing_fields=["intent"],
        actual_action="clarify",
        actual_missing_fields=["intent"],
        action_match=True,
        missing_fields_match=True,
    )

    report = ClarifyReport(
        router_version="self-test",
        total_fixtures=1,
        annotated_fixtures=1,
        action_matches=1,
        action_match_rate=1.0,
        clarify_fixtures=1,
        missing_fields_matches=1,
        missing_fields_match_rate=1.0,
        results=[result],
    )

    json_text = json.dumps(format_report_json(report), ensure_ascii=False)
    human_text = format_report_human(report)

    for output_text in (json_text, human_text):
        if SECRET in output_text:
            print("FAIL: self-test detected secret leak in output", file=sys.stderr)
            sys.exit(1)

    print("self-test ok")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clarify quality measurement across golden dataset fixtures"
    )
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        default=Path("skills/graph-sanity/fixtures/commands"),
        help="Path to fixtures directory",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=None,
        help="Write JSON report to this file",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run privacy self-test and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    # Disable LLM features for deterministic measurement
    os.environ.setdefault("ASSIST_MODE_ENABLED", "false")
    os.environ.setdefault("SHADOW_ROUTER_ENABLED", "false")

    from routers.v1 import RouterV1Adapter
    from routers.v2 import RouterV2Pipeline

    fixtures = load_annotated_fixtures(args.fixtures_dir)
    if not fixtures:
        print("No annotated fixtures found.")
        return

    for label, router in [("V1", RouterV1Adapter()), ("V2", RouterV2Pipeline())]:
        report = compute_report(label, router, fixtures)
        print(format_report_human(report))
        print()

        if args.output_json is not None:
            out = args.output_json.parent / f"{args.output_json.stem}_{label}{args.output_json.suffix}"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(
                json.dumps(format_report_json(report), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"JSON report written to: {out}")


if __name__ == "__main__":
    main()
```

---

## Step 7: Create `tests/test_clarify_measurement.py`

Create this NEW file with the following exact content:

```python
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
    load_annotated_fixtures,
    run_fixture,
)


FIXTURES_DIR = Path(__file__).resolve().parents[1] / "skills" / "graph-sanity" / "fixtures" / "commands"


def _make_fixture(action, missing_fields=None, text="тест", command_id="cmd-test"):
    fixture = {
        "command_id": command_id,
        "user_id": "user-test",
        "timestamp": "2026-01-01T00:00:00+00:00",
        "text": text,
        "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
        "context": {"household": {"members": [{"user_id": "user-test"}]}},
        "expected": {"action": action},
        "_fixture_file": "test_fixture.json",
    }
    if missing_fields is not None:
        fixture["expected"]["missing_fields"] = missing_fields
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


def test_load_annotated_fixtures_filters():
    """load_annotated_fixtures returns only fixtures with 'expected' key."""
    fixtures = load_annotated_fixtures(FIXTURES_DIR)
    # After ST-014, at least 5 fixtures have expected annotations
    assert len(fixtures) >= 5
    for f in fixtures:
        assert "expected" in f


def test_load_annotated_fixtures_all_have_action():
    """All annotated fixtures have expected.action."""
    fixtures = load_annotated_fixtures(FIXTURES_DIR)
    for f in fixtures:
        assert "action" in f["expected"]
```

---

## Verification

Run ALL tests after completing all steps:

```bash
# 1. New tests
python3 -m pytest tests/test_clarify_measurement.py -v

# 2. Full test suite
python3 -m pytest tests/ -v

# 3. Script self-test
python3 scripts/analyze_clarify_quality.py --self-test

# 4. No secrets
grep -rn 'sk-\|api_key' scripts/analyze_clarify_quality.py tests/test_clarify_measurement.py skills/graph-sanity/fixtures/commands/clarify_*.json
```

Expected: ALL tests pass, no secrets, self-test ok.

---

## Files summary

| File | Action |
|------|--------|
| `skills/graph-sanity/fixtures/commands/empty_text.json` | Add `expected` annotation (Step 1) |
| `skills/graph-sanity/fixtures/commands/unknown_intent.json` | Add `expected` annotation (Step 2) |
| `skills/graph-sanity/fixtures/commands/minimal_context.json` | Add `expected` annotation (Step 3) |
| `skills/graph-sanity/fixtures/commands/clarify_partial_shopping.json` | Create new fixture (Step 4) |
| `skills/graph-sanity/fixtures/commands/clarify_ambiguous_intent.json` | Create new fixture (Step 5) |
| `scripts/analyze_clarify_quality.py` | Create new script (Step 6) |
| `tests/test_clarify_measurement.py` | Create new test file (Step 7) |

## Invariants (DO NOT break)

- `routers/v2.py` — NOT modified
- `routers/assist/runner.py` — NOT modified
- `graphs/core_graph.py` — NOT modified
- `contracts/schemas/` — NOT modified
- Existing fixture JSON structure (command fields) — NOT changed, only `expected` key added
- Existing tests — NOT modified
- No raw user text in script output (privacy)
