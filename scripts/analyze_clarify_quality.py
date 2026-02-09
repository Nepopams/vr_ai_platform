#!/usr/bin/env python3
"""Clarify quality measurement across golden dataset fixtures.

Runs each annotated fixture through V1 and V2 routers, compares actual
decision against expected ground truth from a separate manifest file.
Reports action match rate and missing_fields match rate.

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


def load_expected_manifest(manifest_path: Path) -> Dict[str, Dict[str, Any]]:
    """Load expected manifest, return dict keyed by command_id."""
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {entry["command_id"]: entry for entry in data}


def load_fixtures_with_expected(
    fixtures_dir: Path,
    manifest: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Load fixture JSON files that have a matching entry in the manifest."""
    matched = []
    for path in sorted(fixtures_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        command_id = data.get("command_id")
        if command_id and command_id in manifest:
            entry = manifest[command_id]
            data["_expected"] = {
                "action": entry["expected_action"],
            }
            mf = entry.get("expected_missing_fields")
            if mf is not None:
                data["_expected"]["missing_fields"] = mf
            data["_fixture_file"] = path.name
            matched.append(data)
    return matched


def run_fixture(
    router,
    fixture: Dict[str, Any],
) -> FixtureResult:
    """Run a single fixture through a router and compare against expected."""
    expected = fixture["_expected"]
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
    SECRET = "ТЕСТОВЫЙ_СЕКРЕТ_CQ_12345"

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
        "--manifest",
        type=Path,
        default=None,
        help="Path to expected manifest JSON (default: <fixtures-dir>/clarify_expected.json)",
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

    manifest_path = args.manifest or (args.fixtures_dir.parent / "clarify_expected.json")
    manifest = load_expected_manifest(manifest_path)
    fixtures = load_fixtures_with_expected(args.fixtures_dir, manifest)
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
