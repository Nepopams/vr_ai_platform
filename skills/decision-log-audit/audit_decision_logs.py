from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator


REQUIRED_METADATA_FIELDS = {
    "command_id": str,
    "trace_id": str,
    "prompt_version": str,
    "schema_version": str,
    "latency_ms": int,
}


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


def validate_metadata(metadata: dict[str, Any], line_number: int) -> None:
    for field, expected_type in REQUIRED_METADATA_FIELDS.items():
        if field not in metadata:
            raise ValueError(f"Line {line_number}: metadata missing '{field}'")
        value = metadata[field]
        if expected_type is int:
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError(
                    f"Line {line_number}: metadata '{field}' must be an integer"
                )
        elif not isinstance(value, expected_type):
            raise ValueError(
                f"Line {line_number}: metadata '{field}' must be {expected_type.__name__}"
            )
    if metadata["latency_ms"] < 0:
        raise ValueError(f"Line {line_number}: metadata 'latency_ms' must be >= 0")


def validate_entry(
    entry: dict[str, Any],
    decision_validator: Draft202012Validator,
    line_number: int,
) -> None:
    if "decision" not in entry or "metadata" not in entry:
        raise ValueError(
            f"Line {line_number}: entry must include 'decision' and 'metadata' keys"
        )

    decision = entry["decision"]
    metadata = entry["metadata"]

    if not isinstance(decision, dict):
        raise ValueError(f"Line {line_number}: 'decision' must be an object")
    if not isinstance(metadata, dict):
        raise ValueError(f"Line {line_number}: 'metadata' must be an object")

    errors = sorted(decision_validator.iter_errors(decision), key=lambda e: e.path)
    if errors:
        messages = ", ".join(error.message for error in errors)
        raise ValueError(f"Line {line_number}: decision schema errors: {messages}")

    validate_metadata(metadata, line_number)

    if metadata["command_id"] != decision.get("command_id"):
        raise ValueError(
            f"Line {line_number}: metadata.command_id must match decision.command_id"
        )

    reasoning_log = decision.get("reasoning_log", {})
    if metadata["prompt_version"] != reasoning_log.get("prompt_version"):
        raise ValueError(
            f"Line {line_number}: metadata.prompt_version must match"
            " decision.reasoning_log.prompt_version"
        )

    if metadata["schema_version"] != decision.get("version"):
        raise ValueError(
            f"Line {line_number}: metadata.schema_version must match decision.version"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate decision log JSONL entries against schema and metadata."
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to the decision log JSONL file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    schema_path = Path(__file__).resolve().parents[2] / "contracts" / "schemas" / "decision.schema.json"
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
