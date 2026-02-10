# Sprint S05: SemVer CI Governance and Agent Registry Integration

**PI:** standalone (aligns with 2026Q3 LATER phase)
**Period:** 2026-02-10 -- 2026-02-17 (5 calendar days, ~5 working days of Codex effort)
**Status:** Complete

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |
| EP-006 epic | `docs/planning/epics/EP-006/epic.md` |
| EP-007 epic | `docs/planning/epics/EP-007/epic.md` |
| Initiative (semver-and-ci) | `docs/planning/initiatives/INIT-2026Q3-semver-and-ci.md` |
| Initiative (agent-registry) | `docs/planning/initiatives/INIT-2026Q3-agent-registry-integration.md` |
| ADR-001 (contract versioning) | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| ADR-005 (agent contract v0) | `docs/adr/ADR-005-internal-agent-contract-v0.md` |
| S04 retro (action items) | `docs/planning/sprints/S04/retro.md` |

---

## Sprint Goal

Complete CI contract governance (decision_log_audit in CI, real schema breaking-change detection, developer runbook) and integrate the agent registry into the core pipeline (ADR-005 update, capabilities lookup service, flag-gated registry gate) -- closing two LATER-phase initiatives (INIT-2026Q3-semver-and-ci and INIT-2026Q3-agent-registry-integration).

---

## Committed Scope

| Story ID | Title | Epic | Type | Estimate | Owner | Dep | Notes |
|----------|-------|------|------|----------|-------|-----|-------|
| ST-015 | CI completeness: add decision_log_audit and use release_sanity orchestrator | EP-006 | Code | 1 day | Codex | None | Foundation: consolidate CI steps. 2 new tests. |
| ST-016 | Real schema breaking-change detection for contract schemas | EP-006 | Code | 1 day | Codex | ST-015 | Baseline approach. 8 new tests. |
| ST-017 | Contract governance operational policy and PR workflow guide | EP-006 | Docs | 2h | Claude/Codex | None | Runbook document, no code changes. |
| ST-018 | ADR-005 update and integration diagram | EP-007 | Docs | 2h | Claude/Codex | None | ADR addendum + PlantUML diagram. adr_needed=yes, diagrams_needed=yes. |
| ST-019 | Capabilities lookup service for agent registry | EP-007 | Code | 1 day | Codex | ST-018 | New module. 10 new tests. |
| ST-020 | Core pipeline registry-aware gate (flag-gated) | EP-007 | Code | 1 day | Codex | ST-018, ST-019 | Read-only probe in core_graph. 10 new tests. |

**Total estimated effort:** 4 working days of Codex code implementation + ~4h of docs work.

Story specs:
- `docs/planning/epics/EP-006/stories/ST-015-ci-completeness-decision-log-audit.md`
- `docs/planning/epics/EP-006/stories/ST-016-real-schema-breaking-change-detection.md`
- `docs/planning/epics/EP-006/stories/ST-017-contract-governance-policy-doc.md`
- `docs/planning/epics/EP-007/stories/ST-018-adr-005-update-integration-scope.md`
- `docs/planning/epics/EP-007/stories/ST-019-capabilities-lookup-service.md`
- `docs/planning/epics/EP-007/stories/ST-020-core-graph-registry-gate.md`

### DoR Readiness Assessment

| Story | DoR Status | Notes |
|-------|------------|-------|
| ST-015 | Ready | No blockers. All scripts exist. 5 ACs testable. Test strategy: 2 unit tests. |
| ST-016 | Ready (managed dep) | Blocked by ST-015 (CI must be green). 8 ACs testable, 8 unit tests. |
| ST-017 | Ready | No blockers. Docs-only. 5 ACs. ADR-001 provides content basis. |
| ST-018 | Ready | No blockers. Docs-only. 5 ACs. adr_needed=yes, diagrams_needed=yes (deliverables, not prerequisites). |
| ST-019 | Ready (managed dep) | Soft dep on ST-018 (arch documented). 7 ACs, 10 unit tests. |
| ST-020 | Ready (managed dep) | Depends on ST-018 + ST-019. 7 ACs, 9 unit + 1 integration test. |

All 6 stories pass DoR. No discovery stories needed.

---

## Stretch

| Story ID | Title | Condition |
|----------|-------|-----------|
| (none) | -- | All 6 committed stories fill sprint capacity (slightly above normal 3-4 story sprint). If stories complete early, use time for review quality, retro, and INIT-2026Q3-codex-integration candidate analysis. |

---

## Out of Scope (explicit)

