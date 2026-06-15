# ST-049: HomeTusk Seed Fixture Import/Reference and Deterministic Eval Runner

**Status:** Done
**Epic:** `docs/planning/epics/EP-016/epic.md`
**Owner:** Codex PLAN / Codex APPLY / read-only review gate
**Flags:** contract_impact=no-unless-schema-change, adr_needed=none, diagrams_needed=none, security_sensitive=yes, traceability_critical=yes

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md` |
| Epic | `docs/planning/epics/EP-016/epic.md` |
| ST-048 | `docs/planning/epics/EP-016/stories/ST-048-provider-mapping-artifact-gate.md` |
| Existing graph sanity | `skills/graph-sanity/scripts/run_graph_suite.py` |
| Existing quality eval | `skills/quality-eval/scripts/evaluate_golden.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

HomeTusk seed source:

```text
C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0/
```

## Description

Prepare provider-owned fixture source metadata and deterministic eval output for the HomeTusk seed scenarios. This story must avoid raw text in reports and review notes; scenario IDs, source metadata, aggregate metrics, and failure buckets are the reporting boundary.

## Acceptance Criteria

```gherkin
Given the accepted HomeTusk seed fixture package
When provider eval evidence is generated
Then every imported or referenced fixture records source repo, source path, source revision or import date, and fixture version
And per-scenario results are emitted by scenario ID
And aggregate metrics and failure bucket counts are emitted
And unsupported/skipped scenarios include explicit reasons
And eval output includes planner version, decision version, schema version, run command, and feature flags
```

## Scope

### In scope

- Fixture import/reference strategy approved by ST-048.
- Provider eval runner or adapter for HomeTusk seed scenarios.
- Scenario-by-scenario result file using scenario IDs.
- Aggregate metrics and failure bucket report.

### Out of scope

- Expanding the product-owned seed set to 50 scenarios.
- Editing HomeTusk artifacts.
- Contract/schema changes unless a later contract workpack approves them.
- Runtime planner changes unless covered by ST-050.

## Test Strategy

### Unit tests

- Eval parser/mapper tests after implementation workpack is created.

### Integration tests

- Run seed fixture eval against the provider planner path after ST-050.

### Test data

- HomeTusk seed fixture package, referenced by source metadata or imported through a later approved workpack.

## Blocked By

- None. ST-049 is complete.

## Delivery Evidence

| Artifact | Path |
|----------|------|
| Workpack | `docs/planning/workpacks/ST-049/workpack.md` |
| PLAN report | `docs/planning/workpacks/ST-049/plan-report.md` |
| Eval runner | `scripts/evaluate_domain_planner_seed.py` |
| Tests | `tests/test_domain_planner_seed_eval.py` |
| Local seed eval report | `docs/planning/workpacks/ST-049/local-seed-eval-report.json` |
| Review report | `docs/planning/workpacks/ST-049/review-report.md` |

## Gate Decisions

| Gate | Decision |
|------|----------|
| Gate C | GO for eval runner APPLY; no runtime, contract, schema, public API, existing fixture, or HomeTusk edits. |
| Gate D | GO for ST-049 closure; runtime planner acceptance remains HOLD for ST-050/ST-051. |
