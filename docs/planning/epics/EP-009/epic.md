# EP-009: Golden Dataset and Quality Evaluation

**Status:** Ready
**Initiative:** `docs/planning/initiatives/INIT-2026Q4-production-hardening.md`
**Sprint:** TBD (S06-S07 candidate)
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| Golden dataset | `skills/graph-sanity/fixtures/golden_dataset.json` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

A golden dataset of 14 commands exists at `skills/graph-sanity/fixtures/golden_dataset.json`.
It is used by the graph-sanity skill for deterministic intent/entity validation. However:

- No evaluation script runs commands through the LLM-assisted pipeline
- No quality metrics (intent accuracy, entity precision/recall, clarify rate)
- No CI integration for quality reports
- Dataset is too small for reliable statistical measurement

## Goal

Formalize the golden dataset (expand to 20+ commands), create a reproducible evaluation
script that measures LLM quality against the deterministic baseline, and integrate
a quality report into CI.

## Scope

### In scope

- Expand golden dataset to 20+ commands with expected outputs
- Evaluation script: deterministic-only and LLM-assisted modes
- Metrics: intent accuracy, entity precision/recall, clarify rate, start_job rate
- CI step running evaluation in stub mode (no real LLM in CI)
- Documentation: how to run evaluation, add entries, interpret results

### Out of scope

- Automated pass/fail thresholds beyond simple baseline
- LLM performance benchmarks (latency is EP-010)
- Commands for intents beyond add_shopping_item, create_task, clarify_needed
- Automated golden dataset generation
- Fine-tuning based on evaluation results

## Stories

| Story ID | Title | Status | Flags |
|----------|-------|--------|-------|
| [ST-025](stories/ST-025-expand-golden-dataset.md) | Expand golden dataset to 20+ commands | Ready | contract_impact=no, adr_needed=none, diagrams_needed=none |
| [ST-026](stories/ST-026-quality-evaluation-script.md) | Quality evaluation script with metrics | Ready (dep: ST-025) | contract_impact=no, adr_needed=none, diagrams_needed=none |
| [ST-027](stories/ST-027-ci-golden-dataset.md) | CI integration for quality report + docs | Ready (dep: ST-025, ST-026) | contract_impact=no, adr_needed=none, diagrams_needed=none |

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Existing golden dataset (14 entries) | Internal | Done |
| Graph-sanity skill | Internal | Done |
| Pipeline process_command() | Internal | Done |
| CI workflow (release_sanity) | Internal | Done |
| Existing test suite (228 tests) | Internal | Passing |

### Story ordering

```
ST-025 (expand golden dataset)
  |
  v
ST-026 (evaluation script)
  |
  v
ST-027 (CI integration + docs)
```

Linear dependency chain: dataset -> script -> CI.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Golden dataset entries are subjective | Low | Low | Start with obvious cases; iteratively refine |
| Evaluation script false positives | Low | Medium | Threshold-free in CI initially (report only) |
| Schema of golden_dataset.json breaks existing tests | Low | High | Backward-compatible additions; verify graph-sanity tests |

## Readiness Report

### Ready
- **ST-025** -- No blockers. Existing dataset is foundation. (~0.5 day)
- **ST-026** -- Depends on ST-025. Clear metrics spec. (~1 day)
- **ST-027** -- Depends on ST-025+ST-026. CI pattern from release_sanity. (~0.5 day)

### Conditional agents needed
- None (all flags negative)
