# Agent Architecture

The HomeTask AI System is designed to be modular. Agents are lightweight components that can be orchestrated by the core graph.

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
