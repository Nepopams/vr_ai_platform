# Codex APPLY Prompt — ST-001: Golden-dataset analyzer script

## Role

You are an implementation agent. Create exactly 4 new files. Do NOT modify any existing files.

## STOP-THE-LINE

If you need to deviate from this prompt, STOP and report the issue. Do not guess or improvise.

## Boundaries

### Allowed (create only)
- `skills/graph-sanity/fixtures/golden_dataset.json`
- `scripts/analyze_shadow_router.py`
- `scripts/README-shadow-analyzer.md`
- `tests/test_analyze_shadow_router.py`

### Forbidden (do not touch)
- Any file under `routers/`, `app/`, `graphs/`, `agents/`, `agent_registry/`, `llm_policy/`
- `scripts/metrics_agent_hints_v0.py` (reference only)
- `tests/test_shadow_router.py`
- `Makefile`, `pyproject.toml`, `README.md`
- Any existing file in `skills/graph-sanity/fixtures/commands/`

---

## File 1: `skills/graph-sanity/fixtures/golden_dataset.json`

Create a JSON array with exactly 14 entries. Each entry has:
- `command_id` (str) — matches fixture file
- `fixture_file` (str) — filename in `skills/graph-sanity/fixtures/commands/`
- `expected_intent` (str) — one of: `add_shopping_item`, `create_task`, `clarify_needed`
- `expected_entity_keys` (list[str]) — keys that shadow router should extract (e.g. `["item"]` for shopping)
- `notes` (str) — brief explanation of why this intent is expected

**Exact data (confirmed by PLAN findings):**

```json
[
  {
    "command_id": "cmd-wp000-001",
    "fixture_file": "buy_milk.json",
    "expected_intent": "add_shopping_item",
    "expected_entity_keys": ["item"],
    "notes": "Купи молоко — keyword 'куп'"
  },
  {
    "command_id": "cmd-wp000-002",
    "fixture_file": "buy_bread_and_eggs.json",
    "expected_intent": "add_shopping_item",
    "expected_entity_keys": ["item"],
    "notes": "Купить хлеб и яйца — keyword 'куп'"
  },
  {
    "command_id": "cmd-wp000-003",
    "fixture_file": "clean_bathroom.json",
    "expected_intent": "create_task",
    "expected_entity_keys": [],
    "notes": "Убраться в ванной — keyword 'убраться'"
  },
  {
    "command_id": "cmd-wp000-004",
    "fixture_file": "fix_faucet.json",
    "expected_intent": "create_task",
    "expected_entity_keys": [],
    "notes": "Починить кран на кухне — keyword 'починить'"
  },
  {
    "command_id": "cmd-wp000-005",
    "fixture_file": "empty_text.json",
    "expected_intent": "clarify_needed",
    "expected_entity_keys": [],
    "notes": "Whitespace-only text — no keywords"
  },
  {
    "command_id": "cmd-wp000-006",
    "fixture_file": "unknown_intent.json",
    "expected_intent": "clarify_needed",
    "expected_entity_keys": [],
    "notes": "Что-то непонятное про погоду — no keywords match"
  },
  {
    "command_id": "cmd-wp000-007",
    "fixture_file": "minimal_context.json",
    "expected_intent": "create_task",
    "expected_entity_keys": [],
    "notes": "Сделай что-нибудь полезное — keyword 'сделай'"
  },
  {
    "command_id": "cmd-wp000-008",
    "fixture_file": "shopping_no_list.json",
    "expected_intent": "add_shopping_item",
    "expected_entity_keys": ["item"],
    "notes": "Купи бананы — keyword 'куп', no shopping list in context"
  },
  {
    "command_id": "cmd-wp000-009",
    "fixture_file": "task_no_zones.json",
    "expected_intent": "create_task",
    "expected_entity_keys": [],
    "notes": "Нужно помыть окна — keyword 'нужно'"
  },
  {
    "command_id": "cmd-wp000-010",
    "fixture_file": "buy_apples_en.json",
    "expected_intent": "add_shopping_item",
    "expected_entity_keys": ["item"],
    "notes": "Buy apples and oranges — keyword 'buy'"
  },
  {
    "command_id": "cmd-wp000-011",
    "fixture_file": "multiple_tasks.json",
    "expected_intent": "add_shopping_item",
    "expected_entity_keys": ["item"],
    "notes": "Купи молоко и убери кухню — keyword 'куп' wins (shopping checked first)"
  },
  {
    "command_id": "cmd-wp000-012",
    "fixture_file": "add_sugar_ru.json",
    "expected_intent": "add_shopping_item",
    "expected_entity_keys": ["item"],
    "notes": "Добавь сахар в список покупок — 'куп' substring in 'покупок'"
  },
  {
    "command_id": "cmd-graph-002",
    "fixture_file": "grocery_run.json",
    "expected_intent": "add_shopping_item",
    "expected_entity_keys": ["item"],
    "notes": "Купи яблоки и молоко — keyword 'куп'"
  },
  {
    "command_id": "cmd-graph-001",
    "fixture_file": "weekly_chores.json",
    "expected_intent": "create_task",
    "expected_entity_keys": [],
    "notes": "Нужно убрать кухню и составить план — keyword 'нужно'"
  }
]
```

