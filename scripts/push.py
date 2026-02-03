"""Run checks, commit changes, and push the current branch."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import rich_click as click

from . import dependencies as dependencies_module
from ._utils import (
    get_default_remote,
    get_project_metadata,
    git_branch,
    read_version_from_pyproject,
    run,
    sync_metadata_module,
)

__all__ = ["push"]

_DEFAULT_REMOTE = get_default_remote()


def _get_installed_version(package_name: str) -> str | None:
    """Get the installed version of a package, or None if not installed."""
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version(package_name)
    except (PackageNotFoundError, ValueError):
        return None


def _check_and_update_pip() -> None:
    """Check if pip is at the latest version and update if needed."""
    click.echo("[pip] Checking pip version...")

    installed = _get_installed_version("pip")
    if installed is None:
        click.echo("[pip] Could not determine installed pip version", err=True)
        return

    # Fetch latest pip version from PyPI
    latest = dependencies_module.fetch_latest_version("pip")
    if latest is None:
        click.echo("[pip] Could not fetch latest pip version from PyPI", err=True)
        return

    status = dependencies_module.compare_versions(installed, latest)

    if status == "up-to-date":
        click.echo(f"[pip] pip {installed} is up-to-date")
        return

    click.echo(f"[pip] pip {installed} is outdated (latest: {latest})")

    # Check if running in CI or non-interactive mode
    if os.getenv("CI") or not sys.stdin.isatty():
        click.echo("[pip] Updating pip...")
        _do_pip_upgrade()
        return

    # Prompt user for update
    try:
        response = click.prompt(
            "Do you want to update pip now?",
            type=click.Choice(["y", "n"], case_sensitive=False),
            default="y",
            show_choices=True,
        )
    except (click.Abort, EOFError):
        click.echo("\n[pip] Update skipped")
        return

    if response.lower() == "y":
        _do_pip_upgrade()
    else:
        click.echo("[pip] Update skipped")


def _do_pip_upgrade() -> None:
    """Execute pip upgrade command."""
    upgrade_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "pip"]
    if sys.platform.startswith("linux"):
        upgrade_cmd.insert(4, "--break-system-packages")

    result = run(upgrade_cmd, check=False, capture=True)

    if result.code == 0:
        new_version = _get_installed_version("pip")
        click.echo(f"[pip] Successfully updated to pip {new_version}")
    else:
        # Check for SHA256 verification errors in CI (known issue)
        combined = f"{result.out}\n{result.err}".lower()
        if "sha256" in combined and "hash" in combined:
            click.echo("[pip] Update failed due to hash verification (common in CI); continuing...")
        else:
            click.echo(f"[pip] Update failed (exit code {result.code})", err=True)
            if result.err:
                click.echo(result.err, err=True)


def _check_dependencies_and_prompt_update() -> None:
    """Check dependencies and prompt user to update if outdated."""
    click.echo("\n[dependencies] Checking for outdated dependencies...")

    try:
        deps = dependencies_module.check_dependencies()
    except Exception as exc:
        click.echo(f"[dependencies] Failed to check dependencies: {exc}", err=True)
        return

    outdated = [d for d in deps if d.status == "outdated"]

    if not outdated:
        click.echo("[dependencies] All dependencies are up-to-date!")
        return

    # Display outdated dependencies
    click.echo(f"\n[dependencies] Found {len(outdated)} outdated dependencies:\n")

    # Calculate column widths for alignment
    name_width = max(len(d.name) for d in outdated)
    current_width = max(len(d.current_min) for d in outdated)

    for dep in sorted(outdated, key=lambda d: d.name.lower()):
        click.echo(f"  {dep.name:<{name_width}}  {dep.current_min:<{current_width}}  -->  {dep.latest}")

    click.echo("")

    # Check if running in CI or non-interactive mode
    if os.getenv("CI") or not sys.stdin.isatty():
        click.echo("[dependencies] Run 'make dependencies-update' to update dependencies")
        return

    # Prompt user for update
    try:
        response = click.prompt(
            "Do you want to update these dependencies now?",
            type=click.Choice(["y", "n"], case_sensitive=False),
            default="n",
            show_choices=True,
        )
    except (click.Abort, EOFError):
        click.echo("\n[dependencies] Update skipped")
        return

    if response.lower() == "y":
        click.echo("\n[dependencies] Updating dependencies...")
        updated = dependencies_module.update_dependencies(deps, dry_run=False)
        if updated > 0:
            click.echo(f"[dependencies] Successfully updated {updated} dependencies")
            click.echo("[dependencies] Run 'make test' again to verify changes")
        else:
            click.echo("[dependencies] No dependencies were updated")
    else:
        click.echo("[dependencies] Update skipped. Run 'make dependencies-update' later to update.")


def _find_dependency_issues(
    deps: list[dependencies_module.DependencyInfo],
) -> tuple[list[tuple[str, str]], list[tuple[str, str, str, str]]]:
    """Identify missing and outdated installed packages.

    Compares each dependency's required minimum version against the locally
    installed version.  Pure logic -- no I/O or side-effects.

    Args:
        deps: Dependency metadata returned by ``check_dependencies``.

    Returns:
        A ``(missing, outdated_installed)`` tuple where *missing* contains
        ``(name, required_version)`` pairs and *outdated_installed* contains
        ``(name, installed, required, latest)`` tuples.
    """
    missing: list[tuple[str, str]] = []
    outdated_installed: list[tuple[str, str, str, str]] = []

    for dep in deps:
        if not dep.current_min:
            continue

        installed = _get_installed_version(dep.name)

        if installed is None:
            missing.append((dep.name, dep.current_min))
        else:
            installed_status = dependencies_module.compare_versions(installed, dep.current_min)
            if installed_status == "outdated":
                outdated_installed.append((dep.name, installed, dep.current_min, dep.latest))

    return missing, outdated_installed


def _display_dependency_issues(
    missing: list[tuple[str, str]],
    outdated_installed: list[tuple[str, str, str, str]],
) -> None:
    """Display missing and outdated packages via ``click.echo``.

    Args:
        missing: ``(name, required_version)`` pairs for packages not installed.
        outdated_installed: ``(name, installed, required, latest)`` tuples for
            packages whose installed version is below the requirement.
    """
    if missing:
        click.echo(f"\n[dependencies] {len(missing)} packages are NOT installed:\n")
        name_width = max(len(name) for name, _ in missing)
        for name, required in sorted(missing):
            click.echo(f"  [X] {name:<{name_width}}  (requires >={required})")

    if outdated_installed:
        click.echo(f"\n[dependencies] {len(outdated_installed)} installed packages are below required version:\n")
        name_width = max(len(name) for name, _, _, _ in outdated_installed)
        installed_width = max(len(installed) for _, installed, _, _ in outdated_installed)
        for name, installed, required, latest in sorted(outdated_installed):
            click.echo(
                f"  [!] {name:<{name_width}}  {installed:<{installed_width}}  (requires >={required}, latest: {latest})"
            )


def _prompt_and_install_dependencies(total_issues: int) -> None:
    """Prompt the user to install or update packages and run pip if accepted.

    In CI or non-interactive environments a hint is printed instead of
    prompting.

    Args:
        total_issues: Combined count of missing and outdated packages (used in
            the hint message).
    """
    if os.getenv("CI") or not sys.stdin.isatty():
        click.echo(f"[dependencies] {total_issues} package(s) need updating. Run 'pip install -e .[dev]' to fix.")
        return

    try:
        response = click.prompt(
            "Do you want to install/update these packages now?",
            type=click.Choice(["y", "n"], case_sensitive=False),
            default="y",
            show_choices=True,
        )
    except (click.Abort, EOFError):
        click.echo("\n[dependencies] Install skipped")
        return

    if response.lower() == "y":
        click.echo("\n[dependencies] Installing/updating packages...")
        install_cmd = [sys.executable, "-m", "pip", "install", "-e", ".[dev]"]
        if sys.platform.startswith("linux"):
            install_cmd.insert(4, "--break-system-packages")
        result = run(install_cmd, check=False, capture=False)
        if result.code == 0:
            click.echo("[dependencies] Packages installed successfully!")
        else:
            click.echo(f"[dependencies] Package installation failed (exit code {result.code})", err=True)
    else:
        click.echo("[dependencies] Install skipped. Run 'pip install -e .[dev]' to update packages.")


def _check_installed_dependencies() -> None:
    """Check if dependencies are installed at the versions specified in pyproject.toml.

    Orchestrates discovery, display, and interactive installation by
    delegating to ``_find_dependency_issues``,
    ``_display_dependency_issues``, and
    ``_prompt_and_install_dependencies``.
    """
    click.echo("\n[dependencies] Checking installed packages against pyproject.toml requirements...")

    try:
        deps = dependencies_module.check_dependencies()
    except Exception as exc:
        click.echo(f"[dependencies] Failed to check dependencies: {exc}", err=True)
        return

    missing, outdated_installed = _find_dependency_issues(deps)

    if not missing and not outdated_installed:
        click.echo("[dependencies] All required packages are installed at correct versions!")
        return

    _display_dependency_issues(missing, outdated_installed)

    total_issues = len(missing) + len(outdated_installed)
    click.echo("")

    _prompt_and_install_dependencies(total_issues)


def push(*, remote: str = _DEFAULT_REMOTE, message: str | None = None) -> None:
    """Run checks, commit changes, and push the current branch."""
    # Step 0: Ensure pip is up-to-date
    _check_and_update_pip()

    # Step 1: Check pyproject.toml dependencies against PyPI
    _check_dependencies_and_prompt_update()

    # Step 2: Check installed packages meet requirements
    _check_installed_dependencies()

    metadata = get_project_metadata()
    sync_metadata_module(metadata)
    version = read_version_from_pyproject(Path("pyproject.toml")) or "unknown"
    click.echo("[push] project diagnostics: " + ", ".join(metadata.diagnostic_lines()))
    click.echo(f"[push] version={version}")
    branch = git_branch()
    click.echo(f"[push] branch={branch} remote={remote}")

    click.echo("[push] Running local checks (python -m scripts.test)")
    run(["python", "-m", "scripts.test"], capture=False)

    click.echo("[push] Committing and pushing (single attempt)")
    run(["git", "add", "-A"], capture=False)  # stage all
    staged = run(["git", "diff", "--cached", "--quiet"], check=False, capture=True)
    user_message = _resolve_commit_message(message)
    commit_message = f"{version} - {user_message}"
    if staged.code == 0:
        click.echo("[push] No staged changes detected; creating empty commit")
    run(["git", "commit", "--allow-empty", "-m", commit_message], capture=False)  # type: ignore[list-item]
    click.echo(f"[push] Commit message: {commit_message}")
    run(["git", "push", "-u", remote, branch], capture=False)  # type: ignore[list-item]


_DEFAULT_MESSAGE = "chores"


def _resolve_commit_message(message: str | None) -> str:
    """Return the user-facing part of the commit message.

    Resolution order:
    1. Explicit *message* argument (from CLI positional args)
    2. ``COMMIT_MESSAGE`` environment variable
    3. Default: ``"chores"``
    """
    if message is not None:
        return message.strip() or _DEFAULT_MESSAGE

    env_message = os.environ.get("COMMIT_MESSAGE")
    if env_message is not None:
        final = env_message.strip() or _DEFAULT_MESSAGE
        click.echo(f"[push] Using commit message from COMMIT_MESSAGE: {final}")
        return final

    return _DEFAULT_MESSAGE


if __name__ == "__main__":  # pragma: no cover
    from .cli import main as cli_main

    cli_main(["push", *sys.argv[1:]])
