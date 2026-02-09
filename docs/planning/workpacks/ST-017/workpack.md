# Workpack: ST-017 — Contract Governance Runbook

**Status:** Ready
**Story:** `docs/planning/epics/EP-006/stories/ST-017-contract-governance-policy-doc.md`

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-006/epic.md` |
| Story | `docs/planning/epics/EP-006/stories/ST-017-contract-governance-policy-doc.md` |
| ADR-001 | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

Developer-facing runbook at `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` translating ADR-001 into actionable step-by-step workflows for contract changes.

## Acceptance Criteria

1. Breaking vs non-breaking classification matches ADR-001 exactly
2. Non-breaking workflow: step-by-step with paths and commands
3. Breaking workflow: includes MAJOR bump and approval requirement
4. CI checks explained: each check with script path, local run command, failures/fixes
5. PR checklist: copyable Markdown checkboxes

---

## Files to Change

| File | Change |
|------|--------|
| `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` | New file |

---

## Implementation Plan

### Step 1: Create runbook with all sections

Single file `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` containing:

1. **Breaking vs Non-Breaking Classification** — source from ADR-001 sections 3.1 (non-breaking: add optional field, add optional property, extend enum) and 3.2 (breaking: remove required, change type, rename, optional→required)

2. **Non-Breaking Change Workflow** — steps: identify as non-breaking → edit schema → update fixtures → run `validate_contracts` locally → run `schema_bump check` → bump PATCH/MINOR in `contracts/VERSION` → update baseline → submit PR

3. **Breaking Change Workflow** — steps: confirm necessity → reference/create ADR → edit schema → bump MAJOR → update baseline → update fixtures → document migration → request approval → submit PR

4. **Version Bump Procedure** — where version lives (`contracts/VERSION` = 2.0.0), PATCH vs MINOR vs MAJOR, how to use `bump_version.py`, baseline update

5. **CI Checks Explained** — table with 5 checks: validate_contracts, check_breaking_changes, graph_sanity, decision_log_audit, release_sanity — each with script path, what it validates, `python ...` local command, common failures/fixes

6. **PR Checklist** — copyable `- [ ]` checkboxes: schema change, fixtures updated, version bumped, baseline updated, CI passes, ADR (if breaking)

---

## Verification Commands

```bash
# File exists
test -f docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md && echo "OK" || echo "MISSING"

# All referenced scripts exist
for f in \
  skills/contract-checker/scripts/validate_contracts.py \
  skills/schema-bump/scripts/check_breaking_changes.py \
  skills/schema-bump/scripts/bump_version.py \
  skills/graph-sanity/scripts/run_graph_suite.py \
  skills/decision-log-audit/scripts/audit_decision_logs.py \
  skills/release-sanity/scripts/release_sanity.py; do
  test -f "$f" && echo "OK: $f" || echo "MISSING: $f"
done

# Section headers present
for section in "Breaking" "Non-Breaking" "Version Bump" "CI Checks" "PR Checklist"; do
  grep -qi "$section" docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md && echo "OK: $section" || echo "MISSING: $section"
done

# No code changes
git diff --name-only | grep -v '^docs/' && echo "FAIL: non-docs" || echo "OK: docs-only"
```

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Content drifts from ADR-001 | Medium | Low | Include "sourced from ADR-001" reference |

## Rollback

- `git revert <commit>` removes the file. No downstream deps.

## APPLY Boundaries

**Allowed:** `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` (create)
**Forbidden:** everything else
