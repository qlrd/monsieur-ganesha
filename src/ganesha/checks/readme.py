"""README validator for staged Markdown files.

This module implements the ``readme`` pre-commit hook.  It checks
every staged ``README.md`` file for common issues and prints
actionable correction proposals so students know exactly what to fix.

Checks performed (in order)
----------------------------
1. **Empty file** — a README with no content is flagged immediately.
2. **Missing title** — the file must contain at least one ATX heading
   (a line that starts with ``# ``).

Output format
-------------
Each issue is printed to *stderr* in the form::

    README.md: empty file — add at least a title and a short description.
    path/to/README.md: no title found — add "# <Project Name>" as the first line.

The hook exits with code 1 when any issue is found so the commit is
blocked until the student has addressed all reported problems.

Design decisions
----------------
* Only files whose basename is ``README.md`` (case-sensitive) are
  checked; other ``.md`` files are silently ignored.  This mirrors
  the ``files`` filter in ``.pre-commit-hooks.yaml``.
* The heading check only looks for ATX headings (``#``), not
  Setext-style underline headings, because ATX headings are the
  convention recommended for 42 school piscine projects.
* Multi-line detection is not needed: a single pass over the
  splitlines is sufficient.
"""

import sys
from collections.abc import Sequence
from pathlib import Path


def check(files: Sequence[str]) -> bool:
    """Validate ``README.md`` files for common structural issues.

    Scans each file whose basename is ``README.md`` and reports:

    * Empty files (zero non-whitespace content).
    * Files that have no ATX heading (``# ...``).

    A correction proposal is printed alongside every issue so the
    student knows what change is needed.

    Args:
        files: Sequence of file paths passed by pre-commit.  Only
            entries whose :func:`~pathlib.Path.name` equals
            ``"README.md"`` are inspected; everything else is ignored.

    Returns:
        ``True`` if every ``README.md`` file passes all checks.
        ``False`` if at least one issue is detected.  All issues are
        printed to *stderr* before returning.

    Examples:
        Typical call from the CLI layer::

            from ganesha.checks import readme

            ok = readme.check(["README.md"])

        In tests, write a temporary ``README.md`` and call the
        function directly::

            def test_empty_readme_fails(tmp_path):
                p = tmp_path / "README.md"
                p.write_text("")
                assert check([str(p)]) is False

            def test_readme_without_title_fails(tmp_path):
                p = tmp_path / "README.md"
                p.write_text("some content without a heading\\n")
                assert check([str(p)]) is False

            def test_valid_readme_passes(tmp_path):
                p = tmp_path / "README.md"
                p.write_text("# My Project\\n\\nA short description.\\n")
                assert check([str(p)]) is True
    """
    readme_files = [f for f in files if Path(f).name == "README.md"]

    if not readme_files:
        return True

    errors: list[str] = []

    for filepath in readme_files:
        try:
            content = Path(filepath).read_text(encoding="utf-8")
        except OSError as e:
            print(
                f"ERROR: cannot read {filepath}: {e}",
                file=sys.stderr,
            )
            errors.append(f"{filepath}: read error")
            continue

        if not content.strip():
            errors.append(
                f"{filepath}: empty file"
                " — add at least a title and a short description."
            )
            continue

        has_title = any(line.startswith("# ") for line in content.splitlines())
        if not has_title:
            errors.append(
                f"{filepath}: no title found"
                ' — add "# <Project Name>" as the first line.'
            )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return False

    return True
