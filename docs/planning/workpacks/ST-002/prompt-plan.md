# Codex PLAN Prompt — ST-002: Retroactive verification of shadow-router AC1-AC3

## Role

You are a read-only explorer. You MUST NOT edit, create, or delete any files.
You MUST NOT install packages, run builds, or access the network.

## Allowed commands (whitelist)

- `ls`, `find`
- `cat`, `head`, `tail`
- `rg`, `grep`
- `sed -n`
- `git status`, `git diff`

## Forbidden

- Any file modifications (edit/write/move/delete)
- `pip install`, `npm install`, or any package management
- `git commit`, `git push`, or any git mutations
- Network access of any kind

## Environment

- Python binary: `python3` (NOT `python`)
- Tests: `python3 -m pytest` or `.venv/bin/pytest`

## STOP-THE-LINE

If you discover something that contradicts the workpack assumptions, STOP and report it. Do not guess or improvise.

---

## Context

We are implementing ST-002: a documentation-only story that produces a verification report for the shadow-router initiative (INIT-2026Q1-shadow-router) AC1-AC3.

**Workpack:** `docs/planning/workpacks/ST-002/workpack.md`

**Initiative AC to verify:**
1. AC1: Shadow режим выключен по умолчанию и включается флагом
2. AC2: При ошибке/таймауте LLM baseline работает как раньше
3. AC3: JSONL-лог не содержит raw user text и raw LLM output
4. AC4: Воспроизводимый скрипт анализа golden-dataset (already closed by ST-001)

**Deliverables (1 new file, 1 modification):**
1. `docs/planning/epics/EP-001/verification-report.md` — verification report
2. `docs/planning/initiatives/INIT-2026Q1-shadow-router.md` — status update

---

## Exploration Tasks

### Task 1: Gather AC1 evidence — shadow mode off by default

Read config and feature flag mechanism.

```bash
rg -n "SHADOW_ROUTER_ENABLED" routers/
rg -n "SHADOW_ROUTER_ENABLED" app/ graphs/
cat routers/shadow_router.py | head -40
```

**Report:** Exact env var name, default value, file:line where it's read.

### Task 2: Gather AC1 evidence — where shadow is called conditionally

```bash
rg -n "shadow" routers/v2.py
```

**Report:** File:line where shadow router is invoked, and how the flag gates it.

### Task 3: Gather AC1 evidence — tests for disabled/no-impact

```bash
rg -n "def test_shadow_router_no_impact\|def test_shadow_router_policy_disabled" tests/test_shadow_router.py
sed -n '/def test_shadow_router_no_impact/,/^def /p' tests/test_shadow_router.py
sed -n '/def test_shadow_router_policy_disabled/,/^def /p' tests/test_shadow_router.py
```

**Report:** Test names, what each asserts, key assertions (e.g. "decision unchanged").

### Task 4: Gather AC2 evidence — error/timeout handling

```bash
rg -n "try\|except\|timeout\|ThreadPool\|futures" routers/shadow_router.py
cat routers/shadow_router.py
```

**Report:** Error handling mechanism (try/except, ThreadPoolExecutor, timeout value), file:line for each. Confirm errors are swallowed and don't affect return value.

### Task 5: Gather AC2 evidence — timeout test

```bash
sed -n '/def test_shadow_router_timeout_no_impact/,/^def /p' tests/test_shadow_router.py
```

**Report:** What the test does, what it asserts about baseline decision after timeout.

### Task 6: Gather AC3 evidence — no raw text in JSONL logs

```bash
cat app/logging/shadow_router_log.py
rg -n "_summarize_entities\|summarize" routers/shadow_router.py
```

**Report:** List all JSONL fields logged. Confirm which fields contain only summaries/counts (not raw text). Identify `_summarize_entities` function and what it returns.

### Task 7: Gather AC3 evidence — logging shape test

```bash
sed -n '/def test_shadow_router_logging_shape/,/^def /p' tests/test_shadow_router.py
```

**Report:** What the test asserts about log shape. Does it verify absence of raw text?

### Task 8: Confirm AC4 evidence — ST-001 deliverables exist

```bash
ls -la scripts/analyze_shadow_router.py scripts/README-shadow-analyzer.md skills/graph-sanity/fixtures/golden_dataset.json tests/test_analyze_shadow_router.py
```

**Report:** Confirm all 4 ST-001 deliverables exist.

### Task 9: Read current initiative status

```bash
head -10 docs/planning/initiatives/INIT-2026Q1-shadow-router.md
```

**Report:** Current status line. Confirm it says "Proposed".

---

## Expected Output

Produce a numbered report (Task 1 through Task 9) with findings for each task. Include:
- Exact file paths, line numbers, function names, env var names, default values
- Test names and key assertions
- Any discrepancies with the workpack assumptions
- STOP-THE-LINE issues (if any)
- Recommended final initiative status (Done vs Verified)
