# Workpack — ST-005: Verify and Harden Partial Trust Scaffolding + Finalize ADR-004

**Status:** Ready
**Story:** `docs/planning/epics/EP-003/stories/ST-005-verify-harden-scaffolding.md`
**Epic:** `docs/planning/epics/EP-003/epic.md`
**Initiative:** `docs/planning/initiatives/INIT-2026Q2-partial-trust.md`

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-partial-trust.md` |
| ADR-004 | `docs/adr/ADR-004-partial-trust-corridor.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

A formal verification report proving all 4 initiative ACs are met, plus edge case tests hardening uncovered paths in acceptance rules. ADR-004 status confirmed Accepted, ADR index updated.

---

## Acceptance Criteria Summary

1. Verification report at `docs/planning/epics/EP-003/verification-report.md` with PASS verdict for all 4 ACs
2. ADR-004 status is Accepted (already done pre-sprint), ADR index reflects this
3. Edge case tests for confidence boundary (0.59 reject, 0.60 accept)
4. Edge case tests for list_id validation (known, unknown, no context)
5. Edge case test for error catch-all in v2 pipeline
6. Privacy re-verification test across all risk-log paths

---

## Files to Change

### New files (CREATE)

| File | Description |
|------|-------------|
| `tests/test_partial_trust_edge_cases.py` | Edge case tests for acceptance rules + v2 error catch-all + privacy |
| `docs/planning/epics/EP-003/verification-report.md` | Formal AC verification report |

### Modified files (MODIFY)

None. ADR-004 and ADR index already updated pre-sprint.

### Key files to READ (context, not modify)

| File | Why |
|------|-----|
| `routers/partial_trust_config.py` | AC1: feature flags with defaults |
| `routers/partial_trust_acceptance.py` | AC2: acceptance rules, confidence threshold (_MIN_CONFIDENCE=0.6), list_id validation |
| `routers/partial_trust_types.py` | Types: LLMDecisionCandidate, PartialTrustMeta |
| `routers/partial_trust_sampling.py` | Sampling: stable_sample by command_id |
| `routers/partial_trust_candidate.py` | Candidate generation with timeout/error handling |
| `routers/v2.py` (lines 206-452) | Pipeline integration: _maybe_apply_partial_trust, _log_partial_trust, error catch-all |
| `app/logging/partial_trust_risk_log.py` | Risk logging: append_partial_trust_risk_log, privacy comment |
| `tests/test_partial_trust_phase2.py` | Existing unit tests (5 tests) — reuse `_candidate()` helper |
| `tests/test_partial_trust_phase3.py` | Existing integration tests (4 tests) — reuse `_command()`, `_read_log()` helpers |
| `docs/adr/ADR-004-partial-trust-corridor.md` | ADR content for verification report |
| `docs/_indexes/adr-index.md` | ADR index for verification |

---

## Implementation Plan

### Step 1: Create edge case tests file

Create `tests/test_partial_trust_edge_cases.py` with these tests:

**Confidence boundary tests** (unit, uses `evaluate_candidate` from `routers.partial_trust_acceptance`):
- `test_confidence_059_rejected`: candidate with confidence=0.59 → `(False, "low_confidence", ...)`
- `test_confidence_060_accepted`: candidate with confidence=0.60 → `(True, "accepted", ...)`
- `test_confidence_none_accepted`: candidate with confidence=None → accepted (passthrough, existing behavior per `_passes_confidence` line 118-119)

**list_id validation tests** (unit, uses `evaluate_candidate`):
- `test_list_id_known_accepted`: candidate with list_id="list-1", context has shopping_lists=[{list_id: "list-1"}] → accepted
- `test_list_id_unknown_rejected`: candidate with list_id="unknown", context has shopping_lists=[{list_id: "list-1"}] → `(False, "list_id_unknown", ...)`
- `test_list_id_no_context_rejected`: candidate with list_id="list-1", context=None → `(False, "list_id_unknown", ...)`

**Error catch-all test** (integration, uses RouterV2Pipeline):
- `test_v2_partial_trust_error_catchall`: enable partial trust, sample_rate=1, monkeypatch `generate_llm_candidate_with_meta` to raise RuntimeError → decision is baseline start_job, risk-log entry has status="error", reason_code="RuntimeError"

**Privacy re-verification** (integration):
- `test_risk_log_privacy_all_paths`: trigger accepted_llm + fallback_deterministic + error paths, serialize all log entries to JSON, assert raw text ("молоко", "бананы", "Купи") absent from all entries

Test helpers: reuse `_candidate()` pattern from phase2, `_command()` and `_read_log()` from phase3.

