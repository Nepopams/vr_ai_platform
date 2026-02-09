# Sprint S05 -- Demo Plan

**Sprint:** S05 (SemVer CI Governance + Agent Registry Integration)
**Status:** Planning

---

## Demo Outline

### 1. EP-006: Contract Governance (3 stories)

**ST-015 -- CI Completeness**
- Show updated `.github/workflows/ci.yml` using `release_sanity.py`
- Show that decision_log_audit is now included in CI pipeline
- Run `test_release_sanity_runs` -- passes and confirms all 3 sub-checks invoked

**ST-016 -- Real Schema Breaking-Change Detection**
- Show `contracts/schemas/.baseline/` directory with copies of current schemas
- Demo breaking-change detection:
  - Field deletion: detected
  - Type change: detected
  - New required field: detected
  - Optional field addition: NOT flagged (correct)
- Show backward compatibility: `--old`/`--new` CLI flags still work

**ST-017 -- Contract Governance Runbook**
- Walk through `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md`
- Show: breaking vs non-breaking classification
- Show: step-by-step non-breaking and breaking workflows
- Show: CI checks explained with script paths
- Show: PR checklist (copyable)

### 2. EP-007: Agent Registry Integration (3 stories)

**ST-018 -- ADR-005 Update + Diagram**
- Show updated ADR-005 with: Integration Status, Phase 1 plan, Feature Flag Requirements
- Show rendered PlantUML diagram (`docs/diagrams/agent-registry-integration.puml`)
- Show updated indexes (adr-index.md, diagrams-index.md)

**ST-019 -- Capabilities Lookup Service**
- Demo `CapabilitiesLookup.find_agents(intent, mode)`:
  - Matching agent: returns agent spec
  - Disabled agent: filtered out
  - Intent mismatch: empty list
- Demo `has_capability()` and `list_capabilities()`
- Show: all 10 new tests passing

**ST-020 -- Core Pipeline Registry Gate**
- Demo with `AGENT_REGISTRY_CORE_ENABLED=true`:
  - Process command -> DecisionDTO unchanged
  - Log contains `registry_snapshot` with intent, available_agents, any_enabled
- Demo with flag off: no annotation, no overhead
- Demo graceful failure: missing/malformed YAML -> decision normal, error logged
- Show: no raw user text in registry log entries

### 3. Cross-Cutting

**Test Suite**
- All tests passing (target: ~232, baseline: 202)
- Zero regressions

**Zero Behavior Change**
- All feature flags default off
- Existing pipeline behavior identical to pre-S05

---

## Success Criteria

| Criterion | Measure |
|-----------|---------|
| All 6 stories pass review | GO from Claude review gate |
| Tests pass | All ~232 tests green |
| No behavior regression | Existing golden dataset fixtures produce same results |
| CI governance complete | decision_log_audit + real schema check + runbook |
| Agent registry integrated | Lookup service + core gate + ADR + diagram |
| Initiatives closeable | INIT-2026Q3-semver-and-ci + INIT-2026Q3-agent-registry-integration |

---

## Initiative Closure Signal

After demo, if all 6 stories are merged and pass DoD:
- Mark INIT-2026Q3-semver-and-ci as **Done**
- Mark INIT-2026Q3-agent-registry-integration as **Done**
- Remaining LATER phase: INIT-2026Q3-codex-integration only
