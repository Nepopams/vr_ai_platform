# Partial Trust Risk-Log Analyzer

Regression metrics analyzer for the partial trust corridor risk-log.

## Purpose

Reads partial trust risk-log JSONL and computes aggregated metrics to assess whether the partial trust corridor is improving or degrading decision quality compared to baseline.

## Prerequisites

- Python 3.10+
- No external dependencies (uses only stdlib)

## Usage

```bash
# Basic usage (reads default log path)
python3 scripts/analyze_partial_trust.py --risk-log logs/partial_trust_risk.jsonl

# With JSON output
python3 scripts/analyze_partial_trust.py --risk-log logs/partial_trust_risk.jsonl --output-json report.json

# Privacy self-test
python3 scripts/analyze_partial_trust.py --self-test
```

## Output Format

### Human-readable (stdout)

```
=== Partial Trust Risk-Log Analyzer Report ===
Total records:           150
Sampled records:         15
Acceptance rate:         0.6000
Intent mismatch rate:    0.0667
Entity key mismatch:     0.1333
Error rate:              0.0067
Latency p50:             18 ms
Latency p95:             45 ms
Parse errors:            0
Status breakdown:
  accepted_llm: 9
  error: 1
  fallback_deterministic: 6
  not_sampled: 134
Reason code breakdown:
  accepted: 9
  low_confidence: 4
  corridor_mismatch: 1
  not_sampled: 134
  RuntimeError: 1
```

### JSON output (--output-json)

All metric fields:

| Field | Type | Description |
|-------|------|-------------|
| `total_records` | int | Total JSONL records processed |
| `sampled_records` | int | Records where `sampled=true` |
| `status_breakdown` | dict | Count per status: accepted_llm, fallback_deterministic, not_sampled, skipped, error |
| `reason_code_breakdown` | dict | Count per reason_code |
| `acceptance_rate` | float\|null | accepted_llm / (accepted_llm + fallback_deterministic). null if no decisions. |
| `intent_mismatch_rate` | float\|null | Fraction of records with diff_summary where intent_mismatch=true. null if no diff_summary records. |
| `entity_key_mismatch_rate` | float\|null | Fraction of records with diff_summary where entity_key_mismatch=true. null if no diff_summary records. |
| `latency_p50` | int\|null | p50 latency (ms) over records with latency_ms. null if no latency data. |
| `latency_p95` | int\|null | p95 latency (ms). null if no latency data. |
| `error_rate` | float\|null | error_count / total_records. null if total_records=0. |
| `parse_errors` | int | Number of malformed JSONL lines skipped |

## Interpreting Results

### Key metrics

- **acceptance_rate**: Fraction of sampled decisions where LLM replaced baseline. Higher = LLM more aggressive. Target: stable or increasing over rollout stages.
- **intent_mismatch_rate**: How often LLM disagrees with baseline on intent. Should be low (<0.05) for safe corridor.
- **entity_key_mismatch_rate**: How often LLM extracts different entity keys. Some mismatch is expected (LLM may extract more).
- **error_rate**: Should be <0.01. High error rate → investigate LLM provider issues.
- **latency_p95**: Should be within timeout budget (default 200ms). Increasing p95 → consider reducing timeout.

### Decision criteria for sampling progression

| Stage | Sample Rate | Min Duration | Go Criteria | No-Go Criteria |
|-------|------------|-------------|-------------|----------------|
| Stage 1 | 0.01 | 3 days | error_rate < 0.05, intent_mismatch < 0.10 | error_rate > 0.10 or any incident |
| Stage 2 | 0.05 | 5 days | error_rate < 0.03, intent_mismatch < 0.05 | error_rate > 0.05 |
| Stage 3 | 0.10 | 7 days | error_rate < 0.02, stable acceptance_rate | Any regression vs Stage 2 |

### Rollback triggers

- error_rate > 0.05 → immediately reduce sample rate or disable
- intent_mismatch_rate > 0.10 → investigate and reduce
- latency_p95 > 500ms → reduce timeout or disable

## Privacy

The analyzer processes only aggregated fields (status, reason_code, latency_ms, diff_summary booleans). It never reads or outputs raw user text or LLM output, even if present in JSONL records. Run `--self-test` to verify.
