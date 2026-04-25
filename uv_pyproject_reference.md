# uv + pyproject.toml — Working Reference

A scannable companion to M1 (Modern Python Project Hygiene) of the Helios V2 Learning Guide. Open this whenever you forget a command or which file owns what.

---

## 1. The mental model

Three artifacts, one direction of truth.

```
pyproject.toml  ──►  what you DECLARE you want
     │
     │ uv resolves
     ▼
   uv.lock      ──►  the EXACT versions chosen (pinned, hashed, transitive)
     │
     │ uv installs
     ▼
   .venv/       ──►  the actual files Python imports
```

- `pyproject.toml` — source of truth, hand-edited or via `uv add`. **Commit it.**
- `uv.lock` — resolved snapshot, machine-managed. **Commit it.**
- `.venv/` — build artifact. **Do NOT commit** (already in `.gitignore`).

**Asymmetry rule.** Edits to `pyproject.toml` propagate down. Edits to `.venv/` (e.g., `pip install` inside it) do NOT propagate up — and the next `uv sync` will *delete* anything in `.venv/` that isn't in the lockfile.

---

## 2. uv command cheat sheet

### Daily commands

| Command | What it does | Touches |
|---|---|---|
| `uv init <name>` | New project: `pyproject.toml`, `.python-version`, README | files |
| `uv add <pkg>` | Add runtime dep | toml + lock + venv |
| `uv add --dev <pkg>` | Add dev dep (PEP 735 group) | toml + lock + venv |
| `uv remove <pkg>` | Remove a dep | toml + lock + venv |
| `uv sync` | Make `.venv/` match the lockfile | venv only |
| `uv sync --frozen` | Same, but fail if lockfile is stale | venv only |
| `uv lock` | Re-resolve lockfile from `pyproject.toml` | lock only |
| `uv run <cmd>` | Run command inside venv (auto-syncs first) | venv (if stale) |
| `uv tree` | Show dependency tree | nothing |

### Less common but useful

| Command | What it does |
|---|---|
| `uv python install 3.12` | Download a Python interpreter |
| `uv python list` | List available interpreters |
| `uv add --script foo.py requests` | PEP 723 inline-deps for a one-file script |
| `uv run --with rich python` | Temp overlay env (no `pyproject.toml` change) |
| `uv tool install ruff` | Install a CLI tool globally (not project-scoped) |
| `uv export --format requirements-txt` | Export to old-style requirements.txt |
| `uv add -r requirements.txt` | Migrate from pip's requirements.txt |

### Flags worth remembering

- `--frozen` — error if lockfile is out of sync with `pyproject.toml`. **Use in CI and Docker.**
- `--no-install-project` — install only deps, not the project itself (Docker layer-cache trick).
- `--upgrade-package <pkg>` — bump one specific package without touching others.
- `--group <name>` — install a specific dependency group.

---

## 3. pyproject.toml structure (PEP 621)

Minimal-but-real shape for a Helios-style project:

```toml
[build-system]
requires = ["uv_build>=0.5"]
build-backend = "uv_build"

[project]
name = "helios-v2"
version = "0.1.0"
description = "Trustworthy queryable map of real food deals in Austin"
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"
authors = [{ name = "Your Name", email = "you@example.com" }]
dependencies = [
    "fastapi>=0.115",
    "sqlalchemy>=2.0",
    "httpx>=0.27",
    "selectolax>=0.3",
]

[dependency-groups]
dev = ["pytest>=8", "ruff", "mypy", "pre-commit"]
test = ["pytest-cov", "hypothesis"]

[project.scripts]
helios = "helios.cli:main"

[project.urls]
Repository = "https://github.com/First-Helios/First-Helios"

[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
testpaths = ["packages", "apps"]
```

### Field cheatsheet

- **Required:** `name`. That's the only one strictly required.
- **Strongly recommended:** `version`, `description`, `readme`, `requires-python`, `dependencies`.
- `authors` and `maintainers` are **lists of tables**, even for one person: `[{ name = "..." }]`.
- `readme` can be `"README.md"` (string) or `{ file = "...", content-type = "text/markdown" }` (table).
- `license` is now an SPDX string per PEP 639: `license = "MIT"`. (Old `{ text = "MIT" }` form still works.)
- `dynamic = ["version"]` — declare here, omit from `[project]`, when build backend computes it.

### Where deps go

- `[project] dependencies` — runtime, ships with your wheel.
- `[project.optional-dependencies]` — extras users opt into: `pip install pkg[scraping]`.
- `[dependency-groups]` (PEP 735) — local dev/test groups, **never ship** to PyPI. Prefer this for `dev`/`test`/`docs` over the old `optional-dependencies` style.

### Tool config

Anything not in PEP 621 lives under `[tool.*]`:
- `[tool.ruff]` / `[tool.ruff.lint]` — lint and format settings
- `[tool.mypy]` — type checker config (or use a separate `mypy.ini`)
- `[tool.pytest.ini_options]` — pytest config
- `[tool.uv]` — uv-specific settings (index URLs, resolution strategy, etc.)

