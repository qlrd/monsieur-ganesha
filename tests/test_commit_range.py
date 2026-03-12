"""Tests for ganesha.checks.commit_range."""

from __future__ import annotations

import subprocess

from ganesha.checks import commit_range


def _mock_subprocess_result(stdout: str = "", stderr: str = "", returncode: int = 0):
    return subprocess.CompletedProcess(
        args=[],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def test_check_range_accepts_valid_subjects_and_dco(monkeypatch):
    outputs = iter(
        [
            _mock_subprocess_result(stdout="abc123\n"),
            _mock_subprocess_result(stdout="feat: add CI validation\n"),
            _mock_subprocess_result(
                stdout=(
                    "feat: add CI validation\n\n"
                    "Signed-off-by: Jane Doe <jane@example.com>\n"
                )
            ),
        ]
    )

    monkeypatch.setattr(
        commit_range.subprocess,
        "run",
        lambda *args, **kwargs: next(outputs),
    )
    monkeypatch.setattr(
        commit_range.commit_msg, "check", lambda *_args, **_kwargs: True
    )

    assert commit_range.check_range() is True


def test_check_range_fails_when_subject_is_invalid(monkeypatch):
    outputs = iter(
        [
            _mock_subprocess_result(stdout="abc123\n"),
            _mock_subprocess_result(stdout="WIP: do stuff\n"),
        ]
    )

    monkeypatch.setattr(
        commit_range.subprocess,
        "run",
        lambda *args, **kwargs: next(outputs),
    )
    monkeypatch.setattr(
        commit_range.commit_msg, "check", lambda *_args, **_kwargs: False
    )

    assert commit_range.check_range() is False


def test_check_range_fails_when_dco_is_missing(monkeypatch):
    outputs = iter(
        [
            _mock_subprocess_result(stdout="abc123\n"),
            _mock_subprocess_result(stdout="fix: align ci step\n"),
            _mock_subprocess_result(stdout="fix: align ci step\n\nNo trailer\n"),
        ]
    )

    monkeypatch.setattr(
        commit_range.subprocess,
        "run",
        lambda *args, **kwargs: next(outputs),
    )
    monkeypatch.setattr(
        commit_range.commit_msg, "check", lambda *_args, **_kwargs: True
    )

    assert commit_range.check_range() is False


def test_check_range_uses_base_and_head_from_environment(monkeypatch):
    seen_ranges = []

    def mock_git_log_lines(format_spec: str, rev_range: str) -> list[str]:
        seen_ranges.append(rev_range)
        if format_spec == "%H":
            return ["abc123"]
        if format_spec == "%s":
            return ["fix: align ci step"]
        return []

    monkeypatch.setenv("BASE_SHA", "111aaa")
    monkeypatch.setenv("HEAD_SHA", "222bbb")
    monkeypatch.setattr(commit_range, "_git_log_lines", mock_git_log_lines)
    monkeypatch.setattr(
        commit_range.subprocess,
        "run",
        lambda *args, **kwargs: _mock_subprocess_result(
            stdout="fix: align ci step\n\nSigned-off-by: Jane Doe <jane@example.com>\n"
        ),
    )
    monkeypatch.setattr(
        commit_range.commit_msg, "check", lambda *_args, **_kwargs: True
    )

    assert commit_range.check_range() is True
    assert seen_ranges == ["111aaa..222bbb", "111aaa..222bbb"]
