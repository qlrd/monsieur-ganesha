"""Tests for ganesha.xp — XP state management."""

import json

import pytest

from ganesha import xp

# ── load ────────────────────────────────────────────────────────────


def test_load_returns_defaults_when_no_file(tmp_path):
    state = xp.load(tmp_path)
    assert state == {"total": 0, "trial": 0, "commits": 0}


def test_load_reads_existing_file(tmp_path):
    (tmp_path / ".ganesha_xp.json").write_text(
        json.dumps({"total": 50, "trial": 2, "commits": 1})
    )
    state = xp.load(tmp_path)
    assert state == {"total": 50, "trial": 2, "commits": 1}


def test_load_returns_defaults_on_corrupt_file(tmp_path):
    (tmp_path / ".ganesha_xp.json").write_text("not json {{")
    state = xp.load(tmp_path)
    assert state == {"total": 0, "trial": 0, "commits": 0}


def test_load_returns_defaults_on_missing_keys(tmp_path):
    (tmp_path / ".ganesha_xp.json").write_text(json.dumps({"total": 10}))
    state = xp.load(tmp_path)
    assert state == {"total": 0, "trial": 0, "commits": 0}


# ── record_failure ──────────────────────────────────────────────────


def test_record_failure_deducts_xp(tmp_path, capsys):
    xp.record_failure(tmp_path)
    state = xp.load(tmp_path)
    assert state["total"] == -10


def test_record_failure_increments_trial(tmp_path, capsys):
    xp.record_failure(tmp_path)
    xp.record_failure(tmp_path)
    state = xp.load(tmp_path)
    assert state["trial"] == 2


def test_record_failure_does_not_touch_commits(tmp_path, capsys):
    xp.record_failure(tmp_path)
    assert xp.load(tmp_path)["commits"] == 0


def test_record_failure_prints_deducted(tmp_path, capsys):
    xp.record_failure(tmp_path)
    err = capsys.readouterr().err
    assert "DEDUCTED" in err
    assert "-10 XP" in err
    assert "trials: 1" in err


def test_record_failure_accumulates_total(tmp_path, capsys):
    xp.record_failure(tmp_path)
    xp.record_failure(tmp_path)
    xp.record_failure(tmp_path)
    state = xp.load(tmp_path)
    assert state["total"] == -30
    assert state["trial"] == 3


# ── record_success ──────────────────────────────────────────────────


def test_record_success_first_trial_earns_100(tmp_path, capsys):
    xp.record_success(tmp_path)
    assert xp.load(tmp_path)["total"] == 100


def test_record_success_second_trial_earns_75(tmp_path, capsys):
    xp.record_failure(tmp_path)
    xp.record_success(tmp_path)
    assert xp.load(tmp_path)["total"] == -10 + 75


def test_record_success_third_trial_earns_50(tmp_path, capsys):
    xp.record_failure(tmp_path)
    xp.record_failure(tmp_path)
    xp.record_success(tmp_path)
    assert xp.load(tmp_path)["total"] == -20 + 50


def test_record_success_fourth_plus_trial_earns_25(tmp_path, capsys):
    for _ in range(3):
        xp.record_failure(tmp_path)
    xp.record_success(tmp_path)
    assert xp.load(tmp_path)["total"] == -30 + 25


def test_record_success_resets_trial(tmp_path, capsys):
    xp.record_failure(tmp_path)
    xp.record_success(tmp_path)
    assert xp.load(tmp_path)["trial"] == 0


def test_record_success_increments_commits(tmp_path, capsys):
    xp.record_success(tmp_path)
    xp.record_success(tmp_path)
    assert xp.load(tmp_path)["commits"] == 2


def test_record_success_prints_accepted(tmp_path, capsys):
    xp.record_success(tmp_path)
    err = capsys.readouterr().err
    assert "ACCEPTED" in err
    assert "+100 XP" in err
    assert "commits: 1" in err


def test_record_success_flawless_note(tmp_path, capsys):
    xp.record_success(tmp_path)
    err = capsys.readouterr().err
    assert "Flawless execution" in err


def test_record_success_second_trial_note(tmp_path, capsys):
    xp.record_failure(tmp_path)
    capsys.readouterr()
    xp.record_success(tmp_path)
    err = capsys.readouterr().err
    assert "Second trial" in err


def test_record_success_persistence_note_on_high_trial(tmp_path, capsys):
    for _ in range(5):
        xp.record_failure(tmp_path)
    capsys.readouterr()
    xp.record_success(tmp_path)
    err = capsys.readouterr().err
    assert "Persistence rewarded" in err


# ── cross-session accumulation ──────────────────────────────────────


def test_total_xp_accumulates_across_commits(tmp_path, capsys):
    xp.record_success(tmp_path)  # +100
    xp.record_success(tmp_path)  # +100 (trial resets)
    assert xp.load(tmp_path)["total"] == 200


def test_xp_file_written_as_valid_json(tmp_path, capsys):
    xp.record_failure(tmp_path)
    raw = (tmp_path / ".ganesha_xp.json").read_text()
    data = json.loads(raw)
    assert set(data.keys()) == {"total", "trial", "commits"}
