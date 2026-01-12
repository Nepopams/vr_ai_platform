import os
import subprocess
import sys
from importlib.util import find_spec
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]

CHECKS = [
    (
        "contract-checker",
        BASE_DIR / "skills" / "contract-checker" / "scripts" / "validate_contracts.py",
    ),
    (
        "decision-log-audit",
        BASE_DIR
        / "skills"
        / "decision-log-audit"
        / "scripts"
        / "audit_decision_logs.py",
    ),
    (
        "graph-sanity",
        BASE_DIR / "skills" / "graph-sanity" / "scripts" / "run_graph_suite.py",
    ),
]


def _should_run_api_sanity() -> tuple[bool, str, bool]:
    if os.getenv("RUN_API_SANITY") == "1":
        if find_spec("fastapi") is None:
            return False, "fastapi не установлен, RUN_API_SANITY=1", True
        return True, "RUN_API_SANITY=1", False
    if find_spec("fastapi") is None:
        return False, "fastapi не установлен", False
    return True, "fastapi доступен", False


def run_checks() -> list[str]:
    failures: list[str] = []
    for name, script in CHECKS:
        result = subprocess.run([sys.executable, str(script)], check=False)
        if result.returncode != 0:
            failures.append(name)
    should_run_api, reason, is_required = _should_run_api_sanity()
    api_script = BASE_DIR / "scripts" / "api_sanity.py"
    if should_run_api:
        result = subprocess.run([sys.executable, str(api_script)], check=False)
        if result.returncode != 0:
            failures.append("api-sanity")
    else:
        print(f"api-sanity skipped: {reason}")
        if is_required:
            failures.append("api-sanity")
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
