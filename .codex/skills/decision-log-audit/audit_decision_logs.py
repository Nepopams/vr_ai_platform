from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator


def load_decision_schema(schema_path: Path) -> dict[str, Any]:
    return json.loads(schema_path.read_text(encoding="utf-8"))


def iter_jsonl_entries(path: Path) -> Iterable[tuple[int, dict[str, Any]]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Line {line_number}: invalid JSON ({exc})") from exc
            if not isinstance(payload, dict):
                raise ValueError(f"Line {line_number}: expected object at top level")
            yield line_number, payload


def validate_entry(
    entry: dict[str, Any],
    decision_validator: Draft202012Validator,
    line_number: int,
) -> None:
    errors = sorted(decision_validator.iter_errors(entry), key=lambda e: e.path)
    if errors:
        messages = ", ".join(error.message for error in errors)
        raise ValueError(f"Line {line_number}: decision schema errors: {messages}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate decision log JSONL entries against the decision schema."
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to the decision log JSONL file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    schema_path = (
        Path(__file__).resolve().parents[2]
        / "contracts"
        / "schemas"
        / "decision.schema.json"
    )
    decision_schema = load_decision_schema(schema_path)
    decision_validator = Draft202012Validator(decision_schema)

    try:
        for line_number, entry in iter_jsonl_entries(args.path):
            validate_entry(entry, decision_validator, line_number)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
