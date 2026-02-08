# Codex APPLY Prompt — ST-003: Document acceptance rules for assist-mode hints

## Role

You are an implementation agent. Create ONLY the file listed below.
Do not touch any code files. This is a documentation-only story.

## Environment

- Python binary: `python3` (NOT `python`)

## STOP-THE-LINE

If you need to modify any file not listed in "Allowed files", STOP and report.

## Allowed files

- `docs/contracts/assist-mode-acceptance-rules.md` (CREATE)

## Forbidden

- Any file under `routers/`, `app/`, `tests/`, `scripts/`, `agents/`, `graphs/`
- Any `.py` file
- `git commit`, `git push`

---

## Step 1: Create acceptance rules document

Create `docs/contracts/assist-mode-acceptance-rules.md` with EXACTLY this content:

```markdown
# Assist-Mode Acceptance Rules

**Status:** Current
**Initiative:** `docs/planning/initiatives/INIT-2026Q1-assist-mode.md`
**Source code:** `routers/assist/` (runner.py, agent_scoring.py, config.py, types.py)

---

## Overview

Assist-mode provides LLM-generated hints to improve the deterministic baseline pipeline.
The fundamental guarantee: **the baseline always makes the final decision**. LLM hints are
suggestions that the deterministic layer accepts or rejects based on strict rules documented below.

Assist-mode covers three hint types:
1. **Normalization** — canonical form of user text
2. **Entity extraction** — item names for shopping commands
3. **Clarify suggestor** — improved clarification questions

Each type has its own feature flag. All flags are off by default.

---

## Feature Flags

All flags read from environment variables. Default = disabled.

| Env var | Default | Type | Description |
|---------|---------|------|-------------|
| `ASSIST_MODE_ENABLED` | `false` | bool | Master switch for all assist-mode |
| `ASSIST_NORMALIZATION_ENABLED` | `false` | bool | Normalization hint |
| `ASSIST_ENTITY_EXTRACTION_ENABLED` | `false` | bool | Entity extraction hint (LLM) |
| `ASSIST_CLARIFY_ENABLED` | `false` | bool | Clarify question hint |
| `ASSIST_TIMEOUT_MS` | `200` | int | Timeout for LLM hint calls (ms) |
| `ASSIST_LOG_PATH` | `logs/assist.jsonl` | str | JSONL log path |
| `ASSIST_AGENT_HINTS_ENABLED` | `false` | bool | Agent-based entity hints |
| `ASSIST_AGENT_HINTS_AGENT_ID` | `""` | str | Force specific agent (override) |
| `ASSIST_AGENT_HINTS_CAPABILITY` | `extract_entities.shopping` | str | Required capability |
| `ASSIST_AGENT_HINTS_ALLOWLIST` | `""` | list | Allowed agent IDs (CSV) |
| `ASSIST_AGENT_HINTS_SAMPLE_RATE` | `0.0` | float | Sampling rate (0.0-1.0) |
| `ASSIST_AGENT_HINTS_TIMEOUT_MS` | `120` | int | Timeout for agent hints (ms) |

Source: `routers/assist/config.py`

---

## Pipeline Integration

Assist runs inside `RouterV2Pipeline.decide()` (`routers/v2.py`):

```
1. normalized = self.normalize(command)
2. start_shadow_router(command, normalized)
3. assist = apply_assist_hints(command, normalized)    ← assist entry point
4. plan = self.plan(assist.normalized, command)
5. baseline = self.validate_and_build(plan, assist.normalized, command, assist)
6. invoke_shadow_agents(...)
7. _maybe_apply_partial_trust(...)
```

The `apply_assist_hints` function (`routers/assist/runner.py:87`) orchestrates:
1. If `ASSIST_MODE_ENABLED=false` → return unchanged input
2. Build LLM hints (normalization, entity, clarify) per individual flags
3. Apply in order:
   - `_apply_normalization_hint`
   - `_run_agent_entity_hint`
   - `_apply_entity_hints` (with agent hint result)
   - `_select_clarify_hint`
4. Return `AssistApplication` (modified normalized text + clarify question/missing_fields)

Errors inside any `_run_*` or `_apply_*` function are caught internally — never propagated to caller.

---

## 1. Normalization Acceptance Rules

**Purpose:** Improve the canonical form of user text before intent detection.

**Source:** `routers/assist/runner.py`
- `_can_accept_normalized_text` (line 567)
- `_apply_normalization_hint` (line 374)

### Rejection conditions

| # | Condition | Result | Code ref |
|---|-----------|--------|----------|
| N1 | Hint is `None` or `normalized_text` missing | Reject (log: `error_type="no_hint"`) | `runner.py:_apply_normalization_hint` |
| N2 | Candidate (stripped) is empty | Reject | `runner.py:_can_accept_normalized_text` |
| N3 | `len(candidate) > max(len(original) * 2, 10)` | Reject (too long) | `runner.py:_can_accept_normalized_text` |
| N4 | No token overlap between original and candidate | Reject (unrelated text) | `runner.py:_can_accept_normalized_text` |

Token overlap: `_tokens(text)` splits on whitespace and lowercases. Overlap = `bool(original_tokens & candidate_tokens)`.

### On acceptance

When all checks pass:
1. `text` is replaced with the candidate
2. `intent` is re-detected via `detect_intent(candidate)` (or `clarify_needed`)
3. If intent is `add_shopping_item`: `item_name` = `fallback_extract_item_name(candidate)`
4. If intent is `create_task`: `task_title` = candidate
5. Log: `accepted=True`

---

## 2. Entity Extraction Acceptance Rules

**Purpose:** Fill missing `item_name` for shopping commands using LLM or agent hints.

**Source:** `routers/assist/runner.py`
- `_pick_matching_item` (line 584)
- `_apply_entity_hints` (line 405)

### When entity hints apply

Entity hints are evaluated only when ALL conditions are true:
- `intent == "add_shopping_item"`
- `item_name` is not already set

### Item matching rule

`_pick_matching_item(items, original_text)`:
- For each item: `candidate = item.strip()`
- **Accept** if `candidate.lower()` is a substring of `original_text.lower()`
- Returns the first matching item, or `None`

### Agent hint acceptance

Agent hints are applied **first** (priority over LLM). Conditions:
1. `agent_hint.status == "ok"`
2. `intent == "add_shopping_item"`
3. `item_name` is not set
4. `_pick_matching_item(agent_hint.items, original_text)` returns a match

### LLM hint acceptance

LLM hints are applied after agent hints. Conditions:
1. `hint` is not `None`
2. `hint.error_type` is absent/falsy
3. `intent == "add_shopping_item"`
4. `item_name` is not set (may have been set by agent hint)
5. `_pick_matching_item(hint.items, original_text)` returns a match

### Priority: Agent > LLM

- Agent hint is evaluated and applied first
- If agent hint sets `item_name`, LLM hint is skipped (condition 4 fails)
- If agent applied and LLM hint has error/skip status, the log status is corrected to `ok`

---

## 3. Clarify Suggestor Acceptance Rules

**Purpose:** Replace the default clarification question with a more specific one.

**Source:** `routers/assist/runner.py`
- `_clarify_question_is_safe` (line 593)
- `_select_clarify_hint` (line 484)

### Rejection conditions

| # | Condition | Result | Code ref |
|---|-----------|--------|----------|
| C1 | `hint` is `None` | Reject (log: `error_type="no_hint"`) | `runner.py:_select_clarify_hint` |
| C2 | `hint.error_type` is set | Reject (log: error) | `runner.py:_select_clarify_hint` |
| C3 | Question (stripped) is empty | Reject | `runner.py:_clarify_question_is_safe` |
| C4 | `len(question) < 5` | Reject (too short) | `runner.py:_clarify_question_is_safe` |
| C5 | `len(question) > 200` | Reject (too long) | `runner.py:_clarify_question_is_safe` |
| C6 | `original_text.lower()` is substring of `question.lower()` | Reject (echo prevention) | `runner.py:_clarify_question_is_safe` |
| C7 | Intent not in `{add_shopping_item, create_task}` AND `"?" not in question` | Reject | `runner.py:_clarify_question_is_safe` |

### On acceptance

- Returns `question` and `missing_fields` from the hint

### Pipeline gate: missing_fields subset check

In `routers/v2.py:_clarify_question` (lines 198-204):
- If the baseline has determined `missing_fields` for the decision
- And `assist.clarify_missing_fields` is NOT a subset of the baseline's missing_fields
- Then the assist clarify question is **discarded** and the default question is used
- This ensures the LLM cannot introduce irrelevant missing field requirements

---

## 4. Agent Hint Scoring and Selection

**Purpose:** Select the best agent candidate for entity extraction hints.

**Source:**
- `routers/assist/runner.py:_run_agent_entity_hint` (line 186)
- `routers/assist/agent_scoring.py`

### Candidate loading (`_load_agent_candidates`)

1. Load agent registry (`AgentRegistryV0`)
2. Filter by `capability_id` (from `ASSIST_AGENT_HINTS_CAPABILITY`)
3. Filter by `intent` (agent's `allowed_intents` must include current intent)
4. Filter by `allowlist` (if `ASSIST_AGENT_HINTS_ALLOWLIST` is set)
5. Override with `ASSIST_AGENT_HINTS_AGENT_ID` if set (forces specific agent)

### Pre-conditions (skip if any fail)

| Condition | Skip reason |
|-----------|------------|
| `ASSIST_AGENT_HINTS_ENABLED=false` | Disabled |
| `intent != add_shopping_item` | Wrong intent |
| `item_name` already set | Not needed |
| `sample_rate <= 0` | Sampling off |
| `stable_sample(command_id, rate)` returns false | Not sampled |
| `capability_id` empty | No capability configured |
| No candidates after filtering | No agents available |

### Scoring rules (`agent_scoring.py`)

Each candidate is scored as a tuple `(status_rank, applicable_rank, latency_rank, agent_id)`.
**Lower is better.**

| Component | Values | Description |
|-----------|--------|-------------|
| `status_rank` | ok=0, rejected=1, error=2, skipped=3 | Agent execution result |
| `applicable_rank` | 0 if applicable, 1 if not (0 if status != ok) | Item matched via `_pick_matching_item` |
| `latency_rank` | actual ms (None → MAX) | Lower latency preferred |
| `agent_id` | string | Alphabetical tiebreak |

### Tiebreak cascade

1. `status_rank` — prefer `ok` over errors
2. `applicable_rank` — prefer matching items
3. `latency_rank` — prefer faster agents
4. `agent_id` — deterministic alphabetical tiebreak

Selection reason is logged: `status_rank`, `applicable_tiebreak`, `latency_tiebreak`, or `agent_id_tiebreak`.

---

## 5. Timeout and Error Handling

**Source:** `routers/assist/runner.py`

### Timeout mechanism

- LLM hints: `ASSIST_TIMEOUT_MS` (default 200ms)
- Agent hints: `ASSIST_AGENT_HINTS_TIMEOUT_MS` (default 120ms)
- Implementation: `_run_with_timeout(func, timeout_s)` uses `ThreadPoolExecutor` + `future.result(timeout=...)`

### Error propagation

- **All errors are caught inside `_run_*` and `_apply_*` functions**
- On error: the hint returns `None` or an error status
- `apply_assist_hints` never raises — returns unchanged input on any failure
- The baseline pipeline continues without degradation

### Per-subsystem disable

Each hint type has its own flag. Disabling any flag → that hint is skipped, others still run:
- `ASSIST_NORMALIZATION_ENABLED=false` → skip normalization
- `ASSIST_ENTITY_EXTRACTION_ENABLED=false` → skip LLM entity hints
- `ASSIST_AGENT_HINTS_ENABLED=false` → skip agent entity hints
- `ASSIST_CLARIFY_ENABLED=false` → skip clarify

Master switch: `ASSIST_MODE_ENABLED=false` → skip ALL assist processing.

---

## Code Reference Index

| Function | File | Line | Purpose |
|----------|------|------|---------|
| `apply_assist_hints` | `routers/assist/runner.py` | 87 | Main entry point |
| `_build_assist_hints` | `routers/assist/runner.py` | 111 | Build LLM hints per flags |
| `_apply_normalization_hint` | `routers/assist/runner.py` | 374 | Apply normalization |
| `_can_accept_normalized_text` | `routers/assist/runner.py` | 567 | Normalization acceptance check |
| `_apply_entity_hints` | `routers/assist/runner.py` | 405 | Apply entity hints |
| `_pick_matching_item` | `routers/assist/runner.py` | 584 | Substring item match |
| `_run_agent_entity_hint` | `routers/assist/runner.py` | 186 | Agent hint pipeline |
| `_load_agent_candidates` | `routers/assist/runner.py` | 326 | Load and filter agents |
| `_select_clarify_hint` | `routers/assist/runner.py` | 484 | Clarify hint selection |
| `_clarify_question_is_safe` | `routers/assist/runner.py` | 593 | Clarify safety check |
| `_run_with_timeout` | `routers/assist/runner.py` | 536 | Timeout wrapper |
| `_clarify_question` | `routers/v2.py` | 198 | missing_fields subset gate |
| scoring logic | `routers/assist/agent_scoring.py` | — | Agent candidate scoring |
| feature flags | `routers/assist/config.py` | — | All feature flags |
```

---

## Verification

After creating the file, run:

```bash
# 1. Document exists
test -f docs/contracts/assist-mode-acceptance-rules.md && echo "OK" || echo "MISSING"

# 2. Assist-mode tests still pass
python3 -m pytest tests/test_assist_mode.py tests/test_assist_agent_hints.py -v

# 3. Full suite
python3 -m pytest tests/ -v
```
