# ST-005 — AC / DoD Verification Checklist

## Acceptance Criteria

- [ ] AC-1: Verification report maps each initiative AC to code evidence (PASS/FAIL + file:line + test names)
- [ ] AC-2: ADR-004 status = Accepted, date updated, ADR index reflects "accepted"
- [ ] AC-3: Confidence boundary tests (0.59 rejected, 0.60 accepted)
- [ ] AC-4: list_id validation tests (known accepted, unknown rejected, no context rejected)
- [ ] AC-5: Error catch-all test (v2 pipeline Exception → baseline + risk-log status="error")
- [ ] AC-6: Privacy re-verification (no raw text in any risk-log path)

## DoD

- [ ] New tests pass: `python3 -m pytest tests/test_partial_trust_edge_cases.py -v`
- [ ] Existing tests pass: `python3 -m pytest tests/test_partial_trust_phase2.py tests/test_partial_trust_phase3.py -v`
- [ ] Full suite: `python3 -m pytest tests/ -v` (109+ passed)
- [ ] Verification report exists at `docs/planning/epics/EP-003/verification-report.md`
- [ ] ADR-004: `grep "Status" docs/adr/ADR-004-partial-trust-corridor.md` → "Accepted"
- [ ] ADR index: `grep "ADR-004-P" docs/_indexes/adr-index.md` → "accepted"
- [ ] No existing code files modified
