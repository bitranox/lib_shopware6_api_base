"""Install the project with development extras."""

from __future__ import annotations

import sys

from ._utils import run

__all__ = ["install_dev"]


def install_dev(*, dry_run: bool = False) -> None:
    """Install the project with development extras."""
    run([sys.executable, "-m", "pip", "install", "-e", ".[dev]"], dry_run=dry_run)


if __name__ == "__main__":  # pragma: no cover
    from .cli import main as cli_main

    cli_main(["dev", *sys.argv[1:]])
