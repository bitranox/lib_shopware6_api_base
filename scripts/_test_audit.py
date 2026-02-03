"""Pip-audit data structures and guarded execution helpers.

Purpose
-------
Encapsulate everything related to running ``pip-audit``, parsing its JSON
output into typed dataclasses, and deciding whether unexpected vulnerabilities
should fail the build.

Contents
--------
* ``AuditVulnerability`` / ``AuditDependency`` / ``AuditResult`` -- immutable
  dataclasses that mirror the pip-audit JSON schema.
* ``_resolve_pip_audit_ignores`` -- consolidates configured and env-var ignore
  lists.
* ``_run_pip_audit_guarded`` -- runs pip-audit twice (human-readable + JSON),
  then reports only genuinely unexpected findings.

System Role
-----------
Called from the test orchestrator (``test.py``) as a sequential post-step.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

import click
import orjson

if TYPE_CHECKING:
    from ._utils import RunResult

__all__ = [
    "AuditVulnerability",
    "AuditDependency",
    "AuditResult",
    "resolve_pip_audit_ignores",
    "run_pip_audit_guarded",
]


# ---------------------------------------------------------------------------
# Pip-Audit Data Structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AuditVulnerability:
    """A single vulnerability from pip-audit output."""

    vuln_id: str
    fix_versions: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> AuditVulnerability:
        """Parse a vulnerability entry from pip-audit JSON."""
        vuln_id = data.get("id")
        if not isinstance(vuln_id, str):
            vuln_id = "<unknown>"

        fix_versions: tuple[str, ...] = ()
        raw_fix = data.get("fix_versions")
        if isinstance(raw_fix, list):
            typed_fix = cast(list[object], raw_fix)
            fix_versions = tuple(str(v) for v in typed_fix if v is not None)

        aliases: tuple[str, ...] = ()
        raw_aliases = data.get("aliases")
        if isinstance(raw_aliases, list):
            typed_aliases = cast(list[object], raw_aliases)
            aliases = tuple(str(a) for a in typed_aliases if a is not None)

        description = data.get("description", "")
        if not isinstance(description, str):
            description = ""

        return cls(
            vuln_id=vuln_id,
            fix_versions=fix_versions,
            aliases=aliases,
            description=description,
        )


@dataclass(frozen=True)
class AuditDependency:
    """A dependency entry from pip-audit output."""

    name: str
    version: str = ""
    vulns: tuple[AuditVulnerability, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> AuditDependency:
        """Parse a dependency entry from pip-audit JSON."""
        name = data.get("name")
        if not isinstance(name, str):
            name = "<unknown>"

        version = data.get("version", "")
        if not isinstance(version, str):
            version = ""

        vulns: tuple[AuditVulnerability, ...] = ()
        raw_vulns = data.get("vulns")
        if isinstance(raw_vulns, list):
            typed_vulns = cast(list[object], raw_vulns)
            vulns = tuple(
                AuditVulnerability.from_dict(cast(dict[str, object], entry))
                for entry in typed_vulns
                if isinstance(entry, dict)
            )

        return cls(name=name, version=version, vulns=vulns)

    def vuln_ids(self) -> tuple[str, ...]:
        """Return all vulnerability IDs for this dependency."""
        return tuple(v.vuln_id for v in self.vulns)


@dataclass(frozen=True)
class AuditResult:
    """Parsed pip-audit JSON output."""

    dependencies: tuple[AuditDependency, ...] = ()

    @classmethod
    def from_json(cls, json_output: str) -> AuditResult:
        """Parse pip-audit JSON output into structured data."""
        try:
            payload: object = orjson.loads(json_output or "{}")
        except orjson.JSONDecodeError:
            return cls()

        if not isinstance(payload, dict):
            return cls()

        typed_payload = cast(dict[str, object], payload)
        raw_deps = typed_payload.get("dependencies")
        if not isinstance(raw_deps, list):
            return cls()

        typed_deps = cast(list[object], raw_deps)
        return cls(
            dependencies=tuple(
                AuditDependency.from_dict(cast(dict[str, object], entry))
                for entry in typed_deps
                if isinstance(entry, dict)
            )
        )

    def find_unexpected_vulns(self, ignore_ids: set[str]) -> list[str]:
        """Find vulnerabilities not in the ignore set."""
        return [
            f"{dep.name}: {vuln_id}"
            for dep in self.dependencies
            for vuln_id in dep.vuln_ids()
            if vuln_id not in ignore_ids
        ]


# ---------------------------------------------------------------------------
# Pip-Audit Execution
# ---------------------------------------------------------------------------


def resolve_pip_audit_ignores(pip_audit_ignores: tuple[str, ...]) -> list[str]:
    """Return consolidated list of vulnerability IDs to ignore during pip-audit."""
    extra = [token.strip() for token in os.getenv("PIP_AUDIT_IGNORE", "").split(",") if token.strip()]
    ignores: list[str] = []
    for candidate in (*pip_audit_ignores, *extra):
        if candidate and candidate not in ignores:
            ignores.append(candidate)
    return ignores


def run_pip_audit_guarded(pip_audit_ignores: tuple[str, ...], run_fn: Callable[..., RunResult]) -> None:
    """Run pip-audit with configured ignore list and verify results."""
    ignore_ids = resolve_pip_audit_ignores(pip_audit_ignores)
    _run_pip_audit_with_ignores(run_fn, ignore_ids)
    result = _run_pip_audit_json(run_fn)

    if result.code == 0:
        return

    audit_result = AuditResult.from_json(result.out)
    unexpected = audit_result.find_unexpected_vulns(set(ignore_ids))
    _report_unexpected_vulns(unexpected)


def _run_pip_audit_with_ignores(run_fn: Callable[..., RunResult], ignore_ids: list[str]) -> None:
    """Run pip-audit with the configured ignore list."""
    audit_cmd: list[str] = ["pip-audit", "--skip-editable"]
    for vuln_id in ignore_ids:
        audit_cmd.extend(["--ignore-vuln", vuln_id])
    run_fn(audit_cmd, label="pip-audit-ignore", capture=False)


def _run_pip_audit_json(run_fn: Callable[..., RunResult]) -> RunResult:
    """Run pip-audit in JSON mode for verification."""
    return run_fn(
        ["pip-audit", "--skip-editable", "--format", "json"],
        label="pip-audit-verify",
        capture=True,
        check=False,
    )


def _report_unexpected_vulns(unexpected: list[str]) -> None:
    """Report unexpected vulnerabilities and exit if any found."""
    if not unexpected:
        return
    click.echo("pip-audit reported new vulnerabilities:", err=True)
    for entry in unexpected:
        click.echo(f"  - {entry}", err=True)
    raise SystemExit("Resolve the reported vulnerabilities before continuing.")
