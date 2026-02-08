# Workpack — ST-006: Regression Metrics Analyzer for Partial Trust Risk-Log

**Status:** Ready
**Story:** `docs/planning/epics/EP-003/stories/ST-006-regression-metrics-tooling.md`
**Epic:** `docs/planning/epics/EP-003/epic.md`
**Initiative:** `docs/planning/initiatives/INIT-2026Q2-partial-trust.md`

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-partial-trust.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

A reproducible Python script that reads partial trust risk-log JSONL, computes regression metrics, and outputs a structured report (human-readable + JSON). Enables data-driven decisions for sampling rate progression (0.01 → 0.05 → 0.10).

---

## Acceptance Criteria Summary

1. Script reads JSONL from `--risk-log <path>`, exits 0
2. Report contains: total_records, status_breakdown, reason_code_breakdown, acceptance_rate, intent_mismatch_rate, entity_key_mismatch_rate, latency_p50/p95, error_rate
3. `--output-json <path>` writes JSON file + prints human-readable to stdout
4. No raw user text or LLM output in report
5. Empty/nonexistent JSONL → total_records=0, rates null
6. Records without diff_summary excluded from mismatch rate calculations
7. README documents usage

---

## Files to Change

### New files (CREATE)

| File | Description |
|------|-------------|
| `scripts/analyze_partial_trust.py` | Regression metrics analyzer script |
| `scripts/README-partial-trust-analyzer.md` | Usage documentation |
| `tests/test_analyze_partial_trust.py` | Unit tests for the analyzer |

### Key files to READ (context, not modify)

| File | Why |
|------|-----|
| `app/logging/partial_trust_risk_log.py` | Log format: JSONL with `json.dumps(record)` per line |
| `routers/v2.py` (lines 422-452) | `_log_partial_trust` — defines JSONL field names: trace_id, command_id, corridor_intent, sample_rate, sampled, status, reason_code, latency_ms, model_meta, baseline_summary, llm_summary, diff_summary, timestamp |
| `routers/v2.py` (lines 409-419) | `_build_diff_summary` — defines diff_summary fields: intent_mismatch, decision_type_mismatch, action_count_mismatch, entity_key_mismatch |
| `scripts/analyze_shadow_router.py` | Pattern reference: existing analyzer script for shadow router (ST-001) |

---

## Implementation Plan

### Step 1: Create analyzer script

Create `scripts/analyze_partial_trust.py`:

**CLI interface:**
```
python3 scripts/analyze_partial_trust.py --risk-log <path> [--output-json <path>]
```

**Core logic:**
1. Read JSONL file line by line, parse each as JSON
2. Count records by `status` field: accepted_llm, fallback_deterministic, not_sampled, skipped, error
3. Count records by `reason_code` field
4. Compute metrics:
   - `acceptance_rate`: accepted_llm / (accepted_llm + fallback_deterministic). If denominator=0, null.
   - `intent_mismatch_rate`: among records where diff_summary is not None, fraction where diff_summary.intent_mismatch=true
   - `entity_key_mismatch_rate`: among records where diff_summary is not None, fraction where diff_summary.entity_key_mismatch=true
   - `latency_p50`, `latency_p95`: over records where latency_ms is not None (use sorted list, index-based percentile)
   - `error_rate`: error_count / total_records
   - `sampled_count`: records where sampled=true
5. Build report dict with all metrics
6. Print human-readable to stdout (formatted table/summary)
7. If `--output-json`, write JSON to file

**Privacy:** The script processes only aggregated fields (status, reason_code, latency_ms, diff_summary booleans). It never reads or outputs raw text fields even if present in JSONL.

**Edge cases:**
- Empty file or file not found → report with total_records=0, all rates null
- Malformed JSON lines → skip with warning to stderr, count as parse_errors in report

### Step 2: Create tests

Create `tests/test_analyze_partial_trust.py`:

**Test helpers:** Create synthetic JSONL records matching the schema from `_log_partial_trust`:
```python
def _record(status, reason_code, latency_ms=None, diff_summary=None, sampled=True):
    return {
        "trace_id": "t-1",
        "command_id": "c-1",
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
        "timestamp": "2026-02-08T12:00:00Z",
    }
```

