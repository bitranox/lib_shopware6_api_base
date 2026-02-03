"""Re-export facade for shared automation utilities.

Purpose
-------
Maintain backward compatibility for all existing ``from scripts._utils import X``
statements while the actual implementations live in focused sub-modules.

Contents
--------
This module re-exports every public symbol from:

* ``_subprocess`` -- ``RunResult``, ``run``, ``cmd_exists``
* ``_metadata``   -- ``ProjectMetadata``, ``get_project_metadata``,
  ``sync_metadata_module``, ``read_version_from_pyproject``
* ``_git``        -- git/gh helpers (``ensure_clean_git_tree``,
  ``git_branch``, ``git_push``, tag and release functions,
  ``get_default_remote``)
* ``_pip``        -- ``bootstrap_dev``

System Role
-----------
Thin facade only.  No logic lives here; add new functionality to the
appropriate sub-module instead.
"""

from __future__ import annotations

# --- git / GitHub helpers -----------------------------------------------------
from ._git import (
    ensure_clean_git_tree,
    get_default_remote,
    gh_available,
    gh_release_create,
    gh_release_edit,
    gh_release_exists,
    git_branch,
    git_create_annotated_tag,
    git_delete_tag,
    git_push,
    git_tag_exists,
)

# --- project metadata --------------------------------------------------------
from ._metadata import (
    ProjectMetadata,
    get_dependencies,
    get_project_metadata,
    read_version_from_pyproject,
    sync_metadata_module,
)

# --- pip / dev bootstrap ------------------------------------------------------
from ._pip import bootstrap_dev

# --- subprocess primitives ---------------------------------------------------
from ._subprocess import RunResult, cmd_exists, run

__all__ = [
    # _subprocess
    "RunResult",
    "run",
    "cmd_exists",
    # _metadata
    "ProjectMetadata",
    "get_dependencies",
    "get_project_metadata",
    "read_version_from_pyproject",
    "sync_metadata_module",
    # _git
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
    # _pip
    "bootstrap_dev",
]
