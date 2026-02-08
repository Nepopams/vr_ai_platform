# Codex PLAN Prompt — ST-001: Golden-dataset analyzer script

## Role

You are a read-only explorer. You MUST NOT edit, create, or delete any files.
You MUST NOT install packages, run builds, or access the network.

## Allowed commands (whitelist)

- `ls`, `find`
- `cat`, `head`, `tail`
- `rg`, `grep`
- `sed -n`
- `git status`, `git diff`

## Forbidden

- Any file modifications (edit/write/move/delete)
- `pip install`, `npm install`, or any package management
- `git commit`, `git push`, or any git mutations
- Network access of any kind

## STOP-THE-LINE

If you discover something that contradicts the workpack assumptions, STOP and report it. Do not guess or improvise.

---

## Context

We are implementing ST-001: a golden-dataset analyzer script for the shadow router.

**Workpack:** `docs/planning/workpacks/ST-001/workpack.md`

**Deliverables (4 new files, nothing modified):**
1. `skills/graph-sanity/fixtures/golden_dataset.json` — ground truth manifest
2. `scripts/analyze_shadow_router.py` — analyzer script
3. `scripts/README-shadow-analyzer.md` — README
4. `tests/test_analyze_shadow_router.py` — 10 tests

---

## Exploration Tasks

### Task 1: Confirm shadow router JSONL record schema

Read the shadow router code to confirm the exact field names written to JSONL logs.

```bash
cat routers/shadow_router.py | sed -n '150,190p'
cat app/logging/shadow_router_log.py
```

**Report:** List all JSONL record fields with their types. Note which fields are always present vs optional.

### Task 2: Read all 14 fixture command files

List and read all fixture files to confirm command_id values, text content, and structure.

```bash
ls skills/graph-sanity/fixtures/commands/
for f in skills/graph-sanity/fixtures/commands/*.json; do echo "=== $f ==="; cat "$f" | head -5; echo; done
```

**Report:** Table of command_id -> fixture file -> text content (first 40 chars). Confirm exactly 14 files.

### Task 3: Confirm intent detection keywords

Read `graphs/core_graph.py` to confirm the SHOPPING_KEYWORDS and TASK_KEYWORDS used for `detect_intent()`. This determines ground truth labels.

```bash
rg -n "SHOPPING_KEYWORDS|TASK_KEYWORDS|detect_intent" graphs/core_graph.py
cat graphs/core_graph.py | sed -n '1,80p'
```

**Report:** Exact keyword lists and the detect_intent logic (which keyword set is checked first, fallback behavior).

### Task 4: Verify ground truth labels

For each of the 14 fixtures, determine the expected_intent by running the detect_intent logic mentally against the text and keywords from Task 3. Cross-reference with the ground truth table in the workpack.

**Report:** Table of command_id -> text -> matching keyword -> expected_intent -> expected_entity_keys. Flag any discrepancies with the workpack table.

### Task 5: Study reference script pattern

Read the existing `scripts/metrics_agent_hints_v0.py` to understand patterns for:
- CLI argument parsing
- JSONL file iteration
- Percentile calculation
- Privacy self-test
- DANGEROUS_FIELDS set

```bash
cat scripts/metrics_agent_hints_v0.py
```

**Report:** Key patterns to reuse (function signatures, argparse setup, percentile method, self-test approach). Note anything that should differ for the shadow router analyzer.

### Task 6: Check project structure for scripts/ and tests/

Confirm how existing scripts are organized and how tests import from scripts/.

```bash
ls scripts/
ls tests/
rg "sys.path" tests/test_agent_baseline_v0.py tests/test_agent_runner_v0.py | head -10
rg "import.*metrics" tests/ | head -5
```

**Report:** How scripts are imported in tests (sys.path manipulation or other pattern). Note if `scripts/` has an `__init__.py`.

### Task 7: Confirm no existing golden_dataset.json

```bash
find . -name "golden_dataset*" -type f
find . -name "analyze_shadow*" -type f
```

**Report:** Confirm these files do not exist yet.

### Task 8: Check pyproject.toml constraints

```bash
cat pyproject.toml
```

**Report:** Confirm no new dependencies are needed (standard library only). Note the packages.find include list — does `scripts` need to be added?

---

## Expected Output

Produce a numbered report (Task 1 through Task 8) with findings for each task. Include:
- Exact field names, keyword lists, command_ids
- Any discrepancies with the workpack assumptions
- Recommended adjustments (if any)
- STOP-THE-LINE issues (if any)
