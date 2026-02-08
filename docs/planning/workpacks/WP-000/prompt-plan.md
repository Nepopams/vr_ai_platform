# WP-000 — PLAN Prompt (Read-Only Exploration)

> **Mode: PLAN ONLY**
> NO edits. NO file writes. NO git commits. NO network access. NO package installs.
> If any required input is missing — STOP and report it.

---

## Anchor Block

Read these files FIRST (Sources of Truth):

```
cat docs/planning/workpacks/WP-000/workpack.md
cat docs/planning/workpacks/WP-000/checklist.md
cat docs/_governance/dor.md
cat docs/_governance/dod.md
cat .claude/rules/planning.md
```

---

## Mission

You are exploring the repository to prepare an implementation plan for **WP-000: Bootstrap Pipeline Readiness**. This workpack adds:

1. **Makefile `setup-dev` target** + README update
2. **GitHub Actions CI workflow** (pytest + contract_checker + schema_bump + graph_sanity)
3. **12 new golden dataset fixtures** in `skills/graph-sanity/fixtures/commands/`
4. **Shared pytest fixtures** in `tests/conftest.py`
5. **4 planning templates** in `docs/planning/_templates/`
6. **Initiatives index** + **ADR index update** + **ADR-005 duplicate deletion**

You must NOT modify any files. Only read and report findings.

---

## Allowed Commands (whitelist)

```
ls, find
cat
rg, grep
sed -n, head, tail
git status, git diff
```

**FORBIDDEN:** edit, write, mkdir, rm, mv, cp, git commit, git push, pip, python (except for read-only checks below)

---

## Exploration Tasks

Execute these tasks IN ORDER. For each task, report findings clearly.

### Task 1: Verify dev environment setup

```bash
# Current Makefile targets
cat Makefile

# Current pyproject.toml (deps, python version)
cat pyproject.toml

# Current README
cat README.md

# Check if setup-dev target already exists
grep -n "setup-dev" Makefile
```

**Report:**
- Does `setup-dev` target exist? (Expected: no)
- What dependencies are in `[project.optional-dependencies].dev`? (Expected: only pytest)
- Are there any other dev tools (ruff, mypy, flake8) configured? (Expected: no)

---

### Task 2: Verify CI pipeline prerequisites

```bash
# Check for existing CI
ls -la .github/workflows/ 2>/dev/null || echo "NO .github/workflows/ directory"

# Check if GitHub Actions is suitable (any .github/ at all?)
ls -la .github/ 2>/dev/null || echo "NO .github/ directory"

# Verify the 4 CI steps would work locally
# (DO NOT run them — just check they exist)
grep -n "def main" skills/contract_checker.py
grep -n "def main" skills/schema_bump.py
grep -n "def main" skills/graph_sanity.py

# Check how graph_sanity finds fixtures
cat skills/graph-sanity/scripts/run_graph_suite.py
```

**Report:**
- Does `.github/` directory exist? (Expected: no)
- Are all 4 skills importable as `python -m skills.<name>`? List entry points.
- Does `run_graph_suite.py` auto-discover fixtures via `FIXTURE_DIR.glob("*.json")`? (Expected: yes)
- Any special fixture naming conventions? (Expected: any `*.json` in commands/)

---

### Task 3: Audit existing golden dataset and fixture format

```bash
# List existing fixtures
ls -la skills/graph-sanity/fixtures/commands/

# Read each fixture to understand format
cat skills/graph-sanity/fixtures/commands/grocery_run.json
cat skills/graph-sanity/fixtures/commands/weekly_chores.json

# Check command schema for required fields
cat contracts/schemas/command.schema.json

# Also check contract-checker fixtures for format reference
ls skills/contract-checker/fixtures/
cat skills/contract-checker/fixtures/valid_command_add_shopping_item.json
cat skills/contract-checker/fixtures/valid_command_create_task.json
cat skills/contract-checker/fixtures/valid_command_ambiguous.json
```

**Report:**
- List all existing fixture files (both graph-sanity and contract-checker)
- What fields are REQUIRED by command.schema.json?
- What `capabilities` values are valid?
- What `context.household` fields are required vs optional?
- What command_id naming convention is used?
- Are there any fixtures with English text? With empty text?

---

### Task 4: Understand intent detection keywords

```bash
# Find intent detection logic
cat graphs/core_graph.py | head -100

# Find keyword lists
rg "SHOPPING_KEYWORDS|TASK_KEYWORDS|clarify" graphs/core_graph.py

# Find extract_item_name logic
rg "def extract_item_name|def detect_intent" graphs/core_graph.py
```

