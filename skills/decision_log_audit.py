import runpy
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parent
    / "decision-log-audit"
    / "scripts"
    / "audit_decision_logs.py"
)


def main() -> None:
    runpy.run_path(str(SCRIPT_PATH), run_name="__main__")


if __name__ == "__main__":
    main()
