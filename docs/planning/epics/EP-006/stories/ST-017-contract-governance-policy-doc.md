# ST-017: Contract Governance Operational Policy and PR Workflow Guide

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
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

ADR-001 defines the contract versioning policy but there is no operational runbook:
- "I need to change a contract field -- what do I do step by step?"
- "How do I know if my change is breaking?"
- "What does the PR look like for a contract change?"

## User Value

As a developer making contract changes, I want a clear step-by-step guide, so that
I follow the process correctly and my PR passes CI on the first attempt.

## Scope

### In scope

- Create `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` with:
  - Breaking vs non-breaking classification (from ADR-001)
  - Step-by-step: non-breaking workflow (add optional field)
  - Step-by-step: breaking workflow (change/remove field, major bump)
  - Version bump procedure (when, how, baseline update)
  - CI checks explained (what each check does, how to read failures)
  - PR checklist for contract changes

### Out of scope

- Changes to ADR-001
- Changes to CI workflow or scripts
- PR template automation
- CHANGELOG.md creation

---

## Acceptance Criteria

### AC-1: Breaking vs non-breaking classification
```
Given the runbook
When a developer reads the classification section
Then they can classify any field change as breaking or non-breaking
And the classification matches ADR-001 exactly
```

### AC-2: Non-breaking workflow is step-by-step
```
Given a developer wants to add an optional field
When they follow the "Non-Breaking Change" section
Then steps include: edit schema, update fixtures, run checks locally,
  bump PATCH/MINOR, update baseline, submit PR
```

### AC-3: Breaking workflow includes major bump and approval
```
Given a developer wants to remove a required field
When they follow the "Breaking Change" section
Then steps include: confirm necessity, edit schema, bump MAJOR,
  update baseline, request approval, submit PR with ADR reference
```

### AC-4: CI checks are explained
```
Given the runbook
When a developer reads "CI Checks"
Then each check is listed with: what it validates, script path,
  how to run locally, common failures and fixes
```

### AC-5: PR checklist is actionable
```
Given the runbook
When a developer reads "PR Checklist"
Then they see a copyable checkbox list covering: schema change,
  fixtures updated, version bumped, baseline updated, CI passes
```

---

## Test Strategy

### No automated tests (docs-only story)

### Manual verification
- All sections present and internally consistent
- Breaking/non-breaking rules match ADR-001 exactly
- All referenced script paths exist in repo

---

## Code Touchpoints

| File | Change |
|------|--------|
| `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` | New file |

---

## Dependencies

- None (can be done in parallel with ST-015 and ST-016)
