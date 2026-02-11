# INIT-2026Q1-deepen-llm-trust — Deepen LLM Trust: Partial Trust create_task + Comparison

**Приоритет:** Высокий
**Период:** 2026Q1 (PI02)
**Статус:** Proposed
**Owner:** TBD

## Контекст

Partial trust corridor работает для одного интента (`add_shopping_item`).
Confidence threshold захардкожен. Нет инструмента сравнения качества
LLM-решений с baseline. Для расширения "умности" платформы нужно:
- Распространить partial trust на второй интент (`create_task`)
- Сделать confidence thresholds настраиваемыми
- Построить offline A/B comparison

## Цель

Расширить partial trust на `create_task`, сделать confidence thresholds
конфигурируемыми per-intent, построить инструмент offline-сравнения
LLM-решений с baseline на golden dataset.

## Scope

### Epics

- **EP-013**: Partial Trust for create_task (ST-040 — ST-042)
- **EP-014**: Confidence Thresholds & A/B Comparison (ST-043 — ST-046)

### Out of scope

- Partial trust для интентов кроме `add_shopping_item` и `create_task`
- LLM-first для clarify decisions
- Автоматическая настройка threshold
- Online A/B testing infrastructure
- Новые интенты / домены

## Acceptance criteria

1. Partial trust corridor принимает `create_task` (flag-gated)
2. Acceptance rules для `create_task`: shape validation, field allowlist (title + assignee_id), confidence gate
3. Per-intent confidence thresholds в `llm-policy.yaml`
4. A/B comparison script: match rate, entity diff, confidence distribution
5. Golden dataset расширен на 10+ `create_task` entries
6. Observability guide обновлён
7. Все MVP exit criteria сохранены

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| create_task acceptance rules сложнее shopping | Medium | Strict allowlist (title + assignee_id only) |
| ADR-004 amendment scope creep | Medium | PO gate, strict scope: только add `create_task` |
| Golden dataset недостаточен | Low | 10+ entries covering edge cases |

## Dependencies

- Existing partial trust corridor (`routers/partial_trust_*`) — Done
- ADR-004 (partial trust corridor) — Accepted, needs amendment
- `llm-policy.yaml` task/profile structure — Available
- Golden dataset (22 entries) + evaluation script — Available
