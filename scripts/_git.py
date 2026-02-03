"""Git and GitHub CLI helpers for project scripts.

Purpose
-------
Wrap common ``git`` and ``gh`` operations used during release, push and
CI/CD automation so callers do not duplicate subprocess invocations.

Contents
--------
* Tree-cleanliness guard (``ensure_clean_git_tree``).
* Tag operations (``git_tag_exists``, ``git_create_annotated_tag``,
  ``git_delete_tag``).
* Push / branch helpers (``git_push``, ``git_branch``).
* GitHub release wrappers (``gh_available``, ``gh_release_exists``,
  ``gh_release_create``, ``gh_release_edit``).
* Remote configuration reader (``get_default_remote``).

System Role
-----------
Infrastructure layer within ``scripts/``.  Depends on ``_subprocess`` for
command execution and ``_metadata`` for pyproject reading, but never on
higher-level orchestrators like ``release.py`` or ``push.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

from ._metadata import as_str_mapping, load_pyproject
from ._subprocess import cmd_exists, run

__all__ = [
    "ensure_clean_git_tree",
    "git_branch",
    "git_delete_tag",
    "git_tag_exists",
    "git_create_annotated_tag",
    "git_push",
    "gh_available",
    "gh_release_exists",
    "gh_release_create",
    "gh_release_edit",
    "get_default_remote",
]


def ensure_clean_git_tree() -> None:
    """Ensure the git working tree has no uncommitted changes."""
    unstaged = run(["git", "diff", "--quiet"], check=False, capture=True)
    staged = run(["git", "diff", "--cached", "--quiet"], check=False, capture=True)
    if unstaged.code != 0 or staged.code != 0:
        print("[release] Working tree not clean. Commit or stash changes first.", file=sys.stderr)
        raise SystemExit(1)


def git_branch() -> str:
    """Get the current git branch name."""
    return run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture=True).out.strip()


def git_delete_tag(name: str, *, remote: str | None = None) -> None:
    """Delete a git tag locally and optionally from remote."""
    run(["git", "tag", "-d", name], check=False, capture=True)
    if remote:
        run(["git", "push", remote, f":refs/tags/{name}"], check=False)


def git_tag_exists(name: str) -> bool:
    """Check if a git tag exists locally."""
    return run(["git", "rev-parse", "-q", "--verify", f"refs/tags/{name}"], check=False, capture=True).code == 0


def git_create_annotated_tag(name: str, message: str) -> None:
    """Create an annotated git tag."""
    run(["git", "tag", "-a", name, "-m", message])


def git_push(remote: str, ref: str) -> None:
    """Push a ref to a remote repository."""
    run(["git", "push", remote, ref])


def gh_available() -> bool:
    """Check if the GitHub CLI (gh) is available."""
    return cmd_exists("gh")


def gh_release_exists(tag: str) -> bool:
    """Check if a GitHub release exists for the given tag."""
    return run(["gh", "release", "view", tag], check=False, capture=True).code == 0


def gh_release_create(tag: str, title: str, body: str) -> None:
    """Create a new GitHub release."""
    run(["gh", "release", "create", tag, "-t", title, "-n", body], check=False)


def gh_release_edit(tag: str, title: str, body: str) -> None:
    """Edit an existing GitHub release."""
    run(["gh", "release", "edit", tag, "-t", title, "-n", body], check=False)


def get_default_remote(pyproject: Path = Path("pyproject.toml")) -> str:
    """Read default git remote from pyproject.toml [tool.git].default-remote.

    Args:
        pyproject: Path to pyproject.toml file

    Returns:
        The configured default remote, or "origin" if not configured.
    """
    try:
        data = load_pyproject(pyproject)
        tool = as_str_mapping(data.get("tool"))
        git_config = as_str_mapping(tool.get("git"))
        remote = git_config.get("default-remote")
        if isinstance(remote, str) and remote.strip():
            return remote.strip()
    except (ValueError, OSError):
        pass
    return "origin"
