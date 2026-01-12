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

# ADR Compliance

For any changes to `contracts/`, `graphs/`, `agents/`, or `codex/`, development must follow ADR-000 and ADR-001.

- All contract changes must obey semver and backward compatibility rules described in ADR-001.
- If a solution conflicts with an ADR, stop and capture the decision in a new ADR (Draft) instead of pushing code changes.

See `docs/adr/` for the ADR archive. The following ADRs are mandatory:

- ADR-000: AI Platform — Contract-first Intent → Decision Engine (LangGraph)
- ADR-001: Contract versioning & compatibility policy (CommandDTO/DecisionDTO)

# MVP v1 Compliance

Все изменения в `contracts/`, `graphs/`, `agents/`, `skills/` должны соответствовать MVP v1.

- Нельзя добавлять новые intents/actions/поля без:
  - обновления документа MVP (через документ \"MVP v2\"),
  - соблюдения ADR-001 (semver),
  - обновления fixtures/tests.
- Если изменение спорное или затрагивает объём MVP — остановитесь и оформите ADR (Draft), а не делайте \"тихое\" изменение.

См. спецификацию: `docs/mvp/AI_PLATFORM_MVP_v1.md`.
