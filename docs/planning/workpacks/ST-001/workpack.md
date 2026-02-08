# WP / ST-001: Golden-dataset analyzer script + ground truth manifest + README

**Status:** Ready
**Story:** `docs/planning/epics/EP-001/stories/ST-001-golden-dataset-analyzer.md`
**Owner:** Codex (implementation) / Claude (prompts + review)

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q1-shadow-router.md` |
| Epic | `docs/planning/epics/EP-001/epic.md` |
| Story | `docs/planning/epics/EP-001/stories/ST-001-golden-dataset-analyzer.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

Deliver a reproducible Python script that reads shadow router JSONL logs, compares each record against a golden dataset manifest with ground truth labels, and produces a metrics report (intent_match_rate, entity_hit_rate, latency_p50/p95, error_breakdown). This closes initiative AC4 for INIT-2026Q1-shadow-router.

## Acceptance Criteria

1. **AC-1**: Script reads shadow router JSONL (`--shadow-log <path>`) and golden dataset (`--golden-dataset <path>`) without error; exits 0 on success.
2. **AC-2**: Report contains: `intent_match_rate` (float 0.0-1.0), `entity_hit_rate` (float 0.0-1.0), `latency_p50` (int ms), `latency_p95` (int ms), `error_breakdown` (dict error_type->count), `total_records` (int), `matched_records` (int).
3. **AC-3**: `--output-json <path>` writes JSON report to file; human-readable report always printed to stdout.
4. **AC-4**: Report contains NO raw user text, NO raw LLM output; a privacy self-test validates this.
5. **AC-5**: `skills/graph-sanity/fixtures/golden_dataset.json` contains entries for all 14 fixtures, each with `command_id`, `expected_intent`, `expected_entity_keys`.
6. **AC-6**: `scripts/README-shadow-analyzer.md` documents purpose, prerequisites, invocation examples, output format, how to add new entries.
7. **AC-7**: Empty or nonexistent JSONL file produces `total_records=0` and all rates as `null`.

## Files to Change

### New files (create)

| File | Description |
|------|-------------|
| `skills/graph-sanity/fixtures/golden_dataset.json` | Golden dataset manifest with ground truth labels for all 14 fixtures |
| `scripts/analyze_shadow_router.py` | Analyzer script -- reads JSONL + golden dataset, produces metrics report |
| `scripts/README-shadow-analyzer.md` | README documenting the analyzer script usage |
| `tests/test_analyze_shadow_router.py` | Unit tests for the analyzer script |

### Modified files

None.

## Implementation Plan

### Step 1: Create golden dataset manifest

**Commit:** `feat(shadow-router): add golden dataset manifest with ground truth labels`

Create `skills/graph-sanity/fixtures/golden_dataset.json`. Each entry:
```json
{
  "command_id": "cmd-wp000-001",
  "fixture_file": "buy_milk.json",
  "expected_intent": "add_shopping_item",
  "expected_entity_keys": ["item"],
  "notes": "Simple shopping command"
}
```

**Ground truth table** (derived from `graphs/core_graph.py` detect_intent keywords):

| command_id | fixture_file | expected_intent | expected_entity_keys |
|------------|-------------|-----------------|---------------------|
| cmd-wp000-001 | buy_milk.json | add_shopping_item | ["item"] |
| cmd-wp000-002 | buy_bread_and_eggs.json | add_shopping_item | ["item"] |
| cmd-wp000-003 | clean_bathroom.json | create_task | [] |
| cmd-wp000-004 | fix_faucet.json | create_task | [] |
| cmd-wp000-005 | empty_text.json | clarify_needed | [] |
| cmd-wp000-006 | unknown_intent.json | clarify_needed | [] |
| cmd-wp000-007 | minimal_context.json | create_task | [] |
| cmd-wp000-008 | shopping_no_list.json | add_shopping_item | ["item"] |
| cmd-wp000-009 | task_no_zones.json | create_task | [] |
| cmd-wp000-010 | buy_apples_en.json | add_shopping_item | ["item"] |
| cmd-wp000-011 | multiple_tasks.json | add_shopping_item | ["item"] |
| cmd-wp000-012 | add_sugar_ru.json | add_shopping_item | ["item"] |
| cmd-graph-002 | grocery_run.json | add_shopping_item | ["item"] |
| cmd-graph-001 | weekly_chores.json | create_task | [] |

**Note:** Ground truth is based on baseline `detect_intent()` first-match behavior (shadow router should ideally match or beat baseline).

### Step 2: Create analyzer script

**Commit:** `feat(shadow-router): add golden-dataset analyzer script`

Create `scripts/analyze_shadow_router.py`.

**CLI interface (argparse):**
- `--shadow-log PATH` (default: `logs/shadow_router.jsonl`)
- `--golden-dataset PATH` (default: `skills/graph-sanity/fixtures/golden_dataset.json`)
- `--output-json PATH` (optional)
- `--self-test` (run privacy self-test and exit)

**Core functions (public API for testing):**

```
load_golden_dataset(path: Path) -> dict[str, GoldenEntry]
    GoldenEntry dataclass: command_id, expected_intent, expected_entity_keys.

iter_shadow_log(path: Path) -> Iterable[dict]
    Reads JSONL line-by-line (streaming). Handles missing/empty file.

compute_metrics(records: list[dict], golden: dict[str, GoldenEntry]) -> MetricsReport
    Matches by command_id. Computes: intent_match_rate, entity_hit_rate,
    latency_p50, latency_p95, error_breakdown, total_records, matched_records.

format_report_json(report: MetricsReport) -> dict
format_report_human(report: MetricsReport) -> str
run_self_test() -> None
```

