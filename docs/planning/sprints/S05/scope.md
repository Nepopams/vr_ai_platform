# Sprint S05 -- Scope Detail

**Sprint:** S05 (SemVer CI Governance + Agent Registry Integration)
**Status:** Planning

---

## Committed (In Scope)

### Track 1 -- EP-006: SemVer and CI Contract Governance

| Story | Title | Type | Ready | Notes |
|-------|-------|------|-------|-------|
| ST-015 | CI completeness: decision_log_audit + release_sanity orchestrator | Code | Yes | Foundation. Replaces individual CI steps with orchestrator. ~2 new tests. |
| ST-016 | Real schema breaking-change detection | Code | Yes (dep: ST-015) | Baseline-copy approach. Detects field deletion, type change, new required field. ~8 new tests. |
| ST-017 | Contract governance runbook | Docs | Yes | Operational policy doc. No code changes. No new tests. |

### Track 2 -- EP-007: Agent Registry Integration

| Story | Title | Type | Ready | Notes |
|-------|-------|------|-------|-------|
| ST-018 | ADR-005 update + integration diagram | Docs | Yes | Additive update to ADR. New PlantUML diagram. No code. adr_needed=yes, diagrams_needed=yes. |
| ST-019 | Capabilities lookup service | Code | Yes (dep: ST-018) | New module `agent_registry/capabilities_lookup.py`. ~10 new tests. |
| ST-020 | Core pipeline registry gate (flag-gated) | Code | Yes (dep: ST-018, ST-019) | Read-only probe in core_graph. Flag default: off. ~10 new tests. |

---

## Stretch

None. All 6 committed stories fill sprint capacity.

---

## Out of Scope

| Item | Reason |
|------|--------|
| INIT-2026Q3-codex-integration | Separate initiative, candidate for S06. |
| Git-diff-based schema detection | Deferred -- baseline-copy is simpler for MVP. |
| Nested/deep property comparison in schema check | Top-level only for now. |
| Automated baseline update on version bump | Manual process, documented in runbook. |
| Refactoring shadow invoker / assist hints to use new lookup service | Future refactor. ST-019 is additive. |
| Agent invocation from core pipeline | ST-020 is read-only annotation only. |
| DecisionDTO / CommandDTO schema changes | Stable boundary. |
| Enabling agents by default in production | Feature flag defaults to false. |
| PR template automation / GitHub bot | Not in scope. |
| CHANGELOG.md | Deferred. |
| CI for non-contract changes (linting, code quality) | Not in scope. |

---

## Readiness Notes

### All stories pass DoR

- Titles: Clear, user-centric -- Yes (all 6)
- Descriptions: Context, user value, expected behavior -- Yes (all 6)
- Acceptance Criteria: Testable Given/When/Then -- Yes (all 6)
- Related ADR: ST-018 (adr_needed=yes) -- ADR-005 update IS the deliverable
- Related Contracts: No contract_impact for any story
- Test strategy: Identified for all code stories (ST-015: 2, ST-016: 8, ST-019: 10, ST-020: 10)
- Flags checked: All stories reviewed

### Managed dependencies

- ST-016 depends on ST-015 (CI green before schema_bump changes)
- ST-019 depends on ST-018 (architecture documented before implementation)
- ST-020 depends on ST-018 + ST-019 (both architecture and lookup service required)
- No circular dependencies. Dependency graph is a clean DAG.

### S04 retro action items addressed

- Globber/validator check: Will be included in ST-015 and ST-016 workpack risk analysis.
- Schema validation (additionalProperties): Will be checked when creating baseline copies in ST-016.
- Two-file pattern consideration: Applicable if ST-016 needs test annotation data.