**Report:**
- List exact keywords for `add_shopping_item` intent
- List exact keywords for `create_task` intent
- What happens when no keywords match? (Expected: `clarify_needed`)
- How does `extract_item_name` work? (pattern/regex)
- Will fixtures with English text ("Buy apples") trigger shopping intent? Check if "buy" is in keywords.
- Will empty/whitespace text trigger clarify? Or will it crash?

---

### Task 5: Audit existing test structure

```bash
# List all test files
ls tests/

# Check if conftest.py exists
ls tests/conftest.py 2>/dev/null || echo "NO conftest.py"

# Check how existing tests build commands (to avoid conflicts)
head -40 tests/test_contracts.py
head -40 tests/test_graph_execution.py
head -40 tests/test_router_strategy.py

# Check for existing fixture patterns in tests
rg "def.*command|sample_command|FIXTURE" tests/ --type py | head -30
```

**Report:**
- Does `conftest.py` exist? (Expected: no)
- How do existing tests construct test commands? (inline dicts? helper functions? imported fixtures?)
- List any `@pytest.fixture` or `sample_command()` patterns found
- Will adding conftest.py with new fixture names conflict with anything?
- Which test files load schemas themselves vs could benefit from shared fixtures?

---

### Task 6: Audit planning templates requirements

```bash
# Check if templates directory exists
ls docs/planning/_templates/ 2>/dev/null || echo "NO _templates/ directory"

# Read governance rules for required sections
cat .claude/rules/planning.md

# Check DoR for story requirements
cat docs/_governance/dor.md

# Check an existing workpack for format reference
cat docs/planning/workpacks/WP-000/workpack.md | head -50
```

**Report:**
- Does `_templates/` exist? (Expected: no)
- List all MANDATORY sections from `.claude/rules/planning.md` for each template type
- What flags does DoR require? (contract_impact, adr_needed, diagrams_needed, etc.)
- Are there existing epic/story files anywhere to use as format reference?

---

### Task 7: Audit indexes and ADR state

```bash
# Current ADR index
cat docs/_indexes/adr-index.md

# Check for initiatives index
ls docs/_indexes/
cat docs/_indexes/contracts-index.md | head -20
cat docs/_indexes/diagrams-index.md | head -20

# List all initiative files
ls docs/planning/initiatives/

# Check ADR-005 duplicate situation
ls -la docs/adr/ADR-005*

# Check if duplicate ADR-005 is referenced anywhere
rg "Внутренний контракт агента v0 как ABI" docs/ --type md
rg "ADR-005" docs/ --type md | head -20
rg "ADR-005" . --type md --type py --glob '!.venv/**' | head -20
```

**Report:**
- What ADRs are currently in `docs/_indexes/adr-index.md`? (Expected: legacy ones only, no 000-005)
- Does `initiatives-index.md` exist? (Expected: no)
- List exact filenames of both ADR-005 files
- Where is the duplicate ADR-005 referenced? (to assess deletion safety)
- What format do existing index tables use? (columns, links)

---

### Task 8: Verify invariants

```bash
# Contract schemas must not change
cat contracts/VERSION
head -5 contracts/schemas/command.schema.json
head -5 contracts/schemas/decision.schema.json

# Router default
rg "DECISION_ROUTER_STRATEGY" routers/ --type py | head -5

# Feature flags defaults
rg "SHADOW_ROUTER_ENABLED|ASSIST_MODE_ENABLED|PARTIAL_TRUST_ENABLED" routers/ --type py | head -10

# Git status
git status
```

**Report:**
- `contracts/VERSION` value (Expected: `2.0.0`)
- Default router strategy (Expected: `v1`)
- Default feature flag values (Expected: all disabled)
- Git status clean? Any uncommitted changes?

---

## Output Format

After completing all 8 tasks, produce a single summary:

```
## PLAN Findings — WP-000

### Files to Create (confirmed paths)
- [list exact paths]

### Files to Modify (confirmed paths + what to change)
- [list exact paths + specific changes]

### Files to Delete (confirmed paths)
- [list exact paths + safety check result]

### Discovered Risks / Adjustments
- [any deviations from workpack plan]
- [any conflicts or edge cases found]
- [any missing info or blockers]

### Fixture Design Notes
- [command_id convention to use]
- [keywords that will/won't match per intent]
- [edge cases: empty text, English text, multi-intent]

### conftest.py Design Notes
- [existing fixture patterns to avoid conflicts]
- [which tests would benefit from shared fixtures]

### Ready for APPLY?
YES / NO (with blockers if NO)
```

---

## STOP-THE-LINE

If you encounter ANY of these situations, STOP immediately and report:
- A file listed in "Files to Create" already exists
- A file listed in "Forbidden" zone shows recent modifications
- `contracts/VERSION` != `2.0.0`
- Existing tests reference a fixture name we plan to use in conftest.py
- Intent detection logic has changed from what workpack assumes
- Any other deviation from the workpack plan
