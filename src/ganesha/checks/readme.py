"""README validator for staged Markdown files.

This module implements the ``readme`` pre-commit hook.  It checks
every staged ``README.md`` file for common issues and prints
actionable correction proposals so students know exactly what to fix.

This hook is **non-blocking**: it never prevents a commit.  Files that
pass all checks earn an ``+XP`` message on *stderr*; files with issues
receive advisory messages that describe what to improve, but the commit
proceeds regardless.

Checks performed (in order)
----------------------------
1. **Empty file** — advisory message to add a title and description.
2. **Missing title** — advisory message when the file contains no ATX
   heading (a line that starts with ``# ``).
3. **Missing file-descriptor documentation** — advisory message when
   the file does not mention which file descriptors the program uses.
   Accepted keywords: ``stdin``, ``stdout``, ``stderr``,
   ``STDIN_FILENO``, ``STDOUT_FILENO``, ``STDERR_FILENO``,
   ``file descriptor``, ``fd 0``, ``fd 1``, ``fd 2`` (and variants
   without the space, e.g. ``fd0``).  Matching is case-insensitive.

Output format
-------------
Advisory messages are printed to *stderr* in the form::

    README.md: empty file — add at least a title and a short
        description (+XP available).
    path/to/README.md: no title found — add "# <Project Name>"
        as the first line (+XP available).
    path/to/README.md: no file descriptor usage documented — mention which
        file descriptors your program reads from and writes to
        (0=stdin, 1=stdout, 2=stderr) (+XP available).

When a file passes all checks::

    path/to/README.md: well documented — +XP.

The hook always exits with code 0 so it never blocks a commit.

Design decisions
----------------
* Only files whose basename is ``README.md`` (case-sensitive) are
  checked; other ``.md`` files are silently ignored.  This mirrors
  the ``files`` filter in ``.pre-commit-hooks.yaml``.
* The heading check only looks for ATX headings (``#``), not
  Setext-style underline headings, because ATX headings are the
  convention recommended for 42 school piscine projects.
* File-descriptor detection uses a word-boundary-anchored regex so
  that incidental occurrences of "fd" in unrelated words are not
  counted.  The pattern matches the standard POSIX names as well as
  the numeric shorthand (``fd0``/``fd 1``).
* Multi-line detection is not needed: a single pass over the
  splitlines is sufficient.
* The hook is kept non-blocking because a missing README must never
  prevent a student from committing work in progress.  Documentation
  quality is encouraged through positive reinforcement (+XP) rather
  than gatekeeping.
* ``UnicodeDecodeError`` is caught alongside ``OSError`` so that a
  binary or non-UTF-8 file never propagates to the CLI's
  ``ValueError`` handler (which would exit with code 2 and block the
  commit).
* When the hook runs with no staged ``README.md`` files (via
  ``always_run: true``), it looks for an unstaged ``README.md`` on
  disk and rewards the student with +XP for creating one — even in
  exercises that forbid extra files.
"""

import re
import sys
from collections.abc import Sequence
from pathlib import Path

_FD_PATTERN = re.compile(
    r"\b("
    r"stdin|stdout|stderr"  # POSIX stream names
    r"|STDIN_FILENO|STDOUT_FILENO|STDERR_FILENO"  # C constants
    r"|file\s+descriptor"  # generic English phrase
    r"|fd\s*[012]"  # numeric shorthand: fd0, fd 1, fd2, …
    r")\b",
    re.IGNORECASE,
)


def check(files: Sequence[str]) -> bool:
    """Validate ``README.md`` files for common structural issues.

    Scans each file whose basename is ``README.md`` and prints advisory
    messages to *stderr*:

    * Empty files → tip to add a title and description.
    * Files with no ATX heading → tip to add ``# <Project Name>``.
    * Files that do not document file-descriptor usage → tip to mention
      stdin / stdout / stderr.
    * Files that pass all checks → ``+XP`` reward message.

    When no ``README.md`` files are passed (none staged) but one exists
    on disk, the student receives a ``+XP`` message for documenting
    even without staging.

    The function **always returns** ``True``.  It never blocks a commit;
    documentation quality is encouraged through positive reinforcement
    rather than gatekeeping.

    Args:
        files: Sequence of file paths passed by pre-commit.  Only
            entries whose :func:`~pathlib.Path.name` equals
            ``"README.md"`` are inspected; everything else is ignored.

    Returns:
        Always ``True`` — this hook is non-blocking.  Advisory messages
        are printed to *stderr* but do not affect the exit code.

    Examples:
        Typical call from the CLI layer::

            from ganesha.checks import readme

            ok = readme.check(["README.md"])  # always True

        In tests, verify the advisory messages instead of the return
        value::

            def test_empty_readme_warns(tmp_path, capsys):
                p = tmp_path / "README.md"
                p.write_text("")
                assert check([str(p)]) is True
                assert "(+XP available)" in capsys.readouterr().err

            def test_valid_readme_earns_xp(tmp_path, capsys):
                p = tmp_path / "README.md"
                p.write_text(
                    "# My Project\\n\\n"
                    "Writes to stdout (fd 1).\\n"
                )
                assert check([str(p)]) is True
                assert "+XP" in capsys.readouterr().err
    """
    readme_files = [f for f in files if Path(f).name == "README.md"]

    if not readme_files:
        # No staged README.md — check if one exists on disk anyway.
        # Students who create a README without staging it (e.g. in
        # exercises that forbid extra files) still earn +XP.
        if Path("README.md").is_file():
            print(
                "  README.md found but not staged — +XP for documenting.",
                file=sys.stderr,
            )
        return True

    for filepath in readme_files:
        try:
            content = Path(filepath).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            print(
                f"ERROR: cannot read {filepath}: {e}",
                file=sys.stderr,
            )
            continue

        tips: list[str] = []

        if not content.strip():
            tips.append(
                f"{filepath}: empty file"
                " — add at least a title and a short description"
                " (+XP available)."
            )
        else:
            has_title = any(line.startswith("# ") for line in content.splitlines())
            if not has_title:
                tips.append(
                    f"{filepath}: no title found"
                    ' — add "# <Project Name>" as the first line'
                    " (+XP available)."
                )

            if not _FD_PATTERN.search(content):
                tips.append(
                    f"{filepath}: no file descriptor usage documented"
                    " — mention which file descriptors your program"
                    " reads from and writes to"
                    " (0=stdin, 1=stdout, 2=stderr) (+XP available)."
                )

        if tips:
            print("\n".join(tips), file=sys.stderr)
        else:
            print(f"  {filepath}: well documented — +XP.", file=sys.stderr)

    return True
