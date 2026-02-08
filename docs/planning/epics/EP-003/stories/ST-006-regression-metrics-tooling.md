# ST-006: Regression Metrics Analyzer for Partial Trust Risk-Log

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
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Description

As a platform engineer, I need a reproducible script that reads partial trust risk-log JSONL,
computes regression metrics (accepted_llm vs fallback rates, intent/entity mismatches,
latency distribution, error breakdown), and produces a structured report, so that I can
assess whether the partial trust corridor is improving or degrading decision quality.

This fulfills initiative AC4 ("risk-log + regression metrics") and the initiative deliverable
"Risk logging + dashboard script (minimum)".

### User value

Without this tooling, we have risk-log data but no way to systematically analyze it. The
initiative requires measurable regression metrics to decide whether to increase sampling rate
(0.01 -> 0.05 -> 0.10) or roll back.

## Acceptance Criteria

```gherkin
AC-1: Script reads partial trust risk-log JSONL
  Given a JSONL file at the configured path (default: logs/partial_trust_risk.jsonl)
  When I run `python3 scripts/analyze_partial_trust.py --risk-log <path>`
  Then the script reads all JSONL records without error
  And the script exits 0 on success

AC-2: Metrics report contains required fields
  Given the script has processed at least one JSONL record
  When the report is produced
  Then it contains:
    - total_records (int)
    - status_breakdown (dict: status -> count): accepted_llm, fallback_deterministic, not_sampled, skipped, error
    - reason_code_breakdown (dict: reason_code -> count)
    - acceptance_rate (float 0.0-1.0): accepted_llm / (accepted_llm + fallback_deterministic)
    - intent_mismatch_rate (float): fraction of sampled records where diff_summary.intent_mismatch=true
    - entity_key_mismatch_rate (float): fraction of sampled records where diff_summary.entity_key_mismatch=true
    - latency_p50 (int, ms): over sampled records with latency_ms != null
    - latency_p95 (int, ms): over sampled records with latency_ms != null
    - error_rate (float): error / total_records

AC-3: Report output as JSON
  Given the script completes
  When --output-json <path> is provided
  Then a JSON file is written to that path with the metrics report
  And the report is also printed to stdout in human-readable format

AC-4: No raw user text or LLM output in report
  Given the script processes JSONL records
  When generating the report
  Then the report contains only aggregated metrics (counts, rates, percentiles)
  And a privacy self-test validates this property

AC-5: Edge case -- empty or nonexistent JSONL
  Given an empty or nonexistent JSONL file
  When the script runs
  Then it exits 0 with total_records=0 and all rates as null

AC-6: Edge case -- records without diff_summary
  Given JSONL records with status="not_sampled" (which have no diff_summary)
  When the script computes mismatch rates
  Then those records are excluded from mismatch rate calculations
  And the report notes the number of sampled vs total records

AC-7: README documents usage
  Given the file scripts/README-partial-trust-analyzer.md
  When a developer reads it
  Then it explains: purpose, prerequisites, invocation examples, output format, how to interpret metrics, decision criteria for sampling progression
```

## Scope

### In scope

- Python script `scripts/analyze_partial_trust.py`
- README file `scripts/README-partial-trust-analyzer.md`
- Unit tests for the analyzer
- Human-readable stdout output + JSON file output

### Out of scope

- Modification of existing risk-log format or partial trust code
- CI pipeline integration
- Dashboard or web visualization
- Automated decision-making based on metrics (the script reports, humans decide)
- Comparison with golden dataset (this is for shadow router, not partial trust)
- Integration with shadow router analyzer (separate tooling)

## Test Strategy

### Unit tests

- `tests/test_analyze_partial_trust.py`:
  - `test_empty_jsonl_produces_zero_report` -- empty file -> total_records=0, all rates null
  - `test_single_accepted_record` -- one accepted_llm record -> acceptance_rate=1.0
  - `test_single_fallback_record` -- one fallback_deterministic -> acceptance_rate=0.0
  - `test_mixed_statuses` -- 3 accepted + 2 fallback + 5 not_sampled -> correct breakdown and rate
  - `test_intent_mismatch_rate` -- records with/without intent_mismatch -> correct rate
  - `test_entity_mismatch_rate` -- records with/without entity_key_mismatch -> correct rate
  - `test_latency_percentiles` -- known latency values -> correct p50/p95
  - `test_reason_code_breakdown` -- multiple reason codes -> correct counts
  - `test_error_rate` -- error records counted correctly
  - `test_privacy_no_raw_text` -- report contains no raw user/LLM text

### Integration tests

- Run script end-to-end with synthetic JSONL
- Verify JSON output file is valid and contains all required fields

### Test data

- Synthetic JSONL entries covering all statuses (accepted_llm, fallback_deterministic, not_sampled, skipped, error)
- Entries with and without diff_summary, latency_ms, model_meta

## Flags

- contract_impact: no
- adr_needed: none
- diagrams_needed: none
- security_sensitive: no
- traceability_critical: no

## Blocked By

- None (risk-log format is stable and already implemented)
