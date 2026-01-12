# HomeTask AI System

HomeTask AI System is a stateless, contract-driven decision pipeline that powers the HomeTask product. The current implementation runs in mock mode: it accepts a command payload, performs a simulated reasoning flow, and outputs a decision payload that conforms to the published JSON schemas.

## Quick Start

Python 3.11+ is required.

```bash
make run_graph
```

## Repository Structure

- `contracts/` – JSON schemas for command and decision payloads.
- `agents/` – Placeholder for agent implementations.
- `graphs/` – Core reasoning graph/pipeline (mock mode).
- `codex/` – Reasoning log helpers and shared utilities.
- `docs/` – Detailed documentation, including contract definitions.
- `tests/` – Unit tests for the graph and schema validation.

## Common Tasks

```bash
make run_graph
make validate_contracts
make test
```
