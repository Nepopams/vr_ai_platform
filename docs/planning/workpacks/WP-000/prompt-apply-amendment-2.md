# WP-000 — APPLY Amendment #2: Skip verification in sandbox (no network)

> **Context:** Codex sandbox has no network access. `pip install` impossible.
> **Resolution:** Create all files. Skip ALL verification commands (`python -m pytest`, `make setup-dev`, `python -m skills.*`). Verification will be done by Human locally and by CI after push.

> **Mode: APPLY** — Continue implementation.

---

## What was already done (DO NOT redo)

- Makefile: venv-aware `setup`/`setup-dev` targets, `VENV`/`PYTHON` variables
- README.md: Quick Start with venv instructions

**Step 1 is COMPLETE.** Verification will be done locally by Human.

---

## AMENDED RULE: Skip all verification commands

For ALL remaining steps (2-6), **create the files as specified** but **DO NOT run**:

- `python -m pytest ...`
- `python -m skills.*`
- `make setup-dev` / `make test` / `make test-core`
- Any `python` command

These commands require installed packages which are unavailable in sandbox.

Instead, after creating each file, verify ONLY with basic file checks:

```bash
# OK to run:
ls <path>           # file exists
wc -l <path>        # file non-empty
cat <path>          # content looks correct
grep "keyword" <path>  # key content present
```

---

## Proceed with Steps 2-6

Execute Steps 2 through 6 **exactly as specified in the original `prompt-apply.md`**. The file contents are fully specified there. Only the verification commands change (use file checks instead of pytest/skills).

### Step 2: CI pipeline

Create `.github/workflows/ci.yml` exactly as specified in prompt-apply.md.

Verify with:
```bash
cat .github/workflows/ci.yml
grep "pytest" .github/workflows/ci.yml
grep "contract_checker" .github/workflows/ci.yml
```

### Step 3: Golden dataset (12 new fixtures)

Create all 12 JSON files in `skills/graph-sanity/fixtures/commands/` exactly as specified in prompt-apply.md:

1. `buy_milk.json`
2. `buy_bread_and_eggs.json`
3. `clean_bathroom.json`
4. `fix_faucet.json`
5. `empty_text.json`
6. `unknown_intent.json`
7. `minimal_context.json`
8. `shopping_no_list.json`
9. `task_no_zones.json`
10. `buy_apples_en.json`
11. `multiple_tasks.json`
12. `add_sugar_ru.json`

Verify with:
```bash
ls skills/graph-sanity/fixtures/commands/*.json | wc -l   # expected: 14
```

### Step 4: Shared pytest fixtures

Create `tests/conftest.py` exactly as specified in prompt-apply.md.

Verify with:
```bash
ls tests/conftest.py
grep "def command_schema" tests/conftest.py
grep "def valid_command" tests/conftest.py
```

### Step 5: Planning templates

Create directory `docs/planning/_templates/` and 4 files exactly as specified in prompt-apply.md:

1. `docs/planning/_templates/epic.md`
2. `docs/planning/_templates/story.md`
3. `docs/planning/_templates/workpack.md`
4. `docs/planning/_templates/sprint.md`

Verify with:
```bash
ls docs/planning/_templates/*.md | wc -l                            # expected: 4
grep -l "Sources of Truth" docs/planning/_templates/*.md | wc -l    # expected: 4
```

### Step 6: Indexes and ADR cleanup

1. Create `docs/_indexes/initiatives-index.md` as specified
2. Modify `docs/_indexes/adr-index.md` — add AI Platform ADRs (000-005)
3. Delete `docs/adr/ADR-005: Внутренний контракт агента v0 как ABI платформы.md`

Verify with:
```bash
ls docs/_indexes/initiatives-index.md
grep "ADR-000" docs/_indexes/adr-index.md
ls docs/adr/ADR-005* | wc -l    # expected: 1
```

---

## Final file-level verification (no python needed)

```bash
# All new files exist
ls .github/workflows/ci.yml
ls tests/conftest.py
ls docs/planning/_templates/epic.md
ls docs/planning/_templates/story.md
ls docs/planning/_templates/workpack.md
ls docs/planning/_templates/sprint.md
ls docs/_indexes/initiatives-index.md

# Fixture count
ls skills/graph-sanity/fixtures/commands/*.json | wc -l   # expected: 14

# ADR-005 single file
ls docs/adr/ADR-005* | wc -l   # expected: 1

# No forbidden files changed
git diff --name-only contracts/ routers/ graphs/ app/ llm_policy/ agent_registry/
# Expected: empty
```

---

## STOP-THE-LINE (amended)

STOP only if:
- You need to modify a file in the FORBIDDEN list
- A file path from the plan doesn't match reality (parent dir missing, etc.)
- Any other structural deviation

Do NOT stop for:
- `python`/`pip`/`pytest` failures (expected in sandbox)
- Network errors (expected in sandbox)
