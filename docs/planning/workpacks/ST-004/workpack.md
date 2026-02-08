# WP / ST-004: Retroactive verification of assist-mode initiative ACs

**Status:** Ready
**Story:** `docs/planning/epics/EP-002/stories/ST-004-retroactive-verification.md`
**Owner:** Codex (implementation) / Claude (prompts + review)

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q1-assist-mode.md` |
| Epic | `docs/planning/epics/EP-002/epic.md` |
| Story | `docs/planning/epics/EP-002/stories/ST-004-retroactive-verification.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

Produce a formal verification report mapping each assist-mode initiative AC (AC1-AC4) to concrete code evidence, enabling the initiative status transition from "Proposed" to "Done".

## Acceptance Criteria

1. **AC-1**: File `docs/planning/epics/EP-002/verification-report.md` exists with AC1-AC4 mapping.
2. **AC-2**: AC1 row references feature flags, defaults, `test_assist_disabled_no_impact`.
3. **AC-3**: AC2 row references acceptance rules document (ST-003), key functions, tests.
4. **AC-4**: AC3 row references timeout mechanism, `test_assist_timeout_fallback`, `test_agent_hints_timeout_fallback`.
5. **AC-5**: AC4 row references `_log_step`, `test_assist_log_no_raw_text`, `test_agent_hints_privacy_in_logs`.
6. **AC-6**: Initiative status updated to Done.

## Files to Change

### New files (create)

| File | Description |
|------|-------------|
| `docs/planning/epics/EP-002/verification-report.md` | Verification report mapping AC1-AC4 to evidence |

### Modified files

| File | Change |
|------|--------|
| `docs/planning/initiatives/INIT-2026Q1-assist-mode.md` | Update status from "Proposed" to "Done" |

## Implementation Plan

### Step 1: Create verification report

**Commit:** `docs(assist-mode): add AC1-AC4 verification report`

Structure mirrors ST-002 verification report: summary table + per-AC sections with evidence.

### Step 2: Update initiative status

**Commit:** same as step 1

Change status to "Done".

## Verification Commands

```bash
# 1. Report exists
test -f docs/planning/epics/EP-002/verification-report.md && echo "OK" || echo "MISSING"

# 2. Assist-mode tests pass
python3 -m pytest tests/test_assist_mode.py tests/test_assist_agent_hints.py -v

# 3. Initiative status updated
grep "Статус" docs/planning/initiatives/INIT-2026Q1-assist-mode.md

# 4. Full suite
python3 -m pytest tests/ -v
```

## DoD Checklist

- [ ] Verification report with per-AC evidence
- [ ] All referenced file paths exist
- [ ] All referenced tests pass
- [ ] Initiative status updated
- [ ] No code changes

## Risks

| Risk | P | I | Mitigation |
|------|---|---|------------|
| Line numbers shift | Low | Low | Function names are primary reference |

## Rollback

1 new file + 1 status update. Rollback = revert. No code changes.

## APPLY Boundaries

### Allowed
- `docs/planning/epics/EP-002/verification-report.md` (create)
- `docs/planning/initiatives/INIT-2026Q1-assist-mode.md` (modify status only)

### Forbidden
- Any code files
