"""Invoke the project CLI via uvx from the local development directory."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

from ._utils import get_dependencies, get_project_metadata, run

PROJECT = get_project_metadata()

__all__ = ["run_cli"]


def _find_local_dependencies() -> list[tuple[str, str]]:
    """Find sibling directories that match project dependencies.

    Scans the parent directory for subdirectories that match dependency names
    and contain a pyproject.toml file (indicating a valid Python project).

    Returns:
        List of tuples (package_name, absolute_path) for local dependencies.
        Package names use hyphens (PyPI convention) for --reinstall-package.
    """
    project_root = Path.cwd().resolve()
    parent_dir = project_root.parent
    dependencies = get_dependencies()

    local_deps: list[tuple[str, str]] = []
    for dep_name in dependencies:
        # Check both underscore and hyphen variants for directory names
        variants = [dep_name, dep_name.replace("_", "-")]
        for variant in variants:
            sibling = parent_dir / variant
            if sibling.is_dir() and (sibling / "pyproject.toml").exists():
                # Use hyphenated name for --reinstall-package (PyPI convention)
                package_name = dep_name.replace("_", "-")
                local_deps.append((package_name, str(sibling)))
                break
    return local_deps


def run_cli(args: Sequence[str] | None = None) -> int:
    """Invoke the project CLI via uvx using the local development version.

    Uses --no-cache to bypass the cache entirely, ensuring all packages
    (including local dependencies) are always rebuilt from source.
    Discovers sibling directories that match project dependencies and
    includes them with --with flags.

    This approach is project-independent: it reads dependencies from
    pyproject.toml and finds matching sibling directories automatically.
    """
    forwarded = list(args) if args else ["--help"]

    # Build command with no cache to ensure fresh builds
    command = ["uvx", "--from", ".", "--no-cache"]

    # Add local sibling dependencies
    for _dep_name, local_path in _find_local_dependencies():
        command.extend(["--with", local_path])

    command.extend([PROJECT.name, *forwarded])

    result = run(command, capture=False, check=False)
    return result.code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run_cli(sys.argv[1:]))
