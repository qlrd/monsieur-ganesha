"""Tests for config loading."""

from ganesha.config import Config, load_config


def test_load_config_returns_defaults_when_missing(tmp_path):
    cfg = load_config(tmp_path)
    assert cfg == Config()


def test_load_config_parses_toml_file(tmp_path):
    path = tmp_path / ".ganesha.toml"
    path.write_text(
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
    path = tmp_path / ".ganesha.toml"
    path.write_text("[project]\nname = \n", encoding="utf-8")

    try:
        load_config(tmp_path)
    except ValueError as exc:
        assert "TOML inválido em" in str(exc)
    else:
        raise AssertionError("Expected ValueError for malformed TOML")
