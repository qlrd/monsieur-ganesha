"""Norminette wrapper for staged C and header files.

This module implements the ``norminette`` pre-commit hook.  It invokes
the ``norminette`` command-line tool on every staged ``.c`` and ``.h``
file and forwards its output to *stderr*.

What is norminette?
-------------------
`Norminette <https://github.com/42School/norminette>`_ is the official
style checker used at École 42.  It enforces the *Norme* — a strict
coding standard that covers indentation, line length, function length,
variable placement, and more.  Code that does not comply with the
Norme is rejected by the school's evaluation system (moulinette).

Norminette must be installed separately::

    pip install norminette

The hook passes all staged ``.c`` and ``.h`` files to a single
``norminette`` invocation rather than one invocation per file.  This
matches the behaviour of running ``norminette`` manually on a
directory and produces the familiar grouped output.

Error output
------------
When norminette finds style violations it writes them to *stdout*.
This module re-prints that output to *stderr* so that it appears in
the pre-commit hook output stream alongside messages from other hooks.

If norminette is not installed the hook prints a friendly installation
hint and exits with code 1.
"""

import subprocess
import sys
from collections.abc import Sequence


def check(
    files: Sequence[str], *, general_mode: bool = False, strict: bool = True
) -> bool:
    """Run ``norminette`` on all ``.c`` and ``.h`` files in *files*.

    Filters *files* to include only those ending in ``.c`` or ``.h``,
    then passes them all to a single ``norminette`` subprocess call.

    Args:
        files: Sequence of file paths provided by pre-commit.  Files
            not ending in ``.c`` or ``.h`` are ignored.  When the
            filtered list is empty the function returns ``True``
            immediately (nothing to check).

    Returns:
        ``True`` if norminette exits with code 0 (all files comply
        with the Norme).
        ``True`` if *files* contains no ``.c`` or ``.h`` files.
        ``False`` if norminette reports any violations.  The violation
        output is forwarded to *stderr*.
        ``False`` if norminette is not installed.  An installation
        hint is printed to *stderr*.

    Examples:
        Typical call from the CLI layer::

            from ganesha.checks.norminette import check

            ok = check(staged_files)

        In tests with fixture files::

            import pathlib
            fixtures = pathlib.Path("tests/fixtures")

            def test_valid_file_passes():
                # valid.c complies with the Norme
                ok = check([str(fixtures / "valid.c")])
                assert ok is True  # may be skipped if norminette absent

            def test_norm_error_fails():
                ok = check([str(fixtures / "norm_error.c")])
                assert ok is False

    Notes:
        * All matching files are passed to a **single** norminette
          invocation (``norminette f1.c f2.c …``).  This is faster
          than one invocation per file and produces the same output
          format that students expect from running norminette manually.
        * norminette writes its violation report to *stdout*, not
          *stderr*.  Both streams are captured and forwarded to
          *stderr* of the hook process.
    """
    c_files = [f for f in files if f.endswith((".c", ".h"))]

    if not c_files:
        return True

    cmd = ["norminette"]
    if general_mode:
        cmd.append("--use-tabsize=4")
    cmd.extend(c_files)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        if general_mode:
            print(
                "INFO: norminette não encontrado; check advisory ignorado.",
                file=sys.stderr,
            )
            return True
        print(
            "ERRO: norminette não encontrado.\nInstale com: pip install norminette",
            file=sys.stderr,
        )
        return False

    if result.returncode != 0:
        print(result.stdout, end="", file=sys.stderr)
        print(result.stderr, end="", file=sys.stderr)
        if general_mode and not strict:
            return True
        return False

    return True
