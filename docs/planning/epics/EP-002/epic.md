# EP-002: Assist-Mode Gap Closure (Documentation and Verification)

**Status:** Ready
**Initiative:** `docs/planning/initiatives/INIT-2026Q1-assist-mode.md`
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q1-assist-mode.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

The assist-mode initiative (INIT-2026Q1-assist-mode) is fully implemented in code:
- `routers/assist/runner.py` -- full assist mode with 3 subsystems (normalization, entity extraction, clarify suggestor)
- `routers/assist/types.py` -- NormalizationHint, EntityHints, ClarifyHint dataclasses
- `routers/assist/config.py` -- per-subsystem feature flags (all default=false)
- `routers/assist/agent_scoring.py` -- deterministic scoring for agent hint candidates
- `app/logging/assist_log.py` -- JSONL logging (summaries only, no raw text)
- `routers/v2.py` line 41 -- integration into pipeline
- `tests/test_assist_mode.py` -- 5 tests
- `tests/test_assist_agent_hints.py` -- 9 tests

**Remaining gaps:**
1. Acceptance rules exist in code but are NOT documented (initiative AC2 requires documentation).
2. No formal verification report mapping each AC to evidence.

## Goal

Close the remaining gap for INIT-2026Q1-assist-mode by:
1. Documenting the acceptance rules for each assist-mode subsystem
2. Producing a formal verification report mapping each initiative AC to code evidence

## Scope

### In scope

- Document acceptance rules for all 3 assist-mode subsystems
- Document agent hint acceptance rules (allowlist, scoring, tiebreaking)
- Verify all 4 initiative acceptance criteria against code evidence
- Produce verification checklist with file/test references

### Out of scope

- Any code changes to the assist-mode implementation
- New tests (existing 14 tests cover the functionality)
- Changes to public contracts or APIs
- Changes to feature flag defaults

## Stories

| Story ID | Title | Status | Flags |
|----------|-------|--------|-------|
| [ST-003](stories/ST-003-acceptance-rules-documentation.md) | Document acceptance rules for assist-mode hints | Ready | contract_impact=no, adr_needed=none, diagrams_needed=none |
| [ST-004](stories/ST-004-retroactive-verification.md) | Retroactive verification of assist-mode initiative ACs | Ready | contract_impact=no, adr_needed=none, diagrams_needed=none |

## Dependencies

- ST-003 has no blockers
- ST-004 depends on ST-003 (verification report should reference the documented rules)

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Code acceptance rules may have edge cases not covered by tests | Low | Low | ST-004 verification will identify gaps; if found, file follow-up story |
| Documentation may become stale if code changes | Low | Low | Reference code locations in docs; add note to update docs when rules change |

## Flags

- contract_impact: no
- adr_needed: none
- diagrams_needed: none

## Readiness Report

### Ready stories

- **ST-003** -- All inputs available, no blockers
- **ST-004** -- All inputs available; depends on ST-003 but can start in parallel

### Not-ready stories

None.
