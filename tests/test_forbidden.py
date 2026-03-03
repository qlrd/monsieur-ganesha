"""Integration tests for the forbidden-functions check."""

from ganesha.checks.forbidden import check


def test_empty_forbidden_always_passes(tmp_path):
    p = tmp_path / "main.c"
    p.write_text('int main(void) { printf("hi"); }\n')
    assert check([str(p)], []) is True


def test_empty_file_list_passes():
    assert check([], ["printf"]) is True


def test_non_c_files_ignored():
    assert check(["header.h"], ["printf"]) is True


def test_detects_forbidden_call(tmp_path):
    p = tmp_path / "main.c"
    p.write_text('int main(void) { printf("hi"); }\n')
    assert check([str(p)], ["printf"]) is False


def test_detects_call_with_space_before_paren(tmp_path):
    p = tmp_path / "main.c"
    p.write_text('int main(void) { printf ("hi"); }\n')
    assert check([str(p)], ["printf"]) is False


def test_detects_multiple_forbidden_on_same_line(tmp_path):
    p = tmp_path / "main.c"
    p.write_text("int main(void) { char *p = malloc(10); free(p); }\n")
    assert check([str(p)], ["malloc", "free"]) is False


def test_ft_prefix_not_flagged(tmp_path):
    p = tmp_path / "ft_printf.c"
    p.write_text("int ft_printf(char *s) { return 0; }\n")
    assert check([str(p)], ["printf"]) is True


def test_suffix_not_flagged(tmp_path):
    p = tmp_path / "wrap.c"
    p.write_text("int my_printf_wrap(void) { return 0; }\n")
    assert check([str(p)], ["printf"]) is True


def test_single_line_comment_ignored(tmp_path):
    p = tmp_path / "main.c"
    p.write_text('// printf("commented");\nint main(void) { return 0; }\n')
    assert check([str(p)], ["printf"]) is True


def test_clean_file_passes(tmp_path):
    p = tmp_path / "ft_putchar.c"
    p.write_text("int\tft_putchar(char c)\n{\n\treturn ((int)c);\n}\n")
    assert check([str(p)], ["printf", "malloc"]) is True


def test_multiple_files_one_dirty(tmp_path):
    good = tmp_path / "good.c"
    bad = tmp_path / "bad.c"
    good.write_text("int ft_strlen(char *s) { return 0; }\n")
    bad.write_text('int main(void) { printf("oops"); }\n')
    assert check([str(good), str(bad)], ["printf"]) is False


def test_multiple_files_all_clean(tmp_path):
    a = tmp_path / "a.c"
    b = tmp_path / "b.c"
    a.write_text("int ft_strlen(char *s) { return 0; }\n")
    b.write_text("int ft_putchar(char c) { return 0; }\n")
    assert check([str(a), str(b)], ["printf"]) is True
