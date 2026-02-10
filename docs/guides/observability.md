# Observability Guide

This guide documents all observability outputs of the AI Platform: JSONL log files, their schemas, environment variables, and the aggregation script.

## Overview

The platform writes structured JSONL logs (one JSON record per line) for every pipeline execution. All logs:

- Use **newline-delimited JSON** (JSONL) format.
- Include a UTC ISO 8601 `timestamp` field (auto-added by the logging module).
- Create parent directories automatically if they don't exist.
- Are controlled via environment variables for paths and enable/disable.

Log files are located in the `logs/` directory by default.

## Primary Log Types

### 1. Pipeline Latency

Measures total pipeline execution time and per-step breakdown for every `process_command()` call.

**File:** `logs/pipeline_latency.jsonl`
**Module:** `app/logging/pipeline_latency_log.py`

**Record schema:**

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | UTC ISO 8601 (auto-added) |
| `command_id` | string | Command identifier |
| `trace_id` | string | Trace identifier for correlation |
| `total_ms` | float | Total pipeline execution time in milliseconds |
| `steps` | object | Per-step latency breakdown (see below) |
| `llm_enabled` | boolean | Whether LLM policy was enabled for this call |

**Steps breakdown:**

| Step | Description |
|------|-------------|
| `validate_command_ms` | Command validation time |
| `detect_intent_ms` | Intent detection time |
| `registry_ms` | Agent registry annotation gate time |
| `core_logic_ms` | Core decision logic time |
| `validate_decision_ms` | Decision validation time |

**Example record:**

```json
{
  "timestamp": "2026-02-10T12:00:00.000000+00:00",
  "command_id": "cmd-001",
  "trace_id": "trace-abc",
  "total_ms": 15.4,
  "steps": {
    "validate_command_ms": 0.3,
    "detect_intent_ms": 1.2,
    "registry_ms": 0.1,
    "core_logic_ms": 13.5,
    "validate_decision_ms": 0.3
  },
  "llm_enabled": false
}
```

**Environment variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `PIPELINE_LATENCY_LOG_ENABLED` | `true` | Enable/disable latency logging |
| `PIPELINE_LATENCY_LOG_PATH` | `logs/pipeline_latency.jsonl` | Log file path |

---

### 2. Fallback Metrics

Tracks LLM outcomes and fallback events for every pipeline call. Used to measure LLM reliability and fallback rates.

**File:** `logs/fallback_metrics.jsonl`
**Module:** `app/logging/fallback_metrics_log.py`

**Privacy:** NO raw user text or LLM output is logged.

**Record schema:**

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | UTC ISO 8601 (auto-added) |
| `command_id` | string | Command identifier |
| `trace_id` | string | Trace identifier |
| `intent` | string | Detected intent |
| `decision_action` | string | Final decision action |
| `llm_outcome` | string | LLM call result (see values below) |
| `fallback_reason` | string | Reason for fallback (if applicable) |
| `deterministic_used` | boolean | Whether deterministic path was used |
| `llm_latency_ms` | float | LLM call latency (0 if not called) |
| `components` | object | Per-component status summary |

**`llm_outcome` values:**

| Value | Meaning |
|-------|---------|
| `success` | LLM call succeeded and result was used |
| `fallback` | LLM call failed, deterministic fallback used |
| `error` | LLM call raised an error |
| `skipped` | LLM was not called (feature disabled) |
| `deterministic_only` | No LLM path configured |

**Environment variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `FALLBACK_METRICS_LOG_ENABLED` | `true` | Enable/disable fallback logging |
| `FALLBACK_METRICS_LOG_PATH` | `logs/fallback_metrics.jsonl` | Log file path |

---

### 3. Shadow Router

Logs every shadow LLM router execution — parallel LLM calls that do NOT affect decisions.

**File:** `logs/shadow_router.jsonl`
**Module:** `app/logging/shadow_router_log.py`

