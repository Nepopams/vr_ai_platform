# ST-015: CI Completeness -- Add decision_log_audit and Use release_sanity Orchestrator

**Epic:** EP-006 (SemVer and CI Contract Governance)
**Status:** Ready
**Flags:** contract_impact=no, adr_needed=none, diagrams_needed=none

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-006/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-semver-and-ci.md` |
| ADR-001 | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| CI workflow | `.github/workflows/ci.yml` |
| Release sanity script | `skills/release-sanity/scripts/release_sanity.py` |
| Decision log audit script | `skills/decision-log-audit/scripts/audit_decision_logs.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

The current CI workflow (`.github/workflows/ci.yml`) runs 4 steps:
1. `pytest` (tests)
2. `contract_checker` (validate_contracts)
3. `schema_bump check` (schema version check)
4. `graph_sanity` (graph_sanity)

Missing: `decision_log_audit`. The `release_sanity.py` orchestrator already includes
all 3 skill checks (contract-checker, decision-log-audit, graph-sanity) but CI calls
individual steps instead.

## User Value

As a platform developer, I want CI to run ALL contract governance checks including
decision log audit, so that invalid decision logs are caught before merge.

## Scope

### In scope

- Replace individual CI skill steps with single `release_sanity.py` invocation
- Ensure `decision_log_audit` runs as part of CI
- Keep `pytest` step separate
- Keep `schema_bump check` as separate CI step
- Add test for `release_sanity.run_checks()` confirming all expected checks
- Verify all 202 existing tests still pass

### Out of scope

- Changes to individual skill scripts
- Changes to release_sanity.py logic
- GitHub Actions environment debugging
- Schema_bump improvements (ST-016)

---

## Acceptance Criteria

### AC-1: CI runs decision_log_audit
```
Given the CI workflow is triggered
When the release sanity step executes
Then decision_log_audit runs and validates the sample JSONL log
And the step passes (exit code 0 for valid logs)
```

### AC-2: CI uses release_sanity orchestrator
```
Given the CI workflow `.github/workflows/ci.yml`
When reviewed after this change
Then there is a step that runs release_sanity.py
And the individual steps for contract_checker and graph_sanity are replaced
And the schema_bump check step remains separate
```

### AC-3: Release sanity failure blocks CI
```
Given a deliberately invalid decision log fixture (test scenario)
When release_sanity.py runs
Then it returns exit code 1
And the failure message identifies which check failed
```

### AC-4: Test for release_sanity orchestrator
```
Given the test suite
When test_release_sanity_runs is executed
Then it calls run_checks() and verifies no failures
And confirms all 3 sub-checks are invoked
```

### AC-5: All 202 existing tests pass
```
Given the current test suite of 202 tests
When ST-015 changes are applied
Then all 202 tests pass and new tests also pass
```

---

## Test Strategy

### Unit tests (~2 new)
- `test_release_sanity_runs` -- calls `run_checks()`, asserts no failures
- `test_release_sanity_includes_decision_log_audit` -- asserts CHECKS list includes decision-log-audit

### Regression
- Full test suite: 202 tests must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `.github/workflows/ci.yml` | Replace individual skill steps with release_sanity.py; keep pytest and schema_bump check |
| `tests/test_skill_checks.py` | Add release_sanity tests |

---

## Dependencies

- None (foundation story)
- Blocks: ST-016
