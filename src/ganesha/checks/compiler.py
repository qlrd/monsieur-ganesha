"""C syntax checker via ``cc -fsyntax-only``.

This module implements the ``c-compiler`` pre-commit hook.  It invokes
``cc`` on each staged ``.c`` file with the flags::

    -Wall -Wextra -Werror -fsyntax-only

The ``-fsyntax-only`` flag tells cc to parse and type-check the file
without emitting any object code, which avoids two common problems:

1. **No ``.o`` conflicts** — multiple staged files can be checked
   independently without colliding on a shared ``a.out`` or object
   file.
2. **No missing headers** — when only some files are staged, the
   include files referenced by other staged (but not yet written)
   files may not be available; ``-fsyntax-only`` tolerates this
   better than a full compilation.

Each file is compiled in a separate subprocess call so that errors in
one file do not suppress error output from subsequent files.  All
failures are printed before the function returns.

Error output
------------
cc writes its error messages to *stderr* by default; this module
captures them and re-prints them to *stderr* unchanged.  The student
sees the familiar cc output they would get from running cc manually.

If cc is not installed the hook prints an installation hint and exits
with code 1 instead of raising an unhandled :class:`FileNotFoundError`.
"""

import subprocess
import sys
from collections.abc import Sequence


def check(files: Sequence[str]) -> bool:
    """Run ``cc -Wall -Wextra -Werror -fsyntax-only`` on each ``.c`` file.

    Iterates over *files*, skips non-``.c`` entries, and invokes cc
    once per ``.c`` file.  Collects the results and returns ``False``
    if any file fails.

    The function purposefully does **not** short-circuit on the first
    failure: all files are checked so the student sees all errors in a
    single pre-commit run.

    Args:
        files: Sequence of file paths as provided by pre-commit.  Only
            files ending in ``.c`` are compiled; all others are skipped
            silently.  An empty list (or a list with no ``.c`` files)
            returns ``True`` immediately.

    Returns:
        ``True`` if every ``.c`` file compiles without errors.
        ``True`` if *files* is empty or contains no ``.c`` files.
        ``False`` if any file fails to compile.  cc's error output is
        printed to *stderr* for each failing file.
        ``False`` if cc is not found; an installation hint is printed
        to *stderr*.

    Examples:
        Typical call from the CLI layer::

            from ganesha.checks.compiler import check

            ok = check(staged_c_files)

        In tests with fixture files::

            import pathlib
            fixtures = pathlib.Path("tests/fixtures")

            def test_valid_file_passes():
                ok = check([str(fixtures / "valid.c")])
                assert ok is True

            def test_compile_error_fails():
                ok = check([str(fixtures / "compile_error.c")])
                assert ok is False

    Notes:
        * Passing ``check=False`` to :func:`subprocess.run` prevents
          Python from raising :class:`subprocess.CalledProcessError`
          on non-zero exit codes; the error is handled manually.
        * ``capture_output=True`` redirects both stdout and stderr from
          cc into the :class:`subprocess.CompletedProcess` result so
          they can be forwarded to *stderr* of the hook process.
    """
    c_files = [f for f in files if f.endswith(".c")]

    if not c_files:
        return True

    all_passed = True

    for c_file in c_files:
        try:
            result = subprocess.run(
                ["cc", "-Wall", "-Wextra", "-Werror", "-fsyntax-only", c_file],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            print(
                "ERRO: cc não encontrado.\n"
                "Instale: sudo apt install build-essential "
                "(ou equivalente)",
                file=sys.stderr,
            )
            return False

        if result.returncode != 0:
            print(result.stderr, end="", file=sys.stderr)
            print(result.stdout, end="", file=sys.stderr)
            all_passed = False

    return all_passed
