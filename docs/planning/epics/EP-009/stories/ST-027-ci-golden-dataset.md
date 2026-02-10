# ST-027: CI Integration for Golden Dataset Quality Report

**Epic:** EP-009 (Golden Dataset and Quality Evaluation)
**Status:** Ready
**Flags:** contract_impact=no, adr_needed=none, diagrams_needed=none

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-009/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| CI workflow | `.github/workflows/ci.yml` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

ST-025 expands the dataset, ST-026 creates the evaluation script. This story
integrates the evaluation into CI and adds user-facing documentation.

## User Value

As a platform developer, I want the golden dataset evaluation to run automatically in
CI (stub mode), producing a quality report artifact, so that regressions in
deterministic pipeline quality are caught early.

## Scope

### In scope

- Add quality evaluation step to `.github/workflows/ci.yml`
- Runs `evaluate_golden.py` in stub mode (no real LLM in CI)
- Publishes report as CI artifact
- Optional: fail CI if deterministic intent_accuracy drops below threshold
- `docs/guides/golden-dataset.md`: how to run locally, add entries, interpret report

### Out of scope

- CI with real LLM (requires secrets management)
- Automated golden dataset generation
- Performance gates based on LLM quality

---

## Acceptance Criteria

### AC-1: CI runs evaluation
```
Given a CI pipeline run
When the quality-eval step executes
Then evaluate_golden.py runs successfully in stub mode
```

### AC-2: Report artifact is produced
```
Given CI run completes
When artifacts are checked
Then quality_eval_report.json is available
```

### AC-3: Documentation exists
```
Given docs/guides/golden-dataset.md
When reviewed
Then it covers: how to run locally, how to add entries, how to interpret report
```

### AC-4: All 228 existing tests pass

---

## Test Strategy

- CI pipeline verification (manual or via test run)
- Manual: docs review
- No new unit tests (CI integration)

---

## Code Touchpoints

| File | Change |
|------|--------|
| `.github/workflows/ci.yml` | Update: add quality-eval step |
| `docs/guides/golden-dataset.md` | New: golden dataset guide |

---

## Dependencies

- ST-025, ST-026 (dataset and script must exist)
