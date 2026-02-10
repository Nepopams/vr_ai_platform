# Golden Dataset Guide

This guide covers how to use the golden dataset for quality evaluation of the AI Platform pipeline.

## What is the Golden Dataset

The golden dataset is a curated set of 22 test commands with expected outcomes. It verifies that the deterministic pipeline correctly detects intents, extracts entities, and produces the right actions.

**Location:** `skills/graph-sanity/fixtures/golden_dataset.json`
**Fixtures:** `skills/graph-sanity/fixtures/commands/*.json`
**Evaluation script:** `skills/quality-eval/scripts/evaluate_golden.py`

## Running Locally

### Deterministic mode (default)

```bash
source .venv/bin/activate
python3 skills/quality-eval/scripts/evaluate_golden.py
```

Output is a JSON report printed to stdout. To save to a file:

```bash
python3 skills/quality-eval/scripts/evaluate_golden.py > quality_eval_report.json
```

### With LLM comparison

To compare deterministic vs LLM-assisted results, enable the LLM policy:

```bash
export LLM_POLICY_ENABLED=true
export LLM_API_KEY=sk-your-key
export LLM_BASE_URL=https://api.openai.com/v1
python3 skills/quality-eval/scripts/evaluate_golden.py
```

See `docs/guides/llm-setup.md` for full LLM configuration.

## Adding Entries

### Step 1: Create a command fixture

Create a new JSON file in `skills/graph-sanity/fixtures/commands/`:

```json
{
  "command_id": "cmd-gd-NNN",
  "user_id": "user-test",
  "timestamp": "2026-01-01T10:00:00+00:00",
  "text": "Your command text here",
  "capabilities": [
    "start_job",
    "propose_create_task",
    "propose_add_shopping_item",
    "clarify"
  ],
  "context": {
    "household": {
      "household_id": "house-test",
      "members": [{"user_id": "user-test", "display_name": "Test"}],
      "shopping_lists": [{"list_id": "list-1", "name": "Продукты"}]
    },
    "defaults": {"default_list_id": "list-1"}
  }
}
```

Required fields: `command_id`, `user_id`, `timestamp`, `text`, `capabilities`, `context`.

### Step 2: Add entry to the golden dataset

Add an entry to `skills/graph-sanity/fixtures/golden_dataset.json`:

```json
{
  "command_id": "cmd-gd-NNN",
  "fixture_file": "your_fixture.json",
  "expected_intent": "add_shopping_item",
  "expected_entity_keys": ["item"],
  "expected_item_count": 1,
  "expected_item_names": ["молоко"],
  "expected_action": "propose_add_shopping_item",
  "difficulty": "easy",
  "notes": "Description of what this entry tests"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `command_id` | Yes | Unique identifier (match fixture file) |
| `fixture_file` | Yes | Filename in `commands/` directory |
| `expected_intent` | Yes | One of: `add_shopping_item`, `create_task`, `clarify_needed` |
| `expected_entity_keys` | Yes | List of entity keys (e.g., `["item"]` or `[]`) |
| `expected_action` | Yes | One of: `propose_add_shopping_item`, `propose_create_task`, `clarify` |
| `difficulty` | Yes | `easy`, `medium`, or `hard` |
| `notes` | Yes | Human-readable description |
| `expected_item_count` | No | Number of items (shopping commands only) |
| `expected_item_names` | No | List of expected item names (shopping commands only) |

### Step 3: Verify

Run the evaluation to confirm your entry works:

```bash
python3 skills/quality-eval/scripts/evaluate_golden.py
```

Also run the graph-sanity suite to ensure the new fixture passes schema validation:

```bash
python3 skills/graph-sanity/scripts/run_graph_suite.py
```

## Interpreting the Report

### Report structure

**Deterministic mode** (default):

```json
{
  "deterministic": {
    "intent_accuracy": 0.8636,
    "entity_precision": 0.9286,
    "entity_recall": 0.9286,
    "clarify_rate": 0.2273,
    "start_job_rate": 0.7727,
    "total_entries": 22
  }
}
```

**LLM comparison mode** (with `LLM_POLICY_ENABLED=true`):

```json
{
  "deterministic": { ... },
  "llm_assisted": { ... },
  "delta": {
    "intent_accuracy": 0.05,
    "entity_precision": 0.02,
    ...
  }
}
```

### Metrics explained

| Metric | What it measures | Good value |
|--------|-----------------|------------|
| `intent_accuracy` | Fraction of commands with correct intent detection | Higher is better (target: > 0.85) |
| `entity_precision` | Of extracted items, how many are correct | Higher is better (target: > 0.90) |
| `entity_recall` | Of expected items, how many were extracted | Higher is better (target: > 0.90) |
| `clarify_rate` | Fraction of commands that trigger clarification | Lower is better for well-formed commands |
| `start_job_rate` | Fraction of commands that produce a job action | Higher is better (= 1 - clarify_rate) |
| `total_entries` | Number of evaluated commands | Informational |

### Current baseline (22 entries)

- `intent_accuracy`: 86.4%
- `entity_precision`: 92.9%
- `entity_recall`: 92.9%
- `clarify_rate`: 22.7%
- `start_job_rate`: 77.3%

## CI Integration

The CI pipeline runs quality evaluation automatically on every push and pull request.

### What happens in CI

1. Tests run first (`python -m pytest`).
2. Quality evaluation runs in **stub mode** (no real LLM — `LLM_POLICY_ENABLED` is not set in CI).
3. Report is saved as `quality_eval_report.json`.
4. Report is uploaded as a CI artifact named `quality-eval-report`.

### Accessing the report

1. Go to the GitHub Actions run page.
2. Scroll to "Artifacts" section.
3. Download `quality-eval-report`.

### Failure behavior

- If the evaluation script fails (e.g., broken fixture file), the CI step fails with a non-zero exit code.
- The report artifact is uploaded with `if: always()`, so partial reports are available even on failure.
- Quality evaluation does **not** enforce thresholds — it is report-only. A drop in metrics does not block the build.
