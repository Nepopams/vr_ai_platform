# ST-016: Real Schema Breaking-Change Detection for Contract Schemas

**Epic:** EP-006 (SemVer and CI Contract Governance)
**Status:** Ready (dep: ST-015)
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
| Schema bump check | `skills/schema-bump/scripts/check_breaking_changes.py` |
| Contract schemas | `contracts/schemas/command.schema.json`, `contracts/schemas/decision.schema.json` |
| Contract version | `contracts/VERSION` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

Current `check_breaking_changes.py` has two gaps:

1. **Synthetic fixtures**: defaults to `example.schema.json` vs `example.schema.next.json`,
   not real contract schemas. CI never checks actual schemas for breaking changes.

2. **Shallow detection**: only detects removed required fields. Per ADR-001, breaking
   changes also include field deletion from properties, field type change, and
   optional->required promotion.

Solution: baseline copy approach -- maintain `contracts/schemas/.baseline/` with
last-known-good schemas. CI compares current vs baseline.

## User Value

As a platform developer, I want CI to detect actual breaking changes in my contract
schemas, so that I cannot accidentally ship a breaking change without a major version bump.

## Scope

### In scope

- Extend `find_breaking_changes()`: field deletion, type change, new required field
- Add `compare_schemas()` function for two schema paths
- Create `contracts/schemas/.baseline/` with copies of current schemas
- Update CI step to compare real schemas against baseline
- Unit tests for each breaking change category
- Preserve backward compatibility: `--old`/`--new` CLI flags still work

### Out of scope

- Git-diff-based detection (deferred)
- Automated baseline update on version bump
- Nested/deep property comparison (top-level only for MVP)
- `$ref` resolution in schemas
- Changes to `bump_version.py`

---

## Acceptance Criteria

### AC-1: Detect field deletion from properties
```
Given old schema with properties {id, name, status}
And new schema with properties {id, status}
When find_breaking_changes() is called
Then it returns: "Removed property: name"
```

### AC-2: Detect field type change
```
Given old schema with property status: {type: "string"}
And new schema with property status: {type: "object"}
When find_breaking_changes() is called
Then it returns: "Type changed for property 'status': string -> object"
```

### AC-3: Detect new required field
```
Given old schema with required: ["id"]
And new schema with required: ["id", "name"]
When find_breaking_changes() is called
Then it returns: "New required field: name"
```

### AC-4: Detect removed required field (existing behavior preserved)
```
Given old schema with required: ["id", "status"]
And new schema with required: ["id"]
When find_breaking_changes() is called
Then it returns: "Removed required field: status"
```

### AC-5: Non-breaking change is not flagged
```
Given old schema with properties {id, status}
And new schema with properties {id, status, description} where description is optional
When find_breaking_changes() is called
Then it returns no breaking changes
```

### AC-6: CI checks real schemas against baseline
```
Given the CI workflow runs schema_bump check
When contracts/schemas/command.schema.json differs from its baseline
And the difference is a breaking change
Then the CI step fails with a clear message
```

### AC-7: Baseline directory contains current schemas
```
Given contracts/schemas/.baseline/
When inspected after delivery
Then it contains copies matching current schemas
```

### AC-8: All existing tests pass
```
Given the test suite (202+)
When ST-016 changes are applied
Then all tests pass and new tests also pass
```

---

## Test Strategy

### Unit tests (~8 new)
- `test_detect_field_deletion`
- `test_detect_type_change`
- `test_detect_new_required_field`
- `test_detect_removed_required_field_backward_compat`
- `test_non_breaking_optional_field_addition`
- `test_no_changes_returns_empty`
- `test_real_schemas_against_baseline_no_breaking`
- `test_cli_old_new_flags_backward_compat`

### Regression
- Full test suite must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `skills/schema-bump/scripts/check_breaking_changes.py` | Extend detection; add `compare_all_schemas()`; update defaults |
| `contracts/schemas/.baseline/command.schema.json` | New: copy of current schema |
| `contracts/schemas/.baseline/decision.schema.json` | New: copy of current schema |
| `.github/workflows/ci.yml` | Update schema_bump check to use baseline |
| `tests/test_skill_checks.py` | Add breaking-change detection tests |

---

## Dependencies

- ST-015 (CI completeness) -- CI should be green before changing schema_bump
