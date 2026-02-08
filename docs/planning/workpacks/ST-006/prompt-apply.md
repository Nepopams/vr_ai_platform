# Codex APPLY Prompt — ST-006: Regression Metrics Analyzer for Partial Trust Risk-Log

## Role

You are an implementation agent. Create ONLY the files listed below.

## Environment

- Python binary: `python3` (NOT `python`)

## STOP-THE-LINE

If you need to modify any file not listed in "Allowed files", STOP and report.

## Allowed files

- `scripts/analyze_partial_trust.py` (CREATE)
- `scripts/README-partial-trust-analyzer.md` (CREATE)
- `tests/test_analyze_partial_trust.py` (CREATE)

## Forbidden

- Any file under `routers/`, `app/`, `agents/`, `graphs/`
- Any existing `.py` file
- `git commit`, `git push`

---

## Step 1: Create analyzer script

Create `scripts/analyze_partial_trust.py` with EXACTLY this content:

```python
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
```

---

## Step 2: Create tests

Create `tests/test_analyze_partial_trust.py` with EXACTLY this content:

```python
"""Tests for partial trust risk-log regression metrics analyzer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# scripts/ is not a Python package; add to path for import
SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from analyze_partial_trust import (
    MetricsReport,
    compute_metrics,
    format_report_json,
    format_report_human,
    iter_risk_log,
    run_self_test,
)


def _record(
    status: str = "accepted_llm",
    reason_code: str = "accepted",
    latency_ms: int | None = 15,
    sampled: bool = True,
    diff_summary: dict | None = None,
) -> dict:
    return {
        "timestamp": "2026-02-08T12:00:00+00:00",
        "trace_id": "trace-test",
        "command_id": "cmd-test",
        "corridor_intent": "add_shopping_item",
        "sample_rate": 0.1,
        "sampled": sampled,
        "status": status,
        "reason_code": reason_code,
        "latency_ms": latency_ms,
        "model_meta": None,
        "baseline_summary": {"intent": "add_shopping_item", "decision_type": "start_job"},
        "llm_summary": {"intent": "add_shopping_item", "decision_type": "start_job"} if diff_summary else None,
        "diff_summary": diff_summary,
    }


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def test_empty_jsonl(tmp_path):
    """Empty file -> total_records=0, all rates None."""
    log_path = tmp_path / "empty.jsonl"
    log_path.write_text("", encoding="utf-8")

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.total_records == 0
    assert report.acceptance_rate is None
    assert report.intent_mismatch_rate is None
    assert report.entity_key_mismatch_rate is None
    assert report.error_rate is None
    assert report.latency_p50 is None
    assert report.latency_p95 is None


def test_nonexistent_file(tmp_path):
    """Nonexistent file -> total_records=0."""
    log_path = tmp_path / "does_not_exist.jsonl"

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.total_records == 0


def test_single_accepted(tmp_path):
    """One accepted_llm record -> acceptance_rate=1.0."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(log_path, [_record(status="accepted_llm", reason_code="accepted")])

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.total_records == 1
    assert report.acceptance_rate == 1.0
    assert report.status_breakdown["accepted_llm"] == 1


def test_single_fallback(tmp_path):
    """One fallback_deterministic -> acceptance_rate=0.0."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(log_path, [_record(status="fallback_deterministic", reason_code="low_confidence")])

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.total_records == 1
    assert report.acceptance_rate == 0.0
    assert report.status_breakdown["fallback_deterministic"] == 1


def test_mixed_statuses(tmp_path):
    """3 accepted + 2 fallback + 5 not_sampled -> correct breakdown and rate."""
    log_path = tmp_path / "log.jsonl"
    records_data = (
        [_record(status="accepted_llm", reason_code="accepted") for _ in range(3)]
        + [_record(status="fallback_deterministic", reason_code="low_confidence") for _ in range(2)]
        + [_record(status="not_sampled", reason_code="not_sampled", sampled=False, latency_ms=None) for _ in range(5)]
    )
    _write_jsonl(log_path, records_data)

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.total_records == 10
    assert report.status_breakdown["accepted_llm"] == 3
    assert report.status_breakdown["fallback_deterministic"] == 2
    assert report.status_breakdown["not_sampled"] == 5
    assert report.acceptance_rate == 0.6
    assert report.sampled_records == 5  # 3 accepted + 2 fallback


def test_intent_mismatch_rate(tmp_path):
    """2 records with diff_summary, 1 has intent_mismatch -> rate=0.5."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(
        log_path,
        [
            _record(diff_summary={"intent_mismatch": True, "entity_key_mismatch": False}),
            _record(diff_summary={"intent_mismatch": False, "entity_key_mismatch": False}),
        ],
    )

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.intent_mismatch_rate == 0.5


def test_entity_mismatch_rate(tmp_path):
    """2 records, 1 has entity_key_mismatch -> rate=0.5."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(
        log_path,
        [
            _record(diff_summary={"intent_mismatch": False, "entity_key_mismatch": True}),
            _record(diff_summary={"intent_mismatch": False, "entity_key_mismatch": False}),
        ],
    )

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.entity_key_mismatch_rate == 0.5


def test_latency_percentiles(tmp_path):
    """Known latency values -> correct p50 and p95."""
    log_path = tmp_path / "log.jsonl"
    records_data = [_record(latency_ms=i) for i in range(1, 21)]
    _write_jsonl(log_path, records_data)

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    # sorted: [1..20], p50 index = int(19*0.5) = 9 -> value 10
    assert report.latency_p50 == 10
    # p95 index = int(19*0.95) = 18 -> value 19
    assert report.latency_p95 == 19


def test_reason_code_breakdown(tmp_path):
    """Multiple reason codes -> correct counts."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(
        log_path,
        [
            _record(status="fallback_deterministic", reason_code="low_confidence"),
            _record(status="fallback_deterministic", reason_code="low_confidence"),
            _record(status="fallback_deterministic", reason_code="corridor_mismatch"),
            _record(status="accepted_llm", reason_code="accepted"),
        ],
    )

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.reason_code_breakdown["low_confidence"] == 2
    assert report.reason_code_breakdown["corridor_mismatch"] == 1
    assert report.reason_code_breakdown["accepted"] == 1


def test_error_rate(tmp_path):
    """1 error in 10 records -> error_rate=0.1."""
    log_path = tmp_path / "log.jsonl"
    records_data = [_record() for _ in range(9)] + [_record(status="error", reason_code="RuntimeError")]
    _write_jsonl(log_path, records_data)

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.error_rate == pytest.approx(0.1)


def test_records_without_diff_summary_excluded(tmp_path):
    """Records with status=not_sampled (no diff_summary) excluded from mismatch rates."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(
        log_path,
        [
            _record(status="not_sampled", reason_code="not_sampled", sampled=False, latency_ms=None),
            _record(diff_summary={"intent_mismatch": True, "entity_key_mismatch": False}),
        ],
    )

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    # Only 1 record has diff_summary, and it has intent_mismatch=True
    assert report.intent_mismatch_rate == 1.0
    assert report.entity_key_mismatch_rate == 0.0


def test_privacy_no_raw_text(tmp_path):
    """Report output must not contain any raw text from records."""
    SECRET = "СЕКРЕТНОЕ_ЗНАЧЕНИЕ_PT_999"
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(
        log_path,
        [
            {
                **_record(),
                "baseline_summary": {"intent": "add_shopping_item", "secret": SECRET},
                "llm_summary": {"intent": "add_shopping_item", "secret": SECRET},
            }
        ],
    )

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    json_output = json.dumps(format_report_json(report), ensure_ascii=False)
    human_output = format_report_human(report)

    assert SECRET not in json_output
    assert SECRET not in human_output


def test_json_output_has_all_fields(tmp_path):
    """JSON report contains all required metric fields."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(log_path, [_record(diff_summary={"intent_mismatch": False, "entity_key_mismatch": False})])

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)
    data = format_report_json(report)

    required_fields = {
        "total_records",
        "sampled_records",
        "status_breakdown",
        "reason_code_breakdown",
        "acceptance_rate",
        "intent_mismatch_rate",
        "entity_key_mismatch_rate",
        "latency_p50",
        "latency_p95",
        "error_rate",
        "parse_errors",
    }
    missing = required_fields - set(data.keys())
    assert not missing, f"Missing fields: {missing}"


def test_self_test():
    """Self-test must pass without error."""
    run_self_test()
```

