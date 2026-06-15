# ST-050 Read-Only Review Report

**Date:** 2026-06-15
**Mode:** Read-only REVIEW after ST-050 APPLY
**Result:** GO for ST-050 closure; ST-051 closure/handoff remains pending

## Scope Reviewed

| Artifact | Path |
|----------|------|
| Workpack | `docs/planning/workpacks/ST-050/workpack.md` |
| PLAN report | `docs/planning/workpacks/ST-050/plan-report.md` |
| Runtime graph | `graphs/core_graph.py` |
| RouterV2 | `routers/v2.py` |
| Tests | `tests/test_domain_planner_v1_corridor.py` |
| Seed eval report | `docs/planning/workpacks/ST-049/local-seed-eval-report.json` |
| Initiative execution notes | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md` |

## GO / NO-GO

**GO for ST-050 closure.**

The runtime adaptation stays inside the approved current-schema boundary, preserves schema-valid decisions, adds narrow-corridor guardrails, regenerates seed eval evidence with zero blocker failures, and keeps HomeTusk files/contracts/public API untouched.

**HOLD for initiative closure.**

ST-051 must still produce final review/closure evidence and HomeTusk handoff notes.

## Must-Fix Issues

None for ST-050 closure.

## Should-Fix / Follow-Up

- Remaining eval buckets `wrong_intent=7` and `item_boundary_loss=2` are non-blockers under the ST-049/ST-050 blocker definition but should be documented in ST-051 handoff.
- The current-schema `reject` mapping remains semantically rough (`status=error`, `action=clarify`); first-class reject still requires a dedicated contract workpack if HomeTusk requires it.
- Seed coverage remains 10 scenarios; the HomeTusk package still requires 50 product-owned scenarios before final Domain Planner acceptance.

## Evidence

| Check | Result |
|-------|--------|
| `python3 -m pytest tests/test_domain_planner_v1_corridor.py -v` | Pass: 7 passed |
| `python3 -m pytest tests/test_multi_item_e2e.py tests/test_planner_multi_item.py tests/test_graph_execution.py tests/test_api_decide.py -v` | Pass: 14 passed |
| `python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0 --check-no-raw-text --output docs/planning/workpacks/ST-049/local-seed-eval-report.json` | Pass |
| `python3 -m pytest tests/test_domain_planner_seed_eval.py -v` | Pass: 4 passed |
| `python3 -m pytest tests/ -v` | Pass: 336 passed, 4 skipped |
| `git diff --check` | Pass with LF-to-CRLF warnings only |
| Privacy scan over ST-050/ST-049 planning and eval artifacts | Pass: 0 files with raw fixture text matches |

Seed eval summary after ST-050:

| Metric | Value |
|--------|-------|
| Total scenarios | 10 |
| Evaluated scenarios | 10 |
| Schema-valid decisions | 10 |
| Outcome matches | 10 |
| Unsupported auto-execute | 0 |
| Cross-household references | 0 |
| Blocker failure scenarios | 0 |

## Contract / ADR / Diagram Drift

| Area | Result |
|------|--------|
| Contract drift | None. No `contracts/**`, schema, version, or public API files changed. |
| ADR drift | None. Runtime behavior follows ADR-009 current-schema mapping and narrow corridor. |
| Diagram drift | None. AI Platform still returns provider decisions only; HomeTusk remains validation/execution authority. |

## Security / Privacy

- No HomeTusk files were edited.
- No raw fixture text is included in ST-050 planning artifacts or the regenerated local seed eval report.
- ASR remains transcription-only and has a regression test proving `/v1/asr/transcribe` does not call the decision service.
- Raw text logging was not enabled.

## Recommendation

Approve ST-050 for Human Gate D and proceed to ST-051 final review, closure evidence, and HomeTusk handoff.
