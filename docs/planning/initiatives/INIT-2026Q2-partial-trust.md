# INIT-2026Q2-partial-trust — Partial Trust для add_shopping_item

**Приоритет:** Средний  
**Период:** 2026Q2  
**Статус:** Proposed  
**Owner:** TBD

## Контекст
После Shadow и Assist-mode появляется возможность контролируемо дать LLM право
подменять baseline **в одном узком коридоре** для замера реального эффекта.

## Цель
Включить Partial Trust **только** для интента `add_shopping_item`:
- LLM может заменить baseline решение с small sampling
- Только при прохождении acceptance rules
- С kill-switch и риск-логом

## Scope
- Sampling: 0.01 → 0.1 (конфиг)
- Только `add_shopping_item` (или существующее точное имя интента)
- Acceptance rules (пример):
  - intent совпадает с allowlist
  - required fields присутствуют
  - нет конфликтующих атрибутов
  - confidence/quality checks (если есть)
- Risk-log (structured):
  - `accepted_llm` / `fallback` / `error`
  - причина fallback
  - latency bucket
- Kill-switch (1 флаг)
- Метрики регрессий и сравнение с baseline

## Out of scope
- Любые другие интенты
- Изменение контрактов
- Автономное планирование

## Acceptance criteria
1. По умолчанию выключено
2. Работает только на allowlist intent
3. В любой нештатной ситуации — deterministic fallback
4. Есть риск-лог и метрики оценки регрессий

## Метрики
- Regression rate (ошибочные решения vs baseline)
- Clarify rate / iteration count
- Job success proxy (если есть сигнал от продукта)
- Latency p95

## Deliverables
- LLM-first corridor implementation (gated)
- Risk logging + dashboard script (минимум)
- Документация rollout
