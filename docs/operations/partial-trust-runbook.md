# Partial Trust Corridor — Rollout Runbook

Operational guide for enabling, tuning, monitoring, and rolling back the partial trust corridor.

---

## Prerequisites

Before enabling partial trust in any environment, verify:

- [ ] **ADR-004 Accepted** — `docs/adr/ADR-004-partial-trust-corridor.md` status is "Accepted"
- [ ] **Initiative ACs verified** — `docs/planning/epics/EP-003/verification-report.md` shows all 4 ACs PASS
- [ ] **Regression analyzer available** — `scripts/analyze_partial_trust.py` exists and `--self-test` passes
- [ ] **LLM policy configured** — `llm_policy/llm-policy.yaml` contains `partial_trust_shopping` task with `partial_trust` and `reliable` profiles
- [ ] **LLM_POLICY_ENABLED=true** — required for LLM candidate generation
- [ ] **Risk-log directory writable** — `logs/` directory exists and is writable by the application process
- [ ] **Existing tests pass** — `python3 -m pytest tests/ -v` shows all tests passing

---

## Configuration Reference

All configuration is via environment variables. No code changes required for rollout.

| Variable | Type | Default | Description | Valid Range |
|----------|------|---------|-------------|-------------|
| `PARTIAL_TRUST_ENABLED` | bool | `false` | Master switch. Enables/disables the entire corridor. | `true`, `false`, `1`, `yes` |
| `PARTIAL_TRUST_INTENT` | string | `add_shopping_item` | Intent for the corridor. Must be in allowlist. | Only `add_shopping_item` (hardcoded allowlist) |
| `PARTIAL_TRUST_SAMPLE_RATE` | float | `0.01` | Fraction of matching commands where LLM replaces baseline. | `0.0` to `1.0` (clamped) |
| `PARTIAL_TRUST_TIMEOUT_MS` | int | `200` | LLM candidate generation timeout in milliseconds. | `> 0` (0 or invalid → disabled) |
| `PARTIAL_TRUST_PROFILE_ID` | string | `""` (empty) | LLM policy profile override. Empty → uses default profile. | Any valid profile from llm-policy.yaml |
| `PARTIAL_TRUST_RISK_LOG_PATH` | string | `logs/partial_trust_risk.jsonl` | Path to JSONL risk-log file. | Any writable path |
| `LLM_POLICY_ENABLED` | bool | (see llm_policy) | Must be `true` for LLM candidate generation to work. | `true`, `false` |

### Key behaviors when disabled

When `PARTIAL_TRUST_ENABLED=false` (default):
- `partial_trust_sample_rate()` returns `0.0`
- `partial_trust_timeout_ms()` returns `0`
- `partial_trust_profile_id()` returns `None`
- `_maybe_apply_partial_trust()` returns `None` immediately (baseline used)
- No LLM calls are made, no risk-log entries are written

---

## Rollout Plan

### Stage 1: Initial canary (0.01 = 1%)

**Duration:** minimum 3 days

**Enable:**
```bash
export PARTIAL_TRUST_ENABLED=true
export PARTIAL_TRUST_SAMPLE_RATE=0.01
export PARTIAL_TRUST_TIMEOUT_MS=200
export LLM_POLICY_ENABLED=true
# Restart application
```

**Monitor daily:**
```bash
python3 scripts/analyze_partial_trust.py --risk-log logs/partial_trust_risk.jsonl
```

**Go criteria for Stage 2:**
- `error_rate` < 0.05
- `intent_mismatch_rate` < 0.10
- `latency_p95` < 500 ms
- No user-reported incidents
- At least 50 sampled records

**No-Go → rollback if:**
- `error_rate` > 0.10
- Any user-reported incident linked to partial trust
- LLM provider outage

### Stage 2: Expanded canary (0.05 = 5%)

**Duration:** minimum 5 days

**Change sampling rate:**
```bash
export PARTIAL_TRUST_SAMPLE_RATE=0.05
# Restart application
```

**Go criteria for Stage 3:**
- `error_rate` < 0.03
- `intent_mismatch_rate` < 0.05
- `latency_p95` < 400 ms
- Stable `acceptance_rate` (no sudden drops)
- At least 200 sampled records

**No-Go → rollback if:**
- `error_rate` > 0.05
- `intent_mismatch_rate` > 0.10
- Regression vs Stage 1 metrics

### Stage 3: Target rate (0.10 = 10%)

**Duration:** minimum 7 days

**Change sampling rate:**
```bash
export PARTIAL_TRUST_SAMPLE_RATE=0.10
# Restart application
```

**Steady-state criteria:**
- `error_rate` < 0.02
- `intent_mismatch_rate` < 0.05
- Stable `acceptance_rate`
- `latency_p95` < 300 ms

**After 7 days at Stage 3:** evaluate whether to maintain 0.10 or adjust based on product metrics.

