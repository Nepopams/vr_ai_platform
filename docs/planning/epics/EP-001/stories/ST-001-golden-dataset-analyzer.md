# ST-001: Golden-dataset analyzer script + ground truth manifest + README

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

As a platform engineer, I need a reproducible script that analyzes shadow router JSONL logs against a golden dataset with ground truth labels, so that I can measure LLM quality (intent match rate, entity hit rate), latency (p50/p95), and error breakdown -- fulfilling initiative AC4 ("reproducible script + README").

The golden dataset fixtures already exist as command inputs (14 files in `skills/graph-sanity/fixtures/commands/`), but they lack expected outcomes. This story adds ground truth annotations and the analyzer script.

### User value

Without this script, we cannot measure whether the shadow LLM router provides any improvement over baseline. The initiative's success metrics (intent match rate, entity hit rate, latency percentiles, error breakdown) are unmeasurable without it.

## Acceptance Criteria

```gherkin
AC-1: Script reads shadow router JSONL and golden dataset
Given a JSONL file at the configured path (default: logs/shadow_router.jsonl)
  And a golden dataset manifest file with ground truth labels
When I run `python scripts/analyze_shadow_router.py --shadow-log <path> --golden-dataset <path>`
Then the script reads all JSONL records and all golden dataset entries without error
  And the script exits 0 on success

AC-2: Metrics report contains required fields
Given the script has processed at least one JSONL record matching a golden dataset entry
When the report is produced
Then it contains:
  - intent_match_rate (float 0.0-1.0): fraction of records where suggested_intent == expected_intent
  - entity_hit_rate (float 0.0-1.0): fraction of records where entity keys match expected
  - latency_p50 (int, ms)
  - latency_p95 (int, ms)
  - error_breakdown (dict: error_type -> count)
  - total_records (int)
  - matched_records (int): records that matched a golden dataset entry by command_id

AC-3: Report output as JSON
Given the script completes
When --output-json <path> is provided
Then a JSON file is written to that path with the metrics report
  And the report is also printed to stdout in human-readable format

AC-4: No raw user text or LLM output in report
Given the script processes JSONL records
When generating the report
Then the report contains NO raw user text, NO raw LLM output
  And a privacy self-test validates this property

AC-5: Golden dataset manifest includes ground truth
Given the file `skills/graph-sanity/fixtures/golden_dataset.json`
When it is loaded
Then each entry has: command_id, expected_intent, expected_entity_keys (list of strings)
  And all 14 existing fixture command_ids are represented

AC-6: README documents usage
Given the file `scripts/README-shadow-analyzer.md`
When a developer reads it
Then it explains: purpose, prerequisites, invocation examples, output format, how to add new golden dataset entries

AC-7: Edge case -- empty JSONL
Given an empty or nonexistent JSONL file
When the script runs
Then it exits 0 with a report showing total_records=0 and all rates as null/n/a
```

## Scope

### In scope

- Golden dataset manifest file (`skills/graph-sanity/fixtures/golden_dataset.json`) with ground truth labels for all 14 existing fixtures
- Python script `scripts/analyze_shadow_router.py`
- README file `scripts/README-shadow-analyzer.md`
- Unit tests for the analyzer

### Out of scope

- Modification of existing shadow router code
- Modification of existing fixture command JSON files
- CI pipeline integration
- Dashboard or web visualization
- Comparison with baseline decisions
- Integration with `scripts/metrics_agent_hints_v0.py`

## Test Strategy

### Unit tests

- `tests/test_analyze_shadow_router.py`:
  - `test_empty_jsonl_produces_zero_report`
  - `test_single_matching_record_correct_intent`
  - `test_single_matching_record_wrong_intent`
  - `test_entity_hit_rate_calculation`
  - `test_latency_percentiles`
  - `test_error_breakdown_counts`
  - `test_unmatched_records_excluded`
  - `test_privacy_no_raw_text`
  - `test_golden_dataset_manifest_schema`

### Integration tests

- Run script end-to-end with synthetic JSONL + golden dataset manifest
- Verify JSON output file is valid and contains all required fields

## Flags

- contract_impact: no
- adr_needed: none
- diagrams_needed: none
- security_sensitive: no
- traceability_critical: no

## Blocked By

- None
