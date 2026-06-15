# ST-049 Read-Only Review Report

**Date:** 2026-06-15
**Mode:** Read-only REVIEW after ST-049 APPLY
**Result:** GO for ST-049 closure; HOLD remains for ST-050 runtime acceptance

## Scope Reviewed

| Artifact | Path |
|----------|------|
| Workpack | `docs/planning/workpacks/ST-049/workpack.md` |
| PLAN report | `docs/planning/workpacks/ST-049/plan-report.md` |
| Eval runner | `scripts/evaluate_domain_planner_seed.py` |
| Unit tests | `tests/test_domain_planner_seed_eval.py` |
| Local eval report | `docs/planning/workpacks/ST-049/local-seed-eval-report.json` |
| Story | `docs/planning/epics/EP-016/stories/ST-049-fixture-import-eval-runner.md` |
| Epic | `docs/planning/epics/EP-016/epic.md` |
| Execution notes | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md` |

## GO / NO-GO

**GO for ST-049 closure.**

The eval runner exists, reads the HomeTusk seed source by reference, emits source metadata and scenario-ID-only rows, validates provider decisions against the current decision schema, writes aggregate metrics, and passed the raw fixture text guard.

**HOLD for runtime planner acceptance.**

The local seed report shows current provider behavior still has blocker failures. Those are expected ST-050 inputs, not ST-049 runner defects.

## Must-Fix Before ST-049 Closure

None.

## Must-Fix Before Runtime Acceptance / ST-051 Closure

- Reduce blocker failure scenarios from `2` to the acceptance threshold defined by ST-050/ST-051.
- Address unsupported auto-execute evidence before any planner closure claim.
- Resolve current-schema `reject` behavior or open a dedicated contract workpack if first-class reject semantics are required.
- Improve intent/action boundary evidence, including multi-item item boundary loss.

## Should-Fix

- Keep the runner dependency expectation explicit: current Windows validation needed `.venv/Lib/site-packages` exposed through `PYTHONPATH` when using `python3`.
- Keep the local eval report regenerated after ST-050 runtime changes rather than treating this snapshot as acceptance evidence.

## Evidence

| Check | Result |
|-------|--------|
| `python3 -m pytest tests/test_domain_planner_seed_eval.py -v` | Pass: 4 passed |
| `python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0 --check-no-raw-text --output docs/planning/workpacks/ST-049/local-seed-eval-report.json` | Pass |
| `python3 -m pytest tests/test_quality_eval.py -v` | Pass: 6 passed |
| `git diff --check` | Pass with LF-to-CRLF warnings only |

Local seed eval summary:

| Metric | Value |
|--------|-------|
| Total scenarios | 10 |
| Evaluated scenarios | 10 |
| Schema-valid decisions | 10 |
| Outcome matches | 8 |
| Intent matches | 3 |
| Unsupported auto-execute | 1 |
| Cross-household references | 0 |
| Blocker failure scenarios | 2 |

## Security / Privacy

- The runner output omits raw command text, raw entity names, member display names, zone names, list names, prompts, and raw LLM output.
- `--check-no-raw-text` completed successfully against the HomeTusk seed source.
- The runner forces eval-time log-related environment overrides to avoid decision/text log writes through optional telemetry flags.
- No HomeTusk files were edited or copied into this repository.

## Recommendation

Close ST-049 and proceed to a dedicated ST-050 runtime workpack and read-only PLAN. Do not claim Domain Planner v1 runtime acceptance until blocker failures are addressed and a later review gate passes.
