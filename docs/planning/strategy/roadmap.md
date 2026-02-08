# Roadmap (Now / Next / Later) — aligned with Initiatives

Этот roadmap построен вокруг списка инициатив `docs/planning/initiatives/` и отражает
их порядок приоритетности: **High → Medium → Low**.

---

## NOW (2026Q1) — измеримость и безопасные подсказки (Highest priority)

Цель фазы: получить **измеримость** и безопасный LLM-слой без влияния на DecisionDTO.

1) **INIT-2026Q1-shadow-router** — Shadow LLM-router и метрики (**Высокий**)
- RouterSuggestion (internal)
- параллельный LLM-вызов на каждый CommandDTO (под флагом)
- JSONL-лог (intent, entities_summary, clarify_question, latency, error_type)
- анализ golden-dataset (скрипт + гайд)
- *никакого влияния на DecisionDTO*

2) **INIT-2026Q1-assist-mode** — Assist-режим (normalizer++, entity assist, clarify suggestor) (**Средний**)
- LLM-normalizer для канонизации фразы
- улучшение entity extraction (в т.ч. составные/атрибуты в рамках shopping)
- suggest_clarify + acceptance rules (baseline решает, принимать ли подсказку)
- таймауты и безопасное логирование

**Gates (обязательные условия):**
- Feature flags / kill-switch для LLM
- Никаких raw user text / raw LLM output в логах
- Deterministic fallback 100%

**Success signals:**
- Появился воспроизводимый отчёт по golden-dataset
- Понимаем intent/entity качество LLM и baseline на метриках
- Нет деградации latency p95 / ошибок при выключенном флаге

---

## NEXT (2026Q2) — контролируемый Partial Trust и сокращение clarify

Цель фазы: минимально и измеримо повысить “умность” там, где baseline стабилен.

1) **INIT-2026Q2-partial-trust** — Partial Trust для add_shopping_item (**Средний**)
- sampling 0.01 → 0.1 (конфиг)
- allowlist строго на один intent
- risk-log: accepted_llm / fallback / error + причина
- kill-switch и метрики регрессий

2) **INIT-2026Q2-multi-entity-extraction** — Поддержка множественных сущностей (**Средний**)
- списки покупок (milk + bread + bananas)
- количества/единицы/простые атрибуты
- совместимость с текущими контрактами и схемами

3) **INIT-2026Q2-improved-clarify** — Улучшение вопросов Clarify (**Средний**)
- missing_fields (internal)
- LLM-assist для одного осмысленного вопроса
- baseline уточняет только реально недостающие поля
- метрика: снижение clarify-итераций

**Gates:**
- Partial Trust выключен по умолчанию
- Любая ошибка/таймаут LLM → deterministic-only
- Регрессии измеримы (risk-log + golden-dataset)

**Success signals:**
- Снижение среднего числа clarify-итераций
- Рост доли команд, завершающихся `start_job` (proxy)
- Partial Trust не увеличивает регрессии по принятым решениям

---

## LATER (2026Q3) — процесс, контракты и расширяемость (Low priority)

Цель фазы: закрепить дисциплину разработки и подготовиться к расширению.

1) **INIT-2026Q3-semver-and-ci** — SemVer и CI-контроль контрактов (**Низкий**)
- validate_contracts / graph_sanity / decision_log_audit
- diff-анализ контрактов
- политика: breaking → major bump + approval

2) **INIT-2026Q3-codex-integration** — Интеграция с Codex-пайплайном (**Низкий**)
- workpacks + PLAN/APPLY
- codex-review-gate
- шаблоны типовых пакетов изменений (LLM, tests, CI)

3) **INIT-2026Q3-agent-registry-integration** — Интеграция агентной платформы v0 (**Низкий**)
- agent_registry + runner для внутренних baseline-агентов
- ADR-005 с границами и рисками
- включение/отключение через конфиг/флаги

**Gates:**
- CI защищает contracts и decision flow
- Любые расширения через ADR и совместимость

---

## Prioritization principles

- Сначала измеримость и безопасность, потом “умность”
- Любая LLM-фича должна иметь deterministic fallback и kill-switch
- Контракты и DecisionDTO — стабильная граница ответственности
- Расширяемость = через инициативы, ADR и совместимость, а не через “быстрые хаки”
