# Workpack: ST-015 — CI Completeness: decision_log_audit + release_sanity Orchestrator

**Status:** Ready
**Story:** `docs/planning/epics/EP-006/stories/ST-015-ci-completeness-decision-log-audit.md`

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-006/epic.md` |
| Story | `docs/planning/epics/EP-006/stories/ST-015-ci-completeness-decision-log-audit.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-semver-and-ci.md` |
| ADR-001 | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| CI workflow | `.github/workflows/ci.yml` |
| Release sanity | `skills/release-sanity/scripts/release_sanity.py` |
| Decision log audit | `skills/decision-log-audit/scripts/audit_decision_logs.py` |
| Existing tests | `tests/test_skill_checks.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

CI runs ALL contract governance checks via `release_sanity.py` orchestrator (including `decision_log_audit`). Individual CI steps for `contract_checker` and `graph_sanity` replaced by single `release_sanity` step. `schema_bump check` remains separate.

## Acceptance Criteria

1. CI runs `decision_log_audit` via release_sanity step (exit 0 for valid logs)
2. CI uses `release_sanity` orchestrator; individual `contract_checker` and `graph_sanity` steps removed; `schema_bump check` remains
3. Release sanity failure blocks CI (exit 1, identifies which check failed)
4. Tests verify orchestrator: `test_release_sanity_runs`, `test_release_sanity_includes_decision_log_audit`
5. All 202 existing tests pass + new tests pass

---

## Files to Change

| File | Change |
|------|--------|
| `.github/workflows/ci.yml` | Remove `contract_checker` and `graph_sanity` steps; add `release_sanity` step; keep `pytest` and `schema_bump check` |
| `tests/test_skill_checks.py` | Add 2 new test functions |

---

## Implementation Plan

### Step 1: Update CI workflow

Replace individual skill steps with release_sanity orchestrator.

Current steps (remove):
```yaml
      - name: Validate contracts
        run: python -m skills.contract_checker

      - name: Graph sanity
        run: python -m skills.graph_sanity
```

New step (add):
```yaml
      - name: Release sanity
        run: python -m skills.release_sanity
```

Keep unchanged: `pytest` step and `schema_bump check` step.

### Step 2: Add release_sanity tests

Add to `tests/test_skill_checks.py`:

1. `test_release_sanity_runs()` — load `skills/release-sanity/scripts/release_sanity.py` via `load_script()`, call `run_checks()`, assert `failures == []`
2. `test_release_sanity_includes_decision_log_audit()` — load script, read `CHECKS` list, assert contains `"decision-log-audit"`, `"contract-checker"`, `"graph-sanity"`

---

## Verification Commands

```bash
# Full test suite (expect 204 passed)
python3 -m pytest tests/ -v --tb=short

# Just skill checks (expect 6 tests)
python3 -m pytest tests/test_skill_checks.py -v --tb=short

# Release sanity directly (expect exit 0)
python3 -m skills.release_sanity

# Schema bump check (expect exit 0)
python3 -m skills.schema_bump check

# CI file checks
grep -c "release_sanity" .github/workflows/ci.yml        # expect 1
grep -c "skills.contract_checker" .github/workflows/ci.yml  # expect 0
grep -c "skills.graph_sanity" .github/workflows/ci.yml      # expect 0
grep -c "skills.schema_bump" .github/workflows/ci.yml       # expect 1
```

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| `api-sanity` in release_sanity fails (fastapi not installed) | Low | Low | Skipped when `RUN_API_SANITY` not set |
| CI YAML syntax error | Low | Medium | Manual YAML review |

## Rollback

- `git revert <commit>` restores individual CI steps
- No schema/contract/flag changes

## APPLY Boundaries

**Allowed:** `.github/workflows/ci.yml`, `tests/test_skill_checks.py`
**Forbidden:** `skills/`, `contracts/`, `graphs/`, `routers/`, `agent_registry/`, `app/`
