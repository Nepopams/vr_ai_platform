#!/usr/bin/env python3
"""Offline metrics for agent-hints (Phase 5.2c).

Privacy rules:
- Never print or store raw user text or string payload values.
- If string values are detected in events, count a warning only.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import statistics
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


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

ASSIST_SAFE_STRING_FIELDS = {
    "agent_hint_status",
    "agent_hint_selected_status",
    "agent_hint_selected_agent_id",
    "agent_hint_selection_reason",
}


@dataclass
class FileInventory:
    path: Path
    lines_read: int = 0
    parse_errors: int = 0
    schema_drift: int = 0
    keys_seen: Dict[str, int] = field(default_factory=dict)


@dataclass
class Warnings:
    parse_errors: int = 0
    schema_drift: int = 0
    dangerous_fields_present: int = 0
    string_values_detected: int = 0


@dataclass
class Metrics:
    attempted: int = 0
    applied: int = 0
    rejected: int = 0
    skipped: int = 0
    error: int = 0
    reason_codes: Dict[str, int] = field(default_factory=dict)
    agent_hint_latencies: List[int] = field(default_factory=list)
    agent_run_latencies: List[int] = field(default_factory=list)
    diff_overlap_counts: List[int] = field(default_factory=list)
    diff_agent_keys_counts: List[int] = field(default_factory=list)
    diff_baseline_keys_counts: List[int] = field(default_factory=list)
    uplift_proxy: int = 0
    total_events: int = 0
    total_commands: int = 0
    command_ids: set[str] = field(default_factory=set)
    candidate_events_seen: int = 0
    candidates_total: int = 0
    selection_attempted: int = 0
    selection_made: int = 0
    selection_ok: int = 0
    selection_reason_distribution: Dict[str, int] = field(default_factory=dict)
    selected_agent_id_distribution: Dict[str, int] = field(default_factory=dict)
    selected_status_distribution: Dict[str, int] = field(default_factory=dict)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Offline metrics for agent-hints v0")
    parser.add_argument("--assist-log", default="logs/assist.jsonl")
    parser.add_argument("--agent-run-log", default="logs/agent_run.jsonl")
    parser.add_argument("--shadow-diff-log", default="logs/shadow_agent_diff.jsonl")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--report-json", default=None)
    parser.add_argument("--warnings-json", default=None)
    parser.add_argument("--since", default=None)
    parser.add_argument("--until", default=None)
    parser.add_argument("--no-dedupe", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def _parse_iso(ts: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def _should_include(ts: Optional[str], since: Optional[datetime], until: Optional[datetime]) -> bool:
    if not ts:
        return True
    dt = _parse_iso(ts)
    if not dt:
        return True
    if since and dt < since:
        return False
    if until and dt > until:
        return False
    return True


def _iter_jsonl(path: Path, inventory: FileInventory, warnings: Warnings) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            inventory.lines_read += 1
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                inventory.parse_errors += 1
                warnings.parse_errors += 1
                continue
            if isinstance(payload, dict):
                for key in payload.keys():
                    inventory.keys_seen[key] = inventory.keys_seen.get(key, 0) + 1
            yield payload


def _count_string_values(value: Any, safe_string_fields: set[str]) -> int:
    if isinstance(value, str):
        return 1
    if isinstance(value, list):
        return sum(_count_string_values(item, safe_string_fields) for item in value)
    if isinstance(value, dict):
        total = 0
        for key, item in value.items():
            if key in safe_string_fields:
                continue
            total += _count_string_values(item, safe_string_fields)
        return total
    return 0


def _scan_privacy(payload: Dict[str, Any], warnings: Warnings, safe_string_fields: set[str]) -> None:
    for key in payload.keys():
        if key in DANGEROUS_FIELDS:
            warnings.dangerous_fields_present += 1
            break
    if _count_string_values(payload, safe_string_fields) > 0:
        warnings.string_values_detected += 1


def _update_reason(metrics: Metrics, code: Optional[str]) -> None:
    if not code:
        return
    metrics.reason_codes[code] = metrics.reason_codes.get(code, 0) + 1


def _percentile(values: List[int], p: float) -> Optional[int]:
    if not values:
        return None
    values_sorted = sorted(values)
    if len(values_sorted) == 1:
        return values_sorted[0]
    idx = int((len(values_sorted) - 1) * p)
    return values_sorted[idx]


def _record_command_id(metrics: Metrics, command_id: Any, dedupe: bool) -> None:
    if not dedupe:
        metrics.total_commands += 1
        return
    if isinstance(command_id, str):
        if command_id not in metrics.command_ids:
            metrics.command_ids.add(command_id)
            metrics.total_commands += 1


def _handle_assist(
    payload: Dict[str, Any],
    metrics: Metrics,
    warnings: Warnings,
    inventory: FileInventory,
    since: Optional[datetime],
    until: Optional[datetime],
) -> None:
    if not _should_include(payload.get("timestamp"), since, until):
        return
    if payload.get("step") != "entities":
        return
    required = {"step", "status"}
    if not required.issubset(payload.keys()):
        inventory.schema_drift += 1
        warnings.schema_drift += 1
        return
    _scan_privacy(payload, warnings, ASSIST_SAFE_STRING_FIELDS)
    metrics.total_events += 1

    hint_status = payload.get("agent_hint_status")
    if hint_status is None:
        return

    metrics.attempted += 1
    if hint_status == "ok" and payload.get("agent_hint_applied") is True:
        metrics.applied += 1
        metrics.uplift_proxy += 1
    elif hint_status == "ok" and payload.get("agent_hint_applied") is False:
        metrics.rejected += 1
    elif hint_status == "skipped":
        metrics.skipped += 1
    elif hint_status == "error":
        metrics.error += 1
    else:
        metrics.rejected += 1

    latency = payload.get("agent_hint_latency_ms")
    if isinstance(latency, int):
        metrics.agent_hint_latencies.append(latency)

    selection_fields = {
        "agent_hint_candidates_count",
        "agent_hint_selected_agent_id",
        "agent_hint_selected_status",
        "agent_hint_selection_reason",
    }
    has_any_selection_field = any(field in payload for field in selection_fields)
    if has_any_selection_field and "agent_hint_candidates_count" not in payload:
        inventory.schema_drift += 1
        warnings.schema_drift += 1

    candidates_value = payload.get("agent_hint_candidates_count")
    if "agent_hint_candidates_count" in payload:
        metrics.candidate_events_seen += 1
        if isinstance(candidates_value, int):
            metrics.candidates_total += candidates_value
            if candidates_value > 0:
                metrics.selection_attempted += 1
        else:
            inventory.schema_drift += 1
            warnings.schema_drift += 1

    selected_agent_id = payload.get("agent_hint_selected_agent_id")
    if isinstance(selected_agent_id, str) and selected_agent_id:
        metrics.selection_made += 1
        metrics.selected_agent_id_distribution[selected_agent_id] = (
            metrics.selected_agent_id_distribution.get(selected_agent_id, 0) + 1
        )

    selected_status = payload.get("agent_hint_selected_status")
    if isinstance(selected_status, str) and selected_status:
        metrics.selected_status_distribution[selected_status] = (
            metrics.selected_status_distribution.get(selected_status, 0) + 1
        )
        if selected_status == "ok":
            metrics.selection_ok += 1

    selection_reason = payload.get("agent_hint_selection_reason")
    if isinstance(selection_reason, str) and selection_reason:
        metrics.selection_reason_distribution[selection_reason] = (
            metrics.selection_reason_distribution.get(selection_reason, 0) + 1
        )


def _handle_agent_run(
    payload: Dict[str, Any],
    metrics: Metrics,
    warnings: Warnings,
    inventory: FileInventory,
    since: Optional[datetime],
    until: Optional[datetime],
    dedupe: bool,
) -> None:
    if not _should_include(payload.get("timestamp"), since, until):
        return
    required = {"status", "latency_ms"}
    if not required.issubset(payload.keys()):
        inventory.schema_drift += 1
        warnings.schema_drift += 1
    _scan_privacy(payload, warnings, set())
    metrics.total_events += 1
    _record_command_id(metrics, payload.get("command_id"), dedupe)
    _update_reason(metrics, payload.get("reason_code"))
    latency = payload.get("latency_ms")
    if isinstance(latency, int):
        metrics.agent_run_latencies.append(latency)


def _handle_diff(
    payload: Dict[str, Any],
    metrics: Metrics,
    warnings: Warnings,
    inventory: FileInventory,
    since: Optional[datetime],
    until: Optional[datetime],
    dedupe: bool,
) -> None:
    if not _should_include(payload.get("timestamp"), since, until):
        return
    required = {"baseline_summary", "agent_summary", "diff_summary"}
    if not required.issubset(payload.keys()):
        inventory.schema_drift += 1
        warnings.schema_drift += 1
        return
    _scan_privacy(payload, warnings, set())
    metrics.total_events += 1
    _record_command_id(metrics, payload.get("command_id"), dedupe)
    _update_reason(metrics, payload.get("reason_code"))

    diff = payload.get("diff_summary") or {}
    overlap = diff.get("keys_overlap_count")
    if isinstance(overlap, int):
        metrics.diff_overlap_counts.append(overlap)
    agent_keys = diff.get("agent_keys_count")
    if isinstance(agent_keys, int):
        metrics.diff_agent_keys_counts.append(agent_keys)
    baseline_keys = diff.get("baseline_keys_count")
    if isinstance(baseline_keys, int):
        metrics.diff_baseline_keys_counts.append(baseline_keys)


def _write_json(path: Optional[Path], payload: Dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _report_metrics(metrics: Metrics) -> Dict[str, Any]:
    selection_attempted = metrics.selection_attempted
    selection_made = metrics.selection_made
    no_selection = selection_attempted - selection_made
    return {
        "coverage": {
            "attempted": metrics.attempted,
            "applied": metrics.applied,
            "rejected": metrics.rejected,
            "skipped": metrics.skipped,
            "error": metrics.error,
            "total_events": metrics.total_events,
            "total_commands": metrics.total_commands or None,
        },
        "selection": {
            "candidate_events_seen": metrics.candidate_events_seen,
            "candidates_total": metrics.candidates_total,
            "selection_attempted": selection_attempted,
            "selection_made": selection_made,
            "selection_ok": metrics.selection_ok,
            "selection_rate": _ratio(selection_made, selection_attempted),
            "no_selection_rate": _ratio(no_selection, selection_attempted),
            "selection_reason_distribution": metrics.selection_reason_distribution,
            "selected_agent_id_distribution": metrics.selected_agent_id_distribution,
            "selected_status_distribution": metrics.selected_status_distribution,
        },
        "latency": {
            "agent_hint_p50": _percentile(metrics.agent_hint_latencies, 0.5),
            "agent_hint_p95": _percentile(metrics.agent_hint_latencies, 0.95),
            "agent_run_p50": _percentile(metrics.agent_run_latencies, 0.5),
            "agent_run_p95": _percentile(metrics.agent_run_latencies, 0.95),
        },
        "quality_proxies": {
            "uplift_proxy": metrics.uplift_proxy,
            "diff_keys_overlap_p50": _percentile(metrics.diff_overlap_counts, 0.5),
            "diff_keys_overlap_p95": _percentile(metrics.diff_overlap_counts, 0.95),
        },
        "reason_codes": metrics.reason_codes,
    }


def _report_inventory(inventories: List[FileInventory]) -> Dict[str, Any]:
    return {
        str(inv.path): {
            "lines_read": inv.lines_read,
            "parse_errors": inv.parse_errors,
            "schema_drift": inv.schema_drift,
            "keys_seen": inv.keys_seen,
        }
        for inv in inventories
    }


def _collect_reports(
    assist_path: Path,
    agent_run_path: Path,
    diff_path: Path,
    *,
    since: Optional[datetime],
    until: Optional[datetime],
    dedupe: bool,
) -> tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    inventories: List[FileInventory] = []
    warnings = Warnings()
    metrics = Metrics()

    assist_inv = FileInventory(path=assist_path)
    inventories.append(assist_inv)
    for event in _iter_jsonl(assist_path, assist_inv, warnings):
        if isinstance(event, dict):
            _handle_assist(event, metrics, warnings, assist_inv, since, until)

    agent_inv = FileInventory(path=agent_run_path)
    inventories.append(agent_inv)
    for event in _iter_jsonl(agent_run_path, agent_inv, warnings):
        if isinstance(event, dict):
            _handle_agent_run(event, metrics, warnings, agent_inv, since, until, dedupe)

    diff_inv = FileInventory(path=diff_path)
    inventories.append(diff_inv)
    for event in _iter_jsonl(diff_path, diff_inv, warnings):
        if isinstance(event, dict):
            _handle_diff(event, metrics, warnings, diff_inv, since, until, dedupe)

    inventory_report = _report_inventory(inventories)
    metrics_report = _report_metrics(metrics)
    warnings_report = {
        "parse_errors": warnings.parse_errors,
        "schema_drift": warnings.schema_drift,
        "dangerous_fields_present": warnings.dangerous_fields_present,
        "string_values_detected": warnings.string_values_detected,
    }
    return inventory_report, metrics_report, warnings_report


def _ratio(numerator: int, denominator: int) -> Optional[float]:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 4)


def _run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        assist_path = base / "assist.jsonl"
        agent_run_path = base / "agent_run.jsonl"
        diff_path = base / "shadow_agent_diff.jsonl"
        secret = "SECRET_VALUE"

        assist_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "step": "entities",
            "status": "ok",
            "agent_hint_status": "ok",
            "agent_hint_latency_ms": 12,
            "agent_hint_applied": True,
            "agent_hint_candidates_count": 2,
            "agent_hint_selected_agent_id": "agent-x",
            "agent_hint_selected_status": "ok",
            "agent_hint_selection_reason": "latency_tiebreak",
            "item_name": secret,
        }
        agent_run_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "ok",
            "latency_ms": 5,
            "agent_id": "agent-x",
            "command_id": "cmd-1",
        }
        diff_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "baseline_summary": {"intent": "add_shopping_item"},
            "agent_summary": {"keys_present": ["items"]},
            "diff_summary": {"keys_overlap_count": 1, "agent_keys_count": 1, "baseline_keys_count": 1},
        }
        assist_path.write_text(json.dumps(assist_event, ensure_ascii=False) + "\n", encoding="utf-8")
        agent_run_path.write_text(json.dumps(agent_run_event, ensure_ascii=False) + "\n", encoding="utf-8")
        diff_path.write_text(json.dumps(diff_event, ensure_ascii=False) + "\n", encoding="utf-8")

        inventory_report, metrics_report, warnings_report = _collect_reports(
            assist_path,
            agent_run_path,
            diff_path,
            since=None,
            until=None,
            dedupe=True,
        )

        out_report = base / "report.json"
        out_warnings = base / "warnings.json"
        _write_json(out_report, metrics_report | {"inventory": inventory_report})
        _write_json(out_warnings, warnings_report)

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _print_stdout(metrics_report, warnings_report, inventory_report)
        combined = (
            buf.getvalue()
            + out_report.read_text(encoding="utf-8")
            + out_warnings.read_text(encoding="utf-8")
        )
        if secret in combined:
            raise SystemExit("self-test failed: privacy leak detected")

        print("self-test ok")


def main() -> None:
    args = parse_args()
    if args.self_test:
        _run_self_test()
        return

    since = _parse_iso(args.since) if args.since else None
    until = _parse_iso(args.until) if args.until else None

    assist_path = Path(args.assist_log)
    agent_run_path = Path(args.agent_run_log)
    diff_path = Path(args.shadow_diff_log)

    inventory_report, metrics_report, warnings_report = _collect_reports(
        assist_path,
        agent_run_path,
        diff_path,
        since=since,
        until=until,
        dedupe=not args.no_dedupe,
    )

    report_path = None
    warnings_path = None
    if args.output_dir:
        out_dir = Path(args.output_dir)
        report_path = out_dir / "report.json"
        warnings_path = out_dir / "warnings.json"
    if args.report_json:
        report_path = Path(args.report_json)
    if args.warnings_json:
        warnings_path = Path(args.warnings_json)

    _write_json(report_path, metrics_report | {"inventory": inventory_report})
    _write_json(warnings_path, warnings_report)

    _print_stdout(metrics_report, warnings_report, inventory_report)


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    return str(value)


def _print_stdout(metrics: Dict[str, Any], warnings: Dict[str, Any], inventory: Dict[str, Any]) -> None:
    coverage = metrics.get("coverage", {})
    selection = metrics.get("selection", {})
    latency = metrics.get("latency", {})
    quality = metrics.get("quality_proxies", {})

    print("agent-hints metrics (offline)")
    print("coverage:")
    print(f"  attempted: {_fmt(coverage.get('attempted'))}")
    print(f"  applied: {_fmt(coverage.get('applied'))}")
    print(f"  rejected: {_fmt(coverage.get('rejected'))}")
    print(f"  skipped: {_fmt(coverage.get('skipped'))}")
    print(f"  error: {_fmt(coverage.get('error'))}")
    print(f"  total_events: {_fmt(coverage.get('total_events'))}")
    print(f"  total_commands: {_fmt(coverage.get('total_commands'))}")

    print("selection:")
    print(f"  candidate_events_seen: {_fmt(selection.get('candidate_events_seen'))}")
    print(f"  candidates_total: {_fmt(selection.get('candidates_total'))}")
    print(f"  selection_attempted: {_fmt(selection.get('selection_attempted'))}")
    print(f"  selection_made: {_fmt(selection.get('selection_made'))}")
    print(f"  selection_ok: {_fmt(selection.get('selection_ok'))}")
    print(f"  selection_rate: {_fmt(selection.get('selection_rate'))}")
    print(f"  no_selection_rate: {_fmt(selection.get('no_selection_rate'))}")

    print("latency:")
    print(f"  agent_hint_p50: {_fmt(latency.get('agent_hint_p50'))}")
    print(f"  agent_hint_p95: {_fmt(latency.get('agent_hint_p95'))}")
    print(f"  agent_run_p50: {_fmt(latency.get('agent_run_p50'))}")
    print(f"  agent_run_p95: {_fmt(latency.get('agent_run_p95'))}")

    print("quality:")
    print(f"  uplift_proxy: {_fmt(quality.get('uplift_proxy'))}")
    print(f"  diff_keys_overlap_p50: {_fmt(quality.get('diff_keys_overlap_p50'))}")
    print(f"  diff_keys_overlap_p95: {_fmt(quality.get('diff_keys_overlap_p95'))}")

    print("warnings:")
    print(f"  parse_errors: {_fmt(warnings.get('parse_errors'))}")
    print(f"  schema_drift: {_fmt(warnings.get('schema_drift'))}")
    print(f"  dangerous_fields_present: {_fmt(warnings.get('dangerous_fields_present'))}")
    print(f"  string_values_detected: {_fmt(warnings.get('string_values_detected'))}")

    print("inventory:")
    for path, details in inventory.items():
        print(f"  {path} lines={_fmt(details.get('lines_read'))} parse_errors={_fmt(details.get('parse_errors'))} schema_drift={_fmt(details.get('schema_drift'))}")


if __name__ == "__main__":
    main()