**Record schema (17 fields):**

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | UTC ISO 8601 (auto-added) |
| `trace_id` | string | Trace identifier |
| `command_id` | string | Command identifier |
| `router_version` | string | Shadow router version |
| `router_strategy` | string | Routing strategy used |
| `status` | string | Result status (`ok`, `error`, `skipped`) |
| `latency_ms` | float | LLM call latency |
| `error_type` | string | Error classification (or `null`) |
| `suggested_intent` | string | LLM-suggested intent |
| `missing_fields` | list | Fields the LLM identified as missing |
| `clarify_question` | string | LLM-suggested clarification question |
| `entities_summary` | object | Extracted entities summary |
| `confidence` | float | LLM confidence score |
| `model_meta` | object | Model metadata (provider, model name) |
| `baseline_intent` | string | Deterministic baseline intent |
| `baseline_action` | string | Deterministic baseline action |
| `baseline_job_type` | string | Deterministic baseline job type |

**Environment variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `SHADOW_ROUTER_ENABLED` | `false` | Enable/disable shadow router |
| `SHADOW_ROUTER_LOG_PATH` | `logs/shadow_router.jsonl` | Log file path |
| `SHADOW_ROUTER_TIMEOUT_MS` | `150` | Timeout for shadow LLM calls |

---

### 4. Assist Mode

Logs LLM assist operations: normalization, entity extraction, and clarify suggestions.

**File:** `logs/assist.jsonl`
**Module:** `app/logging/assist_log.py`

**Record schema (typical fields):**

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | UTC ISO 8601 (auto-added) |
| `step` | string | Assist step name (e.g., `normalizer`, `entities`, `clarify`) |
| `status` | string | Step result status |
| `accepted` | boolean | Whether the assist result was accepted |
| `error_type` | string | Error classification (or `null`) |
| `latency_ms` | float | Step execution time |
| `entities_summary` | object | Extracted entities (if applicable) |
| `missing_fields_count` | integer | Count of missing fields identified |
| `clarify_used` | boolean | Whether clarification was triggered |
| `assist_version` | string | Assist mode version |

Additional fields may appear for agent-hint steps:

| Field | Description |
|-------|-------------|
| `agent_hint_status` | Agent hint call status |
| `agent_hint_latency_ms` | Agent hint call latency |
| `agent_hint_items_count` | Number of items from agent hint |
| `agent_hint_applied` | Whether agent hint was applied |
| `agent_hint_candidates_count` | Number of candidate agents |
| `agent_hint_selected_agent_id` | Selected agent identifier |
| `agent_hint_selected_status` | Selected agent call status |
| `agent_hint_selection_reason` | Why this agent was selected |

**Environment variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `ASSIST_MODE_ENABLED` | `false` | Master switch for assist mode |
| `ASSIST_LOG_PATH` | `logs/assist.jsonl` | Log file path |
| `ASSIST_TIMEOUT_MS` | `200` | Timeout for assist LLM calls |
| `ASSIST_NORMALIZATION_ENABLED` | `false` | Enable normalization step |
| `ASSIST_ENTITY_EXTRACTION_ENABLED` | `false` | Enable entity extraction step |
| `ASSIST_CLARIFY_ENABLED` | `false` | Enable clarify suggestion step |

---

### 5. Partial Trust Risk

Logs partial trust corridor decisions — when LLM results are considered for production use.

**File:** `logs/partial_trust_risk.jsonl`
**Module:** `app/logging/partial_trust_risk_log.py`

**Privacy:** NO raw user text or LLM output is logged.

**Record schema (typical fields):**

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | UTC ISO 8601 (auto-added) |
| `trace_id` | string | Trace identifier |
| `command_id` | string | Command identifier |
| `corridor_intent` | string | Intent allowed in the trust corridor |
| `sample_rate` | float | Current sampling rate |
| `sampled` | boolean | Whether this call was sampled |
| `status` | string | Outcome (`accepted_llm`, `fallback`, `error`) |
| `reason_code` | string | Reason for the decision |
| `latency_ms` | float | LLM call latency |
| `model_meta` | object | Model metadata |
| `baseline_summary` | object | Deterministic baseline result summary |
| `llm_summary` | object | LLM result summary (structure only, no raw text) |
| `diff_summary` | object | Differences between baseline and LLM |

**Environment variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `PARTIAL_TRUST_ENABLED` | `false` | Enable/disable partial trust |
| `PARTIAL_TRUST_RISK_LOG_PATH` | `logs/partial_trust_risk.jsonl` | Log file path |
| `PARTIAL_TRUST_INTENT` | `add_shopping_item` | Allowed intent for trust corridor |
| `PARTIAL_TRUST_SAMPLE_RATE` | `0.01` | Fraction of calls to sample |
| `PARTIAL_TRUST_TIMEOUT_MS` | `200` | Timeout for LLM calls |

