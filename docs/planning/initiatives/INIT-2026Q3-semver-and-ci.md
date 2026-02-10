# INIT-2026Q3-semver-and-ci — SemVer и CI-контроль контрактов

**Приоритет:** Низкий  
**Период:** 2026Q3  
**Статус:** Done (S05 — ST-015, ST-016, ST-017)
**Owner:** Codex/Claude

## Контекст
Контракты и decision flow должны быть защищены CI-гейтами и семантическим версионированием.

## Цель
- Автоматически валидировать схемы и совместимость
- Требовать major bump на breaking changes
- Добавить базовые sanity checks

## Scope
- validate_contracts
- graph_sanity
- decision_log_audit
- Автоанализ diff контрактов (минимальный)
- Policy: breaking -> major + approval

## Out of scope
- Полноценный release management
- Сложные политики безопасности

## Acceptance criteria
1. CI падает на невалидных схемах
2. CI сигналит о breaking changes и требует major bump
3. Проверки документированы

## Deliverables
- CI jobs / scripts
- docs policy
- пример workflow для PR