**Privacy:**
- DANGEROUS_FIELDS: `{"text", "question", "item_name", "ui_message", "raw", "output", "prompt", "normalized_text"}`
- Report must never include raw string values from JSONL records
- Only aggregated numeric/count metrics

**Percentile calc:** Sort + index-based (no external deps), same pattern as `scripts/metrics_agent_hints_v0.py`.

**Edge cases:**
- Empty/nonexistent JSONL: total_records=0, all rates=null, exit 0
- JSONL record without command_id: count in total, not in matched
- Parse errors: skip line, increment counter
- No matched records: all rates=null

### Step 3: Create README

**Commit:** `docs(shadow-router): add analyzer README`

Create `scripts/README-shadow-analyzer.md` with sections:
1. Purpose
2. Prerequisites (Python 3.11+, no external deps)
3. Invocation examples
4. Output format (describe each metric field)
5. Golden dataset format
6. Adding new entries
7. Privacy

### Step 4: Create unit tests

**Commit:** `test(shadow-router): add analyzer unit tests`

Create `tests/test_analyze_shadow_router.py`:

| Test | Checks |
|------|--------|
| `test_empty_jsonl_produces_zero_report` | Empty file -> total_records=0, rates=None |
| `test_single_matching_record_correct_intent` | intent_match_rate=1.0 |
| `test_single_matching_record_wrong_intent` | intent_match_rate=0.0 |
| `test_entity_hit_rate_calculation` | entity_hit_rate=0.5 for 1-match-1-miss |
| `test_latency_percentiles` | p50/p95 match known values |
| `test_error_breakdown_counts` | Correct error_type counts |
| `test_unmatched_records_excluded` | matched_records=0 for unknown command_ids |
| `test_privacy_no_raw_text` | No SECRET_VALUE in output |
| `test_golden_dataset_manifest_schema` | 14 entries, required fields |
| `test_end_to_end_with_json_output` | Full run, JSON output valid |

**Synthetic JSONL record structure:**
```json
{
  "timestamp": "2026-02-01T10:00:00+00:00",
  "trace_id": "trace-001",
  "command_id": "cmd-wp000-001",
  "router_version": "shadow-router-0.1",
  "router_strategy": "v2",
  "status": "ok",
  "latency_ms": 42,
  "error_type": null,
  "suggested_intent": "add_shopping_item",
  "missing_fields": null,
  "clarify_question": null,
  "entities_summary": {"keys": ["item"], "counts": {"item": 1}},
  "confidence": null,
  "model_meta": {"profile": "cheap", "task_id": "shopping_extraction"},
  "baseline_intent": "add_shopping_item",
  "baseline_action": null,
  "baseline_job_type": null
}
```

## Verification Commands

```bash
# 1. Golden dataset valid (14 entries)
python -c "
import json; from pathlib import Path
data = json.loads(Path('skills/graph-sanity/fixtures/golden_dataset.json').read_text())
assert len(data) == 14; print('OK: 14 entries')
"

# 2. Self-test
python scripts/analyze_shadow_router.py --self-test

# 3. Empty JSONL edge case
python scripts/analyze_shadow_router.py --shadow-log /dev/null

# 4. Unit tests
pytest tests/test_analyze_shadow_router.py -v

# 5. Full suite (no regressions)
pytest

# 6. Privacy grep
python scripts/analyze_shadow_router.py --shadow-log /dev/null 2>&1 | grep -iE "молоко|хлеб|яйца|бананы|сахар" && echo FAIL || echo OK
```

## DoD Checklist

- [ ] Python 3.11+, standard library only, no new deps
- [ ] No raw user text or LLM output in any script output
- [ ] Golden dataset manifest: 14 entries, valid JSON, all required fields
- [ ] `--self-test` passes
- [ ] Empty JSONL handled gracefully (exit 0, zero report)
- [ ] All 10 tests pass: `pytest tests/test_analyze_shadow_router.py -v`
- [ ] Full suite green: `pytest`
- [ ] README documents purpose, usage, format, extending
- [ ] Code reviewed

## Risks

| Risk | P | I | Mitigation |
|------|---|---|------------|
| entities_summary null/unexpected shape | Med | Low | Defensive `.get()`, default to empty keys |
| Ambiguous ground truth (e.g. cmd-wp000-011) | Low | Low | Label based on baseline detect_intent; document in notes |
| scripts/ not on Python path in tests | Med | Low | `sys.path.insert` in test file |
| Privacy leak in edge cases | Low | High | Self-test with planted SECRET_VALUE |

## Rollback

All changes additive (4 new files). Rollback = delete them. No config, pipeline, or DB changes.

## APPLY Boundaries

### Allowed
- `skills/graph-sanity/fixtures/golden_dataset.json` (create)
- `scripts/analyze_shadow_router.py` (create)
- `scripts/README-shadow-analyzer.md` (create)
- `tests/test_analyze_shadow_router.py` (create)

### Forbidden
- `routers/**` (do not modify)
- `app/**` (do not modify)
- `graphs/**` (do not modify)
- `tests/test_shadow_router.py` (do not modify)
- `scripts/metrics_agent_hints_v0.py` (reference only, do not modify)
- `Makefile`, `pyproject.toml` (do not modify)
