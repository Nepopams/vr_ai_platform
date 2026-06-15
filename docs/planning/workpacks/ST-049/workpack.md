# Workpack: ST-049 — HomeTusk Seed Fixture Reference and Deterministic Eval Runner

**Status:** Done (Gate D GO for eval runner scope)
**Story:** `docs/planning/epics/EP-016/stories/ST-049-fixture-import-eval-runner.md`
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
| Story | `docs/planning/epics/EP-016/stories/ST-049-fixture-import-eval-runner.md` |
| Provider mapping | `docs/planning/epics/EP-016/domain-planner-v1-provider-mapping.md` |
| Privacy posture | `docs/guides/domain-planner-v1-privacy-retention.md` |
| ADR-009 | `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md` |
| Command schema | `contracts/schemas/command.schema.json` |
| Decision schema | `contracts/schemas/decision.schema.json` |
| Existing quality eval | `skills/quality-eval/scripts/evaluate_golden.py` |
| Existing graph sanity | `skills/graph-sanity/scripts/run_graph_suite.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

HomeTusk read-only fixture source:

```text
C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0/
```

Source revision read during ST-048/ST-049 planning: `d924c631c80895995c65f22bec6f77dc0a0347b7`.

---

## Outcome

Add a provider-owned deterministic eval runner that references HomeTusk seed fixtures from their read-only source path, emits privacy-safe scenario-level and aggregate evidence, and records fixture source metadata without copying raw scenario text into this repository.

## Artifact Gate Result

**APPROVED for Codex PLAN under delegated user gate. Runtime planner APPLY remains HOLD.**

| Gate | Result |
|------|--------|
| Gate A | GO: initiative provider-side scope recorded in execution notes. |
| Gate B | GO: EP-016 decomposition recorded. |
| ST-048 Gate D | GO: provider mapping, ADR, diagram, and privacy posture complete. |
| Contract | No contract/schema/version/public API changes in ST-049. |
| Fixture strategy | Reference-only. Do not copy HomeTusk raw fixture YAML into this repo. |
| Security/privacy | Eval output must not include raw command text, item names, member names, zone names, list names, prompt text, or raw LLM output. |
| Human Gate C | GO for ST-049 eval runner APPLY. PLAN confirmed reference-only fixture strategy, no runtime/contract/schema/HomeTusk writes, and `yaml` availability. |
| Human Gate D | GO for ST-049 closure. Eval runner, tests, local seed report, and review evidence are complete. Runtime planner acceptance remains HOLD for ST-050. |

## Acceptance Criteria

1. Eval runner reads HomeTusk seed fixture YAML from a caller-supplied or default read-only source directory.
2. Runner records source repository, source path, source revision, fixture versions, scenario count, and context count.
3. Runner emits one result row per scenario using scenario IDs only.
4. Runner emits aggregate metrics and failure bucket counts.
5. Runner emits skipped/unsupported reasons without raw scenario text.
6. Runner output includes schema version, decision version(s), planner version label, run command, and selected feature flags.
7. Runner validates provider outputs against current `decision.schema.json`.
8. Runner output and tests prove no raw HomeTusk scenario text appears in reports.
9. No HomeTusk files, runtime planner files, contract schemas, contract version, public API files, or existing fixtures are changed.

## Files to Change

### New files

| File | Description |
|------|-------------|
| `scripts/evaluate_domain_planner_seed.py` | Privacy-safe Domain Planner v1 seed eval runner. |
| `tests/test_domain_planner_seed_eval.py` | Unit tests for report redaction, metrics, and source metadata. |
| `docs/planning/workpacks/ST-049/plan-report.md` | Read-only PLAN findings and Gate C recommendation. |
| `docs/planning/workpacks/ST-049/review-report.md` | Read-only review and Gate D recommendation after APPLY. |

### Modified files

| File | Change |
|------|--------|
| `docs/planning/epics/EP-016/epic.md` | Update ST-049 status after completion. |
| `docs/planning/epics/EP-016/stories/ST-049-fixture-import-eval-runner.md` | Update status after completion. |
| `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md` | Record ST-049 Gate C/D decisions and next step. |
| `docs/planning/workpacks/ST-049/workpack.md` | Record Gate C/D and checklist status. |

### Deleted files

| File | Reason |
|------|--------|
| None | No deletion authorized. |

## Forbidden Paths

- `contracts/**`
- `contracts/schemas/**`
- `contracts/VERSION`
- `app/**`
- `graphs/**`
- `routers/**`
- `agents/**`
- `agent_registry/**`
- `agent_runner/**`
- `llm_policy/**`
- `skills/**`
- `.codex/skills/**`
- Existing `skills/**/fixtures/**`
- Any file outside `C:/Users/user/Documents/projects/VR_AI_Platform`
- Any file in the HomeTusk repository

## Implementation Plan

### Step 1: Codex PLAN

Run the read-only PLAN in `docs/planning/workpacks/ST-049/prompt-plan.md`.

### Step 2: Delegated Gate C

Record GO/HOLD/NO-GO after PLAN. GO is allowed only if the runner can be implemented without copying HomeTusk raw fixtures and without changing runtime/contracts.

### Step 3: Eval runner

Create `scripts/evaluate_domain_planner_seed.py` using structured YAML parsing. The runner must:

- load `golden-scenarios-v0.yaml` and `context-fixtures-v0.yaml` from the read-only source directory;
- transform HomeTusk context fixtures into current `CommandDTO` shape in memory only;
- call the current provider decision path without writing decision logs;
- validate decisions against `decision.schema.json`;
- map current-schema provider outcomes through `domain-planner-v1-provider-mapping.md`;
- emit privacy-safe JSON to stdout or `--output`;
- never include raw command text or raw extracted entity names in output.

### Step 4: Tests

Create focused tests using temporary synthetic YAML fixtures. Tests must verify:

- source metadata is included;
- report rows use scenario IDs;
- output omits raw text and raw entity names;
- aggregate metrics and failure buckets are computed;
- unsupported/missing source path is handled predictably.

### Step 5: Review

Run validation commands and record a read-only review report. Do not mark ST-050 runtime ready unless ST-049 evidence is complete.

## Verification Commands

```bash
python3 -m pytest tests/test_domain_planner_seed_eval.py -v
python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0 --check-no-raw-text --output docs/planning/workpacks/ST-049/local-seed-eval-report.json
python3 -m pytest tests/test_quality_eval.py -v
git diff --check
```

Generated local report `docs/planning/workpacks/ST-049/local-seed-eval-report.json` may be created during validation only if it contains no raw scenario text. It is an evaluation artifact, not a fixture copy.

## Validation Results

Validation was run on 2026-06-15. The Windows shell used `PYTHONPATH=.venv/Lib/site-packages` with `python3` because the system `python3` environment does not include `pytest`.

| Command | Result |
|---------|--------|
| `python3 -m pytest tests/test_domain_planner_seed_eval.py -v` | Pass: 4 passed |
| `python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0 --check-no-raw-text --output docs/planning/workpacks/ST-049/local-seed-eval-report.json` | Pass |
| `python3 -m pytest tests/test_quality_eval.py -v` | Pass: 6 passed |
| `git diff --check` | Pass with existing LF-to-CRLF warnings only |

Local seed eval metrics:

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

Failure bucket counts:

| Bucket | Count |
|--------|-------|
| `wrong_intent` | 7 |
| `item_boundary_loss` | 3 |
| `wrong_outcome` | 2 |
| `unsupported_auto_execute` | 1 |

## Tests

| Test | Checks | Expected |
|------|--------|----------|
| `tests/test_domain_planner_seed_eval.py` | Source metadata, redaction, metrics, failure buckets | Pass |
| `scripts/evaluate_domain_planner_seed.py --check-no-raw-text` | Real HomeTusk seed source can be evaluated without raw output | Pass or controlled non-zero with privacy-safe error |
| `tests/test_quality_eval.py` | Existing eval helper regression | Pass |

## DoD Checklist

- [x] Read-only PLAN completed.
- [x] Delegated Gate C GO/HOLD/NO-GO recorded.
- [x] Reference-only fixture strategy preserved.
- [x] Eval runner created.
- [x] Tests created and passing.
- [x] Local seed eval command run.
- [x] Eval report contains no raw scenario text.
- [x] No forbidden paths changed.
- [x] Review report records Gate D recommendation.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Runner leaks raw text in output | Medium | High | Add `--check-no-raw-text` and unit tests for redaction. |
| HomeTusk YAML shape changes | Medium | Medium | Include source version and controlled failure buckets; do not silently guess. |
| Current provider fails many seed scenarios before ST-050 | High | Medium | ST-049 establishes evidence; zero-blocker acceptance belongs to ST-051 after runtime work. |
| PyYAML availability differs by environment | Medium | Medium | PLAN must confirm `yaml` import and document dependency/stop condition. |
| Eval command writes decision logs | Low | High | Use router path without `decision_service.decide()` logging. |

## Rollback

Remove ST-049 runner/tests/reports and revert status updates. No runtime rollback should be needed because runtime paths are forbidden.

## APPLY Boundaries

### Allowed

- `scripts/evaluate_domain_planner_seed.py`
- `tests/test_domain_planner_seed_eval.py`
- `docs/planning/workpacks/ST-049/**`
- `docs/planning/epics/EP-016/epic.md`
- `docs/planning/epics/EP-016/stories/ST-049-fixture-import-eval-runner.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md`

### Forbidden

- Runtime, contracts, schemas, existing fixtures, public API, and HomeTusk files listed above.

## Human Gates

- Gate A: GO recorded in initiative execution notes.
- Gate B: GO for provider planning and EP-016 decomposition.
- ST-048 Gate D: GO.
- Human Gate C: GO for ST-049 eval runner APPLY.
- Human Gate D: GO for ST-049 eval runner closure.
