"""Commit-message validator — Conventional Commits 1.0.0.

This module implements the ``commit-message`` pre-commit hook.  It
reads the file that git writes to ``.git/COMMIT_EDITMSG``, strips git
comment lines (lines that start with ``#``), and validates the first
non-empty line (the *subject*) against a configurable regular
expression.

Default format
--------------
The default pattern enforces `Conventional Commits 1.0.0
<https://www.conventionalcommits.org/>`_::

    <type>[(<scope>)][!]: <description>

Where ``type`` is one of:

    feat · fix · docs · style · refactor · perf · test
    build · ci · chore · revert · init · lore

The ``lore`` type is for commits that add in-world narrative
context — mascot artwork, project lore, character descriptions.
It is not a standard CC 1.0.0 type; it is an extension accepted
by monsieur-ganesha for project-level repositories.

The ``(<scope>)`` field accepts any label, including 42-school
exercise identifiers such as ``ex00``, ``rush00``, ``exam01``.

Examples of valid subjects::

    feat: add norminette timeout option
    fix(forbidden): handle empty file list
    feat!: drop support for gcc older than 12
    docs(readme): update installation section
    feat(ex00): implement ft_putchar
    fix(rush00): handle edge case
    feat(ex00)!: rewrite with different algorithm

Custom pattern
--------------
Students can override the pattern in ``.ganesha.toml`` to use the
bare 42-school ``ex00: description`` format (without a CC type
prefix) instead::

    [commit]
    pattern = "^(ex|rush|exam)\\\\d+: .+"

When a custom pattern is active the gamification layer is disabled.

Gamification layer
------------------
When the default pattern is active, accepted commits trigger
informational messages on *stderr*:

* ``docs`` / ``chore``  → francinette approves this commit.
* ``test``              → you discovered the ultimate commit type.
* ``feat!`` with body   → breaking change explained — +XP.
* ``feat!`` without body→ tip: explain why this breaks to earn +XP.

These messages are purely informational and do **not** affect the
hook exit code.

Security posture
----------------
Rejection messages are intentionally terse — ``REJECTED.`` — with no
format hints.  Students are expected to discover the correct format
themselves.  This is by design.
"""

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

DEFAULT_PATTERN = (
    r"^(feat|fix|docs|style|refactor|perf|test"
    r"|build|ci|chore|revert|init|lore)(\([^)]+\))?(!)?: \S.*"
)
"""Conventional Commits 1.0.0 validation regex (extended).

Matches subjects of the form::

    <type>[(<scope>)][!]: <non-empty description>

Accepted types: the standard CC 1.0.0 set plus ``lore``.
``lore`` is for in-world narrative commits (mascot, character
descriptions, project lore) used in project-level repositories.

Group indices (used internally by the gamification layer):

* Group 1 — commit type (e.g. ``feat``, ``fix``, ``test``, ``lore``).
* Group 2 — optional scope including parentheses (e.g. ``(cli)``).
* Group 3 — optional breaking-change marker ``!``.

The description must start with a non-whitespace character (``\\S``)
to prevent subjects like ``feat: `` (trailing space only) from
matching.
"""

MAX_SUBJECT_LEN = 72
"""Maximum allowed length for the commit subject line, in characters.

This matches the 72-character convention used by Git itself and by the
`Conventional Commits specification
<https://www.conventionalcommits.org/>`_.  The length check is
performed **before** the regex check so that an overly long subject
receives a distinct, descriptive error message rather than a bare
``REJECTED.``.
"""

# ---------------------------------------------------------------------------
# Private constants (gamification layer)
# ---------------------------------------------------------------------------

_NICE_TYPES = frozenset({"docs", "chore"})
"""Commit types that trigger a francinette approval message."""

