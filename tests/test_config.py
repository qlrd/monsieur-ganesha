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
                'mode = "general"',
                "",
                "[forbidden]",
                'functions = ["printf", "malloc"]',
                "",
                "[commit]",
                'pattern = "^(ex|rush|exam)\\\\d+: .+"',
                "",
                "[norminette]",
                "strict = true",
                "",
            ]
        ),
        encoding="utf-8",
    )
    cfg = load_config(tmp_path)
    assert cfg.project.name == "C04"
    assert cfg.project.mode == "general"
    assert cfg.forbidden.functions == ["printf", "malloc"]
    assert cfg.commit.pattern == "^(ex|rush|exam)\\d+: .+"
    assert cfg.norminette.strict is True


def test_load_config_invalid_toml_raises_value_error(tmp_path):
    (tmp_path / ".ganesha.toml").write_text("[project]\nname = \n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"TOML.*\.ganesha\.toml"):
        load_config(tmp_path)


def test_load_config_general_mode_defaults_norminette_to_advisory(tmp_path):
    (tmp_path / ".ganesha.toml").write_text(
        '[project]\nmode = "general"\n',
        encoding="utf-8",
    )
    cfg = load_config(tmp_path)
    assert cfg.project.mode == "general"
    assert cfg.norminette.strict is False


def test_load_config_invalid_project_mode_raises_value_error(tmp_path):
    (tmp_path / ".ganesha.toml").write_text(
        '[project]\nmode = "other"\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match=r"\[project\]\.mode"):
        load_config(tmp_path)
