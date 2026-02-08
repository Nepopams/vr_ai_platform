# INIT-2026Q1-assist-mode — Assist-режим (normalizer++, entity assist, clarify suggestor)

**Приоритет:** Средний  
**Период:** 2026Q1  
**Статус:** Proposed  
**Owner:** TBD

## Контекст
Baseline-роутер и extraction покрывают “простые” команды, но требуют улучшения качества понимания.
Assist-mode должен давать подсказки LLM, которые принимает/отклоняет deterministic слой.

## Цель
- Улучшить канонизацию входного текста (normalizer)
- Улучшить извлечение сущностей (entity assist)
- Улучшить формулировку уточняющего вопроса (clarify suggestor)
- Сохранить deterministic control: LLM не принимает решения

## Scope (входит)
- LLM-normalizer: приведение фразы к канонической форме (без изменения смысла)
- Entity assist:
  - множественные товары/атрибуты (в рамках shopping)
  - распознавание количества/единиц (где возможно)
- Clarify suggestor:
  - предложить один осмысленный вопрос
  - предложить список `missing_fields` (internal), используемый baseline
- Таймауты, error handling, логирование summaries

## Out of scope
- Изменения публичных контрактов
- Удаление baseline логики
- Обязательное принятие LLM результата

## Acceptance criteria
1. Assist-mode включается флагом
2. Baseline выбирает принимать подсказку или нет (правила документированы)
3. При любой ошибке/таймауте LLM — baseline без деградации
4. Логи без raw user text / raw LLM output

## Метрики успеха
- Снижение доли clarify на “простых” командах
- Снижение clarify-итераций
- Рост entity extraction hit rate

## Deliverables
- Normalizer assist
- Entity assist
- Clarify suggestor
- Документация “acceptance rules” для подсказок