---

## Additional Log Types

### Decision Log

Core decision logging for all `DecisionDTO` outcomes.

**File:** `logs/decisions.jsonl` (`DECISION_LOG_PATH`)

Always active. Records every decision produced by `process_command()`.

### Decision Text Log

Optional text logging for debugging.

**File:** `logs/decision_text.jsonl` (`DECISION_TEXT_LOG_PATH`)

**Privacy warning:** Contains raw user text. Controlled by `LOG_USER_TEXT` (default: `false`). Only enable in non-production environments for debugging.

### Agent Run Log

Logs individual agent invocations from the agent registry.

**File:** `logs/agent_run.jsonl` (`AGENT_RUN_LOG_PATH`)

Controlled by `AGENT_RUN_LOG_ENABLED` (default: `false`). Best-effort logging — silently catches exceptions.

### Shadow Agent Diff Log

Logs differences between shadow agent runs and baseline decisions.

**File:** `logs/shadow_agent_diff.jsonl` (`SHADOW_AGENT_DIFF_LOG_PATH`)

Controlled by `SHADOW_AGENT_DIFF_LOG_ENABLED` (default: `false`). Uses privacy-safe summarization — logs structure and counts, not raw values.

---

## Environment Variables Reference

### Primary Logging

| Variable | Default | Description |
|----------|---------|-------------|
| `PIPELINE_LATENCY_LOG_ENABLED` | `true` | Enable pipeline latency logging |
| `PIPELINE_LATENCY_LOG_PATH` | `logs/pipeline_latency.jsonl` | Latency log file path |
| `FALLBACK_METRICS_LOG_ENABLED` | `true` | Enable fallback metrics logging |
| `FALLBACK_METRICS_LOG_PATH` | `logs/fallback_metrics.jsonl` | Fallback metrics log file path |
| `SHADOW_ROUTER_LOG_PATH` | `logs/shadow_router.jsonl` | Shadow router log file path |
| `ASSIST_LOG_PATH` | `logs/assist.jsonl` | Assist mode log file path |
| `PARTIAL_TRUST_RISK_LOG_PATH` | `logs/partial_trust_risk.jsonl` | Partial trust risk log file path |

### Additional Logging

| Variable | Default | Description |
|----------|---------|-------------|
| `DECISION_LOG_PATH` | `logs/decisions.jsonl` | Decision log file path |
| `DECISION_TEXT_LOG_PATH` | `logs/decision_text.jsonl` | Decision text log file path |
| `LOG_USER_TEXT` | `false` | Enable raw user text logging (privacy-sensitive) |
| `AGENT_RUN_LOG_ENABLED` | `false` | Enable agent run logging |
| `AGENT_RUN_LOG_PATH` | `logs/agent_run.jsonl` | Agent run log file path |
| `SHADOW_AGENT_DIFF_LOG_ENABLED` | `false` | Enable shadow agent diff logging |
| `SHADOW_AGENT_DIFF_LOG_PATH` | `logs/shadow_agent_diff.jsonl` | Shadow agent diff log file path |

### Feature Flags (control what generates logs)

| Variable | Default | Description |
|----------|---------|-------------|
| `SHADOW_ROUTER_ENABLED` | `false` | Enable shadow router (generates shadow_router log) |
| `SHADOW_ROUTER_TIMEOUT_MS` | `150` | Shadow router LLM timeout |
| `ASSIST_MODE_ENABLED` | `false` | Enable assist mode (generates assist log) |
| `ASSIST_TIMEOUT_MS` | `200` | Assist mode LLM timeout |
| `PARTIAL_TRUST_ENABLED` | `false` | Enable partial trust (generates risk log) |
| `PARTIAL_TRUST_SAMPLE_RATE` | `0.01` | Partial trust sampling rate |
| `PARTIAL_TRUST_TIMEOUT_MS` | `200` | Partial trust LLM timeout |

---

## Running Aggregation

The aggregation script reads pipeline latency and fallback metrics logs and produces a summary report.

### Command

