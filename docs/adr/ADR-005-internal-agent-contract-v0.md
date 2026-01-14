# ADR-005: Internal Agent Contract v0 (ABI платформы, формат ДОРА)

- Status: Accepted
- Date: 2026-01-13
- Related ADRs:
  - ADR-000: `docs/adr/ADR-000-ai-platform-intent-decision-engine.md`
  - ADR-001: `docs/adr/ADR-001-contract-versioning-compatibility-policy.md`
  - ADR-002: `docs/adr/ADR-002-agent-model-execution-boundaries-mvp.md`
  - ADR-003: `docs/adr/ADR-003-llm-model-policy-registry-and-escalation.md`
  - ADR-004: `docs/adr/ADR-004-partial-trust-corridor.md`
- Scope: internal runtime (agents/routers), не часть внешних контрактов

## Контекст

Платформа развивается в сторону более сложной оркестрации агентов. Без общего внутреннего контракта
агенты начинают расходиться по форматам входов/выходов и логированию, что приводит к “snowflake”
поведению, сложной отладке и рискам регрессий.

Нужен единый ABI уровня платформы для агентов, чтобы:

- сохранять детерминированность и совместимость (MVP + ADR-001/002);
- поддерживать registry/оркестрацию без ad‑hoc форматов;
- обеспечить приватность и безопасное логирование по умолчанию.

## Решение

Фиксируем **Internal Agent Contract v0** как ABI платформы (формат ДОРА).
Контракт является **internal‑only**, не относится к публичным API (CommandDTO/DecisionDTO)
и не меняет внешние контракты.

Ключевые правила:

- Никаких ad‑hoc входов/выходов: все агенты обязаны следовать Agent Contract v0.
- Агент регистрируется через file‑based registry (AgentSpec), с явными capabilities.
- Для LLM‑агентов обязательно использовать llm_policy (ADR-003).
- Любой output проходит валидацию/allowlist (fail‑safe).
- По умолчанию **без raw user text и raw LLM output в логах**; только summaries/counters.
- Reason codes стандартизированы и согласованы между агентами.

## Последствия

Плюсы:

- Единый стандарт и предсказуемая интеграция агентов.
- Снижение рисков приватности и лог‑регрессий.
- Проще аудит и масштабирование оркестрации.

Минусы:

- Требуется дисциплина и обновление ADR/registry при расширении.

## Связанные документы

- `AGENTS.md` — обязательные правила агента.
- `CODEX.md` — требования к изменениям.
