#!/usr/bin/env python3
"""Shadow router golden-dataset analyzer.

Privacy: never print raw user text or LLM output.
Only aggregated numeric metrics in report.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List

DANGEROUS_FIELDS = {
    "text",
    "question",
    "item_name",
    "ui_message",
    "raw",
    "output",
    "prompt",
    "normalized_text",
}


@dataclass(frozen=True)
class GoldenEntry:
    command_id: str
    expected_intent: str
    expected_entity_keys: list[str]


@dataclass
class MetricsReport:
    total_records: int = 0
    matched_records: int = 0
    intent_match_rate: float | None = None
    entity_hit_rate: float | None = None
    latency_p50: int | None = None
    latency_p95: int | None = None
    error_breakdown: dict[str, int] = field(default_factory=dict)
    parse_errors: int = 0


def load_golden_dataset(path: Path) -> dict[str, GoldenEntry]:
    """Read golden_dataset.json, return dict keyed by command_id."""
    data = json.loads(path.read_text(encoding="utf-8"))
    result = {}
    for entry in data:
        result[entry["command_id"]] = GoldenEntry(
            command_id=entry["command_id"],
            expected_intent=entry["expected_intent"],
            expected_entity_keys=entry.get("expected_entity_keys", []),
        )
    return result


def iter_shadow_log(path: Path) -> Iterable[tuple[dict[str, Any], bool]]:
    """Yield (record, ok) tuples from JSONL. ok=False on parse error."""
    if not path.exists() or not path.is_file():
        return
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line), True
            except (json.JSONDecodeError, ValueError):
                yield {}, False


def compute_metrics(
    records: list[dict[str, Any]],
    golden: dict[str, GoldenEntry],
) -> MetricsReport:
    """Compute metrics from JSONL records matched against golden dataset."""
    report = MetricsReport()
    report.total_records = len(records)

    latencies: list[int] = []
    intent_matches = 0
    entity_matches = 0
    matched = 0

    for rec in records:
        # Collect latency from ALL records
        lat = rec.get("latency_ms")
        if isinstance(lat, (int, float)):
            latencies.append(int(lat))

        # Collect errors from ALL records
        err = rec.get("error_type")
        if isinstance(err, str) and err:
            report.error_breakdown[err] = report.error_breakdown.get(err, 0) + 1

        # Match against golden dataset
        cid = rec.get("command_id")
        if not isinstance(cid, str) or cid not in golden:
            continue
        matched += 1
        entry = golden[cid]

        # Intent match
        suggested = rec.get("suggested_intent")
        if suggested == entry.expected_intent:
            intent_matches += 1

        # Entity key match
        es = rec.get("entities_summary")
        actual_keys = sorted(es.get("keys", [])) if isinstance(es, dict) else []
        expected_keys = sorted(entry.expected_entity_keys)
        if actual_keys == expected_keys:
            entity_matches += 1

    report.matched_records = matched
    if matched > 0:
        report.intent_match_rate = intent_matches / matched
        report.entity_hit_rate = entity_matches / matched
    if latencies:
        report.latency_p50 = _percentile(latencies, 0.50)
        report.latency_p95 = _percentile(latencies, 0.95)

    return report


def _percentile(values: list[int], p: float) -> int:
    """Index-based percentile (same pattern as metrics_agent_hints_v0.py)."""
    if not values:
        return 0
    s = sorted(values)
    idx = int((len(s) - 1) * p)
    return s[idx]


def format_report_json(report: MetricsReport) -> dict[str, Any]:
    """Convert report to JSON-serializable dict."""
    return {
        "total_records": report.total_records,
        "matched_records": report.matched_records,
        "intent_match_rate": report.intent_match_rate,
        "entity_hit_rate": report.entity_hit_rate,
        "latency_p50": report.latency_p50,
        "latency_p95": report.latency_p95,
        "error_breakdown": report.error_breakdown,
        "parse_errors": report.parse_errors,
    }


def format_report_human(report: MetricsReport) -> str:
    """Human-readable text summary."""
    lines = [
        "=== Shadow Router Analyzer Report ===",
        f"Total records:      {report.total_records}",
        f"Matched records:    {report.matched_records}",
        f"Intent match rate:  {_fmt_rate(report.intent_match_rate)}",
        f"Entity hit rate:    {_fmt_rate(report.entity_hit_rate)}",
        f"Latency p50:        {_fmt_ms(report.latency_p50)}",
        f"Latency p95:        {_fmt_ms(report.latency_p95)}",
        f"Parse errors:       {report.parse_errors}",
    ]
    if report.error_breakdown:
        lines.append("Error breakdown:")
        for etype, count in sorted(report.error_breakdown.items()):
            lines.append(f"  {etype}: {count}")
    else:
        lines.append("Error breakdown:    (none)")
    return "\n".join(lines)


def _fmt_rate(v: float | None) -> str:
    return "n/a" if v is None else f"{v:.4f}"


def _fmt_ms(v: int | None) -> str:
    return "n/a" if v is None else f"{v} ms"


def run_self_test() -> None:
    """Privacy self-test: ensure no raw text leaks into report output."""
    SECRET = "ТЕСТОВЫЙ_СЕКРЕТ_XYZ_12345"
    record = {
        "timestamp": "2026-01-01T00:00:00+00:00",
        "trace_id": "trace-self-test",
        "command_id": "cmd-self-test",
        "router_version": "shadow-router-0.1",
        "router_strategy": "v2",
        "status": "ok",
        "latency_ms": 99,
        "error_type": None,
        "suggested_intent": "add_shopping_item",
        "missing_fields": None,
        "clarify_question": SECRET,
        "entities_summary": {"keys": ["item"], "counts": {"item": 1}},
        "confidence": 0.8,
        "model_meta": {"profile": "cheap", "task_id": SECRET},
        "baseline_intent": "add_shopping_item",
        "baseline_action": None,
        "baseline_job_type": None,
    }
    golden_data = [
        {
            "command_id": "cmd-self-test",
            "fixture_file": "self_test.json",
            "expected_intent": "add_shopping_item",
            "expected_entity_keys": ["item"],
            "notes": "self-test entry",
        }
    ]

    with tempfile.TemporaryDirectory() as td:
        log_path = Path(td) / "shadow.jsonl"
        golden_path = Path(td) / "golden.json"
        log_path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
        golden_path.write_text(json.dumps(golden_data, ensure_ascii=False), encoding="utf-8")

        golden = load_golden_dataset(golden_path)
        records = [r for r, ok in iter_shadow_log(log_path) if ok]
        report = compute_metrics(records, golden)

        json_text = json.dumps(format_report_json(report), ensure_ascii=False)
        human_text = format_report_human(report)

        for output_text in (json_text, human_text):
            if SECRET in output_text:
                print("FAIL: self-test detected secret leak in output", file=sys.stderr)
                sys.exit(1)

    print("self-test ok")


def main() -> None:
    parser = argparse.ArgumentParser(description="Shadow router golden-dataset analyzer")
    parser.add_argument(
        "--shadow-log",
        type=Path,
        default=Path("logs/shadow_router.jsonl"),
        help="Path to shadow router JSONL log",
    )
    parser.add_argument(
        "--golden-dataset",
        type=Path,
        default=Path("skills/graph-sanity/fixtures/golden_dataset.json"),
        help="Path to golden dataset manifest",
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

    golden = load_golden_dataset(args.golden_dataset)
    all_records = []
    parse_errors = 0
    for rec, ok in iter_shadow_log(args.shadow_log):
        if ok:
            all_records.append(rec)
        else:
            parse_errors += 1

    report = compute_metrics(all_records, golden)
    report.parse_errors = parse_errors

    print(format_report_human(report))

    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(format_report_json(report), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"\nJSON report written to: {args.output_json}")


if __name__ == "__main__":
    main()