```bash
source .venv/bin/activate
python3 skills/observability/scripts/aggregate_metrics.py
```

Output is a JSON report printed to stdout. To save:

```bash
python3 skills/observability/scripts/aggregate_metrics.py > metrics_report.json
```

### Input files

The script reads:
- `logs/pipeline_latency.jsonl` — for latency percentiles
- `logs/fallback_metrics.jsonl` — for fallback/error rates

If a file does not exist, the script returns empty statistics (no error).

### Output format

```json
{
  "latency": {
    "all": {
      "count": 100,
      "total_ms": {"p50": 12.3, "p95": 25.1, "p99": 45.6},
      "steps": {
        "validate_command_ms": {"p50": 0.2, "p95": 0.5, "p99": 0.8},
        "detect_intent_ms": {"p50": 1.0, "p95": 2.1, "p99": 3.5},
        "registry_ms": {"p50": 0.1, "p95": 0.2, "p99": 0.3},
        "core_logic_ms": {"p50": 10.5, "p95": 22.0, "p99": 40.0},
        "validate_decision_ms": {"p50": 0.2, "p95": 0.4, "p99": 0.7}
      }
    },
    "with_llm": { "...same structure..." },
    "without_llm": { "...same structure..." }
  },
  "fallback": {
    "count": 100,
    "fallback_rate": 0.05,
    "error_rate": 0.02,
    "success_rate": 0.93,
    "outcome_counts": {
      "success": 93,
      "fallback": 5,
      "error": 2
    }
  },
  "time_range": {
    "first": "2026-02-01T10:00:00+00:00",
    "last": "2026-02-10T15:30:00+00:00"
  }
}
```

### Latency groups

| Group | Description |
|-------|-------------|
| `all` | All pipeline executions |
| `with_llm` | Executions where `llm_enabled=true` |
| `without_llm` | Executions where `llm_enabled` is not `true` |

### Percentile method

Uses linear interpolation between sorted values (same as NumPy's default method).

---

## Interpreting Results

### Healthy latency values

| Metric | Expected range | Action if exceeded |
|--------|---------------|--------------------|
| `total_ms` p50 | < 20 ms | Normal for deterministic pipeline |
| `total_ms` p95 | < 50 ms | Investigate if consistently above |
| `total_ms` p99 | < 100 ms | Check for outlier commands |
| `core_logic_ms` p95 | < 30 ms | Largest step; review if growing |

With LLM enabled, expect higher latency due to network calls. Compare `with_llm` and `without_llm` groups to measure LLM overhead.

### Healthy fallback rates

| Metric | Expected value | Action if exceeded |
|--------|---------------|--------------------|
| `success_rate` | > 0.90 | LLM calls are reliable |
| `fallback_rate` | < 0.10 | Acceptable fallback level |
| `error_rate` | < 0.05 | Investigate if above 5% |

A `fallback_rate` of 1.0 with `deterministic_only` outcomes is normal when LLM is disabled.

### What to look for

- **Rising `error_rate`** — LLM provider may be degraded. Check `SHADOW_ROUTER_LOG_PATH` for `error_type` details.
- **Rising `total_ms` p95** — Pipeline is slowing down. Check per-step breakdown to identify the bottleneck.
- **`fallback_rate` increasing** — LLM responses are being rejected more often. Review shadow router logs for `status=error` patterns.
- **All `deterministic_only`** — LLM is disabled. This is expected when `LLM_POLICY_ENABLED=false`.

---

## Privacy

### What is NOT logged

- **Raw user text** is never written to pipeline_latency, fallback_metrics, partial_trust_risk, or shadow_agent_diff logs.
- **Raw LLM output** is never written to these logs.
- Partial trust and fallback logs contain only structured summaries, flags, and metadata.
- Shadow agent diff uses privacy-safe summarization (structure and counts, not content).

### Opt-in text logging

`LOG_USER_TEXT` (default: `false`) controls whether raw user command text is written to `decision_text.jsonl`. **Only enable in non-production environments for debugging.**

### Safe defaults

All privacy-sensitive features are **disabled by default**:
- `LOG_USER_TEXT=false`
- `PARTIAL_TRUST_ENABLED=false`
- `SHADOW_AGENT_DIFF_LOG_ENABLED=false`
- `AGENT_RUN_LOG_ENABLED=false`
