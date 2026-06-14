---
name: vr-workpack-prompts
description: Instruction-only workflow skill for creating Codex-only workpacks and PLAN/APPLY boundaries. Use when preparing implementation packets, read-only PLAN instructions, APPLY scope, validation commands, rollback, and human gate checkpoints.
---

# vr-workpack-prompts

## Purpose

Create workpacks and Codex PLAN/APPLY boundaries that are executable, source-bound, and safe for human-gated delivery.

## Sources / Inputs

- Approved planning output.
- Artifact gate result.
- `docs/planning/_templates/workpack.md`
- Relevant story, epic, initiative, release, ADR, contracts, diagrams, DoR, and DoD.
- Existing workpacks for format reference only.

## Workflow

1. Confirm sources of truth and artifact gate status.
2. Define outcome, acceptance criteria, allowed paths, forbidden paths, risks, rollback, tests, and validation commands.
3. Create or update `workpack.md`.
4. Create PLAN instructions only after workpack is Ready.
5. PLAN must be read-only and must output findings.
6. Create APPLY instructions only after Human Gate C approves PLAN.
7. APPLY must reference actual PLAN findings and stop conditions.

## Allowed scope

- Create or update workpack and prompt-planning docs under `docs/planning/workpacks/**`.
- Define allowed/forbidden paths and validation commands.
- Add TODO placeholders for unknown implementation facts.

## Forbidden scope

- No runtime code writes.
- No implementation during workpack creation.
- No prompt-apply before approved PLAN findings.
- No APPLY before Human Gate C.
- No human gate bypass.

## Output

```markdown
## Workpack / Prompt Output
- Workpack path:
- Status:
- PLAN readiness:
- APPLY readiness:
- Gates:
- Validation:
- Stop conditions:
```