---

## Monitoring Checklist

Run the analyzer daily (or more frequently during rollout):

```bash
python3 scripts/analyze_partial_trust.py \
  --risk-log logs/partial_trust_risk.jsonl \
  --output-json logs/partial_trust_report.json
```

### Metrics to watch

| Metric | Source | Alarm Threshold | Action |
|--------|--------|-----------------|--------|
| `error_rate` | Analyzer report | > 0.05 | Rollback immediately |
| `intent_mismatch_rate` | Analyzer report | > 0.10 | Investigate, reduce sample rate |
| `entity_key_mismatch_rate` | Analyzer report | > 0.20 | Investigate acceptance rules |
| `latency_p95` | Analyzer report | > 500 ms | Reduce timeout or sample rate |
| `acceptance_rate` | Analyzer report | Sudden drop > 20% | Investigate LLM provider |
| Risk-log file growth | `wc -l logs/partial_trust_risk.jsonl` | Stops growing | Check application health |
| Risk-log recency | `tail -1 logs/partial_trust_risk.jsonl` | > 1 hour stale | Check application health |

### Health check commands

```bash
# Risk-log exists and is being written
ls -la logs/partial_trust_risk.jsonl

# Last entry timestamp
tail -1 logs/partial_trust_risk.jsonl | python3 -c "import sys,json; print(json.load(sys.stdin).get('timestamp','N/A'))"

# Quick status count
python3 -c "
import json
from collections import Counter
c = Counter()
for line in open('logs/partial_trust_risk.jsonl'):
    c[json.loads(line).get('status','')] += 1
for k,v in sorted(c.items()): print(f'  {k}: {v}')
"
```

---

## Rollback Procedure

### Immediate kill-switch (< 1 minute)

```bash
export PARTIAL_TRUST_ENABLED=false
# Restart application
```

**Verify kill-switch took effect:**
```bash
# Wait 1 minute, then check that new entries have status="skipped" or no new entries
tail -5 logs/partial_trust_risk.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    r = json.loads(line.strip())
    print(f\"{r.get('timestamp','')} status={r.get('status','')} reason={r.get('reason_code','')}\")
"
```

After disabling, you should see no new `accepted_llm` or `fallback_deterministic` entries.

### Reduce sampling rate (alternative to full disable)

If the issue is volume-related, reduce instead of disabling:

```bash
export PARTIAL_TRUST_SAMPLE_RATE=0.01  # or 0.0 for effective disable
# Restart application
```

### Post-rollback analysis

After rollback, analyze what happened:

```bash
# Full report for the period
python3 scripts/analyze_partial_trust.py \
  --risk-log logs/partial_trust_risk.jsonl \
  --output-json logs/rollback_analysis.json

# Check error patterns
python3 -c "
import json
from collections import Counter
c = Counter()
for line in open('logs/partial_trust_risk.jsonl'):
    r = json.loads(line)
    if r.get('status') == 'error':
        c[r.get('reason_code','')] += 1
for k,v in sorted(c.items()): print(f'  {k}: {v}')
"
```

---

## Troubleshooting

### No risk-log entries after enabling

1. Check `PARTIAL_TRUST_ENABLED` is `true` (case-insensitive)
2. Check `LLM_POLICY_ENABLED` is `true`
3. Check `PARTIAL_TRUST_SAMPLE_RATE` > 0
4. Check application can write to the log path
5. Check incoming commands have intent `add_shopping_item`

### All entries show status="skipped"

1. `reason_code="corridor_mismatch"` → incoming commands don't match the corridor intent
2. `reason_code="capability_mismatch"` → command doesn't have `start_job` capability
3. `reason_code="policy_disabled"` → LLM policy not configured or `LLM_POLICY_ENABLED=false`

### High error_rate

1. Check LLM provider health (API keys, quotas, network)
2. Check `PARTIAL_TRUST_TIMEOUT_MS` is sufficient (default 200ms)
3. Review `reason_code` breakdown for specific error types

### High intent_mismatch_rate

1. Review acceptance rules in `routers/partial_trust_acceptance.py`
2. Check if LLM model quality has degraded
3. Consider reducing sample rate while investigating

---

## References

| Document | Path |
|----------|------|
| ADR-004 (Partial Trust Corridor) | `docs/adr/ADR-004-partial-trust-corridor.md` |
| Verification Report | `docs/planning/epics/EP-003/verification-report.md` |
| Analyzer Script | `scripts/analyze_partial_trust.py` |
| Analyzer README | `scripts/README-partial-trust-analyzer.md` |
| Config Module | `routers/partial_trust_config.py` |
| Acceptance Rules | `routers/partial_trust_acceptance.py` |
| Risk-Log Module | `app/logging/partial_trust_risk_log.py` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-partial-trust.md` |
