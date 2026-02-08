# Verification Report — INIT-2026Q2-partial-trust

**Date:** 2026-02-08
**Initiative:** `docs/planning/initiatives/INIT-2026Q2-partial-trust.md`
**Epic:** `docs/planning/epics/EP-003/epic.md`
**Reviewer:** Codex + Claude Code

---

## Summary

| Initiative AC | Description | Status | Evidence |
|--------------|-------------|--------|----------|
| AC1 | По умолчанию выключено | **Pass** | See AC1 section |
| AC2 | Работает только на allowlist intent | **Pass** | See AC2 section |
| AC3 | Deterministic fallback на любую ошибку | **Pass** | See AC3 section |
| AC4 | Risk-log и метрики регрессий | **Pass** | See AC4 section |

**Overall: All 4 ACs verified. Recommendation: update initiative status to Done after ST-006 and ST-007 complete.**

---

## AC1: По умолчанию выключено

### What was checked

Partial trust corridor must be disabled by default and enabled only via explicit feature flag.

### Evidence

**Feature flag (default disabled):**
- File: `routers/partial_trust_config.py:13`
- `partial_trust_enabled()` reads `PARTIAL_TRUST_ENABLED` env var, default `"false"`
- When disabled, all dependent functions return zero/None values:
  - `partial_trust_sample_rate()` → 0.0
  - `partial_trust_timeout_ms()` → 0
  - `partial_trust_profile_id()` → None

**All config defaults:**

| Variable | Default | Purpose |
|----------|---------|---------|
| `PARTIAL_TRUST_ENABLED` | `false` | Master switch |
| `PARTIAL_TRUST_INTENT` | `add_shopping_item` | Corridor intent |
| `PARTIAL_TRUST_SAMPLE_RATE` | `0.01` | Sampling rate (clamped 0..1) |
| `PARTIAL_TRUST_TIMEOUT_MS` | `200` | LLM timeout |
| `PARTIAL_TRUST_PROFILE_ID` | `""` | LLM policy profile |
| `PARTIAL_TRUST_RISK_LOG_PATH` | `logs/partial_trust_risk.jsonl` | Risk log path |

**Test evidence:**
- `tests/test_partial_trust_phase3.py::test_partial_trust_disabled_no_llm`
  - Sets `PARTIAL_TRUST_ENABLED=false`
  - Patches `generate_llm_candidate_with_meta` to raise on call
  - Asserts decision completes normally (LLM never called)

### Verdict: **Pass**

---

## AC2: Работает только на allowlist intent

### What was checked

Partial trust corridor must only operate for the `add_shopping_item` intent. All other intents must be rejected.

### Evidence

**Allowlist:**
- File: `routers/partial_trust_config.py:9` — `ALLOWED_CORRIDOR_INTENTS = {"add_shopping_item"}`
- `partial_trust_corridor_intent()` returns intent only if in allowlist

**Corridor check in pipeline:**
- File: `routers/v2.py:222` — `if corridor_intent is None or normalized.get("intent") != corridor_intent:` → skip with status="skipped", reason="corridor_mismatch"

**Acceptance rules (7-step validation):**
- File: `routers/partial_trust_acceptance.py:19` — `evaluate_candidate`
  - Line 27-28: corridor_disabled check
  - Line 29-30: candidate_missing check
  - Line 31-32: policy_disabled check
  - Line 33-36: corridor_mismatch (intent + job_type)
  - Line 37-38: invalid_schema (shape validation)
  - Line 39-40: invalid_item_name
  - Line 41-42: list_id_unknown
  - Line 43-44: low_confidence (threshold _MIN_CONFIDENCE=0.6, uses `>=`)

**Test evidence:**
- `tests/test_partial_trust_phase2.py::test_acceptance_rejects_wrong_intent` — intent=create_task → corridor_mismatch
- `tests/test_partial_trust_phase2.py::test_acceptance_rejects_invalid_schema` — wrong action → invalid_schema
- `tests/test_partial_trust_phase3.py::test_partial_trust_rejected_candidate` — wrong intent → fallback_deterministic
- `tests/test_partial_trust_edge_cases.py::test_confidence_059_rejected` — 0.59 → low_confidence
- `tests/test_partial_trust_edge_cases.py::test_confidence_060_accepted` — 0.60 → accepted
- `tests/test_partial_trust_edge_cases.py::test_list_id_known_accepted` — list-1 in context → accepted
- `tests/test_partial_trust_edge_cases.py::test_list_id_unknown_rejected` — unknown-list → list_id_unknown
- `tests/test_partial_trust_edge_cases.py::test_list_id_no_context_rejected` — no context → list_id_unknown

