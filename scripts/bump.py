"""Version bumping utilities that delegate to bump_version.py."""

from __future__ import annotations

import sys
from pathlib import Path

from ._utils import run

__all__ = ["bump"]


def bump(
    *,
    version: str | None = None,
    part: str | None = None,
    pyproject: Path = Path("pyproject.toml"),
    changelog: Path = Path("CHANGELOG.md"),
) -> None:
    """Bump the project version and update the changelog."""
    args = [sys.executable, "scripts/bump_version.py"]
    if version:
        args += ["--version", version]
    else:
        args += ["--part", part or "patch"]
    args += ["--pyproject", str(pyproject), "--changelog", str(changelog)]
    run(args)


if __name__ == "__main__":  # pragma: no cover
    from .cli import main as cli_main

    cli_main(["bump", *sys.argv[1:]])
