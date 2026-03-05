"""Integration tests for the commit-message check."""

from ganesha.checks.commit_msg import DEFAULT_PATTERN, MAX_SUBJECT_LEN, check


def msg_file(tmp_path, content: str) -> str:
    p = tmp_path / "COMMIT_EDITMSG"
    p.write_text(content)
    return str(p)


# --- Valid: Conventional Commits 1.0.0 ---


def test_feat_valid(tmp_path):
    assert check(msg_file(tmp_path, "feat: add norminette timeout option\n")) is True


def test_fix_with_scope_valid(tmp_path):
    assert check(msg_file(tmp_path, "fix(forbidden): handle empty file list\n")) is True


def test_docs_valid(tmp_path):
    assert (
        check(msg_file(tmp_path, "docs: update readme configuration section\n")) is True
    )


def test_chore_valid(tmp_path):
    assert check(msg_file(tmp_path, "chore: bump regex to 1.11\n")) is True


def test_refactor_valid(tmp_path):
    assert (
        check(
            msg_file(
                tmp_path,
                "refactor: extract subprocess helper into shared module\n",
            )
        )
        is True
    )


def test_test_type_valid(tmp_path):
    assert (
        check(msg_file(tmp_path, "test: add integration test for commit-msg\n")) is True
    )


def test_init_type_valid(tmp_path):
    assert check(msg_file(tmp_path, "init: project setup\n")) is True


def test_breaking_change_exclamation_valid(tmp_path):
    assert (
        check(msg_file(tmp_path, "feat!: drop support for gcc older than 12\n")) is True
    )


def test_breaking_change_with_scope_valid(tmp_path):
    assert (
        check(msg_file(tmp_path, "fix(compiler)!: change exit code on parse error\n"))
        is True
    )


def test_strips_git_comment_lines(tmp_path):
    content = (
        "feat: implement ft_putchar check\n"
        "# Please do not edit below\n"
        "# Changes: modified src/checks/norminette.py\n"
    )
    assert check(msg_file(tmp_path, content)) is True


def test_multiline_uses_first_line(tmp_path):
    assert check(msg_file(tmp_path, "feat: add timeout\n\nLonger body here.\n")) is True


def test_trailing_newline_accepted(tmp_path):
    assert check(msg_file(tmp_path, "fix: correct regex boundary\n")) is True


# --- Invalid ---


def test_bare_text_fails(tmp_path):
    assert check(msg_file(tmp_path, "my implementation\n")) is False


def test_wip_fails(tmp_path):
    assert check(msg_file(tmp_path, "WIP\n")) is False


def test_piscine_style_prefix_fails(tmp_path):
    assert check(msg_file(tmp_path, "ex00: implement ft_putchar\n")) is False


def test_uppercase_type_fails(tmp_path):
    assert check(msg_file(tmp_path, "FEAT: uppercase type\n")) is False


def test_missing_description_fails(tmp_path):
    assert check(msg_file(tmp_path, "feat: \n")) is False


def test_colon_only_fails(tmp_path):
    assert check(msg_file(tmp_path, "feat:\n")) is False


def test_empty_string_fails(tmp_path):
    assert check(msg_file(tmp_path, "")) is False


def test_only_whitespace_fails(tmp_path):
    assert check(msg_file(tmp_path, "   \n  \n")) is False


def test_only_git_comments_fails(tmp_path):
    assert check(msg_file(tmp_path, "# comment\n# another\n")) is False


def test_subject_too_long_fails(tmp_path):
    long_msg = f"feat: {'a' * MAX_SUBJECT_LEN}\n"
    assert check(msg_file(tmp_path, long_msg)) is False


def test_subject_at_max_length_passes(tmp_path):
    # "feat: " is 6 chars; description fills up to 72 total
    desc = "a" * (MAX_SUBJECT_LEN - 6)
    assert check(msg_file(tmp_path, f"feat: {desc}\n")) is True


# --- Custom pattern: 42-school format via config ---


def test_custom_pattern_matches_piscine_format(tmp_path):
    assert (
        check(
            msg_file(tmp_path, "ex00: implementa ft_putchar\n"),
            pattern=r"^(ex|rush|exam)\d+: .+",
        )
        is True
    )


def test_custom_pattern_rejects_cc_format(tmp_path):
    assert (
        check(
            msg_file(tmp_path, "feat: something\n"),
            pattern=r"^(ex|rush|exam)\d+: .+",
        )
        is False
    )


# --- 42-school scopes as sub-scopes in CC 1.0.0 ---


def test_feat_with_ex00_scope_valid(tmp_path):
    assert check(msg_file(tmp_path, "feat(ex00): implement ft_putchar\n")) is True


def test_fix_with_rush00_scope_valid(tmp_path):
    assert check(msg_file(tmp_path, "fix(rush00): handle edge case\n")) is True


def test_docs_with_exam01_scope_valid(tmp_path):
    assert check(msg_file(tmp_path, "docs(exam01): add subject description\n")) is True


def test_feat_breaking_with_ex00_scope_valid(tmp_path):
    assert check(msg_file(tmp_path, "feat(ex00)!: rewrite with different algorithm\n")) is True


def test_bare_ex00_prefix_fails_without_custom_pattern(tmp_path):
    assert check(msg_file(tmp_path, "ex00: implement ft_putchar\n")) is False
