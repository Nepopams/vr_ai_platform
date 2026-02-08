# ST-011 — AC / DoD Verification Checklist

## Acceptance Criteria

- [ ] AC-1: `plan()` generates N proposed_actions for N items
- [ ] AC-2: proposed_actions include quantity/unit when present
- [ ] AC-3: Single item still produces exactly 1 proposed_action
- [ ] AC-4: Empty items + no item_name = clarify decision
- [ ] AC-5: Generated decisions validate against `decision.schema.json`
- [ ] AC-6: Partial trust path not broken (single item still works)
- [ ] AC-7: E2E: "Купи молоко, хлеб и бананы" -> 3 proposed_actions
- [ ] AC-8: list_id propagated to all items

## DoD

- [ ] Tests exist: `test -f tests/test_planner_multi_item.py && test -f tests/test_multi_item_e2e.py`
- [ ] All tests pass: `python3 -m pytest tests/ -v`
- [ ] Golden-like test passes: `python3 -m pytest tests/test_router_golden_like.py -v`
- [ ] `graphs/core_graph.py` not modified
- [ ] `llm_policy/tasks.py` not modified
- [ ] `routers/assist/runner.py` not modified
- [ ] `decision.schema.json` not modified
- [ ] `command.schema.json` not modified
- [ ] `normalized["item_name"]` still populated (partial trust compat)
- [ ] No secrets in new/changed files
