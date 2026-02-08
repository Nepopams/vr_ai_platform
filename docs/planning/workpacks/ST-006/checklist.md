# ST-006 — AC / DoD Verification Checklist

## Acceptance Criteria

- [ ] AC-1: Script reads JSONL, exits 0
- [ ] AC-2: Report contains all required metric fields
- [ ] AC-3: `--output-json` writes JSON file + human-readable stdout
- [ ] AC-4: No raw text in report
- [ ] AC-5: Empty/nonexistent JSONL → total_records=0, rates null
- [ ] AC-6: Records without diff_summary excluded from mismatch calculations
- [ ] AC-7: README documents usage

## DoD

- [ ] Tests pass: `python3 -m pytest tests/test_analyze_partial_trust.py -v`
- [ ] Script runs on empty: `python3 scripts/analyze_partial_trust.py --risk-log /dev/null`
- [ ] Script runs on sample: produces correct output
- [ ] JSON output valid: `python3 -c "import json; json.load(open('/tmp/report.json'))"`
- [ ] Full suite: `python3 -m pytest tests/ -v` (109+ passed)
- [ ] README exists
- [ ] No existing files modified
