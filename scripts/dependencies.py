"""Check pyproject.toml dependencies against latest PyPI versions.

Purpose
-------
Scan all dependency specifications in ``pyproject.toml`` and compare them
against the latest available versions on PyPI. This helps keep dependencies
up-to-date and identifies potential upgrades.

Contents
--------
* ``DependencyInfo`` – captures a dependency's current constraint and latest version.
* ``check_dependencies`` – main entry point that checks all dependencies.
* ``print_report`` – renders a formatted report of dependency status.
* ``update_dependencies`` – updates outdated dependencies to latest versions.

System Role
-----------
Development automation helper that sits alongside other scripts. It queries
PyPI via its JSON API to retrieve latest package versions without requiring
additional dependencies.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import httpx
import orjson

from .toml_config import PyprojectConfig, load_pyproject_config

__all__ = [
    "DependencyInfo",
    "check_dependencies",
    "compare_versions",
    "fetch_latest_version",
    "print_report",
    "update_dependencies",
]

# Precompiled regex patterns for version parsing and dependency matching
_RE_NAME_SEPARATOR = re.compile(r"[-_.]+")
_RE_VERSION_SPEC = re.compile(r"^([a-zA-Z0-9_.-]+)\s*((?:[><=!~]+\s*[\d.a-zA-Z*]+\s*,?\s*)+)?$")
_RE_MIN_VERSION = re.compile(r"[>=~]=?\s*([\d.]+(?:a\d+|b\d+|rc\d+)?)")
_RE_UPPER_BOUND = re.compile(r"<(?!=)\s*([\d.]+(?:a\d+|b\d+|rc\d+)?)")
_RE_PRERELEASE = re.compile(r"(a|b|rc|dev|alpha|beta)", re.IGNORECASE)
_RE_VERSION_NUMERIC = re.compile(r"^([\d.]+)")
_RE_VERSION_CONSTRAINT = re.compile(r"([><=!~]+)\s*([\d.]+(?:a\d+|b\d+|rc\d+)?)")
_RE_HAS_CONSTRAINT = re.compile(r"[><=!~]")
_RE_PACKAGE_NAME = re.compile(r"^([a-zA-Z0-9_.-]+)")


@dataclass
class DependencyInfo:
    """Information about a single dependency."""

    name: str
    source: str
    constraint: str
    current_min: str
    latest: str
    status: str  # "up-to-date", "outdated", "pinned", "unknown", "error"
    original_spec: str = ""  # Original dependency specification string
    upper_bound: str = ""  # Upper version bound if specified (e.g., "<9" means "9")


def _normalize_name(name: str) -> str:
    """Normalize package name for comparison (PEP 503)."""
    return _RE_NAME_SEPARATOR.sub("-", name).lower()


def _parse_version_constraint(spec: str) -> tuple[str, str, str, str]:
    """Parse a dependency spec into (name, constraint, minimum_version, upper_bound).

    Examples:
        "rich-click>=1.9.4" -> ("rich-click", ">=1.9.4", "1.9.4", "")
        "tomli>=2.0.0; python_version<'3.11'" -> ("tomli", ">=2.0.0", "2.0.0", "")
        "pytest>=8.4.2,<9" -> ("pytest", ">=8.4.2,<9", "8.4.2", "9")
        "hatchling>=1.27.0" -> ("hatchling", ">=1.27.0", "1.27.0", "")
    """
    spec = spec.strip()
    if not spec:
        return "", "", "", ""

    # Remove environment markers (e.g., "; python_version<'3.11'")
    marker_idx = spec.find(";")
    if marker_idx != -1:
        spec = spec[:marker_idx].strip()

    # Handle extras in brackets (e.g., "package[extra]>=1.0")
    bracket_idx = spec.find("[")
    if bracket_idx != -1:
        close_bracket = spec.find("]", bracket_idx)
        if close_bracket != -1:
            spec = spec[:bracket_idx] + spec[close_bracket + 1 :]

    # Extract version constraint
    # Patterns: >=, <=, ==, !=, ~=, >, <
    match = _RE_VERSION_SPEC.match(spec)
    if not match:
        # Fallback: just return the spec as name
        return spec, "", "", ""

    name = match.group(1).strip()
    constraint = match.group(2).strip() if match.group(2) else ""

    # Extract minimum version from constraint
    min_version = ""
    upper_bound = ""
    if constraint:
        # Look for >= or == patterns to find minimum version
        version_match = _RE_MIN_VERSION.search(constraint)
        if version_match:
            min_version = version_match.group(1)

        # Look for < or <= patterns to find upper bound (but not !=)
        upper_match = _RE_UPPER_BOUND.search(constraint)
        if upper_match:
            upper_bound = upper_match.group(1)

    return name, constraint, min_version, upper_bound


def _fetch_pypi_data(package_name: str) -> dict[str, Any] | None:
    """Fetch package data from PyPI."""
    normalized = _normalize_name(package_name)
    url = f"https://pypi.org/pypi/{normalized}/json"

    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        return orjson.loads(response.content)  # type: ignore[no-any-return]
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return None
        return None
    except (httpx.ConnectError, httpx.TimeoutException, orjson.JSONDecodeError):
        return None


def fetch_latest_version(package_name: str) -> str | None:
    """Fetch the latest version of a package from PyPI."""
    data = _fetch_pypi_data(package_name)
    if data is None:
        return None
    info = data.get("info")
    if isinstance(info, dict):
        typed_info = cast(dict[str, Any], info)
        version = typed_info.get("version", "")
        return str(version) if version else ""
    return ""


def _fetch_latest_version_below(package_name: str, upper_bound: str) -> str | None:
    """Fetch the latest version of a package that is below the upper bound.

    Args:
        package_name: Name of the package
        upper_bound: Upper version bound (exclusive), e.g., "9" for "<9"

    Returns:
        Latest version string below the bound, or None if not found
    """
    data = _fetch_pypi_data(package_name)
    if data is None:
        return None

    releases = data.get("releases")
    if not isinstance(releases, dict) or not releases:
        return None

    typed_releases = cast(dict[str, Any], releases)

    # Get all version strings and filter to those below upper_bound
    valid_versions: list[tuple[tuple[int, ...], str]] = []
    for version_str in typed_releases:
        # Skip pre-release versions (containing a, b, rc, dev, etc.)
        if _RE_PRERELEASE.search(version_str):
            continue

        version_tuple = _parse_version_tuple(version_str)
        if not version_tuple:
            continue

        # Check if version is below upper_bound
        if not _version_gte(version_str, upper_bound):
            valid_versions.append((version_tuple, version_str))

    if not valid_versions:
        return None

    # Sort by version tuple (descending) and return the highest
    valid_versions.sort(reverse=True, key=lambda x: x[0])
    return valid_versions[0][1]


def _parse_version_tuple(v: str) -> tuple[int, ...]:
    """Parse version string into a tuple of integers for comparison."""
    match = _RE_VERSION_NUMERIC.match(v)
    if not match:
        return ()
    numeric = match.group(1)
    return tuple(int(p) for p in numeric.split(".") if p.isdigit())


def _version_gte(version_a: str, version_b: str) -> bool:
    """Check if version_a >= version_b."""
    a_parts = _parse_version_tuple(version_a)
    b_parts = _parse_version_tuple(version_b)

    # Pad to same length
    max_len = max(len(a_parts), len(b_parts))
    a_padded = a_parts + (0,) * (max_len - len(a_parts))
    b_padded = b_parts + (0,) * (max_len - len(b_parts))

    return a_padded >= b_padded


def compare_versions(current: str, latest: str) -> str:
    """Compare two version strings and return status."""
    if not current or not latest:
        return "unknown"

    current_parts = _parse_version_tuple(current)
    latest_parts = _parse_version_tuple(latest)

    # Pad to same length for comparison
    max_len = max(len(current_parts), len(latest_parts))
    current_padded = current_parts + (0,) * (max_len - len(current_parts))
    latest_padded = latest_parts + (0,) * (max_len - len(latest_parts))

    if current_padded >= latest_padded:
        return "up-to-date"
    return "outdated"


def _extract_dependencies_from_list(
    deps: tuple[str, ...] | list[str],
    source: str,
) -> list[DependencyInfo]:
    """Extract dependency info from a list of requirement strings."""
    results: list[DependencyInfo] = []

    for dep in deps:
        if not dep:
            continue

        original_spec = dep.strip()
        name, constraint, min_version, upper_bound = _parse_version_constraint(dep)
        if not name:
            continue

        # Fetch latest version (respecting upper bound if present)
        latest_absolute = fetch_latest_version(name)
        if latest_absolute is None:
            status = "error"
            latest_str = "not found"
        elif not min_version:
            status = "unknown"
            latest_str = latest_absolute
        elif upper_bound and _version_gte(latest_absolute, upper_bound):
            # Latest version exceeds our upper bound - check for updates within range
            latest_in_range = _fetch_latest_version_below(name, upper_bound)
            if latest_in_range is None:
                status = "pinned"
                latest_str = f"{latest_absolute} (pinned <{upper_bound})"
            elif _version_gte(min_version, latest_in_range):
                # We're at the latest version within the allowed range
                status = "pinned"
                latest_str = f"{latest_absolute} (pinned <{upper_bound})"
            else:
                # There's a newer version within the allowed range
                status = "outdated"
                latest_str = f"{latest_in_range} (max <{upper_bound}, absolute: {latest_absolute})"
        else:
            # No upper bound constraint or latest is within range
            status = compare_versions(min_version, latest_absolute)
            latest_str = latest_absolute

        results.append(
            DependencyInfo(
                name=name,
                source=source,
                constraint=constraint,
                current_min=min_version,
                latest=latest_str,
                status=status,
                original_spec=original_spec,
                upper_bound=upper_bound,
            )
        )

    return results


def _extract_all_dependencies(config: PyprojectConfig) -> list[DependencyInfo]:
    """Extract all dependencies from PyprojectConfig."""
    all_deps: list[DependencyInfo] = []

    # 1. [project].dependencies
    if config.project.dependencies:
        all_deps.extend(_extract_dependencies_from_list(config.project.dependencies, "[project].dependencies"))

    # 2. [project.optional-dependencies]
    for group_name, group_deps in config.project.optional_dependencies.items():
        source = f"[project.optional-dependencies].{group_name}"
        all_deps.extend(_extract_dependencies_from_list(group_deps, source))

    # 3. [build-system].requires
    if config.build_system.requires:
        all_deps.extend(_extract_dependencies_from_list(config.build_system.requires, "[build-system].requires"))

    # 4. [dependency-groups] (PEP 735)
    for group_name, group_deps in config.dependency_groups.groups.items():
        source = f"[dependency-groups].{group_name}"
        all_deps.extend(_extract_dependencies_from_list(group_deps, source))

    # 5. [tool.pdm.dev-dependencies]
    for group_name, group_deps in config.tool.pdm.dev_dependencies.items():
        source = f"[tool.pdm.dev-dependencies].{group_name}"
        all_deps.extend(_extract_dependencies_from_list(group_deps, source))

    # 6. [tool.poetry.dependencies]
    if config.tool.poetry.dependencies:
        poetry_deps = [dep.to_requirement_string() for dep in config.tool.poetry.dependencies]
        all_deps.extend(_extract_dependencies_from_list(poetry_deps, "[tool.poetry.dependencies]"))

    # 7. [tool.poetry.dev-dependencies]
    if config.tool.poetry.dev_dependencies:
        poetry_dev_deps = [dep.to_requirement_string() for dep in config.tool.poetry.dev_dependencies]
        all_deps.extend(_extract_dependencies_from_list(poetry_dev_deps, "[tool.poetry.dev-dependencies]"))

    # 8. [tool.poetry.group.*.dependencies]
    for group_name, group_deps in config.tool.poetry.group_dependencies.items():
        poetry_group_deps = [dep.to_requirement_string() for dep in group_deps]
        source = f"[tool.poetry.group.{group_name}.dependencies]"
        all_deps.extend(_extract_dependencies_from_list(poetry_group_deps, source))

    # 9. [tool.uv.dev-dependencies]
    if config.tool.uv.dev_dependencies:
        all_deps.extend(_extract_dependencies_from_list(config.tool.uv.dev_dependencies, "[tool.uv.dev-dependencies]"))

    return all_deps


def check_dependencies(pyproject: Path = Path("pyproject.toml")) -> list[DependencyInfo]:
    """Check all dependencies in pyproject.toml against PyPI.

    Args:
        pyproject: Path to pyproject.toml file

    Returns:
        List of DependencyInfo objects for all found dependencies.
    """
    config = load_pyproject_config(pyproject)
    return _extract_all_dependencies(config)


def print_report(deps: list[DependencyInfo], *, verbose: bool = False) -> int:
    """Print a formatted dependency status report.

    Args:
        deps: List of dependency info objects
        verbose: If True, show all dependencies; if False, show only outdated

    Returns:
        Exit code (0 if all up-to-date, 1 if any outdated)
    """
    if not deps:
        print("No dependencies found in pyproject.toml")
        return 0

    # Group by source
    by_source: dict[str, list[DependencyInfo]] = {}
    for dep in deps:
        by_source.setdefault(dep.source, []).append(dep)

    outdated_count = 0
    error_count = 0

    for source, source_deps in sorted(by_source.items()):
        # Filter if not verbose
        display_deps = source_deps if verbose else [d for d in source_deps if d.status != "up-to-date"]

        if not display_deps:
            continue

        print(f"\n{source}:")
        print("-" * len(source) + "-")

        # Calculate column widths
        name_width = max(len(d.name) for d in display_deps)
        constraint_width = max(len(d.constraint) for d in display_deps) if display_deps else 0
        latest_width = max(len(d.latest) for d in display_deps)

        for dep in sorted(display_deps, key=lambda d: d.name.lower()):
            status_icon = _get_status_icon(dep.status)
            constraint_display = dep.constraint if dep.constraint else "(any)"

            print(
                f"  {status_icon} {dep.name:<{name_width}}"
                f"  {constraint_display:<{constraint_width}}"
                f"  -> {dep.latest:<{latest_width}}  [{dep.status}]"
            )

            if dep.status == "outdated":
                outdated_count += 1
            elif dep.status == "error":
                error_count += 1

    # Summary
    total = len(deps)
    up_to_date = sum(1 for d in deps if d.status == "up-to-date")
    pinned = sum(1 for d in deps if d.status == "pinned")
    unknown = sum(1 for d in deps if d.status == "unknown")

    print(f"\nSummary: {total} dependencies checked")
    print(f"  Up-to-date: {up_to_date}")
    print(f"  Pinned:     {pinned}")
    print(f"  Outdated:   {outdated_count}")
    print(f"  Unknown:    {unknown}")
    print(f"  Errors:     {error_count}")

    if outdated_count > 0:
        print("\nRun with --verbose to see all dependencies")
        return 1
    return 0


def _get_status_icon(status: str) -> str:
    """Get a status icon character (ASCII-safe for Windows compatibility)."""
    icons = {
        "up-to-date": "[ok]",
        "outdated": "[!!]",
        "pinned": "[==]",
        "unknown": "[??]",
        "error": "[XX]",
    }
    return icons.get(status, "[??]")


def _build_updated_spec(dep: DependencyInfo) -> str:
    """Build an updated dependency specification with the latest version.

    Preserves the original format (>=, ==, etc.) and any environment markers.
    """
    original = dep.original_spec
    latest = dep.latest

    if not original or not latest or latest == "not found":
        return original

    # Check for environment markers
    marker = ""
    marker_idx = original.find(";")
    if marker_idx != -1:
        marker = original[marker_idx:]
        original = original[:marker_idx].strip()

    # Check for extras
    extras = ""
    bracket_idx = original.find("[")
    if bracket_idx != -1:
        close_bracket = original.find("]", bracket_idx)
        if close_bracket != -1:
            extras = original[bracket_idx : close_bracket + 1]

    # Find the version constraint pattern and replace the version
    # Common patterns: >=X.Y.Z, ==X.Y.Z, ~=X.Y.Z, >X.Y.Z
    def replace_version(match: re.Match[str]) -> str:
        operator = match.group(1)
        return f"{operator}{latest}"

    # Replace all version constraints with latest
    updated = _RE_VERSION_CONSTRAINT.sub(replace_version, original)

    # If no version constraint was found, add >=latest
    if updated == original and not _RE_HAS_CONSTRAINT.search(original):
        # Extract just the package name
        name_match = _RE_PACKAGE_NAME.match(original)
        if name_match:
            pkg_name = name_match.group(1)
            updated = f"{pkg_name}{extras}>={latest}"
        else:
            updated = f"{original}>={latest}"
    elif extras and extras not in updated:
        # Re-add extras if they were stripped
        name_match = _RE_PACKAGE_NAME.match(updated)
        if name_match:
            pkg_name = name_match.group(1)
            rest = updated[len(pkg_name) :]
            updated = f"{pkg_name}{extras}{rest}"

    # Re-add environment marker
    if marker:
        updated = f"{updated}{marker}"

    return updated


def update_dependencies(
    deps: list[DependencyInfo],
    pyproject: Path = Path("pyproject.toml"),
    *,
    dry_run: bool = False,
) -> int:
    """Update outdated dependencies in pyproject.toml to latest versions.

    Args:
        deps: List of dependency info objects from check_dependencies
        pyproject: Path to pyproject.toml file
        dry_run: If True, only show what would be changed without modifying

    Returns:
        Number of dependencies updated
    """
    outdated = [d for d in deps if d.status == "outdated"]
    if not outdated:
        print("All dependencies are up-to-date!")
        return 0

    # Read the file content
    content = pyproject.read_text(encoding="utf-8")
    updated_count = 0

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Updating {len(outdated)} dependencies:\n")

    for dep in outdated:
        if not dep.original_spec:
            continue

        new_spec = _build_updated_spec(dep)
        if new_spec == dep.original_spec:
            continue

        # Escape special regex characters in the original spec
        escaped_original = re.escape(dep.original_spec)

        # Try to find and replace the dependency in the file
        # We need to be careful to match the exact string in quotes
        patterns = [
            # Double-quoted string
            rf'"{escaped_original}"',
            # Single-quoted string
            rf"'{escaped_original}'",
        ]

        replaced = False
        for pattern in patterns:
            if re.search(pattern, content):
                quote = pattern[0]
                replacement = f"{quote}{new_spec}{quote}"
                content = re.sub(pattern, replacement, content, count=1)
                replaced = True
                break

        if replaced:
            print(f"  {dep.name}: {dep.original_spec} -> {new_spec}")
            updated_count += 1
        else:
            print(f"  {dep.name}: Could not locate in file (manual update needed)")

    if updated_count > 0:
        if dry_run:
            print(f"\n[DRY RUN] Would update {updated_count} dependencies")
        else:
            pyproject.write_text(content, encoding="utf-8")
            print(f"\nUpdated {updated_count} dependencies in {pyproject}")
    else:
        print("\nNo dependencies were updated")

    return updated_count


def main(
    verbose: bool = False,
    update: bool = False,
    dry_run: bool = False,
    pyproject: Path = Path("pyproject.toml"),
) -> int:
    """Main entry point for dependency checking.

    Args:
        verbose: Show all dependencies, not just outdated ones
        update: Update outdated dependencies to latest versions
        dry_run: Show what would be updated without making changes
        pyproject: Path to pyproject.toml

    Returns:
        Exit code (0 if all up-to-date or update successful, 1 if any outdated)
    """
    print(f"Checking dependencies in {pyproject}...")
    deps = check_dependencies(pyproject)
    exit_code = print_report(deps, verbose=verbose)

    if update:
        updated = update_dependencies(deps, pyproject, dry_run=dry_run)
        if updated > 0 and not dry_run:
            return 0  # Successfully updated
    return exit_code


if __name__ == "__main__":  # pragma: no cover
    verbose_flag = "--verbose" in sys.argv or "-v" in sys.argv
    update_flag = "--update" in sys.argv or "-u" in sys.argv
    dry_run_flag = "--dry-run" in sys.argv
    sys.exit(main(verbose=verbose_flag, update=update_flag, dry_run=dry_run_flag))