### Step 2: Create verification report

Create `docs/planning/epics/EP-003/verification-report.md` following the pattern from EP-001 and EP-002 verification reports. Must map each initiative AC to code evidence:

**AC1: По умолчанию выключено**
- Evidence: `routers/partial_trust_config.py:13` — `PARTIAL_TRUST_ENABLED` defaults to "false"
- Test: `test_partial_trust_disabled_no_llm` (phase3)

**AC2: Работает только на allowlist intent**
- Evidence: `routers/partial_trust_config.py:9` — `ALLOWED_CORRIDOR_INTENTS = {"add_shopping_item"}`
- Evidence: `routers/v2.py:222` — corridor_intent check
- Evidence: `routers/partial_trust_acceptance.py:33-36` — corridor_mismatch check
- Tests: `test_acceptance_rejects_wrong_intent` (phase2), `test_partial_trust_rejected_candidate` (phase3)

**AC3: Deterministic fallback на любую ошибку**
- Evidence: `routers/v2.py:359-374` — catch-all Exception handler returns None (baseline)
- Evidence: `routers/partial_trust_candidate.py:76-77` — generate returns None on Exception
- Tests: `test_candidate_generation_timeout` (phase2), `test_v2_partial_trust_error_catchall` (new, edge cases)

**AC4: Risk-log и метрики**
- Evidence: `routers/v2.py:422-452` — `_log_partial_trust` logs structured data (no raw text)
- Evidence: `app/logging/partial_trust_risk_log.py:24` — privacy comment
- Tests: `test_acceptance_summary_no_raw_item_name` (phase2), `test_partial_trust_not_sampled_logs` (phase3), `test_partial_trust_accepts_candidate` privacy assertion (phase3), `test_risk_log_privacy_all_paths` (new, edge cases)

---

## Verification Commands

```bash
# 1. New edge case tests pass
python3 -m pytest tests/test_partial_trust_edge_cases.py -v
# Expected: 8+ passed (confidence x3, list_id x3, error_catchall, privacy)

# 2. Existing partial trust tests still pass
python3 -m pytest tests/test_partial_trust_phase2.py tests/test_partial_trust_phase3.py -v
# Expected: 9 passed (5 + 4)

# 3. Full test suite — no regressions
python3 -m pytest tests/ -v
# Expected: 109+ passed (109 existing + 8+ new)

# 4. Verification report exists
test -f docs/planning/epics/EP-003/verification-report.md && echo "OK" || echo "MISSING"

# 5. ADR-004 status
grep "Status" docs/adr/ADR-004-partial-trust-corridor.md
# Expected: "- Status: Accepted"

# 6. ADR index status
grep "ADR-004-P" docs/_indexes/adr-index.md
# Expected: "accepted"

# 7. Privacy: no raw text in test helpers
grep -n "молоко\|бананы" tests/test_partial_trust_edge_cases.py
# Expected: only in test input data, never in assertion of log output
```

---

## Tests

| Test file | Test count | Type |
|-----------|-----------|------|
| `tests/test_partial_trust_edge_cases.py` (new) | 8+ | Unit + Integration |
| `tests/test_partial_trust_phase2.py` (existing) | 5 | Unit |
| `tests/test_partial_trust_phase3.py` (existing) | 4 | Integration |

---

## DoD Checklist

- [ ] Verification report created with PASS for all 4 ACs
- [ ] ADR-004 status = Accepted (pre-sprint, verified in report)
- [ ] ADR index updated (pre-sprint, verified in report)
- [ ] Edge case tests for confidence boundary (0.59/0.60/None)
- [ ] Edge case tests for list_id (known/unknown/no context)
- [ ] Edge case test for v2 error catch-all
- [ ] Privacy re-verification across all risk-log paths
- [ ] All new tests pass
- [ ] Existing partial trust tests pass (9)
- [ ] Full test suite passes (109+)
- [ ] No changes to existing code files

---

## Risks

| Risk | Mitigation |
|------|------------|
| Confidence boundary test reveals off-by-one (>= vs >) | Code uses `>=` at line 120: `candidate.confidence >= _MIN_CONFIDENCE`. 0.60 should pass. If not, fix is 1 char. |
| list_id validation test reveals context structure mismatch | Context structure matches `_command()` in phase3: `household.shopping_lists[].list_id`. Verified. |
| Error catch-all test reveals uncaught exception path | v2.py has `except Exception` at line 359 — should catch everything. |

## Rollback

Delete `tests/test_partial_trust_edge_cases.py` and `docs/planning/epics/EP-003/verification-report.md`. No existing files are modified.
