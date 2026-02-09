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

## Integration Status

| Component | File | Status | Feature Flag |
|-----------|------|--------|-------------|
| Shadow agent invoker | `routers/agent_invoker_shadow.py` | Integrated, flag-gated | `shadow_agent_invoker_enabled` (from `routers.shadow_agent_config`) |
| Assist mode hints | `routers/assist/runner.py` | Integrated, flag-gated | `assist_agent_hints_enabled()` (from `routers/assist/config.py`) |
| Core pipeline | `graphs/core_graph.py` | Not yet integrated | `AGENT_REGISTRY_CORE_ENABLED` (planned, Phase 1) |

Notes:
- Shadow invoker: loads registry via `AgentRegistryV0Loader.load(path_override=...)`, filters by mode="shadow" and allowlist, fire-and-forget execution.
- Assist hints: loads registry via `AgentRegistryV0Loader.load()`, filters by mode="assist" and capability `extract_entities.shopping`, applies best candidate if matching.
- Core pipeline: no registry references as of S04. Phase 1 will add a read-only annotation gate.

## Phase 1: Core Pipeline Gate

**Approach:** Registry capabilities lookup annotates decisions with agent metadata (read-only probe).

- The core pipeline (`graphs/core_graph.py`) will query `CapabilitiesLookup` for agents matching the detected intent.
- A `registry_snapshot` will be attached to the decision trace log (NOT to DecisionDTO response).
- **No behavior change** to the deterministic baseline — baseline always executes regardless of registry state.
- Feature flag: `AGENT_REGISTRY_CORE_ENABLED` (env var, default: `false`).
- Any error or timeout in registry lookup → silently skipped, decision produced normally.

**V2 pipeline flow** (from `routers/v2.py`):
1. `normalize()`
2. `start_shadow_router()`
3. `apply_assist_hints()` ← uses registry (assist mode)
4. `plan()`
5. `validate_and_build()`
6. `invoke_shadow_agents()` ← uses registry (shadow mode)
7. `_maybe_apply_partial_trust()`
8. return decision

Phase 1 adds a registry annotation step inside `core_graph.process_command()`, gated by `AGENT_REGISTRY_CORE_ENABLED`.

## Feature Flag Requirements

All registry-related flags default to `false`. Any error or timeout in registry falls back to deterministic baseline.

| Flag | Component | Default | Source | Purpose |
|------|-----------|---------|--------|---------|
| `AGENT_REGISTRY_ENABLED` | Registry loader | `false` | `agent_registry/config.py` | Master switch for registry loading |
| `AGENT_REGISTRY_PATH` | Registry loader | `None` | `agent_registry/config.py` | Optional path override for registry YAML |
| `shadow_agent_invoker_enabled` | Shadow invoker | `false` | `routers/shadow_agent_config.py` | Enable shadow agent execution |
| `assist_agent_hints_enabled` | Assist runner | `false` | `routers/assist/config.py` | Enable agent entity hints |
| `AGENT_REGISTRY_CORE_ENABLED` | Core pipeline | `false` | `agent_registry/config.py` (planned) | Enable registry annotation gate (Phase 1) |
