# ST-025 Checklist

## Acceptance Criteria

- [ ] AC-1: golden_dataset.json has >= 20 entries
- [ ] AC-2: Each intent (add_shopping_item, create_task, clarify_needed) has >= 3 entries
- [ ] AC-3: Entries with difficulty="hard" >= 3
- [ ] AC-4: All existing graph-sanity and shadow-analyzer tests pass
- [ ] AC-5: All 236 existing tests pass + 3 new validation tests pass

## DoD Items

- [ ] golden_dataset.json expanded to 22+ entries
- [ ] New fields `expected_action` and `difficulty` on ALL entries
- [ ] New fixture command files created (6-8 files)
- [ ] `test_analyze_shadow_router.py:261` — `== 14` changed to `>= 20`
- [ ] `tests/test_golden_dataset_validation.py` — 3 new validation tests
- [ ] graph-sanity suite runs cleanly
- [ ] Full test suite passes (236 existing + 3 new = 239)