### Verdict: **Pass**

---

## AC3: Deterministic fallback на любую ошибку

### What was checked

Any LLM error, timeout, or unexpected exception must result in deterministic baseline decision being used.

### Evidence

**Error catch-all in pipeline:**
- File: `routers/v2.py:359-374` — `except Exception as exc:` → logs status="error", reason_code=type(exc).__name__, returns None (baseline used)

**Candidate generation error handling:**
- File: `routers/partial_trust_candidate.py:76-77` — `except Exception: return None, "llm_error"`
- Line 78-79: result is None → `(None, "timeout")`
- Line 80-81: result.status != "ok" → `(None, error_type or "llm_error")`

**Pipeline fallback on None candidate:**
- File: `routers/v2.py:298-313` — if candidate is None → logs status="fallback_deterministic", returns None (baseline)

**Timeout mechanism:**
- File: `routers/partial_trust_candidate.py:7` — ThreadPoolExecutor
- Line 22: `_EXECUTOR = ThreadPoolExecutor(max_workers=1)`
- Line 150: `future.result(timeout=timeout_ms / 1000.0)` → FutureTimeout caught → return None

**Test evidence:**
- `tests/test_partial_trust_phase2.py::test_candidate_generation_timeout` — TimeoutError → returns None
- `tests/test_partial_trust_edge_cases.py::test_v2_partial_trust_error_catchall` — RuntimeError in pipeline → baseline used + risk-log status="error"

### Verdict: **Pass**

---

## AC4: Risk-log и метрики регрессий

### What was checked

All partial trust decisions must be logged with structured data (no raw text). Risk-log must contain metrics for regression analysis.

### Evidence

**Risk logging implementation:**
- File: `routers/v2.py:422-452` — `_log_partial_trust` passes structured payload:
  - trace_id, command_id, corridor_intent, sample_rate, sampled
  - status, reason_code, latency_ms, model_meta
  - baseline_summary, llm_summary, diff_summary
- No raw user text or LLM output in payload

**Privacy guarantee:**
- File: `app/logging/partial_trust_risk_log.py:24` — comment: `# NO RAW USER OR LLM TEXT — PRIVACY GUARANTEE.`
- Summaries use only counts, lengths, booleans (see `_build_summary` in acceptance.py:145-171)

**Diff summary for regression analysis:**
- File: `routers/v2.py:409-419` — `_build_diff_summary` computes:
  - intent_mismatch, decision_type_mismatch, action_count_mismatch, entity_key_mismatch

**All decision paths logged:**
- skipped (corridor_mismatch, capability_mismatch, policy_disabled)
- not_sampled
- fallback_deterministic (with reason_code)
- accepted_llm
- error

**Test evidence:**
- `tests/test_partial_trust_phase2.py::test_acceptance_summary_no_raw_item_name` — "молоко" absent from summary
- `tests/test_partial_trust_phase3.py::test_partial_trust_not_sampled_logs` — "Купи" absent from log (line 82)
- `tests/test_partial_trust_phase3.py::test_partial_trust_accepts_candidate` — "бананы" absent from log (line 105)
- `tests/test_partial_trust_edge_cases.py::test_risk_log_privacy_all_paths` — verifies no raw text across accepted_llm, fallback, and error paths

### Verdict: **Pass**

---

## Verification Commands

To re-verify all ACs, run:

```bash
# Edge case tests (new)
python3 -m pytest tests/test_partial_trust_edge_cases.py -v
# Expected: 9 passed

# Existing partial trust tests
python3 -m pytest tests/test_partial_trust_phase2.py tests/test_partial_trust_phase3.py -v
# Expected: 9 passed (5 + 4)

# ADR-004 status
grep "Status" docs/adr/ADR-004-partial-trust-corridor.md
# Expected: "- Status: Accepted"

# Full test suite (no regressions)
python3 -m pytest tests/ -v
# Expected: 118 passed (109 existing + 9 new)
```

---

## Recommendation

**Partial GO — All 4 initiative ACs verified.**

Initiative closure pending completion of:
- ST-006: Regression metrics analyzer (initiative deliverable)
- ST-007: Rollout documentation (initiative deliverable)
