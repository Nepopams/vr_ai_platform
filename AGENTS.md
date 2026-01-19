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


# Agent Architecture

The HomeTask AI platform is designed to be modular. Agents are lightweight components that can be orchestrated by the core graph.

## Project Summary

HomeTask is an AI platform that routes user commands through a graph of specialized agents to produce structured decisions.

## Do Not Break Contracts

Do not break contracts. Any change to contract definitions or their consumers must preserve backward compatibility unless a coordinated, versioned change is explicitly planned and validated.

## How Agents Are Invoked

- Agents are instantiated within the graph pipeline (`graphs/core_graph.py`).
- Each agent accepts a command payload and returns a structured contribution to the decision.
- The pipeline merges agent outputs into a final decision object.

## Extending the Pipeline

1. Create a new agent module in `agents/`.
2. Define a callable that accepts the command payload and returns a structured result.
3. Wire the agent into the core graph pipeline and add tests.

## Versioning

- Agents should include a `version` identifier.
- The pipeline should record agent versions in the reasoning log whenever an agent is invoked.

## ADR-first development

- Follow ADR-000, ADR-001, and ADR-002 for all platform evolution decisions.
- Ensure safe handling for unknown `action` values and payload fields.
- `contracts/VERSION` is the source of truth for contract schema versions.
- `agent_registry/agent-registry.yaml` — derived from ADR-002; новые intents/agents требуют нового ADR и semver-бампа.
- Включение реестра: `AGENT_REGISTRY_ENABLED=true`, опционально `AGENT_REGISTRY_PATH=/path/to/agent-registry.yaml`.
- Model policy / LLM selection must follow ADR-003.
- Запрещено хардкодить модели в агентах без политики/ADR.

## ADR-first, MVP-first, keep diagrams in sync

- Любые изменения должны соответствовать ADR-000/ADR-001/ADR-002 и MVP v1.
- Диаграммы в `docs/diagrams/` — обязательные артефакты, поддерживайте синхронизацию с кодом.
- Safe handling unknown action/payload — обязательное правило совместимости (ADR-001).
- См. `docs/mvp/AI_PLATFORM_MVP_v1.md` и `docs/diagrams/README.md`.

## ADR-first + MVP-first development

- MVP v1 обязателен для всех изменений в платформе.
- Спецификация: `docs/mvp/AI_PLATFORM_MVP_v1.md`.

## Agent Contract v0 (ADR-005) — обязательный стандарт

Контракт нужен, чтобы избежать “snowflake” агентов и подготовить устойчивую оркестрацию.
**Источник истины**: ADR-005 `docs/adr/ADR-005-internal-agent-contract-v0.md`.

Ключевые правила:

- Internal-only: контракт не является частью `contracts/` и не влияет на публичные API.
- Режимы `shadow/assist/partial_trust` строго ограничены и не меняют DecisionDTO вне коридоров.
- Обязательные validate/allowlist проверки для входов и выходов.
- Приватность: по умолчанию **без raw user text и raw LLM output в логах**.
- Reason codes стандартизированы и используются единообразно.

Definition of Done для нового агента:

- AgentSpec зарегистрирован в file-based registry.
- Capabilities агента явно определены.
- Runner определён (`python_module` или `llm_policy_task`).
- Output проходит validation toolkit/allowlist.
- Логирование только summaries/counters, без raw данных.

## Agent Platform v0 (Phase 4 current state)

Состав компонентов (internal-only, без подключения к RouterV2):

- Реестр агентов v0: `agent_registry/agent-registry-v0.yaml` + loader `agent_registry/v0_loader.py`.
- Каталог capabilities v0: `agent_registry/capabilities-v0.yaml`.
- Validation toolkit: `agent_registry/validation.py` и `agent_registry/v0_reason_codes.py`.
- AgentRunner v0: `agent_registry/v0_runner.py` (`python_module`, `llm_policy_task`).
- Agent run logs: `app/logging/agent_run_log.py` (opt-in).
- Baseline агенты: `agents/baseline_shopping.py`, `agents/baseline_clarify.py`.
- Ручной запуск: `scripts/run_agent_v0.py`.

Checklist для добавления агента v0:

- Spec добавлен в registry v0, `enabled=false` по умолчанию.
- Запуск/проверка только вручную через AgentRunner/`scripts/run_agent_v0.py`.
- Ровно 1 capability, описана в catalog (payload_allowlist, contains_sensitive_text).
- Runner.ref корректен и mode допустим для capability.
- Output проходит validation toolkit; в логах только summaries/counters, без raw данных.

Assist agent-hints (Phase 5.2):

- Подключаются только флагами и не меняют выбор `action/job_type`.
- Используются как подсказки для отсутствующих сущностей, deterministic-first guardrails обязательны.

## Skills

Skills live under `skills/*`. Each skill has its own directory with implementation and metadata, and may include its own Make targets for local execution or validation.

## Keep diagrams in sync

If you change `contracts/`, `graphs/`, `agents/`, or `api`, check whether C4/sequence diagrams need updates. If you did not update diagrams, explain why in the commit/PR description.

## Canonical Commands

- `make validate_contracts`
- `make run_graph`
- `make run_graph_suite`
- `make audit_decisions`
- `make release_sanity`
