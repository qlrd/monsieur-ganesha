"""Monsieur Ganesha — pre-commit hooks for 42 school piscine.

This package provides four pre-commit hooks that run automatically
before every ``git commit`` in a 42 piscine repository:

``norminette``
    Verifies that staged ``.c`` and ``.h`` files comply with the
    42 Norme using the official ``norminette`` tool.

``c-compiler``
    Runs ``gcc -Wall -Wextra -Werror -fsyntax-only`` on each staged
    ``.c`` file to catch compilation errors before they reach the
    repository.

``forbidden-functions``
    Scans staged ``.c`` files for calls to functions listed in the
    ``[forbidden] functions`` key of ``.ganesha.toml``.

``commit-message``
    Validates the commit message subject against Conventional Commits
    1.0.0 (or a custom pattern) and rejects non-conforming messages
    with a terse ``REJECTED.`` to encourage self-discovery.

Public API
----------
The package re-exports two top-level namespaces:

:mod:`ganesha.checks`
    The four check modules: ``norminette``, ``compiler``,
    ``forbidden``, ``commit_msg``.

:mod:`ganesha.config`
    :func:`~ganesha.config.load_config` and the
    :class:`~ganesha.config.Config` dataclass family.

Typical import pattern for library consumers::

    from ganesha import checks, config

    cfg = config.load_config()
    ok = checks.forbidden.check(staged_files, cfg.forbidden.functions)

Pre-commit hook consumers install this package via
``.pre-commit-config.yaml`` and never import it directly.
"""

from ganesha import checks, config

__all__ = ["checks", "config"]
