# INIT-2026Q2-partial-trust — Partial Trust для add_shopping_item

**Приоритет:** Средний  
**Период:** 2026Q2  
**Статус:** Done
**Owner:** Team (Claude + Codex + Human)
**Closed:** 2026-02-08

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
- LLM-first corridor implementation (gated) — `routers/partial_trust_*.py`, `routers/v2.py`
- Risk logging + dashboard script (минимум) — `app/logging/partial_trust_risk_log.py`, `scripts/analyze_partial_trust.py`
- Документация rollout — `docs/operations/partial-trust-runbook.md`

## Closure Evidence

| AC | Verdict | Evidence |
|----|---------|----------|
| 1. По умолчанию выключено | PASS | `partial_trust_enabled()` returns `false`, `sample_rate()` returns `0.0` — verified in `tests/test_partial_trust_phase3.py::test_partial_trust_disabled_no_llm` |
| 2. Только allowlist intent | PASS | `ALLOWED_CORRIDOR_INTENTS = {"add_shopping_item"}`, acceptance rejects wrong intent — verified in `tests/test_partial_trust_phase2.py::test_acceptance_rejects_wrong_intent` |
| 3. Deterministic fallback | PASS | All error paths return `(None, error_type)` → baseline used — verified in `tests/test_partial_trust_edge_cases.py::test_v2_partial_trust_error_catchall` |
| 4. Риск-лог и метрики | PASS | JSONL risk-log in `app/logging/partial_trust_risk_log.py`, analyzer in `scripts/analyze_partial_trust.py` with 14 tests |

Full verification report: `docs/planning/epics/EP-003/verification-report.md`
ADR: `docs/adr/ADR-004-partial-trust-corridor.md` (Accepted)
