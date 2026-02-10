# Workpack — ST-027: CI Integration for Golden Dataset Quality Report

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-009/epic.md` |
| Story spec | `docs/planning/epics/EP-009/stories/ST-027-ci-golden-dataset.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| Sprint | `docs/planning/sprints/S08/sprint.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

Two deliverables:
1. `.github/workflows/ci.yml` updated with a quality-eval step that runs `evaluate_golden.py` in stub mode (no real LLM) and uploads the report as a CI artifact.
2. `docs/guides/golden-dataset.md` — user-facing guide covering how to run locally, add entries, and interpret the quality report.

---

## Acceptance Criteria (from story spec)

| AC | Description | How to verify |
|----|-------------|---------------|
| AC-1 | CI runs evaluation | `evaluate_golden.py` runs in CI step, exits 0 |
| AC-2 | Report artifact produced | CI uploads `quality_eval_report.json` as artifact |
| AC-3 | Documentation exists | `docs/guides/golden-dataset.md` covers run/add/interpret |
| AC-4 | All 270 existing tests pass | Full test suite green (270 passed, 3 skipped) |

---

## Architecture and Design Decisions

### CI step design

The existing CI workflow (`.github/workflows/ci.yml`) has 4 steps:
1. `Install dependencies` — `pip install -e ".[dev]"`
2. `Run tests` — `python -m pytest tests/ -v --tb=short`
3. `Check schema version` — `python -m skills.schema_bump check`
4. `Release sanity` — `python3 skills/release-sanity/scripts/release_sanity.py`

Add a new step **between** "Run tests" and "Check schema version":
- Name: `Quality evaluation`
- Runs: `python3 skills/quality-eval/scripts/evaluate_golden.py > quality_eval_report.json`
- The script prints JSON report to stdout — redirect captures it.
- Script uses `is_llm_policy_enabled()` which defaults to `false` → stub mode (deterministic-only metrics).
- No `LLM_API_KEY` in CI → LLM section is `null` in report.

Then add an `Upload quality report` step using `actions/upload-artifact@v4`:
- Uploads `quality_eval_report.json` as artifact named `quality-eval-report`.
- Condition: `if: always()` — upload even if later steps fail.

### Why no threshold gate

Per story scope: "Optional: fail CI if deterministic intent_accuracy drops below threshold". Decision: **report-only** in this sprint. Thresholds are out of EP-009 scope and can be added later. The report is always available for manual review.

### evaluate_golden.py invocation

Current script (`skills/quality-eval/scripts/evaluate_golden.py`):
- `main()` loads golden dataset, evaluates all entries, prints JSON report to stdout.
- Uses `from llm_policy.config import is_llm_policy_enabled` — checks env var, defaults to `false`.
- In CI: `LLM_POLICY_ENABLED` is not set → `is_llm_policy_enabled()` returns `False` → `llm_metrics = None` → report has only `deterministic` key.
- Exit code: 0 (script does not raise on evaluation; failures are in the report itself).

### Guide structure

`docs/guides/golden-dataset.md` should cover:
1. **What is the golden dataset** — purpose, location, structure.
2. **How to run locally** — command, expected output, environment variables.
3. **How to add entries** — step-by-step (create fixture JSON, add entry to golden_dataset.json, run evaluation).
4. **How to interpret the report** — metrics explained (intent_accuracy, entity_precision/recall, clarify_rate, start_job_rate).
5. **CI integration** — what the CI step does, where to find the artifact.
6. **Reference** — golden_dataset.json entry schema, fixture file structure.

### Existing guide pattern

`docs/guides/llm-setup.md` (151 lines) is the established pattern for guides in this project: clear headings, code blocks, tables for env vars, troubleshooting section.

---

## Files to Change

| File | Change | New/Modify |
|------|--------|------------|
| `.github/workflows/ci.yml` | Add quality-eval step + upload artifact step | Modify |
| `docs/guides/golden-dataset.md` | Golden dataset guide (run/add/interpret) | New |

### Invariants (DO NOT CHANGE)

- `skills/quality-eval/scripts/evaluate_golden.py`
- `skills/graph-sanity/fixtures/golden_dataset.json`
- `skills/graph-sanity/fixtures/commands/*.json`
- `skills/graph-sanity/scripts/run_graph_suite.py`
- `tests/test_quality_eval.py`
- `graphs/core_graph.py`
- `llm_policy/config.py`

---

## Implementation Plan

### Step 1: Update `.github/workflows/ci.yml`

Add two new steps after "Run tests":

```yaml
      - name: Quality evaluation
        run: python3 skills/quality-eval/scripts/evaluate_golden.py > quality_eval_report.json

      - name: Upload quality report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: quality-eval-report
          path: quality_eval_report.json
```

### Step 2: Create `docs/guides/golden-dataset.md`

New guide covering:
- What is the golden dataset
- Running locally (`python3 skills/quality-eval/scripts/evaluate_golden.py`)
- Adding entries (fixture JSON + golden_dataset.json entry)
- Interpreting the report (metrics explanation)
- CI integration (artifact location)
- Reference (entry schema, fixture structure)

---

## Verification Commands

```bash
# Run evaluate_golden.py locally (must produce valid JSON report)
source .venv/bin/activate && python3 skills/quality-eval/scripts/evaluate_golden.py

# Validate CI YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"

# Full test suite (expect 270 passed, 3 skipped — no new tests in this story)
source .venv/bin/activate && python3 -m pytest --tb=short -q

# Verify guide file exists
test -f docs/guides/golden-dataset.md && echo "OK"
```

---

## Tests

No new unit tests. This story is CI integration + documentation.

| Verification | Type | What it covers |
|-------------|------|----------------|
| `evaluate_golden.py` runs without error | Manual/CI | AC-1 |
| Report JSON valid | Manual | AC-2 |
| Guide exists and covers topics | Manual review | AC-3 |
| Full test suite green | Automated | AC-4 |

---

## DoD Checklist

- [ ] `.github/workflows/ci.yml` updated with quality-eval + upload steps
- [ ] `docs/guides/golden-dataset.md` created (covers run/add/interpret)
- [ ] `evaluate_golden.py` runs locally without error
- [ ] Report JSON is valid
- [ ] CI YAML is syntactically valid
- [ ] No invariant files modified
- [ ] No regression in existing tests (270 passed, 3 skipped)

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| `evaluate_golden.py` exit code non-zero on evaluation failure | Low | Medium | Script wraps in try/except, always exits 0. Verify in PLAN. |
| `actions/upload-artifact@v4` API change | Low | Low | Standard GitHub action, widely used. |
| YAML syntax error in CI | Low | Medium | Validate YAML in verification step. |

---

## Rollback

Revert `.github/workflows/ci.yml` to previous version. Delete `docs/guides/golden-dataset.md`. No other files modified.
