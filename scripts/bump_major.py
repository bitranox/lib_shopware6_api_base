"""Convenience wrapper for bumping the major version component."""

from __future__ import annotations

import sys
from pathlib import Path

from .bump import bump

__all__ = ["bump_major"]


def bump_major(pyproject: Path = Path("pyproject.toml"), changelog: Path = Path("CHANGELOG.md")) -> None:
    """Convenience wrapper to bump the major version component."""
    bump(part="major", pyproject=pyproject, changelog=changelog)


if __name__ == "__main__":  # pragma: no cover
    from .cli import main as cli_main

    cli_main(["bump", "--part", "major", *sys.argv[1:]])