- **Codex pipeline integration** (INIT-2026Q3-codex-integration) -- separate initiative, next sprint candidate.
- **Git-diff-based schema detection** -- ST-016 uses baseline-copy approach, not git diff.
- **Nested/deep property comparison** -- ST-016 is top-level only (MVP).
- **Automated baseline update on version bump** -- manual for now.
- **Modifying existing shadow invoker or assist hints** -- ST-019 creates new service, does not refactor consumers.
- **Invoking registry agents from core pipeline** -- ST-020 is read-only probe (annotation only).
- **Changes to DecisionDTO or CommandDTO schemas** -- stable boundary.
- **Enabling agents by default** -- `AGENT_REGISTRY_CORE_ENABLED` defaults to false.
- **PR template automation or GitHub bot integration** -- not in scope.
- **Changes to ADR-001** -- already Accepted, referenced but not modified.
- **CHANGELOG.md** -- deferred.
- **CI for non-contract changes** (linting, code quality) -- not in scope.

---

## Capacity Notes

- **Pipeline model:** Claude generates workpacks and prompts, Human gates, Codex implements. Same proven model as S01 (4/4), S02 (3/3), S03 (3/3), S04 (3/3).
- **Sprint history:** 13 stories across 4 sprints, zero carry-overs, zero scope changes.
- **Codex throughput assumption:** ~1 code story per day (S01-S04 actuals). Docs stories ~2h each.
- **This sprint:** 4 code stories + 2 docs stories = slightly above normal but:
  - 2 docs stories are low-risk, low-effort (~2h each)
  - Two parallel tracks (EP-006 and EP-007) with no code overlap
  - Pipeline maturity supports higher throughput
- **Buffer:** ~20% implicit (5 calendar days for ~5 days estimated effort, plus docs stories are sub-day).
- **Bottleneck risk:** Human gate turnaround. Each code story requires 3 gate interactions. Docs stories require 1 gate each. Total: ~14 gate interactions.
- **Parallelism opportunity:** EP-006 Track 1 (ST-015 -> ST-016) and EP-007 Track 2 (ST-018 -> ST-019 -> ST-020) are independent. ST-017 is independent of everything.
- **S04 retro action items applied:**
  - Check what globbers/validators consume files when adding data to fixture/schema directories.
  - Add to workpack risk: "Does this file format change break schema validation (additionalProperties)?"
  - Consider two-file pattern (data + metadata) for test annotations.
- **Test suite baseline:** 202 tests passing. Expected growth: ~30 new tests across 4 code stories (target: ~232 tests).

---

## Dependencies

| Dependency | Type | Impact | Status |
|------------|------|--------|--------|
| ADR-001 (contract versioning policy) | Internal | ST-015, ST-016, ST-017 reference it. | Accepted |
| ADR-005 (agent contract v0) | Internal | ST-018 updates it. ST-019, ST-020 depend on update. | Accepted, update planned |
| Existing skill scripts (release_sanity, schema_bump, etc.) | Internal | ST-015, ST-016 modify/extend. | Done |
| Agent registry v0 infrastructure | Internal | ST-019, ST-020 build on it. | Done |
| `contracts/schemas/*.json` | Contract | ST-016 creates baseline copies. | Stable (v2.0.0) |
| Existing test suite (202 tests) | Internal | All changes must preserve. | Passing |
| Human gate availability | Process | ~14 gate interactions across 6 stories. | Accepted |
| EP-006 and EP-007 no code overlap | Internal | Parallel execution safe. | Verified (no shared files) |

**No external dependencies.** All work is self-contained within the repo.

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation | ROAM |
|------|-------------|--------|------------|------|
| Sprint scope is above normal (6 stories vs usual 3-4) | Medium | Medium | 2 of 6 are docs-only (~2h each). Two independent tracks allow parallel execution. 20% buffer. | Owned |
| CI workflow changes in ST-015 break existing CI | Low | Medium | Local verification matches CI env. All 202 tests must pass. Rollback: revert ci.yml. | Mitigated |
| Real schema breaking-change detection produces false positives (ST-016) | Low | Medium | Tests include known-non-breaking cases. Backward-compatible CLI flags preserved. | Mitigated |
| Capabilities lookup introduces import cycles with agent_registry (ST-019) | Low | Low | New module, no modifications to existing code. Clean dependency direction. | Mitigated |
| Registry gate adds latency to core pipeline (ST-020) | Low | Medium | Flag-gated (default off). In-memory cached registry. Gate is read-only annotation. | Mitigated |
| ADR-005 update scope disagreement (ST-018) | Low | Low | Additive update only. Human gate for ADR. | Accepted |
| Two-epic sprint creates merge conflicts | Very Low | Low | No overlapping files between EP-006 and EP-007. | Accepted |
| Codex cannot run pytest in sandbox (carry-forward) | -- | Low | Accepted permanent limitation. Verification during Claude review. | Accepted |
| Adding files to fixture/schema dirs breaks globbers (S04 retro lesson) | Low | Medium | Workpack risk analysis will check globber patterns before placing new files. | Mitigated |

---

## Execution Order (recommended)

This sprint has two independent tracks plus two independent docs stories. Recommended order optimizes for critical-path and parallelism.

**Track 1 -- EP-006 (Contract Governance):**

1. **ST-015** -- CI completeness (foundation, no deps).
   Workpack -> prompt-plan -> Codex PLAN -> prompt-apply -> Codex APPLY -> review -> merge.

