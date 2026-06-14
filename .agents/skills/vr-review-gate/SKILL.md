---
name: vr-review-gate
description: Instruction-only workflow skill for the Codex-only read-only review gate. Use after APPLY to inspect diffs, evidence, validation results, contract/ADR/diagram drift, security/privacy, observability, and test gaps before Human Gate D.
---

# vr-review-gate

## Purpose

Produce a read-only GO/NO-GO review gate after APPLY and before Human Gate D.

## Sources / Inputs

- Workpack and checklist.
- PLAN findings and APPLY summary.
- Git diff and touched files.
- Relevant contracts, ADRs, diagrams, DoR, DoD, tests, and logs.
- Outputs from `.codex/agents/**` read-only review agents when used.

## Workflow

1. Confirm review is read-only.
2. Inspect changed files and compare against workpack boundaries.
3. Check acceptance criteria, DoD, contracts, ADRs, diagrams, privacy, observability, and tests.
4. Run or record approved validation commands when appropriate.
5. Classify findings as Must-fix, Should-fix, or Nice-to-have.
6. Produce GO/NO-GO recommendation for Human Gate D.

## Allowed scope

- Read files, diffs, test output, and logs.
- Run read-only validation commands.
- Produce review report.

## Forbidden scope

- No production code writes.
- No document mutation.
- No parallel document mutation.
- No APPLY.
- No human gate bypass.
- No fixing issues during review.

## Output

```markdown
## Review Result: GO | NO-GO

### Must-Fix Issues
- None

### Should-Fix Issues
- None

### Evidence
- Files reviewed:
- Commands run:
- Sources checked:

### Recommendation
Approve for Human Gate D | Block until fixes are complete
```