**Tests:**
- `test_empty_jsonl` — empty file → total_records=0, acceptance_rate=None
- `test_single_accepted` — one accepted_llm → acceptance_rate=1.0
- `test_single_fallback` — one fallback_deterministic → acceptance_rate=0.0
- `test_mixed_statuses` — 3 accepted + 2 fallback + 5 not_sampled → status_breakdown correct, acceptance_rate=0.6
- `test_intent_mismatch_rate` — 2 records with diff_summary, 1 has intent_mismatch=True → rate=0.5
- `test_entity_mismatch_rate` — 2 records, 1 has entity_key_mismatch=True → rate=0.5
- `test_latency_percentiles` — latencies [10, 20, 30, 40, 50] → p50=30, p95≈50
- `test_reason_code_breakdown` — multiple reason codes → correct counts
- `test_error_rate` — 1 error in 10 records → 0.1
- `test_nonexistent_file` — file doesn't exist → total_records=0
- `test_privacy_no_raw_text` — records contain "молоко" in baseline_summary (shouldn't happen, but if it does) → report output does NOT contain "молоко"
- `test_json_output` — `--output-json` produces valid JSON file with all required fields

### Step 3: Create README

Create `scripts/README-partial-trust-analyzer.md` covering:
- Purpose and context
- Prerequisites (Python 3, no external deps)
- Usage examples
- Output format (all metric fields)
- Interpreting results (what acceptance_rate means, mismatch rate thresholds)
- Decision criteria for sampling progression

---

## Verification Commands

```bash
# 1. Analyzer tests pass
python3 -m pytest tests/test_analyze_partial_trust.py -v
# Expected: 12+ passed

# 2. Script runs on empty input
echo -n "" > /tmp/empty.jsonl
python3 scripts/analyze_partial_trust.py --risk-log /tmp/empty.jsonl
# Expected: exit 0, total_records=0

# 3. Script runs with sample data
python3 -c "
import json
records = [
    {'status':'accepted_llm','reason_code':'accepted','latency_ms':15,'sampled':True,'diff_summary':{'intent_mismatch':False,'entity_key_mismatch':False},'timestamp':'2026-02-08T12:00:00Z'},
    {'status':'fallback_deterministic','reason_code':'low_confidence','latency_ms':20,'sampled':True,'diff_summary':{'intent_mismatch':False,'entity_key_mismatch':True},'timestamp':'2026-02-08T12:01:00Z'},
    {'status':'not_sampled','reason_code':'not_sampled','sampled':False,'timestamp':'2026-02-08T12:02:00Z'},
]
with open('/tmp/sample_risk.jsonl','w') as f:
    for r in records: f.write(json.dumps(r)+'\n')
"
python3 scripts/analyze_partial_trust.py --risk-log /tmp/sample_risk.jsonl --output-json /tmp/report.json
# Expected: exit 0, human-readable output, /tmp/report.json created with all metric fields

# 4. Full test suite — no regressions
python3 -m pytest tests/ -v
# Expected: 109+ passed (109 existing + 12+ new)

# 5. README exists
test -f scripts/README-partial-trust-analyzer.md && echo "OK" || echo "MISSING"

# 6. Script file exists
test -f scripts/analyze_partial_trust.py && echo "OK" || echo "MISSING"
```

---

## Tests

| Test file | Test count | Type |
|-----------|-----------|------|
| `tests/test_analyze_partial_trust.py` (new) | 12+ | Unit |

---

## DoD Checklist

- [ ] Script `scripts/analyze_partial_trust.py` created and runs
- [ ] README `scripts/README-partial-trust-analyzer.md` created
- [ ] Tests `tests/test_analyze_partial_trust.py` pass
- [ ] Empty JSONL handled (exit 0, total_records=0)
- [ ] JSON output mode works (`--output-json`)
- [ ] Human-readable stdout output
- [ ] No raw user/LLM text in report output
- [ ] All metric fields present: total_records, status_breakdown, reason_code_breakdown, acceptance_rate, intent_mismatch_rate, entity_key_mismatch_rate, latency_p50, latency_p95, error_rate
- [ ] Full test suite passes (109+)
- [ ] No existing files modified

---

## Risks

| Risk | Mitigation |
|------|------------|
| Risk-log JSONL schema has fields not documented in v2.py | PLAN phase reads actual logged fields from phase3 test output |
| Percentile calculation edge cases (single record, all same latency) | Test both: single record → p50=p95=value; handle gracefully |
| argparse conflicts with pytest | Use `if __name__ == "__main__"` guard; tests import internal functions directly |

## Rollback

Delete `scripts/analyze_partial_trust.py`, `scripts/README-partial-trust-analyzer.md`, `tests/test_analyze_partial_trust.py`. No existing files modified.
