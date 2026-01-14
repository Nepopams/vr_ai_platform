from __future__ import annotations

import json
import sys
from pathlib import Path

from agent_registry.v0_loader import AgentRegistryV0Loader
from agent_registry.v0_runner import run


def _load_input(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python scripts/run_agent_v0.py <agent_id> <input_json_path>")
        return 1

    agent_id = sys.argv[1]
    input_path = Path(sys.argv[2])
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return 1

    registry = AgentRegistryV0Loader.load()
    agent = next((spec for spec in registry.agents if spec.agent_id == agent_id), None)
    if agent is None:
        print(f"Agent not found: {agent_id}")
        return 1

    agent_input = _load_input(input_path)
    result = run(agent, agent_input, trace_id=agent_input.get("trace_id"))
    print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
