# ST-051 Codex PLAN Prompt

**Mode:** Read-only PLAN
**Workpack:** `docs/planning/workpacks/ST-051/workpack.md`

## Objective

Plan provider-side closure for the Domain Planner v1 narrow corridor initiative. Do not mutate runtime, contracts, public API, existing fixtures, or HomeTusk files.

## Required Sources

- `AGENTS.md`
- `CODEX.md`
- `docs/CODEX-WORKFLOW.md`
- `docs/planning/strategy/roadmap.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md`
- `docs/planning/epics/EP-016/epic.md`
- `docs/planning/epics/EP-016/stories/ST-051-review-closure-handoff.md`
- `docs/planning/workpacks/ST-048/review-report.md`
- `docs/planning/workpacks/ST-049/review-report.md`
- `docs/planning/workpacks/ST-050/review-report.md`
- `docs/planning/workpacks/ST-049/local-seed-eval-report.json`
- `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md`
- `docs/diagrams/domain-planner-v1-flow.puml`
- `docs/guides/domain-planner-v1-privacy-retention.md`

## Required PLAN Output

- exact closure artifacts to create or update;
- final validation evidence;
- contract/ADR/diagram drift decision;
- privacy/handoff risks;
- Gate C recommendation.

## Forbidden During PLAN

- runtime edits;
- contract/schema/public API edits;
- HomeTusk writes;
- raw fixture text in reports;
- production rollout/config changes.
