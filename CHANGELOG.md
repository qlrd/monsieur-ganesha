# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog][keepachangelog] and this
project adheres to [Semantic Versioning][semver].

---

## [Unreleased]

---

## [0.1.0] - 2025-03-02

### Added

- `norminette` hook: validates staged `.c` and `.h` files against the
  42 school norm by running the `norminette` CLI.
- `c-compiler` hook: checks syntax of each staged `.c` file with
  `cc -Wall -Wextra -Werror -fsyntax-only`. Files are compiled
  individually so all errors are reported before the hook exits.
- `forbidden-functions` hook: scans staged `.c` files for calls to
  functions listed in `.ganesha.toml` using word-boundary regex.
  `ft_printf` is not flagged when `printf` is forbidden.
  Single-line `//` comments are stripped before scanning.
- `commit-message` hook: validates the first meaningful line of the
  commit message against a configurable regex pattern. Git comment
  lines (starting with `#`) are stripped automatically.
  Default pattern: `^(ex|rush|exam)\d+: .+`
- `.ganesha.toml` configuration file: per-module forbidden
  function list and custom commit message pattern.
- `install.sh`: setup script that installs dependencies, creates
  `.pre-commit-config.yaml` and `.ganesha.toml` templates, and
  activates the hooks in the target repository.
- Mascot SVG (`mascot.svg`): Monsieur Piscinette, drawn in a Roger
  Rabbit adult cartoon style.
- Full test suite: 58 tests covering unit, integration, and CLI
  behaviour via `assert_cmd`.

---

[Unreleased]: https://github.com/qlrd/monsieur-ganesha/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/qlrd/monsieur-ganesha/releases/tag/v0.1.0
[keepachangelog]: https://keepachangelog.com/en/1.1.0/
[semver]: https://semver.org/spec/v2.0.0.html
