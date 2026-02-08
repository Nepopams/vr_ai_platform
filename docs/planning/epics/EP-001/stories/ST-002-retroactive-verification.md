# ST-002: Retroactive verification of shadow-router AC1-AC3

**Status:** Ready
**Epic:** `docs/planning/epics/EP-001/epic.md`
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q1-shadow-router.md` |
| Epic | `docs/planning/epics/EP-001/epic.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Description

As a product owner, I need formal documentation that the existing shadow router implementation meets initiative AC1-AC3, so that we can mark the initiative as verified and track evidence for governance audits.

This is a documentation-only story. All implementation is already done. The deliverable is a verification report that maps each AC to concrete evidence (code references, test names, configuration defaults).

### User value

Without formal verification, the initiative cannot be closed. The evidence exists in code but has not been collected into a single auditable document.

## Acceptance Criteria

```gherkin
AC-1: Verification report exists
Given the file `docs/planning/epics/EP-001/verification-report.md`
When a reviewer reads it
Then it contains a table mapping each initiative AC (AC1, AC2, AC3) to:
  - AC description
  - Status (Pass/Fail)
  - Evidence (file paths, line numbers, test names)

AC-2: AC1 evidence -- shadow mode off by default
Given the verification report
When the AC1 row is reviewed
Then it references:
  - config default="false"
  - env var name: SHADOW_ROUTER_ENABLED
  - test: test_shadow_router_no_impact

AC-3: AC2 evidence -- LLM error/timeout does not affect baseline
Given the verification report
When the AC2 row is reviewed
Then it references:
  - test_shadow_router_no_impact -- decision identical with/without shadow
  - test_shadow_router_timeout_no_impact -- timeout logged, baseline unchanged
  - shadow_router.py error handling code

AC-4: AC3 evidence -- no raw text in JSONL logs
Given the verification report
When the AC3 row is reviewed
Then it references:
  - _summarize_entities only logs keys/counts
  - test_shadow_router_logging_shape
  - shadow_router_log.py

AC-5: Initiative status update
Given all AC1-AC3 are verified as Pass
When the verification report is complete
Then `docs/planning/initiatives/INIT-2026Q1-shadow-router.md` status is updated to "Verified (pending AC4)"

AC-6: Verification commands documented
Given the verification report
When a developer wants to re-verify
Then the report includes runnable verification commands with expected outcomes
```

## Scope

### In scope

- Verification report document (`docs/planning/epics/EP-001/verification-report.md`)
- Mapping of AC1-AC3 to code evidence
- Runnable verification commands
- Update initiative status

### Out of scope

- Code changes of any kind
- New tests
- AC4 verification (that is ST-001's deliverable)

## Test Strategy

### Verification

- Run `pytest tests/test_shadow_router.py -v` and confirm 4 tests pass
- Verify all referenced file paths exist in the repo

## Flags

- contract_impact: no
- adr_needed: none
- diagrams_needed: none
- security_sensitive: no
- traceability_critical: no

## Blocked By

- None
