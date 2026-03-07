"""Tests for ganesha.config — load_config."""

import pytest

from ganesha.config import Config, load_config


def test_load_config_returns_defaults_when_missing(tmp_path):
    cfg = load_config(tmp_path)
    assert cfg == Config()


def test_load_config_parses_toml_file(tmp_path):
    (tmp_path / ".ganesha.toml").write_text(
        "\n".join(
            [
                "[project]",
                'name = "C04"',
                "",
                "[forbidden]",
                'functions = ["printf", "malloc"]',
                "",
                "[commit]",
                'pattern = "^(ex|rush|exam)\\\\d+: .+"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    cfg = load_config(tmp_path)
    assert cfg.project.name == "C04"
    assert cfg.forbidden.functions == ["printf", "malloc"]
    assert cfg.commit.pattern == "^(ex|rush|exam)\\d+: .+"


def test_load_config_invalid_toml_raises_value_error(tmp_path):
    (tmp_path / ".ganesha.toml").write_text("[project]\nname = \n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"TOML.*\.ganesha\.toml"):
        load_config(tmp_path)
