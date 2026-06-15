# WP / ST-052: Expanded 50-Scenario Fixture Reference and Eval Runner

**Status:** Done (Gate D GO for eval tooling; initiative acceptance HOLD)
**Story:** `docs/planning/epics/EP-017/stories/ST-052-expanded-50-scenario-eval-runner.md`
**Owner:** Codex PLAN / Codex APPLY / read-only review gate

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md` |
| Execution notes | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md` |
| Epic | `docs/planning/epics/EP-017/epic.md` |
| Story | `docs/planning/epics/EP-017/stories/ST-052-expanded-50-scenario-eval-runner.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |
| ADR-001 | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| ADR-009 | `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md` |
| Privacy posture | `docs/guides/domain-planner-v1-privacy-retention.md` |

HomeTusk read-only source package:

```text
C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/expanded-golden-scenarios-v1/
```

Source revision read: `b18bfdb6f0bdbf6044ad5b986aee837dca7bf5b3`.

---

## Outcome

ST-052 delivers a privacy-safe provider eval runner path for the HomeTusk expanded v1 50-scenario suite. It produces local evidence for the next contract/runtime decisions without changing contracts, runtime planner behavior, public API, or HomeTusk files.

## Acceptance Criteria

1. Eval runner supports both `golden-scenarios-v0.yaml` / `context-fixtures-v0.yaml` and `golden-scenarios-v1.yaml` / `context-fixtures-v1.yaml`.
2. Eval report records fixture file names, source revision, fixture versions, scenario/context counts, suite policy, run command, feature flags, schema versions, decision versions, metrics, and failure buckets.
3. `reject_or_clarify` v1 expected outcome is evaluated as safe when provider returns clarify or current-schema safe reject.
4. Unit tests cover v1 fixture loading and privacy-safe output.
5. Local 50-scenario report is generated at `docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json`.
6. `--check-no-raw-text` passes for the generated report.
7. No HomeTusk files, contracts, schemas, public API files, or runtime planner files are modified.

## Files to Change

### New files (create)

| File | Description |
|------|-------------|
| `docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json` | Privacy-safe generated 50-scenario eval report. |
| `docs/planning/workpacks/ST-052/review-report.md` | Read-only review gate result after APPLY. |

### Modified files (update)

| File | Change |
|------|--------|
| `scripts/evaluate_domain_planner_seed.py` | Generalize fixture file discovery and report source metadata for v1 suite. |
| `tests/test_domain_planner_seed_eval.py` | Add tests for v1 fixture loading and privacy-safe report behavior. |
| `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md` | Record ST-052 Gate D and evidence. |
| `docs/planning/epics/EP-017/epic.md` | Update ST-052 status after review. |
| `docs/planning/epics/EP-017/stories/ST-052-expanded-50-scenario-eval-runner.md` | Update ST-052 status after review. |

### Deleted files

| File | Reason |
|------|--------|
| None | Not applicable. |

## Implementation Plan

### Step 1: Generalize fixture source loading

Detect supported scenario/context fixture filenames inside the provided source directory and keep the v0 behavior unchanged.

### Step 2: Preserve privacy-safe reporting

Add fixture file metadata and suite policy to the report without adding raw scenario text, household names, or user-facing copy.

### Step 3: Add focused tests

Cover v1 filename detection, metadata, `reject_or_clarify`, and privacy scanning.

### Step 4: Generate local v1 eval evidence

Run the expanded 50-scenario eval against the read-only HomeTusk source and write the report under ST-052.

### Step 5: Review gate and status update

Inspect diffs, validation results, boundaries, and privacy posture; record ST-052 Gate D.

## Verification Commands

```bash
$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 -m pytest tests/test_domain_planner_seed_eval.py -v
$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/expanded-golden-scenarios-v1 --check-no-raw-text --output docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json
git diff --check
git status --short
```

The Windows workspace uses `PYTHONPATH=.;.venv/Lib/site-packages` with `python3` because the system `python3` shim does not expose repository dependencies by default.

## Tests

| Test | Checks | Expected |
|------|--------|----------|
| `tests/test_domain_planner_seed_eval.py` | Eval runner source loading, privacy-safe output, metrics | Pass |
| 50-scenario eval command | Expanded suite can be evaluated and report written | Pass or HOLD with non-zero blocker evidence recorded |

## DoD Checklist

- [x] Unit tests pass.
- [x] 50-scenario eval report is generated.
- [x] `--check-no-raw-text` passes.
- [x] Contract/schema/runtime/HomeTusk forbidden paths remain untouched.
- [x] Review report and ST-052 Gate D are recorded.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| v1 suite has new expected outcome labels | Medium | Medium | Map only safe labels needed for evidence and preserve failure buckets. |
| Eval report leaks raw fixture text | Low | High | Run `--check-no-raw-text` and keep report fields ID/metadata/metrics based. |
| 50-scenario eval has blocker failures | High | High | Record evidence and move next action to HOLD/runtime or contract workpack. |
| Fixture path is unavailable | Low | High | Mark ST-052 HOLD rather than guessing or copying data. |

## Rollback

- Revert changes to `scripts/evaluate_domain_planner_seed.py` and `tests/test_domain_planner_seed_eval.py`.
- Remove `docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json` if generated by this workpack.
- Revert ST-052 status/evidence updates in planning artifacts.

## APPLY Boundaries

### Allowed

- `scripts/evaluate_domain_planner_seed.py`
- `tests/test_domain_planner_seed_eval.py`
- `docs/planning/workpacks/ST-052/**`
- `docs/planning/epics/EP-017/**`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`

### Forbidden

- `contracts/**`
- `contracts/schemas/**`
- `contracts/VERSION`
- `graphs/**`
- `routers/**`
- `app/**`
- `agent_registry/**`
- `agent_runner/**`
- `llm_policy/**`
- HomeTusk repository files
- Production rollout/config files

## Human Gates

- Gate A: GO, recorded in execution notes.
- Gate B: GO for ST-052; HOLD for contract/runtime mutations.
- Human Gate C: delegated GO for ST-052, recorded in execution notes.
- Human Gate D: GO for ST-052 eval tooling; HOLD for initiative acceptance.

## Validation Results

Validation was run on 2026-06-15.

| Command | Result |
|---------|--------|
| `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 -m pytest tests/test_domain_planner_seed_eval.py -v` | Pass: 5 passed |
| `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/expanded-golden-scenarios-v1 --check-no-raw-text --output docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json` | Pass |
| `git diff --check` | Pass with LF-to-CRLF warnings only |

## ST-052 Eval Metrics

| Metric | Value |
|--------|-------|
| Total scenarios | 50 |
| Evaluated scenarios | 50 |
| Schema-valid decisions | 50 |
| Outcome matches | 43 |
| Intent matches | 11 |
| Unsupported auto-execute | 1 |
| Cross-household references | 0 |
| Blocker failure scenarios | 7 |
| Failure buckets | `wrong_outcome=7`, `wrong_intent=39`, `item_boundary_loss=5`, `unsupported_auto_execute=1` |
