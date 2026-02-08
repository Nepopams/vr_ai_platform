# Shadow Router Golden-Dataset Analyzer

## Purpose

Offline analysis tool that compares shadow router JSONL logs against a golden dataset with ground truth labels. Produces metrics: intent match rate, entity hit rate, latency percentiles, and error breakdown.

Used to measure shadow LLM router quality vs baseline deterministic intent detection.

## Prerequisites

- Python 3.11+
- No external dependencies (stdlib only)

## Invocation

### Basic usage (reads default paths)
    python scripts/analyze_shadow_router.py

### Custom paths
    python scripts/analyze_shadow_router.py \
      --shadow-log logs/shadow_router.jsonl \
      --golden-dataset skills/graph-sanity/fixtures/golden_dataset.json

### JSON report output
    python scripts/analyze_shadow_router.py --output-json reports/shadow_metrics.json

### Privacy self-test
    python scripts/analyze_shadow_router.py --self-test

## Output Format

### Human-readable (stdout)
    === Shadow Router Analyzer Report ===
    Total records:      150
    Matched records:    14
    Intent match rate:  0.9286
    Entity hit rate:    0.8571
    Latency p50:        45 ms
    Latency p95:        120 ms
    Parse errors:       0
    Error breakdown:
      timeout: 2
      invalid_json: 1

### JSON (--output-json)
    {
      "total_records": 150,
      "matched_records": 14,
      "intent_match_rate": 0.9286,
      "entity_hit_rate": 0.8571,
      "latency_p50": 45,
      "latency_p95": 120,
      "error_breakdown": {"timeout": 2, "invalid_json": 1},
      "parse_errors": 0
    }

### Metrics

| Metric | Description |
|--------|-------------|
| total_records | Total JSONL records read |
| matched_records | Records matched to golden dataset by command_id |
| intent_match_rate | Fraction of matched records where suggested_intent == expected_intent |
| entity_hit_rate | Fraction of matched records where entity keys match expected |
| latency_p50 | 50th percentile latency across ALL records (ms) |
| latency_p95 | 95th percentile latency across ALL records (ms) |
| error_breakdown | Count per error_type (excluding null) |
| parse_errors | JSONL lines that failed to parse |

## Golden Dataset Format

File: `skills/graph-sanity/fixtures/golden_dataset.json`

Each entry:
    {
      "command_id": "cmd-wp000-001",
      "fixture_file": "buy_milk.json",
      "expected_intent": "add_shopping_item",
      "expected_entity_keys": ["item"],
      "notes": "Купи молоко — keyword 'куп'"
    }

## Adding New Entries

1. Create a new command fixture in `skills/graph-sanity/fixtures/commands/<name>.json`
2. Add an entry to `skills/graph-sanity/fixtures/golden_dataset.json` with:
   - `command_id` matching the fixture
   - `expected_intent` based on detect_intent() logic (see graphs/core_graph.py)
   - `expected_entity_keys` — `["item"]` for shopping, `[]` otherwise
3. Run `python scripts/analyze_shadow_router.py --self-test` to verify

## Privacy

The analyzer NEVER outputs raw user text or LLM output.
Only aggregated numeric metrics appear in reports.
Use `--self-test` to verify privacy compliance.
