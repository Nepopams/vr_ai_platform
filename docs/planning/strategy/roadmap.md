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
| 2026Q2 | ASR UAT | 1 | 1/1 | 270→325 | asr-cloudru-whisper |
| **Total** | | **9** | **31/31** | **325** | **10 done** |

Детали закрытых инициатив: `docs/planning/initiatives/INIT-*.md`.
Ретроспективы: `docs/planning/sprints/S01..S08/retro.md`.

---

## CURRENT — TBD

Текущая инициатива `INIT-2026Q2-asr-cloudru-whisper` завершена и UAT-подтверждена.
Следующая инициатива определяется PO.

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