---

## Step 3: Create README

Create `scripts/README-partial-trust-analyzer.md` with EXACTLY this content:

```markdown
# Partial Trust Risk-Log Analyzer

Regression metrics analyzer for the partial trust corridor risk-log.

## Purpose

Reads partial trust risk-log JSONL and computes aggregated metrics to assess whether the partial trust corridor is improving or degrading decision quality compared to baseline.

## Prerequisites

- Python 3.10+
- No external dependencies (uses only stdlib)

## Usage

```bash
# Basic usage (reads default log path)
python3 scripts/analyze_partial_trust.py --risk-log logs/partial_trust_risk.jsonl

# With JSON output
python3 scripts/analyze_partial_trust.py --risk-log logs/partial_trust_risk.jsonl --output-json report.json

# Privacy self-test
python3 scripts/analyze_partial_trust.py --self-test
```

## Output Format

### Human-readable (stdout)

```
=== Partial Trust Risk-Log Analyzer Report ===
Total records:           150
Sampled records:         15
Acceptance rate:         0.6000
Intent mismatch rate:    0.0667
Entity key mismatch:     0.1333
Error rate:              0.0067
Latency p50:             18 ms
Latency p95:             45 ms
Parse errors:            0
Status breakdown:
  accepted_llm: 9
  error: 1
  fallback_deterministic: 6
  not_sampled: 134
