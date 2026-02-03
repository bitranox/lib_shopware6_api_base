"""Install the project in editable mode."""

from __future__ import annotations

import sys

from ._utils import run

__all__ = ["install"]


def install(*, dry_run: bool = False) -> None:
    """Install the project in editable mode."""
    run([sys.executable, "-m", "pip", "install", "-e", "."], dry_run=dry_run)


if __name__ == "__main__":  # pragma: no cover
    from .cli import main as cli_main

    cli_main(["install", *sys.argv[1:]])
