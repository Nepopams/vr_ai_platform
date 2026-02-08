# Codex PLAN Prompt — ST-005: Verify and Harden Partial Trust Scaffolding

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

We are implementing ST-005: verification report + edge case tests for partial trust scaffolding.

**Workpack:** `docs/planning/workpacks/ST-005/workpack.md`

**Initiative ACs:**
1. AC1: По умолчанию выключено
2. AC2: Работает только на allowlist intent
3. AC3: Deterministic fallback на любую ошибку
4. AC4: Risk-log и метрики регрессий

**Key files (verified by Claude):**
- `routers/partial_trust_config.py` — feature flags (PARTIAL_TRUST_ENABLED defaults "false")
- `routers/partial_trust_acceptance.py` — acceptance rules (evaluate_candidate, _MIN_CONFIDENCE=0.6)
- `routers/partial_trust_types.py` — LLMDecisionCandidate, PartialTrustMeta
- `routers/partial_trust_sampling.py` — stable_sample (SHA-256 bucketing)
- `routers/partial_trust_candidate.py` — generate_llm_candidate_with_meta, ThreadPoolExecutor
- `routers/v2.py` (lines 206-452) — _maybe_apply_partial_trust, _log_partial_trust, error catch-all
- `app/logging/partial_trust_risk_log.py` — append_partial_trust_risk_log
- `tests/test_partial_trust_phase2.py` — 5 unit tests, _candidate() helper
- `tests/test_partial_trust_phase3.py` — 4 integration tests, _command(), _read_log() helpers
- `docs/adr/ADR-004-partial-trust-corridor.md` — Status: Accepted

---

## Exploration Tasks

### Task 1: AC1 — feature flags with defaults

```bash
cat routers/partial_trust_config.py
```

**Report:** List all flags with defaults. Confirm PARTIAL_TRUST_ENABLED defaults to "false".

### Task 2: AC1 — test disabled has no LLM call

```bash
sed -n '/def test_partial_trust_disabled_no_llm/,/^def \|^$/p' tests/test_partial_trust_phase3.py
```

**Report:** What the test asserts.

### Task 3: AC2 — allowlist intent check

```bash
rg -n "ALLOWED_CORRIDOR_INTENTS|corridor_intent" routers/partial_trust_config.py routers/partial_trust_acceptance.py routers/v2.py
```

**Report:** File:line for each allowlist/corridor check. Confirm only `add_shopping_item` is in allowlist.

### Task 4: AC2 — acceptance rules functions

```bash
rg -n "def evaluate_candidate|def _validate_shape|def _validate_item_name|def _validate_list_id|def _passes_confidence" routers/partial_trust_acceptance.py
```

**Report:** File:line for each function.

### Task 5: AC2 — confidence threshold value

```bash
rg -n "_MIN_CONFIDENCE" routers/partial_trust_acceptance.py
```

**Report:** Confirm threshold is 0.6. Confirm `_passes_confidence` uses `>=` (line 120: `candidate.confidence >= _MIN_CONFIDENCE`).

### Task 6: AC2 — list_id validation logic

```bash
sed -n '/def _validate_list_id/,/^def /p' routers/partial_trust_acceptance.py
sed -n '/def _collect_list_ids/,/^def \|^$/p' routers/partial_trust_acceptance.py
```

**Report:** Describe logic: list_id=None → True, list_id present but no context → False, list_id not in known_lists → False. Confirm context structure: `context.household.shopping_lists[].list_id`.

### Task 7: AC3 — error catch-all in v2 pipeline

```bash
sed -n '/except Exception/,/return None/p' routers/v2.py | head -20
```

**Report:** Confirm Exception catch-all at line 359 returns None and logs status="error".

### Task 8: AC3 — candidate generation error handling

```bash
sed -n '/def generate_llm_candidate_with_meta/,/^def /p' routers/partial_trust_candidate.py | head -30
```

**Report:** Confirm all exceptions return (None, error_type).

### Task 9: AC4 — risk log fields (no raw text)

```bash
sed -n '/def _log_partial_trust/,/^$/p' routers/v2.py
```

**Report:** List all fields logged. Confirm no raw user text or LLM output in log payload.

### Task 10: AC4 — existing privacy tests

```bash
rg -n "молоко\|бананы\|Купи" tests/test_partial_trust_phase2.py tests/test_partial_trust_phase3.py
```

**Report:** Where raw text appears (test input only) and where it's asserted absent (log output assertions).

### Task 11: Existing test helpers for reuse

```bash
sed -n '/^def _candidate/,/^def \|^$/p' tests/test_partial_trust_phase2.py
sed -n '/^def _command/,/^def \|^$/p' tests/test_partial_trust_phase3.py
sed -n '/^def _read_log/,/^def \|^$/p' tests/test_partial_trust_phase3.py
sed -n '/^def _candidate/,/^def \|^$/p' tests/test_partial_trust_phase3.py
```

**Report:** Document helper signatures and default values for reuse in edge case tests.

### Task 12: ADR-004 status confirmed

```bash
head -5 docs/adr/ADR-004-partial-trust-corridor.md
grep "ADR-004-P" docs/_indexes/adr-index.md
```

**Report:** Confirm Status: Accepted and index reflects "accepted".

### Task 13: Check for existing edge case tests

```bash
ls tests/test_partial_trust_edge_cases.py 2>/dev/null && echo "EXISTS" || echo "NOT_FOUND"
rg -n "confidence.*0\.59\|confidence.*0\.60\|list_id_unknown\|error_catchall\|privacy_all_paths" tests/ 2>/dev/null || echo "no matches"
```

**Report:** Confirm no existing edge case test file and no existing tests for these specific cases.

---

## Expected Output

Produce a numbered report (Task 1 through Task 13) with:
- Evidence for each AC with file:line references
- Helper function signatures for reuse
- Any STOP-THE-LINE issues
- Confirmation that workpack file paths and assumptions are correct
