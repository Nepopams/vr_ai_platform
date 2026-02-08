# EP-003: Partial Trust Corridor for add_shopping_item

**Status:** Ready
**Initiative:** `docs/planning/initiatives/INIT-2026Q2-partial-trust.md`
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-partial-trust.md` |
| ADR-004 | `docs/adr/ADR-004-partial-trust-corridor.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

The Partial Trust initiative (INIT-2026Q2-partial-trust) enables a controlled LLM-first corridor
for a single intent (`add_shopping_item`). The scaffolding is largely implemented:

- Config, sampling, candidate generation, acceptance rules, types, risk logging -- all implemented
- RouterV2 integration with full pipeline -- implemented
- 9 tests (5 unit + 4 integration) -- passing
- LLM policy routing configured for `partial_trust_shopping` task
- ADR-004 exists but is still in Draft status

Remaining gaps against initiative acceptance criteria:
1. ADR-004 needs finalization (Draft -> Accepted)
2. No regression metrics analyzer script (initiative AC4 partially unmet)
3. Test coverage has gaps in edge cases (confidence boundary, list_id validation, capability_mismatch, policy_disabled paths)
4. No formal verification report mapping each initiative AC to code evidence
5. No rollout documentation (runbook, sampling progression, rollback procedure)

## Decomposition Strategy

**By ordered steps**: verify and harden existing scaffolding, build missing regression tooling, then document rollout. Three vertical slices, each independently demonstrable.

## Goal

Close all remaining gaps for INIT-2026Q2-partial-trust so the initiative can be marked Done:
1. Verify and harden existing scaffolding with formal verification and edge case tests
2. Deliver regression metrics tooling to compare partial trust vs baseline decisions
3. Deliver rollout documentation with runbook, sampling progression, and rollback procedure

## Scope

### In scope

- Formal verification of all 4 initiative ACs against code evidence
- Finalization of ADR-004 (Draft -> Accepted)
- Edge case test additions for uncovered acceptance rule paths
- Regression metrics analyzer script (reads risk-log JSONL, compares accepted_llm vs fallback_deterministic)
- Rollout runbook (sampling progression, monitoring checklist, rollback procedure)
- README for the regression analyzer

### Out of scope

- Re-implementation of partial trust core components (config, sampling, candidate, acceptance, types, risk log)
- Modification of RouterV2 pipeline logic
- Changes to public contracts (CommandDTO, DecisionDTO)
- Changes to LLM policy configuration
- Dashboard or web visualization of metrics
- CI integration of the analyzer
- Extending partial trust to additional intents
- Changing feature flag defaults (PARTIAL_TRUST_ENABLED stays false)

## Stories

| Story ID | Title | Status | Flags |
|----------|-------|--------|-------|
| [ST-005](stories/ST-005-verify-harden-scaffolding.md) | Verify and harden partial trust scaffolding + finalize ADR-004 | NOT READY (adr_needed=lite) | contract_impact=no, adr_needed=lite, diagrams_needed=none |
| [ST-006](stories/ST-006-regression-metrics-tooling.md) | Regression metrics analyzer for partial trust risk-log | Ready | contract_impact=no, adr_needed=none, diagrams_needed=none |
| [ST-007](stories/ST-007-rollout-documentation.md) | Partial trust rollout runbook and operational documentation | Ready | contract_impact=no, adr_needed=none, diagrams_needed=none |

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Partial trust implementation (config, sampling, candidate, acceptance, types, risk log) | Internal | Done |
| RouterV2 integration (`_maybe_apply_partial_trust`) | Internal | Done |
| Existing tests (phase 2 + phase 3) | Internal | Done (9 tests) |
| LLM policy config (`partial_trust_shopping` task) | Internal | Done |
| ADR-004 Draft | Internal | Draft -- must be finalized in ST-005 |
| ST-005 verification report | Internal | Needed before ST-007 can reference evidence |

### Story ordering

- ST-005 should be completed first (verification + ADR finalization provides foundation)
- ST-006 can start in parallel with ST-005 (no hard dependency)
- ST-007 depends on ST-005 (rollout docs should reference verified evidence)

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Edge case tests may reveal acceptance rule bugs | Low | Medium | Any bugs found become must-fix items within ST-005; scaffolding is well-structured |
| ADR-004 finalization may require content changes beyond status flip | Low | Low | ADR content already covers all decision aspects; review may add minor clarifications |
| Risk-log JSONL format may lack fields needed for regression analysis | Low | Medium | Current log format includes baseline_summary, llm_summary, diff_summary -- sufficient for comparison |
| Rollout runbook may become stale if config changes | Medium | Low | Reference env var names and config file paths; add maintenance note |

## Flags

- contract_impact: no (no public contract changes anywhere in this epic)
- adr_needed: lite (ST-005 finalizes existing ADR-004)
- diagrams_needed: none

## Readiness Report

### Ready stories

- **ST-006** -- Regression metrics analyzer. All inputs available, no blockers.
- **ST-007** -- Rollout documentation. Can start after ST-005, but all information is available.

### Not-ready stories

- **ST-005** -- Verify and harden scaffolding. Blocked on: ADR-004 needs finalization (Draft -> Accepted). The story itself encompasses ADR finalization as a deliverable, so it can proceed if we accept "finalize ADR" as part of the story scope rather than a prerequisite.

### Suggested next subagent calls

- **adr-designer**: Review and finalize `docs/adr/ADR-004-partial-trust-corridor.md` (Draft -> Accepted). This unblocks ST-005.
