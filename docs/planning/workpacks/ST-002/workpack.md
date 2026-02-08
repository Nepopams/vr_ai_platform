# WP / ST-002: Retroactive verification of shadow-router AC1-AC3

**Status:** Ready
**Story:** `docs/planning/epics/EP-001/stories/ST-002-retroactive-verification.md`
**Owner:** Codex (implementation) / Claude (prompts + review)

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q1-shadow-router.md` |
| Epic | `docs/planning/epics/EP-001/epic.md` |
| Story | `docs/planning/epics/EP-001/stories/ST-002-retroactive-verification.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

Produce a formal verification report mapping each initiative AC (AC1, AC2, AC3) to concrete code evidence (file paths, line numbers, test names, config defaults), enabling the initiative status transition from "Proposed" to "Verified (pending AC4)". AC4 is already closed by ST-001.

## Acceptance Criteria

1. **AC-1**: File `docs/planning/epics/EP-001/verification-report.md` exists with a table mapping each initiative AC to status + evidence.
2. **AC-2**: AC1 row references `SHADOW_ROUTER_ENABLED`, config default=false, test `test_shadow_router_no_impact`.
3. **AC-3**: AC2 row references `test_shadow_router_no_impact`, `test_shadow_router_timeout_no_impact`, error handling in `shadow_router.py`.
4. **AC-4**: AC3 row references `_summarize_entities`, `test_shadow_router_logging_shape`, `shadow_router_log.py`.
5. **AC-5**: Initiative status updated to "Verified (pending AC4)" in `docs/planning/initiatives/INIT-2026Q1-shadow-router.md`.
6. **AC-6**: Report includes runnable verification commands with expected outcomes.

## Files to Change

### New files (create)

| File | Description |
|------|-------------|
| `docs/planning/epics/EP-001/verification-report.md` | Verification report mapping AC1-AC3 to evidence |

### Modified files

| File | Change |
|------|--------|
| `docs/planning/initiatives/INIT-2026Q1-shadow-router.md` | Update status from "Proposed" to "Verified (pending AC4)" |

## Implementation Plan

### Step 1: Create verification report

**Commit:** `docs(shadow-router): add AC1-AC3 verification report`

Create `docs/planning/epics/EP-001/verification-report.md` with the following structure:

**Header:**
- Title, date, initiative reference, reviewer

**Summary table:**

| Initiative AC | Description | Status | Evidence |
|--------------|-------------|--------|----------|
| AC1 | Shadow режим выключен по умолчанию и включается флагом | Pass/Fail | refs |
| AC2 | При ошибке/таймауте LLM baseline работает как раньше | Pass/Fail | refs |
| AC3 | JSONL-лог не содержит raw user text и raw LLM output | Pass/Fail | refs |
| AC4 | Воспроизводимый скрипт анализа golden-dataset | Pass (ST-001) | refs |

**Per-AC sections (AC1, AC2, AC3):**
Each section contains:
- What was checked
- Code references (file:line, function names)
- Test references (test name, what it asserts)
- Config references (env var, default value)

**AC1 evidence to gather:**
- `routers/shadow_router.py` — `SHADOW_ROUTER_ENABLED` env var, default value
- `routers/v2.py` — where shadow router is called conditionally
- `tests/test_shadow_router.py::test_shadow_router_no_impact` — decision unchanged
- `tests/test_shadow_router.py::test_shadow_router_policy_disabled` — disabled by default

**AC2 evidence to gather:**
- `routers/shadow_router.py` — try/except, ThreadPoolExecutor timeout
- `tests/test_shadow_router.py::test_shadow_router_no_impact` — baseline decision identical
- `tests/test_shadow_router.py::test_shadow_router_timeout_no_impact` — timeout logged, no impact

**AC3 evidence to gather:**
- `app/logging/shadow_router_log.py` — `append_shadow_router_log()` field list, no raw text fields
- `routers/shadow_router.py` — `_summarize_entities()` returns keys/counts only
- `tests/test_shadow_router.py::test_shadow_router_logging_shape` — verifies log structure

**AC4 evidence:**
- `scripts/analyze_shadow_router.py` — exists (ST-001)
- `scripts/README-shadow-analyzer.md` — exists (ST-001)
- `skills/graph-sanity/fixtures/golden_dataset.json` — 14 entries (ST-001)
- `tests/test_analyze_shadow_router.py` — 10 tests passing (ST-001)

**Verification commands section:**
Runnable commands to re-verify each AC with expected outputs.

**Recommendation section:**
GO/NO-GO for initiative status update.

### Step 2: Update initiative status

**Commit:** `docs(shadow-router): update initiative status to Verified`

In `docs/planning/initiatives/INIT-2026Q1-shadow-router.md`:
- Change `**Статус:** Proposed` to `**Статус:** Verified (pending AC4 closure)`

Note: AC4 is already closed by ST-001, so the final status should be `Done` if the report confirms all ACs pass. The PLAN phase will determine the correct final status.

## Verification Commands

```bash
# 1. Confirm verification report exists
test -f docs/planning/epics/EP-001/verification-report.md && echo "OK" || echo "MISSING"

# 2. Confirm all referenced tests pass
python3 -m pytest tests/test_shadow_router.py -v

# 3. Confirm initiative status updated
grep -i "статус" docs/planning/initiatives/INIT-2026Q1-shadow-router.md

# 4. Confirm AC4 evidence (ST-001 deliverables exist)
test -f scripts/analyze_shadow_router.py && test -f scripts/README-shadow-analyzer.md && test -f skills/graph-sanity/fixtures/golden_dataset.json && echo "OK" || echo "MISSING"
```

## DoD Checklist

- [ ] Verification report created with per-AC evidence
- [ ] All referenced file paths exist in the repo
- [ ] All referenced tests pass
- [ ] Verification commands documented in report
- [ ] Initiative status updated
- [ ] No code changes (docs-only story)

## Risks

| Risk | P | I | Mitigation |
|------|---|---|------------|
| Referenced line numbers shift after refactoring | Low | Low | Reference function names + line numbers; function names are stable |
| AC evidence insufficient for governance audit | Low | Med | Include test names, config defaults, and runnable commands |

## Rollback

All changes additive (1 new file, 1 status update). Rollback = revert file + status. No code/config/DB changes.

## APPLY Boundaries

### Allowed
- `docs/planning/epics/EP-001/verification-report.md` (create)
- `docs/planning/initiatives/INIT-2026Q1-shadow-router.md` (modify status only)

### Forbidden
- `routers/**` (do not modify)
- `app/**` (do not modify)
- `tests/**` (do not modify)
- `scripts/**` (do not modify)
- Any code files (this is a docs-only story)