---

## File 2: `scripts/analyze_shadow_router.py`

Create a standalone Python script (no external deps, stdlib only).

### Structure

```python
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
from typing import Any, Dict, Iterable, List, Optional
```

### Constants

```python
DANGEROUS_FIELDS = {
    "text", "question", "item_name", "ui_message",
    "raw", "output", "prompt", "normalized_text",
}
```

### Dataclasses

```python
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
```

### Core functions (public API — tests import these)

```python
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
```

### Helper functions

```python
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
```

### Self-test

```python
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
                print(f"FAIL: self-test detected secret leak in output", file=sys.stderr)
                sys.exit(1)

    print("self-test ok")
```

### Main entry point

```python
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
```

**Important:** Combine all the above sections into a single well-structured Python file. Use exactly these function names and signatures — the tests will import them.

---

## File 3: `scripts/README-shadow-analyzer.md`

Create a markdown README with these sections:

```markdown
# Shadow Router Golden-Dataset Analyzer

## Purpose

Offline analysis tool that compares shadow router JSONL logs against a golden dataset with ground truth labels. Produces metrics: intent match rate, entity hit rate, latency percentiles, and error breakdown.

Used to measure shadow LLM router quality vs baseline deterministic intent detection.

## Prerequisites

- Python 3.11+
- No external dependencies (stdlib only)

## Invocation

### Basic usage (reads default paths)
    python scripts/analyze_shadow_router.py

### Custom paths
    python scripts/analyze_shadow_router.py \
      --shadow-log logs/shadow_router.jsonl \
      --golden-dataset skills/graph-sanity/fixtures/golden_dataset.json

### JSON report output
    python scripts/analyze_shadow_router.py --output-json reports/shadow_metrics.json

### Privacy self-test
    python scripts/analyze_shadow_router.py --self-test

## Output Format

### Human-readable (stdout)
    === Shadow Router Analyzer Report ===
    Total records:      150
    Matched records:    14
    Intent match rate:  0.9286
    Entity hit rate:    0.8571
    Latency p50:        45 ms
    Latency p95:        120 ms
    Parse errors:       0
    Error breakdown:
      timeout: 2
      invalid_json: 1

### JSON (--output-json)
    {
      "total_records": 150,
      "matched_records": 14,
      "intent_match_rate": 0.9286,
      "entity_hit_rate": 0.8571,
      "latency_p50": 45,
      "latency_p95": 120,
      "error_breakdown": {"timeout": 2, "invalid_json": 1},
      "parse_errors": 0
    }

### Metrics

| Metric | Description |
|--------|-------------|
| total_records | Total JSONL records read |
| matched_records | Records matched to golden dataset by command_id |
| intent_match_rate | Fraction of matched records where suggested_intent == expected_intent |
| entity_hit_rate | Fraction of matched records where entity keys match expected |
| latency_p50 | 50th percentile latency across ALL records (ms) |
| latency_p95 | 95th percentile latency across ALL records (ms) |
| error_breakdown | Count per error_type (excluding null) |
| parse_errors | JSONL lines that failed to parse |

## Golden Dataset Format

File: `skills/graph-sanity/fixtures/golden_dataset.json`

Each entry:
    {
      "command_id": "cmd-wp000-001",
      "fixture_file": "buy_milk.json",
      "expected_intent": "add_shopping_item",
      "expected_entity_keys": ["item"],
      "notes": "Купи молоко — keyword 'куп'"
    }

## Adding New Entries

1. Create a new command fixture in `skills/graph-sanity/fixtures/commands/<name>.json`
2. Add an entry to `skills/graph-sanity/fixtures/golden_dataset.json` with:
   - `command_id` matching the fixture
   - `expected_intent` based on detect_intent() logic (see graphs/core_graph.py)
   - `expected_entity_keys` — `["item"]` for shopping, `[]` otherwise
3. Run `python scripts/analyze_shadow_router.py --self-test` to verify

## Privacy

The analyzer NEVER outputs raw user text or LLM output.
Only aggregated numeric metrics appear in reports.
Use `--self-test` to verify privacy compliance.
```

---

## File 4: `tests/test_analyze_shadow_router.py`

Create a test file with 10 test functions.