---

## 4. Workflow rules

The discipline that keeps the three artifacts in lockstep.

1. **Always use `uv add` / `uv remove`** for deps in normal use. Hand-editing `pyproject.toml` works but you'll need to remember to `uv sync` after.
2. **Always use `uv run`** for project commands (`uv run pytest`, `uv run python script.py`). This auto-syncs before running, so the venv is never stale.
3. **Commit `uv.lock`.** Always. It's the reproducibility contract.
4. **Never `pip install` inside `.venv/`.** It silently desyncs and gets wiped on next sync.
5. **`--frozen` everywhere outside your laptop.** CI, Docker, prod — all use `uv sync --frozen` so a stale lockfile fails the build instead of silently mutating.
6. **`uv add foo` to try, `uv remove foo` to undo.** Don't be precious — both are sub-second.

---

## 5. Common operations

### Bootstrap a new project
```bash
uv init helios-learning
cd helios-learning
uv add httpx selectolax
uv add --dev pytest ruff mypy
uv run pytest
```

### Fresh checkout (new machine)
```bash
git clone <repo>
cd <repo>
uv sync          # reads pyproject.toml + uv.lock, builds .venv from scratch
```

### Bump a single dependency
```bash
uv add --upgrade-package httpx httpx
# or for everything:
uv lock --upgrade
uv sync
```

### Try a package without committing
```bash
uv run --with pandas python   # pandas available only for this invocation
```

### Migrate from old setup
```bash
# from requirements.txt:
uv init
uv add -r requirements.txt

# from poetry: uv reads poetry's pyproject.toml; just run `uv lock` then `uv sync`
```

### See what's installed and why
```bash
uv tree                 # full dep graph
uv tree --depth 1       # just direct deps
uv pip list             # flat list (pip-compat interface)
```

---

## 6. Docker integration

uv = reproducible Python env. Docker = reproducible whole machine. Use both.

### Production-style Dockerfile pattern

```dockerfile
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

# Layer 1: deps (cached unless pyproject.toml or lock changes)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Layer 2: source (changes often)
COPY . .
RUN uv sync --frozen

FROM python:3.12-slim
COPY --from=builder /app /app
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Key ideas

- **Multi-stage:** builder has uv + toolchain; runtime is lean.
- **Copy lockfile first, source second:** code changes don't bust the deps cache.
- **`--frozen`:** build fails fast if `pyproject.toml` and `uv.lock` disagree.
- **`PATH=/app/.venv/bin:$PATH`:** in prod, use the venv's binaries directly. No `uv run` needed.

### docker-compose for local dev

Use `docker compose up postgres` to get a real database without polluting your laptop. Don't install Postgres locally — let Docker handle it.

---

## 7. Gotchas and things to internalize

### "I installed it but Python can't find it"
Probably installed into system Python instead of `.venv/`. Use `uv add` or `uv run pip install`, never bare `pip install`.

### "Why did my package disappear?"
You ran `uv sync` after `pip install`-ing into the venv. The venv is downstream of the lockfile; sync is destructive by design. Add via `uv add` instead.

### "My CI build worked yesterday, fails today"
You probably ran `uv add` locally without committing the updated `uv.lock`. CI uses `--frozen` and refuses stale lockfiles. **Always commit `uv.lock` with the same PR as the `pyproject.toml` change.**

### "Lockfile conflict in git"
Resolve `pyproject.toml` first, then run `uv lock` to regenerate `uv.lock` cleanly. Don't try to merge the lockfile by hand.

### "I want to share this project but they don't have uv"
They can: `pip install uv && uv sync`. Or: `uv export --format requirements-txt > requirements.txt` and they `pip install -r requirements.txt`. (You lose the lockfile guarantee with the second option.)

### Dev deps vs optional deps — when to use which?
- **`[dependency-groups]`** for things only you and CI need: pytest, mypy, ruff. **Default choice.**
- **`[project.optional-dependencies]`** for things downstream users might want: `pkg[scraping]`, `pkg[ml]`. Only when you publish a library.

### Don't `source .venv/bin/activate`
You can, but you don't need to. `uv run <cmd>` is shorter and ensures the venv is in sync first. Activation is a habit from the old world.

---

## 8. Self-check (M1 rubric)

You should be able to answer these from memory before moving past M1:

- [ ] Difference between `requirements.txt` and a lockfile?
- [ ] Three things `uv add httpx` modifies, in order?
- [ ] What does `--frozen` enforce, and why is it important in CI?
- [ ] Why is `.venv/` not committed but `uv.lock` is?
- [ ] What happens if you `pip install pandas` inside an active venv, then run `uv sync`?
- [ ] How do you bump exactly one dependency without touching the rest?
- [ ] What's `[dependency-groups]` for vs `[project.optional-dependencies]`?
- [ ] How does Docker's layer cache interact with the order of `COPY` and `RUN uv sync` lines?

If any of these feel shaky, scroll back up — that's where to re-read.

---

*Last updated: 2026-04-24. Living document; update as you discover better workflows.*
