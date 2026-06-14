---
name: vr-planning
description: Instruction-only workflow skill for source-bound Codex-only planning. Use when creating or auditing planning artifacts, epics, stories, sprint scopes, readiness, risks, and delivery boundaries before workpack creation.
---

# vr-planning

## Purpose

Create or audit planning artifacts without inventing product content. Planning must be anchored to existing repository sources and must prepare a safe path to artifact gate or workpack.

## Sources / Inputs

- Triage summary.
- `docs/planning/strategy/product-goal.md`
- `docs/planning/strategy/roadmap.md`
- `docs/planning/releases/MVP.md`
- `docs/_governance/dor.md`
- `docs/_governance/dod.md`
- `docs/planning/_templates/`
- Relevant `docs/planning/initiatives/**`, `docs/planning/epics/**`, and `docs/planning/workpacks/**`.

## Workflow

1. Confirm the scope anchor and sources of truth.
2. Map the request to an existing initiative, epic, story, or workpack where possible.
3. Define in-scope and out-of-scope boundaries.
4. Check DoR readiness and list blockers.
5. Identify artifact gate needs before implementation.
6. Define acceptance criteria and validation approach.
7. Produce a planning artifact or planning audit with evidence.

## Allowed scope

- Create or update planning docs under `docs/planning/**` when requested.
- Create minimal TODO stubs for missing planning files.
- Propose workpack boundaries and validation commands.

## Forbidden scope

- No runtime code writes.
- No contracts, schemas, public API, or fixture changes.
- No new product strategy beyond existing sources.
- No APPLY.
- No human gate bypass.

## Output

```markdown
## Planning Output
- Sources of truth:
- Scope:
- Acceptance criteria:
- Readiness:
- Artifact gate:
- Risks:
- Next step:
```
