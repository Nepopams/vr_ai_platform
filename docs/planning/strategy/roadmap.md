# Roadmap (Now / Next / Later) — aligned with Initiatives

Этот roadmap построен вокруг списка инициатив `docs/planning/initiatives/` и отражает
их порядок приоритетности: **High → Medium → Low**.

---

## Completed

| Phase | Period | Sprints | Stories | Tests | Initiatives |
|-------|--------|---------|---------|-------|-------------|
| 2026Q1 | S01 | 1 | 4/4 | 0→109 | shadow-router, assist-mode |
| 2026Q2 | S02-S04 | 3 | 9/9 | 109→202 | partial-trust, multi-entity-extraction, improved-clarify |
| 2026Q3 | S05 | 1 | 6/6 | 202→228 | semver-and-ci, agent-registry-integration, codex-integration (organically) |
| 2026Q4 | S06-S08 | 3 | 11/11 | 228→270 | production-hardening |
| 2026Q2 | ST-047 | 1 | 1/1 | 270→325 | asr-cloudru-whisper (local MVP; manual Cloud.ru UAT pending) |
| 2026Q3 | ST-048-ST-051 | 1 | 4/4 | 325→340 | domain-planner-v1-narrow-household-command-corridor (provider closure; HomeTusk acceptance separate) |
| 2026Q3 | ST-052-ST-056 | 1 | 5/5 | 340→346 (+4 skipped) | domain-planner-v1-contract-and-50-scenario-eval (provider Gate D GO; HomeTusk runtime integration separate) |
| **Total** | | **11** | **40/40** | **346 (+4 skipped)** | **12 done** |

Детали закрытых инициатив: `docs/planning/initiatives/INIT-*.md`.
Ретроспективы: `docs/planning/sprints/S01..S08/retro.md`.

---

## CURRENT — Awaiting PO / HomeTusk Decision

| Field | Value |
|-------|-------|
| Active initiative | None selected after current Gate D |
| Latest completed initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md` |
| Execution notes | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md` |
| Epic | `docs/planning/epics/EP-017/epic.md` |
| Handoff | `docs/planning/workpacks/ST-056/hometusk-handoff.md` |
| Status | Provider-side Gate D GO; 50 scenarios evaluated; 0 blocker failures; HomeTusk runtime/mobile/backend/API remains separate |

`INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor` remains Completed as provider-side closure evidence. `INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval` is now also Completed as provider evidence and handoff.

---

## NEXT — TBD after HomeTusk Review

Кандидаты определяются PO. Recommended next candidate: a separate HomeTusk-owned runtime integration initiative if HomeTusk accepts the provider handoff.

---

## LATER — TBD

---

## Prioritization principles

- Сначала измеримость и безопасность, потом "умность"
- Любая LLM-фича должна иметь deterministic fallback и kill-switch
- Контракты и DecisionDTO — стабильная граница ответственности
- Расширяемость = через инициативы, ADR и совместимость, а не через "быстрые хаки"