**Import pattern** (PLAN finding: scripts/ is not a package, use sys.path):

```python
"""Tests for shadow router golden-dataset analyzer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# scripts/ is not a Python package; add to path for import
SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from analyze_shadow_router import (
    GoldenEntry,
    MetricsReport,
    compute_metrics,
    format_report_json,
    format_report_human,
    iter_shadow_log,
    load_golden_dataset,
    run_self_test,
)

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "skills" / "graph-sanity" / "fixtures"
```

**Helper to create synthetic JSONL record:**

```python
def _make_record(
    command_id: str = "cmd-test-001",
    suggested_intent: str = "add_shopping_item",
    entity_keys: list[str] | None = None,
    latency_ms: int = 50,
    error_type: str | None = None,
) -> dict:
    return {
        "timestamp": "2026-02-01T10:00:00+00:00",
        "trace_id": "trace-test",
        "command_id": command_id,
        "router_version": "shadow-router-0.1",
        "router_strategy": "v2",
        "status": "ok" if error_type is None else "error",
        "latency_ms": latency_ms,
        "error_type": error_type,
        "suggested_intent": suggested_intent,
        "missing_fields": None,
        "clarify_question": None,
        "entities_summary": {"keys": entity_keys or [], "counts": {}},
        "confidence": None,
        "model_meta": None,
        "baseline_intent": "add_shopping_item",
        "baseline_action": None,
        "baseline_job_type": None,
    }


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _write_golden(path: Path, entries: list[dict]) -> None:
    path.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")


def _golden_entry(
    command_id: str = "cmd-test-001",
    expected_intent: str = "add_shopping_item",
    expected_entity_keys: list[str] | None = None,
) -> dict:
    return {
        "command_id": command_id,
        "fixture_file": "test.json",
        "expected_intent": expected_intent,
        "expected_entity_keys": expected_entity_keys or [],
        "notes": "test entry",
    }
```

**10 test functions:**

