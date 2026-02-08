# Sprint S01 -- Scope Details

## Sources of Truth

| Artifact | Path |
|----------|------|
| Sprint plan | `docs/planning/sprints/S01/sprint.md` |
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| DoR | `docs/_governance/dor.md` |

---

## In Scope -- Committed Stories

### ST-001: Golden-dataset analyzer script + ground truth manifest + README

**Epic:** EP-001 (Shadow Router Gap Closure)
**Type:** Code + tests
**DoR Status:** READY

| Deliverable | Path | Type |
|-------------|------|------|
| Golden dataset manifest | `skills/graph-sanity/fixtures/golden_dataset.json` | JSON data file |
| Analyzer script | `scripts/analyze_shadow_router.py` | Python script |
| README | `scripts/README-shadow-analyzer.md` | Documentation |
| Unit tests | `tests/test_analyze_shadow_router.py` | Test file |

**Readiness notes:**
- 14 existing fixture commands in `skills/graph-sanity/fixtures/commands/` provide the base data.
- Ground truth labels (expected_intent, expected_entity_keys) must be authored for each fixture.
- JSONL log format is defined by the existing shadow router code (inspect in PLAN phase).
- All 7 acceptance criteria are testable and well-specified.
- No flags triggered (no contract/ADR/diagram impact).

---

### ST-002: Retroactive verification of shadow-router AC1-AC3

**Epic:** EP-001 (Shadow Router Gap Closure)
**Type:** Documentation only
**DoR Status:** READY

| Deliverable | Path | Type |
|-------------|------|------|
| Verification report | `docs/planning/epics/EP-001/verification-report.md` | Governance doc |
| Initiative status update | `docs/planning/initiatives/INIT-2026Q1-shadow-router.md` | Status change |

**Readiness notes:**
- All referenced tests exist: `tests/test_shadow_router.py` (4 tests).
- All referenced code files exist: `shadow_router.py`, `shadow_router_log.py`, config files.
- Verification is read-only -- map existing evidence to AC descriptions.
- No code changes. No new tests.

---

### ST-003: Document acceptance rules for assist-mode hints

**Epic:** EP-002 (Assist-Mode Gap Closure)
**Type:** Documentation only
**DoR Status:** READY

| Deliverable | Path | Type |
|-------------|------|------|
| Acceptance rules document | `docs/contracts/assist-mode-acceptance-rules.md` | Contract-adjacent doc |

**Readiness notes:**
- Rules are fully implemented in code (functions: `_can_accept_normalized_text`, `_pick_matching_item`, `_clarify_question_is_safe`, `_clarify_question`).
- Document maps code behavior to human-readable rules. No interpretation needed, just accurate extraction.
- Placed in `docs/contracts/` because it describes behavioral contracts of the assist-mode subsystem.
- No code changes.

---

### ST-004: Retroactive verification of assist-mode initiative ACs

**Epic:** EP-002 (Assist-Mode Gap Closure)
**Type:** Documentation only
**DoR Status:** READY (blocked by ST-003 completion)

| Deliverable | Path | Type |
|-------------|------|------|
| Verification report | `docs/planning/epics/EP-002/verification-report.md` | Governance doc |
| Initiative status update | `docs/planning/initiatives/INIT-2026Q1-assist-mode.md` | Status change |

**Readiness notes:**
- AC2 references `docs/contracts/assist-mode-acceptance-rules.md` which is produced by ST-003. Must sequence ST-003 before ST-004.
- All referenced tests exist: `tests/test_assist_mode.py`, `tests/test_assist_agent_hints.py`.
- All referenced code files exist: `routers/assist/config.py`, assist mode functions.
- Verification is read-only -- map existing evidence to AC descriptions.

---

## Out of Scope (explicit)

| Item | Reason |
|------|--------|
| Shadow router code changes | Sprint is measurement/documentation, not behavior change |
| Assist-mode code changes | Same as above |
| New tests for existing code | Verification stories use existing test suite |
| CI pipeline integration for analyzer | LATER phase (INIT-2026Q3-semver-and-ci) |
| Metrics dashboard/visualization | Not in MVP scope |
| Partial Trust implementation | NEXT phase (2026Q2) |
| Multi-entity extraction | NEXT phase (2026Q2) |
| Improved clarify | NEXT phase (2026Q2) |
| Baseline comparison in analyzer | Potential future enhancement |
| Integration with metrics_agent_hints_v0.py | Explicitly excluded in ST-001 |

---

## DoR Readiness Summary

| Story | Fields | AC | Test Strategy | Flags | Blockers | Verdict |
|-------|--------|----|---------------|-------|----------|---------|
| ST-001 | Complete | 7 ACs, testable | Unit + integration defined | None | None | READY |
| ST-002 | Complete | 6 ACs, testable | Verification commands | None | None | READY |
| ST-003 | Complete | 4 scenarios, testable | Manual review + checklist | None | None | READY |
| ST-004 | Complete | 5 scenarios, testable | Test run + checklist | None | ST-003 | READY (sequenced) |

All 4 stories pass DoR. No discovery stories needed.
