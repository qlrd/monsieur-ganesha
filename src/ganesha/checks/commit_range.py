"""Validate commit subjects and DCO trailers for a git revision range."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile

from ganesha.checks import commit_msg

_SIGNED_OFF_BY_RE = re.compile(r"^Signed-off-by:\s+.+", re.MULTILINE)


def _git_log_lines(format_spec: str, rev_range: str) -> list[str]:
    """Return non-empty output lines from ``git log --format=<spec>``."""
    result = subprocess.run(
        ["git", "log", f"--format={format_spec}", rev_range],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        print(
            f"failed to list commits in '{rev_range}': {stderr}",
            file=sys.stderr,
        )
        return []

    return [line for line in result.stdout.splitlines() if line]


def check_range(base_ref: str | None = None, head_ref: str | None = None) -> bool:
    """Validate commit subjects and Signed-off-by trailers in a ref range."""
    base = base_ref or os.environ.get("BASE_SHA", "origin/main")
    head = head_ref or os.environ.get("HEAD_SHA", "HEAD")
    rev_range = f"{base}..{head}"
    commit_hashes = _git_log_lines("%H", rev_range)
    if not commit_hashes:
        print(f"no commits to validate in {rev_range}.", file=sys.stderr)
        return True

    subjects = _git_log_lines("%s", rev_range)
    if len(subjects) != len(commit_hashes):
        print("failed to read commit subjects for full range.", file=sys.stderr)
        return False

    with tempfile.NamedTemporaryFile(
        mode="w+",
        encoding="utf-8",
        suffix=".commitmsg",
    ) as temp:
        for index, subject in enumerate(subjects):
            temp.seek(0)
            temp.truncate(0)
            temp.write(f"{subject}\n")
            temp.flush()
            if not commit_msg.check(temp.name, commit_msg.DEFAULT_PATTERN):
                print(
                    f"invalid commit subject in {commit_hashes[index]}: {subject}",
                    file=sys.stderr,
                )
                return False

    for commit_hash in commit_hashes:
        result = subprocess.run(
            ["git", "log", "--format=%B", "-n", "1", commit_hash],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            print(
                f"failed to read commit body for {commit_hash}: {stderr}",
                file=sys.stderr,
            )
            return False
        if not _SIGNED_OFF_BY_RE.search(result.stdout):
            print(
                f"missing Signed-off-by trailer in commit {commit_hash}.",
                file=sys.stderr,
            )
            return False

    return True


def main() -> int:
    """CLI entry point for CI usage."""
    return 0 if check_range() else 1


if __name__ == "__main__":
    raise SystemExit(main())
