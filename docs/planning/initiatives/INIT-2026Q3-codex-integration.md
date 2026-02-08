# INIT-2026Q3-codex-integration — Интеграция с Codex-пайплайном

**Приоритет:** Низкий  
**Период:** 2026Q3  
**Статус:** Proposed  
**Owner:** TBD

## Контекст
После стабилизации LLM-фич нужна дисциплина разработки через workpacks и ревью-гейты.

## Цель
- Встроить разработку инициатив через PLAN/APPLY workflow
- Добавить codex-review-gate и шаблоны

## Scope
- Генерация шаблонов workpack’ов под типовые изменения (LLM assist, tests, CI)
- Добавление правил ревью (codex-review-gate)
- Документирование процесса в репозитории

## Out of scope
- Переписывание существующего кода “под пайплайн”
- Изменение контрактов ради процесса

## Acceptance criteria
1. Есть шаблоны workpack’ов
2. Есть документированный процесс PLAN/APPLY
3. Есть минимальный ревью-гейт

## Deliverables
- workpack templates
- codex-review-gate setup (repo-local)
- docs updates
