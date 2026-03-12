"""Integration tests for the docstring check."""

from pathlib import Path

from ganesha.checks.docstring import check

FIXTURES = Path(__file__).parent / "fixtures"


def test_docstring_valid_passes_strict():
    assert check([str(FIXTURES / "docstring_valid.c")], strict=True) is True


def test_docstring_missing_about_fails_strict(capsys):
    assert check([str(FIXTURES / "docstring_no_about.c")], strict=True) is False
    assert "# About" in capsys.readouterr().err


def test_docstring_missing_example_fails_strict(capsys):
    assert check([str(FIXTURES / "docstring_no_example.c")], strict=True) is False
    assert "missing # Example" in capsys.readouterr().err


def test_docstring_missing_code_block_fails_strict(capsys):
    assert check([str(FIXTURES / "docstring_no_code_block.c")], strict=True) is False
    assert "fenced ```c block" in capsys.readouterr().err


def test_docstring_missing_param_warns_but_passes(capsys):
    assert check([str(FIXTURES / "docstring_missing_param.c")], strict=False) is True
    assert "WARNING: missing @param[base]" in capsys.readouterr().err


def test_docstring_mismatched_param_warns(tmp_path, capsys):
    c_file = tmp_path / "mismatch.c"
    c_file.write_text(
        "\n".join(
            [
                "/*",
                " * ft_sum",
                " *",
                " * # About",
                " *",
                " * Sums two integers.",
                " *",
                " * # Example",
                " *",
                " * ```c",
                " * int\tmain(void)",
                " * {",
                " * \treturn (ft_sum(1, 2));",
                " * }",
                " * ```",
                " *",
                " * @param[a]: first value.",
                " * @param[c]: typo should warn.",
                " */",
                "int\tft_sum(int a, int b)",
                "{",
                "\treturn (a + b);",
                "}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    assert check([str(c_file)], strict=False) is True
    output = capsys.readouterr().err
    assert "missing @param[b]" in output
    assert "@param[c] does not match" in output
