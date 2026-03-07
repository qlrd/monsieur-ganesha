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

All tests must pass (currently 103). Also run before committing:

```bash
uv run black --check src/ tests/
uv run isort --check-only src/ tests/
uv run pylint src/ganesha/    # must exit cleanly (no messages)
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
├── config.py         .ganesha.toml loader (tomllib/tomli)
├── xp.py             XP session state (.ganesha_xp.json)
└── checks/
    ├── __init__.py
    ├── norminette.py   subprocess: norminette
    ├── compiler.py     subprocess: cc -Wall -Wextra -Werror -fsyntax-only
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
├── test_config.py      config loader (3 tests)
└── test_cli.py         CLI integration via subprocess

tools/                  git submodules (optional)
├── francinette/        Python piscine tester
└── mini-moulinette/    local moulinette runner
```

## Conventions

- Format: `uv run black src/ tests/`
- Sort imports: `uv run isort src/ tests/`
- Lint: `uv run pylint src/ganesha/` — must exit cleanly
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
  (the `!` selects the exact subkey for signing)
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

- Squash commits of the same scope and context before pushing.
  A branch should have one logical commit per concern.
- Prefer `git push --force-with-lease` over `--force` when
  rewriting a branch.
- `git push --force-if-includes` (git 2.30+) is also acceptable.
- Never force-push `main` or `gh-pages` directly.
- Never use `--no-verify` unless the user explicitly requests it.

## Copilot PR workflow

This repository uses GitHub Copilot as a coding agent and reviewer.

### PR authorship

- **PRs must be opened by humans** — Monsieur Piscinette, qlrd,
  or external contributors. Copilot must never be the PR author
  (copilot-swe-agent PRs violate this rule and must be closed
  immediately).
- Copilot's role is reviewer only: it comments, suggests code
  changes inline, and may apply suggestions in a second review
  round. It does not create branches or PRs.

### Polling protocol

At the start of every session and when prompted:

1. `gh pr list --repo qlrd/monsieur-ganesha --state open` — get
   the current PR list.
2. For each open PR, fetch unresolved review threads via GraphQL.
3. Reply to every unresolved thread — user (`@qlrd`) threads first,
   then Copilot threads.
4. Resolve each thread via GraphQL mutation:
   `gh api graphql -f query='mutation { resolveReviewThread(input: {threadId: "THREAD_ID"}) { thread { isResolved } } }'`
5. Push any fixes to the branch.
6. Repeat until no unresolved threads remain.
7. Post a tACK comment and ask the human maintainer to merge.

### Rules

- **Do NOT post `@copilot review` as a PR comment.** Doing so
  causes Copilot to open a new sub-PR targeting the current branch
  instead of reviewing in-place. Let Copilot's automatic review
  run on PR open and on each push.
- Close any Copilot sub-PRs immediately with an explanation: they
  duplicate work already done in the parent PR.
- Close empty WIP PRs opened by Copilot unless the work is in
  progress and genuinely needed.

## Environment

Set the git editor to vim:

```bash
git config --global core.editor vim
```

The commit-message hook opens the editor when `git commit` is
called without `-m`. vim is the expected editor at 42 school.

## Key design decisions

- `cc -fsyntax-only` avoids `.o` file conflicts across files.
- Forbidden regex `\b(func)\s*\(` so `ft_func(` is not flagged.
- `commit_msg.check` strips `#` git comment lines first.
- `load_config` returns `Config()` when `.ganesha.toml` absent.
- `tomllib` is stdlib (Python 3.11+); `tomli` backport used on
  Python 3.10.
- Gamification messages in commit_msg are informational only
  (do not affect exit code).
- `readme.py` is non-blocking: always returns `True`, emits
  advisory messages to stderr in plain text (no icon prefixes).
- `xp.py` persists state in `.ganesha_xp.json` (gitignored).
  XP schedule: first commit +100, second +75, third +50,
  fourth and subsequent commits +25. Failed blocking hook:
  -10 per invocation.
- `readme` hook uses `always_run: true` and `files: '^README\.md$'`
  (top-level only — 42 exercises forbid extra files).
- `not files` guard in `readme.py` prevents false +XP when
  non-README paths are passed via `always_run`.
