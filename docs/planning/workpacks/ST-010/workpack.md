# Workpack — ST-010: LLM Extraction and Assist Mode Multi-Item Support

**Status:** Ready
**Story:** `docs/planning/epics/EP-004/stories/ST-010-llm-assist-multi-item.md`
**Epic:** `docs/planning/epics/EP-004/epic.md`

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-004/epic.md` |
| Story | `docs/planning/epics/EP-004/stories/ST-010-llm-assist-multi-item.md` |
| ADR-006-P | `docs/adr/ADR-006-multi-item-internal-model.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

LLM-assisted extraction (`llm_policy/tasks.py`) returns multi-item results instead of
a single `item_name`. Assist mode entity hints (`routers/assist/runner.py`) populate
`normalized["items"]` with all matching items instead of picking the first one only.
Backward compatibility is preserved: `item_name` remains as a computed property (first item's name).

---

## Acceptance Criteria Summary

- AC-1: `SHOPPING_EXTRACTION_SCHEMA` defines `items` as array of `{name, quantity, unit}` objects
- AC-2: `ExtractionResult.items` returns `List[dict]`; `.item_name` returns first item's name
- AC-3: `_apply_entity_hints()` populates `normalized["items"]` with all matching items
- AC-4: Mixed matching: only items confirmed in original text are accepted
- AC-5: Agent hint path also populates multi-item
- AC-6: No hint = baseline items unchanged
- AC-7: `_ENTITY_SCHEMA` uses structured item objects `{name, quantity, unit}`

---

## Files to Change

### 1. `llm_policy/tasks.py` (LLM extraction schema + result)

**Current state:**
- Lines 12-19: `SHOPPING_EXTRACTION_SCHEMA = {item_name: string}` (single item)
- Lines 22-26: `ExtractionResult(item_name: str | None, used_policy, error_type)` (single field)
- Lines 29-62: `extract_shopping_item_name()` returns single ExtractionResult
- Lines 57-60: Extracts `item_name` from `result.data.get("item_name")`
- Lines 83-90: `_build_shopping_prompt()` asks for single item

**Changes:**

**Step 1a: Update `SHOPPING_EXTRACTION_SCHEMA` (lines 12-19)**

Replace with multi-item schema per ADR-006-P:

```python
SHOPPING_EXTRACTION_SCHEMA: Mapping[str, object] = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "quantity": {"type": ["string", "null"]},
                    "unit": {"type": ["string", "null"]},
                },
                "required": ["name"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["items"],
    "additionalProperties": False,
}
```

**Step 1b: Update `ExtractionResult` dataclass (lines 22-26)**

Replace `item_name: str | None` with `items: list[dict]`.
Add computed `item_name` property for backward compat (returns first item's name or None).

```python
@dataclass(frozen=True)
class ExtractionResult:
    items: list[dict]
    used_policy: bool
    error_type: str | None

    @property
    def item_name(self) -> str | None:
        if self.items:
            return self.items[0].get("name")
        return None
```

**Step 1c: Update `extract_shopping_item_name()` (lines 29-62)**

- On fallback path (policy disabled or skipped): wrap `fallback_extract_item_name(text)` result
  into items list: `[{"name": name}]` if name is not None, else `[]`.
- On success path: extract `items` list from `result.data.get("items", [])` instead of single `item_name`.
- Import `extract_items` from `graphs.core_graph` for deterministic fallback multi-item.

Updated fallback logic (lines 37-42):
```python
if not enabled:
    fallback_name = fallback_extract_item_name(text)
    items = [{"name": fallback_name}] if fallback_name else []
    return ExtractionResult(items=items, used_policy=False, error_type=None)
```

Updated success path (lines 57-60):
```python
if result.status == "ok" and result.data is not None:
    raw_items = result.data.get("items", [])
    items = [item for item in raw_items if isinstance(item, dict) and item.get("name")]
    return ExtractionResult(items=items, used_policy=True, error_type=None)

return ExtractionResult(items=[], used_policy=True, error_type=result.error_type)
```

Skipped path (lines 50-55) same pattern as fallback.

**Step 1d: Update `_build_shopping_prompt()` (lines 83-90)**

Update prompt text to ask for list of items:
```python
def _build_shopping_prompt(text: str) -> str:
    schema_text = json.dumps(SHOPPING_EXTRACTION_SCHEMA, ensure_ascii=False)
    return (
        "Извлеки все товары из текста пользователя. "
        "Верни JSON со списком items по схеме.\n"
        f"Схема: {schema_text}\n"
        f"Текст: {text}"
    )
```

**Step 1e: Update import**

Add `extract_items` import from `graphs.core_graph` (for fallback).
Keep `extract_item_name as fallback_extract_item_name` for backward compat fallback.

### 2. `routers/v2.py` (adapt to new ExtractionResult)

**Current state (lines 62-66):**
```python
item_name = (
    extract_shopping_item_name(text, trace_id=command.get("trace_id")).item_name
    if intent == "add_shopping_item"
    else None
)
```

**Change:** No code change needed. `ExtractionResult.item_name` is now a property that
returns first item's name, so `result.item_name` still returns `str | None`.
The existing code continues to work via the property.

### 3. `routers/assist/types.py` (entity hint types)

**Current state:**
- Line 21: `EntityHints.items: List[str]` (plain strings)
- Line 31: `AgentEntityHint.items: List[str]` (plain strings)

**Changes:**

**Step 3a: Update `EntityHints.items` type (line 21)**

Change from `List[str]` to `List[dict]`:
```python
@dataclass(frozen=True)
class EntityHints:
    items: List[dict]
    task_hints: Dict[str, object]
    confidence: Optional[float]
    error_type: Optional[str]
    latency_ms: Optional[int]
```

**Step 3b: Update `AgentEntityHint.items` type (line 31)**

Change from `List[str]` to `List[dict]`:
```python
@dataclass(frozen=True)
class AgentEntityHint:
    status: str
    items: List[dict]
    latency_ms: Optional[int]
    candidates_count: int = 0
    selected_agent_id: Optional[str] = None
    selected_status: Optional[str] = None
    selection_reason: Optional[str] = None
```

### 4. `routers/assist/runner.py` (assist mode multi-item)

**Current state:**
- Lines 64-73: `_ENTITY_SCHEMA` has `items: array of string`
- Lines 160-183: `_run_entity_hint()` filters items as strings
- Lines 234-236: Agent runner filters items as strings
- Lines 405-481: `_apply_entity_hints()` picks first item only via `_pick_matching_item()`
- Lines 584-590: `_pick_matching_item()` returns first match
- Lines 608-612: `_summarize_entities()` counts string items

**Changes:**

**Step 4a: Update `_ENTITY_SCHEMA` (lines 64-73)**

Change `items` from `array of string` to `array of object`:
```python
_ENTITY_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "quantity": {"type": ["string", "null"]},
                    "unit": {"type": ["string", "null"]},
                },
                "required": ["name"],
                "additionalProperties": False,
            },
        },
        "task_hints": {"type": "object"},
        "confidence": {"type": "number"},
    },
    "required": ["items"],
    "additionalProperties": False,
}
```

**Step 4b: Update `_run_entity_hint()` (lines 160-183)**

Change item filtering from `isinstance(item, str)` to `isinstance(item, dict) and item.get("name")`:
```python
items = [item for item in payload.get("items", []) if isinstance(item, dict) and item.get("name")]
```

**Step 4c: Update `_run_agent_entity_hint()` agent item parsing (lines 234-236)**

Agent returns items as strings (baseline_shopping agent returns `List[dict]` with `name` key).
Parse both formats:
```python
items_payload = payload.get("items") if isinstance(payload, dict) else None
items = []
if isinstance(items_payload, list):
    for item in items_payload:
        if isinstance(item, dict) and item.get("name"):
            items.append(item)
        elif isinstance(item, str) and item.strip():
            items.append({"name": item.strip()})
```

**Step 4d: Update `_pick_matching_item()` to work with dicts (line 584-590)**

Keep existing function but adapt to work with `List[dict]`:
```python
def _pick_matching_item(items: Iterable[dict], text: str) -> Optional[dict]:
    lowered = text.lower()
    for item in items:
        name = item.get("name", "") if isinstance(item, dict) else str(item)
        candidate = name.strip()
        if candidate and candidate.lower() in lowered:
            return item
    return None
```

**Step 4e: Add `_pick_matching_items()` that returns all matches (new function after line 590)**

```python
def _pick_matching_items(items: Iterable[dict], text: str) -> List[dict]:
    lowered = text.lower()
    matched = []
    for item in items:
        name = item.get("name", "") if isinstance(item, dict) else str(item)
        candidate = name.strip()
        if candidate and candidate.lower() in lowered:
            matched.append(item)
    return matched
```

**Step 4f: Update `_apply_entity_hints()` (lines 405-481)**

Replace single-item logic with multi-item:

Agent hint path (lines 431-440):
```python
if (
    agent_hint.status == "ok"
    and normalized.get("intent") == "add_shopping_item"
):
    matched = _pick_matching_items(agent_hint.items, original_text)
    if matched:
        updated["items"] = matched
        if not updated.get("item_name") and matched:
            updated["item_name"] = matched[0].get("name")
        agent_applied = True
        accepted = True
```

LLM hint path (lines 453-457):
```python
if normalized.get("intent") == "add_shopping_item":
    matched = _pick_matching_items(hint.items, original_text)
    if matched:
        updated["items"] = matched
        if not updated.get("item_name") and matched:
            updated["item_name"] = matched[0].get("name")
        accepted = True
```

**Step 4g: Update agent applicability check (line 237)**

Change from `_pick_matching_item` to check with new dict format:
```python
applicable = bool(_pick_matching_item(items, text)) if output.status == "ok" else False
```
(This still works because `_pick_matching_item` now handles dicts.)

**Step 4h: Update `_summarize_entities()` (lines 608-612)**

Adapt to count dict items:
```python
def _summarize_entities(items: Iterable) -> Dict[str, Any]:
    items_list = list(items)
    keys = ["items"] if items_list else []
    counts = {"items": len(items_list)} if keys else {}
    return {"keys": keys, "counts": counts}
```
(Minimal change since it just counts items.)

**Step 4i: Update `_build_entity_prompt()` (lines 549-554)**

Update prompt to ask for structured items:
```python
def _build_entity_prompt(text: str) -> str:
    return (
        "Извлеки все сущности для shopping/task. "
        "Верни JSON со списком items (объекты с name, quantity, unit) и task_hints.\n"
        f"Текст: {text}"
    )
```

### 5. `routers/assist/agent_scoring.py` (update type hint)

**Current state (line 20):**
```python
items: list[str]
```

**Change:**
```python
items: list[dict]
```

### 6. `tests/test_llm_extraction_multi_item.py` (new tests for LLM extraction)

New test file with:
- `test_shopping_schema_has_items_array` -- verify SHOPPING_EXTRACTION_SCHEMA structure
- `test_extraction_result_items_list` -- ExtractionResult with items returns list
- `test_extraction_result_item_name_compat` -- .item_name returns first item's name
- `test_extraction_result_empty_items` -- empty items -> item_name is None

### 7. `tests/test_assist_multi_item.py` (new tests for assist mode)

New test file with:
- `test_entity_schema_has_structured_items` -- verify _ENTITY_SCHEMA shape
- `test_entity_hints_all_items_applied` -- 3 items hint, all match -> 3 items in normalized
- `test_entity_hints_partial_match` -- 3 hint items, 2 match original -> 2 items
- `test_entity_hints_no_match` -- hint items not in text -> items unchanged
- `test_agent_hint_multi_item` -- agent returns 2 items -> both applied
- `test_entity_hints_fallback_no_hint` -- no hint -> baseline items preserved
- `test_pick_matching_items_all` -- helper returns all matching
- `test_pick_matching_items_partial` -- helper returns only matches

### 8. `tests/test_assist_mode.py` (update existing tests)

**Current state:**
- Line 117: `EntityHints(items=["хлеб"], ...)` creates with string items

**Change:**
- Update to dict format: `EntityHints(items=[{"name": "хлеб"}], ...)`

---

## Implementation Plan (commit-sized)

### Commit 1: LLM extraction multi-item
1. Update `SHOPPING_EXTRACTION_SCHEMA` in `llm_policy/tasks.py` (Step 1a)
2. Update `ExtractionResult` with `items: list[dict]` + `item_name` property (Step 1b)
3. Update `extract_shopping_item_name()` for multi-item (Steps 1c, 1e)
4. Update `_build_shopping_prompt()` (Step 1d)

### Commit 2: Assist types + agent scoring update
1. Update `EntityHints.items` type in `routers/assist/types.py` (Step 3a)
2. Update `AgentEntityHint.items` type in `routers/assist/types.py` (Step 3b)
3. Update `AgentHintCandidate.items` type in `routers/assist/agent_scoring.py` (Step 5)

### Commit 3: Assist runner multi-item
1. Update `_ENTITY_SCHEMA` (Step 4a)
2. Update `_run_entity_hint()` filtering (Step 4b)
3. Update `_run_agent_entity_hint()` item parsing (Step 4c)
4. Update `_pick_matching_item()` for dicts (Step 4d)
5. Add `_pick_matching_items()` (Step 4e)
6. Update `_apply_entity_hints()` multi-item logic (Step 4f)
7. Update agent applicability check (Step 4g)
8. Update `_summarize_entities()` (Step 4h)
9. Update `_build_entity_prompt()` (Step 4i)

### Commit 4: Tests
1. Create `tests/test_llm_extraction_multi_item.py` (Step 6)
2. Create `tests/test_assist_multi_item.py` (Step 7)
3. Update `tests/test_assist_mode.py` existing tests (Step 8)

---

## Verification Commands

```bash
# 1. All tests pass
python3 -m pytest tests/ -v

# 2. New LLM extraction tests pass
python3 -m pytest tests/test_llm_extraction_multi_item.py -v

# 3. New assist multi-item tests pass
python3 -m pytest tests/test_assist_multi_item.py -v

# 4. Existing assist tests still pass
python3 -m pytest tests/test_assist_mode.py -v

# 5. No secrets in changed files
grep -rn "sk-\|api_key\s*=\s*[\"']" llm_policy/tasks.py routers/assist/runner.py routers/assist/types.py routers/assist/agent_scoring.py tests/test_llm_extraction_multi_item.py tests/test_assist_multi_item.py

# 6. Schema structure check
python3 -c "from llm_policy.tasks import SHOPPING_EXTRACTION_SCHEMA; assert 'items' in SHOPPING_EXTRACTION_SCHEMA['properties']"

# 7. ExtractionResult backward compat check
python3 -c "from llm_policy.tasks import ExtractionResult; r = ExtractionResult(items=[{'name': 'молоко'}], used_policy=False, error_type=None); assert r.item_name == 'молоко'"
```

---

## DoD Checklist

See `docs/planning/workpacks/ST-010/checklist.md`.

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing tests rely on `EntityHints(items=["string"])` | Test failures | Update existing test fixtures (Step 8) |
| Agent runner returns items as strings, not dicts | Item parsing fails | Dual-format parsing in Step 4c |
| `_pick_matching_item` callers expect string return | Type mismatch | Return full dict, callers extract `.get("name")` |
| `item_name` property change breaks v2.py | v2 normalize fails | Property returns same `str | None` as before |

---

## Rollback

Revert the commit(s). No data migration, no schema changes to external contracts.
All changes are internal (LLM schemas, assist types, assist runner logic).

---

## Invariants (DO NOT break)

- `extract_item_name()` in `graphs/core_graph.py` — NOT modified
- `extract_items()` in `graphs/core_graph.py` — NOT modified
- `process_command()` in `graphs/core_graph.py` — NOT modified
- `decision.schema.json` — NOT modified
- `command.schema.json` — NOT modified
- V1 pipeline — NOT affected
- `normalized["items"]` from baseline (ST-009) — preserved unless enriched by hints
- `normalized["item_name"]` — still populated (via ExtractionResult.item_name property)
