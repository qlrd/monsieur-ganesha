"""Piscine C00 exercise integration tests — CI failure demo.

These tests run the ganesha hooks against sample C00 student
submissions. The fixture files under tests/fixtures/c00/ contain
intentional violations to demonstrate what CI output looks like
when student code fails the pre-commit checks.

Forbidden functions checked: printf, malloc, realloc, free,
calloc, exit — a typical C00 restriction list.
"""

from pathlib import Path

import pytest

from ganesha.checks.commit_msg import check as check_commit
from ganesha.checks.forbidden import check as check_forbidden

FIXTURES = Path(__file__).parent / "fixtures" / "c00"

C00_FORBIDDEN = ["printf", "malloc", "realloc", "free", "calloc", "exit"]


@pytest.mark.parametrize(
    "filename,exercise",
    [
        ("ft_putchar.c", "ex00"),
        ("ft_print_alphabet.c", "ex01"),
        ("ft_print_reverse_alphabet.c", "ex02"),
        ("ft_print_numbers.c", "ex03"),
        ("ft_is_negative.c", "ex04"),
    ],
)
def test_c00_no_forbidden_functions(filename, exercise):
    """C00 student files must not call forbidden functions."""
    path = FIXTURES / filename
    ok = check_forbidden([str(path)], C00_FORBIDDEN)
    assert ok, f"C00 {exercise} uses a forbidden function"


@pytest.mark.parametrize(
    "message,label",
    [
        ("ex00: ft_putchar done", "bare 42 format, no type prefix"),
        ("WIP", "no colon"),
        ("done", "no structure"),
        ("ft_print_alphabet: print a to z", "function name as type"),
        ("C00 ex01 done", "space-separated, no colon"),
    ],
)
def test_c00_commit_messages_follow_cc(tmp_path, message, label):
    """C00 commit messages must follow Conventional Commits 1.0.0."""
    msg_file = tmp_path / "COMMIT_EDITMSG"
    msg_file.write_text(message + "\n", encoding="utf-8")
    ok = check_commit(str(msg_file))
    assert ok, f"commit rejected ({label}): '{message}'"
