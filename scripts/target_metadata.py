"""Automation target metadata shared by CLI helpers and interactive tools.

Purpose
-------
Provide a single source of truth for the project's automation targets so the
command-line interface, Makefile delegations, and the Textual TUI all present
consistent names, descriptions, and environment-based defaults.

Contents
--------
* ``ParamSpec`` – describes tunable environment parameters exposed to users.
* ``TargetSpec`` – captures a Make/CLI target and its description.
* ``get_targets`` – returns the current targets with environment defaults.
* ``iter_help_rows`` – yields ``(name, description)`` pairs for help output.

System Role
-----------
Keeps automation metadata aligned with documentation and developer workflow
guidance by centralising the definitions referenced by ``scripts.menu`` and
``scripts.help``. This reduces duplication and ensures future changes remain
cohesive across interfaces.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass

from ._utils import get_default_remote

__all__ = [
    "ParamSpec",
    "TargetSpec",
    "get_targets",
    "iter_help_rows",
]

_DEFAULT_REMOTE = get_default_remote()


@dataclass(frozen=True)
class ParamSpec:
    """Describe a configurable environment variable for an automation target."""

    name: str
    description: str
    default: str | None = None
    choices: tuple[str, ...] | None = None
    validator: Callable[[str], bool] | None = None


@dataclass(frozen=True)
class TargetSpec:
    """Describe a Make/CLI target exposed by the automation toolbox."""

    name: str
    description: str
    params: tuple[ParamSpec, ...] = ()


def _env_default(name: str, fallback: str | None = None) -> str | None:
    """Return the environment variable value when set, otherwise fallback."""
    value = os.getenv(name)
    return value if value is not None and value != "" else fallback


def _build_targets() -> tuple[TargetSpec, ...]:
    """Create the immutable collection of automation targets."""
    return (
        TargetSpec("install", "Editable install", ()),
        TargetSpec("dev", "Editable install with dev extras", ()),
        TargetSpec(
            "test",
            "Lint, type-check, run tests, and upload coverage",
            (
                ParamSpec(
                    "COVERAGE",
                    "Coverage mode (on|auto|off)",
                    default=_env_default("COVERAGE", "on"),
                    choices=("on", "auto", "off"),
                ),
                ParamSpec(
                    "SKIP_BOOTSTRAP",
                    "Skip dependency bootstrap (0|1)",
                    default=_env_default("SKIP_BOOTSTRAP", "0"),
                    choices=("0", "1"),
                ),
                ParamSpec(
                    "TEST_VERBOSE",
                    "Verbose test runner output (0|1)",
                    default=_env_default("TEST_VERBOSE", "0"),
                    choices=("0", "1"),
                ),
            ),
        ),
        TargetSpec(
            "coverage",
            "Run python -m coverage run -m pytest -vv and report",
            (
                ParamSpec(
                    "TEST_VERBOSE",
                    "Verbose coverage run output (0|1)",
                    default=_env_default("TEST_VERBOSE", "0"),
                    choices=("0", "1"),
                ),
            ),
        ),
        TargetSpec(
            "test-local",
            "Run local-only tests (SMTP, script composition, external resources)",
            (
                ParamSpec(
                    "TEST_VERBOSE",
                    "Verbose test output (0|1)",
                    default=_env_default("TEST_VERBOSE", "0"),
                    choices=("0", "1"),
                ),
            ),
        ),
        TargetSpec("run", "Run project CLI (defaults to --help)", ()),
        TargetSpec("version-current", "Print version from pyproject.toml", ()),
        TargetSpec(
            "bump",
            "Bump version and update changelog",
            (
                ParamSpec(
                    "VERSION",
                    "Explicit version X.Y.Z",
                    default=_env_default("VERSION"),
                ),
                ParamSpec(
                    "PART",
                    "Version part when VERSION unset",
                    default=_env_default("PART", "patch"),
                    choices=("major", "minor", "patch"),
                ),
            ),
        ),
        TargetSpec("bump-patch", "Bump patch version", ()),
        TargetSpec("bump-minor", "Bump minor version", ()),
        TargetSpec("bump-major", "Bump major version", ()),
        TargetSpec("clean", "Remove caches, build artifacts, coverage", ()),
        TargetSpec(
            "push",
            "Run tests, commit (<version> - <message>), and push",
            (
                ParamSpec(
                    "REMOTE",
                    "Git remote",
                    default=_env_default("REMOTE", _DEFAULT_REMOTE),
                ),
            ),
        ),
        TargetSpec("build", "Build wheel/sdist artifacts", ()),
        TargetSpec(
            "release",
            "Tag vX.Y.Z from pyproject and create release",
            (
                ParamSpec(
                    "REMOTE",
                    "Git remote",
                    default=_env_default("REMOTE", _DEFAULT_REMOTE),
                ),
            ),
        ),
        TargetSpec(
            "dependencies",
            "Check dependencies against latest PyPI versions",
            (
                ParamSpec(
                    "VERBOSE",
                    "Show all dependencies (0|1)",
                    default=_env_default("VERBOSE", "0"),
                    choices=("0", "1"),
                ),
            ),
        ),
        TargetSpec(
            "dependencies-update",
            "Update all outdated dependencies to latest versions",
            (
                ParamSpec(
                    "DRY_RUN",
                    "Preview changes without modifying (0|1)",
                    default=_env_default("DRY_RUN", "0"),
                    choices=("0", "1"),
                ),
            ),
        ),
        TargetSpec("menu", "Interactive TUI automation menu", ()),
        TargetSpec("help", "Show automation command summary", ()),
    )


def get_targets() -> tuple[TargetSpec, ...]:
    """Return the current automation targets with environment defaults."""
    return _build_targets()


def iter_help_rows(targets: Iterable[TargetSpec] | None = None) -> Iterator[tuple[str, str]]:
    """Yield ``(name, description)`` tuples for help/summary displays."""
    items = targets if targets is not None else get_targets()
    for target in items:
        yield target.name, target.description
