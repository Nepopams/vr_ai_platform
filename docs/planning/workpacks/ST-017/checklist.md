# ST-017: DoD Checklist

## Acceptance Criteria

- [ ] AC-1: Breaking/non-breaking classification matches ADR-001 sections 3.1/3.2 exactly
- [ ] AC-2: Non-breaking workflow is step-by-step with paths and commands
- [ ] AC-3: Breaking workflow includes MAJOR bump + approval requirement
- [ ] AC-4: Each CI check documented: script path, what it validates, local command, failures/fixes
- [ ] AC-5: PR checklist is copyable `- [ ]` Markdown checkboxes

## Verification

```bash
test -f docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md && echo "OK"
git diff --name-only | grep -v '^docs/' && echo "FAIL" || echo "OK: docs-only"
```

## Invariants

- [ ] No files outside `docs/` modified
- [ ] All referenced script paths exist
- [ ] Existing tests unaffected
