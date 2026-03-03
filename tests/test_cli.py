"""CLI integration tests for piscinette."""

import subprocess
import sys


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "ganesha", *args],
        capture_output=True,
        text=True,
    )


def msg_file(tmp_path, content: str) -> str:
    p = tmp_path / "COMMIT_EDITMSG"
    p.write_text(content)
    return str(p)


# --- forbidden: no config -> no blocked functions -> always passes ---


def test_forbidden_no_config_passes(tmp_path):
    p = tmp_path / "main.c"
    p.write_text('int main(void) { printf("hi"); }\n')
    result = run("forbidden", str(p))
    assert result.returncode == 0


def test_forbidden_empty_files_passes():
    result = run("forbidden")
    assert result.returncode == 0


# --- commit-msg ---


def test_commit_msg_valid_format(tmp_path):
    f = msg_file(tmp_path, "feat: add norminette timeout option\n")
    result = run("commit-msg", f)
    assert result.returncode == 0


def test_commit_msg_invalid_format_exits_1(tmp_path):
    f = msg_file(tmp_path, "WIP: broken\n")
    result = run("commit-msg", f)
    assert result.returncode == 1
    assert "REJECTED" in result.stderr


def test_commit_msg_empty_exits_1(tmp_path):
    f = msg_file(tmp_path, "")
    result = run("commit-msg", f)
    assert result.returncode == 1


# --- compiler: empty list ---


def test_compiler_no_files_passes():
    result = run("compiler")
    assert result.returncode == 0


# --- norminette: empty list ---


def test_norminette_no_files_passes():
    result = run("norminette")
    assert result.returncode == 0


# --- help ---


def test_help_flag_works():
    result = run("--help")
    assert result.returncode == 0
    assert "ganesha" in result.stdout
