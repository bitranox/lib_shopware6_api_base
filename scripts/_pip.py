"""Pip and development-environment bootstrap helpers.

Purpose
-------
Automate the initial ``pip install -e .[dev]`` dance and guard against common
CI pitfalls (SHA-256 hash-check errors on pre-installed pip wheels, missing
``sqlite3`` on minimal container images).

Contents
--------
* ``bootstrap_dev`` -- top-level entry point called by ``scripts/dev.py``.
* ``_needs_dev_install`` -- heuristic: do dev tools already exist?
* ``_upgrade_pip`` -- upgrade pip with CI-safe error handling.
* ``_is_ci_sha_error`` / ``_print_pip_error`` -- error-classification helpers.
* ``_install_dev_dependencies`` -- ``pip install -e .[dev]``.
* ``_ensure_sqlite3`` -- install ``pysqlite3-binary`` when the stdlib
  ``sqlite3`` module is missing.

System Role
-----------
Infrastructure layer within ``scripts/``.  Depends on ``_subprocess`` for
command execution but never on metadata or git helpers.
"""

from __future__ import annotations

import os
import sys

from ._subprocess import RunResult, cmd_exists, run

__all__ = [
    "bootstrap_dev",
]


def bootstrap_dev() -> None:
    """Bootstrap development environment with required tools."""
    _upgrade_pip()
    if _needs_dev_install():
        _install_dev_dependencies()
    _ensure_sqlite3()


def _needs_dev_install() -> bool:
    """Check if dev dependencies need to be installed."""
    if not (cmd_exists("ruff") and cmd_exists("pyright")):
        return True
    try:
        from importlib import import_module

        import_module("pytest_asyncio")
        return False
    except ModuleNotFoundError:
        return True


def _upgrade_pip() -> None:
    """Upgrade pip, handling CI-specific errors."""
    pip_upgrade = run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        check=False,
        capture=True,
    )
    if pip_upgrade.code == 0:
        return

    if _is_ci_sha_error(pip_upgrade):
        print("[bootstrap] pip upgrade failed due to SHA256 verification; continuing on CI")
        return

    _print_pip_error(pip_upgrade)
    raise SystemExit("pip upgrade failed; see output above")


def _is_ci_sha_error(result: RunResult) -> bool:
    """Check if pip upgrade failed due to SHA256 verification on CI."""
    combined_output = f"{result.out}\n{result.err}".lower()
    ci_token = os.getenv("CI", "").strip().lower()
    is_ci = ci_token in {"1", "true", "yes"}
    sha_error = "sha256" in combined_output and "hash" in combined_output
    return is_ci and sha_error


def _print_pip_error(result: RunResult) -> None:
    """Print pip upgrade error output."""
    if result.out:
        print(result.out, end="")
    if result.err:
        print(result.err, end="", file=sys.stderr)


def _install_dev_dependencies() -> None:
    """Install dev dependencies with pip."""
    print("[bootstrap] Installing dev dependencies via 'pip install -e .[dev]'")
    install_cmd = [sys.executable, "-m", "pip", "install", "-e", ".[dev]"]
    if sys.platform.startswith("linux"):
        install_cmd.insert(4, "--break-system-packages")
    run(install_cmd)


def _ensure_sqlite3() -> None:
    """Ensure sqlite3 is available, installing pysqlite3-binary if needed."""
    try:
        from importlib import import_module

        import_module("sqlite3")
    except Exception:
        sqlite_cmd = [sys.executable, "-m", "pip", "install", "pysqlite3-binary"]
        if sys.platform.startswith("linux"):
            sqlite_cmd.insert(4, "--break-system-packages")
        run(sqlite_cmd, check=False)
