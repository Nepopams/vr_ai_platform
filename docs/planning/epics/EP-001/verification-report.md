# Verification Report — INIT-2026Q1-shadow-router

**Date:** 2026-02-08
**Initiative:** `docs/planning/initiatives/INIT-2026Q1-shadow-router.md`
**Epic:** `docs/planning/epics/EP-001/epic.md`
**Reviewer:** Codex + Claude Code

---

## Summary

| Initiative AC | Description | Status | Evidence |
|--------------|-------------|--------|----------|
| AC1 | Shadow режим выключен по умолчанию и включается флагом | **Pass** | See AC1 section |
| AC2 | При ошибке/таймауте LLM baseline работает как раньше | **Pass** | See AC2 section |
| AC3 | JSONL-лог не содержит raw user text и raw LLM output | **Pass** | See AC3 section |
| AC4 | Воспроизводимый скрипт анализа golden-dataset и README | **Pass** | See AC4 section |

**Overall: All 4 ACs verified. Recommendation: update initiative status to Done.**

---

## AC1: Shadow режим выключен по умолчанию и включается флагом

### What was checked

The shadow router must be disabled by default and enabled only via an explicit feature flag.

### Evidence

**Feature flag configuration:**
- File: `routers/shadow_config.py:9`
- Env var: `SHADOW_ROUTER_ENABLED`
- Default: `"false"` (disabled)
- Parsing: `os.getenv("SHADOW_ROUTER_ENABLED", "false").strip().lower() in {"1", "true", "yes"}`

**Conditional invocation in pipeline:**
- File: `routers/v2.py:33` — `from routers.shadow_router import start_shadow_router`
- File: `routers/v2.py:40` — `start_shadow_router(command, normalized)` called in pipeline
- File: `routers/shadow_router.py` — first check: `if not shadow_router_enabled(): return`

**Test evidence:**
- `tests/test_shadow_router.py::test_shadow_router_no_impact`
  - Compares `decision_without_shadow` and `decision_with_shadow` via `_stable_fields`
  - Asserts equality: shadow does not affect the decision
- `tests/test_shadow_router.py::test_shadow_router_policy_disabled`
  - With `LLM_POLICY_ENABLED=false` and `SHADOW_ROUTER_ENABLED=true`
  - Verifies LLM is not called
  - Verifies log contains `status == "skipped"` and `error_type == "policy_disabled"`

### Verdict: **Pass**

---

## AC2: При ошибке/таймауте LLM baseline работает как раньше

### What was checked

Any error or timeout in the shadow LLM call must be swallowed. The baseline decision must remain unchanged.

### Evidence

**Error handling in shadow router:**
- File: `routers/shadow_router.py`
- ThreadPoolExecutor: imported (line 6), instantiated as `_EXECUTOR` (line 22)
- `_submit_shadow_task` (lines 47-55): try/except catches executor errors, logs `error_type="executor_unavailable"`
- `_consume_future_error` (lines 61-66): try/except swallows exceptions from futures
- Timeout check (lines 96-103): `if latency_ms > timeout_ms` → logs `error_type="timeout_exceeded"` and returns
- General exception handler (line 113+): `except Exception as exc` → logs `error_type=type(exc).__name__`

**Key design:** Shadow router runs in a separate thread. Errors are caught at every level. The `decide()` return value is never modified by shadow results.

**Test evidence:**
- `tests/test_shadow_router.py::test_shadow_router_no_impact`
  - Baseline decision with shadow off == decision with shadow on
  - Asserts via `_stable_fields` equality
- `tests/test_shadow_router.py::test_shadow_router_timeout_no_impact`
  - Forces `shadow_router_timeout_ms = 0` and manipulates `monotonic`
  - Asserts decision is unchanged after timeout
  - Verifies log: `status == "error"`, `error_type == "timeout_exceeded"`

### Verdict: **Pass**

---

## AC3: JSONL-лог не содержит raw user text и raw LLM output

### What was checked

The JSONL log must contain only structured summaries, counts, and metadata — no raw user text or raw LLM output.

### Evidence

**Logger implementation:**
- File: `app/logging/shadow_router_log.py`
- `append_shadow_router_log()` writes a fixed payload as JSONL with a timestamp
- No `text` field is added by the logger

**Entity summarization:**
- File: `routers/shadow_router.py` — function `_summarize_entities`
- Returns `{"keys": [...], "counts": {...}}` — only entity key names and counts
- Raw entity values (item names, text) are never included

**Log fields (verified by PLAN):**
`timestamp`, `trace_id`, `command_id`, `router_version`, `router_strategy`, `status`, `latency_ms`, `error_type`, `suggested_intent`, `missing_fields`, `clarify_question`, `entities_summary`, `confidence`, `model_meta`, `baseline_intent`, `baseline_action`, `baseline_job_type`

**Test evidence:**
- `tests/test_shadow_router.py::test_shadow_router_logging_shape`
  - Verifies all required keys present in log record
  - **Explicitly asserts: `assert "text" not in logged`**
  - Confirms raw user text is excluded from the log

### Verdict: **Pass**

---

## AC4: Воспроизводимый скрипт анализа golden-dataset и README

### What was checked

A reproducible analyzer script, golden dataset, README, and tests must exist.

### Evidence

Delivered by ST-001 (reviewed and merged):

| Deliverable | Path | Status |
|-------------|------|--------|
| Analyzer script | `scripts/analyze_shadow_router.py` | Exists |
| README | `scripts/README-shadow-analyzer.md` | Exists |
| Golden dataset | `skills/graph-sanity/fixtures/golden_dataset.json` (14 entries) | Exists |
| Unit tests | `tests/test_analyze_shadow_router.py` (10 tests, all passing) | Exists |

**Additional verification:**
- `python3 scripts/analyze_shadow_router.py --self-test` → `self-test ok`
- `python3 -m pytest tests/test_analyze_shadow_router.py -v` → `10 passed`

### Verdict: **Pass**

---

## Verification Commands

To re-verify all ACs, run:

```bash
# AC1: Shadow router tests (includes no-impact + policy-disabled)
python3 -m pytest tests/test_shadow_router.py -v
# Expected: 4 passed

# AC1: Confirm default is false
grep -n "SHADOW_ROUTER_ENABLED" routers/shadow_config.py
# Expected: default="false"

# AC2: Timeout test specifically
python3 -m pytest tests/test_shadow_router.py::test_shadow_router_timeout_no_impact -v
# Expected: 1 passed

# AC3: Log shape test (asserts no raw text)
python3 -m pytest tests/test_shadow_router.py::test_shadow_router_logging_shape -v
# Expected: 1 passed

# AC4: ST-001 deliverables exist
test -f scripts/analyze_shadow_router.py && test -f scripts/README-shadow-analyzer.md && test -f skills/graph-sanity/fixtures/golden_dataset.json && test -f tests/test_analyze_shadow_router.py && echo "ALL PRESENT" || echo "MISSING"
# Expected: ALL PRESENT

# AC4: Analyzer self-test
python3 scripts/analyze_shadow_router.py --self-test
# Expected: self-test ok

# Full test suite (no regressions)
python3 -m pytest tests/ -v
# Expected: 109 passed
```

---

## Recommendation

**GO — Update initiative status to Done.**

All 4 acceptance criteria are verified with code references, test evidence, and runnable commands. No gaps found.
