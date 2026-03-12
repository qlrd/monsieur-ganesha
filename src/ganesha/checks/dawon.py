"""Optional pre-push check that runs ``dawon check``.

This module implements the ``dawon-check`` hook for the ``pre-push``
stage.  The hook is intentionally optional and does nothing when the
``dawon`` binary is not available on ``$PATH``.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Optional


def check(module_path: Optional[str]) -> bool:
    """Run ``dawon check --path`` for the configured project module.

    Args:
        module_path: Value from ``[project] module`` in
            ``.ganesha.toml``.  When missing or empty, ``"."`` is used.

    Returns:
        ``True`` when ``dawon`` is unavailable (silent skip) or when the
        command exits with code 0.  ``False`` when ``dawon`` returns a
        non-zero code.
    """
    if shutil.which("dawon") is None:
        return True

    path = module_path or "."
    result = subprocess.run(
        ["dawon", "check", "--path", str(Path(path))],
        check=False,
    )
    return result.returncode == 0
