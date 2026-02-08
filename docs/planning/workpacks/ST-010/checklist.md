# ST-010 — AC / DoD Verification Checklist

## Acceptance Criteria

- [ ] AC-1: `SHOPPING_EXTRACTION_SCHEMA` defines `items` as array of `{name, quantity, unit}` objects
- [ ] AC-2: `ExtractionResult.items` returns `List[dict]`; `.item_name` returns first item's name (backward compat)
- [ ] AC-3: `_apply_entity_hints()` populates `normalized["items"]` with all matching items
- [ ] AC-4: Mixed matching: only items confirmed in original text are accepted
- [ ] AC-5: Agent hint path also populates multi-item
- [ ] AC-6: No hint = baseline items unchanged
- [ ] AC-7: `_ENTITY_SCHEMA` uses structured item objects `{name, quantity, unit}`

## DoD

- [ ] Tests exist: `test -f tests/test_llm_extraction_multi_item.py && test -f tests/test_assist_multi_item.py`
- [ ] All tests pass: `python3 -m pytest tests/ -v`
- [ ] Existing assist tests pass: `python3 -m pytest tests/test_assist_mode.py -v`
- [ ] `extract_item_name()` in core_graph.py not modified (backward compat)
- [ ] `extract_items()` in core_graph.py not modified
- [ ] `process_command()` not modified
- [ ] `decision.schema.json` not modified
- [ ] `command.schema.json` not modified
- [ ] No secrets in new/changed files
