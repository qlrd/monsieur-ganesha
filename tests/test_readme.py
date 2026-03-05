"""Integration tests for the readme check."""

from ganesha.checks.readme import check

def test_binary_readme_does_not_block(tmp_path):
    p = tmp_path / "README.md"
    p.write_bytes(b"\xff\xfe invalid utf-8 \x00\x01")
    assert check([str(p)]) is True


def test_binary_readme_prints_error(tmp_path, capsys):
    p = tmp_path / "README.md"
    p.write_bytes(b"\xff\xfe invalid utf-8 \x00\x01")
    check([str(p)])
    assert "ERROR" in capsys.readouterr().err


# --- Filtering ---


def test_empty_file_list_passes():
    assert check([]) is True


def test_non_readme_files_ignored(tmp_path):
    p = tmp_path / "notes.md"
    p.write_text("")
    assert check([str(p)]) is True


def test_only_non_readme_files_ignored():
    assert check(["src/something.md", "CONTRIBUTING.md"]) is True


# --- Non-blocking: always returns True ---


def test_empty_readme_does_not_block(tmp_path):
    p = tmp_path / "README.md"
    p.write_text("")
    assert check([str(p)]) is True


def test_whitespace_only_readme_does_not_block(tmp_path):
    p = tmp_path / "README.md"
    p.write_text("   \n\n\t\n")
    assert check([str(p)]) is True


def test_readme_without_title_does_not_block(tmp_path):
    p = tmp_path / "README.md"
    p.write_text("Some content but no heading.\n")
    assert check([str(p)]) is True


def test_readme_with_hash_but_no_space_does_not_block(tmp_path):
    p = tmp_path / "README.md"
    p.write_text("#NoSpace\n\nContent here.\n")
    assert check([str(p)]) is True


def test_readme_without_fd_documentation_does_not_block(tmp_path):
    p = tmp_path / "README.md"
    p.write_text("# My Project\n\nA short description.\n")
    assert check([str(p)]) is True


def test_multiple_readmes_one_incomplete_does_not_block(tmp_path):
    good = tmp_path / "README.md"
    subdir = tmp_path / "sub"
    subdir.mkdir()
    bad = subdir / "README.md"
    good.write_text("# Good\n\nWrites to stdout.\n")
    bad.write_text("no heading here\n")
    assert check([str(good), str(bad)]) is True


# --- XP: passes all checks ---


def test_readme_with_stdin_passes(tmp_path):
    p = tmp_path / "README.md"
    p.write_text("# ft_read\n\nReads from stdin.\n")
    assert check([str(p)]) is True


def test_readme_with_stdout_passes(tmp_path):
    p = tmp_path / "README.md"
    p.write_text("# ft_putchar\n\nWrites a character to stdout.\n")
    assert check([str(p)]) is True


def test_readme_with_stderr_passes(tmp_path):
    p = tmp_path / "README.md"
    p.write_text("# ft_error\n\nPrints error messages to stderr.\n")
    assert check([str(p)]) is True


def test_readme_with_fd_number_passes(tmp_path):
    p = tmp_path / "README.md"
    p.write_text("# ft_putchar\n\nWrites to fd 1.\n")
    assert check([str(p)]) is True


def test_readme_with_fd_number_nospace_passes(tmp_path):
    p = tmp_path / "README.md"
    p.write_text("# ft_putchar\n\nWrites to fd1.\n")
    assert check([str(p)]) is True


def test_readme_with_file_descriptor_phrase_passes(tmp_path):
    p = tmp_path / "README.md"
    p.write_text("# ex01\n\nUses file descriptor 1 for output.\n")
    assert check([str(p)]) is True


def test_readme_with_stdin_fileno_passes(tmp_path):
    p = tmp_path / "README.md"
    p.write_text("# ex02\n\nReads using STDIN_FILENO.\n")
    assert check([str(p)]) is True


def test_readme_fd_case_insensitive_passes(tmp_path):
    p = tmp_path / "README.md"
    p.write_text("# ex00\n\nOutput goes to STDOUT.\n")
    assert check([str(p)]) is True


def test_valid_readme_passes(tmp_path):
    p = tmp_path / "README.md"
    p.write_text("# My Project\n\nWrites output to stdout.\n")
    assert check([str(p)]) is True


def test_readme_title_not_on_first_line_passes(tmp_path):
    p = tmp_path / "README.md"
    p.write_text("<!-- badge -->\n\n# My Project\n\nWrites to fd 1.\n")
    assert check([str(p)]) is True


def test_multiple_readmes_all_valid(tmp_path):
    a = tmp_path / "README.md"
    subdir = tmp_path / "sub"
    subdir.mkdir()
    b = subdir / "README.md"
    a.write_text("# Project A\n\nReads from stdin.\n")
    b.write_text("# Project B\n\nWrites to stdout.\n")
    assert check([str(a), str(b)]) is True


# --- Advisory messages ---


def test_empty_readme_prints_advisory(tmp_path, capsys):
    p = tmp_path / "README.md"
    p.write_text("")
    check([str(p)])
    captured = capsys.readouterr()
    assert "empty file" in captured.err
    assert "add at least a title" in captured.err
    assert "+XP available" in captured.err


def test_missing_title_prints_advisory(tmp_path, capsys):
    p = tmp_path / "README.md"
    p.write_text("Content without heading.\n")
    check([str(p)])
    captured = capsys.readouterr()
    assert "no title found" in captured.err
    assert "# <Project Name>" in captured.err
    assert "+XP available" in captured.err


def test_missing_fd_prints_advisory(tmp_path, capsys):
    p = tmp_path / "README.md"
    p.write_text("# My Project\n\nNo fd info here.\n")
    check([str(p)])
    captured = capsys.readouterr()
    assert "no file descriptor usage documented" in captured.err
    assert "0=stdin" in captured.err
    assert "+XP available" in captured.err


def test_valid_readme_earns_xp(tmp_path, capsys):
    p = tmp_path / "README.md"
    p.write_text("# My Project\n\nWrites output to stdout.\n")
    check([str(p)])
    captured = capsys.readouterr()
    assert "well documented" in captured.err
    assert "+XP" in captured.err
