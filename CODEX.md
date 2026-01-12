# Core Principles

1. **Stateless operation**: The system must not persist data between runs. Every decision is derived strictly from the provided command payload.
2. **Contract adherence**: All inputs and outputs must conform to the JSON schemas in `contracts/schemas/`.
3. **Reasoning logging**: Every decision must include a structured reasoning trace that records command ID, steps, and version metadata.
4. **Versioning from day one**: Decisions and reasoning logs must carry a version identifier (model and prompt versions).
5. **Deterministic mock mode**: The initial pipeline simulates reasoning without any external LLM calls.
