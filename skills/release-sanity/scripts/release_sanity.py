import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]

CHECKS = [
    ("contract-checker", BASE_DIR / "skills" / "contract-checker" / "scripts" / "validate_contracts.py"),
    (
        "decision-log-audit",
        BASE_DIR
        / "skills"
        / "decision-log-audit"
        / "scripts"
        / "audit_decision_logs.py",
    ),
    ("graph-sanity", BASE_DIR / "skills" / "graph-sanity" / "scripts" / "run_graph_suite.py"),
]


def run_checks() -> list[str]:
    failures: list[str] = []
    for name, script in CHECKS:
        result = subprocess.run([sys.executable, str(script)], check=False)
        if result.returncode != 0:
            failures.append(name)
    return failures


def main() -> int:
    failures = run_checks()
    if failures:
        print("Release sanity failed for:")
        for name in failures:
            print(f"- {name}")
        return 1

    print("Release sanity checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