2. **ST-016** -- Real schema breaking-change detection (dep: ST-015 merged).
   Workpack -> prompt-plan -> Codex PLAN -> prompt-apply -> Codex APPLY -> review -> merge.

**Track 2 -- EP-007 (Agent Registry Integration):**

3. **ST-018** -- ADR-005 update + integration diagram (foundation, docs-only, no deps).
   Workpack -> prompt-plan -> Codex PLAN -> prompt-apply -> Codex APPLY -> review -> merge.
   **Human Gate (ADR):** ADR-005 addendum requires approval before ST-019/ST-020 proceed.

4. **ST-019** -- Capabilities lookup service (dep: ST-018 merged + approved).
   Workpack -> prompt-plan -> Codex PLAN -> prompt-apply -> Codex APPLY -> review -> merge.

5. **ST-020** -- Core pipeline registry gate (dep: ST-018 + ST-019 merged).
   Workpack -> prompt-plan -> Codex PLAN -> prompt-apply -> Codex APPLY -> review -> merge.

**Independent (parallel with either track):**

6. **ST-017** -- Contract governance runbook (docs-only, no deps, can run any time).
   Workpack -> prompt-plan -> Codex PLAN -> prompt-apply -> Codex APPLY -> review -> merge.

**Parallelism notes:**
- Track 1 and Track 2 can proceed in parallel (no shared files).
- ST-017 can be done at any point during the sprint.
- ST-018 should start early since ST-019 and ST-020 depend on it.
- Optimal startup: Begin ST-015 (Track 1), ST-018 (Track 2), and ST-017 concurrently.

```
Day 1:  ST-015 (code)  |  ST-018 (docs)  |  ST-017 (docs)
Day 2:  ST-016 (code)  |  ST-019 (code)  |
Day 3:  (buffer)       |  ST-020 (code)  |
Day 4:  (buffer/retro) |  (buffer)       |
```

---

## Demo Plan

At sprint end, the following should be demonstrable:

### EP-006: Contract Governance
1. **CI completeness** -- Show ci.yml using release_sanity.py orchestrator with decision_log_audit included. Show test confirming all 3 sub-checks invoked.
2. **Schema breaking-change detection** -- Run `check_breaking_changes.py` against baseline schemas. Show detection of: field deletion, type change, new required field. Show non-breaking addition passes.
3. **Baseline directory** -- Show `contracts/schemas/.baseline/` with copies matching current schemas.
4. **Governance runbook** -- Show `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` with step-by-step non-breaking and breaking workflows, CI check explanations, and PR checklist.

### EP-007: Agent Registry Integration
5. **ADR-005 update** -- Show updated ADR with Integration Status, Phase 1, and Feature Flag sections. Show new PlantUML diagram.
6. **Capabilities lookup** -- Demonstrate `CapabilitiesLookup.find_agents()` with test registry: matching, filtered, empty results.
7. **Registry gate** -- Show core pipeline processing command with `AGENT_REGISTRY_CORE_ENABLED=true`: decision unchanged, `registry_snapshot` in log. Show flag off: no annotation. Show graceful failure with missing YAML.

### Cross-cutting
8. **Test suite growth** -- All tests passing (target: ~232 tests, up from 202).
9. **Zero behavior regression** -- Demonstrate that all existing pipeline behavior is unchanged. Feature flags default off.

**Initiative closure signal:** After all 6 stories pass review:
- INIT-2026Q3-semver-and-ci can be marked Done.
- INIT-2026Q3-agent-registry-integration can be marked Done.
- This leaves INIT-2026Q3-codex-integration as the sole remaining LATER-phase initiative.

---

## Gate Ask (Gate B)

**Requesting PO approval for:**

1. **Sprint Goal:** Complete CI contract governance and agent registry core pipeline integration -- closing two LATER-phase initiatives (INIT-2026Q3-semver-and-ci and INIT-2026Q3-agent-registry-integration).
2. **Committed scope:** 6 stories (ST-015 through ST-020) across 2 epics (EP-006, EP-007). All 6 pass DoR.
3. **Out-of-scope list:** As documented above -- no codex-integration initiative, no git-diff detection, no nested schema comparison, no agent invocation from core, no contract schema changes.
4. **Risk posture:** All risks Low-Medium. Highest concern is sprint size (6 stories vs usual 3-4), mitigated by 2 docs-only stories, two parallel tracks, and 20% buffer. Carry-forward risk from S04 retro addressed in workpack process.
5. **Execution model:** Same pipeline as S01-S04 (13/13 stories, 0 carry-overs). Two-track parallelism is new but safe (no shared code files).
6. **Significance:** Closing these two initiatives leaves only INIT-2026Q3-codex-integration in the LATER phase. S05 represents the penultimate delivery sprint before full initiative closure.

**Decision requested:** Approve sprint goal and committed scope to proceed with workpack generation for ST-015 (Track 1) and ST-018 (Track 2) in parallel.
