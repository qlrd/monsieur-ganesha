"""Entry point for ``python -m ganesha``.

Allows the package to be invoked directly with the Python interpreter
without requiring the ``ganesha`` console script to be installed::

    python -m ganesha norminette file.c
    python -m ganesha compiler    file.c
    python -m ganesha forbidden   file.c
    python -m ganesha commit-msg  .git/COMMIT_EDITMSG

This is especially useful during development before the package has
been installed into a virtual environment, and in environments where
adding scripts to ``$PATH`` is not convenient.

The module simply delegates to :func:`ganesha.cli.main`, which
handles argument parsing and dispatching.
"""

from ganesha.cli import main

main()
