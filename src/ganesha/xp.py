"""XP system — simulates 42 exam-mode scoring.

Persists session state in ``.ganesha_xp.json`` at the repository root.
Each failed blocking-hook run deducts XP and increments the trial
counter.  When a commit-message check passes (meaning the commit goes
through), XP is awarded based on the number of failed attempts
accumulated since the previous successful commit, then the trial
counter resets.

The ``readme`` hook is non-blocking and does not affect the XP score.

XP schedule
-----------
Failed blocking hook:  ``-10 XP``

Successful commit by trial count:

=====  =========  ===========================
Trial  XP earned  Note
=====  =========  ===========================
1         +100    Flawless execution.
2          +75    Second trial.
3          +50    Third trial.
4+         +25    Persistence rewarded.
=====  =========  ===========================

State file
----------
``.ganesha_xp.json`` is written to the current working directory
(the repository root when invoked by pre-commit).  Add it to
``.gitignore`` so session state is not shared across machines.

Example::

    {"total": 75, "trial": 1, "commits": 2}

Fields
------
``total``
    Running total XP (can be negative).
``trial``
    Number of failed hook runs since the last successful commit.
``commits``
    Total successful commits in this session.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_XP_FILE = ".ganesha_xp.json"

_XP_TABLE = [100, 75, 50]
_XP_MIN = 25
_XP_FAILURE = -10

_SUCCESS_NOTES = {
    1: "Flawless execution.",
    2: "Second trial.",
    3: "Third trial.",
}


def _path(root: Path | None) -> Path:
    return (root or Path()) / _XP_FILE


def load(root: Path | None = None) -> dict[str, int]:
    """Load XP state from disk.

    Returns the default state ``{"total": 0, "trial": 0, "commits": 0}``
    when the state file does not exist or cannot be parsed.

    Args:
        root: Directory containing ``.ganesha_xp.json``.  Defaults to
            the current working directory.

    Returns:
        Dictionary with keys ``total``, ``trial``, and ``commits``.
    """
    p = _path(root)
    if not p.is_file():
        return {"total": 0, "trial": 0, "commits": 0}
    try:
        data = json.loads(p.read_text())
        return {
            "total": int(data["total"]),
            "trial": int(data["trial"]),
            "commits": int(data["commits"]),
        }
    except (ValueError, KeyError, TypeError):
        return {"total": 0, "trial": 0, "commits": 0}


def _save(state: dict[str, int], root: Path | None = None) -> None:
    _path(root).write_text(json.dumps(state))


def record_failure(root: Path | None = None) -> None:
    """Record a failed blocking-hook run.

    Deducts :data:`_XP_FAILURE` XP, increments the trial counter, and
    prints a one-line summary to *stderr*.

    Args:
        root: Directory containing ``.ganesha_xp.json``.  Defaults to
            the current working directory.
    """
    state = load(root)
    state["trial"] += 1
    state["total"] += _XP_FAILURE
    _save(state, root)
    trial = state["trial"]
    total = state["total"]
    print(
        f"DEDUCTED.  {_XP_FAILURE} XP." f"  [Total: {total:+d} XP | trials: {trial}]",
        file=sys.stderr,
    )


def record_success(root: Path | None = None) -> None:
    """Record a successful commit (commit-message hook accepted).

    Awards XP based on the number of failed attempts since the last
    successful commit, resets the trial counter, and prints a one-line
    summary to *stderr*.

    Args:
        root: Directory containing ``.ganesha_xp.json``.  Defaults to
            the current working directory.
    """
    state = load(root)
    trial = state["trial"] + 1  # the attempt that succeeded
    if trial <= len(_XP_TABLE):
        delta = _XP_TABLE[trial - 1]
    else:
        delta = _XP_MIN
    state["total"] += delta
    state["commits"] += 1
    state["trial"] = 0
    _save(state, root)
    total = state["total"]
    commits = state["commits"]
    note = _SUCCESS_NOTES.get(trial, "Persistence rewarded.")
    print(
        f"ACCEPTED.  +{delta} XP.  {note}"
        f"  [Total: {total:+d} XP | commits: {commits}]",
        file=sys.stderr,
    )
