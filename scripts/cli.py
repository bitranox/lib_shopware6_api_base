"""CLI entry point for project automation commands."""

from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path

import rich_click as click

from . import build as build_module
from . import bump as bump_module
from . import clean as clean_module
from . import dependencies as dependencies_module
from . import dev as dev_module
from . import help as help_module
from . import install as install_module
from . import menu as menu_module
from . import push as push_module
from . import release as release_module
from . import run_cli as run_cli_module
from . import test as test_module
from . import version_current as version_module
from ._utils import get_default_remote
from .bump_major import bump_major
from .bump_minor import bump_minor
from .bump_patch import bump_patch

__all__ = ["main"]

_COVERAGE_MODES = {"on", "auto", "off"}
_BUMP_PARTS = {"major", "minor", "patch"}
_DEFAULT_REMOTE = get_default_remote()


def env_token(name: str) -> str | None:
    """Return an environment variable stripped of surrounding whitespace."""
    raw = os.getenv(name)
    if raw is None:
        return None
    token = raw.strip()
    return token or None


def choose_token(
    option: str | None,
    *,
    fallbacks: tuple[str | None, ...],
    allowed: set[str],
    label: str,
    default: str,
) -> str:
    """Pick the first non-empty token, ensuring it belongs to the allowed family."""
    for candidate in (option, *fallbacks):
        if candidate is None:
            continue
        token = candidate.strip().lower()
        if token in allowed:
            return token
        allowed_values = ", ".join(sorted(allowed))
        raise click.ClickException(f"{label} must be one of: {allowed_values}")
    return default


def coverage_choice(option: str | None) -> str:
    """Resolve the coverage mode using CLI flag, environment, then default."""
    return choose_token(
        option,
        fallbacks=(env_token("COVERAGE"),),
        allowed=_COVERAGE_MODES,
        label="COVERAGE",
        default="on",
    )


def part_choice(option: str | None) -> str:
    """Resolve the version part to bump."""
    return choose_token(
        option,
        fallbacks=(env_token("PART"),),
        allowed=_BUMP_PARTS,
        label="PART",
        default="patch",
    )


def remote_choice(option: str | None) -> str:
    """Resolve the git remote for push-like workflows."""
    return option or env_token("REMOTE") or _DEFAULT_REMOTE


click.rich_click.GROUP_ARGUMENTS_OPTIONS = True


@click.group(help="Automation toolbox for project workflows.")
def main() -> None:
    """Entry point for the scripts CLI."""


@main.command(name="help", help="Show automation target summary")
def help_command() -> None:
    help_module.print_help()


@main.command(name="install", help="Editable install: pip install -e .")
@click.option("--dry-run", is_flag=True, help="Print commands only")
def install_command(dry_run: bool) -> None:
    install_module.install(dry_run=dry_run)


@main.command(name="dev", help="Install with development extras: pip install -e .[dev]")
@click.option("--dry-run", is_flag=True, help="Print commands only")
def dev_command(dry_run: bool) -> None:
    dev_module.install_dev(dry_run=dry_run)


@main.command(name="clean", help="Remove caches and build artefacts")
@click.option("--pattern", "patterns", multiple=True, help="Additional glob patterns to delete")
def clean_command(patterns: tuple[str, ...]) -> None:
    target_patterns = clean_module.DEFAULT_PATTERNS + tuple(patterns)
    clean_module.clean(target_patterns)


