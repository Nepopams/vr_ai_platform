# ST-007: Partial Trust Rollout Runbook and Operational Documentation

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

As an operator or on-call engineer, I need a runbook documenting the partial trust corridor
rollout procedure (sampling progression, monitoring checklist, rollback steps), so that I
can safely enable, tune, and disable the corridor in production without guesswork.

### User value

The partial trust corridor is disabled by default and requires careful staged rollout. Without
a runbook, operators must reverse-engineer the procedure from code and config. This creates
risk of misconfiguration, delayed rollback, or missed monitoring signals.

## Acceptance Criteria

```gherkin
AC-1: Runbook documents all environment variables
  Given the runbook at docs/operations/partial-trust-runbook.md
  When an operator reads the configuration section
  Then all environment variables are listed:
    - PARTIAL_TRUST_ENABLED (bool, default: false)
    - PARTIAL_TRUST_INTENT (str, default: add_shopping_item)
    - PARTIAL_TRUST_SAMPLE_RATE (float, default: 0.01)
    - PARTIAL_TRUST_TIMEOUT_MS (int, default: 200)
    - PARTIAL_TRUST_PROFILE_ID (str, default: "")
    - PARTIAL_TRUST_RISK_LOG_PATH (str, default: logs/partial_trust_risk.jsonl)
    - LLM_POLICY_ENABLED (bool, required for LLM candidate generation)
  And each variable has: type, default, description, valid range

AC-2: Runbook documents sampling progression
  Given the runbook
  When an operator reads the rollout plan section
  Then it describes the progression: 0.01 -> 0.05 -> 0.10
  And each stage has:
    - duration (minimum observation period)
    - go/no-go criteria (metrics thresholds from analyzer)
    - command to change sampling rate

AC-3: Runbook documents rollback procedure
  Given the runbook
  When an operator reads the rollback section
  Then it describes:
    - immediate kill-switch: set PARTIAL_TRUST_ENABLED=false
    - verification that kill-switch takes effect (check risk-log for status="skipped")
    - rollback to lower sampling rate as alternative to full disable
  And the rollback can be executed in under 1 minute

AC-4: Runbook documents monitoring checklist
  Given the runbook
  When an operator reads the monitoring section
  Then it lists what to monitor:
    - risk-log file growth and recency
    - acceptance_rate from analyzer output
    - error_rate from analyzer output
    - latency_p95 from analyzer output
    - intent_mismatch_rate from analyzer output
  And includes alarm thresholds (e.g., error_rate > 0.05 -> rollback)

AC-5: Runbook documents prerequisites
  Given the runbook
  When an operator reads the prerequisites section
  Then it lists:
    - ADR-004 must be Accepted
    - All initiative ACs verified (reference to verification report)
    - Regression analyzer script available (ST-006)
    - LLM policy configured for partial_trust_shopping task
  And links to each prerequisite artifact

AC-6: No sensitive data in runbook
  Given the runbook
  When reviewed
  Then it contains no API keys, secrets, or production-specific credentials
  And uses placeholder notation for sensitive values (e.g., ${YANDEX_FOLDER_ID})
```

## Scope

### In scope

- Runbook: `docs/operations/partial-trust-runbook.md`
- Environment variable reference (all partial trust config vars)
- Sampling progression plan (0.01 -> 0.05 -> 0.10) with go/no-go criteria
- Rollback procedure (kill-switch + verification)
- Monitoring checklist with alarm thresholds
- Prerequisites checklist with artifact links

### Out of scope

- Any code changes
- Any test changes
- Automated monitoring/alerting setup
- CI/CD pipeline configuration for rollout
- Production-specific deployment instructions (environment-dependent)
- Changes to feature flag defaults in code
- Dashboard or web visualization

## Test Strategy

### Verification

- Manual review: verify each environment variable documented matches `routers/partial_trust_config.py`
- Manual review: verify rollback procedure is executable (env var change -> restart -> check risk-log)
- Checklist: every config parameter in code has a corresponding entry in the runbook

### Completeness check

- Cross-reference with ADR-004 rollout section (0.01 -> 0.05 -> 0.10)
- Cross-reference with initiative deliverables ("Documentation rollout")
- Verify all risk-log statuses are referenced in monitoring section

## Flags

- contract_impact: no
- adr_needed: none
- diagrams_needed: none
- security_sensitive: no
- traceability_critical: no

## Blocked By

- Soft dependency on ST-005 (verification report should be referenced as prerequisite in the runbook)
- Soft dependency on ST-006 (analyzer script should be referenced for monitoring)
- Neither is a hard blocker: the runbook can be written with placeholder links and updated when ST-005/ST-006 complete
