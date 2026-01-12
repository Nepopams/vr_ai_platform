# Graph Guidelines

## Graph Conventions

- Graphs are built with LangGraph nodes and edges; keep node logic focused and composable.
- Validate inputs and outputs at each node boundary before returning results.
- Ensure returned node outputs conform to the expected contract schema.

## Testing Guidance

- Add or update tests when modifying graph structure or node behavior.
- Prefer running `make run_graph_suite` for regression coverage when touching graph logic.
