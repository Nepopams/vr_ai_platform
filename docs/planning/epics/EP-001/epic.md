# EP-001: Shadow Router Gap Closure

**Status:** Ready
**Initiative:** `docs/planning/initiatives/INIT-2026Q1-shadow-router.md`
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q1-shadow-router.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

The Shadow LLM-Router (INIT-2026Q1-shadow-router) is largely implemented:
- `routers/shadow_router.py` -- full shadow LLM router with feature flag
- `routers/shadow_types.py` -- RouterSuggestion dataclass
- `app/logging/shadow_router_log.py` -- JSONL logging
- `routers/v2.py` line 40 -- pipeline integration
- `tests/test_shadow_router.py` -- 4 tests covering no-impact, timeout, log shape, policy-disabled
- 14 golden dataset fixtures in `skills/graph-sanity/fixtures/commands/`
- Feature flag: `SHADOW_ROUTER_ENABLED` (default=false)
- Privacy: no raw text in logs (verified by test)

**Remaining gaps against initiative AC:**
1. AC4 is unmet: no reproducible golden-dataset analyzer script or README exists for shadow router logs.
2. AC1-AC3 are implemented but lack formal verification documentation.

## Goal

Close the remaining gaps in INIT-2026Q1-shadow-router so the initiative can be marked Done:
1. Deliver a reproducible analyzer script that reads shadow router JSONL logs, compares against golden dataset ground truth, and produces a metrics report.
2. Formally verify and document that existing implementation meets all initiative AC.

## Scope

### In scope

- Golden dataset manifest with ground truth labels (expected_intent, expected_entities per fixture)
- Python script reading shadow router JSONL logs + golden dataset, producing metrics report
- README with usage instructions for the analyzer
- Unit tests for the analyzer script
- Formal retroactive verification report for AC1-AC3

### Out of scope

- Re-implementation or modification of shadow_router.py
- Re-implementation or modification of shadow_types.py or JSONL logger
- Changes to the existing test suite
- Changes to the v2 router pipeline
- Modifications to existing golden dataset fixture inputs (only adding ground truth labels)
- CI integration of the analyzer (candidate for future initiative)
- Dashboard or visualization of metrics

## Stories

| Story ID | Title | Status | Flags |
|----------|-------|--------|-------|
| [ST-001](stories/ST-001-golden-dataset-analyzer.md) | Golden-dataset analyzer script + ground truth manifest + README | Ready | contract_impact=no, adr_needed=none, diagrams_needed=none |
| [ST-002](stories/ST-002-retroactive-verification.md) | Retroactive verification of shadow-router AC1-AC3 | Ready | contract_impact=no, adr_needed=none, diagrams_needed=none |

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Shadow router implementation (`routers/shadow_router.py`) | Internal | Done |
| JSONL logger (`app/logging/shadow_router_log.py`) | Internal | Done |
| Golden dataset fixtures (14 commands in `skills/graph-sanity/fixtures/commands/`) | Internal | Done (inputs only, no ground truth) |
| Feature flag mechanism (`SHADOW_ROUTER_ENABLED`) | Internal | Done |

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Golden dataset fixtures lack variety for meaningful metrics | Low | Medium | 14 fixtures cover 6 intent categories + edge cases; sufficient for baseline |
| Analyzer output format may need revision after first real shadow run | Medium | Low | Script outputs JSON; easy to extend fields later |
| Ground truth labeling may be subjective for edge cases (empty_text, unknown_intent) | Low | Low | Document labeling convention in the golden dataset manifest |

## Flags

- contract_impact: no
- adr_needed: none
- diagrams_needed: none

## Readiness Report

### Ready stories

- **ST-001** -- Golden-dataset analyzer script + ground truth manifest + README
- **ST-002** -- Retroactive verification of shadow-router AC1-AC3

### Not-ready stories

None.
