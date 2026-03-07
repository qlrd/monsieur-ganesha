"""Check modules for Monsieur Ganesha.

This package exposes the five pre-commit check modules as a flat
namespace so that the CLI and tests can import them uniformly::

    from ganesha import checks

    checks.norminette.check(files)
    checks.compiler.check(files)
    checks.forbidden.check(files, forbidden_list)
    checks.commit_msg.check(file_path, pattern)
    checks.readme.check(files)

Modules
-------
norminette
    Wraps the ``norminette`` CLI to enforce the 42 Norme on ``.c``
    and ``.h`` files.
compiler
    Wraps ``cc -fsyntax-only`` to catch compilation errors before
    commit.
forbidden
    Pure-Python regex scanner that detects calls to functions
    forbidden by the current module's ``.ganesha.toml``.
commit_msg
    Validates the commit message subject against Conventional Commits
    1.0.0 (or a custom pattern) and applies a gamification layer.
readme
    Validates ``README.md`` files for common structural issues and
    prints actionable correction proposals.
"""

from ganesha.checks import commit_msg, compiler, forbidden, norminette, readme

__all__ = ["commit_msg", "compiler", "forbidden", "norminette", "readme"]
