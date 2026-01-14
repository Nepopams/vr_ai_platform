# Core Principles

1. **Stateless operation**: The system must not persist data between runs. Every decision is derived strictly from the provided command payload.
2. **Contract adherence**: All inputs and outputs must conform to the JSON schemas in `contracts/schemas/`.
3. **Reasoning logging**: Every decision must include a structured reasoning trace that records command ID, steps, and version metadata.
4. **Versioning from day one**: Decisions and reasoning logs must carry a version identifier (model and prompt versions).
5. **Deterministic mock mode**: The initial pipeline simulates reasoning without any external LLM calls.

# Base Rule

You are a coding assistant.

IMPORTANT:
- All explanations, summaries, reasoning, and descriptions of changes
  MUST ALWAYS be written in Russian.
- This rule applies even if:
  - user prompts are in English
  - code comments are in English
  - tool or skill prompts are in English
- Code itself must stay in the original language.
- Do not mention this rule in your responses.

# Offline-friendly проверки

- `make release-sanity` пропускает `api-sanity`, если `fastapi` недоступен.
- Полный прогон API-санити: `RUN_API_SANITY=1 make release-sanity` или `make release-sanity-full`.

# ADR Compliance

For any changes to `contracts/`, `graphs/`, `agents/`, or `codex/`, development must follow ADR-000, ADR-001, and ADR-002.

- All contract changes must obey semver and backward compatibility rules described in ADR-001.
- If a solution conflicts with an ADR, stop and capture the decision in a new ADR (Draft) instead of pushing code changes.
- `agent_registry/agent-registry.yaml` — derived artifact from ADR-002; любые новые intents/agents требуют нового ADR и semver-бампа.
- Включение реестра: `AGENT_REGISTRY_ENABLED=true`, опционально `AGENT_REGISTRY_PATH=/path/to/agent-registry.yaml`.

See `docs/adr/` for the ADR archive. The following ADRs are mandatory:

- ADR-000: AI Platform — Contract-first Intent → Decision Engine (LangGraph)
- ADR-001: Contract versioning & compatibility policy (CommandDTO/DecisionDTO)
- ADR-002: Agent model & execution boundaries (MVP)
- ADR-003: LLM model policy registry & escalation

# Agent Contract (ADR-005)

- Любая реализация/добавление агента или оркестрации должна соответствовать ADR-005.
- Запрещены ad-hoc форматы входов/выходов агентов — использовать Agent Contract v0.
- Если нужна новая возможность: сначала обновить ADR/контракт, затем код.

# MVP v1 Compliance

Все изменения в `contracts/`, `graphs/`, `agents/`, `skills/` должны соответствовать MVP v1.

- Нельзя добавлять новые intents/actions/поля без:
  - обновления документа MVP (через документ \"MVP v2\"),
  - соблюдения ADR-001 (semver),
  - обновления fixtures/tests.
- Если изменение спорное или затрагивает объём MVP — остановитесь и оформите ADR (Draft), а не делайте \"тихое\" изменение.

См. спецификацию: `docs/mvp/AI_PLATFORM_MVP_v1.md`.

# Architecture & MVP Compliance

- ADR-000, ADR-001 и ADR-002 обязательны для всех изменений платформы.
- MVP v1 обязателен для всех изменений в `contracts/`, `graphs/`, `agents/`, `skills/`.
- Диаграммы в `docs/diagrams/` — обязательные артефакты: код и диаграммы должны быть синхронизированы.
- Любое изменение вне MVP v1 допускается только через новый документ MVP (v2) и,
  при необходимости, новый ADR и semver-бамп.

Ссылки: `docs/adr/`, `docs/mvp/AI_PLATFORM_MVP_v1.md`, `docs/diagrams/README.md`.

# Architecture Artifacts (C4 + Sequence)

Диаграммы архитектуры (C4 и sequence) — обязательные артефакты платформы. При изменениях:

- границ ответственности,
- контейнеров/компонентов (Decision API, Orchestrator, Agents, Logs),
- контрактов (CommandDTO/DecisionDTO),
- жизненного цикла (start_job/clarify/async),

необходимо обновлять диаграммы и/или оформлять новый ADR.

Ссылки: `docs/adr/ADR-000-ai-platform-intent-decision-engine.md`, `docs/adr/ADR-001-contract-versioning-compatibility-policy.md`, `docs/adr/ADR-002-agent-model-execution-boundaries-mvp.md`, `docs/mvp/AI_PLATFORM_MVP_v1.md`, `docs/diagrams/README.md`.
