# Verification Report — INIT-2026Q1-assist-mode

**Date:** 2026-02-08
**Initiative:** `docs/planning/initiatives/INIT-2026Q1-assist-mode.md`
**Epic:** `docs/planning/epics/EP-002/epic.md`
**Reviewer:** Codex + Claude Code

---

## Summary

| Initiative AC | Description | Status | Evidence |
|--------------|-------------|--------|----------|
| AC1 | Assist-mode включается флагом | **Pass** | See AC1 section |
| AC2 | Baseline выбирает принимать подсказку или нет, правила документированы | **Pass** | See AC2 section |
| AC3 | При любой ошибке/таймауте LLM — baseline без деградации | **Pass** | See AC3 section |
| AC4 | Логи без raw user text / raw LLM output | **Pass** | See AC4 section |

**Overall: All 4 ACs verified. Recommendation: update initiative status to Done.**

---

## AC1: Assist-mode включается флагом

### What was checked

Assist-mode must be disabled by default and enabled only via explicit feature flags.

### Evidence

**Feature flags (all default to disabled):**
- File: `routers/assist/config.py`

| Flag | Default | Purpose |
|------|---------|---------|
| `ASSIST_MODE_ENABLED` | `false` | Master switch |
| `ASSIST_NORMALIZATION_ENABLED` | `false` | Normalization hints |
| `ASSIST_ENTITY_EXTRACTION_ENABLED` | `false` | Entity extraction hints (LLM) |
| `ASSIST_CLARIFY_ENABLED` | `false` | Clarify question hints |
| `ASSIST_AGENT_HINTS_ENABLED` | `false` | Agent-based entity hints |
| `ASSIST_AGENT_HINTS_SAMPLE_RATE` | `0.0` | Agent hint sampling (off) |

**Test evidence:**
- `tests/test_assist_mode.py::test_assist_disabled_no_impact`
  - Sets `ASSIST_MODE_ENABLED=false` → captures baseline decision
  - Sets `ASSIST_MODE_ENABLED=true` with all sub-flags off
  - Asserts `_stable_fields(baseline) == _stable_fields(decision)` — no impact

### Verdict: **Pass**

---

## AC2: Baseline выбирает принимать подсказку или нет, правила документированы

### What was checked

The deterministic baseline must decide whether to accept or reject each LLM hint.
Acceptance rules must be documented.

### Evidence

**Acceptance rules document:**
- File: `docs/contracts/assist-mode-acceptance-rules.md` (created by ST-003)
- Documents all acceptance/rejection conditions for normalization, entity extraction, and clarify hints

**Key acceptance functions:**
- `routers/assist/runner.py:567` — `_can_accept_normalized_text`
  - Rejects: empty candidate, length > max(original*2, 10), no token overlap
- `routers/assist/runner.py:584` — `_pick_matching_item`
  - Accepts only if candidate.lower() is substring of original_text.lower()
- `routers/assist/runner.py:593` — `_clarify_question_is_safe`
  - Rejects: empty, <5 chars, >200 chars, echo of original text, missing "?" for unknown intents

**Pipeline gate:**
- `routers/v2.py:198` — `_clarify_question`
  - Discards assist clarify question if `missing_fields` is not a subset of baseline's missing_fields

**Test evidence:**
- `tests/test_assist_mode.py::test_assist_entity_whitelist`
  - Entity hint with items=["хлеб"] and text "Купи" → item rejected (no substring match)
  - Falls through to clarify with missing_fields=["item.name"]
- `tests/test_assist_mode.py::test_assist_clarify_rejects_mismatched_missing_fields`
  - Clarify hint with mismatched missing_fields → default question used instead
  - Confirms the missing_fields subset gate in v2 pipeline

### Verdict: **Pass**

---

## AC3: При любой ошибке/таймауте LLM — baseline без деградации

### What was checked

Any LLM error or timeout must be caught silently. The baseline decision must remain unchanged.

### Evidence

**Timeout mechanism:**
- File: `routers/assist/runner.py`
- `ThreadPoolExecutor` imported (line 8), instantiated as `_EXECUTOR` (line 44)
- `_run_with_timeout(func, timeout_s)` (line 536) — uses `future.result(timeout=...)`
- Used in `_run_llm_task` (line 513) for all LLM hint calls
- Timeout config: `ASSIST_TIMEOUT_MS` (default 200ms), `ASSIST_AGENT_HINTS_TIMEOUT_MS` (default 120ms)

**Error propagation:**
- All errors caught inside `_run_*` functions
- On error: hint returns `None` or error status
- `apply_assist_hints` never raises — returns unchanged input on any failure

**Test evidence:**
- `tests/test_assist_mode.py::test_assist_timeout_fallback`
  - Patches `_run_normalization_hint` → returns `error_type="timeout"`
  - Asserts decision is identical to baseline (no degradation)
- `tests/test_assist_agent_hints.py::test_agent_hints_timeout_fallback`
  - `run_agent` raises `TimeoutError`
  - `apply_assist_hints` returns `item_name=None` (no degradation, baseline proceeds)

### Verdict: **Pass**

---

## AC4: Логи без raw user text / raw LLM output

### What was checked

Assist-mode logs must contain only summaries, counts, and metadata — no raw user text or raw LLM output.

### Evidence

**Logging implementation:**
- File: `routers/assist/runner.py:615` — `_log_step`
- Logs: step name, status, error_type, latency, agent hint metadata
- Does not include `text`, `question`, `item_name`, or other raw fields

**Test evidence:**
- `tests/test_assist_mode.py::test_assist_log_no_raw_text`
  - Verifies that log records do not contain the `text` field
- `tests/test_assist_agent_hints.py::test_agent_hints_privacy_in_logs`
  - Serializes all logs to JSON
  - Asserts the string "молоко" (raw user input) is absent from log output
  - Verifies `agent_hint_status` is present (structured metadata, not raw text)

### Verdict: **Pass**

---

## Verification Commands

To re-verify all ACs, run:

```bash
# AC1 + AC2 + AC3 + AC4: All assist-mode tests
python3 -m pytest tests/test_assist_mode.py tests/test_assist_agent_hints.py -v
# Expected: 14 passed

# AC2: Acceptance rules document exists
test -f docs/contracts/assist-mode-acceptance-rules.md && echo "EXISTS" || echo "MISSING"
# Expected: EXISTS

# AC1: Feature flags default to false
grep -n "false" routers/assist/config.py
# Expected: multiple lines showing default="false"

# Full test suite (no regressions)
python3 -m pytest tests/ -v
# Expected: 109 passed
```

---

## Recommendation

**GO — Update initiative status to Done.**

All 4 acceptance criteria are verified with code references, test evidence, and runnable commands. The acceptance rules document (ST-003) satisfies AC2's "правила документированы" requirement.
