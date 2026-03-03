"""Forbidden-function scanner for staged C files.

This module implements the ``forbidden-functions`` pre-commit hook.
It scans every staged ``.c`` file for calls to functions listed in
the ``[forbidden] functions`` key of ``.ganesha.toml``.

Detection strategy
------------------
The scanner builds a single regex of the form::

    \\b(func1|func2|...)\\s*\\(

The ``\\b`` word boundary before the function name ensures that a
prefixed name such as ``ft_printf`` is **not** flagged when ``printf``
is forbidden.  The ``\\s*\\(`` suffix ensures that a call written
with a space before the opening parenthesis (``printf ("hi")``) is
still caught.

Single-line comments (``// ...``) are stripped from each line before
scanning.  Multi-line ``/* */`` comments are **not** stripped; this
is a known limitation.

All violations are collected before returning so the student sees
every problem in a single run, not just the first one.

Error output format::

    path/to/file.c:42: função proibida 'printf'

The output goes to *stderr*; the hook exits with code 1 when any
violation is found.

Example ``.ganesha.toml`` section::

    [forbidden]
    functions = ["printf", "malloc", "realloc", "free", "calloc"]
"""

import re
import sys
from collections.abc import Sequence
from pathlib import Path


def check(files: Sequence[str], forbidden: Sequence[str]) -> bool:
    """Scan ``.c`` files for calls to forbidden functions.

    Builds a word-boundary-anchored regex from *forbidden*, then
    reads each ``.c`` file in *files* and reports every line that
    contains a call to any of the listed functions.

    Only files whose name ends with ``.c`` are scanned; other file
    types (headers, Makefiles, …) are silently ignored.  This mirrors
    the ``files: '\\.c$'`` filter in ``.pre-commit-hooks.yaml``.

    Args:
        files: Sequence of file paths passed by pre-commit.  Typically
            the list of staged files filtered by pre-commit to include
            only those matching ``\\.c$``.  Non-``.c`` entries are
            skipped automatically.
        forbidden: Sequence of C function names to forbid, e.g.
            ``["printf", "malloc"]``.  When empty the function returns
            ``True`` immediately without reading any files.

    Returns:
        ``True`` if no forbidden calls are found (or *forbidden* is
        empty, or no ``.c`` files are present).
        ``False`` if at least one violation is detected.  All
        violations are printed to *stderr* before returning.

    Examples:
        Typical call from the CLI layer::

            from ganesha.checks.forbidden import check
            from ganesha.config import load_config

            cfg = load_config()
            ok = check(staged_files, cfg.forbidden.functions)

        In tests, write a temporary ``.c`` file::

            def test_detects_forbidden_call(tmp_path):
                p = tmp_path / "main.c"
                p.write_text('int main(void) { printf("hi"); }\\n')
                assert check([str(p)], ["printf"]) is False

            def test_ft_prefix_not_flagged(tmp_path):
                p = tmp_path / "ft.c"
                p.write_text("int ft_printf(char *s) { return 0; }\\n")
                assert check([str(p)], ["printf"]) is True

    Notes:
        * The regex uses :func:`re.escape` on each function name, so
          names containing regex metacharacters are handled safely.
        * Single-line comments (``// …``) are stripped by splitting on
          ``//`` and taking the first segment.  This means a comment
          like ``/* printf("x"); */`` would still be scanned if it
          appears on a line that also contains real code before ``//``.
        * Unreadable files are reported and counted as failures so the
          hook exits with a non-zero code.
    """
    if not forbidden:
        return True

    c_files = [f for f in files if f.endswith(".c")]

    if not c_files:
        return True

    alternation = "|".join(re.escape(f) for f in forbidden)
    pattern = re.compile(rf"\b({alternation})\s*\(")

    errors: list[str] = []

    for filepath in c_files:
        try:
            content = Path(filepath).read_text(encoding="utf-8")
        except OSError as e:
            print(
                f"ERRO: não foi possível ler {filepath}: {e}",
                file=sys.stderr,
            )
            errors.append(f"{filepath}: erro de leitura")
            continue

        for lineno, line in enumerate(content.splitlines(), start=1):
            code = line.split("//")[0]
            for match in pattern.finditer(code):
                func = match.group(1)
                errors.append(f"{filepath}:{lineno}: função proibida '{func}'")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return False

    return True
