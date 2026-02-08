# Checklist / ST-002: Retroactive verification of shadow-router AC1-AC3

**Story:** `docs/planning/epics/EP-001/stories/ST-002-retroactive-verification.md`
**DoD:** `docs/_governance/dod.md`

---

## Acceptance Criteria Verification

- [ ] **AC-1: Verification report exists**
  - File: `docs/planning/epics/EP-001/verification-report.md`
  - Expected: contains AC1-AC3 mapping table with status + evidence

- [ ] **AC-2: AC1 evidence — shadow off by default**
  - Report references: `SHADOW_ROUTER_ENABLED`, default=false, `test_shadow_router_no_impact`

- [ ] **AC-3: AC2 evidence — error/timeout no impact**
  - Report references: `test_shadow_router_no_impact`, `test_shadow_router_timeout_no_impact`, error handling code

- [ ] **AC-4: AC3 evidence — no raw text in logs**
  - Report references: `_summarize_entities`, `test_shadow_router_logging_shape`, `shadow_router_log.py`

- [ ] **AC-5: Initiative status updated**
  - File: `docs/planning/initiatives/INIT-2026Q1-shadow-router.md`
  - Expected: status changed from "Proposed"

- [ ] **AC-6: Verification commands documented**
  - Report includes runnable commands with expected outcomes

---

## DoD Verification

### Documentation

- [ ] Verification report created
- [ ] All referenced file paths exist
- [ ] All referenced tests pass: `python3 -m pytest tests/test_shadow_router.py -v`
- [ ] Initiative status updated
- [ ] No code changes made

---

## Verification Commands

```bash
# 1. Report exists
test -f docs/planning/epics/EP-001/verification-report.md && echo "OK" || echo "MISSING"

# 2. Shadow router tests pass
python3 -m pytest tests/test_shadow_router.py -v

# 3. Initiative status updated
grep -i "статус" docs/planning/initiatives/INIT-2026Q1-shadow-router.md

# 4. ST-001 deliverables exist (AC4 evidence)
test -f scripts/analyze_shadow_router.py && echo "OK" || echo "MISSING"
```

---

## Sign-off

- [ ] All AC verified
- [ ] All DoD criteria met
- [ ] Reviewer GO decision