```python
def test_empty_jsonl_produces_zero_report(tmp_path):
    """Empty JSONL -> total_records=0, all rates None."""
    log_path = tmp_path / "empty.jsonl"
    log_path.write_text("", encoding="utf-8")
    golden_path = tmp_path / "golden.json"
    _write_golden(golden_path, [_golden_entry()])

    golden = load_golden_dataset(golden_path)
    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    assert report.total_records == 0
    assert report.matched_records == 0
    assert report.intent_match_rate is None
    assert report.entity_hit_rate is None
    assert report.latency_p50 is None
    assert report.latency_p95 is None


def test_single_matching_record_correct_intent(tmp_path):
    """One record matching golden entry with correct intent -> rate 1.0."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(log_path, [_make_record()])
    golden_path = tmp_path / "golden.json"
    _write_golden(golden_path, [_golden_entry()])

    golden = load_golden_dataset(golden_path)
    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    assert report.total_records == 1
    assert report.matched_records == 1
    assert report.intent_match_rate == 1.0


def test_single_matching_record_wrong_intent(tmp_path):
    """One record with wrong intent -> rate 0.0."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(log_path, [_make_record(suggested_intent="create_task")])
    golden_path = tmp_path / "golden.json"
    _write_golden(golden_path, [_golden_entry(expected_intent="add_shopping_item")])

    golden = load_golden_dataset(golden_path)
    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    assert report.matched_records == 1
    assert report.intent_match_rate == 0.0


def test_entity_hit_rate_calculation(tmp_path):
    """Two records: one matching entities, one not -> rate 0.5."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(log_path, [
        _make_record(command_id="cmd-1", entity_keys=["item"]),
        _make_record(command_id="cmd-2", entity_keys=["wrong"]),
    ])
    golden_path = tmp_path / "golden.json"
    _write_golden(golden_path, [
        _golden_entry(command_id="cmd-1", expected_entity_keys=["item"]),
        _golden_entry(command_id="cmd-2", expected_entity_keys=["item"]),
    ])

    golden = load_golden_dataset(golden_path)
    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    assert report.matched_records == 2
    assert report.entity_hit_rate == 0.5


def test_latency_percentiles(tmp_path):
    """Known latency values -> verify p50 and p95."""
    log_path = tmp_path / "log.jsonl"
    # 20 records with latencies 1..20
    records_data = [_make_record(command_id=f"cmd-{i}", latency_ms=i) for i in range(1, 21)]
    _write_jsonl(log_path, records_data)
    golden_path = tmp_path / "golden.json"
    _write_golden(golden_path, [])  # no golden entries needed for latency

    golden = load_golden_dataset(golden_path)
    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    assert report.total_records == 20
    # sorted: [1..20], p50 index = int(19*0.5) = 9 -> value 10
    assert report.latency_p50 == 10
    # p95 index = int(19*0.95) = 18 -> value 19
    assert report.latency_p95 == 19


def test_error_breakdown_counts(tmp_path):
    """Records with various error types -> correct counts."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(log_path, [
        _make_record(command_id="c1", error_type="timeout"),
        _make_record(command_id="c2", error_type="timeout"),
        _make_record(command_id="c3", error_type="invalid_json"),
        _make_record(command_id="c4", error_type=None),
    ])
    golden_path = tmp_path / "golden.json"
    _write_golden(golden_path, [])

    golden = load_golden_dataset(golden_path)
    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    assert report.error_breakdown == {"timeout": 2, "invalid_json": 1}


def test_unmatched_records_excluded(tmp_path):
    """Records with command_ids NOT in golden dataset -> matched=0, rates None."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(log_path, [
        _make_record(command_id="cmd-unknown-1"),
        _make_record(command_id="cmd-unknown-2"),
    ])
    golden_path = tmp_path / "golden.json"
    _write_golden(golden_path, [_golden_entry(command_id="cmd-other")])

    golden = load_golden_dataset(golden_path)
    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    assert report.total_records == 2
    assert report.matched_records == 0
    assert report.intent_match_rate is None
    assert report.entity_hit_rate is None


def test_privacy_no_raw_text(tmp_path):
    """Report must not contain any planted secret text."""
    SECRET = "СЕКРЕТНОЕ_ЗНАЧЕНИЕ_ABC_999"
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(log_path, [
        {
            **_make_record(),
            "clarify_question": SECRET,
            "model_meta": {"task_id": SECRET},
        }
    ])
    golden_path = tmp_path / "golden.json"
    _write_golden(golden_path, [_golden_entry()])

    golden = load_golden_dataset(golden_path)
    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    json_output = json.dumps(format_report_json(report), ensure_ascii=False)
    human_output = format_report_human(report)

    assert SECRET not in json_output
    assert SECRET not in human_output


def test_golden_dataset_manifest_schema():
    """Validate actual golden_dataset.json: 14 entries, required fields."""
    golden_path = FIXTURES_DIR / "golden_dataset.json"
    assert golden_path.exists(), f"golden_dataset.json not found at {golden_path}"

    data = json.loads(golden_path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 14, f"Expected 14 entries, got {len(data)}"

    required_fields = {"command_id", "expected_intent", "expected_entity_keys"}
    for entry in data:
        missing = required_fields - set(entry.keys())
        assert not missing, f"Entry {entry.get('command_id')} missing fields: {missing}"
        assert isinstance(entry["expected_entity_keys"], list)


def test_end_to_end_with_json_output(tmp_path):
    """Full run: synthetic JSONL + real golden dataset -> valid JSON report."""
    golden_path = FIXTURES_DIR / "golden_dataset.json"
    if not golden_path.exists():
        pytest.skip("golden_dataset.json not yet created")

    golden = load_golden_dataset(golden_path)
    # Create synthetic JSONL with 3 records matching golden entries
    sample_ids = list(golden.keys())[:3]
    log_records = []
    for cid in sample_ids:
        entry = golden[cid]
        log_records.append(_make_record(
            command_id=cid,
            suggested_intent=entry.expected_intent,
            entity_keys=entry.expected_entity_keys,
            latency_ms=42,
        ))
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(log_path, log_records)

    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    assert report.total_records == 3
    assert report.matched_records == 3
    assert report.intent_match_rate == 1.0

    # Test JSON output
    output_path = tmp_path / "report.json"
    output_path.write_text(
        json.dumps(format_report_json(report), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert "intent_match_rate" in loaded
    assert "entity_hit_rate" in loaded
    assert "latency_p50" in loaded
    assert "latency_p95" in loaded
    assert "error_breakdown" in loaded
    assert "total_records" in loaded
    assert "matched_records" in loaded
```

---

## Verification (run after all files created)

```bash
# 1. Golden dataset valid
python -c "import json; from pathlib import Path; d=json.loads(Path('skills/graph-sanity/fixtures/golden_dataset.json').read_text()); assert len(d)==14; print('OK: 14 entries')"

# 2. Self-test
python scripts/analyze_shadow_router.py --self-test

# 3. Empty JSONL
python scripts/analyze_shadow_router.py --shadow-log /dev/null

# 4. Unit tests
python -m pytest tests/test_analyze_shadow_router.py -v

# 5. Full suite
python -m pytest tests/ -v

# 6. Privacy grep
python scripts/analyze_shadow_router.py --shadow-log /dev/null 2>&1 | grep -iE "молоко|хлеб|яйца|бананы|сахар" && echo "FAIL" || echo "OK: no raw text"
```

If any verification step fails, STOP and report the issue.
