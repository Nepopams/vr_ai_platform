# Checklist / ST-001: Golden-dataset analyzer script

**Story:** `docs/planning/epics/EP-001/stories/ST-001-golden-dataset-analyzer.md`
**DoD:** `docs/_governance/dod.md`

---

## Acceptance Criteria Verification

- [ ] **AC-1: Script reads JSONL and golden dataset**
  - Command: `python scripts/analyze_shadow_router.py --shadow-log <path> --golden-dataset <path>`
  - Expected: exits 0, prints report to stdout
  - Test: `test_end_to_end_with_json_output`

- [ ] **AC-2: Report contains required fields**
  - Fields: intent_match_rate, entity_hit_rate, latency_p50, latency_p95, error_breakdown, total_records, matched_records
  - Tests: `test_single_matching_record_correct_intent`, `test_entity_hit_rate_calculation`, `test_latency_percentiles`, `test_error_breakdown_counts`

- [ ] **AC-3: JSON output file**
  - Command: `python scripts/analyze_shadow_router.py --output-json /tmp/report.json`
  - Expected: file created, valid JSON, all required fields
  - Test: `test_end_to_end_with_json_output`

- [ ] **AC-4: No raw text in report (privacy)**
  - Command: `python scripts/analyze_shadow_router.py --self-test`
  - Expected: exits 0, "self-test ok"
  - Test: `test_privacy_no_raw_text`

- [ ] **AC-5: Golden dataset manifest**
  - File: `skills/graph-sanity/fixtures/golden_dataset.json`
  - Expected: 14 entries, each with command_id + expected_intent + expected_entity_keys
  - Test: `test_golden_dataset_manifest_schema`

- [ ] **AC-6: README**
  - File: `scripts/README-shadow-analyzer.md`
  - Expected: sections for purpose, prerequisites, invocation, output format, extending

- [ ] **AC-7: Empty JSONL edge case**
  - Command: `python scripts/analyze_shadow_router.py --shadow-log /dev/null`
  - Expected: total_records=0, rates=null, exit 0
  - Test: `test_empty_jsonl_produces_zero_report`

---

## DoD Verification

### Code Quality

- [ ] Python 3.11+ idioms (type hints, dataclasses, pathlib)
- [ ] No external dependencies added
- [ ] No import errors
- [ ] Follows `scripts/metrics_agent_hints_v0.py` patterns
- [ ] Code reviewed

### Tests

- [ ] 10 tests passing: `pytest tests/test_analyze_shadow_router.py -v`
  - `test_empty_jsonl_produces_zero_report`
  - `test_single_matching_record_correct_intent`
  - `test_single_matching_record_wrong_intent`
  - `test_entity_hit_rate_calculation`
  - `test_latency_percentiles`
  - `test_error_breakdown_counts`
  - `test_unmatched_records_excluded`
  - `test_privacy_no_raw_text`
  - `test_golden_dataset_manifest_schema`
  - `test_end_to_end_with_json_output`
- [ ] Full suite green: `pytest`
- [ ] Each test isolated (uses tmp_path)

### Documentation

- [ ] `scripts/README-shadow-analyzer.md` created
- [ ] No contract updates needed
- [ ] No ADR needed
- [ ] No diagram updates needed

### Security / Privacy

- [ ] DANGEROUS_FIELDS set defined
- [ ] Self-test passes
- [ ] No raw text in stdout or JSON output

---

## Verification Commands

```bash
# 1. Golden dataset
python -c "import json; from pathlib import Path; d=json.loads(Path('skills/graph-sanity/fixtures/golden_dataset.json').read_text()); assert len(d)==14; print('OK')"

# 2. Self-test
python scripts/analyze_shadow_router.py --self-test

# 3. Empty JSONL
python scripts/analyze_shadow_router.py --shadow-log /dev/null

# 4. Unit tests
pytest tests/test_analyze_shadow_router.py -v

# 5. Full suite
pytest

# 6. Privacy grep
python scripts/analyze_shadow_router.py --shadow-log /dev/null 2>&1 | grep -iE "молоко|хлеб|яйца|бананы|сахар" && echo FAIL || echo OK
```

---

## Sign-off

- [ ] All AC verified
- [ ] All DoD criteria met
- [ ] Reviewer GO decision
