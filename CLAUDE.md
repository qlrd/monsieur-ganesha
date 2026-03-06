# CLAUDE.md

Instructions for Claude Code when working in this repository.

## Build

```bash
uv sync --dev          # install all dependencies (incl. dev)
```

There is no compile step — Python runs directly.

## Test

```bash
uv run pytest
```

All tests must pass (currently 100). Also run before committing:

```bash
uv run black --check src/ tests/
uv run isort --check-only src/ tests/
uv run pylint src/ganesha/    # 10.00/10 required
```

Auto-fix formatting before checking:

```bash
uv run black src/ tests/
uv run isort src/ tests/
```

## Project layout

```
src/ganesha/
├── __init__.py       public API (re-exports checks + config)
├── __main__.py       python -m ganesha entry point
├── cli.py            CLI entry point (argparse) — XP integrated
├── config.py         .ganesha.toml loader (tomllib — stdlib)
├── xp.py             XP session state (.ganesha_xp.json)
└── checks/
    ├── __init__.py
    ├── norminette.py   subprocess: norminette
    ├── compiler.py     subprocess: gcc -fsyntax-only
    ├── forbidden.py    pure Python regex scan
    ├── commit_msg.py   pure Python regex + gamification
    └── readme.py       non-blocking README structure check

tests/
├── fixtures/           valid.c  norm_error.c  compile_error.c
│                       forbidden.c
├── test_forbidden.py   integration via lib API
├── test_commit_msg.py  integration via lib API
├── test_readme.py      integration via lib API (29 tests)
├── test_xp.py          XP state management (21 tests)
└── test_cli.py         CLI integration via subprocess

tools/                  git submodules (optional)
├── francinette/        Python piscine tester
└── mini-moulinette/    local moulinette runner
```

## Conventions

- Format: `uv run black src/ tests/`
- Sort imports: `uv run isort src/ tests/`
- Lint: `uv run pylint src/ganesha/` — zero warnings allowed
- New checks: add `src/ganesha/checks/<name>.py`, export in
  `checks/__init__.py`, add CLI subcommand in `cli.py`,
  update `.pre-commit-hooks.yaml`
- Blocking checks (norminette, compiler, forbidden) must call
  `xp.record_failure()` on failure in `cli.py`
- `commit-msg` must call `xp.record_success()` on pass in `cli.py`
- Non-blocking checks (readme) do not touch XP
- Commit messages follow Conventional Commits 1.0.0,
  subject line must not exceed 72 characters
- Prose (comments, docs, Markdown) wraps at 72 characters
- No unnecessary dependencies — prefer stdlib where possible

## Commit format

```
<type>[(<scope>)][!]: <description>
```

Types: `feat` `fix` `docs` `style` `refactor` `perf` `test`
`build` `ci` `chore` `revert` `init`

Additional type: `rev` — used exclusively for git tag annotation
messages (e.g. `rev: v0.1.0`).

Scopes: any identifier is valid; 42-school scopes such as
`(ex00)`, `(rush00)`, `(exam01)` are explicitly supported.

## Commit authorship and signing

Every commit in this repository must be:

- **Authored** as Monsieur Piscinette
  (`piscinette@conservatoire42.fr`)
- **Signed** with GPG key `BDEA0503A0684B03!`
- **Co-authored** by GitHub Copilot and the human maintainer:

```
Co-Authored-By: GitHub Copilot <copilot@github.com>
Co-Authored-By: qlrd <qlrddev@proton.me>
```

Always pass `-S` to `git commit`. Never use `--no-gpg-sign`.

Git tags must be annotated and signed:

```bash
git tag -s v<X.Y.Z> <sha> -m "rev: v<X.Y.Z>"
```

To replace a tag that has the wrong message, delete locally,
recreate, and force-push only the tag ref:

```bash
git tag -d v<X.Y.Z>
git tag -s v<X.Y.Z> <sha> -m "rev: v<X.Y.Z>"
git push --force origin v<X.Y.Z>  # tag refs only — not branch refs
```

## Git workflow

- Prefer `git push --force-with-lease` over `--force` when
  rewriting a branch.
- `git push --force-if-includes` (git 2.30+) is also acceptable.
- Never force-push `main` or `gh-pages` directly.
- Never use `--no-verify` unless the user explicitly requests it.

## Copilot PR workflow

This repository uses GitHub Copilot as a coding agent and reviewer.

- Poll open PRs every 2 minutes with background Bash tasks.
- Reply to every Copilot inline comment before resolving the thread.
- Resolve threads via `gh api graphql` with `resolveReviewThread`.
- After addressing all threads, post `@copilot review` to trigger
  a re-review.
- Repeat until Copilot posts an ACK (no further changes needed).
- Then post a summary comment and ask the human maintainer for
  a tACK before merging.

## Environment

Set the git editor to vim:

```bash
git config --global core.editor vim
```

The commit-message hook opens the editor when `git commit` is
called without `-m`. vim is the expected editor at 42 school.

## Key design decisions

- `gcc -fsyntax-only` avoids `.o` file conflicts across files.
- Forbidden regex `\b(func)\s*\(` so `ft_func(` is not flagged.
- `commit_msg.check` strips `#` git comment lines first.
- `load_config` returns `Config()` when `.ganesha.toml` absent.
- `tomllib` is stdlib (Python 3.11+) — no extra TOML dependency.
- Gamification messages in commit_msg are informational only
  (do not affect exit code).
- `readme.py` is non-blocking: always returns `True`, emits
  advisory messages to stderr in plain text (no icon prefixes).
- `xp.py` persists state in `.ganesha_xp.json` (gitignored).
  XP schedule: first commit +100, second +75, third +50,
  fourth+ +25. Failed blocking hook: -10 per invocation.
- `readme` hook uses `always_run: true` and `files: '^README\.md$'`
  (top-level only — 42 exercises forbid extra files).
- `not files` guard in `readme.py` prevents false +XP when
  non-README paths are passed via `always_run`.
