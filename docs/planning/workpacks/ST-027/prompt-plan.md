# Codex PLAN Prompt — ST-027: CI Integration for Golden Dataset Quality Report

## Role
You are a senior DevOps/Python developer planning CI integration for a quality evaluation script and writing user documentation.

## Goal
Verify all assumptions before generating the APPLY prompt. **NO file modifications allowed.**

## Allowed commands
- `ls`, `find`
- `cat`, `head`, `tail`
- `rg` / `grep`
- `sed -n`
- `git status`, `git diff` (read-only)

## Forbidden
- Any file edits/writes/moves/deletes
- Any network access
- Package install / system changes
- `git commit`, `git push`, migrations, DB ops

## Context

**Story:** Add quality-eval step to CI and create golden-dataset user guide.

**Current CI** (`.github/workflows/ci.yml`):
- Step 1: `Install dependencies` — `pip install -e ".[dev]"`
- Step 2: `Run tests` — `python -m pytest tests/ -v --tb=short`
- Step 3: `Check schema version` — `python -m skills.schema_bump check`
- Step 4: `Release sanity` — `python3 skills/release-sanity/scripts/release_sanity.py`

**evaluate_golden.py** — at `skills/quality-eval/scripts/evaluate_golden.py`:
- `main()` loads golden dataset, runs all entries through `process_command()`, prints JSON report to stdout.
- Uses `is_llm_policy_enabled()` (defaults to `false`) → stub mode in CI (no LLM).
- Expected to exit 0 (no exceptions raised to caller).

**Golden dataset** — `skills/graph-sanity/fixtures/golden_dataset.json`:
- 22 entries, each referencing a fixture file in `skills/graph-sanity/fixtures/commands/`.

**Existing guide pattern** — `docs/guides/llm-setup.md` (151 lines).

---

## Tasks

### Task 1: Confirm evaluate_golden.py exit behavior
Run:
```
cat skills/quality-eval/scripts/evaluate_golden.py
```
Confirm:
1. `main()` does NOT raise exceptions on evaluation — it catches errors or computes metrics cleanly.
2. Script exits 0 on success (no `sys.exit(1)` or `raise SystemExit` unless errors).
3. Output is valid JSON printed to stdout via `print(json.dumps(...))`.
4. In stub mode (`LLM_POLICY_ENABLED` not set), `llm_metrics` is `None` → report has only `deterministic` key.

### Task 2: Confirm evaluate_golden.py can be invoked standalone
Check:
1. Does the script have `if __name__ == "__main__": main()` guard?
2. Does it set up `sys.path` correctly (REPO_ROOT)?
3. Are all imports available from the project root without special setup?
4. Check if `from graphs.core_graph import detect_intent, extract_items, process_command` works from repo root.

### Task 3: Verify CI YAML structure
```
cat .github/workflows/ci.yml
```
Confirm:
1. Exact indentation level for steps (2 spaces for `- name:`, etc.).
2. Where to insert the new steps (after "Run tests", before "Check schema version").
3. Whether `actions/upload-artifact@v4` is already used anywhere.
4. The `python-version` used (3.11) — confirm `evaluate_golden.py` is compatible.

### Task 4: Confirm golden_dataset.json entry schema
```
head -20 skills/graph-sanity/fixtures/golden_dataset.json
```
List all fields in a golden_dataset.json entry. This is needed for the guide's "Reference" section:
- Required fields: `command_id`, `fixture_file`, `expected_intent`, `expected_entity_keys`, `expected_action`, `difficulty`, `notes`
- Optional fields: `expected_item_count`, `expected_item_names`

### Task 5: Confirm fixture command file structure
```
cat skills/graph-sanity/fixtures/commands/buy_milk.json
```
List the required fields for a command fixture file. This is needed for the guide's "Adding entries" section.

### Task 6: Check docs/guides/ directory
```
ls docs/guides/
```
Confirm:
1. `docs/guides/` exists.
2. `golden-dataset.md` does NOT exist yet (no naming conflict).
3. Note existing guides for style consistency.

### Task 7: Confirm report structure
Check what the actual report JSON looks like by examining `build_report()` in `evaluate_golden.py`:
- Stub mode: `{"deterministic": {...metrics...}}`
- LLM mode: `{"deterministic": {...}, "llm_assisted": {...}, "delta": {...}}`

List the exact metric keys: `intent_accuracy`, `entity_precision`, `entity_recall`, `clarify_rate`, `start_job_rate`, `total_entries`.

---

## STOP-THE-LINE
If any of the following occur, STOP and report:
- `evaluate_golden.py` raises exceptions that would cause non-zero exit in CI
- Script requires special environment setup beyond `pip install -e ".[dev]"`
- Golden dataset or fixture structure incompatible with what's documented
- `docs/guides/` directory doesn't exist
