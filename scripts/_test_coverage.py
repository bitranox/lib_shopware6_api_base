"""Coverage file management and Codecov upload helpers.

Purpose
-------
Isolate everything related to cleaning coverage artefacts, resolving git
metadata for Codecov, and uploading coverage reports so the test
orchestrator stays slim.

Contents
--------
* ``prune_coverage_data_files`` / ``remove_report_artifacts`` -- housekeeping
  before and after coverage runs.
* ``ensure_codecov_token`` -- loads ``CODECOV_TOKEN`` from ``.env`` when the
  environment variable is not already set.
* ``upload_coverage_report`` -- drives the official Codecov CLI uploader.
* Git resolution helpers (commit SHA, branch, service).

System Role
-----------
Called from the test orchestrator (``test.py``) after pytest completes.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from ._utils import ProjectMetadata, RunResult

__all__ = [
    "prune_coverage_data_files",
    "remove_report_artifacts",
    "ensure_codecov_token",
    "upload_coverage_report",
]


# ---------------------------------------------------------------------------
# Coverage File Management
# ---------------------------------------------------------------------------


def prune_coverage_data_files() -> None:
    """Delete SQLite coverage data shards to keep the Codecov CLI simple."""
    for path in Path.cwd().glob(".coverage*"):
        if path.is_dir() or path.suffix == ".xml":
            continue
        try:
            path.unlink()
        except FileNotFoundError:
            continue
        except OSError as exc:
            click.echo(f"[coverage] warning: unable to remove {path}: {exc}", err=True)


def remove_report_artifacts(coverage_report_file: str = "coverage.xml") -> None:
    """Remove coverage reports that might lock the SQLite database on reruns."""
    for name in (coverage_report_file, "codecov.xml"):
        artifact = Path(name)
        try:
            artifact.unlink()
        except FileNotFoundError:
            continue
        except OSError as exc:
            click.echo(f"[coverage] warning: unable to remove {artifact}: {exc}", err=True)


# ---------------------------------------------------------------------------
# Codecov Token Management
# ---------------------------------------------------------------------------


def ensure_codecov_token() -> bool:
    """Load CODECOV_TOKEN from .env file if not already set.

    Returns True if the token was loaded or was already present, meaning the
    caller should rebuild its environment dict to pick up the change.
    """
    if os.getenv("CODECOV_TOKEN"):
        return True
    env_path = Path(".env")
    if not env_path.is_file():
        return False
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        if key.strip() == "CODECOV_TOKEN":
            token = value.strip().strip("\"'")
            if token:
                os.environ.setdefault("CODECOV_TOKEN", token)
                return True
            break
    return False


# ---------------------------------------------------------------------------
# Git Utilities
# ---------------------------------------------------------------------------


def _resolve_commit_sha() -> str | None:
    """Resolve the current git commit SHA from environment or git."""
    sha = os.getenv("GITHUB_SHA")
    if sha:
        return sha.strip()
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    candidate = proc.stdout.strip()
    return candidate or None


def _resolve_git_branch() -> str | None:
    """Resolve the current git branch from environment or git."""
    branch = os.getenv("GITHUB_REF_NAME")
    if branch:
        return branch.strip()
    proc = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    candidate = proc.stdout.strip()
    if candidate in {"", "HEAD"}:
        return None
    return candidate


def _resolve_git_service(project: ProjectMetadata) -> str | None:
    """Map repository host to Codecov git service identifier."""
    host = (project.repo_host or "").lower()
    mapping = {
        "github.com": "github",
        "gitlab.com": "gitlab",
        "bitbucket.org": "bitbucket",
    }
    return mapping.get(host)


def _get_repo_slug(project: ProjectMetadata) -> str | None:
    """Get the repository slug (owner/name) if available."""
    if project.repo_owner and project.repo_name:
        return f"{project.repo_owner}/{project.repo_name}"
    return None


# ---------------------------------------------------------------------------
# Codecov Upload
# ---------------------------------------------------------------------------


def upload_coverage_report(
    *,
    project: ProjectMetadata,
    run_fn: Callable[..., RunResult],
    coverage_report_file: str = "coverage.xml",
) -> bool:
    """Upload coverage report via the official Codecov CLI when available."""
    uploader = _check_codecov_prerequisites(coverage_report_file)
    if uploader is None:
        return False

    commit_sha = _resolve_commit_sha()
    if commit_sha is None:
        click.echo("[codecov] Unable to resolve git commit; skipping upload", err=True)
        return False

    args = _build_codecov_args(project, uploader, commit_sha, coverage_report_file)
    env_overrides = _build_codecov_env(project)

    result = run_fn(args, env=env_overrides, check=False, capture=False, label="codecov-upload")
    return _handle_codecov_result(result)


def _check_codecov_prerequisites(coverage_report_file: str = "coverage.xml") -> str | None:
    """Check prerequisites for codecov upload, return uploader path or None."""
    if not Path(coverage_report_file).is_file():
        return None

    if not os.getenv("CODECOV_TOKEN") and not os.getenv("CI"):
        click.echo("[codecov] CODECOV_TOKEN not configured; skipping upload (set CODECOV_TOKEN or run in CI)")
        return None

    uploader = shutil.which("codecovcli")
    if uploader is None:
        click.echo(
            "[codecov] 'codecovcli' not found; install with 'pip install codecov-cli' to enable uploads",
            err=True,
        )
        return None

    return uploader


def _build_codecov_args(
    project: ProjectMetadata,
    uploader: str,
    commit_sha: str,
    coverage_report_file: str = "coverage.xml",
) -> list[str]:
    """Build the codecov CLI arguments."""
    args = [
        uploader,
        "upload-coverage",
        "--file",
        coverage_report_file,
        "--disable-search",
        "--fail-on-error",
        "--sha",
        commit_sha,
        "--name",
        f"local-{platform.system()}-{platform.python_version()}",
        "--flag",
        "local",
    ]

    branch = _resolve_git_branch()
    if branch:
        args.extend(["--branch", branch])

    git_service = _resolve_git_service(project)
    if git_service:
        args.extend(["--git-service", git_service])

    slug = _get_repo_slug(project)
    if slug:
        args.extend(["--slug", slug])

    return args


def _build_codecov_env(project: ProjectMetadata) -> dict[str, str]:
    """Build environment overrides for codecov upload."""
    env_overrides: dict[str, str] = {"CODECOV_NO_COMBINE": "1"}
    slug = _get_repo_slug(project)
    if slug:
        env_overrides["CODECOV_SLUG"] = slug
    return env_overrides


def _handle_codecov_result(result: RunResult) -> bool:
    """Handle the codecov upload result."""
    if result.code == 0:
        click.echo("[codecov] upload succeeded")
        return True
    click.echo(f"[codecov] upload failed (exit {result.code})", err=True)
    return False
