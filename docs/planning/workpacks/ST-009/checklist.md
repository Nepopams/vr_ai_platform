# ST-009 — AC / DoD Verification Checklist

## Acceptance Criteria

- [ ] AC-1: `extract_items("Купи молоко, хлеб и бананы")` returns 3 items with correct names
- [ ] AC-2: `extract_items("Купи хлеб и яйца")` returns 2 items (conjunction split)
- [ ] AC-3: `extract_items("Buy apples and oranges")` returns 2 items (English)
- [ ] AC-4: `extract_items("Купи 2 литра молока")` returns quantity="2", unit="литра"
- [ ] AC-5: `extract_item_name()` still works unchanged (backward compat)
- [ ] AC-6: `normalized["items"]` populated by V2 normalize
- [ ] AC-7: Golden dataset has `expected_item_count` / `expected_item_names` for multi-item entries
- [ ] AC-8: `agent_runner/schemas.py` quantity type is `["string", "null"]`
- [ ] AC-9: `agents/baseline_shopping.py` uses `extract_items()` and returns multiple items

## DoD

- [ ] Tests exist: `test -f tests/test_multi_item_extraction.py`
- [ ] All tests pass: `python3 -m pytest tests/ -v`
- [ ] `extract_item_name()` not modified (backward compat)
- [ ] V1 pipeline (`process_command`) not modified
- [ ] No secrets in new files
