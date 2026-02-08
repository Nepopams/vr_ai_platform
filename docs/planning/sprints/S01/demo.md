# Sprint S01 -- Demo Plan

## Sources of Truth

| Artifact | Path |
|----------|------|
| Sprint plan | `docs/planning/sprints/S01/sprint.md` |
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |

---

## Sprint Increment

At the end of Sprint S01, both NOW-phase initiatives will have all acceptance criteria verified with traceable evidence, and the platform will have a reproducible golden-dataset analysis capability.

---

## Demo Items

### 1. ST-001: Golden-dataset analyzer in action

**Demonstrable artifact:** Working Python script that analyzes shadow router logs against ground truth.

**Demo steps:**

1. Show the golden dataset manifest (`skills/graph-sanity/fixtures/golden_dataset.json`):
   - 14 entries with command_id, expected_intent, expected_entity_keys.
   - Explain ground truth labeling rationale for 2-3 representative entries.

2. Run the analyzer against synthetic JSONL test data:
   ```bash
   python scripts/analyze_shadow_router.py \
     --shadow-log tests/fixtures/synthetic_shadow.jsonl \
     --golden-dataset skills/graph-sanity/fixtures/golden_dataset.json \
     --output-json /tmp/demo_report.json
   ```

3. Show the human-readable stdout report:
   - intent_match_rate, entity_hit_rate
   - latency_p50, latency_p95
   - error_breakdown
   - total_records, matched_records

4. Show the JSON output file and confirm it contains all required fields.

5. Run with empty JSONL to demonstrate edge case handling:
   ```bash
   python scripts/analyze_shadow_router.py \
     --shadow-log /dev/null \
     --golden-dataset skills/graph-sanity/fixtures/golden_dataset.json
   ```
   - Confirm: total_records=0, rates show null/n/a.

6. Run unit tests:
   ```bash
   pytest tests/test_analyze_shadow_router.py -v
   ```
   - All tests pass (including privacy self-test).

7. Show README (`scripts/README-shadow-analyzer.md`):
   - Purpose, prerequisites, invocation, output format, how to add entries.

**Success criteria for demo:** Script runs, produces correct metrics, tests pass, README is clear.

---

### 2. ST-002: Shadow-router initiative verification report

**Demonstrable artifact:** Formal verification report with evidence trail.

**Demo steps:**

1. Open `docs/planning/epics/EP-001/verification-report.md`.

2. Walk through the AC table:
   - AC1 (shadow mode off by default): show referenced config, env var, test.
   - AC2 (LLM error does not affect baseline): show referenced tests and error handling code.
   - AC3 (no raw text in logs): show referenced log functions and test.

3. Run the verification commands listed in the report:
   ```bash
   pytest tests/test_shadow_router.py -v
   ```
   - Confirm 4 tests pass as documented.

4. Show the initiative status update in `docs/planning/initiatives/INIT-2026Q1-shadow-router.md`:
   - Status changed to "Verified (pending AC4)".

**Success criteria for demo:** All 3 ACs map to concrete evidence, tests pass, initiative status updated.

---

### 3. ST-003: Assist-mode acceptance rules documentation

**Demonstrable artifact:** Human-readable acceptance rules document.

**Demo steps:**

1. Open `docs/contracts/assist-mode-acceptance-rules.md`.

2. Walk through each section:
   - **Normalization rules:** rejection conditions (empty, length, no overlap), acceptance behavior (re-detection).
   - **Entity extraction rules:** intent guard, agent vs LLM priority, substring check, agent scoring.
   - **Clarify suggestor rules:** length bounds, echo prevention, intent-specific behavior, v2 missing_fields check.
   - **Fallback behavior:** timeout mechanism, error handling, feature flags.

3. For 2-3 rules, cross-reference with actual code function to confirm accuracy.

**Success criteria for demo:** Document is complete, accurate, and every rule references a code location.

---

### 4. ST-004: Assist-mode initiative verification report

**Demonstrable artifact:** Formal verification report with GO/NO-GO recommendation.

**Demo steps:**

1. Open `docs/planning/epics/EP-002/verification-report.md`.

2. Walk through each AC:
   - AC1 (feature flag enablement): config file, flag names, defaults, test evidence.
   - AC2 (acceptance rules documented): reference to ST-003 deliverable + code functions + tests.
   - AC3 (error/timeout fallback): timeout mechanism, test evidence.
   - AC4 (no raw text in logs): logging approach, test evidence.

3. Run the verification commands:
   ```bash
   pytest tests/test_assist_mode.py tests/test_assist_agent_hints.py -v
   ```
   - Confirm all referenced tests pass.

4. Show GO/NO-GO recommendation and initiative status update.

**Success criteria for demo:** All 4 ACs verified, tests pass, initiative can be formally closed.

---

## Overall Sprint Demo Narrative

**Theme:** "We can now measure and verify."

1. **Before this sprint:** Shadow router and assist-mode were implemented and tested, but we could not measure LLM quality against ground truth, acceptance rules were tribal knowledge in code, and initiative ACs were not formally verified.

2. **After this sprint:**
   - Golden-dataset analyzer enables reproducible LLM quality measurement (initiative success signal: "reproducible report").
   - Acceptance rules are documented for audit and onboarding.
   - Both initiatives have formal verification reports with traceable evidence.
   - Initiatives can transition toward closure.

3. **What this enables next:** With measurement in place, the NEXT phase (2026Q2) can begin Partial Trust and improved clarify with a baseline to measure against.
