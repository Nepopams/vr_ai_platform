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

## ADR-first, MVP-first, keep diagrams in sync

- Любые изменения должны соответствовать ADR-000/ADR-001/ADR-002 и MVP v1.
- Диаграммы в `docs/diagrams/` — обязательные артефакты, поддерживайте синхронизацию с кодом.
- Safe handling unknown action/payload — обязательное правило совместимости (ADR-001).
- См. `docs/mvp/AI_PLATFORM_MVP_v1.md` и `docs/diagrams/README.md`.

## ADR-first + MVP-first development

- MVP v1 обязателен для всех изменений в платформе.
- Спецификация: `docs/mvp/AI_PLATFORM_MVP_v1.md`.

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