@main.command(
    name="run",
    help="Run the project CLI and forward extra arguments",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
    add_help_option=False,
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def run_command(args: Sequence[str]) -> None:
    raise SystemExit(run_cli_module.run_cli(args))


@main.command(name="test", help="Run lint, type-check, tests, and coverage upload")
@click.option("--coverage", type=click.Choice(sorted(_COVERAGE_MODES)), default=None, show_default=False)
@click.option("--verbose", is_flag=True, help="Print executed commands")
@click.option("--strict-format/--no-strict-format", default=None, help="Control ruff format behaviour")
def test_command(coverage: str | None, verbose: bool, strict_format: bool | None) -> None:
    resolved_coverage = coverage_choice(coverage)
    test_module.run_tests(
        coverage=resolved_coverage,
        verbose=verbose,
        strict_format=strict_format,
    )


@main.command(name="coverage", help="Run python -m coverage run -m pytest -vv (no PATH shim needed)")
@click.option("--verbose", is_flag=True, help="Print executed commands and stdout/stderr")
def coverage_command(verbose: bool) -> None:
    test_module.run_coverage(verbose=verbose)


@main.command(name="test-local", help="Run local-only tests (requires external resources)")
@click.option("--verbose", is_flag=True, help="Print verbose test output")
def test_local_command(verbose: bool) -> None:
    """Run tests marked local_only (skipped in CI).

    These tests require external resources (SMTP server, etc.) or the local
    dev environment. Configure EMAIL__SMTP_HOSTS and EMAIL__FROM_ADDRESS in .env.
    """
    test_module.run_local_tests(verbose=verbose)


@main.command(name="build", help="Build wheel/sdist artifacts")
def build_command() -> None:
    build_module.build_artifacts()


@main.command(name="release", help="Create git tag and optional GitHub release")
@click.option("--remote", default=None, show_default=False)
def release_command(remote: str | None) -> None:
    resolved_remote = remote_choice(remote)
    release_module.release(remote=resolved_remote)


@main.command(name="push", help="Run checks, commit, and push current branch")
@click.option("--remote", default=None, show_default=False)
@click.argument("message_words", nargs=-1, type=click.UNPROCESSED)
def push_command(remote: str | None, message_words: tuple[str, ...]) -> None:
    resolved_remote = remote_choice(remote)
    message = " ".join(message_words).strip() if message_words else env_token("COMMIT_MESSAGE")
    push_module.push(remote=resolved_remote, message=message or None)


@main.command(name="version-current", help="Print current version from pyproject.toml")
@click.option("--pyproject", type=click.Path(path_type=Path), default=Path("pyproject.toml"))
def version_command(pyproject: Path) -> None:
    click.echo(version_module.print_current_version(pyproject))


@main.command(name="bump", help="Bump version and changelog")
@click.option("--version", "version_", type=str, help="Explicit version X.Y.Z")
@click.option("--part", type=click.Choice(["major", "minor", "patch"]), default=None)
@click.option("--pyproject", type=click.Path(path_type=Path), default=Path("pyproject.toml"))
@click.option("--changelog", type=click.Path(path_type=Path), default=Path("CHANGELOG.md"))
def bump_command(
    version_: str | None,
    part: str | None,
    pyproject: Path,
    changelog: Path,
) -> None:
    resolved_version = version_ or env_token("VERSION")
    resolved_part = part_choice(part)
    bump_module.bump(version=resolved_version, part=resolved_part, pyproject=pyproject, changelog=changelog)


@main.command(name="bump-major", help="Convenience wrapper to bump major version")
def bump_major_command() -> None:
    bump_major()


@main.command(name="bump-minor", help="Convenience wrapper to bump minor version")
def bump_minor_command() -> None:
    bump_minor()


@main.command(name="bump-patch", help="Convenience wrapper to bump patch version")
def bump_patch_command() -> None:
    bump_patch()


@main.command(name="dependencies", help="Check dependencies against latest PyPI versions")
@click.option("--verbose", "-v", is_flag=True, help="Show all dependencies, not just outdated")
@click.option("--update", "-u", is_flag=True, help="Update outdated dependencies to latest versions")
@click.option("--dry-run", is_flag=True, help="Show what would be updated without making changes")
@click.option("--pyproject", type=click.Path(path_type=Path), default=Path("pyproject.toml"))
def dependencies_command(verbose: bool, update: bool, dry_run: bool, pyproject: Path) -> None:
    raise SystemExit(dependencies_module.main(verbose=verbose, update=update, dry_run=dry_run, pyproject=pyproject))


@main.command(name="dependencies-update", help="Update all outdated dependencies to latest versions")
@click.option("--dry-run", is_flag=True, help="Show what would be updated without making changes")
@click.option("--pyproject", type=click.Path(path_type=Path), default=Path("pyproject.toml"))
def dependencies_update_command(dry_run: bool, pyproject: Path) -> None:
    raise SystemExit(dependencies_module.main(verbose=False, update=True, dry_run=dry_run, pyproject=pyproject))


@main.command(name="menu", help="Launch interactive TUI menu")
def menu_command() -> None:
    menu_module.run_menu()


if __name__ == "__main__":  # pragma: no cover
    main()
