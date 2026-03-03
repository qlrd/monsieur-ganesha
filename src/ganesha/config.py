"""Configuration loader for Monsieur Ganesha.

This module provides :func:`load_config`, which reads an optional
``.ganesha.toml`` file from the root of the student's repository
and returns a :class:`Config` dataclass with safe defaults.

The configuration file is intentionally optional: if it does not exist
the loader returns a :class:`Config` with empty forbidden-function list
and no custom commit pattern, so all hooks still work out of the box.

Typical ``.ganesha.toml`` layout::

    [project]
    name = "C00"

    [forbidden]
    functions = ["printf", "malloc", "free"]

    [commit]
    # Override the default Conventional Commits 1.0.0 pattern.
    # Uncomment the line below to use the 42-school ex00: format instead.
    # pattern = "^(ex|rush|exam)\\\\d+: .+"

Design decisions
----------------
* ``tomllib`` is part of the Python 3.11 standard library, so no
  external TOML dependency is needed.
* A missing file returns :class:`Config` with defaults rather than
  raising an error: the student should not be blocked by a missing
  config file.
* An *existing but malformed* TOML file raises :class:`ValueError`
  so the problem is surfaced immediately.
"""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

CONFIG_FILE = ".ganesha.toml"


@dataclass
class ProjectConfig:
    """Project-level metadata from the ``[project]`` TOML table.

    Attributes:
        name: Short identifier for the current module, e.g. ``"C00"``
            or ``"rush01"``.  Used only for informational purposes;
            no hook behaviour depends on it.  Defaults to ``None``
            when the key is absent from the configuration file.
    """

    name: Optional[str] = None


@dataclass
class ForbiddenConfig:
    """Forbidden-function configuration from the ``[forbidden]`` TOML table.

    Attributes:
        functions: List of C function names that are disallowed in the
            current module.  The :mod:`ganesha.checks.forbidden`
            module builds a regex alternation from this list and scans
            every staged ``.c`` file.

            The list is empty by default, meaning the
            ``forbidden-functions`` hook always passes unless the
            student explicitly adds entries here.

    Example::

        [forbidden]
        functions = ["printf", "malloc", "realloc", "free", "calloc"]
    """

    functions: list[str] = field(default_factory=list)


@dataclass
class CommitConfig:
    """Commit-message configuration from the ``[commit]`` TOML table.

    Attributes:
        pattern: Optional regular expression used to validate the
            commit message subject line.  When ``None`` (the default),
            :mod:`ganesha.checks.commit_msg` uses
            :const:`~ganesha.checks.commit_msg.DEFAULT_PATTERN`
            (Conventional Commits 1.0.0).

            Override this to accept a different format, for example
            the 42-school ``ex00: description`` style::

                [commit]
                pattern = "^(ex|rush|exam)\\\\d+: .+"

            Note that the gamification layer (francinette approvals,
            ultimate type easter egg, +XP for breaking changes) is
            active **only** when the default pattern is in use.
    """

    pattern: Optional[str] = None


@dataclass
class Config:
    """Root configuration object returned by :func:`load_config`.

    Aggregates all TOML sections into a single, typed container.
    All fields default to their respective dataclass defaults so that
    the object is always fully usable even when the configuration file
    is absent.

    Attributes:
        project: Metadata from the ``[project]`` table.
        forbidden: Forbidden-function list from the ``[forbidden]``
            table.
        commit: Commit-message pattern from the ``[commit]`` table.
    """

    project: ProjectConfig = field(default_factory=ProjectConfig)
    forbidden: ForbiddenConfig = field(default_factory=ForbiddenConfig)
    commit: CommitConfig = field(default_factory=CommitConfig)


def load_config(root: Optional[Path] = None) -> Config:
    """Load ``.ganesha.toml`` and return a typed :class:`Config` object.

    Searches for ``.ganesha.toml`` in *root* (or the current working
    directory when *root* is ``None``).  If the file does not exist a
    default :class:`Config` is returned silently.  If the file exists
    but contains invalid TOML a :class:`ValueError` is raised so the
    student sees the problem immediately rather than silently receiving
    wrong defaults.

    Args:
        root: Directory in which to look for ``.ganesha.toml``.
            Pass an explicit :class:`~pathlib.Path` in tests to avoid
            touching the working directory.  Defaults to ``None``,
            which resolves to the current working directory
            (``Path(".ganesha.toml")``).

    Returns:
        A fully-populated :class:`Config` dataclass.  All fields have
        safe defaults, so callers do not need to guard against
        ``None`` at the top level.

    Raises:
        ValueError: If ``.ganesha.toml`` exists but cannot be parsed
            as valid TOML.  The message includes the file path and the
            underlying parse error from :mod:`tomllib`.

    Examples:
        Load config from the current directory (normal hook usage)::

            cfg = load_config()
            print(cfg.forbidden.functions)  # [] if key absent

        Load config from a specific directory (useful in tests)::

            from pathlib import Path
            cfg = load_config(Path("/tmp/my_project"))

        Access the optional commit pattern::

            pattern = cfg.commit.pattern or DEFAULT_PATTERN
    """
    path = (root / CONFIG_FILE) if root else Path(CONFIG_FILE)

    if not path.exists():
        return Config()

    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"TOML inválido em {path}: {e}") from e

    project = ProjectConfig(
        name=data.get("project", {}).get("name"),
    )
    forbidden = ForbiddenConfig(
        functions=data.get("forbidden", {}).get("functions", []),
    )
    commit = CommitConfig(
        pattern=data.get("commit", {}).get("pattern"),
    )
    return Config(project=project, forbidden=forbidden, commit=commit)
