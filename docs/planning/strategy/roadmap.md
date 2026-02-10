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
| **Total** | | **5** | **19/19** | **228** | **8 done** |

Детали закрытых инициатив: `docs/planning/initiatives/INIT-*.md`.
Ретроспективы: `docs/planning/sprints/S01..S05/retro.md`.

---

## CURRENT (2026Q4) — Production Hardening

Цель фазы: подготовить платформу к реальной эксплуатации с живым LLM.

1) **INIT-2026Q4-production-hardening** — Production Hardening: LLM, метрики, качество (**Высокий**)
- Реальный LLM-клиент в shadow router (flag-gated, fallback, kill-switch)
- Golden dataset (≥20 команд) + evaluation script + quality metrics
- Latency observability (p50/p95/p99, structured logging, baseline comparison)
- Error budget / fallback metrics (risk log, dashboard-ready JSONL)

**Gates:**
- Feature flags / kill-switch для LLM (retain existing)
- Deterministic fallback 100% (retain existing)
- Все 228 существующих тестов проходят

**Success signals:**
- Shadow router работает с реальным LLM (под флагом)
- Golden dataset автоматически оценивает intent accuracy ≥ baseline
- Latency breakdown и fallback rate измеримы и логируются

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
