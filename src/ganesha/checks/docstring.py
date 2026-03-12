"""Docstring validator for C function definitions.

This module implements the ``docstring-check`` hook.  It validates
non-static C function definitions against the piscine docstring format:

* A preceding ``/* ... */`` block comment is required.
* The comment must include ``# About`` with non-empty content.
* The comment must include ``# Example`` with a fenced `````c`` block.
* The example code block must contain a ``main``-style snippet.
* ``@param[name]: ...`` entries are compared to function parameters.

By default this check is advisory (non-blocking).  When ``strict=True``
the check fails on errors (not warnings).
"""

import re
import sys
from collections.abc import Sequence
from pathlib import Path

_COMMENT_PATTERN = re.compile(r"/\*.*?\*/", re.DOTALL)
_FUNCTION_PATTERN = re.compile(
    r"(?ms)^[ \t]*(?!static\b)"
    r"(?:[A-Za-z_][\w\s\*]*?\s+)?"
    r"(?P<name>[A-Za-z_]\w*)\s*"
    r"\((?P<params>[^;{}]*)\)\s*\{"
)
_SKIP_NAMES = {"if", "for", "while", "switch"}


def _normalize_comment(comment: str) -> str:
    body = comment.strip()
    if body.startswith("/*"):
        body = body[2:]
    if body.endswith("*/"):
        body = body[:-2]
    lines = [re.sub(r"^\s*\*\s?", "", line) for line in body.splitlines()]
    return "\n".join(lines).strip()


def _extract_section(comment: str, section: str) -> str | None:
    pattern = re.compile(
        rf"(?ms)^#\s*{re.escape(section)}\s*$\n(?P<body>.*?)(?=^#\s+\w+|^@param\[|\Z)"
    )
    match = pattern.search(comment)
    if not match:
        return None
    return match.group("body").strip()


def _param_names(param_text: str) -> list[str]:
    params = param_text.strip()
    if not params or params == "void":
        return []

    names: list[str] = []
    for raw_param in params.split(","):
        chunk = raw_param.strip()
        if not chunk or chunk == "...":
            continue
        match = re.search(r"([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?\s*$", chunk)
        if match:
            names.append(match.group(1))
    return names


def _param_doc_names(comment: str) -> list[str]:
    return re.findall(r"(?m)^@param\[([A-Za-z_]\w*)\]\s*:", comment)


def _validate_example(
    filepath: str, line: int, function_name: str, comment: str
) -> list[str]:
    errors: list[str] = []
    example = _extract_section(comment, "Example")
    if example is None:
        errors.append(
            f"{filepath}:{line}: ERROR: missing # Example for '{function_name}'"
        )
        return errors

    code_match = re.search(r"(?ms)```c\s*(.*?)```", example)
    if not code_match:
        errors.append(
            f"{filepath}:{line}: ERROR: # Example for "
            f"'{function_name}' must include a fenced ```c block"
        )
        return errors

    if not re.search(r"\bmain\s*\(", code_match.group(1)):
        errors.append(
            f"{filepath}:{line}: ERROR: # Example code block for "
            f"'{function_name}' must include main(...) usage"
        )
    return errors


def _validate_param_docs(
    filepath: str, line: int, function_name: str, params: list[str], comment: str
) -> list[str]:
    warnings: list[str] = []
    doc_params = _param_doc_names(comment)
    for param in params:
        if param not in doc_params:
            warnings.append(
                f"{filepath}:{line}: WARNING: missing @param[{param}] for "
                f"'{function_name}'"
            )
    for doc_param in doc_params:
        if doc_param not in params:
            warnings.append(
                f"{filepath}:{line}: WARNING: @param[{doc_param}] does not "
                f"match any parameter in '{function_name}'"
            )
    return warnings


def _preceding_comment(
    comments: list[tuple[int, int, str]], content: str, function_start: int
) -> str | None:
    for _start, end, text in reversed(comments):
        if end > function_start:
            continue
        if content[end:function_start].strip():
            return None
        return text
    return None


def _validate_function_doc(
    filepath: str,
    content: str,
    function_match: re.Match[str],
    comments: list[tuple[int, int, str]],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    function_name = function_match.group("name")
    line = content.count("\n", 0, function_match.start()) + 1
    params = _param_names(function_match.group("params"))
    raw_comment = _preceding_comment(comments, content, function_match.start())

    if raw_comment is None:
        errors.append(
            f"{filepath}:{line}: ERROR: missing docstring block for "
            f"'{function_name}'"
        )
        return errors, warnings

    comment = _normalize_comment(raw_comment)
    about = _extract_section(comment, "About")
    if not about:
        errors.append(
            f"{filepath}:{line}: ERROR: missing non-empty # About for "
            f"'{function_name}'"
        )

    errors.extend(_validate_example(filepath, line, function_name, comment))
    warnings.extend(
        _validate_param_docs(filepath, line, function_name, params, comment)
    )

    return errors, warnings


def check(files: Sequence[str], strict: bool = False) -> bool:
    """Validate piscine-style function docstrings in staged C files."""
    c_files = [f for f in files if f.endswith(".c")]
    if not c_files:
        return True

    errors: list[str] = []
    warnings: list[str] = []

    for filepath in c_files:
        try:
            content = Path(filepath).read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{filepath}: ERROR: cannot read file: {exc}")
            continue

        comments = [
            (match.start(), match.end(), match.group(0))
            for match in _COMMENT_PATTERN.finditer(content)
        ]

        for match in _FUNCTION_PATTERN.finditer(content):
            function_name = match.group("name")
            if function_name in _SKIP_NAMES:
                continue
            function_errors, function_warnings = _validate_function_doc(
                filepath, content, match, comments
            )
            errors.extend(function_errors)
            warnings.extend(function_warnings)

    if errors:
        print("\n".join(errors), file=sys.stderr)
    if warnings:
        print("\n".join(warnings), file=sys.stderr)

    if strict and errors:
        return False
    return True
