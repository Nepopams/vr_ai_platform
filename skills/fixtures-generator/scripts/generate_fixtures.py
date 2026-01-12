"""Generate fixtures and update generated documentation sections."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List


ROOT_DIR = Path(__file__).resolve().parents[3]
FIXTURES_DIR = ROOT_DIR / "skills" / "fixtures-generator" / "fixtures"
DOCS_FILE = ROOT_DIR / "docs" / "CONTRACTS.md"
BEGIN_MARKER = "<!-- BEGIN GENERATED EXAMPLES -->"
END_MARKER = "<!-- END GENERATED EXAMPLES -->"


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    payload: dict


def _iso_timestamp() -> str:
    return datetime(2024, 1, 2, 9, 30, tzinfo=timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )


def build_scenarios() -> List[Scenario]:
    timestamp = _iso_timestamp()
    return [
        Scenario(
            name="create_task",
            description="Create a new household task.",
            payload={
                "command_id": "cmd-create-001",
                "user_id": "user-100",
                "timestamp": timestamp,
                "task": {
                    "title": "Schedule plumber visit",
                    "description": "Book a plumber to fix the kitchen sink leak.",
                    "priority": "high",
                },
                "context": {
                    "source": "mobile-app",
                },
            },
        ),
        Scenario(
            name="assign_task",
            description="Assign an existing task to a household member.",
            payload={
                "command_id": "cmd-assign-002",
                "user_id": "user-101",
                "timestamp": timestamp,
                "task": {
                    "title": "Take out recycling",
                    "description": "Assign the recycling pickup to Sam.",
                    "priority": "medium",
                },
                "context": {
                    "assignee": "Sam",
                    "due_date": "2024-01-05",
                },
            },
        ),
        Scenario(
            name="add_shopping_item",
            description="Add an item to the shared shopping list.",
            payload={
                "command_id": "cmd-shop-003",
                "user_id": "user-102",
                "timestamp": timestamp,
                "task": {
                    "title": "Buy oat milk",
                    "description": "Add oat milk to the grocery list for this week.",
                    "priority": "low",
                },
                "context": {
                    "list": "groceries",
                    "quantity": "2 cartons",
                },
            },
        ),
        Scenario(
            name="clarify",
            description="Ask a clarifying question for missing task details.",
            payload={
                "command_id": "cmd-clarify-004",
                "user_id": "user-103",
                "timestamp": timestamp,
                "task": {
                    "title": "Plan weekend errands",
                    "description": "Need confirmation on which stores to visit.",
                    "priority": "medium",
                },
                "context": {
                    "needs_clarification": ["store list", "time window"],
                },
            },
        ),
    ]


def write_fixtures(scenarios: Iterable[Scenario]) -> None:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    for scenario in scenarios:
        path = FIXTURES_DIR / f"{scenario.name}.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump(scenario.payload, handle, indent=2, sort_keys=True)
            handle.write("\n")


def render_generated_examples(scenarios: Iterable[Scenario]) -> str:
    blocks = []
    for scenario in scenarios:
        payload = json.dumps(scenario.payload, indent=2, sort_keys=True)
        blocks.append(
            "\n".join(
                [
                    f"### {scenario.name}",
                    "",
                    scenario.description,
                    "",
                    "```json",
                    payload,
                    "```",
                ]
            )
        )
    return "\n\n".join(blocks)


def update_docs(scenarios: Iterable[Scenario]) -> None:
    content = DOCS_FILE.read_text(encoding="utf-8")
    if BEGIN_MARKER not in content or END_MARKER not in content:
        raise RuntimeError("Documentation markers not found in docs/CONTRACTS.md")

    generated = render_generated_examples(scenarios)
    before, remainder = content.split(BEGIN_MARKER, 1)
    _, after = remainder.split(END_MARKER, 1)
    updated = "".join(
        [
            before,
            BEGIN_MARKER,
            "\n",
            generated,
            "\n",
            END_MARKER,
            after,
        ]
    )
    DOCS_FILE.write_text(updated, encoding="utf-8")


def main() -> None:
    scenarios = build_scenarios()
    write_fixtures(scenarios)
    update_docs(scenarios)


if __name__ == "__main__":
    main()
