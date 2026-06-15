# Workpack: ST-051 — Review Gate, Closure Evidence, and HomeTusk Handoff

**Status:** Done (Gate D GO; provider initiative closure)
**Story:** `docs/planning/epics/EP-016/stories/ST-051-review-closure-handoff.md`
**Owner:** Codex PLAN / Codex APPLY / read-only review gate

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md` |
| Execution notes | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md` |
| Epic | `docs/planning/epics/EP-016/epic.md` |
| Story | `docs/planning/epics/EP-016/stories/ST-051-review-closure-handoff.md` |
| ST-048 review | `docs/planning/workpacks/ST-048/review-report.md` |
| ST-049 review | `docs/planning/workpacks/ST-049/review-report.md` |
| ST-050 review | `docs/planning/workpacks/ST-050/review-report.md` |
| Handoff note | `docs/planning/epics/EP-016/domain-planner-v1-closure-handoff.md` |
| Seed eval report | `docs/planning/workpacks/ST-049/local-seed-eval-report.json` |
| DoD | `docs/_governance/dod.md` |

## Outcome

Close the provider-side Domain Planner v1 narrow corridor initiative with source-bound evidence, explicit residual risks, and HomeTusk handoff notes. This workpack does not approve HomeTusk runtime work, production rollout, contract changes, or public API changes.

## Artifact Gate Result

| Gate | Result |
|------|--------|
| Gate A | GO, recorded in initiative execution notes. |
| Gate B | GO, recorded in initiative execution notes. |
| ST-048 Gate D | GO, artifact gate complete. |
| ST-049 Gate D | GO, eval runner complete. |
| ST-050 Gate D | GO, runtime adaptation complete with zero blocker failures. |
| Contract | No contract/schema/version/public API changes. |
| ADR/Diagram | ADR-009 and Domain Planner v1 flow diagram remain aligned. |
| Human Gate C | GO for ST-051 docs-only closure APPLY. |
| Human Gate D | GO for provider initiative closure. |

## Acceptance Criteria

1. ST-051 review report states GO/NO-GO, must-fix, should-fix, evidence, drift checks, and recommendation.
2. Handoff note summarizes provider evidence without raw fixture text.
3. Seed eval evidence has zero blocker failures.
4. Contract/ADR/diagram drift is checked.
5. Privacy/retention posture and remaining HOLD items are linked.
6. Roadmap, initiative, epic, and story statuses are updated consistently.
7. No HomeTusk files, contracts, schemas, public API, runtime code, existing fixtures, or `.codex/skills/**` are changed by ST-051.

## Files to Change

### New files

| File | Description |
|------|-------------|
| `docs/planning/workpacks/ST-051/workpack.md` | ST-051 workpack and gate evidence. |
| `docs/planning/workpacks/ST-051/prompt-plan.md` | Read-only PLAN instructions. |
| `docs/planning/workpacks/ST-051/plan-report.md` | PLAN findings and Gate C recommendation. |
| `docs/planning/workpacks/ST-051/review-report.md` | Final review gate and Gate D recommendation. |
| `docs/planning/epics/EP-016/domain-planner-v1-closure-handoff.md` | Provider-side closure and HomeTusk handoff note. |

### Modified files

| File | Change |
|------|--------|
| `docs/planning/strategy/roadmap.md` | Move initiative to Completed and clear active current slot. |
| `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md` | Mark provider initiative Done. |
| `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md` | Record ST-051 Gate C/D and closure decision. |
| `docs/planning/epics/EP-016/epic.md` | Mark EP-016 Done. |
| `docs/planning/epics/EP-016/stories/ST-051-review-closure-handoff.md` | Mark ST-051 Done and link evidence. |

### Deleted files

| File | Reason |
|------|--------|
| None | No deletion authorized. |

## Verification Commands

```bash
python3 -m pytest tests/ -v
python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0 --check-no-raw-text --output docs/planning/workpacks/ST-049/local-seed-eval-report.json
git diff --check
```

## Validation Results

| Command | Result |
|---------|--------|
| `python3 -m pytest tests/ -v` | Pass: 336 passed, 4 skipped |
| `python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0 --check-no-raw-text --output docs/planning/workpacks/ST-049/local-seed-eval-report.json` | Pass |
| `git diff --check` | Pass with LF-to-CRLF warnings only |
| Privacy scan over ST-049/ST-050/ST-051 planning and eval artifacts | Pass: 0 files with raw fixture text matches |

## DoD Checklist

- [x] Read-only PLAN completed.
- [x] Delegated Gate C GO recorded.
- [x] Closure handoff note created.
- [x] Review report records Gate D recommendation.
- [x] Seed eval has zero blocker failures.
- [x] Contract/ADR/diagram drift checked.
- [x] Roadmap/initiative/epic/story statuses updated.
- [x] No HomeTusk files changed.
- [x] No contract/schema/public API/runtime files changed by ST-051.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| HomeTusk treats provider GO as product acceptance | Medium | High | Handoff states provider closure only; HomeTusk acceptance remains separate. |
| Seed set is too small for final product acceptance | High | Medium | Handoff records the 50-scenario requirement as follow-up. |
| Current-schema reject/confirm gaps remain | Medium | Medium | Handoff links mapping and recommends contract workpack if first-class outcomes are required. |
| Residual non-blocker eval buckets are overlooked | Medium | Medium | Handoff and review report list them explicitly. |

## Rollback

Revert ST-051 planning artifacts and status updates. ST-048/ST-050 implementation artifacts should not be reverted unless a separate rollback decision is made.

## APPLY Boundaries

### Allowed

- `docs/planning/workpacks/ST-051/**`
- `docs/planning/epics/EP-016/domain-planner-v1-closure-handoff.md`
- `docs/planning/epics/EP-016/epic.md`
- `docs/planning/epics/EP-016/stories/ST-051-review-closure-handoff.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md`
- `docs/planning/strategy/roadmap.md`

### Forbidden

- Runtime code, contracts, schemas, public API, existing fixtures, HomeTusk files, `.codex/skills/**`, and production rollout/config files.

## Human Gates

- Human Gate C: GO for ST-051 docs-only closure APPLY.
- Human Gate D: GO for provider initiative closure.
