import json
from pathlib import Path

from graphs.core_graph import process_command, sample_command


BASE_DIR = Path(__file__).resolve().parents[2]
FIXTURE_DIR = BASE_DIR / "skills" / "fixtures-generator" / "fixtures"
README_PATH = BASE_DIR / "skills" / "fixtures-generator" / "README.md"
START_MARKER = "<!-- FIXTURE-DOCS:START -->"
END_MARKER = "<!-- FIXTURE-DOCS:END -->"


def generate_fixtures(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    command_payload = sample_command()
    decision_payload = process_command(command_payload)

    command_path = output_dir / "generated_command.json"
    decision_path = output_dir / "generated_decision.json"

    command_path.write_text(
        json.dumps(command_payload, indent=2) + "\n", encoding="utf-8"
    )
    decision_path.write_text(
        json.dumps(decision_payload, indent=2) + "\n", encoding="utf-8"
    )

    return [command_path, decision_path]


def _render_fixture_summary(paths: list[Path]) -> str:
    lines = ["", "Generated fixture files:"]
    for path in paths:
        lines.append(f"- `{path.relative_to(BASE_DIR)}`")
    lines.append("")
    return "\n".join(lines)


def update_readme(paths: list[Path]) -> None:
    content = README_PATH.read_text(encoding="utf-8")
    if START_MARKER not in content or END_MARKER not in content:
        raise ValueError("README markers not found for fixture docs.")

    before, remainder = content.split(START_MARKER, maxsplit=1)
    _, after = remainder.split(END_MARKER, maxsplit=1)
    summary = _render_fixture_summary(paths)
    updated = f"{before}{START_MARKER}{summary}{END_MARKER}{after}"
    README_PATH.write_text(updated, encoding="utf-8")


def main() -> int:
    paths = generate_fixtures(FIXTURE_DIR)
    update_readme(paths)
    print("Generated fixtures:")
    for path in paths:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