Reason code breakdown:
  accepted: 9
  low_confidence: 4
  corridor_mismatch: 1
  not_sampled: 134
  RuntimeError: 1
```

### JSON output (--output-json)

All metric fields:

| Field | Type | Description |
|-------|------|-------------|
| `total_records` | int | Total JSONL records processed |
| `sampled_records` | int | Records where `sampled=true` |
| `status_breakdown` | dict | Count per status: accepted_llm, fallback_deterministic, not_sampled, skipped, error |
| `reason_code_breakdown` | dict | Count per reason_code |
| `acceptance_rate` | float\|null | accepted_llm / (accepted_llm + fallback_deterministic). null if no decisions. |
| `intent_mismatch_rate` | float\|null | Fraction of records with diff_summary where intent_mismatch=true. null if no diff_summary records. |
| `entity_key_mismatch_rate` | float\|null | Fraction of records with diff_summary where entity_key_mismatch=true. null if no diff_summary records. |
| `latency_p50` | int\|null | p50 latency (ms) over records with latency_ms. null if no latency data. |
| `latency_p95` | int\|null | p95 latency (ms). null if no latency data. |
| `error_rate` | float\|null | error_count / total_records. null if total_records=0. |
| `parse_errors` | int | Number of malformed JSONL lines skipped |

## Interpreting Results

### Key metrics

- **acceptance_rate**: Fraction of sampled decisions where LLM replaced baseline. Higher = LLM more aggressive. Target: stable or increasing over rollout stages.
- **intent_mismatch_rate**: How often LLM disagrees with baseline on intent. Should be low (<0.05) for safe corridor.
- **entity_key_mismatch_rate**: How often LLM extracts different entity keys. Some mismatch is expected (LLM may extract more).
- **error_rate**: Should be <0.01. High error rate → investigate LLM provider issues.
- **latency_p95**: Should be within timeout budget (default 200ms). Increasing p95 → consider reducing timeout.

### Decision criteria for sampling progression

| Stage | Sample Rate | Min Duration | Go Criteria | No-Go Criteria |
|-------|------------|-------------|-------------|----------------|
| Stage 1 | 0.01 | 3 days | error_rate < 0.05, intent_mismatch < 0.10 | error_rate > 0.10 or any incident |
| Stage 2 | 0.05 | 5 days | error_rate < 0.03, intent_mismatch < 0.05 | error_rate > 0.05 |
| Stage 3 | 0.10 | 7 days | error_rate < 0.02, stable acceptance_rate | Any regression vs Stage 2 |

### Rollback triggers

- error_rate > 0.05 → immediately reduce sample rate or disable
- intent_mismatch_rate > 0.10 → investigate and reduce
- latency_p95 > 500ms → reduce timeout or disable

## Privacy

The analyzer processes only aggregated fields (status, reason_code, latency_ms, diff_summary booleans). It never reads or outputs raw user text or LLM output, even if present in JSONL records. Run `--self-test` to verify.
```

---

## Verification

After creating the files, run:

```bash
# 1. Analyzer tests pass
python3 -m pytest tests/test_analyze_partial_trust.py -v

# 2. Self-test
python3 scripts/analyze_partial_trust.py --self-test

# 3. Script runs on empty input
echo -n "" > /tmp/empty_pt.jsonl
python3 scripts/analyze_partial_trust.py --risk-log /tmp/empty_pt.jsonl

# 4. Full test suite
python3 -m pytest tests/ -v
```
