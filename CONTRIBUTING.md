# Contributing

Thank you for contributing to monsieur-ganesha.

---

## Before you start

Open an issue to discuss significant changes before writing code.
For small fixes (typos, obvious bugs) a direct pull request is fine.

---

## Getting started

Fork the repository, then clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/monsieur-ganesha
cd monsieur-ganesha
```

Install all dependencies (including dev tools) and run the
full test suite:

```bash
uv sync --dev
pytest
```

All tests must pass before opening a pull request.

---

## Code style

- Format with `black src/ tests/` before every commit.
- Sort imports with `isort src/ tests/`.
- Lint with `pylint src/ganesha/` — zero warnings allowed.
- Keep prose (comments, docs, Markdown) at or below 72
  characters per line.
- Do not add unnecessary dependencies. Prefer stdlib where
  possible.

Run all checks at once:

```bash
black --check src/ tests/
isort --check-only src/ tests/
pylint src/ganesha/
```

---

## Commit messages

This project uses **Conventional Commits 1.0.0**.

```
<type>[(<scope>)][!]: <description>
```

- The subject line must not exceed 72 characters.
- Use the imperative mood: "add support" not "added support".
- Types: `feat` `fix` `docs` `style` `refactor` `perf` `test`
  `build` `ci` `chore` `revert` `init`
- Append `!` after the type/scope to signal a breaking change.
  Add a body explaining why.

Examples:

```
feat(norminette): add support for custom flags
fix: handle empty file list in forbidden check
docs: update configuration section in README.md
test: add integration test for commit-msg strip behaviour
refactor: extract subprocess helper into shared module
feat!: change exit code from 2 to 3 on internal errors
```

Set your editor to vim so `git commit` opens correctly:

```bash
git config --global core.editor vim
```

---

## Adding a new hook

1. Create `src/ganesha/checks/<name>.py` with a public
   `check` function.
2. Export it in `src/ganesha/checks/__init__.py`.
3. Add a subcommand in `src/ganesha/cli.py` and wire it
   in `main()`.
4. Register the hook in `.pre-commit-hooks.yaml`:

   ```yaml
   - id: new-hook
     name: New Hook
     entry: ganesha new-hook
     language: python
     files: '\.(c|h)$'
     pass_filenames: true
   ```

5. Write tests in `tests/test_<name>.py`.
6. Update `CHANGELOG.md` under `[Unreleased]`.

---

## Review process

Maintainers review pull requests using tACK (tested ACK).

**tACK** — confirms the branch passes locally (first review).
**re-tACK** — re-posted after the author addresses feedback.

Use `'''` as code-block delimiters in review comments —
backtick fences require escaping in shell heredocs.

tACK template:

```
tACK <sha>

Tested locally against branch tip:

'''
OS:     <uname -sr>
cc:     <cc --version | head -1>
Python: <python --version>

uv sync --dev --frozen   ✓
black --check            ✓
isort --check-only       ✓
pylint src/ganesha/      ✓
pytest                   ✓  (<N> passed)
'''

<one-line summary of what the branch does>. Ready to merge.
```

re-tACK template (same; note what changed after the sha):

```
re-tACK <sha>

Tested locally against branch tip (after <what changed>):

'''
OS:     <uname -sr>
cc:     <cc --version | head -1>
Python: <python --version>

uv sync --dev --frozen   ✓
black --check            ✓
isort --check-only       ✓
pylint src/ganesha/      ✓
pytest                   ✓  (<N> passed)
'''

<one-line summary of what the branch does>. Ready to merge.
```

Commands to fill in the template:

```bash
uname -sr                  # OS line (kernel, no username)
cc --version | head -1     # cc line
python --version           # Python line
```

---

## Submitting a pull request

1. Create a branch from `main`:

   ```bash
   git checkout -b feat/my-feature
   ```

2. Make your changes and add or update tests as needed.
3. Ensure all checks pass locally:

   ```bash
   uv sync --dev --frozen
   black --check src/ tests/
   isort --check-only src/ tests/
   pylint src/ganesha/
   pytest
   ```

4. Push your branch and open a pull request against `main`.
5. Describe what the PR does, why it is needed, and how it
   was tested. Reference any related issues.

Pull requests require at least one tACK from a maintainer
before merging. The CI pipeline must be green.

---

## Developer Certificate of Origin

All contributions must include a `Signed-off-by` footer. Add it
automatically with:

```bash
git commit -s
```

By signing off you certify that you have the right to submit
your work under the terms of the MIT License. See the full
[DCO](https://developercertificate.org/).

---

## Reporting bugs

Open an issue at:

```
https://github.com/qlrd/monsieur-ganesha/issues
```

Include:

- Your operating system (`uname -sr`)
- Python version (`python --version`)
- uv version (`uv --version`)
- `cc` version (`cc --version | head -1`)
- `pre-commit` version (`pre-commit --version`)
- Exact steps to reproduce the problem
- Expected behaviour vs. actual behaviour
- Any relevant output or error messages

---

## License

By contributing you agree that your work will be released under
the terms of the [MIT License](LICENSE).
