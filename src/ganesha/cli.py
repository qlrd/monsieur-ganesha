"""Command-line interface for Monsieur Ganesha.

This module provides the ``ganesha`` console script entry point.
It is a thin dispatcher that parses arguments and delegates to the
appropriate check module.  All business logic lives in
:mod:`ganesha.checks` and :mod:`ganesha.config`.

Subcommands
-----------
``ganesha norminette <files...>``
    Run the norminette check on the given files.

``ganesha compiler <files...>``
    Run the gcc syntax check on the given files.

``ganesha forbidden <files...>``
    Run the forbidden-function scan on the given files.  Reads the
    forbidden function list from ``.ganesha.toml`` in the current
    working directory.

``ganesha commit-msg <file>``
    Validate the commit message stored in *file*.  Reads the optional
    custom pattern from ``.ganesha.toml``.

Exit codes
----------
``0``
    The check passed.

``1``
    The check failed.  Details are printed to *stderr*.

``2``
    Internal error (e.g. malformed ``.ganesha.toml``).  Details
    are printed to *stderr*.

Usage from the shell
--------------------
After installing with ``uv sync`` or ``pip install -e .`` the
``ganesha`` script is available on ``$PATH``::

    ganesha norminette  ex00/ft_putchar.c header.h
    ganesha compiler    ex00/ft_putchar.c
    ganesha forbidden   ex00/ft_putchar.c
    ganesha commit-msg  .git/COMMIT_EDITMSG

pre-commit invokes the same script automatically on every ``git commit``.
"""

import argparse
import sys

from ganesha import checks, config


def main() -> None:
    """Parse command-line arguments and dispatch to the correct check.

    This function is registered as the ``ganesha`` console script
    entry point in ``pyproject.toml``::

        [project.scripts]
        ganesha = "ganesha.cli:main"

    It is also called when the package is run as a module::

        python -m ganesha norminette file.c

    The function never returns normally: it always calls
    :func:`sys.exit` with an appropriate exit code (0, 1, or 2).

    Raises:
        SystemExit: Always.  Exit code 0 on success, 1 on check
            failure, 2 on internal error (configuration parse error).
    """
    parser = argparse.ArgumentParser(
        prog="ganesha",
        description="Pre-commit hooks para 42 school piscine",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_norm = sub.add_parser(
        "norminette",
        help="verifica arquivos C/H contra a norma 42",
    )
    p_norm.add_argument("files", nargs="*")

    p_comp = sub.add_parser(
        "compiler",
        help="compila .c com -Wall -Wextra -Werror (syntax check)",
    )
    p_comp.add_argument("files", nargs="*")

    p_forb = sub.add_parser(
        "forbidden",
        help="verifica uso de funções proibidas (lê .ganesha.toml)",
    )
    p_forb.add_argument("files", nargs="*")

    p_msg = sub.add_parser(
        "commit-msg",
        help="valida o formato da mensagem de commit",
    )
    p_msg.add_argument(
        "file",
        help="caminho para o arquivo com a mensagem de commit",
    )

    args = parser.parse_args()

    try:
        if args.command == "norminette":
            ok = checks.norminette.check(args.files)
        elif args.command == "compiler":
            ok = checks.compiler.check(args.files)
        elif args.command == "forbidden":
            cfg = config.load_config()
            ok = checks.forbidden.check(args.files, cfg.forbidden.functions)
        elif args.command == "commit-msg":
            cfg = config.load_config()
            pattern = cfg.commit.pattern or checks.commit_msg.DEFAULT_PATTERN
            ok = checks.commit_msg.check(args.file, pattern)
        else:
            ok = False
    except ValueError as e:
        print(f"Erro interno: {e}", file=sys.stderr)
        sys.exit(2)

    sys.exit(0 if ok else 1)
