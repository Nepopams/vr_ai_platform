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
| **Total** | | **10** | **35/35** | **340** | **11 done** |

Детали закрытых инициатив: `docs/planning/initiatives/INIT-*.md`.
Ретроспективы: `docs/planning/sprints/S01..S08/retro.md`.

---

## CURRENT — No Active Initiative Selected

Текущая high-priority provider-side инициатива закрыта. Следующая active initiative не выбрана; кандидаты остаются в `NEXT`.

---

## NEXT — TBD

Кандидаты определяются PO.

---

## LATER — TBD

---

## Prioritization principles

- Сначала измеримость и безопасность, потом "умность"
- Любая LLM-фича должна иметь deterministic fallback и kill-switch
- Контракты и DecisionDTO — стабильная граница ответственности
- Расширяемость = через инициативы, ADR и совместимость, а не через "быстрые хаки"
