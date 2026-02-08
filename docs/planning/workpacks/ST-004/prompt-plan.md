# Codex PLAN Prompt — ST-004: Retroactive verification of assist-mode initiative ACs

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

We are implementing ST-004: verification report for assist-mode initiative (INIT-2026Q1-assist-mode) AC1-AC4.

**Workpack:** `docs/planning/workpacks/ST-004/workpack.md`

**Initiative ACs:**
1. AC1: Assist-mode включается флагом
2. AC2: Baseline выбирает принимать подсказку или нет (правила документированы)
3. AC3: При любой ошибке/таймауте LLM — baseline без деградации
4. AC4: Логи без raw user text / raw LLM output

**Key files (from ST-003 PLAN):**
- `routers/assist/config.py` — feature flags
- `routers/assist/runner.py` — all acceptance logic
- `routers/assist/agent_scoring.py` — scoring
- `docs/contracts/assist-mode-acceptance-rules.md` — rules doc (ST-003)
- `tests/test_assist_mode.py` — 5 tests
- `tests/test_assist_agent_hints.py` — 9 tests

---

## Exploration Tasks

### Task 1: AC1 — feature flags with defaults

```bash
cat routers/assist/config.py
```

**Report:** List all flags with defaults. Confirm all default to false/disabled.

### Task 2: AC1 — test disabled has no impact

```bash
sed -n '/def test_assist_disabled_no_impact/,/^def /p' tests/test_assist_mode.py
```

**Report:** What the test asserts.

### Task 3: AC2 — acceptance rules document exists

```bash
test -f docs/contracts/assist-mode-acceptance-rules.md && echo "EXISTS" || echo "MISSING"
head -20 docs/contracts/assist-mode-acceptance-rules.md
```

**Report:** Confirm document exists and has expected structure.

### Task 4: AC2 — key acceptance functions exist

```bash
rg -n "def _can_accept_normalized_text|def _pick_matching_item|def _clarify_question_is_safe" routers/assist/runner.py
```

**Report:** File:line for each function.

### Task 5: AC2 — tests for acceptance rules

```bash
sed -n '/def test_assist_entity_whitelist/,/^def /p' tests/test_assist_mode.py
sed -n '/def test_assist_clarify_rejects_mismatched_missing_fields/,/^def /p' tests/test_assist_mode.py
```

**Report:** What each test asserts about acceptance/rejection.

### Task 6: AC3 — timeout mechanism

```bash
rg -n "ThreadPoolExecutor\|_run_with_timeout\|ASSIST_TIMEOUT" routers/assist/runner.py | head -10
```

**Report:** Timeout implementation details.

### Task 7: AC3 — timeout fallback tests

```bash
sed -n '/def test_assist_timeout_fallback/,/^def /p' tests/test_assist_mode.py
sed -n '/def test_agent_hints_timeout_fallback/,/^def /p' tests/test_assist_agent_hints.py
```

**Report:** What each test asserts about fallback behavior.

### Task 8: AC4 — logging uses summaries only

```bash
rg -n "def _log_step" routers/assist/runner.py
sed -n '/_log_step/,/^def /p' routers/assist/runner.py | head -30
```

**Report:** What `_log_step` logs. Confirm no raw text fields.

### Task 9: AC4 — privacy tests

```bash
sed -n '/def test_assist_log_no_raw_text/,/^def /p' tests/test_assist_mode.py
sed -n '/def test_agent_hints_privacy_in_logs/,/^def /p' tests/test_assist_agent_hints.py
```

**Report:** What each test asserts about log privacy.

### Task 10: Current initiative status

```bash
head -10 docs/planning/initiatives/INIT-2026Q1-assist-mode.md
```

**Report:** Current status. Confirm "Proposed".

---

## Expected Output

Produce a numbered report (Task 1 through Task 10) with:
- Evidence for each AC with file:line references
- Any STOP-THE-LINE issues
- Recommended initiative status
