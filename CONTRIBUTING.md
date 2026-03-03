# Contributing

Thank you for contributing to monsieur-piscinette.

---

## Before you start

Open an issue to discuss significant changes before writing code.
For small fixes (typos, obvious bugs) a direct pull request is fine.

---

## Getting started

Fork the repository, then clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/monsieur-piscinette
cd monsieur-piscinette
```

Build the project and run the full test suite:

```bash
cargo build
cargo test
```

All tests must pass before opening a pull request.

---

## Code style

- Format Rust code with `cargo fmt` before every commit.
- Lint with `cargo clippy -- -D warnings`. No warnings are allowed.
- Keep prose (comments, docs, Markdown) at or below 72 characters
  per line.
- Do not add unnecessary dependencies. Prefer `std` where possible.

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
feat(norminette): add support for custom gcc flags
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

## Developer Certificate of Origin

All contributions must include a `Signed-off-by` footer. Add it
automatically with:

```bash
git commit -s
```

By signing off you certify that you have the right to submit your
work under the terms of the MIT License. See the full
[DCO](https://developercertificate.org/).

---

## Adding a new hook

1. Create `src/checks/new_hook.rs` with a public `check` function.
2. Export it in `src/checks/mod.rs`:

   ```rust
   pub mod new_hook;
   ```

3. Add a `Command` variant in `src/main.rs` and wire it in `run()`.
4. Register the hook in `.pre-commit-hooks.yaml`:

   ```yaml
   - id: new-hook
     name: New Hook
     entry: piscinette new-hook
     language: rust
     files: '\.(c|h)$'
     pass_filenames: true
   ```

5. Write unit tests inside the module (`#[cfg(test)]`) and an
   integration test file in `tests/test_new_hook.rs`.
6. Update `CHANGELOG.md` under `[Unreleased]`.

---

## Submitting a pull request

1. Create a branch from `main`:

   ```bash
   git checkout -b feat/my-feature
   ```

2. Make your changes and add or update tests as needed.
3. Ensure all CI checks pass locally:

   ```bash
   cargo fmt --check
   cargo clippy -- -D warnings
   cargo test
   ```

4. Push your branch and open a pull request against `main`.
5. Describe what the PR does, why it is needed, and how it was
   tested. Reference any related issues.

Pull requests require at least one review from a maintainer before
merging. The CI pipeline must be green.

---

## Reporting bugs

Open an issue at:

```
https://github.com/qlrd/monsieur-piscinette/issues
```

Include:

- Your operating system and architecture
- Rust version (`rustc --version`)
- `pre-commit` version (`pre-commit --version`)
- Exact steps to reproduce the problem
- Expected behaviour vs. actual behaviour
- Any relevant output or error messages

---

## License

By contributing you agree that your work will be released under the
terms of the [MIT License](LICENSE).
