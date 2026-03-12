# Copilot Instructions for monsieur-ganesha

These instructions apply to all Copilot interactions in this
repository: code review, chat, agent tasks, and PR generation.

---

## Companion project

**dawon** (`https://github.com/qlrd/dawon`) is the companion
submission evaluator for the 42 piscine.  The two projects are
complementary:

| Tool | Language | Role |
|------|----------|------|
| monsieur-ganesha | Python | Pre-commit hooks: norminette, compiler, forbidden functions, commit-message, README |
| dawon | Rust | Submission evaluator: symbol, build, valgrind, harness (SHA-256) |

When a change in monsieur-ganesha affects a check that dawon also
performs, check whether dawon needs a corresponding update, and
vice versa.  When opening an issue or PR that spans both repos,
link them with `Refs qlrd/dawon#N` or `Refs qlrd/monsieur-ganesha#N`.

---

## Project summary

monsieur-ganesha is a Python pre-commit hook suite for the 42 school
piscine.  Named after Monsieur Ganesha, Directeur of the Conservatoire
de Paris XLII.

Hooks:

| Hook | What it does |
|------|--------------|
| `norminette` | Runs norminette on staged `.c` and `.h` files |
| `c-compiler` | Compiles each `.c` with `cc -Wall -Wextra -Werror` |
| `forbidden-functions` | Regex scan for configurable forbidden functions |
| `commit-message` | Enforces Conventional Commits 1.0.0 |
| `readme` | Advisory README structural check (non-blocking) |

---

## Stack

- Python 3.10+ (3.10.12 on 42 school Debian VMs)
- `tomllib` (stdlib 3.11+) / `tomli` (backport for 3.10)
- `uv` for environment and package management
- `pytest` for tests, `black` + `isort` + `pylint` for quality

---

## Configuration file

The config file is always `.ganesha.toml`.  Never write
`.piscinette.toml` or any other name.

---

## Commit discipline

- Follow **Conventional Commits 1.0.0**: `<type>[(<scope>)][!]: <description>`
- Subject line ≤ 72 characters
- Types: `feat` `fix` `docs` `style` `refactor` `perf` `test`
  `build` `ci` `chore` `revert` `init` `lore`
- `lore` is for in-world narrative commits (mascot artwork, character
  descriptions, project lore) — only use in project-level repos, not
  student submissions
- Once the PR number is known, include it in commit metadata by
  appending `(#N)` to the subject line or adding `Closes #N` /
  `Refs #N` in the commit body footer
- All commits must include `Signed-off-by:` (DCO)
- When force-pushing a branch, always use `--force-with-lease` — never
  bare `--force`

---

## Code style

- `black src/ tests/` — format before every commit
- `isort src/ tests/` — sort imports
- `pylint src/ganesha/` — zero warnings allowed
- Prose (comments, docs, Markdown) wraps at 72 characters
- No unnecessary dependencies — prefer stdlib where possible

---

## Pull request discipline

- Open an issue before writing code for non-trivial changes
- PR description must state: what, why, how tested
- CI must be green before merging
- Merge method: **Rebase and merge**

---

## Feedback loop with @copilot

Every review comment, NACK, tACK, or concern posted in response
to a Copilot-opened PR or Copilot comment **must** address
`@copilot` directly.  This notifies the agent and keeps the
review thread active.

Examples:

```
@copilot NACK — remove the extra tomllib import before merging.

@copilot tACK abc1234 — all 103 tests pass, pylint 10/10.

@copilot the forbidden regex misses multi-line calls; fix it.
```

Do not leave review concerns as unaddressed prose.  If the
concern is actionable, mention `@copilot` so the agent can
act on it.
