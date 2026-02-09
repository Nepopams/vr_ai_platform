# EP-006: SemVer and CI Contract Governance

**Status:** Ready
**Initiative:** `docs/planning/initiatives/INIT-2026Q3-semver-and-ci.md`
**Sprint:** S05
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-semver-and-ci.md` |
| ADR-001 | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| Contract schemas | `contracts/schemas/command.schema.json`, `contracts/schemas/decision.schema.json` |
| Contract version | `contracts/VERSION` (currently 2.0.0) |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

The initiative INIT-2026Q3-semver-and-ci calls for CI-level protection of contracts and
semantic versioning enforcement. Most of the tooling already exists from prior sprints:

| Tool | Script | CI step | Test coverage |
|------|--------|---------|---------------|
| validate_contracts | `skills/contract-checker/scripts/validate_contracts.py` | Yes | `test_contract_checker_fixtures` |
| graph_sanity | `skills/graph-sanity/scripts/run_graph_suite.py` | Yes | `test_graph_sanity_runs` |
| decision_log_audit | `skills/decision-log-audit/scripts/audit_decision_logs.py` | **No (gap)** | `test_decision_log_audit_fixture` |
| schema_bump check | `skills/schema-bump/scripts/check_breaking_changes.py` | Yes | `test_schema_bump_breaking_changes` |
| schema_bump bump | `skills/schema-bump/scripts/bump_version.py` | N/A (manual) | N/A |
| release_sanity | `skills/release-sanity/scripts/release_sanity.py` | **No (gap)** | N/A |

ADR-001 (Accepted) defines the versioning policy. `contracts/VERSION` is at 2.0.0.

### Remaining gaps

1. CI does not run `decision_log_audit`
2. `schema_bump check` compares synthetic example fixtures, not real contract schemas
3. No operational policy document or PR workflow example for developers

## Goal

Complete CI contract governance so that:
1. All existing sanity checks run in CI (no gaps)
2. Breaking changes to real contract schemas are detected and block MINOR/PATCH bumps
3. Developers have a clear runbook for contract changes

## Scope

### In scope

- Add decision_log_audit to CI via release_sanity orchestrator
- Replace synthetic schema comparison with real contract schema comparison
- Expand breaking-change detection (type changes, field deletions)
- Operational policy document with PR workflow example

### Out of scope

- Full release management
- Complex security policies
- Automated PR labeling or GitHub bot integration
- Schema migration tooling
- CI for non-contract changes (code quality, linting)
- Changes to ADR-001 (already Accepted)

## Stories

| Story ID | Title | Status | Flags |
|----------|-------|--------|-------|
| [ST-015](stories/ST-015-ci-completeness-decision-log-audit.md) | CI completeness: add decision_log_audit and use release_sanity orchestrator | Ready | contract_impact=no, adr_needed=none, diagrams_needed=none |
| [ST-016](stories/ST-016-real-schema-breaking-change-detection.md) | Real schema breaking-change detection for contract schemas | Ready | contract_impact=no, adr_needed=none, diagrams_needed=none |
| [ST-017](stories/ST-017-contract-governance-policy-doc.md) | Contract governance operational policy and PR workflow guide | Ready | contract_impact=no, adr_needed=none, diagrams_needed=none |

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| ADR-001 (contract versioning policy) | Internal | Accepted |
| `contracts/schemas/*.json` exist | Internal | Done |
| `contracts/VERSION` exists | Internal | Done (2.0.0) |
| Existing skill scripts | Internal | Done |
| Existing tests pass (202 tests) | Internal | Verified |

### Story ordering

```
ST-015 (CI completeness)        ST-017 (policy doc)
  |                                  (independent)
  v
ST-016 (real schema detection)
```

- ST-015 first (establishes CI baseline that ST-016 builds upon).
- ST-016 depends on ST-015 (CI must be passing before changing schema_bump behavior).
- ST-017 is independent (docs only) and can be done in parallel.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| CI workflow fails in GitHub Actions due to env differences | Medium | Medium | Local verification steps match CI env |
| Real schema breaking-change detection produces false positives | Low | Medium | Tests include known-non-breaking cases |
| Existing 202 tests break when schema_bump defaults change | Low | High | Preserve backward-compatible CLI flags |

## Readiness Report

### Ready
- **ST-015** -- No blockers. Foundation story. All prerequisite scripts exist.
- **ST-016** -- Soft dependency on ST-015. Contract schemas exist.
- **ST-017** -- No blockers. Docs-only story. ADR-001 provides content basis.
