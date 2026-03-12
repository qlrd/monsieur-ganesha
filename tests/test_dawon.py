"""Tests for the optional dawon pre-push check."""

from ganesha.checks import dawon


def test_dawon_check_skips_when_binary_is_missing(monkeypatch):
    monkeypatch.setattr(dawon.shutil, "which", lambda _name: None)

    assert dawon.check("C00") is True


def test_dawon_check_uses_configured_module_path(monkeypatch):
    monkeypatch.setattr(dawon.shutil, "which", lambda _name: "/usr/bin/dawon")
    called = {}

    class Result:
        returncode = 0

    def fake_run(args, check):
        called["args"] = args
        called["check"] = check
        return Result()

    monkeypatch.setattr(dawon.subprocess, "run", fake_run)

    assert dawon.check("C04") is True
    assert called["args"] == ["dawon", "check", "--path", "C04"]
    assert called["check"] is False


def test_dawon_check_fails_when_command_fails(monkeypatch):
    monkeypatch.setattr(dawon.shutil, "which", lambda _name: "/usr/bin/dawon")

    class Result:
        returncode = 1

    monkeypatch.setattr(
        dawon.subprocess,
        "run",
        lambda args, check: Result(),
    )

    assert dawon.check("C04") is False


def test_dawon_check_defaults_to_dot_when_module_is_missing(monkeypatch):
    monkeypatch.setattr(dawon.shutil, "which", lambda _name: "/usr/bin/dawon")
    called = {}

    class Result:
        returncode = 0

    def fake_run(args, check):
        called["args"] = args
        return Result()

    monkeypatch.setattr(dawon.subprocess, "run", fake_run)

    assert dawon.check(None) is True
    assert called["args"] == ["dawon", "check", "--path", "."]
