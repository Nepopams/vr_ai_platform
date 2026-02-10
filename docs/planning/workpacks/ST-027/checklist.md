# Checklist — ST-027: CI Integration for Golden Dataset Quality Report

## Acceptance Criteria

- [ ] AC-1: CI runs `evaluate_golden.py` in stub mode (exits 0)
- [ ] AC-2: `quality_eval_report.json` uploaded as CI artifact
- [ ] AC-3: `docs/guides/golden-dataset.md` covers run/add/interpret
- [ ] AC-4: All 270 existing tests pass (full suite green)

## DoD

- [ ] `.github/workflows/ci.yml` updated with quality-eval + upload steps
- [ ] `docs/guides/golden-dataset.md` created
- [ ] `evaluate_golden.py` runs locally without error
- [ ] Report JSON is valid
- [ ] CI YAML is syntactically valid
- [ ] No invariant files modified
- [ ] No regression in existing tests

## Verification

```bash
source .venv/bin/activate && python3 skills/quality-eval/scripts/evaluate_golden.py
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
source .venv/bin/activate && python3 -m pytest --tb=short -q
test -f docs/guides/golden-dataset.md && echo "OK"
```
