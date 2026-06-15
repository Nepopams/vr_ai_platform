# Codex PLAN — ST-052 Expanded 50-Scenario Eval Runner

## Mode

Read-only PLAN. Do not edit files, install packages, mutate runtime state, commit, or touch HomeTusk files.

## Sources

- `docs/planning/workpacks/ST-052/workpack.md`
- `docs/planning/epics/EP-017/stories/ST-052-expanded-50-scenario-eval-runner.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`
- `scripts/evaluate_domain_planner_seed.py`
- `tests/test_domain_planner_seed_eval.py`
- HomeTusk read-only source: `C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/expanded-golden-scenarios-v1/`

## Required Findings

- Confirm supported fixture filenames and source metadata.
- Confirm exact files to change.
- Confirm forbidden paths stay untouched.
- Confirm validation commands.
- Confirm whether contract/schema/runtime changes are needed.
- Confirm privacy stop conditions for raw fixture text.

## Stop Conditions

- Need to edit `contracts/**`, `contracts/schemas/**`, `contracts/VERSION`, public API, runtime planner files, or HomeTusk files.
- Need to copy raw HomeTusk scenario text into planning/review summaries.
- HomeTusk source package unavailable.
