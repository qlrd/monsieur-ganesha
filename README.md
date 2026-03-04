# Monsieur Ganesha

[![CI](https://github.com/qlrd/monsieur-ganesha/actions/workflows/ci.yml/badge.svg)](https://github.com/qlrd/monsieur-ganesha/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

<p align="center">
  <img src="assets/ganesha.png" alt="Monsieur Ganesha" width="320"/>
</p>

Pre-commit hooks for the 42 school piscine.
Checks your C code *before* Moulinette does.

---

## Why this tool exists

At 42, your code is evaluated by **Moulinette** — an automated
grader that runs norminette, compiles your files, and checks for
forbidden functions. If your push fails any of those checks, it
counts against you.

**Monsieur Ganesha** runs those exact same checks locally,
before you push. Think of it as a dress rehearsal: catch the
problems yourself, fix them quietly, and only push when you are
ready. Moulinette never needs to see your drafts.

For students who have already mastered the basics, the tool can
be configured to apply stricter rules — giving you the same
rigour as a real evaluation, on demand, on your own machine.

---

## What it checks

| Hook | What it does |
|---|---|
| `norminette` | Runs `norminette` on every `.c` and `.h` file you are about to commit |
| `c-compiler` | Compiles each `.c` file with `gcc -Wall -Wextra -Werror -fsyntax-only` |
| `forbidden-functions` | Scans for function calls you are not allowed to use |
| `commit-message` | Validates the format of your commit message |

All four hooks run automatically, every time you `git commit`.
If any check fails, the commit is blocked and the errors are
printed. You fix, you stage, you commit again.

---

## Self-evaluation before pushing

The most important use of this tool is **running it before
`git push`**. Here is the workflow:

```
1.  Write your code.
2.  git add <files>
3.  git commit   ← hooks run here; fix any errors reported
4.  Repeat until all hooks pass.
5.  git push     ← only now does Moulinette see your work.
```

Each failed hook tells you exactly which file, which line, and
what the problem is. Fix it, stage the fix, commit again. The
hooks re-run on every commit attempt, so you always get
up-to-date feedback.

You can also run any check manually at any time:

```bash
python -m ganesha norminette  src/*.c src/*.h
python -m ganesha compiler    src/*.c
python -m ganesha forbidden   src/*.c
python -m ganesha commit-msg  .git/COMMIT_EDITMSG
```

Each command exits with `0` (pass), `1` (check failed), or
`2` (tool not found — install norminette or gcc first).

---

## For advanced users: strict evaluation mode

Once you are comfortable with the default rules, you can tighten
them to simulate a real evaluation session.

Create `.ganesha.toml` at the root of your project:

```toml
[project]
name = "ex00"

[forbidden]
functions = [
    "printf", "puts", "putchar",
    "malloc", "free",
    "open", "read", "write", "close",
]

[commit]
pattern = '^(ex|rush|exam)\d+: .+'
```

With this configuration:

- **Any call to a forbidden function** causes a hook failure,
  just like a real evaluation.
- **Commit messages** must follow the `ex00: description` format
  required at the piscine.
- You can run `git commit` as many times as you need; only
  conforming commits succeed.

This makes the tool suitable for **self-imposed mock
evaluations**: set the forbidden list to match the exercise
constraints, write your solution, and only commit when
everything passes. If it passes here, it will pass Moulinette.

---

## Requirements

- Python 3.11 or later
- `norminette` (install once: `pip install norminette`)
- `gcc`
- `pre-commit` (install once: `pip install pre-commit`)

---

## Installation

### Quick install (recommended)

```bash
bash <(curl -fsSL \
  https://raw.githubusercontent.com/YOUR_USER/monsieur-ganesha/main/install.sh)
```

The script installs `pre-commit`, configures the hooks for the
current repository, and sets `git config core.editor vim`.

### Manual install

Add this to your project's `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/YOUR_USER/monsieur-ganesha
    rev: v0.1.0
    hooks:
      - id: norminette
      - id: c-compiler
      - id: forbidden-functions
      - id: commit-message
```

Then run:

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

---

## Configuration reference

All settings live in `.ganesha.toml` at the root of your
repository. The file is optional — defaults are used when it is
absent.

```toml
[project]
name = "my-project"      # informational only

[forbidden]
functions = []           # list of function names to forbid

[commit]
pattern = ""             # regex for commit message first line
                         # leave empty for Conventional Commits
```

When `pattern` is empty, the default format is:

```
<type>[(<scope>)][!]: <description>
```

Recognised types: `feat`, `fix`, `docs`, `style`, `refactor`,
`perf`, `test`, `build`, `ci`, `chore`, `revert`, `init`.

The subject line must not exceed **72 characters**.

---

## Commit message format

Monsieur Ganesha enforces
[Conventional Commits 1.0.0](https://www.conventionalcommits.org/)
by default.

```
feat: add write_fd function
fix(compiler): accept variadic macros
docs!: rewrite README — breaking change in hook API
```

A breaking change is marked with `!` before the colon.
An optional body follows after a blank line.

If the message does not match, the commit is rejected with:

```
REJECTED.
```

No hints are given — discovering the required format is part of
the exercise.

---

## Gamification layer

Commit types carry hidden rewards, displayed after a successful
commit:

- `docs` or `chore` — Francinette approves.
- `test` — the ultimate commit type.
- `!` (breaking change) with a body — bonus XP.

These messages are informational only. They do not affect the
exit code or block the commit.

---

## Development

```bash
uv sync --dev          # install dependencies
pytest                 # run all tests (45 tests)
black --check src/ tests/
isort --check-only src/ tests/
pylint src/ganesha/ # must score 10.00/10
```

### Project layout

```
src/ganesha/
├── __init__.py
├── __main__.py
├── cli.py
├── config.py
└── checks/
    ├── norminette.py
    ├── compiler.py
    ├── forbidden.py
    └── commit_msg.py
tests/
├── fixtures/          valid.c  norm_error.c  compile_error.c  forbidden.c
├── test_forbidden.py
├── test_commit_msg.py
└── test_cli.py
```

---

## Rebase note

This section unlocks once you have performed at least one
correct `git rebase` using `fixup`, `reword`, or `edit`.

Rebase operations are verified in the reflog. The reflog
itself must never be modified.

---

## Lore

*When you and Norminette fall in love, Moulinette notices.*
*She always does. C'est terrible.*
*Close the door.*

                                        — Ganesha
