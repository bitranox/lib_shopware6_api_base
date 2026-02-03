"""Build wheel and sdist artifacts for PyPI distribution."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import rich_click as click

from ._utils import get_project_metadata, run

__all__ = ["build_artifacts"]

PROJECT = get_project_metadata()
DIST_DIR = Path("dist")


def _status(label: str) -> str:
    return click.style(label, fg="green")


def _failure(label: str) -> str:
    return click.style(label, fg="red")


def _purge_dist(dist_dir: Path = DIST_DIR) -> None:
    """Remove the dist directory so stale artifacts never reach PyPI."""
    if not dist_dir.exists():
        return
    click.echo(f"[build] Removing stale artifacts in {dist_dir.as_posix()}/")
    shutil.rmtree(dist_dir)


def build_artifacts() -> None:
    """Build Python wheel and sdist artifacts."""
    _purge_dist()
    click.echo("[build] Building wheel/sdist via python -m build")
    build_result = run(["python", "-m", "build"], check=False, capture=False)
    click.echo(f"[build] {_status('success') if build_result.code == 0 else _failure('failed')}")
    if build_result.code != 0:
        raise SystemExit(build_result.code)


def main() -> None:  # pragma: no cover
    build_artifacts()


if __name__ == "__main__":  # pragma: no cover
    from .cli import main as cli_main

    cli_main(["build", *sys.argv[1:]])
