"""Convenience wrapper for bumping the patch version component."""

from __future__ import annotations

import sys
from pathlib import Path

from .bump import bump

__all__ = ["bump_patch"]


def bump_patch(pyproject: Path = Path("pyproject.toml"), changelog: Path = Path("CHANGELOG.md")) -> None:
    """Convenience wrapper to bump the patch version component."""
    bump(part="patch", pyproject=pyproject, changelog=changelog)


if __name__ == "__main__":  # pragma: no cover
    from .cli import main as cli_main

    cli_main(["bump", "--part", "patch", *sys.argv[1:]])
