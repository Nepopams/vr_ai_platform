# ST-052: Expanded 50-Scenario Fixture Reference and Eval Runner

**Status:** Done (Gate D GO for eval tooling; initiative acceptance HOLD)
**Epic:** `docs/planning/epics/EP-017/epic.md`
**Owner:** Codex / AI Platform engineering team

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md` |
| Execution notes | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md` |
| Epic | `docs/planning/epics/EP-017/epic.md` |
| Workpack | `docs/planning/workpacks/ST-052/workpack.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |
| Existing eval runner | `scripts/evaluate_domain_planner_seed.py` |
| Existing eval tests | `tests/test_domain_planner_seed_eval.py` |

HomeTusk read-only source package:

```text
C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/expanded-golden-scenarios-v1/
```

Source revision read: `b18bfdb6f0bdbf6044ad5b986aee837dca7bf5b3`.

---

## Description

Generalize the privacy-safe provider eval runner so it can consume the expanded HomeTusk v1 fixture filenames and produce a 50-scenario eval report with source metadata, metrics, failure buckets, and no raw scenario text in generated planning/review summaries.

## Acceptance Criteria

```gherkin
Given the HomeTusk expanded v1 fixture directory is available read-only
When the provider eval runner is executed with that source directory
Then it evaluates all 50 scenarios and writes a privacy-safe report
And the report records source revision, fixture versions, scenario/context counts, suite policy, run command, feature flags, schema versions, decision versions, metrics, and failure buckets
And `--check-no-raw-text` fails if raw fixture text appears in the report
And no HomeTusk files, contracts, schemas, public API files, or runtime planner files are modified
```

## Scope

### In scope

- Support both v0 and v1 HomeTusk fixture filenames in the existing eval runner.
- Preserve existing seed fixture behavior and tests.
- Add tests for v1 fixture filename detection and privacy-safe output.
- Generate `docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json`.
- Record ST-052 validation and Gate D evidence.

### Out of scope

- Contract/schema/version/public API changes.
- Runtime planner changes in `graphs/**`, `routers/**`, or `app/**`.
- HomeTusk repository edits or fixture copying into provider contract fixtures.
- First-class `reject`, `confirm`, `answer`, or plural shopping schema implementation.
- Production rollout/config changes.

## Test Strategy

### Unit tests

- `tests/test_domain_planner_seed_eval.py`

### Integration / eval commands

- `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/expanded-golden-scenarios-v1 --check-no-raw-text --output docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json`

### Test data

- HomeTusk expanded v1 fixtures, read-only external input.
- Synthetic unit-test fixtures with redacted placeholder text.

## Flags

- contract_impact: no
- adr_needed: none
- diagrams_needed: none
- security_sensitive: yes
- traceability_critical: yes

## Blocked By

- None for ST-052.

Contract/schema/runtime follow-up remains blocked on later Gate B/Gate C decisions.

## Closure Evidence

| Field | Value |
| --- | --- |
| Eval report | `docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json` |
| Review report | `docs/planning/workpacks/ST-052/review-report.md` |
| Total scenarios | 50 |
| Schema-valid decisions | 50 |
| Blocker failure scenarios | 7 |
| Unsupported auto-execute | 1 |
| Cross-household references | 0 |
| Gate D | GO for ST-052 tooling; HOLD for initiative acceptance |
