# Codex PLAN Prompt — ST-010: LLM Extraction and Assist Mode Multi-Item Support

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

We are implementing ST-010: LLM extraction and assist mode multi-item support.

**Workpack:** `docs/planning/workpacks/ST-010/workpack.md`
**ADR-006-P:** `docs/adr/ADR-006-multi-item-internal-model.md`

**Key decisions from ADR-006-P:**
- Internal model: `items: List[dict]` with `{name, quantity, unit}`
- Quantity type: `string` (aligned with contract)
- Backward compat: `item_name` kept as computed property

---

## Exploration Tasks

### Task 1: Current `SHOPPING_EXTRACTION_SCHEMA` in llm_policy/tasks.py

```bash
sed -n '1,19p' llm_policy/tasks.py
```

**Report:** Confirm schema structure (single `item_name: string`), imports, and task ID constant.

### Task 2: Current `ExtractionResult` dataclass

```bash
sed -n '22,27p' llm_policy/tasks.py
```

**Report:** Confirm fields: `item_name: str | None`, `used_policy: bool`, `error_type: str | None`.

### Task 3: Current `extract_shopping_item_name()` function

```bash
sed -n '29,62p' llm_policy/tasks.py
```

**Report:** Confirm fallback path (lines 37-42), skipped path (lines 50-55), success path (lines 57-60), and error path (line 62). Count all places that construct `ExtractionResult`.

### Task 4: Current `_build_shopping_prompt()` function

```bash
sed -n '83,91p' llm_policy/tasks.py
```

**Report:** Confirm prompt text asks for single item.

### Task 5: Current `_ENTITY_SCHEMA` in assist runner

```bash
sed -n '64,73p' routers/assist/runner.py
```

**Report:** Confirm `items` is `array of string` (line 67).

### Task 6: Current `_run_entity_hint()` item filtering

```bash
sed -n '160,183p' routers/assist/runner.py
```

**Report:** Confirm line 175 filters items with `isinstance(item, str)`.

### Task 7: Current `_run_agent_entity_hint()` item parsing

```bash
sed -n '234,247p' routers/assist/runner.py
```

**Report:** Confirm line 236 filters items as strings. Report exact line for `_pick_matching_item` usage (line 237).

### Task 8: Current `_apply_entity_hints()` full function

```bash
sed -n '405,481p' routers/assist/runner.py
```

**Report:** Confirm both agent hint path (lines 431-440) and LLM hint path (lines 453-457) use `_pick_matching_item` returning single item. Confirm both set `updated["item_name"]`.

### Task 9: Current `_pick_matching_item()` function

```bash
sed -n '584,590p' routers/assist/runner.py
```

**Report:** Confirm signature `(items: Iterable[str], text: str) -> Optional[str]` and that it returns first match.

### Task 10: Current `_summarize_entities()` function

```bash
sed -n '608,612p' routers/assist/runner.py
```

**Report:** Confirm it counts string items.

### Task 11: Current `EntityHints` and `AgentEntityHint` types

```bash
cat routers/assist/types.py
```

**Report:** Confirm `EntityHints.items: List[str]` (line 21) and `AgentEntityHint.items: List[str]` (line 31).

### Task 12: Current `AgentHintCandidate` items type

```bash
sed -n '13,21p' routers/assist/agent_scoring.py
```

**Report:** Confirm `items: list[str]` (line 20).

### Task 13: Existing assist mode tests

```bash
cat tests/test_assist_mode.py
```

**Report:** List all tests and identify which create `EntityHints(items=["string"])` that need updating to dict format.

### Task 14: All callers of `ExtractionResult` across codebase

```bash
rg "ExtractionResult" --type py
```

**Report:** Complete list. These must all work after the dataclass change.

### Task 15: All callers of `_pick_matching_item` across codebase

```bash
rg "_pick_matching_item" --type py
```

**Report:** List all call sites. These must all work after the signature change.

### Task 16: All places that read `EntityHints.items` or `AgentEntityHint.items`

```bash
rg "\.items" routers/assist/runner.py | head -30
```

**Report:** Identify all lines that iterate over `.items` and currently expect strings.

### Task 17: V2 normalize() — confirm no code change needed

```bash
sed -n '59,80p' routers/v2.py
```

**Report:** Confirm `extract_shopping_item_name(...).item_name` at line 63 — the `.item_name` property will work transparently.

### Task 18: Check for existing test files to avoid name collision

```bash
ls tests/test_llm_extraction* tests/test_assist_multi* 2>/dev/null || echo "No existing files"
```

**Report:** Confirm no collision with planned new test file names.

### Task 19: `_build_entity_prompt()` function

```bash
sed -n '549,554p' routers/assist/runner.py
```

**Report:** Confirm current prompt text for entity extraction.

---

## Expected Output

Produce a numbered report (Task 1 through Task 19) with:
- All function signatures, types, and imports confirmed
- Complete list of `ExtractionResult` and `_pick_matching_item` callers
- All `.items` access points in runner.py that expect strings
- Existing test fixtures that need updating
- Any STOP-THE-LINE issues
