# ST-004: Retroactive Verification of Assist-Mode Initiative ACs

**Status:** Ready
**Epic:** `docs/planning/epics/EP-002/epic.md`
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q1-assist-mode.md` |
| Epic | `docs/planning/epics/EP-002/epic.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Description

The assist-mode initiative defines 4 acceptance criteria. The implementation is complete and tested, but no formal verification report exists. This story produces that report, enabling the initiative status transition from "Proposed" to "Done".

**User value:** Product owner and reviewers can confirm that the initiative is formally closed, with traceable evidence for each acceptance criterion.

## Acceptance Criteria

```gherkin
Scenario: AC1 verification -- feature flag enablement
  Given the verification report exists at docs/planning/epics/EP-002/verification-report.md
  When a reader checks AC1 ("Assist-mode включается флагом")
  Then the report lists:
    - config file: routers/assist/config.py
    - flags: ASSIST_MODE_ENABLED, ASSIST_NORMALIZATION_ENABLED, ASSIST_ENTITY_EXTRACTION_ENABLED, ASSIST_CLARIFY_ENABLED
    - default values: all false
    - test evidence: test_assist_disabled_no_impact

Scenario: AC2 verification -- acceptance rules documented
  Given the verification report exists
  When a reader checks AC2 ("Baseline выбирает принимать подсказку или нет, правила документированы")
  Then the report references:
    - acceptance rules document: docs/contracts/assist-mode-acceptance-rules.md (from ST-003)
    - code functions: _can_accept_normalized_text, _pick_matching_item, _clarify_question_is_safe
    - test evidence: test_assist_entity_whitelist, test_assist_clarify_rejects_mismatched_missing_fields

Scenario: AC3 verification -- error/timeout fallback
  Given the verification report exists
  When a reader checks AC3 ("При любой ошибке/таймауте LLM -- baseline без деградации")
  Then the report references:
    - timeout mechanism: ThreadPoolExecutor + ASSIST_TIMEOUT_MS
    - test evidence: test_assist_timeout_fallback, test_agent_hints_timeout_fallback

Scenario: AC4 verification -- no raw text in logs
  Given the verification report exists
  When a reader checks AC4 ("Логи без raw user text / raw LLM output")
  Then the report references:
    - logging: _log_step uses summaries only
    - test evidence: test_assist_log_no_raw_text, test_agent_hints_privacy_in_logs

Scenario: Initiative status recommendation
  Given the verification report is complete
  When all ACs have evidence mapped
  Then the report includes a GO/NO-GO recommendation for updating initiative status to Done
```

## Scope

### In scope

- Create `docs/planning/epics/EP-002/verification-report.md`
- Map each initiative AC to code evidence (files, functions, tests)
- Run existing tests and record results
- Provide GO/NO-GO recommendation for initiative closure
- If GO: update initiative status

### Out of scope

- Writing new tests
- Code changes
- Performance benchmarking

## Test Strategy

### Verification

- Run `pytest tests/test_assist_mode.py tests/test_assist_agent_hints.py -v` and record results
- Verify each AC has at least one test covering it

## Flags

- contract_impact: no
- adr_needed: none
- diagrams_needed: none
- security_sensitive: no
- traceability_critical: no

## Blocked By

- ST-003 (acceptance rules documentation must exist before AC2 can be fully verified)
