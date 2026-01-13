# ADR-004: Partial Trust Corridor (LLM-first, ограниченный коридор)

- Status: Draft
- Date: 2026-01-12
- Related ADRs:
  - ADR-000: `docs/adr/ADR-000-ai-platform-intent-decision-engine.md`
  - ADR-001: `docs/adr/ADR-001-contract-versioning-compatibility-policy.md`
  - ADR-002: `docs/adr/ADR-002-agent-model-execution-boundaries-mvp.md`
  - ADR-003: `docs/adr/ADR-003-llm-model-policy-registry-and-escalation.md`
- Scope: RouterV2 pipeline (internal-only), без изменения публичных контрактов

## Контекст

MVP и ADR-002 задают базовую норму: LLM не должен напрямую формировать DecisionDTO и не может влиять
на решения глобально. При этом требуется ограниченный «LLM-first» режим в одном узком коридоре для
повышения качества извлечения покупок, с обязательным fallback и наблюдаемостью.

## Решение

Ввести **controlled exception**: Partial Trust corridor для **одного** intent (`add_shopping_item`)
под строгими флагами и правилами принятия. Вне коридора и при любом сбое LLM используется
детерминированный baseline.

### Границы

- Только один intent/коридор (`add_shopping_item`).
- Никаких изменений `contracts/` или публичной семантики DecisionDTO/CommandDTO.
- Никаких новых intents/actions/полей.
- Только под feature flags и sample-rate rollout.
- Любой сбой LLM → deterministic fallback.

### Acceptance rules (упрощённо)

- intent/job_type строго совпадают с коридором;
- строгая allowlist‑валидация shape/полей;
- sanity checks по item.name и list_id;
- policy gate по `llm_policy` + доступность профиля;
- confidence threshold (или суррогат при отсутствии confidence).

### Double-run и риск‑логирование

- Baseline (RouterV2) вычисляется всегда.
- LLM‑candidate сравнивается с baseline в safe‑summary формате.
- В JSONL‑логах фиксируются статус/причины/метрики **без raw данных**.

### Kill‑switch и rollout

- Master‑flag выключает corridor полностью.
- Stable sampling по `command_id` обеспечивает воспроизводимость.
- Роллаут: 0.01 → 0.05 → 0.10 с быстрым откатом `PARTIAL_TRUST_ENABLED=false`.

## Совместимость с ADR-002

ADR-002 остаётся базовой нормой. Partial Trust — ограниченное исключение:
LLM не изменяет контракты, не добавляет intents/actions и не влияет на решения
за пределами одного строго контролируемого коридора.

## Последствия

Плюсы:

- Улучшение качества извлечения покупок в узком коридоре.
- Прозрачный риск‑контур с fallback и метриками.

Минусы:

- Усложнение RouterV2 (дополнительная логика контроля).
- Требуется дисциплина флагов и наблюдаемости.
