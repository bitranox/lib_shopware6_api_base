"""Clean build artifacts and cache directories.

Reads patterns from pyproject.toml [tool.clean].patterns or uses built-in defaults.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterable
from pathlib import Path

from .toml_config import load_pyproject_config

_FALLBACK_PATTERNS: tuple[str, ...] = (
    ".hypothesis",
    ".import_linter_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".pyright",
    ".mypy_cache",
    ".tox",
    ".nox",
    ".eggs",
    "*.egg-info",
    "build",
    "dist",
    "htmlcov",
    ".coverage",
    "coverage.xml",
    "codecov.sh",
    ".cache",
    "result",
)

__all__ = ["clean", "get_clean_patterns"]


def get_clean_patterns(pyproject: Path = Path("pyproject.toml")) -> tuple[str, ...]:
    """Read clean patterns from pyproject.toml [tool.clean].patterns."""
    config = load_pyproject_config(pyproject)
    patterns = config.tool.clean.patterns
    if patterns:
        return patterns
    return _FALLBACK_PATTERNS


# For backwards compatibility
DEFAULT_PATTERNS = get_clean_patterns()


def clean(patterns: Iterable[str] | None = None) -> None:
    """Remove cached artefacts and build outputs matching ``patterns``.

    Args:
        patterns: Glob patterns to remove. If None, reads from pyproject.toml
                  or uses built-in defaults.
    """
    if patterns is None:
        patterns = get_clean_patterns()

    for pattern in patterns:
        for path in Path.cwd().glob(pattern):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                try:
                    path.unlink()
                except FileNotFoundError:
                    continue


if __name__ == "__main__":  # pragma: no cover
    from .cli import main as cli_main

    cli_main(["clean"])
