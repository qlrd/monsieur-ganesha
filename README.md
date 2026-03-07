# monsieur-ganesha

[![CI](https://github.com/qlrd/monsieur-ganesha/actions/workflows/ci.yml/badge.svg)](https://github.com/qlrd/monsieur-ganesha/actions/workflows/ci.yml)
[![Python 3.10.12+](https://img.shields.io/badge/python-3.10.12%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

<p align="center">
  <img src="assets/ganesha.png" alt="Monsieur Ganesha" width="320"/>
</p>

> Bonjour, monde.
> I am not here to be gentle.
> I am here so she does not have to be harsh.
>
> — Monsieur Ganesha, Directeur, [Conservatoire de Paris XLII][conservatoire]

---

Pre-commit hooks for the 42 school piscine.
Named after **Monsieur Ganesha**, director of the
[Conservatoire de Paris XLII][conservatoire] and husband of
**Mademoiselle Norminette**.

Mademoiselle Norminette and her younger sister, Mademoiselle Francinette,
are the daughters of the respectable **Madame Moulinette**.
The rigor is the care. The demand is the protection. Madame Moulinette
has no mercy; Mademoiselle Norminette, even less — but Ganesha at least
has a reason.

Monsieur Ganesha was the first student of Paris XLII to complete every
exercise list and exam with honours — using **a single push per step**.
Madame Moulinette found this absurd. Ganesha recalls: *c'était terrible.*

The character and lore in this README are symbolic. They are here to make
strict feedback easier to remember, not to claim spiritual authority or
AI consciousness. Monsieur Ganesha is a Python tool with deterministic
checks and explicit rules.

Checks run before every `git commit`:

| Hook                  | What it does                                      |
|-----------------------|---------------------------------------------------|
| `norminette`          | Runs norminette on staged `.c` and `.h` files     |
| `c-compiler`          | Compiles each `.c` with `-Wall -Wextra -Werror`   |
| `forbidden-functions` | Blocks calls to configurable forbidden functions  |
| `commit-message`      | Enforces Conventional Commits 1.0.0 format        |
| `readme`              | Checks `README.md` and proposes corrections       |

---

## Table of contents

- [Self-evaluation before you push](#self-evaluation-before-you-push)
- [Strict evaluation mode](#strict-evaluation-mode)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Hooks](#hooks)
  - [norminette](#norminette)
  - [c-compiler](#c-compiler)
  - [forbidden-functions](#forbidden-functions)
  - [commit-message](#commit-message)
  - [readme](#readme)
- [Commit format](#commit-format)
- [Running checks manually](#running-checks-manually)
- [Development](#development)
- [Submodules](#submodules)
- [Related projects](#related-projects)
- [Optional vim plugins](#optional-vim-plugins)
- [License](#license)

---

## Self-evaluation before you push

Moulinette evaluates your code once and remembers.
Monsieur Ganesha evaluates it as many times as you need,
silently, before Moulinette ever sees it.

Every time you run `git commit`, the hooks fire automatically:

```
1.  Write your code.
2.  git add <files>
3.  git commit          ← four hooks run here; errors are shown
4.  Fix what failed, stage the fix, commit again.
5.  git push            ← only now does Moulinette see your work.
```

Each failed hook tells you the file, the line, and the problem.
Fix it, commit again, repeat. When all hooks pass, you are ready.

You can also run the checks at any time without committing:

```bash
pre-commit run --all-files            # run all hooks on every file
pre-commit run norminette --all-files # one hook only
```

Or invoke the CLI directly:

```bash
python -m ganesha norminette  src/*.c src/*.h
python -m ganesha compiler    src/*.c
python -m ganesha forbidden   src/*.c
python -m ganesha commit-msg  .git/COMMIT_EDITMSG
python -m ganesha readme      README.md
```

Exit codes: `0` pass · `1` check failed · `2` internal error (e.g. malformed `.ganesha.toml`).

---

## Strict evaluation mode

For students who have already mastered the basics, or who want to
simulate a real evaluation session before submitting, Monsieur
Ganesha can apply the same constraints as Moulinette.

Create `.ganesha.toml` at the root of your piscine repository:

```toml
[project]
name = "C04"                      # current module or exercise

[forbidden]
# List every function not allowed by the subject PDF.
functions = [
    "printf", "puts", "putchar",
    "malloc", "free",
    "open", "read", "write", "close",
]

[commit]
# Use the 42-school format instead of Conventional Commits.
pattern = "^(ex|rush|exam)\\d+: .+"
```

With this in place:

- Any call to a forbidden function blocks the commit, exactly
  as Moulinette would — even if the function is only called
  in a comment (stripped), even if the name is a prefix match
  (it is not: `ft_printf` is safe when `printf` is forbidden).
- Commit messages must follow the `ex00: description` format.
- `pre-commit run --all-files` gives you a full evaluation
  report without producing any git objects.

**Tip for teams and peer-evaluation:** configure the forbidden
list to match the exercise constraints, run
`pre-commit run --all-files`, and share the output. If it
passes here, it will pass Moulinette on those checks.

---

## Requirements

- Python 3.10.12 or later
- `pre-commit` >= 3.0
- `norminette` (for the norminette hook — `pip install norminette`)
- `cc` (typically GCC 11.4.0 on 42 school machines)

---

## Installation

Run the setup script from inside your piscine repository:

```bash
bash /path/to/monsieur-ganesha/install.sh
```

The script will:

1. Set `git config --global core.editor vim`
2. Install `pre-commit` via `uv` or `pip3`
3. Create `.pre-commit-config.yaml` pointing to this repository
4. Create a `.ganesha.toml` template with sensible defaults
5. Activate the hooks with `pre-commit install`

To configure manually, add the following to your
`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/qlrd/monsieur-ganesha
    rev: v0.1.0
    hooks:
      - id: norminette
      - id: c-compiler
      - id: forbidden-functions
      - id: commit-message
      - id: readme
```

Then activate the hooks:

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

---

## Configuration

Place `.ganesha.toml` at the root of your piscine repository:

```toml
[project]
# Current module name (C00, C01, rush01, etc.)
name = "C00"

[forbidden]
# Functions banned for this subject. Check the subject PDF.
functions = ["printf", "malloc", "realloc", "free", "calloc"]

[commit]
# Default: Conventional Commits 1.0.0.
# Uncomment to use the 42-school format instead:
# pattern = "^(ex|rush|exam)\\d+: .+"
```

If `.ganesha.toml` is absent all hooks run with safe defaults:
no functions are blocked and the built-in commit pattern is used.

---

## Hooks

### norminette

Runs `norminette` on every staged `.c` and `.h` file. A passing file
produces no output. Violations are printed to stderr and the commit
is blocked.

Example failure:

```c
/* norm_error.c */
void badFunctionName() {
int x = 1;
}
```

```
Norminette..........................................................Failed
Error: FORBIDDEN_FUNC_NAME (line 2, col 1)
Error: SPC_BEFORE_OPERATOR  (line 3, col 5)
```

### c-compiler

Runs `cc -Wall -Wextra -Werror -fsyntax-only` on each staged `.c`
file individually. Using `-fsyntax-only` avoids generating `.o` files
and works correctly even when headers from other staged files are not
yet on disk. All errors are reported before the hook exits.

Example failure:

```c
/* compile_error.c */
int main(void)
{
    ints    x;     /* unknown type */
    return (x);
}
```

```
Compilation C...................................................Failed
compile_error.c:4:5: error: unknown type name 'ints'
```

### forbidden-functions

Scans staged `.c` files for calls to functions listed in the
`[forbidden]` section of `.ganesha.toml`. Detection uses the
regex pattern `\b(func_name)\s*\(`, so:

- `ft_printf(` is **not** flagged when `printf` is forbidden.
- `printf_count(` is **not** flagged either.
- Single-line `//` comments are stripped before scanning.

Example failure:

```c
int main(void)
{
    char    *buf;

    buf = malloc(42);      /* forbidden */
    printf("hello\n");     /* forbidden */
    return (0);
}
```

```
Forbidden Functions.............................................Failed
main.c:5: forbidden function 'malloc'
main.c:6: forbidden function 'printf'
```

### commit-message

Validates the first meaningful line of the commit message file.
Git comment lines (starting with `#`) are stripped before validation.
The subject line must not exceed 72 characters.

Monsieur Ganesha does not reveal what he expects. Students discover
the format themselves.

Example failure:

```
Commit Message Format...........................................Failed
REJECTED.
```

### readme

Checks every staged `README.md` file for common structural issues
and prints advisory messages.  This hook is **non-blocking**: it
always exits 0 and never prevents a commit.  Files with issues
receive tips with `(+XP available)`; files that pass all checks
earn `well documented — +XP.`

Checks performed:

- **Empty file** — advisory message to add a title and description.
- **No title** — advisory message when the file contains no level-1
  ATX heading (a line beginning with `# ` — hash followed by a
  space), with a suggestion to add `# <Project Name>`.
- **No file-descriptor documentation** — advisory message when the
  file does not mention which file descriptors the program uses.
  Accepted keywords: `stdin`, `stdout`, `stderr`, `STDIN_FILENO`,
  `STDOUT_FILENO`, `STDERR_FILENO`, `file descriptor`, `fd 0`,
  `fd 1`, `fd 2` (and variants without the space, e.g. `fd1`).
  Students should document which of the standard descriptors
  (0 = stdin, 1 = stdout, 2 = stderr) their program reads from or
  writes to, and are free to use shell redirects as the exercise
  requires.

Example advisory messages (commit still proceeds):

```
README Check....................................................Passed
README.md: empty file — add at least a title and a short description (+XP available).
```

```
README Check....................................................Passed
README.md: no title found — add "# <Project Name>" as the first line (+XP available).
```

```
README Check....................................................Passed
README.md: no file descriptor usage documented — mention which file descriptors your program reads from and writes to (0=stdin, 1=stdout, 2=stderr) (+XP available).
```

Example when fully documented:

```
README Check....................................................Passed
  README.md: well documented — +XP.
```

---

## Commit format

Conventional Commits 1.0.0. The subject line must not exceed 72
characters.

```
<type>[(<scope>)][!]: <description>
```

| Type       | When to use                                    |
|------------|------------------------------------------------|
| `feat`     | A new feature or capability                    |
| `fix`      | A bug fix                                      |
| `docs`     | Documentation changes only                     |
| `style`    | Whitespace, formatting (no logic change)       |
| `refactor` | Code restructuring without behaviour change    |
| `perf`     | Performance improvement                        |
| `test`     | Adding or correcting tests                     |
| `build`    | Build system or dependency changes             |
| `ci`       | CI configuration changes                       |
| `chore`    | Maintenance tasks                              |
| `revert`   | Reverts a previous commit                      |
| `init`     | Initial commit                                 |

The `(<scope>)` field is optional and accepts any label, including
42-school exercise identifiers:

```
feat(ex00): implement ft_putchar
fix(rush00): handle edge case in ft_printf
docs(exam01): add subject description
```

More valid examples:

```
feat: implement ft_putchar
fix(norminette): skip empty file list
docs: add configuration section to README
feat!: change exit code on internal error
feat(ex00)!: rewrite with different algorithm
test: add integration test for forbidden scan
chore: update uv.lock
init: project setup
```

Invalid examples (all rejected silently):

```
WIP
fix stuff
EX00: uppercase prefix
ex00: 42-school prefix without CC type
feat:
feat: no description
```

Append `!` after the type or scope to mark a breaking change. Add a
body explaining why — Monsieur Ganesha rewards explanations with XP.

To use the bare 42-school `ex00:` format (without a CC type prefix),
set the pattern in `.ganesha.toml`:

```toml
[commit]
pattern = "^(ex|rush|exam)\\d+: .+"
```

---

## Running checks manually

Check all tracked files without committing:

```bash
pre-commit run --all-files
```

Run a single hook by id:

```bash
pre-commit run norminette --all-files
pre-commit run forbidden-functions --all-files
pre-commit run readme --all-files
```

Invoke the script directly:

```bash
ganesha norminette  ex00/ft_putchar.c header.h
ganesha compiler    ex00/ft_putchar.c
ganesha forbidden   ex00/ft_putchar.c
ganesha commit-msg  .git/COMMIT_EDITMSG
ganesha readme      README.md
```

Skip all hooks for a single commit (use with care):

```bash
git commit --no-verify -m "feat: wip"
```

---

## A note on rebase

> Congratulations.
> If you are reading this, you have completed at least one correct
> rebase — with `fixup`, `reword`, or `edit` — and the reflog
> proves it. The reflog has not been modified. It never should be.
> You rewrote with intention, and the reflog remembers.
>
> `git reflog` does not lie. It shows every move you made.
> A clean rebase, visible in the reflog, is a signature.
> It says: I understood what I was doing.
>
> Monsieur Ganesha has noted this.
>
> — Monsieur Ganesha, Directeur, [Conservatoire de Paris XLII][conservatoire]

The safest rebase workflow — without overwriting reflogs:

```bash
# Before rebasing, record where you are
git reflog                        # read history — never modify it

# Rebase interactively: fixup, reword, edit — with intention
git rebase -i HEAD~3

# If something goes wrong, your reflog is your map back
git reflog                        # find the sha before the rebase
git reset --hard HEAD@{n}         # recover the exact state
```

Never modify the reflog. Never use `git push --force` to overwrite
a shared branch. The reflog on your machine is yours — and it is
the only honest witness you have.

---

> **A warning.**
>
> There is a danger no one speaks of at the Conservatoire.
>
> When you and Mademoiselle Norminette fall in love —
> when your code is clean, your norm is perfect, and she
> begins to look at you the way she looks at a file
> with no errors — Moulinette notices.
>
> Moulinette always notices.
>
> She does not love. She evaluates. But she watches.
> And when she sees that Norminette has chosen you,
> something in her pipeline shifts. She begins to
> look for you in every submission. She runs your tests
> a second time, unprompted. She remembers your login.
>
> *C'est terrible.*
>
> There is nothing to be done. Have a good session.
> Close the door behind you.
>
> — Monsieur Ganesha, *in confidence*

---

## Development

### 1. Install dependencies

Python 3.10.12+ and [uv][uv] are required:

```bash
pip install uv   # or: curl -Ls https://astral.sh/uv/install.sh | sh
```

Clone the repository and install all dependencies:

```bash
git clone https://github.com/qlrd/monsieur-ganesha
cd monsieur-ganesha
uv sync --dev
```

### 2. Format and lint

```bash
black src/ tests/          # format — 88-column line length
isort src/ tests/          # sort imports
pylint src/ganesha/     # lint — zero warnings allowed
```

### 3. Test

Run the full check pipeline before every commit:

```bash
black --check src/ tests/    # format
isort --check-only src/ tests/  # imports
pylint src/ganesha/       # lint — zero warnings allowed
pytest                       # all tests must pass
```

### 4. Stage

Add and commit following Conventional Commits 1.0.0:

```bash
git add src/ tests/
git commit -s -m "feat: describe what changed"
```

The `-s` flag adds the required `Signed-off-by` footer (see
[CONTRIBUTING.md](CONTRIBUTING.md)).

### 5. Deploy

Maintainers only. Tag the release, push, and publish on GitHub so
that `rev: vX.Y.Z` in student configs resolves correctly:

```bash
git tag -a v0.2.0 -m "release: v0.2.0"
git push origin main --tags
```

Then create a GitHub release from the tag so pre-commit can fetch
and install the package via `language: python`.

---

### Project layout

```
src/ganesha/
  __init__.py       public API (re-exports checks + config)
  __main__.py       python -m ganesha entry point
  cli.py            thin CLI wrapper using argparse
  config.py         reads .ganesha.toml (tomllib/tomli)
  checks/
    norminette.py   subprocess wrapper
    compiler.py     cc -Wall -Wextra -Werror -fsyntax-only
    forbidden.py    pure-Python regex scan, no subprocess
    commit_msg.py   CC 1.0.0 validator, gamification layer
    readme.py       README.md structural validator
tests/
  test_forbidden.py   integration tests via lib API + tmp_path
  test_commit_msg.py  integration tests via lib API + tmp_path
  test_readme.py      integration tests via lib API + tmp_path
  test_cli.py         CLI tests via subprocess
  fixtures/           valid.c  norm_error.c  compile_error.c  forbidden.c
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution
workflow.

---

## Submodules

This repository includes two optional testing tools as git
submodules under `tools/`:

| Submodule | Path | Description |
|-----------|------|-------------|
| [Francinette][francinette] | `tools/francinette` | Python piscine tester |
| [mini-moulinette][mini-moulinette] | `tools/mini-moulinette` | Local moulinette runner |

When cloning, initialise the submodules in one step:

```bash
git clone --recurse-submodules <repo-url>
```

After cloning, initialise submodules with:

```bash
git submodule update --init --recursive
```

If the submodules are out of sync with the commit this repository
tracks (e.g. after `git pull`), bring them back in sync with:

```bash
git submodule update --init --recursive
```

To update them to their latest upstream commit:

```bash
git submodule update --remote --merge
```

---

## Related projects

| Project | Description |
|---------|-------------|
| [Francinette][francinette] | Python piscine tester — the older sibling |
| [mini-moulinette][mini-moulinette] | Local moulinette runner for 42 projects |
| [Norminette][norminette] | Official 42 School code style checker |

---

## Optional vim plugins

Monsieur Ganesha recommends vim. The following plugins make the
experience less painful — which is not the same as comfortable.

> VSCode is a possible path. I do not recommend it.
> It corrects your mistakes before you make them.
> It also hides them. The exam terminal does neither.
>
> — Monsieur Ganesha, Directeur, [Conservatoire de Paris XLII][conservatoire]

### vim

| Plugin | What it adds |
|--------|--------------|
| [norminette-vim][norminette-vim] | Norminette error highlighting via Syntastic |
| [ALE][ale] | Async linting — configurable to run norminette on save |
| [vim-fugitive][fugitive] | Git commands and status inside vim |

### neovim

| Plugin | What it adds |
|--------|--------------|
| [norminette42.nvim][norminette42-nvim] | Norminette diagnostics via LSP |
| [norminette-lint.nvim][norminette-lint-nvim] | Norminette lint integration |
| [42norm.nvim][42norm-nvim] | 42 norm highlighting for neovim |

---

## License

MIT. See [LICENSE](LICENSE).

[conservatoire]:        https://42.fr "École 42, Paris — XLII in Roman numerals"
[uv]:                   https://docs.astral.sh/uv
[francinette]:          https://github.com/xicodomingues/francinette
[mini-moulinette]:      https://github.com/k11q/mini-moulinette
[norminette]:           https://github.com/42School/norminette
[norminette-vim]:       https://github.com/alexandregv/norminette-vim
[ale]:                  https://github.com/dense-analysis/ale
[fugitive]:             https://github.com/tpope/vim-fugitive
[norminette42-nvim]:    https://github.com/hardyrafael17/norminette42.nvim
[norminette-lint-nvim]: https://github.com/FtVim/norminette-lint.nvim
[42norm-nvim]:          https://github.com/MoulatiMehdi/42norm.nvim
