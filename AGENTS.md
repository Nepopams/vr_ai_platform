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

- Follow ADR-000 and ADR-001 for all platform evolution decisions.
- Ensure safe handling for unknown `action` values and payload fields.
- `contracts/VERSION` is the source of truth for contract schema versions.

## ADR-first + MVP-first development

- MVP v1 обязателен для всех изменений в платформе.
- Спецификация: `docs/mvp/AI_PLATFORM_MVP_v1.md`.

## Skills

Skills live under `skills/*`. Each skill has its own directory with implementation and metadata, and may include its own Make targets for local execution or validation.

## Canonical Commands

- `make validate_contracts`
- `make run_graph`
- `make run_graph_suite`
- `make audit_decisions`
- `make release_sanity`
