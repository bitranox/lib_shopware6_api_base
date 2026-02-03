"""Subprocess wrapper utilities for project scripts.

Purpose
-------
Provide a structured subprocess execution helper and command-existence check
so that all script modules share the same error-handling and dry-run semantics.

Contents
--------
* ``RunResult`` -- dataclass capturing exit code, stdout and stderr.
* ``run`` -- execute a command, optionally capturing output and enforcing
  exit-code checks.
* ``cmd_exists`` -- test whether a named executable is on ``$PATH``.

System Role
-----------
Lowest-level building block in the ``scripts/`` package.  Other script helpers
(``_git``, ``_pip``, ``_metadata``) depend on these primitives but never the
reverse.
"""

from __future__ import annotations

import shlex
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from subprocess import CompletedProcess

__all__ = [
    "RunResult",
    "run",
    "cmd_exists",
]


@dataclass
class RunResult:
    """Result of a subprocess execution.

    Attributes:
        code: Exit code from the process
        out: Captured stdout content
        err: Captured stderr content
    """

    code: int
    out: str
    err: str


def run(
    cmd: Sequence[str] | str,
    *,
    check: bool = True,
    capture: bool = True,
    cwd: str | None = None,
    env: Mapping[str, str] | None = None,
    dry_run: bool = False,
) -> RunResult:
    if isinstance(cmd, str):
        display = cmd
        shell = True
        args: Sequence[str] | str = cmd
    else:
        display = " ".join(shlex.quote(p) for p in cmd)
        shell = False
        args = list(cmd)
    if dry_run:
        print(f"[dry-run] {display}")
        return RunResult(0, "", "")
    proc: CompletedProcess[str] = subprocess.run(
        args,
        shell=shell,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=capture,
        check=False,
    )
    if check and proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return RunResult(int(proc.returncode or 0), proc.stdout or "", proc.stderr or "")


def cmd_exists(name: str) -> bool:
    """Check if a command exists in the system PATH."""
    return shutil.which(name) is not None