_ULTIMATE_TYPE = "test"
"""The commit type that reveals the easter-egg gamification message."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def check(file_path: str, pattern: str = DEFAULT_PATTERN) -> bool:
    """Validate the commit message stored at *file_path*.

    This is the main entry point for the ``commit-message`` pre-commit
    hook.  Git writes the commit message to ``.git/COMMIT_EDITMSG``
    before invoking the hook; *file_path* is that path.

    Processing steps
    ~~~~~~~~~~~~~~~~
    1. Read the file contents (UTF-8).
    2. Strip every line that begins with ``#`` (git comment lines).
    3. Trim surrounding whitespace from the remaining text.
    4. Reject if the cleaned message is empty.
    5. Extract the first non-empty line as the *subject*.
    6. Reject if the subject exceeds :const:`MAX_SUBJECT_LEN` chars.
    7. Compile *pattern* and match it against the subject.
    8. Reject if the subject does not match.
    9. If *pattern* is :const:`DEFAULT_PATTERN`, run the gamification
       layer (informational messages on *stderr*).
    10. Return ``True`` on success.

    Rejection output
    ~~~~~~~~~~~~~~~~
    All rejection messages are printed to *stderr*.  They are
    intentionally vague to encourage students to discover the correct
    format themselves:

    * Empty message       → ``REJECTED.``
    * Subject too long    → ``REJECTED.\\n  subject line: N chars (max 72).``
    * Pattern mismatch    → ``REJECTED.``

    Args:
        file_path: Path to the file containing the commit message.
            Git passes ``.git/COMMIT_EDITMSG`` here.  May be absolute
            or relative to the current working directory.
        pattern: Regular expression validated against the subject line.
            Defaults to :const:`DEFAULT_PATTERN`.  Must be a valid
            Python :mod:`re` pattern; an invalid pattern is caught,
            reported to *stderr*, and causes the function to return
            ``False``.

    Returns:
        ``True`` if the commit message passes all checks.
        ``False`` if any check fails (rejection message already printed
        to *stderr*).

    Examples:
        Basic usage from the CLI layer::

            from ganesha.checks.commit_msg import check, DEFAULT_PATTERN

            ok = check(".git/COMMIT_EDITMSG", DEFAULT_PATTERN)
            # ok is True on a valid commit, False otherwise

        Using a custom 42-school pattern::

            ok = check(path, pattern=r"^(ex|rush|exam)\\d+: .+")

        In tests, write a temporary file and call check directly::

            def test_feat_valid(tmp_path):
                p = tmp_path / "COMMIT_EDITMSG"
                p.write_text("feat: add norminette timeout option\\n")
                assert check(str(p)) is True
    """
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except OSError as e:
        print(f"cannot read '{file_path}': {e}", file=sys.stderr)
        return False

    stripped = [line for line in content.splitlines() if not line.startswith("#")]
    clean = "\n".join(stripped).strip()

    if not clean:
        print("REJECTED.", file=sys.stderr)
        return False

    all_lines = clean.splitlines()
    first_line = all_lines[0] if all_lines else ""

    if len(first_line) > MAX_SUBJECT_LEN:
        print(
            f"REJECTED.\n  subject line: {len(first_line)} chars"
            f" (max {MAX_SUBJECT_LEN}).",
            file=sys.stderr,
        )
        return False

    try:
        compiled = re.compile(pattern)
    except re.error as e:
        print(f"invalid commit pattern: '{pattern}': {e}", file=sys.stderr)
        return False

    match = compiled.match(first_line)
    if not match:
        print("REJECTED.", file=sys.stderr)
        return False

    # ------------------------------------------------------------------
    # Gamification layer — active only with the default CC 1.0.0 pattern
    # ------------------------------------------------------------------
    if pattern == DEFAULT_PATTERN:
        commit_type = match.group(1) or ""
        is_breaking = match.group(3) is not None

        if commit_type == _ULTIMATE_TYPE:
            print(
                "  you discovered the ultimate commit type.",
                file=sys.stderr,
            )
        elif commit_type in _NICE_TYPES:
            print(
                f"  francinette approves this {commit_type} commit.",
                file=sys.stderr,
            )

        if is_breaking:
            body_lines = all_lines[1:]
            has_body = any(line.strip() for line in body_lines)
            if has_body:
                print("  breaking change explained — +XP.", file=sys.stderr)
            else:
                print(
                    "  tip: explain why this breaks to earn +XP.",
                    file=sys.stderr,
                )

    return True
