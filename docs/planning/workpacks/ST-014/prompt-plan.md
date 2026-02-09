# Codex PLAN Prompt — ST-014: Clarify Golden Dataset Ground Truth and Quality Measurement

## Role

You are a read-only exploration agent. Do NOT create or edit any files.

## Environment

- Python binary: `python3` (NOT `python`)

## STOP-THE-LINE

If any finding contradicts the workpack assumptions, STOP and report.

---

## Context

Implementing ST-014: Add ground truth annotations to clarify fixtures, create 2 new clarify edge-case fixtures, and build a measurement script that computes missing_fields match rate.

**Changes planned:**
1. Add `expected` key to 3 existing clarify fixtures
2. Create 2 new clarify-specific fixtures
3. Create `scripts/analyze_clarify_quality.py` measurement script
4. Create `tests/test_clarify_measurement.py` unit tests

---

## Exploration Tasks

### Task 1: Verify existing clarify fixtures structure
```bash
cat skills/graph-sanity/fixtures/commands/empty_text.json
cat skills/graph-sanity/fixtures/commands/unknown_intent.json
cat skills/graph-sanity/fixtures/commands/minimal_context.json
```
Confirm: No `expected` key present. Note exact JSON structure and command fields.

### Task 2: Verify V1 and V2 router decide() signatures
```bash
rg "class RouterV1Adapter" routers/v1.py -A 20
rg "class RouterV2Pipeline" routers/v2.py -A 10
rg "def decide" routers/v1.py routers/v2.py --no-heading
```
Confirm: Both have `decide(command) -> dict`. Note import paths: `routers.v1.RouterV1Adapter`, `routers.v2.RouterV2Pipeline`.

### Task 3: Run V2 router on clarify fixtures to see actual decisions
```bash
python3 -c "
import json
from routers.v2 import RouterV2Pipeline
r = RouterV2Pipeline()
for f in ['empty_text.json', 'unknown_intent.json', 'minimal_context.json']:
    cmd = json.loads(open(f'skills/graph-sanity/fixtures/commands/{f}').read())
    d = r.decide(cmd)
    print(f'{f}: action={d[\"action\"]}, missing_fields={d.get(\"payload\",{}).get(\"missing_fields\")}')
"
```
Confirm: What V2 returns for each clarify fixture. Expected:
- empty_text.json: action=clarify, missing_fields=["text"]
- unknown_intent.json: action=clarify, missing_fields=["intent"]
- minimal_context.json: action=clarify, missing_fields depends on intent detection

### Task 4: Run V1 router on clarify fixtures to see actual decisions
```bash
python3 -c "
import json
from routers.v1 import RouterV1Adapter
r = RouterV1Adapter()
for f in ['empty_text.json', 'unknown_intent.json', 'minimal_context.json']:
    cmd = json.loads(open(f'skills/graph-sanity/fixtures/commands/{f}').read())
    d = r.decide(cmd)
    print(f'{f}: action={d[\"action\"]}, missing_fields={d.get(\"payload\",{}).get(\"missing_fields\")}')
"
```
Confirm: What V1 returns. Note any differences from V2 (V1 may return None for missing_fields).

### Task 5: Check build_clarify_decision return structure
```bash
rg "def build_clarify_decision" graphs/ routers/ --no-heading -A 15
```
Confirm: Exact field names in clarify decision payload (question, missing_fields, explanation).

### Task 6: Verify existing start_job fixtures (to confirm no `expected` annotations exist anywhere)
```bash
rg '"expected"' skills/graph-sanity/fixtures/commands/ --no-heading
```
Confirm: No fixture has `expected` key yet.

### Task 7: List all 14 fixtures and their text fields
```bash
for f in skills/graph-sanity/fixtures/commands/*.json; do echo "=== $(basename $f) ==="; cat "$f" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'text={repr(d.get(\"text\",\"\")[:30])}')"; done
```
Confirm: Full list of 14 fixtures. Identify which trigger clarify (empty/whitespace text, unknown intent, minimal context).

### Task 8: Check existing analyzer scripts for pattern reference
```bash
head -30 scripts/analyze_shadow_router.py
head -30 scripts/analyze_partial_trust.py
```
Confirm: Both use argparse + MetricsReport dataclass + format_report_json/human + run_self_test pattern.

### Task 9: Check decision schema for payload.missing_fields type
```bash
cat contracts/schemas/decision.schema.json | python3 -c "
import sys, json
schema = json.load(sys.stdin)
props = schema.get('properties', {}).get('payload', {}).get('properties', {})
print('missing_fields schema:', json.dumps(props.get('missing_fields'), indent=2))
"
```
Confirm: missing_fields is array of strings (or nullable).

### Task 10: Check current total test count
```bash
python3 -m pytest tests/ --co -q 2>/dev/null | tail -3
```
Confirm: 192 tests currently.

---

## Expected Findings

1. 3 clarify fixtures have no `expected` key — will add
2. V2 returns `action=clarify` with specific `missing_fields` for each fixture
3. V1 may differ on `missing_fields` (possibly None for some)
4. `build_clarify_decision` puts `missing_fields` in `payload`
5. No fixtures have `expected` key yet
6. Analyzer scripts follow argparse + dataclass + self-test pattern
7. 192 tests currently
8. Decision schema allows `missing_fields` as array in payload

## Deliverable

Report findings for all 10 tasks. Highlight:
- Exact V1/V2 outputs for the 3 clarify fixtures (critical for ground truth annotations)
- Any V1/V2 differences in missing_fields behavior
- STOP-THE-LINE issues
