# CLAUDE.md

Instructions for Claude Code when working in this repository.

## Build

```bash
uv sync --dev          # install all dependencies (incl. dev)
```

There is no compile step — Python runs directly.

## Test

```bash
pytest
```

All tests must pass. Also run before committing:

```bash
black --check src/ tests/
isort --check-only src/ tests/
pylint src/ganesha/
```

## Project layout

```
src/ganesha/
├── __init__.py       public API (re-exports checks + config)
├── __main__.py       python -m ganesha entry point
├── cli.py            CLI entry point (argparse)
├── config.py         .ganesha.toml loader (tomllib/tomli)
└── checks/
    ├── __init__.py
    ├── norminette.py   subprocess: norminette
    ├── compiler.py     subprocess: cc -fsyntax-only
    ├── forbidden.py    pure Python regex scan
    └── commit_msg.py   pure Python regex + gamification

tests/
├── fixtures/           valid.c  norm_error.c  compile_error.c  forbidden.c
├── test_forbidden.py   integration via lib API
├── test_commit_msg.py  integration via lib API
└── test_cli.py         CLI integration via subprocess
```

## Conventions

- Format: `black src/ tests/`
- Sort imports: `isort src/ tests/`
- Lint: `pylint src/ganesha/` — zero warnings allowed
- New checks: add `src/ganesha/checks/<name>.py`, export in
  `checks/__init__.py`, add CLI subcommand in `cli.py`,
  update `.pre-commit-hooks.yaml`
- Commit messages follow Conventional Commits 1.0.0,
  subject line must not exceed 72 characters
- Prose (comments, docs, Markdown) wraps at 72 characters
- No unnecessary dependencies — prefer stdlib where possible

## Commit message format

```
<type>[(<scope>)][!]: <description>
```

Types: `feat` `fix` `docs` `style` `refactor` `perf` `test`
`build` `ci` `chore` `revert` `init`

Longer commit messages can include an optional body and footers:

```text
feat(rush03): summarize the change

Explain context and impact in a wrapped body paragraph.

Fixes #123
Co-authored-by: Name <mail@example.com>
```

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
- `load_config` uses tomllib on 3.11+ and tomli on 3.10.
- Gamification messages in commit_msg are informational only
  (do not affect exit code).
