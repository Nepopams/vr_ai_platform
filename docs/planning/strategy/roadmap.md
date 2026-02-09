# Roadmap (Now / Next / Later) — aligned with Initiatives

Этот roadmap построен вокруг списка инициатив `docs/planning/initiatives/` и отражает
их порядок приоритетности: **High → Medium → Low**.

---

## Completed

| Phase | Period | Sprints | Stories | Tests | Initiatives |
|-------|--------|---------|---------|-------|-------------|
| 2026Q1 | S01 | 1 | 4/4 | 0→109 | shadow-router, assist-mode |
| 2026Q2 | S02-S04 | 3 | 9/9 | 109→202 | partial-trust, multi-entity-extraction, improved-clarify |
| **Total** | | **4** | **13/13** | **202** | **5 done** |

Детали закрытых инициатив: `docs/planning/initiatives/INIT-2026Q1-*.md`, `INIT-2026Q2-*.md`.
Ретроспективы: `docs/planning/sprints/S01..S04/retro.md`.

---

## NOW (2026Q3) — процесс, контракты и расширяемость

Цель фазы: закрепить дисциплину разработки и подготовиться к расширению.

1) **INIT-2026Q3-semver-and-ci** — SemVer и CI-контроль контрактов
- validate_contracts / graph_sanity / decision_log_audit
- diff-анализ контрактов
- политика: breaking → major bump + approval

2) **INIT-2026Q3-codex-integration** — Интеграция с Codex-пайплайном
- workpacks + PLAN/APPLY
- codex-review-gate
- шаблоны типовых пакетов изменений (LLM, tests, CI)

3) **INIT-2026Q3-agent-registry-integration** — Интеграция агентной платформы v0
- agent_registry + runner для внутренних baseline-агентов
- ADR-005 с границами и рисками
- включение/отключение через конфиг/флаги

**Gates:**
- CI защищает contracts и decision flow
- Любые расширения через ADR и совместимость

---

## NEXT — TBD

Кандидаты определяются по итогам 2026Q3.

---

## LATER — TBD

---

## Prioritization principles

- Сначала измеримость и безопасность, потом "умность"
- Любая LLM-фича должна иметь deterministic fallback и kill-switch
- Контракты и DecisionDTO — стабильная граница ответственности
- Расширяемость = через инициативы, ADR и совместимость, а не через "быстрые хаки"
