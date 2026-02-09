# Checklist: ST-014 — Clarify Golden Dataset Ground Truth and Quality Measurement

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Story spec | `docs/planning/epics/EP-005/stories/ST-014-clarify-golden-dataset-measurement.md` |
| Workpack | `docs/planning/workpacks/ST-014/workpack.md` |
| DoD | `docs/_governance/dod.md` |

---

## Acceptance Criteria

- [ ] AC-1: `empty_text.json`, `unknown_intent.json`, `minimal_context.json` have `expected` ground truth annotations (action + missing_fields)
- [ ] AC-2: `scripts/analyze_clarify_quality.py` computes missing_fields match rate across golden fixtures
- [ ] AC-3: At least 2 new clarify-specific fixtures added (`clarify_partial_shopping.json`, `clarify_ambiguous_intent.json`)
- [ ] AC-4: Script handles both V1 (`RouterV1Adapter`) and V2 (`RouterV2Pipeline`) routers
- [ ] AC-5: `tests/test_clarify_measurement.py` with unit tests for measurement functions
- [ ] AC-6: All 192 existing tests pass

## DoD Checklist

- [ ] No modifications to `routers/v2.py`
- [ ] No modifications to `routers/assist/runner.py`
- [ ] No modifications to `graphs/core_graph.py`
- [ ] No modifications to `contracts/schemas/`
- [ ] Existing fixture command fields unchanged (only `expected` key added)
- [ ] No existing tests modified
- [ ] No raw user text in script output (privacy)
- [ ] No secrets in any file (`sk-`, `api_key`)

## Verification Commands

```bash
# 1. New tests
python3 -m pytest tests/test_clarify_measurement.py -v

# 2. Full test suite
python3 -m pytest tests/ -v

# 3. Script self-test
python3 scripts/analyze_clarify_quality.py --self-test

# 4. Script with golden fixtures
python3 scripts/analyze_clarify_quality.py --fixtures-dir skills/graph-sanity/fixtures/commands/

# 5. No secrets
grep -rn 'sk-\|api_key' scripts/analyze_clarify_quality.py tests/test_clarify_measurement.py skills/graph-sanity/fixtures/commands/clarify_*.json
```
