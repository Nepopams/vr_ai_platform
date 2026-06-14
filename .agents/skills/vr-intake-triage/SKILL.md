---
name: vr-intake-triage
description: Instruction-only workflow skill for Codex-only intake triage in this repository. Use when classifying a request, identifying scope, risk, missing inputs, source anchors, and the next delivery workflow step before planning or workpack creation.
---

# vr-intake-triage

## Purpose

Classify a user request before planning or implementation. Keep the result source-bound, minimal, and aligned with the Codex-only workflow.

## Sources / Inputs

- User request and constraints.
- `AGENTS.md`
- `docs/CODEX-WORKFLOW.md`
- `docs/planning/strategy/product-goal.md`
- `docs/planning/strategy/roadmap.md`
- `docs/planning/releases/MVP.md`
- `docs/_governance/dor.md`
- `docs/_governance/dod.md`
- Relevant ADRs, contracts, diagrams, and workpacks if the request touches them.

## Workflow

1. Restate the request in repository terms only.
2. Identify the current scope anchor: release, initiative, epic, story, or workpack.
3. Classify change type: docs-only, planning, contract, ADR, diagram, runtime, test, observability, security, or mixed.
4. Identify risk level and impacted sources of truth.
5. Set flags: `contract_impact`, `adr_needed`, `diagrams_needed`, `security_sensitive`, `traceability_critical`.
6. List missing inputs and blockers.
7. Recommend next workflow step: planning, artifact gate, workpack, PLAN, APPLY, review, or blocked.

## Allowed scope

- Read repository files.
- Produce a triage summary.
- Recommend gates and skills.
- Create or update planning-only artifacts when explicitly requested and source-bound.

## Forbidden scope

- No production code writes.
- No runtime, contracts, schemas, public API, or fixture changes.
- No APPLY.
- No human gate bypass.
- No assumptions from repository name or external projects.

## Output

```markdown
## Triage Summary
- Request type:
- Scope anchor:
- Risk:
- Impacted sources:
- Flags:
- Missing inputs:
- Next step:
```
