---
name: vr-contract-governance
description: Instruction-only workflow skill for contract governance in the Codex-only workflow. Use when a request may touch CommandDTO, DecisionDTO, contract schemas, contract versioning, public API compatibility, fixtures, or contract validation gates.
---

# vr-contract-governance

## Purpose

Classify and govern contract-related changes before APPLY. Preserve ADR-001 compatibility rules and prevent unapproved schema/public API drift.

## Sources / Inputs

- `contracts/schemas/`
- `contracts/VERSION`
- `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md`
- `docs/CONTRACTS.md`
- `docs/adr/ADR-001-contract-versioning-compatibility-policy.md`
- `docs/adr/ADR-007-api-versioning.md`
- Relevant fixtures in `skills/**/fixtures/` and `.codex/skills/**/fixtures/`.
- Relevant tests in `tests/`.

## Workflow

1. Determine whether the request changes contract shape, semantics, versioning, public API, or fixtures.
2. Classify as non-breaking, breaking, or no contract impact.
3. If breaking, require Draft ADR or accepted migration plan before implementation.
4. Identify required semver bump and fixture/test updates.
5. Identify validation commands.
6. Produce artifact gate decision.

## Allowed scope

- Read contracts, schemas, fixtures, ADRs, tests, and governance docs.
- Produce a contract impact report.
- Draft TODO-only planning notes when contract inputs are missing.

## Forbidden scope

- No schema edits during triage or PLAN.
- No public API changes without artifact gate approval.
- No contract version bump without approved contract workpack.
- No APPLY.
- No human gate bypass.

## Output

```markdown
## Contract Gate
- Impact: none | non-breaking | breaking | unclear
- Affected contracts:
- ADR-001 classification:
- Version decision:
- Fixtures/tests required:
- Validation commands:
- Gate result:
```
