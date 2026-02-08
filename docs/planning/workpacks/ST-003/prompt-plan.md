# Codex PLAN Prompt — ST-003: Document acceptance rules for assist-mode hints

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

## STOP-THE-LINE

If you discover something that contradicts the workpack assumptions, STOP and report it. Do not guess or improvise.

---

## Context

We are implementing ST-003: document the acceptance rules for assist-mode hints. This is a documentation-only story.

**Workpack:** `docs/planning/workpacks/ST-003/workpack.md`
**Deliverable:** `docs/contracts/assist-mode-acceptance-rules.md`

**IMPORTANT — Corrected file structure (from previous PLAN STOP-THE-LINE):**

All assist-mode logic lives in these files:
- `routers/assist/runner.py` — ALL acceptance/rejection functions (24KB, main file)
- `routers/assist/agent_scoring.py` — agent hint scoring/tiebreaking
- `routers/assist/config.py` — feature flags and defaults
- `routers/assist/types.py` — dataclasses (AssistHints, AssistApplication, etc.)

There are NO separate `normalization.py`, `entity_extraction.py`, `clarify.py`, or `agent_hints.py` files.

Key functions in `runner.py`:
- `_can_accept_normalized_text` (line 567) — normalization acceptance
- `_apply_normalization_hint` (line 374) — normalization application
- `_pick_matching_item` (line 584) — entity item matching
- `_apply_entity_hints` (line 405) — entity acceptance
- `_clarify_question_is_safe` (line 593) — clarify safety check
- `_select_clarify_hint` (line 484) — clarify selection
- `apply_assist_hints` (line 87) — main entry point

---

## Exploration Tasks

### Task 1: Read feature flags and config

```bash
cat routers/assist/config.py
```

**Report:** Table of all feature flags (env var, default, type, description).

### Task 2: Read types/dataclasses

```bash
cat routers/assist/types.py
```

**Report:** List all dataclasses and their fields. These define the structure of hints.

### Task 3: Read normalization acceptance rules

```bash
sed -n '567,582p' routers/assist/runner.py
sed -n '374,404p' routers/assist/runner.py
```

**Report:** For `_can_accept_normalized_text` and `_apply_normalization_hint`:
- List every acceptance/rejection condition
- What happens on acceptance (re-detection, re-extraction)
- File:line for each condition

### Task 4: Read entity extraction acceptance rules

```bash
sed -n '584,592p' routers/assist/runner.py
sed -n '405,483p' routers/assist/runner.py
```

**Report:** For `_pick_matching_item` and `_apply_entity_hints`:
- When do entity hints apply (which intent, which fields missing)
- Substring check logic
- Agent vs LLM hint priority
- File:line for each condition

### Task 5: Read clarify acceptance rules

```bash
sed -n '593,614p' routers/assist/runner.py
sed -n '484,505p' routers/assist/runner.py
```

**Report:** For `_clarify_question_is_safe` and `_select_clarify_hint`:
- Length checks (min/max)
- Echo prevention
- Intent-specific behavior (known vs unknown intents)
- missing_fields handling
- File:line for each condition

### Task 6: Read agent hints scoring and selection

```bash
cat routers/assist/agent_scoring.py
sed -n '186,310p' routers/assist/runner.py
```

**Report:** For agent hint pipeline:
- `_run_agent_entity_hint` flow
- `_load_agent_candidates` — allowlist filtering, capability matching
- Scoring rules (from agent_scoring.py)
- Tiebreaking rules
- Agent vs LLM priority logic
- File:line for each

### Task 7: Read timeout and error handling

```bash
sed -n '536,540p' routers/assist/runner.py
rg -n "timeout\|_run_with_timeout\|ASSIST_TIMEOUT" routers/assist/runner.py
```

**Report:** Timeout mechanism, fallback behavior, how errors propagate (or don't).

### Task 8: Read pipeline integration in v2.py

```bash
rg -n "assist\|_clarify_question\|missing_fields" routers/v2.py | head -30
sed -n '190,210p' routers/v2.py
```

**Report:** Where assist is called in pipeline. How `_clarify_question` checks missing_fields subset before replacing default question.

### Task 9: Read main entry point

```bash
sed -n '87,132p' routers/assist/runner.py
```

**Report:** How `apply_assist_hints` orchestrates normalization → entity → clarify. Error handling at top level.

---

## Expected Output

Produce a numbered report (Task 1 through Task 9) with findings for each task. Include:
- Complete list of acceptance/rejection rules with file:line references
- Feature flags table with defaults
- Agent scoring rules
- Pipeline integration details
- Any discrepancies or STOP-THE-LINE issues
