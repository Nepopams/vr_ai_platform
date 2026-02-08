# ST-005: Verify and Harden Partial Trust Scaffolding + Finalize ADR-004

**Status:** Ready
**Epic:** `docs/planning/epics/EP-003/epic.md`
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-partial-trust.md` |
| Epic | `docs/planning/epics/EP-003/epic.md` |
| ADR-004 | `docs/adr/ADR-004-partial-trust-corridor.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Description

As a platform engineer, I need formal verification that the existing partial trust scaffolding
meets all four initiative acceptance criteria, with edge case test coverage for uncovered paths,
so that we have documented evidence the corridor is safe to roll out.

Additionally, ADR-004 (Partial Trust Corridor) is currently in Draft status. This story includes
finalizing it to Accepted, since the implementation matches the decision described in the ADR.

### User value

Without formal verification, we cannot confidently state that the partial trust corridor meets
its safety requirements. Without ADR finalization, the architecture decision lacks governance
approval. Both are prerequisites for rollout.

## Acceptance Criteria

```gherkin
AC-1: Verification report maps each initiative AC to code evidence
  Given a verification report file at docs/planning/epics/EP-003/verification-report.md
  When a reviewer reads it
  Then each of the 4 initiative ACs has:
    - a verdict (PASS/FAIL)
    - file:line references as evidence
    - test name references as evidence
  And all 4 ACs have verdict PASS

AC-2: ADR-004 status is Accepted
  Given docs/adr/ADR-004-partial-trust-corridor.md
  When a reviewer reads the Status field
  Then it says "Accepted"
  And the Date field is updated to the acceptance date
  And the ADR index (docs/_indexes/adr-index.md) reflects status "accepted"

AC-3: Confidence boundary edge case is tested
  Given a test in tests/test_partial_trust_phase2.py (or new file)
  When a candidate has confidence=0.59
  Then evaluate_candidate returns (False, "low_confidence", ...)
  And when a candidate has confidence=0.60
  Then evaluate_candidate returns (True, "accepted", ...)

AC-4: list_id validation paths are tested
  Given a test for list_id validation
  When candidate has list_id="list-1" and context has shopping_lists=[{list_id: "list-1"}]
  Then accepted=True
  And when candidate has list_id="unknown-list" and context has shopping_lists=[{list_id: "list-1"}]
  Then accepted=False with reason="list_id_unknown"
  And when candidate has list_id="list-1" but context is None (no shopping lists)
  Then accepted=False with reason="list_id_unknown"

AC-5: Error catch-all in v2 pipeline is tested
  Given a test in tests/test_partial_trust_phase3.py (or new file)
  When _maybe_apply_partial_trust raises an unexpected Exception during LLM candidate generation
  Then the method returns None (baseline is used)
  And a risk-log entry is written with status="error"

AC-6: No raw user text or LLM output in risk logs (privacy re-verification)
  Given an integration test that triggers accepted_llm, fallback_deterministic, and error paths
  When the risk-log JSONL is inspected
  Then no entry contains raw user command text
  And no entry contains raw LLM output text
```

## Scope

### In scope

- Formal verification report mapping each initiative AC to code evidence
- Finalize ADR-004: Draft -> Accepted (status, date, index update)
- New tests for edge cases:
  - Confidence boundary (0.59 reject, 0.60 accept)
  - list_id validation (known, unknown, no context)
  - Error catch-all in v2 pipeline
  - Privacy re-verification across all risk-log paths
- Update ADR index entry for ADR-004

### Out of scope

- Any changes to acceptance rules logic or thresholds
- Any changes to partial trust config, sampling, candidate generation, or types
- Any changes to RouterV2 pipeline logic
- Changes to public contracts
- Changes to feature flag defaults
- Adding new acceptance rule checks
- Regression metrics tooling (ST-006)
- Rollout documentation (ST-007)

## Test Strategy

### Unit tests

- `tests/test_partial_trust_edge_cases.py` (new file or extend phase2):
  - `test_confidence_boundary_059_rejected` -- confidence=0.59 -> (False, "low_confidence")
  - `test_confidence_boundary_060_accepted` -- confidence=0.60 -> (True, "accepted")
  - `test_list_id_known_accepted` -- list_id matches context -> accepted
  - `test_list_id_unknown_rejected` -- list_id not in context -> (False, "list_id_unknown")
  - `test_list_id_no_context_rejected` -- list_id present, context=None -> (False, "list_id_unknown")
  - `test_list_id_none_accepted` -- no list_id in candidate -> accepted (existing behavior)

### Integration tests

- `tests/test_partial_trust_phase3.py` (extend or new file):
  - `test_partial_trust_error_catchall` -- simulate Exception in LLM generation, verify baseline used + risk-log entry with status="error"
  - `test_risk_log_privacy_all_paths` -- trigger accepted_llm, fallback, error; verify no raw text in any log entry

### Test data

- Reuse existing `_candidate()` and `_command()` helpers from phase2/phase3 test files
- Add context with shopping_lists for list_id tests

## Flags

- contract_impact: no
- adr_needed: lite (finalize existing ADR-004, not create new)
- diagrams_needed: none
- security_sensitive: no
- traceability_critical: no

## Blocked By

- ADR-004 finalization: requires adr-designer agent to review ADR-004 content and approve transition from Draft to Accepted. Alternatively, this story can encompass the finalization itself if the ADR content is deemed correct as-is.

## Notes

- The verification report should be stored at `docs/planning/epics/EP-003/verification-report.md` and follow the pattern established by ST-002 and ST-004 in EP-001/EP-002.
- ADR-004 content appears complete and accurate vs implementation. The finalization is primarily a status change + date update + index update.
