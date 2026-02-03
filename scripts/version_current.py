"""Print the current version from pyproject.toml."""

from __future__ import annotations

from pathlib import Path

from ._utils import read_version_from_pyproject

__all__ = ["print_current_version"]


def print_current_version(pyproject: Path = Path("pyproject.toml")) -> str:
    """Return the project version declared in ``pyproject.toml``."""
    version = read_version_from_pyproject(pyproject)
    if not version:
        raise SystemExit("version not found")
    return version


if __name__ == "__main__":  # pragma: no cover
    print(print_current_version())
