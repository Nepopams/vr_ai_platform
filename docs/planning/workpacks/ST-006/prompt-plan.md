# Codex PLAN Prompt — ST-006: Regression Metrics Analyzer for Partial Trust Risk-Log

## Role

You are a read-only explorer. You MUST NOT edit, create, or delete any files.

## Allowed commands (whitelist)

- `ls`, `find`
- `cat`, `head`, `tail`
- `rg`, `grep`
- `sed -n`
- `git status`, `git diff`

## Forbidden

- Any file modifications
- Package management, network access
- `git commit`, `git push`

## Environment

- Python binary: `python3` (NOT `python`)

## STOP-THE-LINE

If you discover something that contradicts the workpack assumptions, STOP and report it.

---

## Context

We are implementing ST-006: a regression metrics analyzer script that reads partial trust risk-log JSONL and produces a structured report.

**Workpack:** `docs/planning/workpacks/ST-006/workpack.md`

**Key files (verified by Claude):**
- `app/logging/partial_trust_risk_log.py` — JSONL appender (json.dumps per line)
- `routers/v2.py` (lines 422-452) — `_log_partial_trust` defines JSONL fields
- `routers/v2.py` (lines 409-419) — `_build_diff_summary` defines diff_summary fields
- `scripts/analyze_shadow_router.py` — existing analyzer script (pattern reference for ST-001)
- `tests/test_analyze_shadow_router.py` — existing analyzer tests (pattern reference)

---

## Exploration Tasks

### Task 1: Risk-log JSONL schema

```bash
sed -n '/def _log_partial_trust/,/^$/p' routers/v2.py
```

**Report:** List all fields in the JSONL payload. Confirm: trace_id, command_id, corridor_intent, sample_rate, sampled, status, reason_code, latency_ms, model_meta, baseline_summary, llm_summary, diff_summary, timestamp.

### Task 2: diff_summary fields

```bash
sed -n '/def _build_diff_summary/,/^$/p' routers/v2.py
```

**Report:** List all diff_summary fields: intent_mismatch, decision_type_mismatch, action_count_mismatch, entity_key_mismatch. All are booleans.

### Task 3: Status values used in pipeline

```bash
rg -n "status=" routers/v2.py | grep "_log_partial_trust\|status="
```

**Report:** List all possible status values: skipped, not_sampled, fallback_deterministic, accepted_llm, error.

### Task 4: Existing shadow router analyzer (pattern reference)

```bash
head -50 scripts/analyze_shadow_router.py
```

**Report:** Note CLI pattern (argparse), output format, module structure for reuse in ST-006.

### Task 5: Existing shadow router analyzer tests (pattern reference)

```bash
head -60 tests/test_analyze_shadow_router.py
```

**Report:** Note test helper patterns, fixture generation, assertions for reuse in ST-006.

### Task 6: Shadow router analyzer full structure

```bash
rg -n "^def " scripts/analyze_shadow_router.py
```

**Report:** List all public functions. Note which ones can serve as pattern for ST-006.

### Task 7: Risk-log append mechanism

```bash
cat app/logging/partial_trust_risk_log.py
```

**Report:** Confirm JSONL format (one json.dumps per line), timestamp auto-added. Note resolve_log_path() for default path.

### Task 8: Existing scripts directory

```bash
ls scripts/
```

**Report:** List existing scripts. Confirm `analyze_partial_trust.py` does NOT yet exist.

### Task 9: Phase3 test log output (sample JSONL structure)

```bash
sed -n '/def test_partial_trust_accepts_candidate/,/^def \|^$/p' tests/test_partial_trust_phase3.py
```

**Report:** Note what fields appear in logged JSONL entries. Confirm `_read_log` reads last line as JSON.

### Task 10: Check standard library availability for percentiles

```bash
python3 -c "import statistics; print(statistics.median([1,2,3]))"
python3 -c "import statistics; print(statistics.quantiles([1,2,3,4,5], n=20))"
```

**Report:** Confirm `statistics` module available. Note if `quantiles` is available (Python 3.8+) for p50/p95 calculation.

---

## Expected Output

Produce a numbered report (Task 1 through Task 10) with:
- JSONL schema (all fields)
- All possible status values
- Shadow router analyzer patterns for reuse
- Any STOP-THE-LINE issues
- Confirmation that workpack assumptions are correct
