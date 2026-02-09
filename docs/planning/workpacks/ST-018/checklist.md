# ST-018: DoD Checklist

## Acceptance Criteria

- [ ] AC-1: ADR-005 has "Integration Status" (shadow=integrated, assist=integrated, core=not yet)
- [ ] AC-2: ADR-005 has "Phase 1: Core Pipeline Gate" with `AGENT_REGISTRY_CORE_ENABLED` flag
- [ ] AC-3: `docs/diagrams/agent-registry-integration.puml` exists, valid PlantUML, shows V2 pipeline + registry
- [ ] AC-4: ADR index and diagrams index updated
- [ ] AC-5: No files outside `docs/` modified

## Verification

```bash
grep -c "## Integration Status" docs/adr/ADR-005-internal-agent-contract-v0.md   # 1
grep -c "## Phase 1" docs/adr/ADR-005-internal-agent-contract-v0.md              # 1
test -f docs/diagrams/agent-registry-integration.puml && echo "OK"
grep "agent-registry-integration" docs/_indexes/diagrams-index.md
git diff --name-only | grep -v "^docs/" && echo "FAIL" || echo "OK"
```

## Invariants

- [ ] ADR-005 existing sections (Контекст, Решение, Последствия) unchanged
- [ ] No files outside `docs/` modified
- [ ] Existing tests unaffected
