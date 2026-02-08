# ST-014: Clarify Golden Dataset Ground Truth and Quality Measurement

**Epic:** EP-005 (Improved Clarify Questions)
**Status:** Ready (dep: ST-012)
**Flags:** contract_impact=no, adr_needed=none, diagrams_needed=none

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-005/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-improved-clarify.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

The golden dataset (`skills/graph-sanity/fixtures/commands/`) has 14 command fixtures but no ground truth for clarify behavior:
- What `missing_fields` should each clarify fixture produce?
- How many clarify-triggering fixtures are there?
- What is the baseline clarify quality before improvements?

Without measurement, we can't prove the initiative achieved its goal of "снижение clarify-итераций".

**Clarify-relevant fixtures (produce clarify decisions):**
- `empty_text.json` -- empty input
- `unknown_intent.json` -- unrecognized intent
- `minimal_context.json` -- vague request

**Edge cases (may or may not clarify):**
- `shopping_no_list.json` -- shopping without list context
- `task_no_zones.json` -- task without zone info

## User Value

As a product owner, I want to measure whether clarify question improvements actually reduce unnecessary clarification rounds, so I can verify the initiative delivered value.

## Scope

### In scope

- Add `expected_missing_fields` annotations to clarify-triggering golden fixtures
- Create a clarify quality measurement script that:
  - Runs all golden fixtures through V2 router
  - Compares actual `missing_fields` vs expected
  - Reports match rate as a metric
  - Reports clarify vs start_job split
- Add new clarify-specific golden fixtures (edge cases)
- Unit tests for the measurement script

### Out of scope

- Subjective question quality scoring (too complex for MVP)
- Automated CI integration of measurement
- Changes to router logic (ST-012/ST-013)
- Dashboard or visualization

---

## Acceptance Criteria

### AC-1: Clarify fixtures have expected_missing_fields ground truth
```
Given golden dataset fixtures that produce clarify decisions
When each fixture is inspected
Then it includes an "expected" object with:
  - "action": "clarify"
  - "missing_fields": [...expected fields...]
```

### AC-2: Measurement script computes missing_fields match rate
```
Given the golden dataset with ground truth annotations
When scripts/analyze_clarify_quality.py runs
Then it outputs:
  - Total clarify commands
  - missing_fields exact match rate (actual == expected)
  - missing_fields subset match rate (expected ⊆ actual)
  - Clarify vs start_job split
```

### AC-3: At least 2 new clarify-specific fixtures added
```
Given the golden dataset
When ST-014 is complete
Then at least 2 new fixtures exist specifically testing clarify edge cases
(e.g., partial shopping info, ambiguous intent between task/shopping)
```

### AC-4: Measurement script handles both V1 and V2
```
Given the measurement script
When run with --router=v1 or --router=v2
Then it produces separate reports for each router version
```

### AC-5: Script has unit tests
```
Given the measurement script
When its test file is run
Then tests verify: fixture loading, metric computation, output formatting
```

### AC-6: All existing tests pass
```
Given the test suite (176+ after ST-012/ST-013)
When ST-014 changes are applied
Then all tests pass
```

---

## Test Strategy

### Unit tests (~6 new tests)
- `test_clarify_analyzer_loads_fixtures` -- fixture loading with expected annotations
- `test_clarify_analyzer_computes_match_rate` -- metric computation
- `test_clarify_analyzer_handles_no_clarify` -- all start_job -> 0 clarify commands
- `test_clarify_analyzer_v1_v2_comparison` -- both routers produce valid output
- `test_clarify_fixture_ground_truth_valid` -- expected_missing_fields are valid identifiers
- `test_new_clarify_fixtures_schema_valid` -- new fixtures validate against command.schema.json

### Regression
- Full test suite must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `skills/graph-sanity/fixtures/commands/empty_text.json` | Add `expected` annotation |
| `skills/graph-sanity/fixtures/commands/unknown_intent.json` | Add `expected` annotation |
| `skills/graph-sanity/fixtures/commands/minimal_context.json` | Add `expected` annotation |
| `skills/graph-sanity/fixtures/commands/clarify_partial_shopping.json` | New fixture |
| `skills/graph-sanity/fixtures/commands/clarify_ambiguous_intent.json` | New fixture |
| `scripts/analyze_clarify_quality.py` | New script: measurement |
| `tests/test_clarify_measurement.py` | New file: unit tests for script |

---

## Dependencies

- ST-012 (enhanced missing_fields) -- ground truth must align with enriched fields
- Independent of ST-013 (measurement works regardless of LLM prompt quality)
