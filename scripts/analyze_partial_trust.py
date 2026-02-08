#!/usr/bin/env python3
"""Partial trust risk-log regression metrics analyzer.

Privacy: never print raw user text or LLM output.
Only aggregated numeric metrics in report.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List


@dataclass
class MetricsReport:
    total_records: int = 0
    sampled_records: int = 0
    status_breakdown: dict[str, int] = field(default_factory=dict)
    reason_code_breakdown: dict[str, int] = field(default_factory=dict)
    acceptance_rate: float | None = None
    intent_mismatch_rate: float | None = None
    entity_key_mismatch_rate: float | None = None
    latency_p50: int | None = None
    latency_p95: int | None = None
    error_rate: float | None = None
    parse_errors: int = 0


def iter_risk_log(path: Path) -> Iterable[tuple[dict[str, Any], bool]]:
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


def compute_metrics(records: list[dict[str, Any]]) -> MetricsReport:
    """Compute regression metrics from risk-log records."""
    report = MetricsReport()
    report.total_records = len(records)

    latencies: list[int] = []
    accepted_count = 0
    fallback_count = 0
    error_count = 0
    intent_mismatch_total = 0
    entity_mismatch_total = 0
    diff_records = 0

    for rec in records:
        # Status breakdown
        status = rec.get("status", "unknown")
        report.status_breakdown[status] = report.status_breakdown.get(status, 0) + 1

        # Reason code breakdown
        reason = rec.get("reason_code")
        if isinstance(reason, str) and reason:
            report.reason_code_breakdown[reason] = report.reason_code_breakdown.get(reason, 0) + 1

        # Count by status type
        if status == "accepted_llm":
            accepted_count += 1
        elif status == "fallback_deterministic":
            fallback_count += 1
        elif status == "error":
            error_count += 1

        # Sampled records
        if rec.get("sampled") is True:
            report.sampled_records += 1

        # Latency (only for records with latency_ms)
        lat = rec.get("latency_ms")
        if isinstance(lat, (int, float)):
            latencies.append(int(lat))

        # Diff summary analysis (only for records that have it)
        diff = rec.get("diff_summary")
        if isinstance(diff, dict):
            diff_records += 1
            if diff.get("intent_mismatch") is True:
                intent_mismatch_total += 1
            if diff.get("entity_key_mismatch") is True:
                entity_mismatch_total += 1

    # Compute rates
    decision_total = accepted_count + fallback_count
    if decision_total > 0:
        report.acceptance_rate = accepted_count / decision_total

    if diff_records > 0:
        report.intent_mismatch_rate = intent_mismatch_total / diff_records
        report.entity_key_mismatch_rate = entity_mismatch_total / diff_records

    if report.total_records > 0:
        report.error_rate = error_count / report.total_records

    if latencies:
        report.latency_p50 = _percentile(latencies, 0.50)
        report.latency_p95 = _percentile(latencies, 0.95)

    return report


def _percentile(values: list[int], p: float) -> int:
    """Index-based percentile (same pattern as analyze_shadow_router.py)."""
    if not values:
        return 0
    s = sorted(values)
    idx = int((len(s) - 1) * p)
    return s[idx]


def format_report_json(report: MetricsReport) -> dict[str, Any]:
    """Convert report to JSON-serializable dict."""
    return {
        "total_records": report.total_records,
        "sampled_records": report.sampled_records,
        "status_breakdown": report.status_breakdown,
        "reason_code_breakdown": report.reason_code_breakdown,
        "acceptance_rate": report.acceptance_rate,
        "intent_mismatch_rate": report.intent_mismatch_rate,
        "entity_key_mismatch_rate": report.entity_key_mismatch_rate,
        "latency_p50": report.latency_p50,
        "latency_p95": report.latency_p95,
        "error_rate": report.error_rate,
        "parse_errors": report.parse_errors,
    }


def format_report_human(report: MetricsReport) -> str:
    """Human-readable text summary."""
    lines = [
        "=== Partial Trust Risk-Log Analyzer Report ===",
        f"Total records:           {report.total_records}",
        f"Sampled records:         {report.sampled_records}",
        f"Acceptance rate:         {_fmt_rate(report.acceptance_rate)}",
        f"Intent mismatch rate:    {_fmt_rate(report.intent_mismatch_rate)}",
        f"Entity key mismatch:     {_fmt_rate(report.entity_key_mismatch_rate)}",
        f"Error rate:              {_fmt_rate(report.error_rate)}",
        f"Latency p50:             {_fmt_ms(report.latency_p50)}",
        f"Latency p95:             {_fmt_ms(report.latency_p95)}",
        f"Parse errors:            {report.parse_errors}",
    ]
    if report.status_breakdown:
        lines.append("Status breakdown:")
        for status, count in sorted(report.status_breakdown.items()):
            lines.append(f"  {status}: {count}")
    else:
        lines.append("Status breakdown:        (none)")
    if report.reason_code_breakdown:
        lines.append("Reason code breakdown:")
        for reason, count in sorted(report.reason_code_breakdown.items()):
            lines.append(f"  {reason}: {count}")
    else:
        lines.append("Reason code breakdown:   (none)")
    return "\n".join(lines)


def _fmt_rate(v: float | None) -> str:
    return "n/a" if v is None else f"{v:.4f}"


def _fmt_ms(v: int | None) -> str:
    return "n/a" if v is None else f"{v} ms"


def run_self_test() -> None:
    """Privacy self-test: ensure no raw text leaks into report output."""
    SECRET = "ТЕСТОВЫЙ_СЕКРЕТ_PT_12345"
    record = {
        "timestamp": "2026-02-08T00:00:00+00:00",
        "trace_id": "trace-self-test",
        "command_id": "cmd-self-test",
        "corridor_intent": "add_shopping_item",
        "sample_rate": 0.1,
        "sampled": True,
        "status": "accepted_llm",
        "reason_code": "accepted",
        "latency_ms": 42,
        "model_meta": {"profile": "partial_trust", "task_id": SECRET},
        "baseline_summary": {"intent": "add_shopping_item", "decision_type": "start_job", "secret": SECRET},
        "llm_summary": {"intent": "add_shopping_item", "decision_type": "start_job"},
        "diff_summary": {"intent_mismatch": False, "entity_key_mismatch": False},
    }

    import tempfile

    with tempfile.TemporaryDirectory() as td:
        log_path = Path(td) / "risk.jsonl"
        log_path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")

        all_records = []
        for rec, ok in iter_risk_log(log_path):
            if ok:
                all_records.append(rec)
        report = compute_metrics(all_records)

        json_text = json.dumps(format_report_json(report), ensure_ascii=False)
        human_text = format_report_human(report)

        for output_text in (json_text, human_text):
            if SECRET in output_text:
                print("FAIL: self-test detected secret leak in output", file=sys.stderr)
                sys.exit(1)

    print("self-test ok")


def main() -> None:
    parser = argparse.ArgumentParser(description="Partial trust risk-log regression metrics analyzer")
    parser.add_argument(
        "--risk-log",
        type=Path,
        default=Path("logs/partial_trust_risk.jsonl"),
        help="Path to partial trust risk-log JSONL",
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

    all_records = []
    parse_errors = 0
    for rec, ok in iter_risk_log(args.risk_log):
        if ok:
            all_records.append(rec)
        else:
            parse_errors += 1

    report = compute_metrics(all_records)
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
