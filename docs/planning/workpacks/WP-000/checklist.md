# WP-000: Bootstrap Pipeline Readiness — DoD Checklist

**Workpack:** `docs/planning/workpacks/WP-000/workpack.md`

---

## Sources of Truth

- [x] Product goal: `docs/planning/strategy/product-goal.md`
- [x] Scope anchor: `docs/planning/releases/MVP.md`
- [x] DoR: `docs/_governance/dor.md`
- [x] DoD: `docs/_governance/dod.md`

---

## Pre-flight (before starting)

- [ ] Python 3.11+ available
- [ ] Git repo clean (`git status` = clean)
- [ ] Current branch = `main` or feature branch from main

---

## Step 1: Dev Environment

- [ ] `Makefile` target `setup-dev` added
- [ ] `make setup-dev` installs package with dev dependencies
- [ ] `README.md` Quick Start updated with `make setup-dev`
- [ ] `make test-core` passes after setup

**Verify:**
```bash
make setup-dev && make test-core
```

---

## Step 2: CI Pipeline

- [ ] `.github/workflows/ci.yml` created
- [ ] Workflow triggers on push to main and PRs
- [ ] Steps: checkout, setup-python 3.11, pip install, pytest, contract_checker, schema_bump, graph_sanity
- [ ] YAML is valid (no syntax errors)

**Verify:**
```bash
# Local validation (optional, requires actionlint)
actionlint .github/workflows/ci.yml

# Or push and check GitHub Actions tab
```

---

## Step 3: Golden Dataset

- [ ] >= 12 new fixture files added to `skills/graph-sanity/fixtures/commands/`
- [ ] All fixtures valid against `contracts/schemas/command.schema.json`
- [ ] Coverage: add_shopping_item (>= 3), create_task (>= 2), clarify_needed (>= 3), edge cases (>= 3)
- [ ] Each fixture has unique `command_id`
- [ ] `python -m skills.graph_sanity` passes with all fixtures

**Verify:**
```bash
ls skills/graph-sanity/fixtures/commands/*.json | wc -l    # >= 14
python -m skills.graph_sanity
```

---

## Step 4: Shared Test Fixtures

- [ ] `tests/conftest.py` created
- [ ] Contains fixtures: valid_command, valid_command_shopping, valid_command_task
- [ ] Contains fixtures: household_context, minimal_context
- [ ] Contains fixtures: command_schema, decision_schema
- [ ] No existing tests broken

**Verify:**
```bash
python -m pytest tests/ -v --tb=short
```

---

## Step 5: Planning Templates

- [ ] `docs/planning/_templates/epic.md` created
- [ ] `docs/planning/_templates/story.md` created
- [ ] `docs/planning/_templates/workpack.md` created
- [ ] `docs/planning/_templates/sprint.md` created
- [ ] Each template contains `## Sources of Truth` section
- [ ] Workpack template contains all mandatory sections per `.claude/rules/planning.md`

**Verify:**
```bash
ls docs/planning/_templates/*.md | wc -l   # = 4
grep -l "Sources of Truth" docs/planning/_templates/*.md | wc -l   # = 4
```

---

## Step 6: Indexes & ADR Cleanup

- [ ] `docs/_indexes/initiatives-index.md` created with 8 initiatives
- [ ] All initiative links resolve to existing files
- [ ] `docs/_indexes/adr-index.md` updated with ADR-000 through ADR-005
- [ ] All ADR links resolve to existing files
- [ ] `docs/adr/ADR-005: Внутренний контракт агента v0 как ABI платформы.md` deleted
- [ ] Only 1 ADR-005 file remains: `docs/adr/ADR-005-internal-agent-contract-v0.md`

**Verify:**
```bash
ls docs/adr/ADR-005* | wc -l              # = 1
wc -l docs/_indexes/initiatives-index.md   # non-empty
```

---

## Invariants (must NOT change)

- [ ] `contracts/schemas/command.schema.json` unchanged (git diff = empty)
- [ ] `contracts/schemas/decision.schema.json` unchanged
- [ ] `contracts/VERSION` = `2.0.0`
- [ ] No changes in `routers/`, `graphs/`, `app/`, `llm_policy/`, `agent_registry/`
- [ ] All pre-existing tests still pass

**Verify:**
```bash
git diff contracts/
python -m pytest tests/ -v --tb=short
python -m skills.contract_checker
python -m skills.schema_bump check
```

---

## Final Gate

- [ ] All checks above pass
- [ ] `python -m skills.release_sanity` passes
- [ ] No compiler/linter warnings introduced
- [ ] PR created with evidence of all checks

**Verify:**
```bash
python -m skills.release_sanity
```

---

## Sign-off

| Role | Name | Date | Decision |
|------|------|------|----------|
| Human (PO) | | | Approve / Reject |
| Claude (Review) | | | GO / NO-GO |
