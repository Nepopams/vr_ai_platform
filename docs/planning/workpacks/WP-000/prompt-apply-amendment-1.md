# WP-000 — APPLY Amendment #1: Fix PEP 668 (venv)

> **Context:** Codex STOP-THE-LINE on Step 1 — `pip install` fails with
> `externally-managed-environment` (PEP 668) on modern Ubuntu/Debian.
> **Resolution:** Use virtual environment. `.venv/` is already in `.gitignore`.

> **Mode: APPLY** — Continue implementation from where you stopped.
> Steps 2-6 from the original prompt-apply.md remain unchanged.

---

## What was already done (DO NOT redo)

- Makefile: `setup-dev` target added, `.PHONY` updated
- README.md: Quick Start updated

## What needs fixing (Step 1 amendment)

### 1a. Fix `Makefile` — replace `setup-dev` target

Replace the current `setup-dev` target:

```makefile
setup-dev:
	pip install -e ".[dev]"
```

With venv-aware version:

```makefile
VENV := .venv
PYTHON := $(VENV)/bin/python

setup-dev:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -e ".[dev]"
	@echo ""
	@echo "Virtualenv ready. Activate with:"
	@echo "  source $(VENV)/bin/activate"
```

Also update `setup` target the same way:

```makefile
setup:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -e .
	@echo ""
	@echo "Virtualenv ready. Activate with:"
	@echo "  source $(VENV)/bin/activate"
```

Add `VENV` and `PYTHON` variables at the TOP of Makefile (after `.PHONY` line, before any targets).

### 1b. Fix `README.md` — update Quick Start

Replace the current Quick Start block:

```markdown
## Quick Start

Python 3.11+ is required.

```bash
make setup-dev              # create venv + install dev dependencies
source .venv/bin/activate   # activate virtualenv
make test                   # run full test suite
make test-core              # run minimal suite (no API deps)
make run_graph              # run core graph with sample command
```
```

### Verify Step 1 (amended):

```bash
make setup-dev                             # creates .venv/, installs deps
source .venv/bin/activate                  # activate
python -m pytest tests/test_contracts.py -v   # must pass
```

---

## Continue with Steps 2-6

After Step 1 verification passes, continue with **Steps 2 through 6 EXACTLY as specified in `prompt-apply.md`**. No changes to those steps.

**Important:** All `python` and `python -m pytest` commands in steps 2-6 verification blocks assume the venv is activated (`source .venv/bin/activate`). If running without activation, prefix with `.venv/bin/python`.

The CI workflow (Step 2) does NOT need venv — GitHub Actions `pip install` works without PEP 668 restrictions.

---

## STOP-THE-LINE (same rules as original)

If ANY of these occur, STOP and report:
- Any existing test fails after your changes
- A new fixture causes errors
- You need to modify a file in the FORBIDDEN list
- Any other deviation from the plan
