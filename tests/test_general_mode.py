"""General-mode integration tests."""

import subprocess
import sys
from unittest.mock import Mock

from ganesha.checks import compiler, norminette


def run(*args: str, cwd=None) -> subprocess.CompletedProcess:
    """Run ganesha CLI in a subprocess."""
    return subprocess.run(
        [sys.executable, "-m", "ganesha", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def test_general_mode_skips_forbidden_functions(tmp_path):
    (tmp_path / ".ganesha.toml").write_text(
        '[project]\nmode = "general"\n\n[forbidden]\nfunctions = ["printf"]\n',
        encoding="utf-8",
    )
    p = tmp_path / "main.c"
    p.write_text('int main(void) { printf("hi"); }\n', encoding="utf-8")

    result = run("forbidden", str(p), cwd=tmp_path)

    assert result.returncode == 0
    assert "mode='general'" in result.stderr


def test_general_mode_norminette_is_advisory(monkeypatch, tmp_path):
    c_file = tmp_path / "main.c"
    c_file.write_text("int main(void){return(0);}\n", encoding="utf-8")
    mocked = Mock(return_value=subprocess.CompletedProcess([], 1, "Error\n", ""))
    monkeypatch.setattr("ganesha.checks.norminette.subprocess.run", mocked)

    ok = norminette.check([str(c_file)], general_mode=True, strict=False)

    assert ok is True
    mocked.assert_called_once()
    assert "--use-tabsize=4" in mocked.call_args.args[0]


def test_general_mode_compiler_accepts_cpp_extension(monkeypatch, tmp_path):
    cpp_file = tmp_path / "main.cpp"
    cpp_file.write_text("int main(){return 0;}\n", encoding="utf-8")
    mocked = Mock(return_value=subprocess.CompletedProcess([], 0, "", ""))
    monkeypatch.setattr("ganesha.checks.compiler.subprocess.run", mocked)

    ok = compiler.check([str(cpp_file)], mode="general")

    assert ok is True
    mocked.assert_called_once()
    assert mocked.call_args.args[0][-1].endswith("main.cpp")
